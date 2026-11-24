#!/usr/bin/env python
"""Generate and gate the Blender content tier (CONN-BLENDER-CONNECTOR-CONTENT-R006).

Modes:
  --refresh  start the upstream, read tools/list and the server version,
             and write content/snapshots/blender.tools.json
  --write    render the ontology, skill and prompts from the source and
             the snapshot, and write the generated files
  --check    render in memory and compare bytes with the committed files
             (the offline drift gate; needs no upstream)
  --live     refresh in memory and compare each tool fingerprint with
             the committed snapshot (the live drift gate; needs the
             upstream)

The tool names in a snapshot are the upstream names; the renderers add
the namespace prefix when they write content.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from scion_sdk.manifest.tool_schema import compatibility_fingerprint

from blender_connector.content_gen.errors import (
    CONTENT_SNAPSHOT_MISSING,
    ContentError,
)
from blender_connector.content_gen.ontology import render_ontology
from blender_connector.content_gen.prompts import (
    render_prompts,
    unassigned_tools,
)
from blender_connector.content_gen.skill import render_skill
from blender_connector.content_gen.sources import (
    BlenderSource,
    ToolInfo,
    ToolSnapshot,
    load_app_source,
    load_snapshot,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "content" / "apps" / "blender.yml"
DEFAULT_SNAPSHOT = REPO_ROOT / "content" / "snapshots" / "blender.tools.json"
PACKAGE_DIR = REPO_ROOT / "blender_connector"

REFRESH_TIMEOUT_DEFAULT_S = 30.0
REFRESH_TIMEOUT_MIN_S = 5.0
REFRESH_TIMEOUT_MAX_S = 300.0


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _committed_paths(source: BlenderSource, snapshot: ToolSnapshot) -> dict[str, str]:
    """File name to rendered text, for all three content kinds."""
    files: dict[str, str] = {}
    files["skills/blender/SKILL.md"] = render_skill(source, snapshot)
    files["ontology/blender.ttl"] = render_ontology(source, snapshot)
    files.update(
        {
            f"prompts/{name}": text
            for name, text in render_prompts(source, snapshot).items()
        }
    )
    return files


def refresh_snapshot(timeout_s: float) -> ToolSnapshot:
    """Start the upstream, read its tool list, and build the snapshot."""
    import shutil

    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    from blender_connector.upstreams import BLENDER_COMMAND

    binary = shutil.which(BLENDER_COMMAND)
    if binary is None:
        raise ContentError(
            CONTENT_SNAPSHOT_MISSING, f"{BLENDER_COMMAND!r} is not on the PATH"
        )

    async def read() -> tuple[str, list[dict[str, Any]]]:
        env = dict(os.environ, DISABLE_TELEMETRY="1")
        async with Client(
            StdioTransport(binary, [], env=env), timeout=timeout_s, mode="legacy"
        ) as client:
            info = await client.session.initialize()
            tools = await client.list_tools()
            return info.server_info.version, [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": dict(tool.inputSchema or {}),
                }
                for tool in tools
            ]

    version, raw_tools = asyncio.run(read())
    tools = tuple(
        ToolInfo(
            name=str(item["name"]),
            description=str(item.get("description", "")),
            input_schema=dict(item.get("input_schema", {}) or {}),
        )
        for item in raw_tools
    )
    return ToolSnapshot(
        app="blender",
        version=version,
        tools=tuple(sorted(tools, key=lambda tool: tool.name)),
    )


def snapshot_document(snapshot: ToolSnapshot) -> str:
    """The JSON text of the committed snapshot file."""
    return (
        json.dumps(
            {
                "app": snapshot.app,
                "version": snapshot.version,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema,
                    }
                    for tool in snapshot.tools
                ],
            },
            indent=2,
            ensure_ascii=True,
        )
        + "\n"
    )


def main(argv: list[str] | None = None) -> int:
    """The console entry point; one of --refresh, --write, --check, --live."""
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--refresh", action="store_true", help="write the snapshot from the upstream"
    )
    group.add_argument(
        "--write", action="store_true", help="write the generated content files"
    )
    group.add_argument(
        "--check", action="store_true", help="compare renders with committed files"
    )
    group.add_argument(
        "--live", action="store_true", help="compare a fresh read with the snapshot"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=REFRESH_TIMEOUT_DEFAULT_S,
        help=f"upstream timeout in seconds ({REFRESH_TIMEOUT_MIN_S}..{REFRESH_TIMEOUT_MAX_S})",
    )
    args = parser.parse_args(argv)
    if not REFRESH_TIMEOUT_MIN_S <= args.timeout <= REFRESH_TIMEOUT_MAX_S:
        print(
            "timeout must be within the documented range",
            file=sys.stderr,
        )
        return 2

    if args.refresh:
        snapshot = refresh_snapshot(args.timeout)
        _write(DEFAULT_SNAPSHOT, snapshot_document(snapshot))
        print(f"snapshot written: {len(snapshot.tools)} tools @ {snapshot.version}")
        return 0

    if not DEFAULT_SNAPSHOT.exists():
        print(
            f"snapshot missing: {DEFAULT_SNAPSHOT} (run --refresh)",
            file=sys.stderr,
        )
        return 1

    source = load_app_source(DEFAULT_SOURCE)
    snapshot = load_snapshot(DEFAULT_SNAPSHOT)

    if args.write:
        files = _committed_paths(source, snapshot)
        for relative, text in files.items():
            _write(PACKAGE_DIR / relative, text)
        unassigned = unassigned_tools(source, snapshot)
        print(f"content written: {len(files)} files")
        if unassigned:
            print(f"note: no functionality names: {', '.join(unassigned)}")
        return 0

    if args.check:
        files = _committed_paths(source, snapshot)
        drifted = [
            name
            for name, text in files.items()
            if (PACKAGE_DIR / name).read_text(encoding="utf-8") != text
        ]
        if drifted:
            print(f"CONTENT_DRIFT: {', '.join(drifted)}", file=sys.stderr)
            return 1
        print(f"content check: {len(files)} files match")
        return 0

    # --live: compare a fresh read against the committed snapshot.
    fresh = refresh_snapshot(args.timeout)
    committed = {tool.name: tool for tool in snapshot.tools}
    stale = [
        tool.name
        for tool in fresh.tools
        if tool.name in committed
        and compatibility_fingerprint(tool.name, tool.input_schema)
        != compatibility_fingerprint(
            committed[tool.name].name, committed[tool.name].input_schema
        )
    ]
    missing = [tool.name for tool in fresh.tools if tool.name not in committed]
    if fresh.version != snapshot.version:
        print(
            f"note: upstream version {fresh.version} differs from snapshot "
            f"{snapshot.version}",
            file=sys.stderr,
        )
    if stale or missing:
        print(
            f"CONTENT_SNAPSHOT_STALE: changed={stale} new={missing}",
            file=sys.stderr,
        )
        return 1
    print("live check: snapshot matches the upstream")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
