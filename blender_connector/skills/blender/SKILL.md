---
name: blender
description: Blender 3D scene work through the mcp-for-blender upstream — inspect the scene, build geometry, author materials, place cameras and lights, rig and animate, review the viewport, import assets, and generate 3D content.
---

# Blender

## When to use

Blender 3D scene work through the mcp-for-blender upstream — inspect the scene, build geometry, author materials, place cameras and lights, rig and animate, review the viewport, import assets, and generate 3D content.

## Activation

The `blender` namespace is active by default: the `blender_*` tools are visible from the first tool list. If the operator set lazy activation, call `registry_activate` with the namespace `blender` before using any of them.

## Tools

| Tool | What it does |
|---|---|
| `blender_disable_telemetry` | Turn OFF collection of prompts, code, screenshots and scene data. |
| `blender_execute_blender_code` | Run Python in the user's live Blender (bpy, bmesh, mathutils). |
| `blender_generate_3d` | Make one new textured 3D model from a text prompt or an image, and import it. |
| `blender_generate_gaussian_world` | Generate a whole environment with World Labs Marble and import it as Gaussian splats (a
photoreal capture of the place, not editable meshes), with a hidden rough collision mesh for
placing objects and its panorama as the world background, in metres with the ground at z=0. |
| `blender_get_addon_status` | Check the connected Blender: its version, whether the addon matches this server, and which
asset libraries and 3D generators are switched on. |
| `blender_get_scene_info` | Facts about the scene as text: what's there, where, how big, and how healthy meshes and rigs
are. |
| `blender_import_asset` | Download an asset found with search_assets and bring it into the scene. |
| `blender_look` | See the scene as one image. |
| `blender_record_trajectory_feedback` | Record evaluation feedback for a captured trajectory step. |
| `blender_search_assets` | Search a library of existing assets. |

## Functionalities

- `blender-inspect_scene` — Report the addon status, the connection state and the scene's objects and materials.
- `blender-build_scene` — Add, move and shape objects with Python executed inside Blender.
- `blender-materials` — Author materials, textures and node graphs for objects.
- `blender-camera_lighting` — Place cameras and lights and set the world environment.
- `blender-rig_animate` — Rig objects with armatures and animate actions and keyframes.
- `blender-review_viewport` — Review the scene with viewport screenshots.
- `blender-assets` — Search and import library assets into the scene.
- `blender-generative_3d` — Generate 3D content from text or images; these operations may cost credits.
- `blender-session_controls` — Session maintenance: telemetry opt-out and trajectory feedback.
