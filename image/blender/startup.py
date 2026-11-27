"""Start-up script of the Blender image: add-on, Cycles device, integrations.

Blender runs it once at start (``blender --python``). It installs the pinned MCP for Blender
add-on into the user add-ons directory, enables it, selects the Cycles compute device (GPU
with a CPU fallback), and switches on every integration the add-on offers for which it holds
what the integration needs. The script, not the agent, owns all of this: the connector runs
with safe mode on, which blocks the agent from preferences.

Secrets (API keys) never live in the image. Each key is read at start from a mounted file
(``<BLENDER_SECRETS_DIR>/<name>``, default ``/run/secrets``, or the path named by
``BLENDER_<NAME>_FILE``) or, failing that, from the environment variable ``BLENDER_<NAME>``.
An integration whose key is absent stays off and the script prints that on stdout. The
preferences persist under the home volume, so a restart keeps them.

Configuration (environment):
    BLENDER_INTEGRATIONS        "all" (default) or a comma list of integrations to consider
    BLENDER_INTEGRATIONS_OFF    comma list of integrations to keep off
    BLENDER_SECRETS_DIR         directory of mounted secret files (default /run/secrets)
    BLENDER_COMPUTE_DEVICE      comma list of Cycles device types in order (default OPTIX,CUDA)
    BLENDER_HYPER3D_MODE        MAIN_SITE (default) or FAL_AI
    BLENDER_TRIPO_DOMAIN        ai (default) or com
    BLENDER_HUNYUAN3D_API_URL   a local Hunyuan3D service; selects its local mode without keys
"""

from __future__ import annotations

import os
import shutil
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ADDON_MODULE = "blender_mcp"
ADDON_SOURCE = "/etc/blender-addons/blender_mcp.py"
DEFAULT_SECRETS_DIR = "/run/secrets"
DEFAULT_DEVICE_ORDER = ("OPTIX", "CUDA")
#: The add-on gates World Labs on Blender 5.3 or newer.
WORLDLABS_MIN_BLENDER = (5, 3, 0)


@dataclass(frozen=True)
class Integration:
    """One add-on integration: its scene switch and the secrets it needs."""

    name: str
    scene_flag: str
    label: str
    secrets: tuple[str, ...] = ()
    #: scene or preference property per secret name
    prefs: Mapping[str, str] = field(default_factory=dict)


INTEGRATIONS: tuple[Integration, ...] = (
    Integration("polyhaven", "blendermcp_use_polyhaven", "Poly Haven"),
    Integration(
        "sketchfab",
        "blendermcp_use_sketchfab",
        "Sketchfab",
        ("sketchfab_api_key",),
        {"sketchfab_api_key": "sketchfab_api_key"},
    ),
    Integration(
        "polypizza",
        "blendermcp_use_polypizza",
        "Poly Pizza",
        ("polypizza_api_key",),
        {"polypizza_api_key": "polypizza_api_key"},
    ),
    Integration(
        "hyper3d",
        "blendermcp_use_hyper3d",
        "Hyper3D Rodin",
        ("hyper3d_api_key",),
        {"hyper3d_api_key": "hyper3d_api_key"},
    ),
    Integration(
        "hunyuan3d",
        "blendermcp_use_hunyuan3d",
        "Hunyuan3D",
        ("hunyuan3d_secret_id", "hunyuan3d_secret_key"),
        {
            "hunyuan3d_secret_id": "hunyuan3d_secret_id",
            "hunyuan3d_secret_key": "hunyuan3d_secret_key",
        },
    ),
    Integration(
        "tripo",
        "blendermcp_use_tripo",
        "Tripo",
        ("tripo_api_key",),
        {"tripo_api_key": "tripo_api_key"},
    ),
    Integration(
        "meshy",
        "blendermcp_use_meshy",
        "Meshy",
        ("meshy_api_key",),
        {"meshy_api_key": "meshy_api_key"},
    ),
    Integration(
        "worldlabs",
        "blendermcp_use_worldlabs",
        "World Labs",
        ("worldlabs_api_key",),
        {"worldlabs_api_key": "worldlabs_api_key"},
    ),
)
INTEGRATION_NAMES = tuple(item.name for item in INTEGRATIONS) + ("premium",)


@dataclass
class Decision:
    """The outcome for one integration: on or off, why, and what to apply."""

    name: str
    enabled: bool
    reason: str
    prefs: dict[str, str] = field(default_factory=dict)
    scene: dict[str, Any] = field(default_factory=dict)


def _split(raw: str) -> list[str]:
    return [part.strip().lower() for part in raw.split(",") if part.strip()]


