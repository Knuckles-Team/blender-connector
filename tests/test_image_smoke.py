"""The CI smoke job of the two images (CONN-BLENDER-CONNECTOR-R018)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "smoke_images", ROOT / "scripts" / "smoke_images.py"
)
assert _SPEC and _SPEC.loader
smoke = importlib.util.module_from_spec(_SPEC)
sys.modules["smoke_images"] = smoke
_SPEC.loader.exec_module(smoke)

HEALTHY = {"command_found": True, "addon_socket": {"reachable": True, "error": None}}


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R018")
def test_the_smoke_assertions_accept_a_healthy_result() -> None:
    assert smoke.check_handshake(HEALTHY) == []
    assert smoke.check_scene('{"scene": "Scene", "object_count": 3}') == []
    image = SimpleNamespace(type="image", data="aGVsbG8=")
    assert smoke.check_look([SimpleNamespace(type="text", text="ok"), image]) == []


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R018")
def test_the_smoke_assertions_name_each_failure() -> None:
    down = {
        "command_found": False,
        "addon_socket": {"reachable": False, "error": "refused"},
    }
    problems = smoke.check_handshake(down)
    assert len(problems) == 2 and "refused" in problems[1]
    assert smoke.check_scene("Timeout waiting for Blender") and smoke.check_scene(
        "hello"
    )
    assert smoke.check_look([SimpleNamespace(type="text", text="no image")]) == [
        "the rendered view returned no image"
    ]
    assert smoke.check_look([SimpleNamespace(type="image", data="")])


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R018")
def test_the_workflow_builds_runs_and_asserts() -> None:
    document = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "image-smoke.yml").read_text(encoding="utf-8")
    )
    job = document["jobs"]["smoke"]
    runs = "\n".join(step.get("run", "") for step in job["steps"])
    assert "pipelines-connector render" in runs and "uv build --wheel" in runs
    assert "docker build --target mcp" in runs and "docker/blender.Dockerfile" in runs
    assert (
        "docker compose -f deploy/compose.yml up -d" in runs
        and "scripts/smoke_images.py" in runs
    )
    assert "compose.gpu.yml" not in runs and "--gpus" not in runs
    assert job["permissions"] == {"contents": "read"} and document["permissions"] == {
        "contents": "read"
    }
    assert any(
        step.get("if") == "failure()" and "logs" in step["run"] for step in job["steps"]
    )
    assert any(
        step.get("if") == "always()" and "down -v" in step["run"]
        for step in job["steps"]
    )
