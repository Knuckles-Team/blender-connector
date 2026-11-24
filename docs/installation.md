# Installation

## Requirements

- Python 3.12–3.14
- the upstream binary `blender-mcp` on the `PATH`
  (`uv tool install blender-mcp`, the community `mcp-for-blender`
  project), with the Blender addon installed and enabled in a running
  Blender when you want live scene access
- `uv` for the locked environment (optional but recommended)

## Source install

```sh
git clone https://github.com/Knuckles-Team/blender-connector
cd blender-connector
scripts/bootstrap.sh     # pinned Python, locked env, git hooks
blender-connector        # serve the MCP server (stdio by default)
```

Or without the bootstrap script:

```sh
pip install -e .
blender-connector
blender-connector-probe   # verify the upstream answers the MCP handshake
```

## MCP client entry

`mcp_config.json` holds a ready-to-paste entry:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["run", "blender-connector"],
      "env": {
        "DISABLE_TELEMETRY": "1",
        "SCION_UPSTREAMS_INHERIT_ENV": "PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT"
      }
    }
  }
}
```

The child environment is clean by construction: only the whitelisted names
cross to the upstream process.

## Verification

- `blender-connector-probe` prints `{"upstream": "blender", "exposes_mcp": true, …}`
- in the client: `tools/list` shows the `blender_*` tools plus
  `handshake` and the four `registry_*` tools; `handshake` reports the
  addon socket state; `skill://blender/SKILL.md` is listed as a resource.
