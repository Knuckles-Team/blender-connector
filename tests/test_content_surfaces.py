"""CONN-BLENDER-CONNECTOR-CONTENT-R001: the server lists its packaged content.

The skill, the ontology and every prompt are found by the package
convention and served by the SDK with no wiring of their own. The
upstream is disabled for the test so no child starts.
"""

from __future__ import annotations

import asyncio
import importlib
from pathlib import Path

import pytest
from fastmcp import Client

PACKAGE = "blender_connector"
ROOT = Path(list(importlib.import_module(PACKAGE).__path__)[0])

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-CONTENT-R001")


def test_default_content_surfaces(clean_upstream_env, monkeypatch) -> None:
    monkeypatch.setenv("SCION_UPSTREAMS_DISABLED", "blender")

    from blender_connector.mcp_server import build_server

    async def listings():
        async with Client(build_server(command_args=[])) as client:
            resources = {
                str(resource.uri) for resource in await client.list_resources()
            }
            prompts = {prompt.name for prompt in await client.list_prompts()}
        return resources, prompts

    resources, prompts = asyncio.run(listings())
    if list(ROOT.glob("skills/*/SKILL.md")):
        assert any(uri.startswith("skill://") for uri in resources)
    if list(ROOT.glob("ontology/*.ttl")):
        assert any(uri.startswith("ontology://blender-connector/") for uri in resources)
    for path in ROOT.glob("prompts/*.json"):
        if not path.name.startswith("_"):
            assert path.stem in prompts


def test_the_kit_review_prompt_is_listed(clean_upstream_env, monkeypatch) -> None:
    """CONN-BLENDER-CONNECTOR-CONTENT-R008: the kit review functionality is served."""
    monkeypatch.setenv("SCION_UPSTREAMS_DISABLED", "blender")

    from blender_connector.mcp_server import build_server

    async def listings():
        async with Client(build_server(command_args=[])) as client:
            return {prompt.name for prompt in await client.list_prompts()}

    assert "blender-export_and_validate_kit" in asyncio.run(listings())
    skill = (ROOT / "skills/blender-export-and-validate-kit/SKILL.md").read_text(
        encoding="utf-8"
    )
    for step in ("1. ", "2. ", "3. ", "4. "):
        assert step in skill
    for tool in ("execute_blender_code", "look", "get_scene_info"):
        assert f"blender_{tool}" in skill
