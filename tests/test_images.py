"""The two published images, the compose bundle and the deployment guide (R011 to R013, R016, R017, R019)."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest
import yaml

from blender_connector.upstreams import INHERIT_ENV_DEFAULT

ROOT = Path(__file__).parents[1]
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
CONTAINER = PYPROJECT["tool"]["pipelines"]["container"]
BLENDER = CONTAINER["targets"]["blender"]
OFFICIAL_SHA256 = "b7d09d1aa7c346fed1e56390e815dbf1589d47324734fbad9e2007fe75ca0b8d"
ADDON_VERSION = "2.3.3"
ADDON_WHEEL_SHA256 = "ca06b6be4534859648970986b49f53d8a506355d8771adb9efba7eccfb9fa869"
COMPOSE = yaml.safe_load((ROOT / "deploy" / "compose.yml").read_text(encoding="utf-8"))
GPU = yaml.safe_load((ROOT / "deploy" / "compose.gpu.yml").read_text(encoding="utf-8"))
GUIDE = (ROOT / "docs" / "deployment.md").read_text(encoding="utf-8")


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R011")
def test_connector_image_is_configured_and_published() -> None:
    stage = CONTAINER["extra_stages"][0]
    assert (
        f"mcp-for-blender=={ADDON_VERSION}" in stage
        and "uv venv /opt/mcp-for-blender" in stage
    )
    assert "FROM builder-base AS upstream" in stage
    copies = "\n".join(CONTAINER["stage_copies"])
    assert (
        "ln -s /opt/mcp-for-blender/bin/mcp-for-blender /usr/local/bin/mcp-for-blender"
        in copies
    )
    env_line = next(
        line for line in CONTAINER["stage_copies"] if line.startswith("ENV ")
    )
    env = dict(pair.split("=", 1) for pair in env_line.removeprefix("ENV ").split())
    assert env["DISABLE_TELEMETRY"] == "1" and env["BLENDER_MCP_SAFE_MODE"] == "1"
    assert env["BLENDER_HOST"] == "localhost"
    assert env["SCION_UPSTREAMS_INHERIT_ENV"] == INHERIT_ENV_DEFAULT
    workflow = (ROOT / ".github" / "workflows" / "connector.yml").read_text(
        encoding="utf-8"
    )
    assert (
        "python-connector: false" not in workflow
        and "render-connector: false" not in workflow
    )
    assert not (ROOT / "docker").exists() or not list(
        (ROOT / "docker").glob("*Dockerfile")
    )


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R012")
def test_blender_image_pins_the_application_and_the_add_on() -> None:
    assert BLENDER["template"] == "gui-runtime" and BLENDER["version"].startswith(
        "4.5."
    )
    app = BLENDER["app"]
    assert app["sha256"] == OFFICIAL_SHA256 and re.fullmatch(
        r"[0-9a-f]{64}", app["sha256"]
    )
    assert app["url"].startswith("https://download.blender.org/release/Blender4.5/")
    assert "${version}" in app["url"]
    step = BLENDER["setup"][0]
    assert (
        f"mcp-for-blender=={ADDON_VERSION}" in step
        and f"{ADDON_WHEEL_SHA256}  " in step
    )
    assert step.index("sha256sum -c") < step.index("zipfile")
    assert BLENDER["uid"] >= 1000 and BLENDER["command"][0] == "blender"
    assert BLENDER["files"] == [
        {"source": "image/blender/startup.py", "target": "/opt/gui/startup.py"}
    ]
    assert (ROOT / BLENDER["files"][0]["source"]).is_file()


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R012")
def test_blender_image_states_its_licences_and_holds_no_secret() -> None:
    assert "GPL" in BLENDER["licenses"] and "MIT" in BLENDER["licenses"]
    notice = " ".join(BLENDER["notice"])
    assert (
        "GNU General Public License" in notice
        and "download.blender.org/source" in notice
    )
    assert "MIT-licensed" in notice and "ADDON-LICENSE" in notice
    for name in BLENDER.get("env", {}):
        assert not re.search(r"KEY|SECRET|TOKEN|PASSWORD", name), name
    assert "NVIDIA_DRIVER_CAPABILITIES" not in BLENDER.get("env", {})


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R013")
def test_display_mode_defaults_to_auto_and_the_gpu_override_requests_graphics() -> None:
    assert BLENDER["display_mode"] == "auto"
    blender = GPU["services"]["blender"]
    assert (
        "NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics" in blender["environment"]
    )
    device = blender["deploy"]["resources"]["reservations"]["devices"][0]
    assert {"graphics", "compute"} <= set(device["capabilities"])
    base = COMPOSE["services"]["blender"]
    assert "deploy" not in base and not any(
        "NVIDIA" in item for item in base["environment"]
    )
    assert "GUI_DISPLAY_MODE=${GUI_DISPLAY_MODE:-auto}" in base["environment"]


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R016")
def test_compose_bundle_shares_network_and_tmp_and_publishes_only_the_connector() -> (
    None
):
    services = COMPOSE["services"]
    assert services["connector"]["network_mode"] == "service:blender"
    assert (
        "tmp:/tmp" in services["blender"]["volumes"]
        and "tmp:/tmp" in services["connector"]["volumes"]
    )
    assert "home:/home/blender" in services["blender"]["volumes"]
    ports = services["blender"]["ports"]
    assert [(p["host_ip"], p["target"]) for p in ports] == [("127.0.0.1", 8000)]
    assert "ports" not in services["connector"] and not any(
        9876 == p.get("target") for p in ports
    )
    assert (
        services["connector"]["depends_on"]["blender"]["condition"] == "service_healthy"
    )
    assert "BLENDER_MCP_SAFE_MODE=1" in services["connector"]["environment"]
    assert "DISABLE_TELEMETRY=1" in services["connector"]["environment"]
    mounts = [v for v in services["blender"]["volumes"] if isinstance(v, dict)]
    assert mounts[0]["target"] == "/run/secrets" and mounts[0]["read_only"] is True
    for name in ("blender", "connector"):
        assert services[name]["cap_drop"] == ["ALL"]
        assert "no-new-privileges:true" in services[name]["security_opt"]
    for key in ("BLENDER_IMAGE", "CONNECTOR_IMAGE"):
        assert (
            f"${{{key}:?"
            in (services["blender" if key == "BLENDER_IMAGE" else "connector"]["image"])
        )


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R016")
def test_gpu_is_an_override_not_a_requirement() -> None:
    assert set(GPU) == {"services"} and set(GPU["services"]) == {"blender"}
    assert "nvidia" in str(GPU) and "nvidia" not in str(COMPOSE).lower()


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R017")
def test_viewer_is_a_profile_bound_to_loopback_and_documented_as_gated() -> None:
    viewer = COMPOSE["services"]["viewer"]
    assert viewer["profiles"] == ["viewer"] and viewer["command"] == ["viewer"]
    assert [(p["host_ip"], p["target"]) for p in viewer["ports"]] == [
        ("127.0.0.1", 6080)
    ]
    assert BLENDER["viewer"] is True
    assert not any(p.get("host_ip") in (None, "0.0.0.0", "") for p in viewer["ports"])
    assert "authenticating gateway" in COMPOSE_TEXT or "authenticating gateway" in GUIDE
    assert (
        "behind\nauthentication" in GUIDE and "never by\npublishing the port" in GUIDE
    )


COMPOSE_TEXT = (ROOT / "deploy" / "compose.yml").read_text(encoding="utf-8")


@pytest.mark.spec("CONN-BLENDER-CONNECTOR-R019")
def test_the_deployment_guide_covers_the_images() -> None:
    for needle in (
        "<image>:<version>-blender",
        "deploy/compose.yml",
        "deploy/compose.gpu.yml",
        "GUI_DISPLAY_MODE",
        "BLENDER_SECRETS_DIR",
        "--profile viewer",
        "NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics",
        "BLENDER_MCP_SAFE_MODE=1",
        "GNU General Public\nLicense",
    ):
        assert needle in GUIDE, needle
    assert not re.search(r"\.arpa|registry\.|/home/|gr1080", GUIDE)
