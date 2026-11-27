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

## Container images

A `v*` tag publishes two images from one CI run, both built from configuration in
`pyproject.toml` (the repository commits no Dockerfile):

| Image | Tag | Holds |
|---|---|---|
| connector | `<image>:<version>` | `blender-connector` and the pinned `mcp-for-blender` upstream in its own virtual environment, command on `PATH` |
| Blender | `<image>:<version>-blender` | Blender (pinned by version and SHA-256), the pinned MCP for Blender add-on, a virtual display, the start-up script |

Pin both by digest in a deployment. The add-on refuses to start its socket server under
`blender -b`, so the Blender image runs Blender under a display it starts itself. The add-on
binds to `localhost` and has no authentication: keep both containers in one pod or one network
namespace and never publish port 9876.

### Compose bundle

`deploy/compose.yml` runs both containers in one network namespace with one shared `/tmp`
(the upstream hands screenshots from Blender to the server through files there, and
`blender_look` fails with a missing file otherwise):

```sh
BLENDER_IMAGE=<blender image@digest> CONNECTOR_IMAGE=<connector image@digest> \
  docker compose -f deploy/compose.yml up -d
```

Only the connector port (`CONNECTOR_PORT`, default 8000) is published, on loopback. The
connector keeps `BLENDER_MCP_SAFE_MODE=1` and `DISABLE_TELEMETRY=1`. Safe mode blocks the
agent from Blender preferences, so the start-up script sets the compute device and the
integrations, never the agent. The home volume keeps Blender's preferences across restarts.

### GPU and display

Add `-f deploy/compose.gpu.yml` to give the Blender container the GPU
(`NVIDIA_VISIBLE_DEVICES`, `NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics`). The start-up
script tries the Cycles device types in `BLENDER_COMPUTE_DEVICE` order (default `OPTIX,CUDA`),
enables every device of the first type that has one, and renders on the CPU when none exists.

`GUI_DISPLAY_MODE` selects the display:

- `auto` (default): a GPU-driven X server when the runtime exposes a GPU and its X driver,
  otherwise a software virtual display, with a note on stdout.
- `nvidia`: the GPU-driven X server, or exit with an error.
- `xvfb`: the software virtual display.

Both start directly in the entrypoint; the `xvfb-run` wrapper hangs when it is PID 1 of a
container. A pod needs the NVIDIA runtime, `NVIDIA_VISIBLE_DEVICES` and the capabilities above.
No GPU is needed to run the images: CI starts them on a software display.

### Integrations and secrets

The start-up script switches on every integration of the add-on (asset libraries and 3D
generators) for which it holds what is needed, and prints one line per integration:

```text
startup: integration polyhaven: on (no key needed)
startup: integration sketchfab: off (no sketchfab_api_key)
```

A key is read at start, never from the image, in this order: the file named by
`BLENDER_<NAME>_FILE`, a mounted file `<name>` in `BLENDER_SECRETS_DIR` (default
`/run/secrets`), then the variable `BLENDER_<NAME>`. The names are
`sketchfab_api_key`, `polypizza_api_key`, `hyper3d_api_key`, `tripo_api_key`, `meshy_api_key`,
`worldlabs_api_key`, `hunyuan3d_secret_id` with `hunyuan3d_secret_key` (or a local service in
`BLENDER_HUNYUAN3D_API_URL`) and `premium_license_key`. An integration without its key stays
off. `BLENDER_INTEGRATIONS` limits the set (default `all`), `BLENDER_INTEGRATIONS_OFF` removes
members, `BLENDER_HYPER3D_MODE` and `BLENDER_TRIPO_DOMAIN` select a provider mode. Mount the
secrets read-only (a compose bind mount, or a Kubernetes secret volume).

### Optional watch-and-drive session

`docker compose -f deploy/compose.yml --profile viewer up -d` adds a third container that
attaches a remote-desktop server to the Blender display and serves a browser client on
`VIEWER_PORT` (default 6080, loopback). It is off by default. It must sit behind
authentication: expose it only through a gateway that authenticates the user, never by
publishing the port. `GUI_VNC_VIEWONLY=1` makes it watch-only, and a `vnc_password` secret
adds a session password.

### Licences

The Blender image contains Blender, which is free software under the GNU General Public
License (version 3 or later); its source for the pinned version is available from the Blender
project, as the notice in `/usr/share/doc/blender-image/NOTICE` states. The MCP for Blender
add-on is MIT-licensed and its licence text ships in the image. The image holds no API key.
