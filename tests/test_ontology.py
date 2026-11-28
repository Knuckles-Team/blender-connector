"""CONN-BLENDER-CONNECTOR-CONTENT-R009: scene classes are creative works."""

from __future__ import annotations

from pathlib import Path

import pytest
import rdflib
from rdflib import RDFS, URIRef

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-CONTENT-R009")

ROOT = Path(__file__).resolve().parent.parent
APP = "http://knuckles.team/kg/blender#"
KG_RETIRED = "http://knuckles.team/kg#"
CORE_MODULE = "https://knuckles-team.github.io/ontology/core#"


def test_scene_and_file_are_creative_works() -> None:
    graph = rdflib.Graph()
    graph.parse(
        ROOT / "blender_connector" / "ontology" / "blender.ttl", format="turtle"
    )
    for name in ("BlenderFile", "Scene"):
        parents = set(graph.objects(URIRef(APP + name), RDFS.subClassOf))
        assert URIRef(KG_RETIRED + "CreativeWork") in parents, name
        assert URIRef(CORE_MODULE + "CreativeWork") in parents, name
        assert not any(str(p).endswith("#Document") for p in parents), name
