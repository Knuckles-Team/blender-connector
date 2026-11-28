---
name: blender-export-and-validate-kit
skill_type: skill
description: >-
  Build one asset-kit family in the live session from its kit script, export it as GLB, and report its triangle counts, LOD nodes and sockets. Use when a person reviews one generated asset family by eye before a kit release. Do NOT use for building the release kit, which runs headless with no add-on socket.
license: MIT
tags: [blender, export_and_validate_kit, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: export and validate kit

Build one asset-kit family in the live session from its kit script, export it as GLB, and report its triangle counts, LOD nodes and sockets.

## When to use

A person reviews one generated asset family by eye before a kit release.

## When NOT to use

Building the release kit, which runs headless with no add-on socket.

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
| `blender_execute_blender_code` | Run Python in the user's live Blender (bpy, bmesh, mathutils). |
| `blender_look` | See the scene as one image. |
| `blender_get_scene_info` | Facts about the scene as text: what's there, where, how big, and how healthy meshes and rigs are. |

## Steps

1. **Clear the scene, add the kit directory to `sys.path`, import the stage module the caller names and call its `build([family_id], style)`.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy, sys, importlib\nbpy.ops.wm.read_factory_settings(use_empty=True)\nsys.path.insert(0, \"<kit_dir>\")\nstage = importlib.import_module(\"<stage_module>\")\nstage.build([\"<family_id>\"], \"<style>\")\nprint(\"BUILT <family_id>\")"}
     ```

   - Verify: The output holds the line `BUILT <family_id>`.
2. **Export the selection as GLB, then print each LOD node with its triangle count and each `socket.*` empty with its location.**
   - Tool: `blender_execute_blender_code`
   - Arguments:

     ```json
     {"code": "import bpy\nbpy.ops.object.select_all(action=\"SELECT\")\nbpy.ops.export_scene.gltf(filepath=\"<temp_path>.glb\", export_format=\"GLB\", export_extras=True)\nfor o in bpy.data.objects:\n    if o.type == \"MESH\" and \"LOD\" in o.name:\n        o.data.calc_loop_triangles()\n        print(\"LOD\", o.name, len(o.data.loop_triangles))\n    elif o.type == \"EMPTY\" and o.name.startswith(\"socket.\"):\n        print(\"SOCKET\", o.name, tuple(round(v, 3) for v in o.location))"}
     ```

   - Verify: One output line per LOD node and one per socket.
3. **Look at the family from the front, the top and a street-level angle.**
   - Tool: `blender_look`
   - Arguments:

     ```json
     {"mode": "angles", "target": ["<family_root>"], "views": ["front", "top", [1, -1, 0.1]], "max_size": 768}
     ```

   - Verify: Three images, each with the family centred.
4. **Read the topology of the family.**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"root": "<family_root>", "fields": ["topology"]}
     ```

   - Verify: Zero non-manifold edges.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| The stage module cannot be imported | The kit path is wrong | Correct `<kit_dir>` and the module name the caller gave, then repeat step 1. |
| A triangle count is over budget | The family fails the kit gate | Change the stage script and rebuild; never hand-edit the generated geometry. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `Backoff` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-export_and_validate_kit`.
- Refusals are reported to the operator and never retried past the recovery rows above.
