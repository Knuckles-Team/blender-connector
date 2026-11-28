# Usage

## The proxied surface

The upstream's tools appear namespaced; the snapshot of the served
surface (plain MCP client, no app extensions) is:

| Tool | What it does |
|---|---|
| `blender_get_addon_status` | Check the connected Blender, addon match, library/generator state |
| `blender_get_scene_info` | Facts about the scene: objects, materials, mesh/rig health |
| `blender_execute_blender_code` | Run Python in the live Blender (bpy, bmesh, mathutils) |
| `blender_look` | Capture the viewport as an image |
| `blender_search_assets` | Search the enabled asset libraries |
| `blender_import_asset` | Import a found asset into the scene |
| `blender_generate_3d` | Text/image to a textured 3D model (may cost credits) |
| `blender_generate_gaussian_world` | Generative Gaussian-splat world (may cost credits) |
| `blender_disable_telemetry` | Turn off upstream telemetry collection |
| `blender_record_trajectory_feedback` | Record trajectory feedback for the session |

A live listing is authoritative; the content tier (skill, ontology,
prompts) is generated from the committed snapshot and is gated against
drift (`scripts/generate_blender_content.py --check` / `--live`).

## Ready

Call `handshake` before the first `blender_*` call. It reports whether
`mcp-for-blender` is on the PATH and whether the addon socket
(`BLENDER_HOST`/`BLENDER_PORT`, default `localhost:9876`) answers. A
missing socket usually means Blender is not running with the addon
enabled. `registry_status` reports the upstream's registry state and
refusal code.

## Governance

- The child environment is clean: only `SCION_UPSTREAMS_INHERIT_ENV`
  names reach it (default: `PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT,BLENDER_MCP_SAFE_MODE`).
- `DISABLE_TELEMETRY=1` is the shipped start value.
- `execute_blender_code` runs arbitrary Python inside Blender — inherent
  to the upstream; the connector re-gates nothing and adds no second
  Blender access path.
- A drifted upstream (tool list changed vs. the pin) reports `Degraded`
  under `on_drift=warn`; switch the declaration to `refuse` to hard-stop.
