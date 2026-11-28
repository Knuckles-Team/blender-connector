---
name: blender-review-viewport
skill_type: skill
description: >-
  Review the scene with viewport screenshots. Use when seeing the scene or an object as an image: a quick check after an edit, multiple angles, the camera framing, or frames across an animation. Do NOT use for exact numbers such as sizes, counts or positions (use blender-inspect-scene).
license: MIT
tags: [blender, review_viewport, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: review viewport

Review the scene with viewport screenshots.

## When to use

Seeing the scene or an object as an image: a quick check after an edit, multiple angles, the camera framing, or frames across an animation.

## When NOT to use

Exact numbers such as sizes, counts or positions (use blender-inspect-scene).

## Before you start

- The `blender` namespace is active (`registry_activate` otherwise).
- A running Blender (3.0 or newer) with the MCP for Blender add-on enabled and its server started; the add-on listens on `BLENDER_HOST:BLENDER_PORT` (default `localhost:9876`).
- Call the connector's `handshake` tool first: `ready: true` means the add-on socket answers. `ready: false` means Blender is not running, the add-on is off, or the host and port do not match.
- Save the .blend file before any `blender_execute_blender_code` call: that tool runs arbitrary Python inside the live session.
- The connector never opens its own socket to Blender; every scene action goes through a `blender_*` tool.

## Tools

| Tool | What it does |
|---|---|
| `blender_look` | See the scene as one image. |
| `blender_get_scene_info` | Facts about the scene as text: what's there, where, how big, and how healthy meshes and rigs are. |

## Steps

1. **Capture the viewport at a small size for a quick check.**
   - Tool: `blender_look`
   - Arguments:

     ```json
     {"mode": "viewport", "shading": "solid", "max_size": 512}
     ```

   - Verify: An image is returned that shows the area you edited.
2. **Look at the target from several sides.**
   - Tool: `blender_look`
   - Arguments:

     ```json
     {"mode": "angles", "target": ["Crate"], "views": ["front", "right", "top", "three_quarter"], "shading": "rendered", "max_size": 512}
     ```

   - Verify: One tile per requested view; the object is centered and fully visible in each.
3. **Inspect the image and iterate on the scene until it is right.**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"query": "Crate", "fields": ["placement", "size"]}
     ```

   - Verify: The numbers agree with what the image shows. If the image is wrong, change the scene and look again; if numbers are needed, read them with this call.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| The image is empty or shows the wrong area | The target names do not exist or the viewport is not looking at the scene | List object names with `get_scene_info`, pass them in `target` exactly, or omit `target` to frame everything visible. |
| The rendered look takes too long | Many views with Cycles | Use `shading: solid` or `material` (instant), fewer `views`, or a smaller `max_size`. |
| The look is too small to judge detail | `max_size` defaults to 768 pixels | Raise `max_size` for one detail look and lower `distance` to frame closer. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `Backoff` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-review_viewport`.
- Refusals are reported to the operator and never retried past the recovery rows above.
