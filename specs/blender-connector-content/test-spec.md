# CONN-BLENDER-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-BLENDER-CONNECTOR-CONTENT-R001` | `tests/test_content_surfaces.py::test_default_content_surfaces` | The listings include `skill://blender/SKILL.md`, `ontology://blender-connector/blender.ttl` and each of the nine packaged prompts. |
| T-002 | `CONN-BLENDER-CONNECTOR-CONTENT-R002` | `tests/test_content_drift.py::test_functionality_partition_covers_the_snapshot` | The committed source's functionalities partition the committed snapshot: no tool is unassigned. |
| T-003 | `CONN-BLENDER-CONNECTOR-CONTENT-R003` | `tests/test_content_drift.py::test_committed_content_matches_snapshot` | The committed `blender.ttl` matches the render of its sources byte for byte, pinning the pack classes, the dual parent edges and the individuals. |
| T-004 | `CONN-BLENDER-CONNECTOR-CONTENT-R004` | `tests/test_content_drift.py::test_committed_content_matches_snapshot` | The committed `SKILL.md` matches the render, pinning the full tool table against the snapshot. |
| T-005 | `CONN-BLENDER-CONNECTOR-CONTENT-R005` | `tests/test_content_drift.py::test_render_refuses_an_unknown_tool` | A functionality that names a tool the snapshot lacks fails with `CONTENT_PROMPT_TOOL_UNKNOWN`. The nine committed prompt files match the render through the drift gate. |
| T-006 | `CONN-BLENDER-CONNECTOR-CONTENT-R006` | `tests/test_content_drift.py::test_committed_content_matches_snapshot` | The committed content equals the render of its sources, so two runs give identical bytes. A run without the snapshot fails with `CONTENT_SNAPSHOT_MISSING`. |
| T-007 | `CONN-BLENDER-CONNECTOR-CONTENT-R007` | `tests/test_content_drift.py::test_committed_content_matches_snapshot` | The offline gate passes as a subprocess against the committed content and fails on a drift. The live gate is an operator step on a host with the binary; a host without it records the gap. |
| T-008 | `CONN-BLENDER-CONNECTOR-CONTENT-R008` | `tests/test_content_surfaces.py::test_the_kit_review_prompt_is_listed` | The server lists the prompt `blender-export_and_validate_kit`; the committed skill holds its four steps; the drift gate passes. |
| T-009 | `CONN-BLENDER-CONNECTOR-CONTENT-R009` | `tests/test_ontology.py::test_scene_and_file_are_creative_works` (planned) | `blender.ttl` states `BlenderFile` and `Scene` as subclasses of the core `CreativeWork`. |
