"""CONN-BLENDER-CONNECTOR-CONTENT-R007: the committed content matches the snapshot.

The offline drift gate renders in memory and compares bytes with the
committed files. The functionality partition must name every snapshot
tool, and a render that names an unknown tool refuses.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-CONTENT-R007")


def test_committed_content_matches_snapshot() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "generate_blender_content.py"),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"content drift: {result.stdout}\n{result.stderr}"


def test_functionality_partition_covers_the_snapshot() -> None:
    from blender_connector.content_gen.prompts import unassigned_tools
    from blender_connector.content_gen.sources import (
        load_app_source,
        load_snapshot,
    )

    source = load_app_source(REPO_ROOT / "content" / "apps" / "blender.yml")
    snapshot = load_snapshot(REPO_ROOT / "content" / "snapshots" / "blender.tools.json")
    assert unassigned_tools(source, snapshot) == []


def test_render_refuses_an_unknown_tool() -> None:
    from blender_connector.content_gen.errors import (
        CONTENT_PROMPT_TOOL_UNKNOWN,
        ContentError,
    )
    from blender_connector.content_gen.prompts import render_prompts
    from blender_connector.content_gen.sources import (
        BlenderSource,
        Functionality,
        ToolInfo,
        ToolSnapshot,
    )

    snapshot = ToolSnapshot(
        app="blender",
        version="0.0.0",
        tools=(ToolInfo(name="get_scene_info", description="The scene."),),
    )
    source = BlenderSource(
        app="blender",
        summary="Fixture.",
        classes=(),
        functionalities=(
            Functionality(
                name="ghost",
                description="Names a tool the snapshot lacks.",
                tools=("missing_tool",),
            ),
        ),
    )
    with pytest.raises(ContentError) as excinfo:
        render_prompts(source, snapshot)
    assert excinfo.value.code == CONTENT_PROMPT_TOOL_UNKNOWN
