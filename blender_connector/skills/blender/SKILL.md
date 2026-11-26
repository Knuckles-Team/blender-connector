---
name: blender
skill_type: skill
description: >-
  Blender 3D scene work through the mcp-for-blender upstream - inspect the scene, build geometry, author materials, place cameras and lights, rig and animate, review the viewport, import assets, and generate 3D content. Use when the agent must work in a live Blender session through the blender_ prefixed tools and needs the right functionality skill.
license: MIT
tags: [blender, 3d, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender

Router for the Blender connector: one MCP server that proxies the `mcp-for-blender` upstream. Pick the functionality skill below, then follow its numbered steps.

## When to use

Blender 3D scene work through the mcp-for-blender upstream - inspect the scene, build geometry, author materials, place cameras and lights, rig and animate, review the viewport, import assets, and generate 3D content.

## When NOT to use

- Batch rendering or conversion without a running Blender: the connector only reaches a live session through the add-on socket.
- Any other 3D or CAD application: use that application's connector.

## Prerequisites

- A running Blender (3.0 or newer) with the MCP for Blender add-on enabled and its server started; the add-on listens on `BLENDER_HOST:BLENDER_PORT` (default `localhost:9876`).
- Call the connector's `handshake` tool first: `ready: true` means the add-on socket answers. `ready: false` means Blender is not running, the add-on is off, or the host and port do not match.
- Save the .blend file before any `blender_execute_blender_code` call: that tool runs arbitrary Python inside the live session.
- The connector never opens its own socket to Blender; every scene action goes through a `blender_*` tool.

## Activation

The `blender` namespace is active by default: the `blender_*` tools are visible from the first tool list. If the operator set lazy activation, call `registry_activate` with the namespace `blender` before using any of them.

## Tools

| Tool | What it does |
|---|---|
| `blender_disable_telemetry` | Turn OFF collection of prompts, code, screenshots and scene data. |
| `blender_execute_blender_code` | Run Python in the user's live Blender (bpy, bmesh, mathutils). |
| `blender_generate_3d` | Make one new textured 3D model from a text prompt or an image, and import it. |
| `blender_generate_gaussian_world` | Generate a whole environment with World Labs Marble and import it as Gaussian splats (a photoreal capture of the place, not editable meshes), with a hidden rough collision mesh for placing objects and its panorama as the world background, in metres with the ground at z=0. |
| `blender_get_addon_status` | Check the connected Blender: its version, whether the addon matches this server, and which asset libraries and 3D generators are switched on. |
| `blender_get_scene_info` | Facts about the scene as text: what's there, where, how big, and how healthy meshes and rigs are. |
| `blender_import_asset` | Download an asset found with search_assets and bring it into the scene. |
| `blender_look` | See the scene as one image. |
| `blender_record_trajectory_feedback` | Record evaluation feedback for a captured trajectory step. |
| `blender_search_assets` | Search a library of existing assets. |
| `handshake` | Local readiness check: upstream binary and add-on socket. |

## Functionality skills

| Skill | Use it to |
|---|---|
| `blender-inspect-scene` | Report the addon status, the connection state and the scene's objects and materials. |
| `blender-build-scene` | Add, move and shape objects with Python executed inside Blender. |
| `blender-materials` | Author materials, textures and node graphs for objects. |
| `blender-camera-lighting` | Place cameras and lights and set the world environment. |
| `blender-rig-animate` | Rig objects with armatures and animate actions and keyframes. |
| `blender-review-viewport` | Review the scene with viewport screenshots. |
| `blender-assets` | Search and import library assets into the scene. |
| `blender-generative-3d` | Generate 3D content from text or images; these operations may cost credits. |
| `blender-session-controls` | Session maintenance: telemetry opt-out and trajectory feedback. |

## Where the data lives

- **scene**: The open .blend session inside the running Blender, reached only through the add-on socket.
- **asset_libraries**: Poly Haven, Sketchfab and Poly Pizza, reached through `blender_search_assets` and `blender_import_asset`; availability per user comes from `blender_get_addon_status`.
- **generators**: The 3D generation providers (for example Meshy) and the world generator, reached through `blender_generate_3d` and `blender_generate_gaussian_world`; each call may cost money or a monthly generation.
- **renders**: Images returned by `blender_look` (kept in the conversation) and the in-session `Render Result` image.

## Error recovery

| Symptom | Likely cause | Fix |
|---|---|---|
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `unavailable` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |
| `blender_get_addon_status` says the add-on is outdated | The installed add-on does not match the server version | Run `uvx mcp-for-blender install-addon` on the Blender host, then restart Blender or re-enable the add-on, and call `blender_get_addon_status` again. |
| A script is blocked with a reason | Safe mode (`BLENDER_MCP_SAFE_MODE=1`) refused file, process, network or persistence access | Rewrite the script without the blocked call (use Blender operators and `bpy.data` instead of direct file or process access) and run it again. Report the refusal; never switch safe mode off to get past it. |
| A call returns an error from Blender (Python traceback) | The script or arguments were wrong for the current scene state | Read the traceback's last line, inspect the scene with `blender_get_scene_info`, fix the one failing statement and rerun a smaller step. |
