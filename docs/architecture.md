# Architecture

The `blender_connector` package owns one declared upstream and the
connector-native tools; the shared connector SDK owns everything else.

```
MCP client
   │  (stdio by default)
   ▼
blender-connector (scion_sdk Connector, fleet name blender-connector)
┌──────────────────────────────────────────────────────────────┐
│ native:      handshake                                        │
│ registry:    registry_list_namespaces, registry_activate,     │
│              registry_deactivate, registry_status             │
│ proxied:     blender_<tool>  (tag ns:blender, scion/upstream) │
│               └─ stdio child: mcp-for-blender ──socket──► Blender  │
│ content:     skill://blender/SKILL.md                         │
│              ontology://blender-connector/blender.ttl         │
│              prompts: blender-<functionality>                  │
└──────────────────────────────────────────────────────────────┘
```

Layers:

- `blender_connector/upstreams.py` — the one `UpstreamDecl`: stdio,
  command `mcp-for-blender`, explicit empty sandbox grant (no root flags exist
  on the upstream), `activation=active`, `on_drift=warn`.
- `blender_connector/mcp/` — `register_blender_tools` (toggle
  `BLENDERTOOL`) registers the `handshake` tool.
- `blender_connector/content_gen/` — pure renderers from the authored
  source (`content/apps/blender.yml`) and the committed snapshot
  (`content/snapshots/blender.tools.json`) to the skill, ontology and
  prompt files; driven by `scripts/generate_blender_content.py`.
- SDK — namespacing, pooling, health, drift, overlay merging, content
  publication, readiness, fleet registration, transports.

The namespace `blender` owns the `blender_` prefix: connector-native tools
must not carry it (the SDK refuses with `UPSTREAM_TOOL_COLLISION`).

Operator overlays (a TOML named by `SCION_UPSTREAMS_FILE`) can switch the
upstream to `kind: http` for a remote host serving the surface; see
[deployment](deployment.md) and `docs/upstreams.example.toml`.
