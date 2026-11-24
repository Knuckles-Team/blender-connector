# CONN-BLENDER-CONNECTOR-CONTENT — The connector serves its packaged Blender content

Owner: blender-connector. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R073`, `MEDULLA-TYPED-PACKS-R071.2`, `MEDULLA-TYPED-PACKS-R102.3`, `MEDULLA-TYPED-PACKS-R105`, `CONN-BLENDER-CONNECTOR-R001`.

## Purpose and user stories

The `blender-connector` server serves its packaged Blender skill, prompts and ontology to any client, with no wiring of its own. The content covers the full served tool surface: one ontology file, one skill and one prompt per functionality, generated from the authored source and the committed tool snapshot.

## Why a new spec

Search: `git grep -n "skill\|ontology\|prompt\|snapshot" -- specs` in this repository. The upstream bundle `CONN-BLENDER-CONNECTOR` owns the declaration, the probe, the deployment modes and the acceptance gates. No spec owns the packaged content, its generator or its drift gate. This spec owns the content only.

## User Scenarios & Testing

### User Story 1 - Find the Blender skill before the first call (Priority: P1)

An agent lists the server's resources, reads the Blender skill and activates the namespace.

**Acceptance Scenarios**:

1. **Given** the default server, **When** the client lists resources and prompts, **Then** it sees the skill at `skill://blender/SKILL.md`, the ontology at `ontology://blender-connector/blender.ttl` and the nine `blender-*` prompts (`CONN-BLENDER-CONNECTOR-CONTENT-R001`).
2. **Given** the skill, **When** the agent reads its tool table, **Then** every tool is named `blender_<tool>` and exists in the committed snapshot (`CONN-BLENDER-CONNECTOR-CONTENT-R004`).

### User Story 2 - Ask the graph about Blender use cases (Priority: P2)

A graph user asks which use cases exist and which tools each one walks through.

**Acceptance Scenarios**:

1. **Given** the ontology file, **When** the user reads the `BlenderUseCase` individuals, **Then** each one links to the app and names the tools it uses (`CONN-BLENDER-CONNECTOR-CONTENT-R003`).
2. **Given** a functionality, **When** the agent loads its prompt, **Then** the prompt names only tools that the snapshot lists (`CONN-BLENDER-CONNECTOR-CONTENT-R005`).

### User Story 3 - Keep content current after an upstream update (Priority: P2)

A maintainer updates `blender-mcp` and sees what changed before the next client hits it.

**Acceptance Scenarios**:

1. **Given** a changed tool schema, **When** the live gate runs, **Then** it names the stale tools (`CONN-BLENDER-CONNECTOR-CONTENT-R007`).
2. **Given** an edited generated file, **When** CI runs the offline gate, **Then** it fails with the file name (`CONN-BLENDER-CONNECTOR-CONTENT-R007`).

### Edge Cases

- A functionality names a tool that the snapshot lacks: generation fails (`CONN-BLENDER-CONNECTOR-CONTENT-R005`).
- A snapshot tool belongs to no functionality: the generator report lists it as unassigned; the skill table still shows it (`CONN-BLENDER-CONNECTOR-CONTENT-R002`).
- The upstream has no snapshot yet: a non-refresh run fails with a typed code (`CONN-BLENDER-CONNECTOR-CONTENT-R006`).
- An authored class names a parent outside the allowed set: generation fails with a typed code (`CONN-BLENDER-CONNECTOR-CONTENT-R003`).

## Requirements

- **FR-001**: Serve the packaged content with no wiring. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R001`.
- **FR-002**: Author the Blender app source; the functionalities partition the tool surface. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R002`.
- **FR-003**: Generate the ontology. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R003`.
- **FR-004**: Generate the skill. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R004`.
- **FR-005**: Generate a prompt per functionality. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R005`.
- **FR-006**: Generate content from the committed tool snapshot. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R006`.
- **FR-007**: Gate generated content against drift. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R007`.

## Success Criteria

- **SC-001**: The skill, the ontology file and nine prompts exist and are listed by the server. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R001`, `CONN-BLENDER-CONNECTOR-CONTENT-R003`, `CONN-BLENDER-CONNECTOR-CONTENT-R004`, `CONN-BLENDER-CONNECTOR-CONTENT-R005`.
- **SC-002**: Every snapshot tool belongs to at least one functionality. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R002`.
- **SC-003**: Two generator runs give identical bytes. Rows: `CONN-BLENDER-CONNECTOR-CONTENT-R006`, `CONN-BLENDER-CONNECTOR-CONTENT-R007`.

## Assumptions

- The tool names in the snapshot are the upstream names; the renderers add the `blender_` prefix when they write content.
- The engine rows `MEDULLA-TYPED-PACKS-R071.2`, `MEDULLA-TYPED-PACKS-R102.3` and `MEDULLA-TYPED-PACKS-R105` already cover how a pack ontology joins the core, so this spec adds no engine row.
- Only a host that carries the `blender-mcp` binary runs `--refresh` and `--live`.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). The upstream registry rows are in `CONN-BLENDER-CONNECTOR`. Out of scope: engine ontology composition and pack import services.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-BLENDER-CONNECTOR-CONTENT-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-BLENDER-CONNECTOR-CONTENT-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-BLENDER-CONNECTOR-CONTENT-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-BLENDER-CONNECTOR-CONTENT-R004` | [plan.md](plan.md) | T-004 | [test-spec.md](test-spec.md) |
| FR-005 | `CONN-BLENDER-CONNECTOR-CONTENT-R005` | [plan.md](plan.md) | T-005 | [test-spec.md](test-spec.md) |
| FR-006 | `CONN-BLENDER-CONNECTOR-CONTENT-R006` | [plan.md](plan.md) | T-006 | [test-spec.md](test-spec.md) |
| FR-007 | `CONN-BLENDER-CONNECTOR-CONTENT-R007` | [plan.md](plan.md) | T-007 | [test-spec.md](test-spec.md) |
