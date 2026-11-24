# CONN-BLENDER-CONNECTOR-CONTENT quickstart

Run the proof of each row from a fresh checkout after `uv sync`.

- CONN-BLENDER-CONNECTOR-CONTENT-R001: `uv run pytest tests/test_content_surfaces.py -q`
- CONN-BLENDER-CONNECTOR-CONTENT-R002: `uv run pytest tests/test_content_drift.py::test_functionality_partition_covers_the_snapshot -q`
- CONN-BLENDER-CONNECTOR-CONTENT-R003: `uv run pytest tests/test_content_drift.py::test_committed_content_matches_snapshot -q`
- CONN-BLENDER-CONNECTOR-CONTENT-R004: `uv run pytest tests/test_content_drift.py::test_committed_content_matches_snapshot -q`
- CONN-BLENDER-CONNECTOR-CONTENT-R005: `uv run pytest tests/test_content_drift.py::test_render_refuses_an_unknown_tool -q`
- CONN-BLENDER-CONNECTOR-CONTENT-R006: `uv run pytest tests/test_content_drift.py::test_committed_content_matches_snapshot -q`
- CONN-BLENDER-CONNECTOR-CONTENT-R007: `uv run pytest tests/test_content_drift.py -q`

Regenerate content with `uv run python scripts/generate_blender_content.py --write`. Check it with `--check`. Refresh the snapshot with `--refresh` on a host that has the `blender-mcp` binary. Run the live gate with `--live`.
