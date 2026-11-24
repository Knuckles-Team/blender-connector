#!/usr/bin/env python
"""A fixture that stands in for the mcp-for-blender upstream.

It serves an MCP surface over stdio with three tools shaped like the
real upstream's (a read, a write and a viewport view). Test knobs are
environment variables:

- ``BLENDER_FIXTURE_VERSION``     the reported server version
- ``BLENDER_FIXTURE_DIE``         ``1``: exit at once, before the handshake
- ``BLENDER_FIXTURE_TOOL_DRIFT``  ``1``: give ``get_scene_info`` an extra parameter

The tests place one copy on the PATH under the name ``blender-mcp``.
"""

from __future__ import annotations

import os

from fastmcp import FastMCP


def main() -> int:
    if os.environ.get("BLENDER_FIXTURE_DIE") == "1":
        print(
            "blender-mcp: fixture dies before the handshake",
            file=__import__("sys").stderr,
        )
        return 1

    mcp = FastMCP(
        "blender",
        version=os.environ.get("BLENDER_FIXTURE_VERSION", "2.0.0-fixture"),
    )

    drift = os.environ.get("BLENDER_FIXTURE_TOOL_DRIFT") == "1"

    if drift:

        @mcp.tool
        async def get_scene_info(include_hidden: bool = False) -> dict:
            """The scene inventory of the fixture (drifted input schema)."""
            return {"objects": [], "materials": [], "collections": []}

    else:

        @mcp.tool
        async def get_scene_info() -> dict:
            """The scene inventory: objects, materials and collections."""
            return {"objects": [], "materials": [], "collections": []}

    @mcp.tool
    async def execute_blender_code(code: str) -> dict:
        """Execute Python code inside Blender and report the outcome."""
        return {"ok": True, "chars": len(code)}

    @mcp.tool
    async def look(max_size: int = 1000) -> str:
        """Capture the viewport and return it as an image."""
        return "viewport placeholder"

    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
