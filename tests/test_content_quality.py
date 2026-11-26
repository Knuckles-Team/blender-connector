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


def test_front_matter_holds_no_character_the_engine_refuses() -> None:
    """Arbora onboarding refuses a skill whose front matter holds & * ! { or }."""
    for path in sorted(ROOT.glob("skills/*/SKILL.md")):
        front = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
        assert not set(front) & set("&*!{}"), path.parent.name


def test_the_generator_refuses_an_unsafe_description() -> None:
    from blender_connector.content_gen.errors import (
        CONTENT_FRONT_MATTER_UNSAFE,
        ContentError,
    )
    from blender_connector.content_gen.skill import _frontmatter

    with pytest.raises(ContentError) as raised:
        _frontmatter("blender", "use the blender_* tools", ["blender"])
    assert raised.value.code == CONTENT_FRONT_MATTER_UNSAFE


def test_descriptions_are_inside_the_connector_standard_budget() -> None:
    """The connector-standard hook fails a description over 400 characters."""
    for path in sorted(ROOT.glob("skills/*/SKILL.md")):
        front = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
        text = front.split("description:", 1)[1].split("\nlicense:", 1)[0]
        assert len(" ".join(text.replace(">-", "").split())) <= 400, path.parent.name


def test_the_generator_refuses_an_overlong_description() -> None:
    from blender_connector.content_gen.errors import (
        CONTENT_DESCRIPTION_TOO_LONG,
        ContentError,
    )
    from blender_connector.content_gen.skill import _frontmatter

    with pytest.raises(ContentError) as raised:
        _frontmatter("blender", "word " * 100, ["blender"])
    assert raised.value.code == CONTENT_DESCRIPTION_TOO_LONG
