# CONN-BLENDER-CONNECTOR data model

This spec adds no persisted type. It uses the SDK types `UpstreamDecl`, `SandboxRoots` and `BridgeDecl` (`SCION-CONNECTOR-CONTROL-R914.1`).

- Declaration tuple (`blender_connector/upstreams.py`, CONN-BLENDER-CONNECTOR-R001): one `UpstreamDecl` value with an explicit empty sandbox grant.
- Probe result (`blender_connector/probe.py`, CONN-BLENDER-CONNECTOR-R003): `{upstream, exposes_mcp, version, tool_count}`, or the refusal code `BLENDER_MCP_NOT_FOUND` / `BLENDER_MCP_NO_MCP`; printed and never stored.
- Handshake result (`blender_connector/mcp/__init__.py`, CONN-BLENDER-CONNECTOR-R006): `{command_found, socket_open, host, port}`; reported and never stored.
- Operator overlay (`docs/upstreams.example.toml`, CONN-BLENDER-CONNECTOR-R005): a TOML file that the SDK merges by upstream name.
