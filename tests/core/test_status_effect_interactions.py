"""Status interaction regressions for effect-driven abilities."""

from __future__ import annotations

from src.core.combat.combat_result import CombatResult
from src.core.effects import StatusApplyEffect
from tests.test_framework import TestGameState


def _combatant(name: str, *, intel: int = 30, wisdom: int = 10):
    return TestGameState.create_player(
        name=name,
        class_name="Wizard",
        race_name="Human",
        level=30,
        health=(300, 300),
        mana=(100, 100),
        stats={
            "strength": 10,
            "intel": intel,
            "wisdom": wisdom,
            "con": 10,
            "charisma": 10,
            "dex": 10,
        },
    )


def test_status_apply_stun_respects_post_stun_immunity(monkeypatch):
    actor = _combatant("Caster", intel=100)
    target = _combatant("Target", wisdom=1)
    actor.check_mod = lambda *_args, **_kwargs: 0
    target.check_mod = lambda *_args, **_kwargs: 0
    monkeypatch.setattr("random.randint", lambda _low, high: high)

    effect = StatusApplyEffect(status_name="Stun", duration=2)

    blocked = CombatResult(action="Shock", actor=actor, target=target)
    target.status_effects["Stun"].extra = 1
    effect.apply(actor, target, blocked)

    assert target.status_effects["Stun"].active is False
    assert blocked.effects_applied["Status"] == []
    assert blocked.extra["status_immune"] == "Stun"

    applied = CombatResult(action="Shock", actor=actor, target=target)
    target.status_effects["Stun"].extra = 0
    effect.apply(actor, target, applied)

    assert target.status_effects["Stun"].active is True
    assert target.status_effects["Stun"].duration == 2
    assert applied.effects_applied["Status"] == ["Stun"]


def test_damage_over_time_effects_resolve_before_regen(monkeypatch):
    character = _combatant("Patient", wisdom=10)
    character.health.max = 120
    character.health.current = 100
    character.combat.magic_def = 0

    character.status_effects["Poison"].active = True
    character.status_effects["Poison"].duration = 1
    character.status_effects["Poison"].extra = 10
    character.magic_effects["DOT"].active = True
    character.magic_effects["DOT"].duration = 1
    character.magic_effects["DOT"].extra = 6
    character.magic_effects["DOT"].source = "Burn"
    character.physical_effects["Bleed"].active = True
    character.physical_effects["Bleed"].duration = 1
    character.physical_effects["Bleed"].extra = 8
    character.magic_effects["Regen"].active = True
    character.magic_effects["Regen"].duration = 1
    character.magic_effects["Regen"].extra = 10

    monkeypatch.setattr("src.core.character.random.randint", lambda *_args: 0)

    text = character.effects()

    assert character.health.current == 83
    assert text.index("poison damages") < text.index("burns for")
    assert text.index("burns for") < text.index("bleeds for")
    assert text.index("bleeds for") < text.index("health has regenerated")
    assert character.status_effects["Poison"].active is False
    assert character.magic_effects["DOT"].active is False
    assert character.physical_effects["Bleed"].active is False
    assert character.magic_effects["Regen"].active is False


def test_timed_silence_expires_but_indefinite_silence_persists():
    character = _combatant("Mage", wisdom=10)
    character.status_effects["Silence"].active = True
    character.status_effects["Silence"].duration = 1

    text = character.effects()

    assert "Mage can speak again." in text
    assert character.status_effects["Silence"].active is False
    assert character.status_effects["Silence"].duration == 0

    character.status_effects["Silence"].active = True
    character.status_effects["Silence"].duration = -1

    text = character.effects()

    assert text == ""
    assert character.status_effects["Silence"].active is True
    assert character.status_effects["Silence"].duration == -1


def test_prone_recovery_waits_until_after_sleep_expires(monkeypatch):
    character = _combatant("Sleeper", wisdom=10)
    character.status_effects["Sleep"].active = True
    character.status_effects["Sleep"].duration = 1
    character.physical_effects["Prone"].active = True
    character.physical_effects["Prone"].duration = 1

    text = character.effects()

    assert "no longer asleep" in text
    assert "no longer prone" not in text
    assert character.status_effects["Sleep"].active is False
    assert character.physical_effects["Prone"].active is True
    assert character.physical_effects["Prone"].duration == 1

    monkeypatch.setattr("src.core.character.random.randint", lambda *_args: 0)

    text = character.effects()

    assert "Sleeper is no longer prone." in text
    assert character.physical_effects["Prone"].active is False
