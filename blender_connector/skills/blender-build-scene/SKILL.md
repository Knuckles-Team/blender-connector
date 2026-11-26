---
name: blender-build-scene
skill_type: skill
description: >-
  Add, move and shape objects with Python executed inside Blender. Use when creating, moving, scaling, parenting, deleting or modifying objects and meshes; any scene change that has no dedicated tool. Do NOT use for downloading a library asset (use blender-assets), producing a new textured model from a prompt (use blender-generative-3d) or only looking at the scene (use blender-review-viewport).
license: MIT
tags: [blender, build_scene, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: build scene

Add, move and shape objects with Python executed inside Blender.

## When to use

Creating, moving, scaling, parenting, deleting or modifying objects and meshes; any scene change that has no dedicated tool.

## When NOT to use

Downloading a library asset (use blender-assets), producing a new textured model from a prompt (use blender-generative-3d) or only looking at the scene (use blender-review-viewport).

## Before you start

- The `blender` namespace is active (`registry_activate` otherwise).
- A running Blender (3.0 or newer) with the MCP for Blender add-on enabled and its server started; the add-on listens on `BLENDER_HOST:BLENDER_PORT` (default `localhost:9876`).
- Call the connector's `handshake` tool first: `ready: true` means the add-on socket answers. `ready: false` means Blender is not running, the add-on is off, or the host and port do not match.
- Save the .blend file before any `blender_execute_blender_code` call: that tool runs arbitrary Python inside the live session.
- The connector never opens its own socket to Blender; every scene action goes through a `blender_*` tool.

## Tools

| Tool | What it does |
|---|---|
| `blender_execute_blender_code` | Run Python in the user's live Blender (bpy, bmesh, mathutils). |
| `blender_get_scene_info` | Facts about the scene as text: what's there, where, how big, and how healthy meshes and rigs are. |

## Steps

1. **Plan the change in bpy terms and keep it to one small step: one object or one operation.**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"fields": ["placement"], "limit": 20}
     ```

   - Verify: You can state in one sentence what the script adds or changes, the object names it touches, and what it will print.
2. **Execute it in one bounded code block that prints what you need to know.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy\nbpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))\nobj = bpy.context.active_object\nobj.name = \"Crate\"\nprint(obj.name, tuple(obj.location), tuple(obj.dimensions))"}
     ```

   - Verify: The printed output names the object and its dimensions. A Python traceback means the step failed: read its last line.
3. **Verify the result with the scene inventory or a look.**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"query": "Crate", "fields": ["placement", "ground", "topology"]}
     ```

   - Verify: The object exists with the expected location, size and mesh health; the ground field says on ground, floating or below.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `AttributeError` or `RuntimeError: Operator bpy.ops... poll() failed` | The operator needs a mode or context (for example Object Mode, an active object) | Set the mode first (`bpy.ops.object.mode_set(mode='OBJECT')`) and select the target (`obj.select_set(True)`; `bpy.context.view_layer.objects.active = obj`), or use `bpy.data` calls that need no context. |
| The call times out | The script is too large or runs a long operation | Split it into smaller steps; do heavy work (subdivision, bakes, renders) one at a time. |
| The object name has a `.001` suffix | The name already existed | Read the name back from the printed output and use that name in later steps. |
| The scene did not change as expected | The script ran on a different object than you meant | Print `[o.name for o in bpy.context.selected_objects]` before acting and address objects by name from `bpy.data.objects`. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `unavailable` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-build_scene`.
- Refusals are reported to the operator and never retried past the recovery rows above.
