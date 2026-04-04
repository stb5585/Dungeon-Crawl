import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))


def test_half_orc_reduces_weapon_crit_damage_taken(monkeypatch):
    from tests.test_framework import TestGameState

    attacker = TestGameState.create_player(class_name="Warrior", race_name="Human", level=30, health=(999, 999))
    # Keep defenders identical except for race.
    human_def = TestGameState.create_player(class_name="Warrior", race_name="Human", level=30, health=(500, 500))
    orc_def = TestGameState.create_player(class_name="Warrior", race_name="Half Orc", level=30, health=(500, 500))

    # Make the swing deterministic and non-dodge.
    monkeypatch.setattr(human_def, "dodge_chance", lambda *a, **k: 0.0)
    monkeypatch.setattr(orc_def, "dodge_chance", lambda *a, **k: 0.0)
    monkeypatch.setattr(attacker, "hit_chance", lambda *a, **k: 1.0)
    monkeypatch.setattr(random, "random", lambda: 0.9999)  # no Blind Rage proc side effect
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)  # no variance

    # Force a crit via the crit param.
    attacker.weapon_damage(human_def, crit=2)
    attacker.weapon_damage(orc_def, crit=2)

    human_taken = 500 - human_def.health.current
    orc_taken = 500 - orc_def.health.current
    assert orc_taken < human_taken


def test_half_orc_blind_rage_procs_on_damage(monkeypatch):
    from tests.test_framework import TestGameState

    attacker = TestGameState.create_player(class_name="Warrior", race_name="Human", level=30, health=(999, 999))
    defender = TestGameState.create_player(class_name="Warrior", race_name="Half Orc", level=30, health=(500, 500))

    monkeypatch.setattr(defender, "dodge_chance", lambda *a, **k: 0.0)
    monkeypatch.setattr(attacker, "hit_chance", lambda *a, **k: 1.0)
    monkeypatch.setattr(attacker, "critical_chance", lambda *a, **k: 0.0)
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)
    monkeypatch.setattr(random, "random", lambda: 0.0)  # always proc when checked

    assert defender.status_effects["Blind Rage"].active is False
    attacker.weapon_damage(defender, crit=1)
    assert defender.status_effects["Blind Rage"].active is True
    assert defender.status_effects["Blind Rage"].duration > 0
