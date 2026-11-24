# Gateway fleet seam contract

Provider: arbora ARBORA-FLEET-R061
Consumer: blender-connector CONN-BLENDER-CONNECTOR-R008

Counterpart: arbora `specs/fleet-catalog-and-tools/requirements.md`, row `ARBORA-FLEET-R061`.

## Wire shape

The connector is one fleet server named `blender-connector`, declared by the single `scion_sdk.connector` entry point in `pyproject.toml`. Every proxied tool carries the metadata key `scion/upstream` with the value `{namespace, upstream}`. The gateway reads `namespace` as the item group: `blender`. The shipped declaration is `activation: active`, so the gateway catalog holds every proxied tool without an extra setting. The gateway operations `fleet.tools.load` and `fleet.tools.unload` accept `groups`.

## Refusal codes

The connector adds no code. The gateway reports `UNAVAILABLE` for a registered server with no admitted tool (`ARBORA-FLEET-R060.4`). An unknown group returns an empty result and no error.
