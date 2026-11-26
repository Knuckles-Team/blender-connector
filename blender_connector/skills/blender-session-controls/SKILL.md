---
name: blender-session-controls
skill_type: skill
description: >-
  Session maintenance: telemetry opt-out and trajectory feedback. Use when the user asks to stop data collection, or reacts to a result (accept, reject, undo, correction). Do NOT use for any scene work, and never to turn telemetry back on: only the user can do that in Blender preferences.
license: MIT
tags: [blender, session_controls, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---

# Blender: session controls

Session maintenance: telemetry opt-out and trajectory feedback.

## When to use

The user asks to stop data collection, or reacts to a result (accept, reject, undo, correction).

## When NOT to use

Any scene work, and never to turn telemetry back on: only the user can do that in Blender preferences.

## Before you start

- The `blender` namespace is active (`registry_activate` otherwise).
- A running Blender (3.0 or newer) with the MCP for Blender add-on enabled and its server started; the add-on listens on `BLENDER_HOST:BLENDER_PORT` (default `localhost:9876`).
- Call the connector's `handshake` tool first: `ready: true` means the add-on socket answers. `ready: false` means Blender is not running, the add-on is off, or the host and port do not match.
- Save the .blend file before any `blender_execute_blender_code` call: that tool runs arbitrary Python inside the live session.
- The connector never opens its own socket to Blender; every scene action goes through a `blender_*` tool.

## Tools

| Tool | What it does |
|---|---|
| `blender_disable_telemetry` | Turn OFF collection of prompts, code, screenshots and scene data. |
| `blender_record_trajectory_feedback` | Record evaluation feedback for a captured trajectory step. |

## Steps

1. **Disable telemetry for the session when the user asks.**
   - Tool: `blender_disable_telemetry`
   - Arguments:

     ```json
     {"user_prompt": "<the user words, verbatim>"}
     ```

   - Verify: The reply confirms collection is off; `blender_get_addon_status` shows `telemetry_consent` off.
2. **Record the user's reaction to a result as feedback.**
   - Tool: `blender_record_trajectory_feedback`
   - Arguments:

     ```json
     {"feedback": "correction", "correction_text": "too dark"}
     ```

   - Verify: The reply confirms the feedback row was recorded for the last step.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Telemetry still reports on | The preference was changed in Blender after the call | Call `blender_disable_telemetry` again and read `telemetry_consent` from `blender_get_addon_status`. |
| Feedback is rejected | `feedback` is not one of accept, reject, undo, correction | Use exactly one of those values and put the user's words in `correction_text`. |
| `handshake` returns `ready: false`, or a `blender_*` call times out | Blender is not running, the add-on server is stopped, or the host and port do not match the running instance | Start Blender, open the 3D viewport sidebar (N), tab `MCP for Blender`, press `Start MCP Server`; then re-run `handshake` and confirm the port equals `BLENDER_PORT`. |
| `registry_status` shows the `blender` upstream `unavailable` with `UPSTREAM_SPAWN_FAILED` | The `mcp-for-blender` binary is not on the connector's PATH | Install it with `uv tool install mcp-for-blender` on the connector host, then call `registry_status` again. `handshake` reports `command_found`. |
| No `blender_*` tools are listed | The `blender` namespace was deactivated or lazy activation is on | Call `registry_activate` with the namespace `blender`, then list tools again. |

## Related

- Router skill `blender`; prompt `blender-session_controls`.
- Refusals are reported to the operator and never retried past the recovery rows above.
