"""CONN-BLENDER-CONNECTOR-R020: the declared surface matches the committed snapshot."""

from __future__ import annotations

from pathlib import Path

import pytest

from blender_connector.connector_contracts import UPSTREAM_TOOLS
from blender_connector.content_gen.sources import load_snapshot

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R020")

SNAPSHOT = (
    Path(__file__).resolve().parent.parent
    / "content"
    / "snapshots"
    / "blender.tools.json"
)


def test_declared_upstream_tools_match_the_snapshot() -> None:
    snapshot = load_snapshot(SNAPSHOT)
    declared = {t.tool: (t.description, dict(t.input_schema)) for t in UPSTREAM_TOOLS}
    assert declared == {t.name: (t.description, t.input_schema) for t in snapshot.tools}
