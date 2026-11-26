"""Fixtures: the fixture upstream on PATH and the overlay writer."""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest


@pytest.fixture
def blender_cli_factory(tmp_path, monkeypatch):
    """Place the fixture upstream on the PATH as ``mcp-for-blender``.

    Returns ``make(**knobs) -> wrapper_path``. The factory prepends its
    bin directory to the PATH for the rest of the test.
    """
    fixture = Path(__file__).resolve().parent / "fixtures" / "fake_blender_mcp.py"
    bin_dir = tmp_path / "blender-bin"
    bin_dir.mkdir()
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])

    def make(*, die=False, drift=False, version="2.0.0-fixture"):
        wrapper = bin_dir / "mcp-for-blender"
        env_lines = []
        if die:
            env_lines.append("BLENDER_FIXTURE_DIE=1")
        if drift:
            env_lines.append("BLENDER_FIXTURE_TOOL_DRIFT=1")
        body = "\n".join(f"export {line}\n" for line in env_lines)
        wrapper.write_text(
            "#!/bin/sh\n"
            + body
            + f'BLENDER_FIXTURE_VERSION="{version}"\n'
            + "export BLENDER_FIXTURE_VERSION\n"
            + f'exec "{sys.executable}" "{fixture}" "$@"\n',
            encoding="utf-8",
        )
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)
        return wrapper

    return make


@pytest.fixture
def overlay_writer(tmp_path):
    """Write one overlay TOML; returns the path."""

    def write(text: str) -> Path:
        path = tmp_path / "overlay.toml"
        path.write_text(text, encoding="utf-8")
        return path

    return write


@pytest.fixture
def clean_upstream_env(monkeypatch):
    """Remove the upstream knobs so a test sets them explicitly."""
    for var in (
        "SCION_UPSTREAMS_FILE",
        "SCION_UPSTREAMS_DISABLED",
        "SCION_UPSTREAMS_INHERIT_ENV",
        "SCION_UPSTREAM_ACTIVATION",
        "DISABLE_TELEMETRY",
        "BLENDER_HOST",
        "BLENDER_PORT",
    ):
        monkeypatch.delenv(var, raising=False)
