"""Coverage for legacy Class Ring awakening state and mechanics."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import abilities, items
from src.core.combat.battle_engine import BattleEngine
from src.core.classes import class_rings, paladin
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _player_with_class_ring(class_name, **kwargs):
    player = TestGameState.create_player(class_name=class_name, race_name="Human", **kwargs)
    ring = items.ClassRing()
    player.equipment["Ring"] = ring
    return player, ring


def test_legacy_class_ring_defaults_to_dormant_description_and_mod():
    player, ring = _player_with_class_ring("Berserker")

    ring.class_mod(player)

    assert player.class_ring_awakening["awakened"]["Berserker"] is False
    assert player.equipment["Ring"].mod == "Dormant Bloodied Crits"
    assert "Activation: No Healing Duel" in ring.get_description(player)


def test_berserker_bloodied_crits_and_weapon_damage_require_awakening():
    player, ring = _player_with_class_ring("Berserker", health=(100, 20))
    ring.class_mod(player)
    dormant_crit = player.critical_chance("Weapon")
    dormant_weapon = player.check_mod("weapon")

    ok, _ = player.awaken_class_ring()
    ring.class_mod(player)

    assert ok is True
    assert player.critical_chance("Weapon") >= dormant_crit + 0.14
    assert player.check_mod("weapon") > dormant_weapon
    assert player.equipment["Ring"].mod == "Bloodied Crits"


def test_no_healing_duel_fails_when_player_restores_hp():
    player, _ring = _player_with_class_ring("Berserker", health=(100, 30))
    player.change_location(0, 0, 1)
    player.inventory = {"Health Potion": [items.HealthPotion()]}
    enemy = SimpleNamespace(
        name="Trial Champion",
        health=SimpleNamespace(current=50, max=50),
        mana=SimpleNamespace(current=0, max=1),
        effects=lambda end=False: "",
        is_alive=lambda: True,
        class_ring_trial_enemy=True,
        class_ring_trial_name="No Healing Duel",
        class_ring_no_healing_duel=True,
    )
    tile = SimpleNamespace(available_actions=lambda _player: ["Attack", "Use Item"])
    engine = BattleEngine(player, enemy, tile)
    engine.attacker = player
    engine.defender = enemy

    result = engine.execute_action("Use Item", "Health Potion")
    outcome = engine.end_battle()

    assert "rejects restored life" in result.message
    assert outcome.result == "defeat"
    assert player.health.current == 1
    assert player.in_town() is False


def test_dragoon_jump_mod_stays_dormant_until_guard_the_fall():
    player, ring = _player_with_class_ring("Dragoon")
    jump = abilities.Jump()

    ring.class_mod(player)
    dormant_max = jump.get_max_active_modifications(player)
    assert player.equipment["Ring"].mod == "Dormant Aerial Supremacy"

    ok, _ = player.awaken_class_ring()
    ring.class_mod(player)

    assert ok is True
    assert player.equipment["Ring"].mod == "Aerial Supremacy"
    assert jump.get_max_active_modifications(player) == dormant_max


def test_knight_enchanter_arcane_tempo_replaces_mana_tap_plus_display():
    player, ring = _player_with_class_ring("Knight Enchanter")

    ring.class_mod(player)
    assert player.equipment["Ring"].mod == "Dormant Arcane Tempo"

    ok, _ = player.awaken_class_ring()
    ring.class_mod(player)

    assert ok is True
    assert player.equipment["Ring"].mod == "Arcane Tempo"


def test_grand_summoner_conduit_ritual_sacrifices_hp_and_empowers_summons():
    player, ring = _player_with_class_ring("Grand Summoner", health=(200, 200))

    ok, _ = player.awaken_class_ring()
    ring.class_mod(player)

    assert ok is True
    assert player.health.max == 190
    assert player.health.current == 190
    assert player.equipment["Ring"].mod == "+30% Summons"
    assert class_rings.summon_multiplier(player) == 1.30


def test_crusader_activation_requires_and_affirms_paladin_vow():
    player, ring = _player_with_class_ring("Crusader")

    ok, message = player.awaken_class_ring()

    assert ok is False
    assert "requires a sworn Paladin vow" in message

    player.choose_paladin_vow("Redemption")
    paladin.trigger_aura(player, "Redemption")
    dormant_rate = paladin.encounter_rate_multiplier(player)

    ok, message = player.awaken_class_ring()
    ring.class_mod(player)

    assert ok is True
    assert "Vow Trial" in message
    assert ring.mod == "Vow Affirmation"
    assert player.class_ring_awakening["data"]["Crusader"]["vow"] == "Redemption"
    assert paladin.encounter_rate_multiplier(player) < dormant_rate


def test_archbishop_intervention_and_reset_combat_flags():
    player, _ring = _player_with_class_ring("Archbishop", health=(100, 40))
    player.awaken_class_ring()
    rng = SimpleNamespace(random=lambda: 0.0)

    healed = class_rings.divine_intervention(player, rng=rng)
    second = class_rings.divine_intervention(player, rng=rng)

    assert healed == 25
    assert second == 0
    class_rings.reset_combat_flags(player)
    player.health.current = 40
    assert class_rings.divine_intervention(player, rng=rng) == 25


def test_rogue_loaded_dice_and_seeker_hidden_cache():
    rogue, _ring = _player_with_class_ring("Rogue")
    rogue.awaken_class_ring()
    assert class_rings.loaded_dice_succeeds(rogue, rng=SimpleNamespace(random=lambda: 0.14))

    seeker, _ring = _player_with_class_ring("Seeker")
    seeker.awaken_class_ring()
    assert class_rings.hidden_cache_available(seeker, 3, reveal_progress=0.75)
    claimed, reward = class_rings.claim_hidden_cache(seeker, 3, reveal_progress=0.75)
    assert claimed is True
    assert reward == "Hidden Utility Cache"
    assert not class_rings.hidden_cache_available(seeker, 3, reveal_progress=1.0)


def test_master_monk_martial_master_and_arcane_trickster_buff():
    monk, _ring = _player_with_class_ring(
        "Master Monk",
        equipment={"Weapon": "No Weapon", "Armor": "No Armor"},
    )
    monk.awaken_class_ring()
    unawakened = TestGameState.create_player(
        class_name="Master Monk",
        race_name="Human",
        equipment={"Weapon": "No Weapon", "Armor": "No Armor"},
    )
    unawakened.equipment["Ring"] = items.NoRing()
    weapon_before = unawakened.check_mod("weapon")
    assert monk.check_mod("weapon") > weapon_before

    trickster, _ring = _player_with_class_ring("Arcane Trickster")
    trickster.awaken_class_ring()
    base_magic = trickster.check_mod("magic")
    class_rings.activate_spell_steal_buff(trickster)
    assert trickster.check_mod("magic") > base_magic


def test_legacy_class_ring_state_save_round_trip():
    player, _ring = _player_with_class_ring("Astromancer")
    player.awaken_class_ring()
    class_rings.advance_constellation(player)

    data = PlayerDataSerializer.serialize(player)
    restored = PlayerDataSerializer.deserialize(data, skip_tiles=True)

    assert restored.class_ring_awakening["awakened"]["Astromancer"] is True
    assert class_rings.active_constellation(restored) == "Tide"
