"""The Blender image's start-up script (CONN-BLENDER-CONNECTOR-R014, R015)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "blender_startup", ROOT / "image" / "blender" / "startup.py"
)
assert _SPEC and _SPEC.loader
startup = importlib.util.module_from_spec(_SPEC)
sys.modules["blender_startup"] = startup
_SPEC.loader.exec_module(startup)

NEW = (4, 5, 17)


def _plan(
    env: dict[str, str], version: tuple[int, int, int] = NEW
) -> dict[str, startup.Decision]:
    decisions = startup.plan_integrations(env, startup.make_secret_reader(env), version)
    return {d.name: d for d in decisions}


def _env(tmp_path: Path, **extra: str) -> dict[str, str]:
    return {"BLENDER_SECRETS_DIR": str(tmp_path), **extra}


class _Device(SimpleNamespace):
    pass


def _cycles(devices: dict[str, list[str]]) -> SimpleNamespace:
    prefs = SimpleNamespace(compute_device_type="NONE", devices=[])

    def get_devices() -> None:
        if (
            prefs.compute_device_type not in devices
            and prefs.compute_device_type != "NONE"
        ):
            raise TypeError("unknown device type")
        names = devices.get(prefs.compute_device_type, [])
        prefs.devices = [
            _Device(type=prefs.compute_device_type, name=name, use=False)
            for name in names
        ]
        prefs.devices.append(_Device(type="CPU", name="cpu", use=True))

    prefs.get_devices = get_devices
    return prefs


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R014")
def test_install_addon_copies_once(tmp_path: Path) -> None:
    source = tmp_path / "addon.py"
    source.write_text("# add-on\n", encoding="utf-8")
    addons = tmp_path / "home" / "addons"
    assert startup.install_addon(addons, str(source)) is True
    assert (addons / "blender_mcp.py").read_text(encoding="utf-8") == "# add-on\n"
    assert startup.install_addon(addons, str(source)) is False
    source.write_text("# newer\n", encoding="utf-8")
    assert startup.install_addon(addons, str(source)) is True


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R014")
def test_cycles_uses_the_first_device_type_that_has_a_device() -> None:
    assert startup.device_order({}) == ["OPTIX", "CUDA"]
    assert startup.device_order({"BLENDER_COMPUTE_DEVICE": "hip, cuda"}) == [
        "HIP",
        "CUDA",
    ]
    prefs = _cycles({"CUDA": ["GPU 0", "GPU 1"]})
    kind, names = startup.configure_cycles(prefs, ["OPTIX", "CUDA"])
    assert (kind, names) == ("CUDA", ["GPU 0", "GPU 1"])
    assert prefs.compute_device_type == "CUDA"
    assert [d.use for d in prefs.devices] == [True, True, False]
    scene = SimpleNamespace(
        render=SimpleNamespace(engine=""), cycles=SimpleNamespace(device="")
    )
    startup.select_render_device(scene, True)
    assert (scene.render.engine, scene.cycles.device) == ("CYCLES", "GPU")


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R014")
def test_cycles_falls_back_to_the_cpu_when_no_device_exists() -> None:
    prefs = _cycles({})
    assert startup.configure_cycles(prefs, ["OPTIX", "CUDA"]) == ("CPU", [])
    assert prefs.compute_device_type == "NONE" and not any(d.use for d in prefs.devices)
    scene = SimpleNamespace(
        render=SimpleNamespace(engine=""), cycles=SimpleNamespace(device="")
    )
    startup.select_render_device(scene, False)
    assert scene.cycles.device == "CPU"


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R015")
def test_keys_come_from_a_mounted_file_then_the_environment(tmp_path: Path) -> None:
    (tmp_path / "sketchfab_api_key").write_text("  from-file\n", encoding="utf-8")
    other = tmp_path / "elsewhere"
    other.write_text("explicit\n", encoding="utf-8")
    env = _env(
        tmp_path,
        BLENDER_SKETCHFAB_API_KEY="from-env",
        BLENDER_POLYPIZZA_API_KEY="env-only",
        BLENDER_TRIPO_API_KEY_FILE=str(other),
        BLENDER_MESHY_API_KEY="  ",
    )
    read = startup.make_secret_reader(env)
    assert read("sketchfab_api_key") == "from-file"
    assert read("polypizza_api_key") == "env-only"
    assert read("tripo_api_key") == "explicit"
    assert read("meshy_api_key") == "" and read("hyper3d_api_key") == ""
    plan = _plan(env)
    assert plan["sketchfab"].prefs == {"sketchfab_api_key": "from-file"}
    assert (
        plan["tripo"].enabled and plan["tripo"].scene["blendermcp_tripo_domain"] == "ai"
    )


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R015")
def test_an_integration_without_its_key_stays_off_and_says_so(tmp_path: Path) -> None:
    decisions = startup.plan_integrations(
        _env(tmp_path), startup.make_secret_reader(_env(tmp_path)), NEW
    )
    lines = startup.report(decisions)
    assert "startup: integration sketchfab: off (no sketchfab_api_key)" in lines
    assert (
        "startup: integration hunyuan3d: off (no hunyuan3d_secret_id and hunyuan3d_secret_key, and no BLENDER_HUNYUAN3D_API_URL)"
        in lines
    )
    assert "startup: integration premium: off (no premium_license_key)" in lines
    plan = {d.name: d for d in decisions}
    assert (
        plan["sketchfab"].scene == {"blendermcp_use_sketchfab": False}
        and plan["sketchfab"].prefs == {}
    )
    assert len(lines) == len(startup.INTEGRATION_NAMES)


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R015")
def test_keyless_integrations_are_on_by_default(tmp_path: Path) -> None:
    plan = _plan(_env(tmp_path))
    assert plan["polyhaven"].enabled and plan["polyhaven"].scene == {
        "blendermcp_use_polyhaven": True
    }
    assert sorted(name for name, d in plan.items() if d.enabled) == ["polyhaven"]
    keys = {
        name: "k"
        for name in (
            "BLENDER_SKETCHFAB_API_KEY",
            "BLENDER_POLYPIZZA_API_KEY",
            "BLENDER_HYPER3D_API_KEY",
            "BLENDER_TRIPO_API_KEY",
            "BLENDER_MESHY_API_KEY",
            "BLENDER_WORLDLABS_API_KEY",
            "BLENDER_HUNYUAN3D_SECRET_ID",
            "BLENDER_HUNYUAN3D_SECRET_KEY",
            "BLENDER_PREMIUM_LICENSE_KEY",
        )
    }
    everything = _plan(
        _env(
            tmp_path, **keys, BLENDER_HYPER3D_MODE="fal_ai", BLENDER_TRIPO_DOMAIN="com"
        ),
        (5, 3, 0),
    )
    assert all(d.enabled for d in everything.values())
    assert everything["hyper3d"].scene["blendermcp_hyper3d_mode"] == "FAL_AI"
    assert everything["tripo"].scene["blendermcp_tripo_domain"] == "com"
    assert everything["hunyuan3d"].scene["blendermcp_hunyuan3d_mode"] == "OFFICIAL_API"
    assert everything["premium"].prefs["generation_source"] == "PREMIUM"


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R015")
def test_selection_and_off_lists_limit_the_set(tmp_path: Path) -> None:
    keys = {"BLENDER_SKETCHFAB_API_KEY": "k", "BLENDER_MESHY_API_KEY": "k"}
    only = _plan(_env(tmp_path, **keys, BLENDER_INTEGRATIONS="polyhaven,meshy"))
    assert sorted(n for n, d in only.items() if d.enabled) == ["meshy", "polyhaven"]
    assert only["sketchfab"].reason == "not selected by BLENDER_INTEGRATIONS"
    off = _plan(_env(tmp_path, **keys, BLENDER_INTEGRATIONS_OFF="meshy, polyhaven"))
    assert sorted(n for n, d in off.items() if d.enabled) == ["sketchfab"]
    assert off["meshy"].reason == "switched off by BLENDER_INTEGRATIONS_OFF"
    local = _plan(_env(tmp_path, BLENDER_HUNYUAN3D_API_URL="http://localhost:8081"))
    assert (
        local["hunyuan3d"].enabled
        and local["hunyuan3d"].scene["blendermcp_hunyuan3d_mode"] == "LOCAL_API"
    )


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R015")
def test_preferences_hold_keys_and_keep_telemetry_off(tmp_path: Path) -> None:
    plan = startup.plan_integrations(
        _env(tmp_path, BLENDER_SKETCHFAB_API_KEY="sk-1", BLENDER_MESHY_API_KEY="  "),
        startup.make_secret_reader(
            _env(tmp_path, BLENDER_SKETCHFAB_API_KEY="sk-1", BLENDER_MESHY_API_KEY="  ")
        ),
        NEW,
    )
    prefs = SimpleNamespace(telemetry_consent=True, allow_remote_connections=True)
    startup.apply_preferences(prefs, plan)
    assert prefs.telemetry_consent is False and prefs.allow_remote_connections is False
    assert prefs.sketchfab_api_key == "sk-1" and not hasattr(prefs, "meshy_api_key")
    scene = SimpleNamespace(
        blendermcp_use_sketchfab=False,
        blendermcp_use_meshy=True,
        blendermcp_use_polyhaven=False,
    )
    startup.apply_scene(scene, plan)
    assert (
        scene.blendermcp_use_sketchfab is True and scene.blendermcp_use_meshy is False
    )
    assert scene.blendermcp_use_polyhaven is True


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R015")
def test_a_gated_integration_stays_off_on_an_older_blender(tmp_path: Path) -> None:
    env = _env(tmp_path, BLENDER_WORLDLABS_API_KEY="k")
    assert _plan(env)["worldlabs"].reason == "needs Blender 5.3 or newer"
    assert not _plan(env)["worldlabs"].enabled
    assert _plan(env, (5, 3, 0))["worldlabs"].enabled


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R014")
def test_the_add_ons_directory_is_put_on_the_import_path_once(tmp_path: Path) -> None:
    path: list[str] = ["/usr/lib"]
    assert startup.ensure_importable(tmp_path, path) is True
    assert startup.ensure_importable(tmp_path, path) is False
    assert path == ["/usr/lib", str(tmp_path)]
