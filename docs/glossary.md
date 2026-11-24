# Glossary

| Term | Meaning |
|---|---|
| upstream | The external `mcp-for-blender` (a.k.a. `blender-mcp`) MCP server that this connector proxies |
| namespace | The `blender` prefix that owns `blender_*` tool names and the `ns:blender` tag |
| declaration | The `UpstreamDecl` value in `blender_connector/upstreams.py` |
| registry | The SDK's upstream registry: activation, health, drift, refusal codes |
| registry tools | `registry_list_namespaces`, `registry_activate`, `registry_deactivate`, `registry_status` |
| native tool | A connector-owned tool that is not proxied; here: `handshake` |
| snapshot | `content/snapshots/blender.tools.json`; the upstream's `tools/list` at refresh time |
| source | `content/apps/blender.yml`; the authored summary, classes and functionalities |
| content tier | The generated skill, ontology and prompt files served over MCP |
| overlay | The operator TOML named by `SCION_UPSTREAMS_FILE` |
| drift | A tool-list difference between the live upstream and the pinned/committed snapshot |
| addon socket | The Blender addon's local socket (default `localhost:9876`) the upstream talks to |
| fleet | The Arbora MCP gateway that loads and unloads connector tool groups |
| group | The set of proxied tools of one namespace, loaded/unloaded as a unit |
