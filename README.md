# blender-connector

The Blender connector of the Arbora ecosystem: one MCP server that
**proxies the popular third-party `mcp-for-blender` upstream** (formerly
`blender-mcp`, the community Blender MCP) and **serves the packaged
Blender skill, prompts and ontology** alongside it, built on the shared
connector SDK (`scion-sdk`).

- **Upstream:** `blender-mcp` (a.k.a. `mcp-for-blender`) as a pooled stdio
  child, namespaced `blender`: every upstream tool is served as
  `blender_<tool>` with the tag `ns:blender` and the `scion/upstream`
  metadata, and the upstream's resources pass through unmodified.
- **Native tools:** `handshake` — a local readiness check (upstream binary
  on PATH, addon socket reachable) that never talks to Blender itself.
- **Registry tools:** `registry_list_namespaces`, `registry_activate`,
  `registry_deactivate`, `registry_status`, served by the SDK.
- **Content tier:** `skill://blender/SKILL.md`, `ontology://blender-connector/blender.ttl`
  and the `blender-*` prompts, generated from the committed tool snapshot
  by `scripts/generate_blender_content.py` (refresh / write / check / live).
- **Fleet:** one connector, one group (`blender`); the `scion/upstream`
  metadata is what Arbora loads and unloads.

The upstream talks to a running Blender through the addon's socket
(default `localhost:9876`). With Blender down, the `blender_*` calls
return the upstream's actionable timeout text while the server, the
registry and the content keep serving.

## Install

```sh
pip install -e .            # or: uv sync
blender-connector           # serve the MCP server (stdio by default)
blender-connector-probe     # probe the upstream after an update
```

The server needs the upstream binary `blender-mcp` on the `PATH`
(`uv tool install blender-mcp` or the `uvx mcp-for-blender` family).

## Operator settings

| Setting | Meaning | Start value |
|---|---|---|
| `DISABLE_TELEMETRY` | Telemetry opt-out, inherited by the upstream child | `1` |
| `BLENDER_HOST` / `BLENDER_PORT` | The addon socket address, inherited by the upstream child | `localhost` / `9876` |
| `SCION_UPSTREAMS_INHERIT_ENV` | The child environment whitelist that carries the rows above | `PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT` |
| `SCION_UPSTREAMS_FILE` | An operator overlay TOML (example: `docs/upstreams.example.toml`) | unset |
| `BLENDERTOOL` | Toggle for the connector-native tool surface | on |

A ready-to-paste MCP client entry ships in `mcp_config.json`.

## Development

```sh
scripts/bootstrap.sh                    # pinned environment + hooks
uvx pre-commit run --all-files          # the gate
uv run pytest tests -q                  # the suite (hermetic: fixture upstream)
uv run python scripts/generate_blender_content.py --check   # content drift gate
```

Specs live under `specs/` (`blender-connector`, `blender-connector-content`);
the shared pipelines spec standard applies. See [docs/](docs/index.md).
