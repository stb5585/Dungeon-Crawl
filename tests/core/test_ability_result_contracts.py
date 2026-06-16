"""Focused ability result-shape contracts for P3 effects integration."""

from __future__ import annotations

from src.core import abilities
from src.core.combat.combat_result import CombatResult
from tests.test_framework import TestGameState


EXPECTED_EFFECT_BUCKETS = {"Status", "Physical", "Stat", "Magic", "Class"}


def _player(name: str = "Caster"):
    return TestGameState.create_player(
        name=name,
        class_name="Wizard",
        race_name="Human",
        level=30,
        health=(300, 300),
        mana=(200, 200),
        stats={
            "strength": 18,
            "intel": 30,
            "wisdom": 20,
            "con": 18,
            "charisma": 12,
            "dex": 18,
        },
    )


def _target(name: str = "Target"):
    return TestGameState.create_player(
        name=name,
        class_name="Warrior",
        race_name="Human",
        level=30,
        health=(500, 500),
        mana=(50, 50),
        stats={
            "strength": 18,
            "intel": 8,
            "wisdom": 10,
            "con": 0,
            "charisma": 10,
            "dex": 10,
        },
    )


def _assert_result_contract(result: CombatResult, *, action: str, actor, target) -> None:
    assert isinstance(result, CombatResult)
    assert result.action == action
    assert result.actor is actor
    assert result.target is target
    assert isinstance(result.message, str)
    assert str(result) == result.message
    assert EXPECTED_EFFECT_BUCKETS <= set(result.effects_applied)
    assert isinstance(result.extra, dict)
    assert isinstance(result.damage, int)
    assert isinstance(result.healing, int)


def test_data_driven_damage_spell_returns_stable_combat_result(monkeypatch):
    caster = _player()
    target = _target()
    spell = abilities.Fireball()

    monkeypatch.setattr(
        "src.core.data.data_driven_abilities.random.randint",
        lambda _low, high: high,
    )
    monkeypatch.setattr(
        "src.core.data.data_driven_abilities.random.uniform",
        lambda _low, _high: 1.0,
    )
    caster.check_mod = lambda *_args, **_kwargs: 30
    caster.hit_chance = lambda *_args, **_kwargs: 1.0
    target.dodge_chance = lambda *_args, **_kwargs: 0.0
    target.handle_defenses = lambda _caster, damage, *_args, **_kwargs: (
        True,
        "",
        damage,
    )
    target.damage_reduction = lambda damage, *_args, **_kwargs: (True, "", damage)

    result = spell.cast(caster, target)

    _assert_result_contract(result, action="Fireball", actor=caster, target=target)
    assert result.hit is True
    assert result.damage == 60
    assert target.health.current == 440
    assert "damages Target for 60 hit points" in result.message


def test_data_driven_damage_spell_reflect_updates_result_target(monkeypatch):
    caster = _player()
    target = _target()
    spell = abilities.Fireball()
    target.magic_effects["Reflect"].active = True

    monkeypatch.setattr(
        "src.core.data.data_driven_abilities.random.randint",
        lambda _low, high: high,
    )
    monkeypatch.setattr(
        "src.core.data.data_driven_abilities.random.uniform",
        lambda _low, _high: 1.0,
    )
    caster.check_mod = lambda *_args, **_kwargs: 30
    caster.hit_chance = lambda *_args, **_kwargs: 1.0
    target.dodge_chance = lambda *_args, **_kwargs: 0.0
    caster.handle_defenses = lambda _caster, damage, *_args, **_kwargs: (
        True,
        "",
        damage,
    )
    caster.damage_reduction = lambda damage, *_args, **_kwargs: (True, "", damage)

    result = spell.cast(caster, target)

    _assert_result_contract(result, action="Fireball", actor=caster, target=caster)
    assert result.hit is True
    assert result.damage == 60
    assert caster.health.current == 240
    assert target.health.current == 500
    assert result.extra["reflected_by"] == "Target"
    assert "Fireball is reflected back at Caster!" in result.message


def test_weapon_data_driven_skill_records_weapon_damage_in_result():
    user = _player("Warrior")
    target = _target()
    skill = abilities.DoubleStrike()
    calls = []

    def weapon_damage(_target, **_kwargs):
        calls.append(_kwargs)
        _target.health.current -= 7
        return "Warrior hits Target for 7 hit points.\n", True, 1

    user.weapon_damage = weapon_damage

    result = skill.use(user, target)

    _assert_result_contract(
        result, action="Double Strike", actor=user, target=target
    )
    assert result.hit is True
    assert result.damage == 14
    assert result.extra["last_damage"] == 14
    assert target.health.current == 486
    assert len(calls) == 2


def test_legacy_base_spell_cast_resets_reusable_combat_result():
    caster = _player()
    target = _target()
    spell = abilities.Spell("Legacy Probe", "A minimal legacy spell.")
    spell.result.message = "stale text"
    spell.result.hit = True
    spell.result.damage = 99
    spell.result.healing = 7
    spell.result.effects_applied["Status"].append("Poison")
    spell.result.extra["stale"] = True

    result = spell.cast(caster, target)

    _assert_result_contract(result, action="Legacy Probe", actor=caster, target=target)
    assert result.hit is None
    assert result.damage == 0
    assert result.healing == 0
    assert result.message == ""
    assert result.effects_applied == {
        "Status": [],
        "Physical": [],
        "Stat": [],
        "Magic": [],
        "Class": [],
    }
    assert result.extra == {"cost": 0, "type": "Spell", "subtype": ""}


def test_legacy_base_skill_use_resets_reusable_combat_result():
    user = _player("User")
    target = _target()
    skill = abilities.Skill("Legacy Feint", "A minimal legacy skill.")
    skill.result.message = "old move"
    skill.result.hit = False
    skill.result.damage = 42
    skill.result.healing = 3
    skill.result.effects_applied["Physical"].append("Prone")
    skill.result.extra["old"] = "value"

    result = skill.use(user, target)

    _assert_result_contract(result, action="Legacy Feint", actor=user, target=target)
    assert result.hit is None
    assert result.damage == 0
    assert result.healing == 0
    assert result.message == ""
    assert result.effects_applied == {
        "Status": [],
        "Physical": [],
        "Stat": [],
        "Magic": [],
        "Class": [],
    }
    assert result.extra == {"cost": 0, "type": "Skill", "subtype": ""}
