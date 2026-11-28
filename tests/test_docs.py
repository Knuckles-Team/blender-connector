"""CONN-BLENDER-CONNECTOR-R021: the add-on socket risk is documented."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-R021")

ROOT = Path(__file__).resolve().parent.parent
RULES = (
    "loopback address only",
    "same host as Blender",
    "port mapping",
    "dedicated user",
    "fleet.call",
)


def test_readme_and_skill_state_the_addon_socket_risk() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Security: the add-on socket" in readme
    section = readme.split("## Security: the add-on socket", 1)[1].split("\n## ", 1)[0]
    skill = (ROOT / "blender_connector/skills/blender/SKILL.md").read_text(
        encoding="utf-8"
    )
    for rule in RULES:
        assert rule in section, rule
        assert rule in skill, rule
