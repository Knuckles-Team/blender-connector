# CONN-BLENDER-CONNECTOR — Implementation tasks

Governing spec: [spec.md](spec.md). Design: [plan.md](plan.md). Rows: [requirements.md](requirements.md).

Each task line reads `- [ ] T001 [P] [US1] <ID>-R001 description`. Order is producer first.

- [x] T001 [US1] CONN-BLENDER-CONNECTOR-R001 Declare the mcp-for-blender stdio upstream.
- [x] T002 [US1] CONN-BLENDER-CONNECTOR-R002 Serve the full proxied surface; the initial list holds it all.
- [x] T003 [US1] CONN-BLENDER-CONNECTOR-R003 Probe the upstream for MCP support.
- [x] T004 [US1] CONN-BLENDER-CONNECTOR-R004 Behavior: an absent upstream degrades, the server stays up.
- [x] T005 [US1] CONN-BLENDER-CONNECTOR-R005 Behavior: an operator overlay switches the upstream to a remote endpoint.
- [x] T006 [US1] CONN-BLENDER-CONNECTOR-R006 A connector-native readiness tool.
- [x] T007 [US1] CONN-BLENDER-CONNECTOR-R007 Behavior: a drifted upstream reports drifted.
- [x] T008 [US1] CONN-BLENDER-CONNECTOR-R008 Wiring: the connector registers once and the fleet loads the blender group.
- [x] T009 [US1] CONN-BLENDER-CONNECTOR-R009 Acceptance: phase 1 proves the connector end to end.
- [x] T010 [US1] CONN-BLENDER-CONNECTOR-R010 Acceptance: phase 2 proves the content tier and the live surface.
