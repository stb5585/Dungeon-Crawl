#!/usr/bin/env python3
"""Focused regression coverage for the UI-agnostic battle engine."""

from __future__ import annotations

from types import SimpleNamespace

from src.core import abilities, items
from src.core.classes import class_rings, promotion_kits
from src.core.combat.battle_engine import BattleEngine, STOLEN_SCROLL_CHOICE_PREFIX
from src.core.data.data_driven_abilities import DataDrivenSpell
from src.core.enemies import Barghest, Goblin, GuildArcaneBoss
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


def test_resolve_skill_ignores_silence_and_spends_resolve():
    engine, player = _make_engine_with_player_attacking()
    player.cls = SimpleNamespace(name="Sentinel")
    player.equipment["OffHand"] = SimpleNamespace(subtyp="Shield")
    player.spellbook["Skills"]["Shield Check"] = abilities.ShieldBash()
    class_rings.ensure_state(player)["data"]["Stalwart Defender"]["guard_meter"] = 10
    player.abilities_suppressed = lambda: True

    result = engine.execute_action("Use Skill", "Shield Check")

    assert "cannot use skills because of silence" not in result.message
    assert "uses Shield Check" in result.message
    assert "spends 10 Resolve on Shield Check" in result.message
    assert promotion_kits.current_resolve(player) == 0


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


def test_shapeshifted_barghest_victory_credits_original_enemy(monkeypatch):
    player = TestGameState.create_player(name="Kongol", class_name="Warrior", race_name="Half Giant")
    enemy = Barghest()
    engine = BattleEngine(player, enemy, DummyCombatTile())
    player.quest_dict = {
        "Bounty": {},
        "Main": {
            "Cry Havoc!": {
                "Type": "Defeat",
                "What": "Barghest",
                "Total": 1,
                "Completed": False,
            }
        },
        "Side": {},
    }
    monkeypatch.setattr(player, "loot", lambda defeated_enemy, _tile: f"{defeated_enemy.name} dropped loot.\n")

    engine.start_battle()
    enemy.name = "Direwolf"
    enemy.enemy_typ = "Animal"

    msg = engine._process_victory()

    assert player.bestiary["Barghest"]["seen_count"] == 1
    assert player.kill_dict["Fiend"]["Barghest"] == 1
    assert "Direwolf" not in player.kill_dict.get("Animal", {})
    assert player.quest_dict["Main"]["Cry Havoc!"]["Completed"] is True
    assert "Barghest dropped loot" in msg


def test_thieves_guild_trial_victory_uses_guild_wording_and_awards_signet():
    player = TestGameState.create_player(name="Shade", class_name="Spell Stealer", race_name="Human")
    enemy = GuildArcaneBoss()
    engine = BattleEngine(player, enemy, DummyCombatTile())

    outcome = engine.end_battle()

    assert outcome.result == "victory"
    assert "Class Ring" not in outcome.message
    assert "Spell-Sealed Cutpurse" in outcome.message
    assert "Thieves Guild Signet" in outcome.message
    assert "Thieves Guild Signet" in player.special_inventory


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


def test_execute_spell_accepts_stolen_scroll_choice_token():
    player = TestGameState.create_player(name="TestHero", class_name="Spell Stealer", race_name="Human")
    enemy = Goblin()
    engine = BattleEngine(player, enemy, DummyCombatTile())
    engine.attacker = player
    engine.defender = enemy
    scroll = items.InscribedSpellScroll("Firebolt", charges=2)
    player.inventory[scroll.name] = [scroll]

    result = engine.execute_action("Cast Spell", f"{STOLEN_SCROLL_CHOICE_PREFIX}{scroll.name}")

    assert f"TestHero uses {scroll.name}" in result.message
    assert "Stolen Charge" in result.message
    assert scroll.charges == 1


def test_execute_spell_consumes_stolen_scroll_when_charges_run_out():
    player = TestGameState.create_player(name="TestHero", class_name="Spell Stealer", race_name="Human")
    enemy = Goblin()
    engine = BattleEngine(player, enemy, DummyCombatTile())
    engine.attacker = player
    engine.defender = enemy
    scroll = items.InscribedSpellScroll("Firebolt", charges=1)
    player.inventory[scroll.name] = [scroll]

    result = engine.execute_action("Cast Spell", f"{STOLEN_SCROLL_CHOICE_PREFIX}{scroll.name}")

    assert "crumbles to dust" in result.message
    assert scroll.name not in player.inventory


def test_execute_spell_rejects_non_stolen_scroll_choice_token():
    engine, player = _make_engine_with_player_attacking()
    player.inventory["Potion"] = [SimpleNamespace(name="Potion")]

    result = engine.execute_action("Cast Spell", f"{STOLEN_SCROLL_CHOICE_PREFIX}Potion")

    assert result.message == "Potion is not a stolen spell scroll.\n"


def test_execute_spell_still_casts_learned_spell_with_matching_scroll_inventory():
    engine, player = _make_engine_with_player_attacking()
    spell = abilities.Firebolt()
    player.spellbook["Spells"] = {"Firebolt": spell}
    player.inventory["Stolen Firebolt Scroll"] = [items.InscribedSpellScroll("Firebolt", charges=2)]

    result = engine.execute_action("Cast Spell", "Firebolt")

    assert "TestHero casts Firebolt" in result.message
    assert player.inventory["Stolen Firebolt Scroll"][0].charges == 2


def test_smoke_screen_requires_and_consumes_smoke_bomb():
    engine, player = _make_engine_with_player_attacking()
    player.spellbook["Skills"] = {"Smoke Screen": abilities.SmokeScreen()}
    player.flee = lambda _enemy, smoke=False: (True, "TestHero vanishes into smoke.\n")

    missing_result = engine.execute_action("Use Skill", "Smoke Screen")

    assert missing_result.message == "Smoke Screen requires a Smoke Bomb.\n"
    assert missing_result.fled is False

    player.inventory["Smoke Bomb"] = [items.SmokeBomb()]
    result = engine.execute_action("Use Skill", "Smoke Screen")

    assert "TestHero uses Smoke Screen." in result.message
    assert "A Smoke Bomb bursts open." in result.message
    assert "TestHero vanishes into smoke." in result.message
    assert "Smoke Bomb" not in player.inventory
    assert result.fled is True
