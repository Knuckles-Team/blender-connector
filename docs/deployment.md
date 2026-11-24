# Deployment

## Local (default)

The connector serves stdio and starts the local `blender-mcp` binary as a
pooled stdio child on first use. One MCP client entry (see
`mcp_config.json`) is the whole deployment.

## Remote HTTP overlay

When a host serves the upstream's surface over streamable HTTP, an
operator overlay switches the declaration:

```toml
# named by SCION_UPSTREAMS_FILE
[[upstream]]
name = "blender"
kind = "http"
url = "https://<host>/mcp"
credential = "env://BLENDER_CONNECTOR_TOKEN"   # a secret reference, never a value
tls_profile = "default"
```

A working example with an unresolvable placeholder domain ships at
`docs/upstreams.example.toml`. A literal credential in the overlay
refuses the whole overlay (`UPSTREAM_DECL_INVALID`); the connector
declarations keep serving.

## Fleet (Arbora)

The connector registers once under the fleet name `blender-connector`;
the `blender` group is what the gateway loads and unloads, using the
`scion/upstream` metadata on every proxied tool. `registry_status` and
the `connector://upstreams` resource expose the upstream health for
readiness.

## Snapshot discipline

After every upstream update:

```sh
blender-connector-probe                          # does it still answer?
uv run python scripts/generate_blender_content.py --refresh   # new snapshot
uv run python scripts/generate_blender_content.py --write     # regenerate content
uv run python scripts/generate_blender_content.py --check     # drift gate
uv run python scripts/generate_blender_content.py --live      # live gate
```

Commit the refreshed snapshot and regenerated content together, with the
`Spec:` trailer of the content spec.
