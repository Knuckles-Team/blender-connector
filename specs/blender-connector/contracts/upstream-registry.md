# Upstream registry seam contract

Provider: scion-sdk SCION-CONNECTOR-CONTROL-R914
Consumer: blender-connector CONN-BLENDER-CONNECTOR-R001

Counterpart: scion-sdk `specs/scion-connector-control/contracts/upstream-registry.md`.

## Wire shape

The connector sets `Connector.upstreams` to one `UpstreamDecl` value: `kind` `stdio`, `command` `blender-mcp`, `args` empty, `activation` `active`, `on_drift` `warn` and a `sandbox` with both root tuples empty and the SDK flag names `--automation-read-root` and `--automation-write-root`. Because both tuples are empty, no root flag is ever passed to the child. The child environment is clean: only the setting `SCION_UPSTREAMS_INHERIT_ENV` names cross, shipped as `PATH,HOME,LANG,DISABLE_TELEMETRY,BLENDER_HOST,BLENDER_PORT`. An operator overlay named by `SCION_UPSTREAMS_FILE` switches the upstream to `http`.

The SDK serves proxied tools as `blender_<tool>` with the tag `ns:blender` and the metadata key `scion/upstream`. A local tool with the `blender_` prefix is refused with `UPSTREAM_TOOL_COLLISION`.

## Refusal codes

The connector adds no refusal code at this seam. It passes through `UPSTREAM_ROOTS_REQUIRED`, `UPSTREAM_SPAWN_FAILED`, `UPSTREAM_SECRET_LITERAL`, `UPSTREAM_EGRESS_REFUSED`, `UPSTREAM_DECL_INVALID` and `UPSTREAM_DRIFT_REFUSED` from the SDK.
