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
from blender_connector.content_gen.sources import (
    BlenderSource,
    ToolSnapshot,
    skill_name,
)


def _check_tools(app: str, tools, snapshot: ToolSnapshot) -> None:
    known = snapshot.names()
    for tool in tools:
        if tool not in known:
            raise ContentError(
                CONTENT_PROMPT_TOOL_UNKNOWN,
                f"{app}: functionality names tool {tool!r} not in the snapshot",
            )


def _step_text(app: str, index: int, step) -> str:
    text = f"({index}) {step.do}"
    if step.tool:
        text += f" Call `{app}_{step.tool}`."
    if step.check:
        text += f" Check: {step.check}"
    return text


def _prompt(
    source: BlenderSource, functionality, snapshot: ToolSnapshot
) -> dict[str, object]:
    app = source.app
    namespaced = [f"{app}_{tool}" for tool in functionality.tools]
    directive = (
        f"Use only the {app} upstream of the blender-connector connector. "
        f"The namespace `{app}` is active by default; if the operator set "
        f"lazy activation, activate it with registry_activate first. Every "
        f"tool below is namespaced {app}_<tool>. Call `handshake` first and "
        f"stop with a recovery report when it is not ready. Save the .blend "
        f"file before running code. "
    )
    if functionality.use_when:
        directive += f"Use this when: {functionality.use_when} "
    if functionality.not_for:
        directive += f"Do not use it for: {functionality.not_for} "
    if namespaced:
        directive += "Tools: " + ", ".join(f"`{name}`" for name in namespaced) + ". "
    if functionality.steps:
        directive += (
            "Steps, each with one objective and a check you must pass before "
            "the next: "
            + " ".join(
                _step_text(app, index, step)
                for index, step in enumerate(functionality.steps, 1)
            )
            + " "
        )
    directive += (
        "On failure follow the recovery table of the skill "
        f"`{skill_name(app, functionality.name)}`; report a refusal payload when a tool "
        "refuses and never retry past a refusal."
    )
    return {
        "task": f"{app}-{functionality.name}",
        "type": "prompt",
        "schema_version": "1.0",
        "prompt_version": "0.2.0",
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
                "the blender namespace was available and handshake was ready before the first tool call",
                "every step's check passed before the next step ran",
                "every tool named in this prompt exists in the upstream snapshot",
                "refusals are reported to the operator, never retried silently",
            ],
        },
        "agent": {
            "kind": "operator",
            "tools": namespaced,
            "skills": [app, skill_name(app, functionality.name)],
            "data": {
                "reads": list(functionality.reads),
                "writes": list(functionality.writes),
            },
            "guardrails": {
                "approval_required": [
                    t for t in namespaced if t in APPROVAL_REQUIRED_TOOLS
                ],
                "never": list(source.agent_never),
            },
            "outputs": list(source.agent_outputs),
        },
        "skills": [app, skill_name(app, functionality.name)],
        "tools": namespaced,
        "requires_namespace": app,
    }


#: The one tool that runs arbitrary Python in the live session.
APPROVAL_REQUIRED_TOOLS = frozenset({"blender_execute_blender_code"})


def _agent_kind(role) -> dict[str, str]:
    """The operator, or a business role named after its source entry."""
    if role.name == "operator":
        return {"kind": "operator"}
    return {"kind": "business-role", "business_role": role.name}


def _role_prompt(
    source: BlenderSource, role, snapshot: ToolSnapshot
) -> dict[str, object]:
    app = source.app
    by_name = {f.name: f for f in source.functionalities}
    tools: list[str] = []
    skills = [app]
    for name in role.functionalities:
        func = by_name[name]
        _check_tools(app, func.tools, snapshot)
        skills.append(skill_name(app, name))
        tools += [f"{app}_{t}" for t in func.tools if f"{app}_{t}" not in tools]
    directive = (
        f"You are the {role.title}. {role.goal} Work only through the "
        f"`{app}` namespace of the blender-connector; call `handshake` first. "
        "For each task load the matching skill, follow its numbered steps in "
        "order, pass each step's check before continuing, and use its "
        "error-recovery table on failure. Skills: "
        + ", ".join(f"`{s}`" for s in skills)
        + ". Require approval before any tool listed under approval_required, "
        "save the .blend file before running code, and report every result."
    )
    return {
        "task": f"{app}-{role.name}",
        "type": "prompt",
        "schema_version": "1.0",
        "prompt_version": "0.2.0",
        "source": "blender-connector",
        "description": f"Agent definition for the {role.title}.",
        "title": role.title,
        "metadata": {
            "topic": app.title(),
            "tone": "technical and precise",
            "style": f"{app.title()} agent",
        },
        "identity": {"role": role.title, "goal": role.goal},
        "instructions": {
            "core_directive": directive,
            "quality_checklist": [
                "handshake was ready before the first tool call",
                "every step's check passed before the next step ran",
                "every scene change was verified with get_scene_info or look",
                "approval was obtained for every approval_required tool",
            ],
        },
        "agent": {
            **_agent_kind(role),
            "tools": tools,
            "skills": skills,
            "data": {"reads": list(role.reads), "writes": list(role.writes)},
            "guardrails": {
                "approval_required": list(role.approval_required),
                "never": list(role.never),
            },
            "outputs": list(role.outputs),
        },
        "skills": skills,
        "tools": tools,
        "requires_namespace": app,
    }


def render_prompts(source: BlenderSource, snapshot: ToolSnapshot) -> Mapping[str, str]:
    """``blender-<name>.json`` file names to their JSON text."""
    rendered: dict[str, str] = {}
    for functionality in source.functionalities:
        _check_tools(source.app, functionality.tools, snapshot)
        name = f"{source.app}-{functionality.name}.json"
        rendered[name] = _dump(_prompt(source, functionality, snapshot))
    for role in source.roles:
        rendered[f"{source.app}-{role.name}.json"] = _dump(
            _role_prompt(source, role, snapshot)
        )
    return rendered


def _dump(document: dict[str, object]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=True) + "\n"


def unassigned_tools(source: BlenderSource, snapshot: ToolSnapshot) -> list[str]:
    """Snapshot tools no functionality names; a report line, not a failure."""
    named = {
        tool for functionality in source.functionalities for tool in functionality.tools
    }
    return sorted(snapshot.names() - named)
