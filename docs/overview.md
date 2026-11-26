# Overview

`blender-connector` is the Arbora-ecosystem connector for Blender. It is a
single MCP server that:

1. **Proxies the upstream** — the `mcp-for-blender` binary (the community
   `mcp-for-blender` project) runs as a pooled stdio child of this server.
   Every upstream tool is served as `blender_<tool>`, tagged `ns:blender`,
   with the `scion/upstream` metadata; the upstream's resources pass
   through unmodified.
2. **Adds a native tool** — `handshake`, a local readiness check (upstream
   binary on PATH, addon socket reachable) that never talks to Blender.
3. **Serves the SDK registry** — `registry_list_namespaces`,
   `registry_activate`, `registry_deactivate`, `registry_status`.
4. **Serves the content tier** — `skill://blender/SKILL.md`,
   `ontology://blender-connector/blender.ttl`, and the `blender-*`
   prompts, generated from the committed tool snapshot.

The upstream is the only thing that talks to Blender (the addon socket,
default `localhost:9876`). With Blender down, the `blender_*` calls return
the upstream's actionable timeout text; the server, registry and content
keep serving.
