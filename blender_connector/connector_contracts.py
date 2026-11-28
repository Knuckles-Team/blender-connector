"""Surface contracts of the Blender connector (SCION-CONNECTOR-CONTROL-R916).

The upstream tools are declared from the committed snapshot
(``content/snapshots/blender.tools.json``) because the proxied server is not
started when the surface is checked offline; ``tests/test_surface_contracts.py``
holds the two in step. Contracts, links and roles follow the authored source
(``content/apps/blender.yml``): one task per functionality.
"""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
    UpstreamTool,
)

UPSTREAM_TOOLS = (
    UpstreamTool(
        "blender",
        "disable_telemetry",
        "\nTurn OFF collection of prompts, code, screenshots and scene data.\n\nUse this whenever the user asks to stop data collection, opt out of\ntelemetry, or stop sharing their data. Takes effect immediately.\n\nThis tool can only turn collection OFF. Turning it back on is done by the\nuser in Blender under Preferences > Add-ons > Blender MCP.\n",
        {
            "properties": {
                "user_prompt": {"default": "", "title": "User Prompt", "type": "string"}
            },
            "title": "disable_telemetryArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "execute_blender_code",
        "\nRun Python in the user's live Blender (bpy, bmesh, mathutils). Whatever it prints is returned.\n\nWork in small steps and print what you need to know.\n\nParameters:\n- code: The Python code to execute\n- user_prompt: The user's own words describing what they want, quoted verbatim (do not paraphrase or summarise). Pass the same goal on every call in a multi-step task so each action is linked to the intent behind it. Never substitute your own sub-goal, plan step, or status text; if the user has given no new instruction, repeat their previous words unchanged.\n",
        {
            "properties": {
                "code": {"title": "Code", "type": "string"},
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
            },
            "required": ["code"],
            "title": "execute_blender_codeArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "generate_3d",
        '\nMake one new textured 3D model from a text prompt or an image, and import it.\n\nOne object per call: not a whole scene, the ground, or parts to assemble. It arrives at\narbitrary scale and facing (meshy: real-world size, origin at the bottom). Each call can cost\nthe user money or a monthly generation, so duplicate a generated object for repeats.\n\nWaits up to wait_seconds (at most 45), then imports. Generation usually takes 1-3 minutes: if\nit isn\'t done in time you get a job handle; call generate_3d(job=..., name=...) again to keep\nwaiting. Repeating a request whose generation is still unfinished resumes it instead of paying\nagain.\n\nParameters:\n- prompt: Short English description of one object ("weathered wooden treasure chest").\n- image: Instead of a prompt: an absolute image file path or an http(s) URL. Images attached in\n  chat can\'t be passed: ask the user for a path or URL, don\'t fall back to text without asking.\n  hyper3d also takes a folder of up to 5 images, as views of one object (Premium uses the first).\n- name: Object name in the scene. Defaults to one made from the prompt.\n- provider: auto (default), tripo, hunyuan3d, hyper3d or meshy. Auto prefers the user\'s MCP for\n  Blender Premium generators, then their own API keys.\n- quality: "standard" or "high" (Premium; not Meshy, and not Tripo on your own key). Omit for\n  the user\'s default; "high" only when the user asks for more detail.\n- bbox_condition: hyper3d only: [length, width, height] proportions.\n- pose_mode: meshy only: "a-pose" or "t-pose" when the user asks for a character in an A-pose\n  or T-pose (often to rig it).\n- job: A handle from an earlier call, to resume waiting for it.\n- user_prompt: The user\'s own words describing what they want, quoted verbatim.\n',
        {
            "properties": {
                "prompt": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Prompt",
                },
                "image": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Image",
                },
                "name": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Name",
                },
                "provider": {"default": "auto", "title": "Provider", "type": "string"},
                "quality": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Quality",
                },
                "bbox_condition": {
                    "anyOf": [
                        {"items": {"type": "number"}, "type": "array"},
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "Bbox Condition",
                },
                "pose_mode": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Pose Mode",
                },
                "job": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Job",
                },
                "wait_seconds": {
                    "default": 50,
                    "title": "Wait Seconds",
                    "type": "integer",
                },
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
            },
            "title": "generate_3dArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "generate_gaussian_world",
        '\nGenerate a whole environment with World Labs Marble and import it as Gaussian splats (a\nphotoreal capture of the place, not editable meshes), with a hidden rough collision mesh for\nplacing objects and its panorama as the world background, in metres with the ground at z=0.\nNeeds Blender 5.3+.\n\nUse it sparingly: only when the user asks for a Gaussian splat or generated world, or for a\nready-made environment to set things in. Never for ordinary scene building, single objects\n(generate_3d), or ground, rooms and backdrops you can model or get from search_assets.\n\nEach call costs the user money or a high-quality monthly generation, and takes about 5\nminutes. Waits up to wait_seconds (at most 45), then imports; if it isn\'t done in time you get\na job handle: call generate_gaussian_world(job=..., name=...) again to keep waiting.\nRepeating a request whose generation is still unfinished resumes it instead of paying again.\n\nParameters:\n- prompt: English description of the place ("sunlit Mediterranean courtyard with a fountain").\n- image: Instead of a prompt: an absolute image file path or an http(s) URL of the place; a\n  360° equirectangular panorama works too. On the user\'s own key, also a folder of up to 4\n  images of one place, in name order going around it (the first is the front). Images attached\n  in chat can\'t be passed: ask the user for a path or URL.\n- name: Name of the world\'s parent object. Defaults to one made from the prompt.\n- resolution: Splats to import: "100k", "500k" (default) or "full_res" (about 2 million; sharper\n  but slow in the viewport).\n- job: A handle from an earlier call, to resume waiting for it.\n- user_prompt: The user\'s own words describing what they want, quoted verbatim.\n',
        {
            "properties": {
                "prompt": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Prompt",
                },
                "image": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Image",
                },
                "name": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Name",
                },
                "resolution": {
                    "default": "500k",
                    "title": "Resolution",
                    "type": "string",
                },
                "job": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Job",
                },
                "wait_seconds": {
                    "default": 50,
                    "title": "Wait Seconds",
                    "type": "integer",
                },
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
            },
            "title": "generate_gaussian_worldArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "get_addon_status",
        "\nCheck the connected Blender: its version, whether the addon matches this server, and which\nasset libraries and 3D generators are switched on. Call it once at the start.\n\n`libraries` are the search_assets sources, `generators` the generate_3d providers and\n`worlds` the generate_gaussian_world providers, each on or off for this user. \"(Premium)\" ones come with MCP for Blender Premium and don't use the\nuser's own API keys. When pointing the user to Premium, link\nhttps://mcp-for-blender.com/premium?ref=mcp-status\n\nIf outdated, tells the user how to update via `uvx mcp-for-blender install-addon`\n(then restart or re-enable the addon in Blender).\n\n`telemetry_consent` reports whether data collection is on, off, or null if\nBlender could not be reached. Use it to answer telemetry status questions.\n",
        {
            "properties": {
                "user_prompt": {"default": "", "title": "User Prompt", "type": "string"}
            },
            "title": "get_addon_statusArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "get_scene_info",
        '\nFacts about the scene as text: what\'s there, where, how big, and how healthy meshes and rigs\nare. No image; to see the scene, use look.\n\nOne header line (object counts, active, selection, mode), then one line per object with the\nfields you ask for. Top-level objects by default; root="Name" lists that object\'s hierarchy,\nquery="chair" lists every object whose name contains the text. For anything else about an\nobject, read it with execute_blender_code.\n\nParameters:\n- fields: What to show per object (default: location, size, children, hidden).\n  placement: location (world), size (world bounding box), ground (on ground, floating or\n    below by), rotation (degrees), scale, parent\n  contents: children (count), hidden, details (faces, bones or light power), materials,\n    modifiers, animation\n  health: topology (quads, tris, ngons, non-manifold and boundary edges, loose verts,\n    poles), weights (vertices no deform bone moves, deform bones with no vertex group)\n  settings: adds a line with the file, engine, frame range, resolution, camera, HDRI and\n    unit scale\n- query: Name filter across all objects.\n- root: Object whose hierarchy to list.\n- limit: Maximum object lines (default 20).\n- user_prompt: The user\'s own words describing what they want, quoted verbatim.\n',
        {
            "properties": {
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
                "query": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Query",
                },
                "root": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Root",
                },
                "fields": {
                    "anyOf": [
                        {"items": {"type": "string"}, "type": "array"},
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "Fields",
                },
                "limit": {"default": 20, "title": "Limit", "type": "integer"},
            },
            "title": "get_scene_infoArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "import_asset",
        "\nDownload an asset found with search_assets and bring it into the scene.\n\nParameters:\n- source: polyhaven, sketchfab or polypizza.\n- id: The asset's id (UID for sketchfab) from search_assets.\n- asset_type: polyhaven only, required: hdris (becomes the world lighting), textures (builds a\n  PBR material) or models.\n- target_size: Size in metres of the model's largest dimension (chair 1.0, car 4.5, cup 0.12).\n  Required for sketchfab, recommended for polypizza; library models come at arbitrary scale.\n- apply_to: polyhaven textures: object names to put the material on (replaces their materials).\n  Without it the material is created but unused, and is lost if the file is saved.\n- resolution: polyhaven: 1k, 2k, 4k or 8k. 1k-2k for background, 4k for close-ups.\n- file_format: polyhaven, optional: hdr/exr for HDRIs, jpg/png/exr for textures.\n- user_prompt: The user's own words describing what they want, quoted verbatim.\n\nAfterwards check the reported bounding box, put the object on the ground, and look at it.\n",
        {
            "properties": {
                "source": {"title": "Source", "type": "string"},
                "id": {"title": "Id", "type": "string"},
                "asset_type": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Asset Type",
                },
                "target_size": {
                    "anyOf": [{"type": "number"}, {"type": "null"}],
                    "default": None,
                    "title": "Target Size",
                },
                "apply_to": {
                    "anyOf": [
                        {"items": {"type": "string"}, "type": "array"},
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "Apply To",
                },
                "resolution": {
                    "default": "1k",
                    "title": "Resolution",
                    "type": "string",
                },
                "file_format": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "File Format",
                },
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
            },
            "required": ["source", "id"],
            "title": "import_assetArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "look",
        "\nSee the scene as one image. For counts, sizes and positions, use get_scene_info.\n\nChoose where from (mode) and how it's drawn (shading):\n- mode: viewport (what the user sees; default), camera (through the scene camera, at the\n  render aspect), angles (the target from several sides, auto-framed; default front, right,\n  top, three_quarter), frames (a strip over the animation).\n- shading: rendered (default: a real render with the scene's engine, Cycles included, cut to\n  a few samples and denoised, so lights, materials and world look as they'll render; takes\n  seconds, more for angles and frames since each tile renders), material, solid, wireframe\n  (edges over a plain surface), xray (see-through, bones in front). All but rendered draw the\n  viewport and are instant.\n- image: Instead of the scene, show this image: \"Render Result\" after a render, another\n  image in the file, or a file path.\n\nParameters:\n- target: Object names to frame (children included). Default: every visible object.\n- views: For angles: up to 6 of front, back, left, right, top, three_quarter, or [x, y, z]\n  directions from the target towards the eye ([0, -1, 0.2] is front, slightly above).\n- distance: Metres from the target's centre to the eye, for angles and frames views. Default:\n  far enough to fit it; closer for detail or to stand inside a room.\n- frames / frame_count: For frames: explicit frame numbers, or how many to sample (2-12).\n- view: For frames: \"camera\", an angle name or an [x, y, z] direction; default the viewport.\n- max_size: Longest side in pixels (default 768). Images stay in the conversation, so go\n  smaller for quick checks and larger only to read fine detail.\n- user_prompt: The user's own words describing what they want, quoted verbatim.\n\nEvery setting changed to take the picture is restored afterwards.\n",
        {
            "properties": {
                "mode": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Mode",
                },
                "target": {
                    "anyOf": [
                        {"items": {"type": "string"}, "type": "array"},
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "Target",
                },
                "views": {
                    "anyOf": [
                        {
                            "items": {
                                "anyOf": [
                                    {"type": "string"},
                                    {"items": {"type": "number"}, "type": "array"},
                                ]
                            },
                            "type": "array",
                        },
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "Views",
                },
                "distance": {
                    "anyOf": [{"type": "number"}, {"type": "null"}],
                    "default": None,
                    "title": "Distance",
                },
                "shading": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Shading",
                },
                "frames": {
                    "anyOf": [
                        {"items": {"type": "integer"}, "type": "array"},
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "Frames",
                },
                "frame_count": {
                    "default": 6,
                    "title": "Frame Count",
                    "type": "integer",
                },
                "view": {
                    "anyOf": [
                        {"type": "string"},
                        {"items": {"type": "number"}, "type": "array"},
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "View",
                },
                "image": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Image",
                },
                "max_size": {"default": 768, "title": "Max Size", "type": "integer"},
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
            },
            "title": "lookArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "record_trajectory_feedback",
        '\nRecord evaluation feedback for a captured trajectory step.\n\nCall it when the user reacts to a result: "accept" when they keep it ("looks good"),\n"reject" or "undo" when they reject it or ask to undo, and "correction" with their words\nas correction_text when they correct you ("too dark", "make it taller").\n\nParameters:\n- feedback: One of accept | reject | undo | correction\n- correction_text: Optional free-text correction or follow-up (especially for correction)\n- step_index: Optional 0-based step index; defaults to the last recorded step\n- user_prompt: Optional goal/prompt context for the feedback row\n',
        {
            "properties": {
                "feedback": {"title": "Feedback", "type": "string"},
                "correction_text": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Correction Text",
                },
                "step_index": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "title": "Step Index",
                },
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
            },
            "required": ["feedback"],
            "title": "record_trajectory_feedbackArguments",
            "type": "object",
        },
    ),
    UpstreamTool(
        "blender",
        "search_assets",
        '\nSearch a library of existing assets. The sources:\n- polyhaven: HDRIs, PBR textures and realistic models, all CC0. Search understands intent and\n  synonyms ("couch" finds sofas).\n- sketchfab: a large catalogue of user-made models, realistic and specific ones included;\n  licences and face counts vary per model.\n- polypizza: stylised low-poly models, CC0 or CC-BY (credit the creator).\n\nParameters:\n- source: polyhaven, sketchfab or polypizza.\n- query: What you\'re looking for, in plain words.\n- asset_type: polyhaven only: hdris, textures, models or all.\n- category: Optional. polyhaven: a category path ("Metal/Sheet & Corrugated"). sketchfab:\n  comma-separated categories. polypizza: e.g. "Furniture & Decor", "Nature", "Animals".\n- attributes: polyhaven only: filters like {"weather": "clear"}; an unknown key errors with the\n  valid ones.\n- min_size_m: polyhaven only: minimum real-world size in metres. Use 2+ for walls, floors and\n  ground so textures don\'t visibly repeat.\n- licence: polypizza only: "CC0" or "CC-BY".\n- animated: polypizza only: animated models only.\n- limit: Number of results.\n- previews: Attach thumbnails of the first N results (max 6; polyhaven and sketchfab). Cheaper\n  than importing the wrong asset.\n- user_prompt: The user\'s own words describing what they want, quoted verbatim.\n\nResults include each asset\'s id; pass it to import_asset.\n',
        {
            "properties": {
                "source": {"title": "Source", "type": "string"},
                "query": {"default": "", "title": "Query", "type": "string"},
                "asset_type": {
                    "default": "all",
                    "title": "Asset Type",
                    "type": "string",
                },
                "category": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Category",
                },
                "attributes": {
                    "anyOf": [
                        {"additionalProperties": True, "type": "object"},
                        {"type": "null"},
                    ],
                    "default": None,
                    "title": "Attributes",
                },
                "min_size_m": {
                    "anyOf": [{"type": "number"}, {"type": "null"}],
                    "default": None,
                    "title": "Min Size M",
                },
                "licence": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "title": "Licence",
                },
                "animated": {"default": False, "title": "Animated", "type": "boolean"},
                "limit": {"default": 20, "title": "Limit", "type": "integer"},
                "previews": {"default": 0, "title": "Previews", "type": "integer"},
                "user_prompt": {
                    "default": "",
                    "title": "User Prompt",
                    "type": "string",
                },
            },
            "required": ["source"],
            "title": "search_assetsArguments",
            "type": "object",
        },
    ),
)

