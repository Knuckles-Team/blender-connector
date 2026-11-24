"""CONN-BLENDER-CONNECTOR-R007: a drifted upstream reports ``drifted``.

The declaration pins ``expected_fingerprint``; a listing whose tools do
not match the pin reports the namespace ``drifted`` under the
``on_drift: warn`` policy, while the rest of the server keeps serving.
"""

from __future__ import annotations

import asyncio
import dataclasses

import pytest
from fastmcp import Client
from scion_sdk.mcp.upstreams import SandboxRoots, UpstreamDecl

import blender_connector
from blender_connector.mcp_server import build_server

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R007")


def _declare_pinned(monkeypatch) -> None:
    """The fixture upstream against a fingerprint it cannot match."""
    decl = UpstreamDecl(
        name="blender",
        kind="stdio",
        command="blender-mcp",
        activation="active",
        on_drift="warn",
        expected_fingerprint="0" * 64,
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


def test_drifted_upstream_reports_drifted(blender_cli_factory, clean_upstream_env, monkeypatch) -> None:
    blender_cli_factory()
    _declare_pinned(monkeypatch)
    server = build_server(command_args=[])

    async def scenario() -> None:
        async with Client(server) as client:
            await client.list_tools()
            status = {
                entry["namespace"]: entry
                for entry in (
                    await client.call_tool("registry_status", {})
                ).structured_content["result"]
            }
            assert status["blender"]["state"] == "drifted"
            # The connector surface stays up alongside the drifted upstream.
            tools = {tool.name for tool in await client.list_tools()}
            assert "handshake" in tools

    asyncio.run(scenario())
