"""CONN-BLENDER-CONNECTOR-R009: phase 1 proves the connector end to end.

Against the fixture upstream: the full namespaced surface is listed,
a read and a write pass through the proxy unaltered, the native
readiness tool answers locally, and the registry reports ready.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import Client

from blender_connector.mcp_server import build_server

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R009")

# The fixture upstream serves exactly these tools, namespaced by app.
FIXTURE_TOOLS = ("execute_blender_code", "get_scene_info", "look")


def test_phase1_gate(blender_cli_factory, clean_upstream_env) -> None:
    blender_cli_factory()
    server = build_server(command_args=[])

    async def scenario() -> None:
        async with Client(server) as client:
            # The full proxied surface is listed under the namespace.
            tools = {tool.name for tool in await client.list_tools()}
            assert {f"blender_{name}" for name in FIXTURE_TOOLS} <= tools

            # A read passes through the proxy unaltered.
            read = await client.call_tool("blender_get_scene_info", {})
            assert read.is_error is False
            assert read.structured_content == {
                "objects": [],
                "materials": [],
                "collections": [],
            }

            # A write passes through the proxy unaltered.
            write = await client.call_tool(
                "blender_execute_blender_code", {"code": "print(42)"}
            )
            assert write.is_error is False
            assert write.structured_content == {"ok": True, "chars": 9}

            # The native readiness tool answers locally.
            handshake = await client.call_tool("handshake", {})
            assert handshake.structured_content["command_found"] is True

            # The registry reports the active upstream ready.
            status = {
                entry["namespace"]: entry
                for entry in (
                    await client.call_tool("registry_status", {})
                ).structured_content["result"]
            }
            assert status["blender"]["state"] == "ready"
            assert status["blender"]["tool_count"] == len(FIXTURE_TOOLS)

    asyncio.run(scenario())
