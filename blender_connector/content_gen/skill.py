"""Render the Blender skills (CONN-BLENDER-CONNECTOR-CONTENT-R004).

Pure functions from the source and its tool snapshot to Markdown. The
router skill ``blender`` lists every snapshot tool exactly once as
``blender_<tool>`` with its first description sentence, the shared
prerequisites, the functionality skills and a shared recovery table.
Each functionality renders one skill ``blender-<functionality>`` with
when to use and when not to use, numbered steps (one objective and one
check each), concrete tool-call arguments and an error-recovery table.
"""

from __future__ import annotations

from collections.abc import Mapping

from blender_connector.content_gen.errors import (
    CONTENT_FRONT_MATTER_UNSAFE,
    CONTENT_SKILL_TOOL_UNKNOWN,
    ContentError,
)
from blender_connector.content_gen.sources import (
    BlenderSource,
    Functionality,
    Recovery,
    ToolSnapshot,
    first_sentence,
    skill_name,
)


def _check_tools(app: str, tools, snapshot: ToolSnapshot) -> None:
    known = snapshot.names()
    for tool in tools:
        if tool not in known:
            raise ContentError(
                CONTENT_SKILL_TOOL_UNKNOWN,
                f"{app}: tool {tool!r} is not in the snapshot",
            )


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _recovery_table(rows: tuple[Recovery, ...]) -> list[str]:
    lines = ["| Symptom | Likely cause | Fix |", "|---|---|---|"]
    for row in rows:
        lines.append(
            f"| {_cell(row.symptom)} | {_cell(row.cause)} | {_cell(row.fix)} |"
        )
    return lines


#: Characters the engine refuses anywhere in a skill's front matter.
_UNSAFE_FRONT_MATTER = "&*!{}"


def _frontmatter(name: str, description: str, tags: list[str]) -> list[str]:
    unsafe = sorted({c for c in name + description + " ".join(tags) if c in _UNSAFE_FRONT_MATTER})
    if unsafe:
        raise ContentError(
            CONTENT_FRONT_MATTER_UNSAFE,
            f"{name}: front matter holds {''.join(unsafe)!r}",
        )
    return [
        "---",
        f"name: {name}",
        "skill_type: skill",
        "description: >-",
        f"  {description}",
        "license: MIT",
        f"tags: [{', '.join(tags)}]",
        "metadata:",
        "  author: Knuckles-Team",
        "  version: '0.2.0'",
        "---",
    ]


def render_skill(source: BlenderSource, snapshot: ToolSnapshot) -> str:
    """The Markdown text of the router skill ``skills/blender/SKILL.md``."""
    app = source.app
    for func in source.functionalities:
        _check_tools(app, func.tools, snapshot)
    description = (
        f"{source.summary} Use when the agent must work in a live Blender "
        "session through the blender_ prefixed tools and needs the right functionality "
        "skill. Do NOT use for rendering farms, file conversion outside a "
        "running Blender, or any other 3D application."
    )
    lines = _frontmatter(app, " ".join(description.split()), [app, "3d", "mcp"])
    lines += [
        "",
        "# Blender",
        "",
        "Router for the Blender connector: one MCP server that proxies the "
        "`mcp-for-blender` upstream. Pick the functionality skill below, "
        "then follow its numbered steps.",
        "",
        "## When to use",
        "",
        source.summary,
        "",
        "## When NOT to use",
        "",
        "- Batch rendering or conversion without a running Blender: the "
        "connector only reaches a live session through the add-on socket.",
        "- Any other 3D or CAD application: use that application's connector.",
        "",
        "## Prerequisites",
        "",
    ]
    lines += [f"- {item}" for item in source.prerequisites]
    lines += [
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
        lines.append(f"| `{app}_{tool.name}` | {_cell(sentence)} |")
    lines += [
        "| `handshake` | Local readiness check: upstream binary and add-on socket. |"
    ]
    if source.functionalities:
        lines += ["", "## Functionality skills", ""]
        lines += ["| Skill | Use it to |", "|---|---|"]
        for func in source.functionalities:
            lines.append(
                f"| `{skill_name(app, func.name)}` | {_cell(func.description)} |"
            )
    if source.data_locations:
        lines += ["", "## Where the data lives", ""]
        lines += [f"- **{loc.name}**: {loc.where}" for loc in source.data_locations]
    if source.recovery:
        lines += ["", "## Error recovery", ""]
        lines += _recovery_table(source.recovery)
    lines.append("")
    return "\n".join(lines)


def render_functionality_skill(
    source: BlenderSource, func: Functionality, snapshot: ToolSnapshot
) -> str:
    """The Markdown text of one ``skills/blender-<functionality>/SKILL.md``."""
    app = source.app
    _check_tools(app, func.tools, snapshot)
    name = skill_name(app, func.name)
    description = (
        f"{func.description} Use when {func.use_when[:1].lower()}"
        f"{func.use_when[1:]} Do NOT use for {func.not_for[:1].lower()}"
        f"{func.not_for[1:]}"
    )
    lines = _frontmatter(name, " ".join(description.split()), [app, func.name, "mcp"])
    lines += [
        "",
        f"# Blender: {func.name.replace('_', ' ')}",
        "",
        func.description,
        "",
        "## When to use",
        "",
        func.use_when,
        "",
        "## When NOT to use",
        "",
        func.not_for,
        "",
        "## Before you start",
        "",
        f"- The `{app}` namespace is active (`registry_activate` otherwise).",
    ]
    lines += [f"- {item}" for item in source.prerequisites]
    lines += ["", "## Tools", "", "| Tool | What it does |", "|---|---|"]
    by_name = {tool.name: tool for tool in snapshot.tools}
    for tool_name in func.tools:
        sentence = first_sentence(by_name[tool_name].description) or tool_name
        lines.append(f"| `{app}_{tool_name}` | {_cell(sentence)} |")
    lines += ["", "## Steps", ""]
    for index, step in enumerate(func.steps, 1):
        lines.append(f"{index}. **{step.do}**")
        if step.tool:
            lines.append(f"   - Tool: `{app}_{step.tool}`")
        if step.args:
            lines += [
                "   - Arguments:",
                "",
                "     ```json",
                f"     {step.args}",
                "     ```",
                "",
            ]
        if step.check:
            lines.append(f"   - Check: {step.check}")
    lines += ["", "## Error recovery", ""]
    lines += _recovery_table(func.recovery + source.recovery[:3])
    lines += [
        "",
        "## Related",
        "",
        f"- Router skill `{app}`; prompt `{app}-{func.name}`.",
        "- Refusals are reported to the operator and never retried past the "
        "recovery rows above.",
        "",
    ]
    return "\n".join(lines)


def render_skills(source: BlenderSource, snapshot: ToolSnapshot) -> Mapping[str, str]:
    """Package-relative skill paths to their Markdown text."""
    files = {f"skills/{source.app}/SKILL.md": render_skill(source, snapshot)}
    for func in source.functionalities:
        files[f"skills/{skill_name(source.app, func.name)}/SKILL.md"] = (
            render_functionality_skill(source, func, snapshot)
        )
    return files
