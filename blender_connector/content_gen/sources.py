"""The authored Blender source and the tool snapshot the renders read.

``content/apps/blender.yml`` is the authored half (summary, domain
classes, functionalities); ``content/snapshots/blender.tools.json`` is
the generated half (the upstream's ``tools/list`` at refresh time).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

#: The parents a domain class may name (shared core catalog).
ALLOWED_PARENTS = frozenset({"CreativeWork", "Document", "Artifact"})


@dataclass(frozen=True)
class AppClass:
    """One domain class of the Blender pack, naming one allowed parent."""

    name: str
    parent: str
    description: str = ""


@dataclass(frozen=True)
class Step:
    """One numbered step: one objective, the tool call and the check."""

    do: str
    check: str = ""
    tool: str = ""
    args: str = ""


@dataclass(frozen=True)
class Recovery:
    """One error-recovery row."""

    symptom: str
    cause: str
    fix: str


@dataclass(frozen=True)
class Functionality:
    """One use case: an ordered tool list the prompt walks through."""

    name: str
    description: str
    tools: tuple[str, ...]
    steps: tuple[Step, ...] = field(default_factory=tuple)
    use_when: str = ""
    not_for: str = ""
    recovery: tuple[Recovery, ...] = field(default_factory=tuple)
    reads: tuple[str, ...] = field(default_factory=tuple)
    writes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DataLocation:
    """Where one kind of Blender data lives and how it is reached."""

    name: str
    where: str


@dataclass(frozen=True)
class Role:
    """One agent definition: the operator or a business role."""

    name: str
    title: str
    goal: str
    functionalities: tuple[str, ...]
    reads: tuple[str, ...] = field(default_factory=tuple)
    writes: tuple[str, ...] = field(default_factory=tuple)
    approval_required: tuple[str, ...] = field(default_factory=tuple)
    never: tuple[str, ...] = field(default_factory=tuple)
    outputs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BlenderSource:
    """The authored half of the connector's content."""

    app: str
    summary: str
    classes: tuple[AppClass, ...]
    functionalities: tuple[Functionality, ...]
    prerequisites: tuple[str, ...] = field(default_factory=tuple)
    data_locations: tuple[DataLocation, ...] = field(default_factory=tuple)
    recovery: tuple[Recovery, ...] = field(default_factory=tuple)
    roles: tuple[Role, ...] = field(default_factory=tuple)
    agent_never: tuple[str, ...] = field(default_factory=tuple)
    agent_outputs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ToolInfo:
    """One tool from the snapshot, in its upstream name."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolSnapshot:
    """The generated half: the upstream's tool list at refresh time."""

    app: str
    version: str
    tools: tuple[ToolInfo, ...]

    def names(self) -> frozenset[str]:
        return frozenset(tool.name for tool in self.tools)


def load_app_source(path: Path) -> BlenderSource:
    """Parse the authored source; the app name must match the file."""
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    app = document.get("app")
    if not isinstance(app, str) or app != path.stem:
        raise ValueError(f"{path.name}: the app name must match the file name")
    classes = tuple(
        AppClass(
            name=str(item["name"]),
            parent=str(item["parent"]),
            description=str(item.get("description", "")),
        )
        for item in document.get("classes", [])
        if isinstance(item, dict) and item.get("name")
    )
    functionalities = tuple(
        Functionality(
            name=str(item["name"]),
            description=str(item.get("description", "")),
            tools=tuple(str(t) for t in item.get("tools", [])),
            steps=tuple(_step(raw) for raw in item.get("steps", [])),
            use_when=str(item.get("use_when", "")),
            not_for=str(item.get("not_for", "")),
            recovery=_recovery(item.get("recovery", [])),
            reads=_strs(item.get("reads", [])),
            writes=_strs(item.get("writes", [])),
        )
        for item in document.get("functionality", [])
        if isinstance(item, dict) and item.get("name")
    )
    for func in functionalities:
        for step in func.steps:
            if step.tool and step.tool not in func.tools:
                raise ValueError(
                    f"{func.name}: step tool {step.tool!r} is not in its tool list"
                )
    roles = tuple(
        Role(
            name=str(item["name"]),
            title=str(item.get("title", item["name"])),
            goal=str(item.get("goal", "")),
            functionalities=_strs(item.get("functionalities", [])),
            reads=_strs(item.get("reads", [])),
            writes=_strs(item.get("writes", [])),
            approval_required=_strs(item.get("approval_required", [])),
            never=_strs(item.get("never", [])),
            outputs=_strs(item.get("outputs", [])),
        )
        for item in document.get("roles", [])
        if isinstance(item, dict) and item.get("name")
    )
    locations = {
        str(i["name"])
        for i in document.get("data_locations", [])
        if isinstance(i, dict) and i.get("name")
    }
    for func in functionalities:
        for name in (*func.reads, *func.writes):
            if name not in locations:
                raise ValueError(f"{func.name}: unknown data location {name!r}")
    defaults = document.get("agent_defaults") or {}
    known = {func.name for func in functionalities}
    for role in roles:
        for name in role.functionalities:
            if name not in known:
                raise ValueError(f"role {role.name}: unknown functionality {name!r}")
    return BlenderSource(
        app=app,
        summary=str(document.get("summary", "")).strip(),
        classes=classes,
        functionalities=functionalities,
        prerequisites=_strs(document.get("prerequisites", [])),
        data_locations=tuple(
            DataLocation(name=str(i["name"]), where=str(i.get("where", "")))
            for i in document.get("data_locations", [])
            if isinstance(i, dict) and i.get("name")
        ),
        recovery=_recovery(document.get("recovery", [])),
        roles=roles,
        agent_never=_strs(defaults.get("never", [])),
        agent_outputs=_strs(defaults.get("outputs", [])),
    )


def _strs(values) -> tuple[str, ...]:
    return tuple(str(v) for v in values or [])


def _step(raw) -> Step:
    if isinstance(raw, str):
        return Step(do=raw)
    return Step(
        do=str(raw["do"]),
        check=str(raw.get("check", "")),
        tool=str(raw.get("tool", "")),
        args=str(raw.get("args", "")),
    )


def _recovery(rows) -> tuple[Recovery, ...]:
    return tuple(
        Recovery(
            symptom=str(r["symptom"]), cause=str(r.get("cause", "")), fix=str(r["fix"])
        )
        for r in rows or []
        if isinstance(r, dict) and r.get("symptom")
    )


def load_snapshot(path: Path) -> ToolSnapshot:
    """Parse one committed tool snapshot, sorted by tool name."""
    document = json.loads(path.read_text(encoding="utf-8"))
    tools = tuple(
        ToolInfo(
            name=str(item["name"]),
            description=str(item.get("description", "")),
            input_schema=dict(item.get("input_schema", {}) or {}),
        )
        for item in document.get("tools", [])
        if isinstance(item, dict) and item.get("name")
    )
    tools = tuple(sorted(tools, key=lambda tool: tool.name))
    return ToolSnapshot(
        app=str(document.get("app", path.stem.split(".")[0])),
        version=str(document.get("version", "")),
        tools=tools,
    )


def first_sentence(text: str) -> str:
    """The first sentence of a tool description, for tables and prompts."""
    text = text.strip()
    match = re.search(r"[^.!\?]+[.!\?]", text)
    if match is None:
        return text
    return match.group(0).strip()


def skill_name(app: str, functionality: str) -> str:
    """The Agent Skill name: lowercase with hyphens, matching its folder."""
    return f"{app}-{functionality.replace('_', '-')}"
