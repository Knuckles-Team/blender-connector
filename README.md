# Blender Connector
## CLI or API | MCP

![PyPI - Version](https://img.shields.io/pypi/v/blender-connector)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/blender-connector)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/blender-connector)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/blender-connector)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/blender-connector)
![PyPI - License](https://img.shields.io/pypi/l/blender-connector)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/blender-connector)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/blender-connector)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/blender-connector)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/blender-connector)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/blender-connector)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/blender-connector)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/blender-connector)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/blender-connector)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/blender-connector)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/blender-connector)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/blender-connector)

> **Documentation** — Installation, deployment, and usage are maintained in the
> [official documentation](https://knuckles-team.github.io/blender-connector/).

---

## Overview

**Blender Connector** is a Model Context Protocol (MCP) server for Blender 3D scene work. It **proxies the third-party `mcp-for-blender` upstream** (formerly `blender-mcp`) instead of reimplementing it, and serves the packaged Blender skills, prompts and ontology alongside it. It is built on the shared connector SDK (`scion-sdk`).

The upstream talks to a running Blender through an add-on socket (default `localhost:9876`). With Blender down, the `blender_*` calls return the upstream's actionable timeout text while the server, the registry and the content keep serving.

---

## Key Features

- **Wraps, does not reimplement:** the upstream is a pooled stdio child namespaced `blender`; every upstream tool is served as `blender_<tool>` with the `scion/upstream` metadata, and upstream resources pass through unmodified.
- **Complete surface:** nine functionality skills plus a router skill, one prompt per functionality plus an operator and three role prompts (scene builder, look-dev and lighting artist, technical animator), and an ontology of tool-use contracts and data locations.
- **Safe by default:** safe mode (`BLENDER_MCP_SAFE_MODE=1`) and the telemetry opt-out are shipped in the example client entry, and the child gets a clean environment.
- **Readiness without Blender:** the connector-native `handshake` tool checks the upstream binary and the add-on socket without any Blender protocol traffic.
- **Drift gates:** a committed tool snapshot, byte-checked generated content and a live drift check against the upstream.

---

## MCP

### Available MCP Tools

| MCP Tool | Description |
|----------|-------------|
| `handshake` | Local readiness check: upstream binary on PATH and add-on socket reachable. |
| `blender_get_addon_status` | Version, add-on match, and which libraries and generators are on. |
| `blender_get_scene_info` | Scene facts as text: objects, placement, health, settings. |
| `blender_execute_blender_code` | Run Python (bpy, bmesh, mathutils) in the live Blender. |
| `blender_look` | See the scene as an image: viewport, camera, angles or frames. |
| `blender_search_assets` | Search Poly Haven, Sketchfab and Poly Pizza. |
| `blender_import_asset` | Import a found asset into the scene. |
| `blender_generate_3d` | Generate one textured model from a prompt or an image (may cost credits). |
| `blender_generate_gaussian_world` | Generate a Gaussian-splat environment (may cost credits; Blender 5.3+). |
| `blender_disable_telemetry` | Turn off data collection for the session. |
| `blender_record_trajectory_feedback` | Record accept, reject, undo or correction feedback. |
| `registry_list_namespaces`, `registry_activate`, `registry_deactivate`, `registry_status` | SDK registry tools for the upstream namespace. |

### Skills and prompts

| Skill | Use it to |
|-------|-----------|
| `blender` | Router: pick the functionality skill. |
| `blender-inspect-scene` | Report status and scene facts. |
| `blender-build-scene` | Add, move and shape objects with Python. |
| `blender-materials` | Author materials and node graphs. |
| `blender-camera-lighting` | Cameras, lights, world, render device. |
| `blender-rig-animate` | Armatures, keyframes and actions. |
| `blender-review-viewport` | Review with viewport and rendered looks. |
| `blender-assets` | Search and import library assets. |
| `blender-generative-3d` | Generate models and worlds. |
| `blender-session-controls` | Telemetry opt-out and feedback. |

Every skill has numbered steps (one objective and one check each), concrete tool arguments, an error-recovery table, and when-to-use and when-not-to-use guidance. Prompts are served as `blender-<functionality>`, `blender-operator`, `blender-scene_builder`, `blender-lookdev_lighting_artist` and `blender-technical_animator`.

### MCP Configuration Examples

#### stdio Transport (local IDEs: Cursor, Claude Desktop, VS Code)

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["--from", "blender-connector[mcp]", "blender-connector"],
      "env": {
        "DISABLE_TELEMETRY": "1",
        "BLENDER_MCP_SAFE_MODE": "1",
        "SCION_UPSTREAMS_INHERIT_ENV": "PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT,BLENDER_MCP_SAFE_MODE"
      }
    }
  }
}
```

#### Streamable-HTTP Transport (networked)

```sh
blender-connector --transport streamable-http --host 0.0.0.0 --port 8000
```

The Blender add-on socket has no authentication: keep it on the same host or pod as the connector, never on an untrusted network.

---

## Environment Variables

| Setting | Meaning | Start value |
|---|---|---|
| `DISABLE_TELEMETRY` | Telemetry opt-out, inherited by the upstream child | `1` |
| `BLENDER_MCP_SAFE_MODE` | Validate scripts before they run in Blender, inherited by the upstream child | `1` |
| `BLENDER_HOST` / `BLENDER_PORT` | The add-on socket address, inherited by the upstream child | `localhost` / `9876` |
| `SCION_UPSTREAMS_INHERIT_ENV` | The child environment whitelist that carries the rows above | `PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT,BLENDER_MCP_SAFE_MODE` |
| `SCION_UPSTREAMS_FILE` | An operator overlay TOML (example: `docs/upstreams.example.toml`) | unset |
| `BLENDERTOOL` | Toggle for the connector-native tool surface | on |

---

## Installation

```sh
pip install "blender-connector[mcp]"
uv tool install mcp-for-blender        # the upstream binary must be on PATH
uvx mcp-for-blender install-addon      # install the Blender add-on, then enable it in Blender
blender-connector                      # serve the MCP server (stdio by default)
blender-connector-probe                # probe the upstream after an update
```

The upstream binary is `mcp-for-blender` (the package was named `blender-mcp` before version 2). For a headless GPU deployment (virtual display, Cycles CUDA) see [docs/deployment.md](docs/deployment.md).

---

## Documentation

See [docs/](docs/index.md): overview, architecture, installation, usage, deployment, glossary. Specs live under `specs/`.

## Development

```sh
scripts/bootstrap.sh                    # pinned environment + hooks
uvx pre-commit run --all-files          # the gate
uv run pytest tests -q                  # the suite (hermetic: fixture upstream)
uv run python scripts/generate_blender_content.py --check   # content drift gate
```

## Repository Owners

Maintained by the Knuckles Team.

## Contribute

Open an issue or a pull request on [GitHub](https://github.com/Knuckles-Team/blender-connector). Every change carries a `Spec:` trailer; see `AGENTS.md`.
