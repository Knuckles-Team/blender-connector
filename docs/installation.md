# Installation

## Requirements

- Python 3.12–3.14
- the upstream binary `mcp-for-blender` on the `PATH`
  (`uv tool install mcp-for-blender`; the package was named `blender-mcp`
  before version 2, and only the new name installs the binary), with the Blender addon installed and enabled in a running
  Blender when you want live scene access
- the upstream in its **own** environment: it pins an older MCP library
  than the connector SDK, so installing both into one environment fails to
  resolve (`uv tool install` and a separate virtual environment both work)
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
        "SCION_UPSTREAMS_INHERIT_ENV": "PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT,BLENDER_MCP_SAFE_MODE"
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
