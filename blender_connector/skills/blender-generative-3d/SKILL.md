---
name: blender-generative-3d
skill_type: skill
description: >-
  Generate 3D content from text or images; these operations may cost credits. Use when the user asks for a new textured model from a prompt or image, or for a generated environment as Gaussian splats. Do NOT use for ordinary scene building, ground, rooms or backdrops you can model or find (use blender-build-scene or blender-assets). Do not generate repeats: duplicate the first object instead.
license: MIT
tags: [blender, generative_3d, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: generative 3d

Generate 3D content from text or images; these operations may cost credits.

## When to use

The user asks for a new textured model from a prompt or image, or for a generated environment as Gaussian splats.

## When NOT to use

Ordinary scene building, ground, rooms or backdrops you can model or find (use blender-build-scene or blender-assets). Do not generate repeats: duplicate the first object instead.

## Before you start

- The `blender` namespace is active (`registry_activate` otherwise).
- A running Blender (3.0 or newer) with the MCP for Blender add-on enabled and its server started; the add-on listens on `BLENDER_HOST:BLENDER_PORT` (default `localhost:9876`).
- Call the connector's `handshake` tool first: `ready: true` means the add-on socket answers. `ready: false` means Blender is not running, the add-on is off, or the host and port do not match.
- Save the .blend file before any `blender_execute_blender_code` call: that tool runs arbitrary Python inside the live session.
- The connector never opens its own socket to Blender; every scene action goes through a `blender_*` tool.

## Tools

| Tool | What it does |
|---|---|
| `blender_get_addon_status` | Check the connected Blender: its version, whether the addon matches this server, and which asset libraries and 3D generators are switched on. |
| `blender_generate_3d` | Make one new textured 3D model from a text prompt or an image, and import it. |
| `blender_generate_gaussian_world` | Generate a whole environment with World Labs Marble and import it as Gaussian splats (a photoreal capture of the place, not editable meshes), with a hidden rough collision mesh for placing objects and its panorama as the world background, in metres with the ground at z=0. |
| `blender_get_scene_info` | Facts about the scene as text: what's there, where, how big, and how healthy meshes and rigs are. |

## Steps

1. **Confirm a generator is switched on and get the user's approval for the cost.**
   - Tool: `blender_get_addon_status`
   - Arguments:

     ```json
     {}
     ```

   - Verify: `generators` (or `worlds`) lists a provider as on, and the user has agreed to a billable generation.
2. **Describe one object (or one world) and start the generation.**
   - Tool: `blender_generate_3d`
   - Arguments:

     ```json
     {"prompt": "a weathered wooden barrel", "name": "Barrel", "wait_seconds": 45}
     ```

   - Verify: Either the object is imported, or you receive a job handle.
3. **If a job handle came back, call again with the job until it finishes.**
   - Tool: `blender_generate_3d`
   - Arguments:

     ```json
     {"job": "<job handle>", "name": "Barrel"}
     ```

   - Verify: The object is imported; repeating a request whose job is unfinished resumes it rather than paying again.
4. **Inspect the result and integrate it (scale, place, ground).**
   - Tool: `blender_get_scene_info`
   - Arguments:

     ```json
     {"query": "Barrel", "fields": ["placement", "size", "ground"]}
     ```

   - Verify: Size and orientation are plausible; fix with a `blender_execute_blender_code` step.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| No generator is available | No provider key or Premium access is configured in the add-on | Report which providers `blender_get_addon_status` lists and ask the user to enable one in the add-on preferences; do not retry. |
| The call returns a job handle instead of a model | Generation takes 1-3 minutes and a call waits at most 45 seconds | Call the same tool again with `job` and the same `name`. |
| The imported object is the wrong size or facing | Generated models arrive at arbitrary scale and facing | Set `obj.dimensions` and rotation with a `blender_execute_blender_code` step and verify with `blender_look`. |
| `generate_gaussian_world` fails | It needs Blender 5.3 or newer | Report the Blender version from `blender_get_addon_status`; do not retry on an older Blender. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `unavailable` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-generative_3d`.
- Refusals are reported to the operator and never retried past the recovery rows above.
