# CONN-BLENDER-CONNECTOR quickstart

Run the proof of each row from a fresh checkout after `uv sync`. Each command exercises the row through the production server.

- CONN-BLENDER-CONNECTOR-R001: `uv run pytest tests/test_upstream_declarations.py -q`
- CONN-BLENDER-CONNECTOR-R002: `uv run pytest tests/test_tool_budget.py -q`
- CONN-BLENDER-CONNECTOR-R003: `uv run pytest tests/test_probe.py -q`
- CONN-BLENDER-CONNECTOR-R004: `uv run pytest tests/test_local_mode.py -q`
- CONN-BLENDER-CONNECTOR-R005: `uv run pytest tests/test_remote_overlay.py -q`
- CONN-BLENDER-CONNECTOR-R006: `uv run pytest tests/test_phase1_gate.py -q`
- CONN-BLENDER-CONNECTOR-R007: `uv run pytest tests/test_drift.py -q`
- CONN-BLENDER-CONNECTOR-R008: `uv run pytest -q` (the SDK conformance suite runs inside the suite)
- CONN-BLENDER-CONNECTOR-R009: `uv run pytest tests/test_phase1_gate.py -q`
- CONN-BLENDER-CONNECTOR-R010: `uv run pytest tests/test_content_drift.py -q` plus `uv run python scripts/generate_blender_content.py --check`

The live gate runs only on a host that has the `blender-mcp` binary: `uv run python scripts/generate_blender_content.py --live`, together with `uv run blender-connector-probe`.
