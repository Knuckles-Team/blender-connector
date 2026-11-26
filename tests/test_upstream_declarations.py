"""CONN-BLENDER-CONNECTOR-R001: the upstream declaration is data only."""

from __future__ import annotations

import pytest

from blender_connector.upstreams import (
    BLENDER_COMMAND,
    INHERIT_ENV_DEFAULT,
    INHERIT_ENV_SETTING,
    UPSTREAM_NAME,
    UPSTREAMS,
)

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R001")


def test_single_stdio_declaration() -> None:
    assert len(UPSTREAMS) == 1
    decl = UPSTREAMS[0]
    assert decl.name == UPSTREAM_NAME == "blender"
    assert decl.effective_namespace == "blender"
    assert decl.kind == "stdio"
    assert decl.command == BLENDER_COMMAND == "mcp-for-blender"
    assert decl.args == ()
    assert decl.env == {}
    # The upstream carries no read/write root flags: an explicit empty
    # grant, so no flag is ever passed and no root can reach the child.
    assert decl.sandbox is not None
    assert decl.sandbox.read == () and decl.sandbox.write == ()
    # Fifteen proxied tools carry no activation pressure.
    assert decl.activation == "active"
    assert decl.on_drift == "warn"


def test_inherit_env_default_carries_telemetry_and_socket() -> None:
    assert INHERIT_ENV_SETTING == "SCION_UPSTREAMS_INHERIT_ENV"
    names = set(INHERIT_ENV_DEFAULT.split(","))
    assert names == {
        "PATH",
        "HOME",
        "LANG",
        "DISABLE_TELEMETRY",
        "BLENDER_HOST",
        "BLENDER_PORT",
        "BLENDER_MCP_SAFE_MODE",
    }
