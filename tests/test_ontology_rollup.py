"""CONN-BLENDER-CONNECTOR-CONTENT-R003: the pack rolls up to the medulla core.

Every app class declares ``rdfs:subClassOf`` to its core parent under both
parent-catalog namespaces (the retired ``kg#`` base and the core module
base), so whichever catalog generation a serving engine composes, the
subclass closure from the class reaches a core class. The file declares
no ``owl:imports`` and redeclares no core class.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import rdflib
import yaml
from rdflib import OWL, RDF, RDFS, URIRef

REPO_ROOT = Path(__file__).resolve().parent.parent
APP = "http://knuckles.team/kg/blender#"
KG_RETIRED = "http://knuckles.team/kg#"
CORE_MODULE = "https://knuckles-team.github.io/ontology/core#"
PARENT_BASES = (KG_RETIRED, CORE_MODULE)
CORE_NAMES = frozenset(
    {"Application", "Tool", "Task", "Document", "Artifact", "CreativeWork"}
)

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-CONTENT-R003")


def _parents(graph: rdflib.Graph) -> dict[rdflib.Node, set[rdflib.Node]]:
    return {
        subject: set(graph.objects(subject, RDFS.subClassOf))
        for subject in graph.subjects(RDFS.subClassOf, None)
    }


def _local_name(node: rdflib.Node) -> str:
    return str(node).rsplit("#", 1)[-1]


def _reaches_core(
    start: rdflib.Node,
    parents: dict[rdflib.Node, set[rdflib.Node]],
    seen: set[rdflib.Node] | None = None,
) -> list[rdflib.Node] | None:
    """The subclass-closure path from ``start`` to a core class, or None."""
    if seen is None:
        seen = set()
    if _local_name(start) in CORE_NAMES and str(start).startswith(PARENT_BASES):
        return [start]
    if start in seen:
        return None
    seen.add(start)
    for parent in sorted(parents.get(start, ()), key=str):
        reached = _reaches_core(parent, parents, seen)
        if reached is not None:
            return [start] + reached
    return None


def test_pack_classes_roll_up_to_the_core_and_import_nothing() -> None:
    graph = rdflib.Graph()
    path = REPO_ROOT / "blender_connector" / "ontology" / "blender.ttl"
    raw_text = path.read_text(encoding="utf-8")

    # The pack composes the core; it does not import or redeclare it.
    assert "owl:imports" not in raw_text
    graph.parse(path, format="turtle")
    parents = _parents(graph)

    for subject in graph.subjects(RDFS.subClassOf, None):
        assert not str(subject).startswith(PARENT_BASES), (
            f"{subject} sits in a core-namespace position (redeclaration)"
        )
    assert any(
        subject == URIRef("http://knuckles.team/kg/blender")
        for subject in graph.subjects(RDF.type, OWL.Ontology)
    ), "the ontology IRI is not declared"

    app_classes = sorted(
        (s for s in graph.subjects(RDF.type, OWL.Class) if str(s).startswith(APP)),
        key=str,
    )
    assert app_classes, "no app classes declared"

    # The three pack classes hold their dual edge to the core parent.
    for name, core in {
        "BlenderApp": "Application",
        "BlenderTool": "Tool",
        "BlenderUseCase": "Task",
    }.items():
        node = URIRef(APP + name)
        class_parents = parents.get(node, set())
        assert URIRef(KG_RETIRED + core) in class_parents, (
            f"app:{name} lacks its edge to the kg# {core}"
        )
        assert URIRef(CORE_MODULE + core) in class_parents, (
            f"app:{name} lacks its edge to the core-module {core}"
        )
        assert {
            parent for parent in class_parents if _local_name(parent) != core
        } == set(), f"app:{name} extends more than :{core}"
        assert _reaches_core(node, parents), f"app:{name} does not reach a core class"

    # Every authored domain class (read from the source, not hardcoded)
    # holds its dual edge, and the closure reaches a core class under at
    # least one parent-catalog base.
    source = yaml.safe_load(
        (REPO_ROOT / "content" / "apps" / "blender.yml").read_text(encoding="utf-8")
    )
    domain = {entry["name"]: entry["parent"] for entry in source["classes"]}
    assert domain, "the authored source lists no domain classes"
    for name, core in domain.items():
        node = URIRef(APP + name)
        assert node in parents, f"app:{name} is not declared"
        class_parents = parents[node]
        assert URIRef(KG_RETIRED + core) in class_parents, (
            f"app:{name} lacks its edge to the kg# {core}"
        )
        assert URIRef(CORE_MODULE + core) in class_parents, (
            f"app:{name} lacks its edge to the core-module {core}"
        )
        assert {
            parent for parent in class_parents if _local_name(parent) != core
        } == set(), f"app:{name} extends more than :{core}"
        assert _reaches_core(node, parents), f"app:{name} does not reach a core class"

    # No orphan: every app class in the file reaches the core.
    for node in app_classes:
        assert _reaches_core(node, parents), (
            f"app:{_local_name(node)} is an orphan (no subclass path to the core)"
        )
