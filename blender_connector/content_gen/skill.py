"""Render the Blender skill file (CONN-BLENDER-CONNECTOR-CONTENT-R004).

A pure function from the source and its tool snapshot to Markdown. The
body holds when to use the connector, the activation note, a table
listing every snapshot tool exactly once as ``blender_<tool>`` with its
first description sentence, and the functionality list linking to the
prompt names.
"""

from __future__ import annotations

from blender_connector.content_gen.errors import (
    CONTENT_SKILL_TOOL_UNKNOWN,
    ContentError,
)
from blender_connector.content_gen.sources import (
    BlenderSource,
    ToolSnapshot,
    first_sentence,
)


def _check_tools(app: str, tools, snapshot: ToolSnapshot) -> None:
    known = snapshot.names()
    for tool in tools:
        if tool not in known:
            raise ContentError(
                CONTENT_SKILL_TOOL_UNKNOWN,
                f"{app}: tool {tool!r} is not in the snapshot",
            )


def render_skill(source: BlenderSource, snapshot: ToolSnapshot) -> str:
    """The Markdown text of ``skills/blender/SKILL.md``."""
    app = source.app
    for func in source.functionalities:
        _check_tools(app, func.tools, snapshot)
    lines = [
        "---",
        f"name: {app}",
        f"description: {source.summary}",
        "---",
        "",
        f"# {app.title()}",
        "",
        "## When to use",
        "",
        source.summary,
        "",
        "## Activation",
        "",
        f"The `{app}` namespace is active by default: the `{app}_*` tools are "
        "visible from the first tool list. If the operator set lazy "
        f"activation, call `registry_activate` with the namespace `{app}` "
        "before using any of them.",
        "",
        "## Tools",
        "",
        "| Tool | What it does |",
        "|---|---|",
    ]
    for tool in snapshot.tools:
        sentence = first_sentence(tool.description) or tool.name
        lines.append(f"| `{app}_{tool.name}` | {sentence} |")
    if source.functionalities:
        lines += ["", "## Functionalities", ""]
        for func in source.functionalities:
            lines.append(
                f"- `{app}-{func.name}` — {func.description}"
                if func.description
                else f"- `{app}-{func.name}`"
            )
    lines.append("")
    return "\n".join(lines)
