# CONN-BLENDER-CONNECTOR — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The connector declares one upstream and the SDK registry serves it. This plan covers the `blender` declaration, the environment whitelist, the probe, the native readiness tool, the remote overlay example, the drift behavior and the two acceptance gates. The registry, the pool, the health report and the drift check are SDK rows (`SCION-CONNECTOR-CONTROL-R914`). The gateway group load is an Arbora row (`ARBORA-FLEET-R061`). The packaged content is a sibling spec (`CONN-BLENDER-CONNECTOR-CONTENT`).

## Technical Context

- **Language/Version**: Python 3.12–3.14
- **Primary Dependencies**: scion-sdk with the `mcp` extra, which pins the MCP framework; PyYAML for the authored source
- **Storage**: N/A; the connector stores nothing, and generated content is committed files
- **Testing**: pytest with a fixture upstream binary on `PATH`; the live gate is opt-in
- **Target Platform**: Linux developer hosts that carry the `mcp-for-blender` binary
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: the SDK owns the registry, the lifecycle and the drift check; the connector reimplements none of them
- **Scale/Scope**: 10 rows, one upstream declaration, one native tool

## Constitution Check

- One owner per concept: pass. The SDK owns the registry. This connector owns the Blender declaration and the native tool only.
- Extend before you create: pass. The content rows stay in `CONN-BLENDER-CONNECTOR-CONTENT`; this spec holds the upstream rows no spec owns.
- Connectors depend on the SDK and are called through the gateway: pass.
- No ratchets: pass. The rows add no suppression and no baseline.
- Complete rows: pass. Every row holds a caller chain, a shape and a test reference.

## Project Structure

```text
blender_connector/upstreams.py        new       UPSTREAM_NAME, BLENDER_COMMAND, INHERIT_ENV_*, upstreams()
blender_connector/__init__.py         new       the Connector identity, fleet name blender-connector
blender_connector/mcp_server.py       new       build_server / run / mcp_server entry points
blender_connector/mcp/__init__.py     new       register_blender_tools: the handshake tool
blender_connector/probe.py            new       blender-connector-probe
blender_connector/prompts/__init__.py new       prompt provider entry point
blender_connector/mcp_config.json     new       the ready-to-paste client entry
docs/upstreams.example.toml           new       the remote overlay example
tests/fixtures/fake_blender_mcp.py    new       the fixture upstream binary
tests/                                new       the row-bound test modules
```

## Phase 0: Research

Unknowns settled during the build:

- Which upstream to wrap: the popular third-party `mcp-for-blender` (formerly `blender-mcp`); no official Blender MCP is verifiable from the build host, recorded in the scope document.
- The served surface: ten tools for a plain MCP client, plus four resources; the app-extension-only tools are hidden from that client.
- SDK 0.7.1 requires an explicit `SandboxRoots` on stdio declarations, so the empty grant is spelled out.
- The namespace owns its tool-name prefix: the native tool is `handshake`, not `blender_handshake`.

## Phase 1: Design

### Existing system and reuse

The SDK registry owns the proxy, the namespace, the activation tools, the stdio pool, the health report, the elicitation pass-through and the drift check. This connector adds data, not mechanisms: one declaration, one native tool, one probe, one example overlay.

### Decisions

Namespacing: `blender_<tool>`, one lowercase word for the app. The native tool carries no prefix because the namespace owns it.

Activation: `active` in the declaration. The ten proxied tools carry no activation pressure, so the first list holds the full surface. An operator may still set lazy activation per deployment.

Environment: the child environment is clean by construction. The shipped whitelist `PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT,BLENDER_MCP_SAFE_MODE` is the only way the telemetry opt-out and the socket address reach the upstream.

Sandbox: an explicit empty grant. The upstream has no root flags, so both tuples are empty and no flag is ever passed.

Lifecycle: pooled stdio child, owned by the SDK (`SCION-CONNECTOR-CONTROL-R914.8`). The connector sets no lifecycle knob.

Remote mode: an operator overlay only. The repository ships an example with placeholder values; it is validated, not exercised.

### Acceptance phases

| Phase | Scope | Row |
|---|---|---|
| 1 | End to end against the fixture upstream: surface, read, write, native, registry | `CONN-BLENDER-CONNECTOR-R009` |
| 2 | Content tier green, live gate on a host with the binary | `CONN-BLENDER-CONNECTOR-R010` |

### Quality and release gates

Run `pipelines-hook spec-standard`, `pipelines-hook spec-status` and `ste-staged` on the spec directory. Phase gates run offline against the fixture upstream.

## Phase 2: Task approach

Order the work producer first. The SDK rows `SCION-CONNECTOR-CONTROL-R914.1` to `SCION-CONNECTOR-CONTROL-R914.5` land before `CONN-BLENDER-CONNECTOR-R001`. The gateway rows land before `CONN-BLENDER-CONNECTOR-R008`. The acceptance gates land last, one after each group of rows.

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

Entry point: the `blender-connector` console script calls `mcp_server` in `blender_connector/mcp_server.py`, which builds the server from the `Connector` identity in `blender_connector/__init__.py`. `_attach_upstreams` (`scion_sdk/connector/_serve.py`) calls `attach_upstreams` with `connector.upstreams` from `blender_connector/upstreams.py`. The probe is a development command with no run-time caller. Obsolete paths to delete: none.

## Cross-repo seams

- Upstream registry: provider `SCION-CONNECTOR-CONTROL-R914`, consumer `CONN-BLENDER-CONNECTOR-R001`; see [contracts/upstream-registry.md](contracts/upstream-registry.md).
- Gateway fleet: provider `ARBORA-FLEET-R061`, consumer `CONN-BLENDER-CONNECTOR-R008`; see [contracts/arbora-fleet.md](contracts/arbora-fleet.md).
