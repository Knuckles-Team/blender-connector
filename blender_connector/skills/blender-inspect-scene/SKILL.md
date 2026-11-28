---
name: blender-inspect-scene
skill_type: skill
description: >-
  Report the addon status, the connection state and the scene's objects and materials. Use when starting a session, before editing, or when you need facts about what is in the scene: counts, positions, sizes, materials, modifiers, mesh health or render settings. Do NOT use for seeing the scene as an image (use blender-review-viewport) or changing anything (use blender-build-scene).
license: MIT
tags: [blender, inspect_scene, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: inspect scene

Report the addon status, the connection state and the scene's objects and materials.

## When to use

Starting a session, before editing, or when you need facts about what is in the scene: counts, positions, sizes, materials, modifiers, mesh health or render settings.

## When NOT to use

Seeing the scene as an image (use blender-review-viewport) or changing anything (use blender-build-scene).

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
| `blender_get_scene_info` | Facts about the scene as text: what's there, where, how big, and how healthy meshes and rigs are. |

## Steps

1. **Check the add-on and the connection.**
   - Tool: `blender_get_addon_status`
   - Arguments:

     ```json
     {}
     ```

   - Verify: The reply names the Blender version, says the add-on matches this server, and lists which libraries and generators are on. Anything else is a recovery row.
2. **Read the scene inventory with the fields you need.**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"fields": ["placement", "contents"], "limit": 50}
     ```

   - Verify: A header line with object counts, then one line per object. An empty scene says so explicitly.
3. **Narrow to one object or hierarchy when the inventory is long.**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"root": "Chair", "fields": ["placement", "materials", "modifiers", "topology"]}
     ```

   - Verify: Only that object and its children are listed, with the requested fields.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| The inventory is truncated | More objects than `limit` | Raise `limit`, or filter with `query` (name contains) or `root` (one hierarchy). |
| A field you need is not offered | `get_scene_info` covers placement, contents, health and settings only | Read it with `blender_execute_blender_code` and `print(...)` (see blender-build-scene). |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `Backoff` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-inspect_scene`.
- Refusals are reported to the operator and never retried past the recovery rows above.
