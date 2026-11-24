"""The connector-native tools of the Blender connector.

One readiness probe that stays local: it checks the upstream binary on
PATH and the Blender addon socket, so an agent gets a deterministic
answer before the first ``blender_*`` call. It never talks to Blender
itself: every Blender interaction stays in the upstream.
"""

from __future__ import annotations

import os
import shutil
import socket
from typing import Any

#: The default Blender addon socket address, as the upstream resolves it.
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9876

#: The bounded probe window for the socket check.
PROBE_TIMEOUT_S = 2.0


def _socket_state(host: str, port: int) -> dict[str, Any]:
    """One bounded TCP probe of the addon socket; no protocol traffic."""
    try:
        with socket.create_connection((host, port), timeout=PROBE_TIMEOUT_S):
            return {"reachable": True, "error": None}
    except OSError as exc:
        return {"reachable": False, "error": str(exc)}


def register_blender_tools(mcp: Any) -> None:
    """Register the connector-native tools (toggle: ``BLENDERTOOL``)."""

    # The namespace ``blender`` owns the ``blender_`` prefix, so the
    # connector-native tool carries no such prefix (UPSTREAM_TOOL_COLLISION).
    @mcp.tool(
        title="Blender readiness",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        tags={"blender"},
    )
    async def handshake() -> dict[str, Any]:
        """Check the Blender toolchain before the first blender_* call.

        Reports whether the upstream binary is on PATH, and whether the
        Blender addon socket (``BLENDER_HOST`` / ``BLENDER_PORT``,
        defaults ``localhost:9876``) answers a bounded TCP probe. A
        missing socket usually means Blender is not running with the
        addon enabled, or the host and port do not match the running
        instance.
        """
        host = os.environ.get("BLENDER_HOST", DEFAULT_HOST)
        raw_port = os.environ.get("BLENDER_PORT", "")
        try:
            port = int(raw_port) if raw_port else DEFAULT_PORT
        except ValueError:
            port = DEFAULT_PORT
        socket_state = _socket_state(host, port)
        return {
            "upstream_command": "blender-mcp",
            "command_found": shutil.which("blender-mcp") is not None,
            "host": host,
            "port": port,
            "addon_socket": socket_state,
            "ready": socket_state["reachable"],
            "hint": None
            if socket_state["reachable"]
            else (
                "Start Blender with the mcp-for-blender addon enabled; the "
                "socket must listen on the reported host:port."
            ),
        }
