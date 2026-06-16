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
