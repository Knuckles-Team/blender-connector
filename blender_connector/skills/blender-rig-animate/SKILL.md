---
name: blender-rig-animate
skill_type: skill
description: >-
  Rig objects with armatures and animate actions and keyframes. Use when creating an armature, parenting a mesh to bones, posing, setting keyframes or an action, or changing the frame range. Do NOT use for static scene layout (use blender-build-scene) or reviewing the motion only (use blender-review-viewport with frames).
license: MIT
tags: [blender, rig_animate, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: rig animate

Rig objects with armatures and animate actions and keyframes.

## When to use

Creating an armature, parenting a mesh to bones, posing, setting keyframes or an action, or changing the frame range.

## When NOT to use

Static scene layout (use blender-build-scene) or reviewing the motion only (use blender-review-viewport with frames).

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
| `blender_look` | See the scene as one image. |

## Steps

1. **Build the armature and parent the mesh to it.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy\nbpy.ops.object.armature_add(location=(0, 0, 0))\narm = bpy.context.active_object\narm.name = \"Rig\"\nmesh = bpy.data.objects[\"Crate\"]\nmesh.parent = arm\nprint(arm.name, [b.name for b in arm.data.bones])"}
     ```

   - Check: The printed bone list is not empty and the mesh's parent is the armature.
2. **Pose the rig and keyframe the action.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy\nsc = bpy.context.scene\nobj = bpy.data.objects[\"Crate\"]\nsc.frame_start, sc.frame_end = 1, 48\nobj.location.z = 0.5\nobj.keyframe_insert(\"location\", frame=1)\nobj.location.z = 2.0\nobj.keyframe_insert(\"location\", frame=24)\nprint(obj.animation_data.action.name)"}
     ```

   - Check: The printed action name exists and the frame range covers your keyframes.
3. **Check rig health, then verify the motion with a strip of frames.**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"root": "Rig", "fields": ["details", "weights", "animation"]}
     ```

   - Check: No deform bones without vertices and no vertices without a deform bone.
4. **Look at several frames.**
   - Tool: `blender_look`
   - Arguments:

     ```json
     {"mode": "frames", "frame_count": 6, "shading": "solid", "max_size": 512}
     ```

   - Check: The strip shows the motion progressing across the frame range.

## Error recovery

| Symptom | Likely cause | Fix |
|---|---|---|
| The mesh does not follow the bones | Parenting without an armature modifier or vertex weights | Parent with automatic weights (`bpy.ops.object.parent_set(type='ARMATURE_AUTO')` with the mesh selected and the armature active) and re-check `weights` in `get_scene_info`. |
| Keyframes do not appear | The property was changed but never keyed, or the frame range excludes the key | Call `keyframe_insert` after each change and set `scene.frame_start` and `frame_end`. |
| A pose operator fails | Pose Mode is required | Switch with `bpy.ops.object.mode_set(mode='POSE')` with the armature active, or set `pose.bones[...]` values directly. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `unavailable` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-rig_animate`.
- Refusals are reported to the operator and never retried past the recovery rows above.
