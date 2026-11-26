"""CONN-BLENDER-CONNECTOR-CONTENT-R004: every skill meets the quality bar.

Each functionality skill states when to use and when not to use, has
numbered steps that each carry a check, concrete tool arguments, and an
error-recovery table. Every prompt links its skills.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent / "blender_connector"

pytestmark = pytest.mark.spec("CONN-BLENDER-CONNECTOR-CONTENT-R004")


def _skills() -> list[Path]:
    return sorted(ROOT.glob("skills/blender-*/SKILL.md"))


def test_there_is_one_skill_per_functionality() -> None:
    assert len(_skills()) == 9


@pytest.mark.parametrize("path", _skills(), ids=lambda p: p.parent.name)
def test_functionality_skill_shape(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert re.search(rf"^name: {path.parent.name}$", text, re.M)
    assert "Do NOT use for" in text
    assert "## When to use" in text and "## When NOT to use" in text
    steps = re.findall(r"^\d+\. \*\*", text, re.M)
    assert steps
    checks = text.count("- Check:")
    assert checks >= len([s for s in steps if s])
    assert "## Error recovery" in text and "| Symptom | Likely cause | Fix |" in text


def test_prompts_link_existing_skills() -> None:
    names = {path.parent.name for path in ROOT.glob("skills/*/SKILL.md")}
    for path in ROOT.glob("prompts/blender-*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["skills"], path.name
        assert set(document["skills"]) <= names, path.name