def make_secret_reader(env: Mapping[str, str]) -> Callable[[str], str]:
    """A reader of one secret by name: ``..._FILE`` path, mounted file, then environment."""
    directory = Path(env.get("BLENDER_SECRETS_DIR", DEFAULT_SECRETS_DIR))

    def read(name: str) -> str:
        upper = name.upper()
        explicit = env.get(f"BLENDER_{upper}_FILE", "")
        for candidate in ([Path(explicit)] if explicit else []) + [directory / name]:
            try:
                value = candidate.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if value:
                return value
        return env.get(f"BLENDER_{upper}", "").strip()

    return read


def _selected(env: Mapping[str, str]) -> tuple[set[str], set[str]]:
    wanted = _split(env.get("BLENDER_INTEGRATIONS", "all"))
    chosen = set(INTEGRATION_NAMES) if not wanted or "all" in wanted else set(wanted)
    return chosen, set(_split(env.get("BLENDER_INTEGRATIONS_OFF", "")))


def _decide_hunyuan(read: Callable[[str], str], env: Mapping[str, str]) -> Decision:
    secret_id, secret_key = read("hunyuan3d_secret_id"), read("hunyuan3d_secret_key")
    url = env.get("BLENDER_HUNYUAN3D_API_URL", "").strip()
    if secret_id and secret_key:
        prefs = {"hunyuan3d_secret_id": secret_id, "hunyuan3d_secret_key": secret_key}
        if url:
            prefs["hunyuan3d_api_url"] = url
        return Decision(
            "hunyuan3d",
            True,
            "official API keys present",
            prefs,
            {"blendermcp_hunyuan3d_mode": "OFFICIAL_API"},
        )
    if url:
        return Decision(
            "hunyuan3d",
            True,
            "local service URL configured",
            {"hunyuan3d_api_url": url},
            {
                "blendermcp_hunyuan3d_mode": "LOCAL_API",
                "blendermcp_hunyuan3d_api_url": url,
            },
        )
    return Decision(
        "hunyuan3d",
        False,
        "no hunyuan3d_secret_id and hunyuan3d_secret_key, and no BLENDER_HUNYUAN3D_API_URL",
    )


def _scene_extras(name: str, env: Mapping[str, str]) -> dict[str, Any]:
    if name == "hyper3d":
        mode = env.get("BLENDER_HYPER3D_MODE", "MAIN_SITE").upper()
        return {
            "blendermcp_hyper3d_mode": mode
            if mode in ("MAIN_SITE", "FAL_AI")
            else "MAIN_SITE"
        }
    if name == "tripo":
        domain = env.get("BLENDER_TRIPO_DOMAIN", "ai").lower()
        return {"blendermcp_tripo_domain": domain if domain in ("ai", "com") else "ai"}
    return {}


def _off(item: Integration, reason: str) -> Decision:
    """An integration that stays off; its scene switch is written off too."""
    return Decision(item.name, False, reason, scene={item.scene_flag: False})


def plan_integrations(
    env: Mapping[str, str],
    read: Callable[[str], str],
    blender_version: tuple[int, int, int],
) -> list[Decision]:
    """Decide every integration from configuration and the secrets that are present."""
    chosen, off = _selected(env)
    decisions: list[Decision] = []
    for item in INTEGRATIONS:
        if item.name not in chosen:
            decisions.append(_off(item, "not selected by BLENDER_INTEGRATIONS"))
            continue
        if item.name in off:
            decisions.append(_off(item, "switched off by BLENDER_INTEGRATIONS_OFF"))
            continue
        if item.name == "hunyuan3d":
            decision = _decide_hunyuan(read, env)
        else:
            values = {name: read(name) for name in item.secrets}
            missing = [name for name, value in values.items() if not value]
            if missing:
                decisions.append(_off(item, f"no {', '.join(missing)}"))
                continue
            prefs = {item.prefs[name]: value for name, value in values.items()}
            decision = Decision(
                item.name,
                True,
                "key present" if item.secrets else "no key needed",
                prefs,
            )
        if (
            decision.enabled
            and item.name == "worldlabs"
            and blender_version < WORLDLABS_MIN_BLENDER
        ):
            decisions.append(_off(item, "needs Blender 5.3 or newer"))
            continue
        decision.scene.update(_scene_extras(item.name, env))
        decision.scene[item.scene_flag] = decision.enabled
        decisions.append(decision)
    premium_key = (
        read("premium_license_key")
        if "premium" in chosen and "premium" not in off
        else ""
    )
    if premium_key:
        decisions.append(
            Decision(
                "premium",
                True,
                "license key present",
                {"premium_license_key": premium_key, "generation_source": "PREMIUM"},
            )
        )
    else:
        reason = (
            "no premium_license_key"
            if "premium" in chosen and "premium" not in off
            else "not selected"
        )
        decisions.append(Decision("premium", False, reason))
    return decisions


