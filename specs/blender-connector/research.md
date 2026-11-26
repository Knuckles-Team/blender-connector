# Research

Unknowns settled while building this spec.

- The wrapped upstream is the third-party `mcp-for-blender` project (formerly `blender-mcp`). Its 2.x package installs only the `mcp-for-blender` command, so the declared command is `mcp-for-blender`.
- The upstream's add-on serves its socket only in a Blender with a display; a headless run needs a virtual display, never `blender -b`.
- The served surface for a plain MCP client is ten tools; the app-extension-only tools are outside the snapshot.
- Safe mode (`BLENDER_MCP_SAFE_MODE=1`) validates scripts before they run in Blender; the connector forwards it through the environment whitelist.
