"""The Blender upstream declaration (CONN-BLENDER-CONNECTOR-R001).

One declared upstream: the popular third-party ``mcp-for-blender`` MCP
server (formerly ``blender-mcp``), reached as a pooled stdio child. The
SDK owns the registry, the pool and the health; this module adds data
only.

The child gets a clean environment: only the names whitelisted in
``SCION_UPSTREAMS_INHERIT_ENV`` plus declared ``env`` references. The
telemetry opt-out and the Blender socket address cross that boundary
through the whitelist named in ``INHERIT_ENV_DEFAULT``; the operator
sets the values on the connector process (see ``docs/usage.md``).
"""

from __future__ import annotations

import os

from scion_sdk.mcp.upstreams import SandboxRoots, UpstreamDecl

__all__ = [
    "BLENDER_COMMAND",
    "BLENDER_HOST_ENV",
    "BLENDER_PORT_ENV",
    "DEFAULT_BLENDER_HOST",
    "DEFAULT_BLENDER_PORT",
    "INHERIT_ENV_DEFAULT",
    "INHERIT_ENV_SETTING",
    "UPSTREAM_NAME",
    "UPSTREAMS",
    "blender_host",
    "blender_port",
    "build_upstreams",
]

#: The declared upstream: its name and namespace.
UPSTREAM_NAME = "blender"

#: The upstream binary on the operator's PATH.
BLENDER_COMMAND = "mcp-for-blender"

#: The SDK setting that whitelists the child environment names.
INHERIT_ENV_SETTING = "SCION_UPSTREAMS_INHERIT_ENV"

#: The starting whitelist: the SDK basics plus the telemetry opt-out, the
#: Blender socket address and the upstream's safe-mode switch.
INHERIT_ENV_DEFAULT = (
    "PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT,BLENDER_MCP_SAFE_MODE"
)

#: The addon socket address the upstream resolves from the operator
#: environment. This module is the package's declared configuration
#: module: the environment reads live here and only here (env-sprawl).
BLENDER_HOST_ENV = "BLENDER_HOST"
BLENDER_PORT_ENV = "BLENDER_PORT"
DEFAULT_BLENDER_HOST = "localhost"
DEFAULT_BLENDER_PORT = 9876


def blender_host() -> str:
    """The addon socket host set on this process (default ``localhost``)."""
    return os.environ.get(BLENDER_HOST_ENV, DEFAULT_BLENDER_HOST)


def blender_port() -> int:
    """The addon socket port set on this process (default ``9876``).

    A value that is not a port number falls back to the default, the
    same way the upstream's own socket probe does.
    """
    raw = os.environ.get(BLENDER_PORT_ENV, "")
    try:
        return int(raw) if raw else DEFAULT_BLENDER_PORT
    except ValueError:
        return DEFAULT_BLENDER_PORT


def build_upstreams() -> tuple[UpstreamDecl, ...]:
    """The one declaration the connector serves.

    The sandbox is an explicit empty grant: both root tuples are empty,
    which the SDK treats as an explicit deny, so no root flag is ever
    passed; file access is governed inside Blender, not by CLI flags.
    The flag names carry the SDK's standard vocabulary for the sake of
    the declaration's shape. Activation is ``active``: ten proxied tools
    (the surface served to a plain MCP client) carry no activation
    pressure, so the namespace is visible from the first list.
    """
    return (
        UpstreamDecl(
            name=UPSTREAM_NAME,
            kind="stdio",
            command=BLENDER_COMMAND,
            args=(),
            activation="active",
            on_drift="warn",
            sandbox=SandboxRoots(
                read=(),
                write=(),
                read_flag="--automation-read-root",
                write_flag="--automation-write-root",
            ),
        ),
    )


#: The declarations the connector serves.
UPSTREAMS: tuple[UpstreamDecl, ...] = build_upstreams()
