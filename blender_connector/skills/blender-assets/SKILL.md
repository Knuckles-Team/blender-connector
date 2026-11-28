---
name: blender-assets
skill_type: skill
description: >-
  Search and import library assets into the scene. Use when using an existing asset: an HDRI for the world, a PBR texture set, or a model from Poly Haven, Sketchfab or Poly Pizza. Do NOT use for creating a new model from a prompt (use blender-generative-3d) or modeling by script (use blender-build-scene).
license: MIT
tags: [blender, assets, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: assets

Search and import library assets into the scene.

## When to use

Using an existing asset: an HDRI for the world, a PBR texture set, or a model from Poly Haven, Sketchfab or Poly Pizza.

## When NOT to use

Creating a new model from a prompt (use blender-generative-3d) or modeling by script (use blender-build-scene).

## Before you start

- The `blender` namespace is active (`registry_activate` otherwise).
- A running Blender (3.0 or newer) with the MCP for Blender add-on enabled and its server started; the add-on listens on `BLENDER_HOST:BLENDER_PORT` (default `localhost:9876`).
- Call the connector's `handshake` tool first: `ready: true` means the add-on socket answers. `ready: false` means Blender is not running, the add-on is off, or the host and port do not match.
- Save the .blend file before any `blender_execute_blender_code` call: that tool runs arbitrary Python inside the live session.
- The connector never opens its own socket to Blender; every scene action goes through a `blender_*` tool.
- Security: the add-on socket has no authentication and `blender_execute_blender_code` runs any Python in the session, so the socket must listen on the loopback address only, the connector must run on the same host as Blender, no gateway, port forward or container port mapping may expose the socket, Blender should run as a dedicated user with no access to credentials, and callers reach the connector only through Arbora `fleet.call`, which applies admission and scopes.

## Tools

| Tool | What it does |
|---|---|
| `blender_get_addon_status` | Check the connected Blender: its version, whether the addon matches this server, and which asset libraries and 3D generators are switched on. |
| `blender_search_assets` | Search a library of existing assets. |
| `blender_import_asset` | Download an asset found with search_assets and bring it into the scene. |

## Steps

1. **Confirm which libraries are switched on.**
   - Tool: `blender_get_addon_status`
   - Arguments:

     ```json
     {}
     ```

   - Verify: The `libraries` list shows the source you want as on; if off, tell the user to switch it on in Blender and do not guess another source silently.
2. **Search the library with plain words.**
   - Tool: `blender_search_assets`
   - Arguments:

     ```json
     {"source": "polyhaven", "query": "wooden chair", "asset_type": "models", "limit": 5}
     ```

   - Verify: Results with ids; pick one by licence and size. Sketchfab licences vary per model; Poly Pizza CC-BY needs credit.
3. **Import the chosen asset at a stated real-world size.**
   - Tool: `blender_import_asset`
   - Arguments:

     ```json
     {"source": "polyhaven", "id": "<id from search>", "asset_type": "models", "target_size": 1.0, "resolution": "1k"}
     ```

   - Verify: The reply names the imported object; confirm it with `get_scene_info` (query by name) and the size matches `target_size`.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| A Poly Haven import freezes Blender for a while | Assets download on Blender's main thread and size grows about fourfold per resolution step | Ask for `1k` or `2k` unless the asset is close to the camera. |
| The texture material is created but not visible | `apply_to` was not given for a texture import | Import again with `apply_to` set to the object names; an unused material is lost when the file is saved. |
| A Poly Pizza download fails with a bot challenge | The CDN blocks datacenter and VPN addresses | Retry from a normal connection, or import the .glb by hand with File > Import > glTF 2.0. |
| `import_asset` rejects the call | A required argument is missing (`asset_type` for Poly Haven, `target_size` for Sketchfab) | Add the missing argument named in the error and retry once. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `Backoff` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-assets`.
- Refusals are reported to the operator and never retried past the recovery rows above.
