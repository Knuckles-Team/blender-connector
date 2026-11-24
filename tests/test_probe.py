"""CONN-BLENDER-CONNECTOR-R003: the probe reports the upstream's surface."""

from __future__ import annotations

import asyncio

import pytest

from blender_connector.probe import (
    BLENDER_MCP_NO_MCP,
    BLENDER_MCP_NOT_FOUND,
    probe_upstream,
)

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R003")


def test_probe_reports_the_fixture_upstream(blender_cli_factory) -> None:
    blender_cli_factory(version="9.9.9-fixture")
    result = asyncio.run(probe_upstream(20.0))
    assert result["exposes_mcp"] is True
    assert result["version"] == "9.9.9-fixture"
    assert result["tool_count"] == 3


def test_probe_reports_a_missing_binary(clean_upstream_env, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    result = asyncio.run(probe_upstream(20.0))
    assert result["exposes_mcp"] is False
    assert result["code"] == BLENDER_MCP_NOT_FOUND


def test_probe_reports_a_dead_upstream(blender_cli_factory) -> None:
    blender_cli_factory(die=True)
    result = asyncio.run(probe_upstream(20.0))
    assert result["exposes_mcp"] is False
    assert result["code"] == BLENDER_MCP_NO_MCP