def report(decisions: list[Decision]) -> list[str]:
    """One stdout line per integration: on, or off with the reason."""
    return [
        f"startup: integration {d.name}: {'on' if d.enabled else 'off'} ({d.reason})"
        for d in decisions
    ]


def apply_preferences(prefs: Any, decisions: list[Decision]) -> None:
    """Write the enabled integrations' keys to the add-on preferences; telemetry stays off."""
    prefs.telemetry_consent = False
    prefs.allow_remote_connections = False
    for decision in decisions:
        if not decision.enabled:
            continue
        for key, value in decision.prefs.items():
            setattr(prefs, key, value)


def apply_scene(scene: Any, decisions: list[Decision]) -> None:
    """Set the per-scene switches. Every integration flag is written, on or off."""
    for decision in decisions:
        for key, value in decision.scene.items():
            if hasattr(scene, key):
                setattr(scene, key, value)


def device_order(env: Mapping[str, str]) -> list[str]:
    """The Cycles device types to try, in order."""
    raw = [
        part.strip().upper()
        for part in env.get("BLENDER_COMPUTE_DEVICE", "").split(",")
        if part.strip()
    ]
    return raw or list(DEFAULT_DEVICE_ORDER)


def configure_cycles(cycles_prefs: Any, order: list[str]) -> tuple[str, list[str]]:
    """Enable the devices of the first type that has any; return that type and the device names.

    No device of any listed type means CPU rendering: the type is ``CPU`` and the list is empty.
    """
    for device_type in order:
        try:
            cycles_prefs.compute_device_type = device_type
            cycles_prefs.get_devices()
        except (TypeError, ValueError, RuntimeError):
            continue
        enabled = []
        for device in cycles_prefs.devices:
            device.use = device.type == device_type
            if device.use:
                enabled.append(device.name)
        if enabled:
            return device_type, enabled
    cycles_prefs.compute_device_type = "NONE"
    for device in cycles_prefs.devices:
        device.use = False
    return "CPU", []


def select_render_device(scene: Any, use_gpu: bool) -> None:
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU" if use_gpu else "CPU"


def install_addon(addons_dir: Path, source: str = ADDON_SOURCE) -> bool:
    """Copy the pinned add-on into the user add-ons directory; True when it changed."""
    target = addons_dir / f"{ADDON_MODULE}.py"
    addons_dir.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() == Path(source).read_bytes():
        return False
    shutil.copyfile(source, target)
    return True


def ensure_importable(directory: Path, search_path: list[str]) -> bool:
    """Put the add-ons directory on the import path; it did not exist when Blender started."""
    entry = str(directory)
    if entry in search_path:
        return False
    search_path.append(entry)
    return True


def main() -> None:
    """Run inside Blender."""
    import addon_utils
    import bpy

    if os.getuid() == 0:
        print(
            "startup: refusing to run as root; the image runs Blender as a non-root user"
        )
        sys.exit(1)
    env = os.environ
    addons_dir = Path(bpy.utils.user_resource("SCRIPTS", path="addons", create=True))
    changed = install_addon(addons_dir)
    ensure_importable(addons_dir, sys.path)
    bpy.utils.refresh_script_paths()
    addon_utils.modules_refresh()
    if addon_utils.enable(ADDON_MODULE, default_set=True, persistent=True) is None:
        print(
            f"startup: the add-on {ADDON_MODULE} could not be enabled from {addons_dir}"
        )
        sys.exit(1)
    print(
        f"startup: add-on {ADDON_MODULE} enabled ({'installed' if changed else 'already installed'})"
    )

    version = tuple(bpy.app.version)
    decisions = plan_integrations(env, make_secret_reader(env), version)
    for line in report(decisions):
        print(line)
    apply_preferences(
        bpy.context.preferences.addons[ADDON_MODULE].preferences, decisions
    )

    device_type, enabled = configure_cycles(
        bpy.context.preferences.addons["cycles"].preferences, device_order(env)
    )
    print(
        f"startup: cycles {device_type} devices enabled: {enabled or 'none; rendering on the CPU'}"
    )

    def on_scene(*_args: Any) -> None:
        select_render_device(bpy.context.scene, bool(enabled))
        apply_scene(bpy.context.scene, decisions)

    on_scene()
    bpy.app.handlers.load_post.append(on_scene)
    bpy.ops.wm.save_userpref()


if __name__ == "__main__":
    main()
