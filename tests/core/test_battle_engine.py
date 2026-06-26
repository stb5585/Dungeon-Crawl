#!/usr/bin/env python3
"""Focused regression coverage for the UI-agnostic battle engine."""

from __future__ import annotations

from src.core.combat.battle_engine import BattleEngine
from src.core.data.data_driven_abilities import DataDrivenSpell
from src.core.enemies import Goblin
from tests.test_framework import TestGameState


class DummyCombatTile:
    def available_actions(self, _player):
        return ["Attack"]


def _make_engine_with_player_attacking():
    player = TestGameState.create_player(name="TestHero", class_name="Warrior", race_name="Human")
    enemy = Goblin()
    engine = BattleEngine(player, enemy, DummyCombatTile())
    engine.attacker = player
    engine.defender = enemy
    return engine, player


class FakeJumpSkill:
    name = "Jump"
    cost = 0

    def __init__(self, *, unstoppable: bool = False):
        self.charging = True
        self.modifications = {"Unstoppable": unstoppable}
        self.use_calls = 0

    def get_charge_time(self):
        return 1

    def use(self, _user, target=None):
        self.use_calls += 1
        self.charging = False
        return f"Jump hits {target.name}.\n"

    def cancel_charge(self, _user):
        self.charging = False
        return "Jump was cancelled.\n"


class FakeChargingJumpSkill(FakeJumpSkill):
    def __init__(self):
        super().__init__()
        self.charging = False

    def use(self, _user, target=None):
        self.use_calls += 1
        self.charging = True
        return "TestHero is coiling their legs, preparing to leap into the air!\n"


class FakeContinuingJumpSkill(FakeJumpSkill):
    def __init__(self):
        super().__init__()
        self.charge_turns = 2

    def get_charge_time(self):
        return 2

    def use(self, _user, target=None):
        self.use_calls += 1
        self.charge_turns -= 1
        return "TestHero continues to gather power... (1 turn remaining)\n"


def test_pre_turn_duration_one_stun_still_skips_current_turn():
    engine, player = _make_engine_with_player_attacking()
    player.status_effects["Stun"].active = True
    player.status_effects["Stun"].duration = 1

    result = engine.pre_turn()

    assert result.can_act is False
    assert result.inactive_reason == ""
    assert "no longer stunned" in result.effects_text
    assert player.status_effects["Stun"].active is False


def test_pre_turn_duration_one_sleep_still_skips_current_turn():
    engine, player = _make_engine_with_player_attacking()
    player.status_effects["Sleep"].active = True
    player.status_effects["Sleep"].duration = 1

    result = engine.pre_turn()

    assert result.can_act is False
    assert result.inactive_reason == ""
    assert "no longer asleep" in result.effects_text
    assert player.status_effects["Sleep"].active is False


def test_pre_turn_prone_recovery_still_skips_current_turn(monkeypatch):
    engine, player = _make_engine_with_player_attacking()
    player.physical_effects["Prone"].active = True
    player.physical_effects["Prone"].duration = 1
    monkeypatch.setattr("src.core.character.random.randint", lambda *_args: 0)

    result = engine.pre_turn()

    assert result.can_act is False
    assert result.inactive_reason == ""
    assert "no longer prone" in result.effects_text
    assert player.physical_effects["Prone"].active is False


def test_pre_turn_stun_cancels_pending_jump():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeJumpSkill()
    player.spellbook["Skills"] = {"Jump": jump}
    player.class_effects["Jump"].active = True
    player.status_effects["Stun"].active = True
    player.status_effects["Stun"].duration = 2

    result = engine.pre_turn()

    assert result.can_act is False
    assert "Jump" in result.effects_text
    assert jump.charging is False
    assert player.class_effects["Jump"].active is False
    assert "stunned" in result.inactive_reason


def test_start_battle_clears_stale_saved_jump_charge():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeContinuingJumpSkill()
    player.spellbook["Skills"] = {"Jump": jump}
    player.class_effects["Jump"].active = True

    engine.start_battle()

    assert jump.charging is False
    assert jump.charge_turns == 0
    assert player.class_effects["Jump"].active is False


def test_start_battle_records_bestiary_encounter():
    engine, player = _make_engine_with_player_attacking()

    engine.start_battle()

    record = player.bestiary["Goblin"]
    assert record["name"] == "Goblin"
    assert record["type"] == "Humanoid"
    assert record["seen_count"] == 1
    assert record["details_unlocked"] is False
    assert "resistances" not in record


def test_boss_battle_blocks_enemy_detail_vision():
    engine, player = _make_engine_with_player_attacking()
    player.cls.name = "Seeker"
    engine.boss = True

    assert engine.player_has_sight() is True
    assert engine.show_enemy_details() is False


def test_initial_jump_charge_omits_generic_uses_line():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeChargingJumpSkill()
    player.spellbook["Skills"] = {"Jump": jump}

    result = engine.execute_action("Use Skill", "Jump")

    assert "uses Jump" not in result.message
    assert "coiling their legs" in result.message
    assert jump.charging is True


def test_continuing_jump_charge_omits_generic_uses_line():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeContinuingJumpSkill()
    player.spellbook["Skills"] = {"Jump": jump}
    player.class_effects["Jump"].active = True

    result = engine.execute_action("Use Skill", "Jump")

    assert "uses Jump" not in result.message
    assert "continues to gather power" in result.message
    assert jump.charging is True


def test_charging_skill_forced_action_takes_priority_over_berserk():
    engine, player = _make_engine_with_player_attacking()
    charge = FakeJumpSkill()
    charge.name = "Dragon Breath (Fire)"
    player.spellbook["Skills"] = {"Dragon Breath (Fire)": charge}
    player.status_effects["Berserk"].active = True

    forced = engine.get_forced_action()

    assert forced is not None
    assert forced.action == "Use Skill"
    assert forced.choice == "Dragon Breath (Fire)"


def test_resolved_jump_clears_forced_action_and_returns_control():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeJumpSkill()
    player.spellbook["Skills"] = {"Jump": jump}
    player.class_effects["Jump"].active = True

    forced = engine.get_forced_action()
    assert forced is not None
    assert forced.action == "Use Skill"
    assert forced.choice == "Jump"

    result = engine.execute_action(forced.action, forced.choice)

    assert "Jump hits" in result.message
    assert jump.use_calls == 1
    assert jump.charging is False
    assert player.class_effects["Jump"].active is False
    assert engine.get_forced_action() is None


def test_unstoppable_jump_resolves_before_berserk_forced_attack():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeJumpSkill(unstoppable=True)
    player.spellbook["Skills"] = {"Jump": jump}
    player.class_effects["Jump"].active = True
    player.status_effects["Berserk"].active = True
    player.status_effects["Berserk"].duration = 2

    forced = engine.get_forced_action()

    assert forced is not None
    assert forced.action == "Use Skill"
    assert forced.choice == "Jump"


def test_execute_spell_accepts_data_driven_spell_with_engine_context():
    engine, player = _make_engine_with_player_attacking()
    spell = DataDrivenSpell(
        name="Test Flame",
        description="A regression spell.",
        cost=0,
        dmg_mod=1,
        crit=999,
        subtyp="Fire",
    )
    player.spellbook["Spells"] = {"Test Flame": spell}

    result = engine.execute_action("Cast Spell", "Test Flame")

    assert "TestHero casts Test Flame" in result.message
