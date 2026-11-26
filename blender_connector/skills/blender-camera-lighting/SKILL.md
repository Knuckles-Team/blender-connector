---
name: blender-camera-lighting
skill_type: skill
description: >-
  Place cameras and lights and set the world environment. Use when adding or aiming a camera, adding lights, setting exposure or the world background, or choosing the render engine and device. Do NOT use for importing an HDRI from a library (use blender-assets with polyhaven hdris) or inspecting without changing (use blender-inspect-scene).
license: MIT
tags: [blender, camera_lighting, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: camera lighting

Place cameras and lights and set the world environment.

## When to use

Adding or aiming a camera, adding lights, setting exposure or the world background, or choosing the render engine and device.

## When NOT to use

Importing an HDRI from a library (use blender-assets with polyhaven hdris) or inspecting without changing (use blender-inspect-scene).

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
| `blender_look` | See the scene as one image. |

## Steps

1. **Add or adjust the camera and make it the scene camera.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy, math\ncam_data = bpy.data.cameras.new(\"MainCam\")\ncam = bpy.data.objects.new(\"MainCam\", cam_data)\nbpy.context.scene.collection.objects.link(cam)\ncam.location = (4.0, -4.0, 2.5)\ncam.rotation_euler = (math.radians(65), 0, math.radians(45))\nbpy.context.scene.camera = cam\nprint(bpy.context.scene.camera.name)"}
     ```

   - Verify: The printed name equals the camera you created and `scene.camera` points at it.
2. **Add lights and set the world, exposure and render device (select GPU rendering when the host has one).**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy\nlight = bpy.data.lights.new(\"Key\", type=\"AREA\")\nlight.energy = 800\nobj = bpy.data.objects.new(\"Key\", light)\nbpy.context.scene.collection.objects.link(obj)\nobj.location = (3, -2, 4)\nsc = bpy.context.scene\nsc.render.engine = \"CYCLES\"\nsc.cycles.device = \"GPU\"\nprint(sc.render.engine, sc.cycles.device)"}
     ```

   - Verify: The printed engine and device match what you set. If the host has no usable GPU, the device falls back to CPU at render time.
3. **Verify the framing through the camera.**
   - Tool: `blender_look`
   - Arguments:

     ```json
     {"mode": "camera", "shading": "rendered", "max_size": 768}
     ```

   - Verify: The subject is inside the frame and exposed neither black nor blown out; adjust and look again.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| The camera view is black | No light and a dark world, or the camera is inside an object | Add a light or raise the world strength (`bpy.context.scene.world.node_tree.nodes['Background'].inputs[1].default_value`), and move the camera outside the geometry. |
| `look` with `mode: camera` fails | `scene.camera` is not set | Assign `bpy.context.scene.camera` in a script, then look again. |
| Rendering is slow or Cycles reports no GPU | No compute device is enabled in Blender's Cycles preferences; safe mode blocks script access to preferences | Set `scene.cycles.device = 'GPU'` in a script (allowed) and ask the operator to enable the CUDA devices in the host's Blender startup or preferences; otherwise accept CPU rendering. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `unavailable` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-camera_lighting`.
- Refusals are reported to the operator and never retried past the recovery rows above.
