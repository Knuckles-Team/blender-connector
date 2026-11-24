"""Render the Blender prompt packs (CONN-BLENDER-CONNECTOR-CONTENT-R005).

A pure function to JSON text, one prompt per functionality. Each prompt
tells the model that the ``blender`` namespace is active by default,
activating it first only under lazy activation, and names only tools
the snapshot lists.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from blender_connector.content_gen.errors import (
    CONTENT_PROMPT_TOOL_UNKNOWN,
    ContentError,
)
from blender_connector.content_gen.sources import BlenderSource, ToolSnapshot


def _check_tools(app: str, tools, snapshot: ToolSnapshot) -> None:
    known = snapshot.names()
    for tool in tools:
        if tool not in known:
            raise ContentError(
                CONTENT_PROMPT_TOOL_UNKNOWN,
                f"{app}: functionality names tool {tool!r} not in the snapshot",
            )


def _prompt(
    source: BlenderSource, functionality, snapshot: ToolSnapshot
) -> dict[str, object]:
    app = source.app
    namespaced = [f"{app}_{tool}" for tool in functionality.tools]
    directive = (
        f"Use only the {app} upstream of the blender-connector connector. "
        f"The namespace `{app}` is active by default; if the operator set "
        f"lazy activation, activate it with registry_activate first. Every "
        f"tool below is namespaced {app}_<tool>. "
    )
    if namespaced:
        directive += (
            "Work through these tools in order: "
            + ", ".join(f"`{name}`" for name in namespaced)
            + ". "
        )
    if functionality.steps:
        directive += (
            "Steps: "
            + " ".join(
                f"({index}) {step}" for index, step in enumerate(functionality.steps, 1)
            )
            + " "
        )
    directive += (
        "Report a refusal payload when a tool refuses; never retry past a refusal."
    )
    return {
        "task": f"{app}-{functionality.name}",
        "type": "prompt",
        "schema_version": "1.0",
        "prompt_version": "0.1.0",
        "source": "blender-connector",
        "description": functionality.description,
        "metadata": {
            "topic": app.title(),
            "tone": "technical and precise",
            "style": f"{app.title()} functionality",
        },
        "identity": {
            "role": f"{app.title()} {functionality.name.replace('_', ' ').title()} Specialist",
            "goal": (
                f"Complete the {functionality.name.replace('_', ' ')} use case "
                f"of {app} using only its snapshot tools."
            ),
            "personality": ["methodical", "provenance-aware"],
        },
        "instructions": {
            "core_directive": directive,
            "quality_checklist": [
                "the blender namespace was available before the first tool call",
                "every tool named in this prompt exists in the upstream snapshot",
                "refusals are reported to the operator, never retried silently",
            ],
        },
        "skills": [],
        "tools": namespaced,
        "requires_namespace": app,
    }


def render_prompts(source: BlenderSource, snapshot: ToolSnapshot) -> Mapping[str, str]:
    """``blender-<functionality>.json`` file names to their JSON text."""
    rendered: dict[str, str] = {}
    for functionality in source.functionalities:
        _check_tools(source.app, functionality.tools, snapshot)
        name = f"{source.app}-{functionality.name}.json"
        rendered[name] = (
            json.dumps(
                _prompt(source, functionality, snapshot),
                indent=2,
                ensure_ascii=True,
            )
            + "\n"
        )
    return rendered


def unassigned_tools(source: BlenderSource, snapshot: ToolSnapshot) -> list[str]:
    """Snapshot tools no functionality names; a report line, not a failure."""
    named = {
        tool for functionality in source.functionalities for tool in functionality.tools
    }
    return sorted(snapshot.names() - named)
