"""Focused coverage for Paladin vows and Crusader affirmation."""

from types import SimpleNamespace

from src.core import abilities, items
from src.core.classes import paladin
from src.core.combat.battle_engine import BattleEngine
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _player(class_name="Paladin", **kwargs):
    return TestGameState.create_player(class_name=class_name, race_name="Human", **kwargs)


def _enemy(name="Bandit", hp=(40, 10), exp=25, gold=12):
    return SimpleNamespace(
        name=name,
        health=SimpleNamespace(max=hp[0], current=hp[1]),
        mana=SimpleNamespace(max=0, current=0),
        experience=exp,
        gold=gold,
        inventory={"Potion": [items.HealthPotion]},
        enemy_typ="Humanoid",
        effects=lambda end=False: "",
        is_alive=lambda: False,
    )


def test_vow_state_normalizes_legacy_values_and_grants_signature_skill():
    player = _player()

    assert paladin.normalize_state("redemption")["path"] == "Redemption"

    ok, message = player.choose_paladin_vow("Protection")

    assert ok is True
    assert "Interpose" in message
    assert player.paladin_vow["path"] == "Protection"
    assert "Interpose" in player.spellbook["Skills"]

    ok, message = player.choose_paladin_vow("Conquest")
    assert ok is False
    assert "already sworn" in message


def test_save_load_preserves_vow_state_and_skill():
    player = _player()
    player.choose_paladin_vow("Retribution")
    paladin.trigger_aura(player, "Retribution", doubled=True)

    data = PlayerDataSerializer.serialize(player)
    restored = PlayerDataSerializer.deserialize(data, skip_tiles=True)

    assert restored.paladin_vow["path"] == "Retribution"
    assert restored.paladin_vow["aura"]["encounters"] == 6
    assert "Judgment Riposte" in restored.spellbook["Skills"]


def test_redeem_success_is_mercy_victory_with_gold_and_no_kill_or_loot_credit():
    player = _player(gold=0)
    player.choose_paladin_vow("Redemption")
    enemy = _enemy()
    tile = SimpleNamespace(available_actions=lambda _player: ["Use Skill"])
    engine = BattleEngine(player, enemy, tile)
    engine.attacker = player
    engine.defender = enemy

    message = abilities.Redeem().use(player, enemy, rng=SimpleNamespace(random=lambda: 0.0))
    outcome = engine.end_battle()

    assert "yields to mercy" in message
    assert outcome.result == "victory"
    assert player.level.exp == 33
    assert player.gold == 14  # Human + Redemption Aura reward multiplier.
    assert player.kill_dict == {}
    assert "Potion" not in player.inventory


def test_vow_skills_update_state_for_challenge_interpose_and_riposte():
    conquest = _player()
    conquest.choose_paladin_vow("Conquest")
    foe = _enemy()
    assert "Challenged Foe" in abilities.Challenge().use(conquest, foe)
    assert paladin.challenge_matches(conquest, foe)
    paladin.apply_mark(conquest, "Conquest")
    paladin.on_enemy_defeated(conquest, foe, bounty_target=True)
    assert not paladin.mark_active(conquest, "Mark of the Craven")

    protection = _player()
    protection.choose_paladin_vow("Protection")
    assert "guarded stance" in abilities.Interpose().use(protection)
    assert protection.paladin_vow["interpose"]["turns"] == 2
    assert paladin.block_succeeded(protection)
    assert protection.paladin_vow["aura"]["name"] == "Protection Aura"

    retribution = _player()
    retribution.choose_paladin_vow("Retribution")
    assert "retaliatory judgment" in abilities.JudgmentRiposte().use(retribution)
    assert paladin.pending_riposte(retribution)
    target = _enemy(hp=(30, 30))
    result = paladin.resolve_riposte(retribution, target)
    assert "Judgment Riposte" in result
    assert not paladin.pending_riposte(retribution)


def test_crusader_affirmation_scales_aura_and_mark_values():
    player = _player(class_name="Crusader")
    ring = items.ClassRing()
    player.equipment["Ring"] = ring
    player.choose_paladin_vow("Conquest")

    paladin.trigger_aura(player, "Conquest")
    dormant = paladin.conquest_damage_multiplier(player)

    ok, message = player.awaken_class_ring("Crusader")
    ring.class_mod(player)
    affirmed = paladin.conquest_damage_multiplier(player)

    assert ok is True
    assert "Vow Trial" in message
    assert player.class_ring_awakening["data"]["Crusader"]["vow"] == "Conquest"
    assert ring.mod == "Vow Affirmation"
    assert affirmed > dormant

    paladin.apply_mark(player, "Conquest")
    assert paladin.conquest_damage_multiplier(player) > 0.90
