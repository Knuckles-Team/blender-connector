"""CONN-BLENDER-CONNECTOR-R020: the connector runs on the current SDK line."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R020")

PIN = "scion-sdk[mcp]>=0.14.0,<0.15"


def test_the_sdk_pin_is_the_current_line() -> None:
    project = tomllib.loads(
        (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text(
            encoding="utf-8"
        )
    )["project"]
    assert PIN in project["dependencies"]
    assert project["optional-dependencies"]["mcp"] == [PIN]
    assert project["optional-dependencies"]["all"] == [PIN]
