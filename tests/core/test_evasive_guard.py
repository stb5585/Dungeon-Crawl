import random


def test_evasive_guard_builds_stacks_on_hit_and_resets_on_dodge(monkeypatch):
    from src.core import abilities
    from tests.test_framework import TestGameState

    attacker = TestGameState.create_player(class_name="Warrior", level=30)
    defender = TestGameState.create_player(class_name="Footpad", level=30)

    # Ensure the passive exists regardless of class level wiring.
    defender.spellbook["Skills"]["Evasive Guard"] = abilities.EvasiveGuard()

    # Force deterministic, non-dodge hits.
    monkeypatch.setattr(defender, "dodge_chance", lambda *a, **k: 0.0)
    monkeypatch.setattr(attacker, "hit_chance", lambda *a, **k: 1.0)
    monkeypatch.setattr(random, "random", lambda: 0.0)  # hit + no crit randomness
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)  # no damage variance

    assert defender.evasive_guard_stacks == 0
    attacker.weapon_damage(defender)
    assert defender.evasive_guard_stacks == 1
    attacker.weapon_damage(defender)
    assert defender.evasive_guard_stacks == 2
    attacker.weapon_damage(defender)
    attacker.weapon_damage(defender)
    assert defender.evasive_guard_stacks == 3  # capped

    # Now force a dodge; stacks should decay by 1.
    monkeypatch.setattr(defender, "dodge_chance", lambda *a, **k: 1.0)
    attacker.weapon_damage(defender)
    assert defender.evasive_guard_stacks == 2
