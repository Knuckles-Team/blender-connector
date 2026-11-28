"""CONN-BLENDER-CONNECTOR-R002: the initial list holds the full proxied surface.

The upstream starts active: the first list already carries every
proxied tool, alongside the four registry tools and the one native
tool.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import Client
from scion_sdk.mcp.upstreams.activation import REGISTRY_TOOL_NAMES

from blender_connector.mcp_server import build_server

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R002")

# The fixture upstream serves exactly these tools, namespaced by app.
FIXTURE_TOOLS = ("execute_blender_code", "get_scene_info", "look")


def test_initial_list_is_full_surface(
    blender_cli_factory, clean_upstream_env, monkeypatch
) -> None:
    blender_cli_factory()
    server = build_server(command_args=[])

    async def scenario() -> None:
        async with Client(server) as client:
            tools = {tool.name for tool in await client.list_tools()}
            assert tools == (
                set(REGISTRY_TOOL_NAMES)
                | {"handshake"}
                | {f"blender_{name}" for name in FIXTURE_TOOLS}
            )
            assert len(tools) == 8
            # The active upstream started as a stdio child.
            status = {
                entry["namespace"]: entry
                for entry in (
                    await client.call_tool("registry_status", {})
                ).structured_content["result"]
            }
            assert status["blender"]["state"] == "Ready"
            assert status["blender"]["tool_count"] == len(FIXTURE_TOOLS)

    asyncio.run(scenario())
