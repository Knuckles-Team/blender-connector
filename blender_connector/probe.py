"""Probe the Blender upstream for MCP support (CONN-BLENDER-CONNECTOR-R003).

The operator or a host job runs it after each upstream update. It starts
the declared command exactly as the registry would (telemetry off),
performs the MCP handshake and a ``tools/list``, and prints one JSON
result to stderr: stdout stays clean for the stdio transport, and the
exit code is the machine signal. It writes no file, and exits non-zero
when the upstream no longer answers: a missing binary reports
``BLENDER_MCP_NOT_FOUND``, a binary that does not complete the handshake
reports ``BLENDER_MCP_NO_MCP``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from collections.abc import Sequence
from typing import Any

from .upstreams import BLENDER_COMMAND

#: A binary the host does not carry.
BLENDER_MCP_NOT_FOUND = "BLENDER_MCP_NOT_FOUND"
#: A binary that does not answer the MCP handshake.
BLENDER_MCP_NO_MCP = "BLENDER_MCP_NO_MCP"

TIMEOUT_DEFAULT_S = 20.0
TIMEOUT_MIN_S = 5.0
TIMEOUT_MAX_S = 120.0

__all__ = [
    "BLENDER_MCP_NO_MCP",
    "BLENDER_MCP_NOT_FOUND",
    "main",
    "probe_upstream",
]


async def probe_upstream(timeout_s: float) -> dict[str, Any]:
    """One probe: the handshake result, or the refusal code for a bad binary."""
    binary = shutil.which(BLENDER_COMMAND)
    if binary is None:
        return {
            "upstream": "blender",
            "exposes_mcp": False,
            "code": BLENDER_MCP_NOT_FOUND,
        }
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    env = dict(os.environ, DISABLE_TELEMETRY="1")
    try:
        async with Client(
            StdioTransport(binary, [], env=env), timeout=timeout_s, mode="legacy"
        ) as client:
            info = await client.session.initialize()
            tools = await client.list_tools()
    except Exception:
        return {
            "upstream": "blender",
            "exposes_mcp": False,
            "code": BLENDER_MCP_NO_MCP,
        }
    return {
        "upstream": "blender",
        "exposes_mcp": True,
        "version": info.server_info.version,
        "tool_count": len(tools),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """The console entry point; one JSON result on stderr, exit code the signal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=float,
        default=TIMEOUT_DEFAULT_S,
        help=f"handshake timeout in seconds ({TIMEOUT_MIN_S}..{TIMEOUT_MAX_S})",
    )
    args = parser.parse_args(argv)
    if not TIMEOUT_MIN_S <= args.timeout <= TIMEOUT_MAX_S:
        print(
            f"probe timeout must be within {TIMEOUT_MIN_S}..{TIMEOUT_MAX_S} seconds",
            file=sys.stderr,
        )
        return 2
    result = asyncio.run(probe_upstream(args.timeout))
    print(json.dumps(result, indent=2), file=sys.stderr)
    return 0 if result["exposes_mcp"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
