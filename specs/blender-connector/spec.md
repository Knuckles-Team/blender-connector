# CONN-BLENDER-CONNECTOR — The Blender upstream registry

Owner: blender-connector. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R914`, `ARBORA-FLEET-R059`, `ARBORA-FLEET-R060`, `ARBORA-FLEET-R061`, `CONN-BLENDER-CONNECTOR-CONTENT-R001`.

## Purpose and user stories

The `blender-connector` server is the one MCP facade for Blender scene work. It proxies the popular third-party `mcp-for-blender` upstream (formerly `blender-mcp`) under the namespace `blender` and serves the packaged Blender skill, prompts and ontology alongside. This spec owns the Blender-specific part: the upstream declaration, the deployment modes, the native tool and the acceptance gates.

## Why a new spec

Search: `git grep -n "upstream\|mcp-for-blender\|overlay\|stdio" -- specs` in this repository. The content bundle `CONN-BLENDER-CONNECTOR-CONTENT` owns the packaged content only. No spec owns the upstream declaration, the probe, the deployment modes or the phase gates. The generic registry is an SDK capability and lives in `SCION-CONNECTOR-CONTROL-R914`. This spec holds no registry code.

## User Scenarios & Testing

### User Story 1 - Do Blender scene work through one server (Priority: P1)

An agent author connects to one server and inspects the scene, builds geometry, authors materials, reviews the viewport and imports assets without wiring the upstream itself.

**Acceptance Scenarios**:

1. **Given** the server has started with the upstream active, **When** the agent lists tools, **Then** it sees the four registry tools, the native tool and every proxied `blender_*` tool (`CONN-BLENDER-CONNECTOR-R002`).
2. **Given** a session, **When** it calls `blender_get_scene_info`, **Then** the call passes through the proxy unaltered to the upstream child (`CONN-BLENDER-CONNECTOR-R009`).

### User Story 2 - Run the upstream locally, or remotely when a host serves it (Priority: P2)

An operator picks the deployment mode without changing code.

**Acceptance Scenarios**:

1. **Given** the default server, **When** it lists the upstream, **Then** it reaches the local `mcp-for-blender` binary with a clean child environment and telemetry off (`CONN-BLENDER-CONNECTOR-R001`, `CONN-BLENDER-CONNECTOR-R004`).
2. **Given** an overlay file for a remote host, **When** the server starts, **Then** the upstream is reached over HTTP with a credential reference and a TLS profile name (`CONN-BLENDER-CONNECTOR-R005`).

### User Story 3 - Keep the surface honest across upstream updates (Priority: P2)

A maintainer updates the upstream and sees what changed before the next client hits it.

**Acceptance Scenarios**:

1. **Given** an updated `mcp-for-blender` binary, **When** the operator runs the probe, **Then** it reports the version and the tool count, or a typed code when the binary no longer answers (`CONN-BLENDER-CONNECTOR-R003`).
2. **Given** a changed tool list, **When** the live gate runs, **Then** it names the stale tools (`CONN-BLENDER-CONNECTOR-R010`).

### User Story 4 - Load the blender group behind the gateway (Priority: P3)

A gateway user loads and unloads the Blender tools as one group.

**Acceptance Scenarios**:

1. **Given** the connector is registered once, **When** the user loads the group `blender`, **Then** only the `blender_*` tools load (`CONN-BLENDER-CONNECTOR-R008`).

### Edge Cases

- The upstream binary is missing from `PATH`: the upstream is `unavailable` with a typed code and the server stays up (`CONN-BLENDER-CONNECTOR-R004`).
- The Blender addon socket is down: the `blender_*` calls return the upstream's actionable timeout text while the server, the registry and the content keep serving (`CONN-BLENDER-CONNECTOR-R004`).
- A literal credential in an overlay: the overlay refuses (`CONN-BLENDER-CONNECTOR-R005`).
- An upstream update changes the tool list: the probe and the drift gate report it (`CONN-BLENDER-CONNECTOR-R003`, `CONN-BLENDER-CONNECTOR-R007`, `CONN-BLENDER-CONNECTOR-R010`).
- A local tool name carries the `blender_` prefix: the server refuses it at build time (`CONN-BLENDER-CONNECTOR-R002`).

## Requirements

- **FR-001**: Declare the `mcp-for-blender` stdio upstream. Rows: `CONN-BLENDER-CONNECTOR-R001`.
- **FR-002**: Serve the full proxied surface and keep the initial list honest. Rows: `CONN-BLENDER-CONNECTOR-R002`.
- **FR-003**: Probe the upstream for MCP support. Rows: `CONN-BLENDER-CONNECTOR-R003`.
- **FR-004**: Support local, remote and degraded deployment. Rows: `CONN-BLENDER-CONNECTOR-R004`, `CONN-BLENDER-CONNECTOR-R005`.
- **FR-005**: Expose a native readiness tool with typed output. Rows: `CONN-BLENDER-CONNECTOR-R006`.
- **FR-006**: Report drift instead of hiding it. Rows: `CONN-BLENDER-CONNECTOR-R007`.
- **FR-007**: Register once and load the group behind the gateway. Rows: `CONN-BLENDER-CONNECTOR-R008`.
- **FR-008**: Pass two acceptance gates. Rows: `CONN-BLENDER-CONNECTOR-R009`, `CONN-BLENDER-CONNECTOR-R010`.

## Success Criteria

- **SC-001**: The first tool list holds exactly eight tools against a three-tool fixture upstream and fifteen against the live snapshot surface. Rows: `CONN-BLENDER-CONNECTOR-R002`.
- **SC-002**: An unavailable upstream hides only its own proxied tools. Rows: `CONN-BLENDER-CONNECTOR-R004`.
- **SC-003**: A drifted upstream reports `drifted` while the rest of the server keeps serving. Rows: `CONN-BLENDER-CONNECTOR-R007`.
- **SC-004**: Phase 1 passes end to end against the fixture upstream. Rows: `CONN-BLENDER-CONNECTOR-R009`.

## Assumptions

- The upstream binary `mcp-for-blender` (the `mcp-for-blender` project) is available on the operator host through `uv tool install mcp-for-blender`.
- The surface served to a plain MCP client holds ten tools. The upstream's app-extension-only tools (the viewport app surface and mention search) are not part of that surface and are not in the committed snapshot; a client with app support is a snapshot refresh plus a source extension, gated by the drift checks.
- The SDK registry rows (`SCION-CONNECTOR-CONTROL-R914`) land before the rows here that depend on them; scion-sdk 0.7.1 from PyPI satisfies them.
- No official Blender MCP is verifiable from the build host. The wrapped upstream is the popular third-party `mcp-for-blender`, recorded in the scope document.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the registry code, the pool, the health report and the drift check (all in the SDK), the group load rows (in the gateway), and the packaged content rows (in `CONN-BLENDER-CONNECTOR-CONTENT`).

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-BLENDER-CONNECTOR-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-BLENDER-CONNECTOR-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-BLENDER-CONNECTOR-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-BLENDER-CONNECTOR-R004`, `CONN-BLENDER-CONNECTOR-R005` | [plan.md](plan.md) | T-004 to T-005 | [test-spec.md](test-spec.md) |
| FR-005 | `CONN-BLENDER-CONNECTOR-R006` | [plan.md](plan.md) | T-006 | [test-spec.md](test-spec.md) |
| FR-006 | `CONN-BLENDER-CONNECTOR-R007` | [plan.md](plan.md) | T-007 | [test-spec.md](test-spec.md) |
| FR-007 | `CONN-BLENDER-CONNECTOR-R008` | [plan.md](plan.md) | T-008 | [test-spec.md](test-spec.md) |
| FR-008 | `CONN-BLENDER-CONNECTOR-R009`, `CONN-BLENDER-CONNECTOR-R010` | [plan.md](plan.md) | T-009 to T-010 | [test-spec.md](test-spec.md) |
