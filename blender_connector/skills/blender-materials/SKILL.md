---
name: blender-materials
skill_type: skill
description: >-
  Author materials, textures and node graphs for objects. Use when creating or editing a material, wiring a shader node graph, assigning a material to an object, or setting texture inputs. Do NOT use for downloading a ready-made PBR texture set (use blender-assets with asset_type textures).
license: MIT
tags: [blender, materials, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: materials

Author materials, textures and node graphs for objects.

## When to use

Creating or editing a material, wiring a shader node graph, assigning a material to an object, or setting texture inputs.

## When NOT to use

Downloading a ready-made PBR texture set (use blender-assets with asset_type textures).

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

1. **Create the material with nodes and assign it to the target object.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy\nobj = bpy.data.objects[\"Crate\"]\nmat = bpy.data.materials.new(\"CrateWood\")\nmat.use_nodes = True\nbsdf = mat.node_tree.nodes[\"Principled BSDF\"]\nbsdf.inputs[\"Base Color\"].default_value = (0.45, 0.28, 0.12, 1.0)\nbsdf.inputs[\"Roughness\"].default_value = 0.6\nobj.data.materials.clear()\nobj.data.materials.append(mat)\nprint([m.name for m in obj.data.materials])"}
     ```

   - Check: The printed list contains the new material name.
2. **Build or adjust the node graph (textures, mix, bump) with further small scripts.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy\nmat = bpy.data.materials[\"CrateWood\"]\nprint([n.name for n in mat.node_tree.nodes])"}
     ```

   - Check: The printed node names include every node you intended to add, and links are listed when you print `mat.node_tree.links`.
3. **Verify with a rendered look at the object.**
   - Tool: `blender_look`
   - Arguments:

     ```json
     {"mode": "angles", "target": ["Crate"], "shading": "rendered", "max_size": 512}
     ```

   - Check: The returned image shows the material on the object under the scene lighting. If it is black or pink, see recovery.

## Error recovery

| Symptom | Likely cause | Fix |
|---|---|---|
| The object renders pink or black | A texture image is missing or a node input is not connected | Print `[(n.name, n.type) for n in mat.node_tree.nodes]` and the links; reconnect the input, or replace the missing image with a flat color. |
| The material is created but not visible on the object | It was never appended to the object's material slots, or the viewport shading is solid | Append it to `obj.data.materials` and use `shading: material` or `rendered` in the look. |
| A material disappears after saving | It has no user (not assigned) | Assign it to an object or set `mat.use_fake_user = True`. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `unavailable` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-materials`.
- Refusals are reported to the operator and never retried past the recovery rows above.
