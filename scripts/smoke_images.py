"""Smoke test of the two images started by ``deploy/compose.yml`` (CONN-BLENDER-CONNECTOR-R018).

    python scripts/smoke_images.py [http://127.0.0.1:8000/mcp]

Waits for the connector, then checks three things through it: the readiness tool reports the
add-on socket reachable, ``blender_get_scene_info`` answers with scene data, and a rendered
``blender_look`` returns an image. Each check is a pure function of the tool result.
"""

from __future__ import annotations

import asyncio
import sys
import time
from typing import Any

DEFAULT_URL = "http://127.0.0.1:8000/mcp"
READY_TIMEOUT_S = 300.0
POLL_S = 5.0


def check_handshake(result: dict[str, Any]) -> list[str]:
    """Problems with the readiness result; empty when the add-on socket is reachable."""
    problems = []
    if not result.get("command_found"):
        problems.append("the upstream command is not on PATH in the connector image")
    if not (result.get("addon_socket") or {}).get("reachable"):
        problems.append(
            f"the add-on socket is not reachable: {(result.get('addon_socket') or {}).get('error')}"
        )
    return problems


def check_scene(text: str) -> list[str]:
    """Problems with the scene answer; empty when it carries scene data."""
    lowered = text.lower()
    if "timeout" in lowered or "not connected" in lowered:
        return [f"the scene query reports no Blender: {text[:200]}"]
    if "object" not in lowered and "scene" not in lowered:
        return [f"the scene answer holds no scene data: {text[:200]}"]
    return []


def check_look(content: list[Any]) -> list[str]:
    """Problems with the rendered view; empty when an image came back."""
    images = [
        item
        for item in content
        if getattr(item, "type", None) == "image" and getattr(item, "data", "")
    ]
    return [] if images else ["the rendered view returned no image"]


def _text(content: list[Any]) -> str:
    return " ".join(
        getattr(item, "text", "")
        for item in content
        if getattr(item, "type", None) == "text"
    )


async def _wait_ready(client: Any) -> dict[str, Any]:
    deadline = time.monotonic() + READY_TIMEOUT_S
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        result = await client.call_tool("handshake", {})
        last = dict(result.data or {})
        if not check_handshake(last):
            return last
        await asyncio.sleep(POLL_S)
    return last


async def run(url: str) -> list[str]:
    from fastmcp import Client

    async with Client(url) as client:
        problems = check_handshake(await _wait_ready(client))
        scene = await client.call_tool("blender_get_scene_info", {})
        problems += check_scene(_text(scene.content))
        look = await client.call_tool(
            "blender_look", {"shading": "rendered", "max_size": 256}
        )
        problems += check_look(look.content)
    return problems


def main(argv: list[str]) -> int:
    problems = asyncio.run(run(argv[1] if len(argv) > 1 else DEFAULT_URL))
    for problem in problems:
        print(f"smoke: {problem}", file=sys.stderr)
    print("smoke: ok" if not problems else "smoke: failed", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
