# CONN-BLENDER-CONNECTOR-CONTENT — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

`pyproject.toml` declares `blender-connector` as the connector identity, and the SDK serves the packaged content of `blender_connector` by convention. This plan adds the Blender content: one ontology file, one skill and nine prompts, all generated from the authored source and the committed tool snapshot, with a drift gate.

## Technical Context

- **Language/Version**: Python 3.12–3.14
- **Primary Dependencies**: scion-sdk with the `mcp` extra; PyYAML for the authored source
- **Storage**: N/A; the connector stores nothing, and generated content is committed files
- **Testing**: pytest against the package directories; the live gate runs on a host with the binary
- **Target Platform**: Linux developer hosts that carry the `blender-mcp` binary
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: the renderers are pure functions; the generator is the only writer
- **Scale/Scope**: 7 rows, one app, nine functionalities, ten snapshot tools

## Constitution Check

- One owner per concept: pass. The engine owns how a pack ontology joins the core. This spec owns the content only.
- Extend before you create: pass. The upstream rows stay in `CONN-BLENDER-CONNECTOR`; this spec holds the content rows no spec owns.
- Packs roll up to the core: pass. Every pack class has a subclass path to a core class under both parent-catalog namespaces, and no file imports the core ontology.
- Complete rows: pass. Every row holds a caller chain, a shape and a test reference.

## Project Structure

```text
blender_connector/ontology/blender.ttl      new       generated: pack classes, domain classes, individuals
blender_connector/skills/blender/SKILL.md   new       generated: front matter, activation, tool table
blender_connector/prompts/blender-*.json    new       generated, nine files
blender_connector/content_gen/              new       sources, skill, ontology, prompts, errors
scripts/generate_blender_content.py         new       --refresh, --write, --check, --live
content/apps/blender.yml                    new       authored summary, classes, functionalities
content/snapshots/blender.tools.json        new       generated from the live tool list
```

## Phase 0: Research

No unknowns. The pack rules are in `MEDULLA-TYPED-PACKS-R071.2`, `MEDULLA-TYPED-PACKS-R102.3` and `MEDULLA-TYPED-PACKS-R105`. The served surface facts are recorded in `CONN-BLENDER-CONNECTOR-R002`.

## Phase 1: Design

### Existing system and reuse

The server already lists packaged `skills/`, `ontology/` and `prompts/` with no wiring (`CONN-BLENDER-CONNECTOR-CONTENT-R001`). The generator writes into those directories, so no server code changes. The drift fingerprint reuses the SDK `compatibility_fingerprint`.

### Decisions

The ontology is self-contained: one file holds the pack classes, the domain classes and the individuals. It declares no `owl:imports` at all, so it never imports the core ontology and never needs a sibling pack. The dual-namespace parent edges cover both engine generations.

Tools are not ontology individuals. A use case names its tools with `usesToolName` strings, so the ontology stays small.

Authored text is separate from generated text. Authors edit `content/apps/blender.yml`. The generator owns every file it writes under `blender_connector/`.

The snapshot is the contract. The tool table, the prompt tool lists and the use case tool names all come from the snapshot names with the `blender_` prefix added; the renderers refuse a name the snapshot does not hold.

### Quality and release gates

Run `pipelines-hook spec-standard`, `pipelines-hook spec-status` and `ste-staged` on the spec directory. The offline drift gate runs in pre-commit and CI.

## Phase 2: Task approach

Order the work producer first: the source, then the generator, then the three renderers, then the committed files, then the drift gate.

## Complexity Tracking

none. The constitution check passed.

## Build contract

The change must meet these gate thresholds from the organization constitution table.

- Cyclomatic complexity 10 and cognitive complexity 15 per function (`pipelines_hooks/complexity`).
- Words per sentence 20 (`ste`).
- Clone similarity 0.85 blocking at 40 tokens (`dupehound`).
- KISS limits from `.config/kiss.toml`: 35 statements, 15 locals, 20 calls, 3 positional arguments, 4 indentation levels, 300 lines and 10 functions per file.
- Pre-land fast set: `format`, `hygiene`, `secrets`, `types`, `tests-fast`; post-land set: `spec`, `tests`, `supply-chain`.

Repository commands: `pre-commit run --all-files`, then `uv run pytest tests`. No scanner gaming, no suppression and no duplicate implementation: a row reuses the helper named in its `Shape:` sentence.

## Production caller chain

Entry point: `build_server` (`blender_connector/mcp_server.py`) calls the SDK `build_server`, which lists the packaged content directories. The generator is a development command and has no run-time caller. Obsolete paths to delete: none.

## Cross-repo seams

- Ontology joins the core: provider `MEDULLA-TYPED-PACKS-R105`, consumer `CONN-BLENDER-CONNECTOR-CONTENT-R003`; see [contracts/medulla-ontology.md](contracts/medulla-ontology.md).
