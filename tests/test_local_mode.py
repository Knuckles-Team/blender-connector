"""CONN-BLENDER-CONNECTOR-R004: an absent upstream degrades, the server stays up.

A binary missing from the PATH marks the upstream ``unavailable`` with
the SDK's refusal code; the registry tools, the native tool and the
content keep serving.
"""

from __future__ import annotations

import asyncio
import dataclasses

import pytest
from fastmcp import Client
from scion_sdk.mcp.upstreams import UpstreamDecl
from scion_sdk.mcp.upstreams.model import UPSTREAM_SPAWN_FAILED

import blender_connector
from blender_connector.mcp_server import build_server

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R004")


def _declare_absent(monkeypatch) -> None:
    """Serve the connector with an upstream command the host lacks."""
    from scion_sdk.mcp.upstreams import SandboxRoots

    decl = UpstreamDecl(
        name="blender",
        kind="stdio",
        command="blender-mcp-absent",
        activation="active",
        on_drift="warn",
        sandbox=SandboxRoots(
            read=(),
            write=(),
            read_flag="--automation-read-root",
            write_flag="--automation-write-root",
        ),
    )
    monkeypatch.setattr(
        blender_connector,
        "connector",
        dataclasses.replace(blender_connector.connector, upstreams=(decl,)),
    )


def test_missing_binary_marks_upstream_unavailable(
    clean_upstream_env, monkeypatch, tmp_path
) -> None:
    _declare_absent(monkeypatch)
    # No upstream binary on the PATH: the probe must report not_found.
    monkeypatch.setenv("PATH", str(tmp_path))
    server = build_server(command_args=[])

    async def scenario() -> None:
        async with Client(server) as client:
            tools = {tool.name for tool in await client.list_tools()}
            # No proxied tools, but the server surface stays up.
            assert "handshake" in tools
            assert not any(
                name.startswith("blender_") and name != "handshake" for name in tools
            )
            # The registry reports the spawn failure with its refusal code.
            status = {
                entry["namespace"]: entry
                for entry in (
                    await client.call_tool("registry_status", {})
                ).structured_content["result"]
            }
            assert status["blender"]["state"] == "unavailable"
            assert status["blender"]["last_error_code"] == UPSTREAM_SPAWN_FAILED
            # The readiness probe still answers and reports the gap.
            handshake = await client.call_tool("handshake", {})
            assert handshake.structured_content["command_found"] is False

    asyncio.run(scenario())