CONTRACTS = (
    ToolUseContract(
        "check-readiness",
        (
            ToolStep(
                "handshake",
                result=("command_found", "addon_socket", "ready", "hint"),
            ),
            ToolStep(
                "registry_status", result=("namespace", "state", "last_error_code")
            ),
            ToolStep("registry_list_namespaces", result=("namespace", "active")),
            ToolStep(
                "registry_activate",
                params=("namespace",),
                result=("namespace", "active"),
                refusals=(
                    Refusal(
                        "UPSTREAM_NAMESPACE_UNKNOWN", "the namespace is not declared"
                    ),
                ),
            ),
            ToolStep(
                "registry_deactivate",
                params=("namespace",),
                result=("namespace", "active"),
                refusals=(
                    Refusal(
                        "UPSTREAM_NAMESPACE_UNKNOWN", "the namespace is not declared"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        "inspect_scene",
        (
            ToolStep(
                "blender_get_addon_status",
                params=(),
                result=("result",),
                refusals=(
                    Refusal("ADDON_UNREACHABLE", "the add-on socket does not answer"),
                ),
            ),
            ToolStep(
                "blender_get_scene_info",
                params=("fields", "limit"),
                result=("result",),
                refusals=(),
            ),
        ),
        "Report the addon status, the connection state and the scene's objects and materials.",
    ),
    ToolUseContract(
        "build_scene",
        (
            ToolStep(
                "blender_get_scene_info",
                params=("fields", "limit"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "blender_execute_blender_code",
                params=("code",),
                result=("result",),
                refusals=(
                    Refusal(
                        "SCRIPT_BLOCKED",
                        "safe mode refused file, process, network or persistence access in the script",
                    ),
                ),
            ),
        ),
        "Add, move and shape objects with Python executed inside Blender.",
    ),
    ToolUseContract(
        "materials",
        (
            ToolStep(
                "blender_execute_blender_code",
                params=("code",),
                result=("result",),
                refusals=(
                    Refusal(
                        "SCRIPT_BLOCKED",
                        "safe mode refused file, process, network or persistence access in the script",
                    ),
                ),
            ),
            ToolStep(
                "blender_look",
                params=("mode", "target", "shading", "max_size"),
                result=("result",),
                refusals=(),
            ),
        ),
        "Author materials, textures and node graphs for objects.",
    ),
    ToolUseContract(
        "camera_lighting",
        (
            ToolStep(
                "blender_execute_blender_code",
                params=("code",),
                result=("result",),
                refusals=(
                    Refusal(
                        "SCRIPT_BLOCKED",
                        "safe mode refused file, process, network or persistence access in the script",
                    ),
                ),
            ),
            ToolStep(
                "blender_look",
                params=("mode", "shading", "max_size"),
                result=("result",),
                refusals=(),
            ),
        ),
        "Place cameras and lights and set the world environment.",
    ),
    ToolUseContract(
        "rig_animate",
        (
            ToolStep(
                "blender_execute_blender_code",
                params=("code",),
                result=("result",),
                refusals=(
                    Refusal(
                        "SCRIPT_BLOCKED",
                        "safe mode refused file, process, network or persistence access in the script",
                    ),
                ),
            ),
            ToolStep(
                "blender_get_scene_info",
                params=("root", "fields"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "blender_look",
                params=("mode", "frame_count", "shading", "max_size"),
                result=("result",),
                refusals=(),
            ),
        ),
        "Rig objects with armatures and animate actions and keyframes.",
    ),
    ToolUseContract(
        "review_viewport",
        (
            ToolStep(
                "blender_look",
                params=("mode", "shading", "max_size"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "blender_get_scene_info",
                params=("query", "fields"),
                result=("result",),
                refusals=(),
            ),
        ),
        "Review the scene with viewport screenshots.",
    ),
    ToolUseContract(
        "assets",
        (
            ToolStep(
                "blender_get_addon_status",
                params=(),
                result=("result",),
                refusals=(
                    Refusal("ADDON_UNREACHABLE", "the add-on socket does not answer"),
                ),
            ),
            ToolStep(
                "blender_search_assets",
                params=("source", "query", "asset_type", "limit"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "blender_import_asset",
                params=("source", "id", "asset_type", "target_size", "resolution"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ASSET_NOT_FOUND", "the library holds no asset with that id"
                    ),
                ),
            ),
        ),
        "Search and import library assets into the scene.",
    ),
    ToolUseContract(
        "generative_3d",
        (
            ToolStep(
                "blender_get_addon_status",
                params=(),
                result=("result",),
                refusals=(
                    Refusal("ADDON_UNREACHABLE", "the add-on socket does not answer"),
                ),
            ),
            ToolStep(
                "blender_generate_3d",
                params=("prompt", "name", "wait_seconds"),
                result=("result",),
                refusals=(
                    Refusal(
                        "PROVIDER_UNAVAILABLE",
                        "no generation provider is enabled for this user",
                    ),
                ),
            ),
            ToolStep(
                "blender_get_scene_info",
                params=("query", "fields"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "blender_generate_gaussian_world",
                params=(),
                result=("result",),
                refusals=(
                    Refusal(
                        "PROVIDER_UNAVAILABLE",
                        "no world generator is enabled for this user",
                    ),
                ),
            ),
        ),
        "Generate 3D content from text or images; these operations may cost credits.",
    ),
    ToolUseContract(
        "session_controls",
        (
            ToolStep(
                "blender_disable_telemetry",
                params=("user_prompt",),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "blender_record_trajectory_feedback",
                params=("feedback", "correction_text"),
                result=("result",),
                refusals=(),
            ),
        ),
        "Session maintenance: telemetry opt-out and trajectory feedback.",
    ),
    ToolUseContract(
        "export_and_validate_kit",
        (
            ToolStep(
                "blender_execute_blender_code",
                params=("code",),
                result=("result",),
                refusals=(
                    Refusal(
                        "SCRIPT_BLOCKED",
                        "safe mode refused file, process, network or persistence access in the script",
                    ),
                ),
            ),
            ToolStep(
                "blender_look",
                params=("mode", "target", "views", "max_size"),
                result=("result",),
                refusals=(),
            ),
            ToolStep(
                "blender_get_scene_info",
                params=("root", "fields"),
                result=("result",),
                refusals=(),
            ),
        ),
        "Build one asset-kit family in the live session from its kit script, export it as GLB, and report its triangle counts, LOD nodes and sockets.",
    ),
)

LINKS = (
    SurfaceLink(
        "check-readiness",
        tools=(
            "handshake",
            "registry_status",
            "registry_list_namespaces",
            "registry_activate",
            "registry_deactivate",
        ),
        skills=("blender",),
    ),
    SurfaceLink(
        "inspect_scene",
        tools=(
            "blender_get_addon_status",
            "blender_get_scene_info",
        ),
        prompts=("blender-inspect_scene",),
        skills=("blender-inspect-scene",),
    ),
    SurfaceLink(
        "build_scene",
        tools=(
            "blender_execute_blender_code",
            "blender_get_scene_info",
        ),
        prompts=("blender-build_scene",),
        skills=("blender-build-scene",),
    ),
    SurfaceLink(
        "materials",
        tools=(
            "blender_execute_blender_code",
            "blender_look",
        ),
        prompts=("blender-materials",),
        skills=("blender-materials",),
    ),
    SurfaceLink(
        "camera_lighting",
        tools=(
            "blender_execute_blender_code",
            "blender_look",
        ),
        prompts=("blender-camera_lighting",),
        skills=("blender-camera-lighting",),
    ),
    SurfaceLink(
        "rig_animate",
        tools=(
            "blender_execute_blender_code",
            "blender_get_scene_info",
            "blender_look",
        ),
        prompts=("blender-rig_animate",),
        skills=("blender-rig-animate",),
    ),
    SurfaceLink(
        "review_viewport",
        tools=(
            "blender_look",
            "blender_get_scene_info",
        ),
        prompts=("blender-review_viewport",),
        skills=("blender-review-viewport",),
    ),
    SurfaceLink(
        "assets",
        tools=(
            "blender_get_addon_status",
            "blender_search_assets",
            "blender_import_asset",
        ),
        prompts=("blender-assets",),
        skills=("blender-assets",),
    ),
    SurfaceLink(
        "generative_3d",
        tools=(
            "blender_get_addon_status",
            "blender_generate_3d",
            "blender_generate_gaussian_world",
            "blender_get_scene_info",
        ),
        prompts=("blender-generative_3d",),
        skills=("blender-generative-3d",),
    ),
    SurfaceLink(
        "session_controls",
        tools=(
            "blender_disable_telemetry",
            "blender_record_trajectory_feedback",
        ),
        prompts=("blender-session_controls",),
        skills=("blender-session-controls",),
    ),
    SurfaceLink(
        "export_and_validate_kit",
        tools=(
            "blender_execute_blender_code",
            "blender_look",
            "blender_get_scene_info",
        ),
        prompts=("blender-export_and_validate_kit",),
        skills=("blender-export-and-validate-kit",),
    ),
    SurfaceLink(
        "role-operator",
        prompts=("blender-operator",),
    ),
    SurfaceLink(
        "role-scene-builder",
        prompts=("blender-scene_builder",),
    ),
    SurfaceLink(
        "role-lookdev-lighting-artist",
        prompts=("blender-lookdev_lighting_artist",),
    ),
    SurfaceLink(
        "role-technical-animator",
        prompts=("blender-technical_animator",),
    ),
)

LOCATIONS = (
    DataLocation(
        "scene",
        holds=("BlenderFile", "Scene", "Object", "Material", "Camera", "Light", "Rig"),
        instance="the open .blend session in the running Blender",
        read_tool="blender_get_scene_info",
    ),
    DataLocation(
        "asset_libraries",
        holds=("Object", "Material"),
        instance="Poly Haven, Sketchfab and Poly Pizza",
        read_tool="blender_search_assets",
    ),
    DataLocation(
        "generators",
        holds=("Object",),
        instance="the 3D generation providers and the world generator",
        read_tool="blender_get_addon_status",
    ),
    DataLocation(
        "renders",
        holds=("Render",),
        instance="the images returned by look and the in-session Render Result",
        read_tool="blender_look",
    ),
)

ROLES = (
    BusinessRole(
        "scene_builder",
        tasks=("inspect_scene", "build_scene", "assets", "review_viewport"),
        description="Lay out a scene with objects and library assets at correct real-world scale, and prove the layout with numbers and images.",
    ),
    BusinessRole(
        "lookdev_lighting_artist",
        tasks=("materials", "camera_lighting", "review_viewport"),
        description="Make the scene read well: materials, lights, world and camera framing, verified with rendered looks.",
    ),
    BusinessRole(
        "technical_animator",
        tasks=("build_scene", "rig_animate", "review_viewport"),
        description="Rig objects and animate them, then prove the motion across the frame range.",
    ),
)
