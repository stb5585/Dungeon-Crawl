"""Focused regressions for the awakened Wizard School Streak."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core import abilities
from src.core import items
from src.core.classes import class_rings
from src.core.classes import mage_mechanics
from src.core.classes import promotion_kits
from src.core.classes import wizard
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


class _FixedRng:
    """Return one deterministic rider roll."""

    def __init__(self, value: float):
        self.value = value

    def random(self) -> float:
        return self.value


def _player(*, awakened: bool = True):
    player = TestGameState.create_player(
        class_name="Wizard",
        health=(300, 300),
        mana=(300, 300),
    )
    player.equipment["Ring"] = items.ClassRing()
    if awakened:
        success, _message = player.awaken_class_ring()
        assert success
    return player


def _spell(school: str):
    return SimpleNamespace(
        name=f"{school} Test Spell",
        school=school,
        subtyp=school,
        result=SimpleNamespace(damage=20),
    )


def _streak(player):
    return class_rings.ensure_state(player)["data"]["Wizard"]["school_streak"]


@pytest.mark.parametrize(
    ("school", "passive"),
    (
        ("Electric", abilities.Paralyzer),
        ("Wind", abilities.EjectionGale),
        ("Ice", abilities.Subzero),
        ("Water", abilities.UnrelentingWaves),
    ),
)
def test_registered_random_rider_failures_build_isolated_school_streaks(
    school,
    passive,
):
    player = _player()
    target = TestGameState.create_player(class_name="Warrior")
    learned = passive()
    player.spellbook["Skills"][learned.name] = learned
    promotion_kits.begin_action(player, action="Cast Spell", choice=_spell(school).name)

    message = mage_mechanics.process_cast(
        player,
        _spell(school),
        target,
        rng=_FixedRng(0.99),
    )

    assert message == ""
    assert _streak(player) == {school: 1}


def test_four_failures_guarantee_and_consume_the_next_registered_rider():
    player = _player()
    target = TestGameState.create_player(class_name="Warrior")
    player.spellbook["Skills"]["Subzero"] = abilities.Subzero()
    spell = _spell("Ice")

    for index in range(4):
        promotion_kits.begin_action(
            player,
            action="Cast Spell",
            choice=spell.name,
        )
        message = mage_mechanics.process_cast(
            player,
            spell,
            target,
            rng=_FixedRng(0.99),
        )
        assert "frozen solid" not in message
        assert _streak(player)["Ice"] == index + 1

    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
    message = mage_mechanics.process_cast(
        player,
        spell,
        target,
        rng=_FixedRng(0.99),
    )

    assert "frozen solid" in message
    assert _streak(player)["Ice"] == 0


def test_school_streak_records_only_once_per_spell_action():
    player = _player()
    target = TestGameState.create_player(class_name="Warrior")
    player.spellbook["Skills"]["Subzero"] = abilities.Subzero()
    spell = _spell("Ice")
    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)

    mage_mechanics.process_cast(player, spell, target, rng=_FixedRng(0.99))
    mage_mechanics.process_cast(player, spell, target, rng=_FixedRng(0.99))

    assert _streak(player) == {"Ice": 1}


def test_each_failure_improves_the_next_registered_rider_roll():
    player = _player()
    target = TestGameState.create_player(class_name="Warrior")
    player.spellbook["Skills"]["Subzero"] = abilities.Subzero()
    spell = _spell("Ice")

    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
    first = mage_mechanics.process_cast(
        player,
        spell,
        target,
        rng=_FixedRng(0.35),
    )
    assert "frozen solid" not in first
    assert _streak(player)["Ice"] == 1

    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
    second = mage_mechanics.process_cast(
        player,
        spell,
        target,
        rng=_FixedRng(0.35),
    )
    assert "frozen solid" in second
    assert _streak(player)["Ice"] == 0


def test_wizard_cast_pipeline_records_registered_rider_failure(monkeypatch):
    player = _player()
    target = TestGameState.create_player(class_name="Warrior")
    player.spellbook["Skills"]["Subzero"] = abilities.Subzero()
    spell = _spell("Ice")
    monkeypatch.setattr(mage_mechanics.random, "random", lambda: 0.99)
    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)

    message = wizard.process_cast(player, spell, target)

    assert "frozen solid" not in message
    assert _streak(player) == {"Ice": 1}


def test_school_streak_requires_awakening_equipment_and_wizard_class():
    player = _player(awakened=False)
    target = TestGameState.create_player(class_name="Warrior")
    player.spellbook["Skills"]["Subzero"] = abilities.Subzero()
    spell = _spell("Ice")

    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
    mage_mechanics.process_cast(player, spell, target, rng=_FixedRng(0.99))
    assert _streak(player) == {}

    player.awaken_class_ring()
    player.equipment["Ring"] = SimpleNamespace(name="Ordinary Ring")
    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
    mage_mechanics.process_cast(player, spell, target, rng=_FixedRng(0.99))
    assert _streak(player) == {}

    player.equipment["Ring"] = items.ClassRing()
    player.cls = SimpleNamespace(name="Sorcerer")
    promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
    mage_mechanics.process_cast(player, spell, target, rng=_FixedRng(0.99))
    assert _streak(player) == {}


def test_deterministic_and_arcane_effects_do_not_use_school_streak():
    player = _player()
    target = TestGameState.create_player(class_name="Warrior")
    player.spellbook["Skills"]["Inferno"] = abilities.Inferno()

    for school in ("Fire", "Arcane"):
        spell = _spell(school)
        promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
        mage_mechanics.process_cast(
            player,
            spell,
            target,
            rng=_FixedRng(0.99),
        )

    assert _streak(player) == {}


def test_school_streak_persists_but_mastery_buffs_are_combat_only(monkeypatch):
    player = _player()
    target = TestGameState.create_player(class_name="Warrior")
    player.spellbook["Skills"]["Subzero"] = abilities.Subzero()
    spell = _spell("Ice")
    for _index in range(2):
        promotion_kits.begin_action(player, action="Cast Spell", choice=spell.name)
        mage_mechanics.process_cast(player, spell, target, rng=_FixedRng(0.99))

    player.wizard_affinity["Fire"] = 100
    monkeypatch.setattr(wizard.random, "random", lambda: 0.0)
    wizard.process_cast(player, _spell("Fire"), target)
    assert player.mage_enhancement_state["school_mastery_buffs"]["Fire"] == 1
    mage_mechanics.tick_combat_state(player)
    assert player.mage_enhancement_state["school_mastery_buffs"]["Fire"] == 1

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert _streak(restored)["Ice"] == 2
    assert not getattr(restored, "mage_enhancement_state", {})

    mage_mechanics.tick_combat_state(player, end=True)
    assert player.mage_enhancement_state == {}
    player.mage_enhancement_state["school_mastery_buffs"] = {"Fire": 3}
    mage_mechanics.start_combat(player)
    assert player.mage_enhancement_state == {}


def test_school_streak_player_copy_hides_formula_and_counter():
    player = _player()
    description = class_rings.class_voluntas_identity(player)["description"]

    assert "+15%" not in description
    assert "four stacks" not in description
    assert "increasingly reliable" in description
