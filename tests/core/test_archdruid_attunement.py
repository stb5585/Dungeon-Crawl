from types import SimpleNamespace

from src.core import enemies, items
from src.core.classes import archdruid
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _archdruid():
    player = TestGameState.create_player(
        class_name="Archdruid",
        race_name="Human",
        level=60,
        pro_level=3,
        stats={"strength": 12, "intel": 30, "wisdom": 30, "con": 20, "charisma": 14, "dex": 18},
    )
    player.gold = 10000
    return player


def _unlock_grove(player):
    for affinity in archdruid.AFFINITIES:
        archdruid.adjust_attunement(player, affinity, archdruid.ENTRY_THRESHOLD)
    return player.ensure_archdruid_attunement()


def test_archdruid_state_defaults_and_grove_unlock_threshold():
    player = _archdruid()

    state = player.ensure_archdruid_attunement()

    assert state["grove_unlocked"] is False
    assert state["ring_awakened"] is False
    assert state["attunement"] == {affinity: 0 for affinity in archdruid.AFFINITIES}

    for affinity in ("Venom", "Stone", "Growth"):
        archdruid.adjust_attunement(player, affinity, 50)
    assert archdruid.grove_unlocked(player) is False

    archdruid.adjust_attunement(player, "Storm", 50)
    assert archdruid.grove_unlocked(player) is True


def test_attunement_gain_loss_and_mastery_cap_until_aspect_ritual():
    player = _archdruid()

    player.record_archdruid_damage_dealt(250, "Electric")
    assert player.archdruid_attunement["attunement"]["Storm"] == 2

    player.record_archdruid_healing_done(220)
    assert player.archdruid_attunement["attunement"]["Growth"] == 2

    archdruid.adjust_attunement(player, "Venom", 150)
    assert player.archdruid_attunement["attunement"]["Venom"] == 99

    _unlock_grove(player)
    player.modify_inventory(items.SerpentVenomHeart(), rare=True)
    success, _message = archdruid.perform_ritual(player, "Venom")
    assert success is True

    archdruid.adjust_attunement(player, "Venom", 10)
    assert player.archdruid_attunement["attunement"]["Venom"] == 100
    assert archdruid.mastery_unlocked(player, "Venom") is True
    assert "Poison" in player.status_immunity


def test_catalyst_drops_only_for_archdruid_after_grove_unlock_and_only_once():
    player = _archdruid()
    enemy = enemies.StormMyrmidon()
    enemy.gold = 0
    enemy.inventory = {}
    tile = SimpleNamespace()

    assert player.loot(enemy, tile) == ""
    assert "Stormglass Feather" not in player.special_inventory

    _unlock_grove(player)
    message = player.loot(enemy, tile)

    assert "Stormglass Feather" in message
    assert "Stormglass Feather" in player.special_inventory
    assert player.archdruid_attunement["catalysts"]["Storm"] is True

    message = player.loot(enemy, tile)
    assert "Stormglass Feather" not in message
    assert len(player.special_inventory["Stormglass Feather"]) == 1


def test_ritual_failure_does_not_consume_catalyst_and_success_unlocks_aspect():
    player = _archdruid()
    _unlock_grove(player)

    success, message = archdruid.perform_ritual(player, "Stone")
    assert success is False
    assert "Heartstone Shard" in message

    player.modify_inventory(items.HeartstoneShard(), rare=True)
    success, message = archdruid.perform_ritual(player, "Stone")

    assert success is True
    assert "remain standing" in message
    assert player.archdruid_attunement["aspects"]["Stone"] is True
    assert "Heartstone Shard" not in player.special_inventory


def test_all_four_aspects_awaken_ring_only_when_ring_is_visible():
    player = _archdruid()
    _unlock_grove(player)
    player.inventory = {"Class Ring": [items.ClassRing()]}
    player.equipment["Ring"] = items.NoRing()

    for item_cls, affinity in (
        (items.SerpentVenomHeart, "Venom"),
        (items.HeartstoneShard, "Stone"),
        (items.VerdantSeed, "Growth"),
        (items.StormglassFeather, "Storm"),
    ):
        player.modify_inventory(item_cls(), rare=True)
        success, _message = archdruid.perform_ritual(player, affinity)
        assert success is True

    assert all(player.archdruid_attunement["aspects"].values())
    assert player.archdruid_attunement["ring_awakened"] is False

    player.storage = {"Class Ring": [items.ClassRing()]}
    success, message = archdruid.awaken_ring(player)

    assert success is True
    assert "fourfold harmony" in message
    assert player.archdruid_attunement["ring_awakened"] is True


def test_archdruid_class_ring_description_names_grove_progress_and_equipped_harmony():
    player = _archdruid()
    player.equipment["Ring"] = items.ClassRing()

    pre_grove_description = player.equipment["Ring"].get_description(player)
    assert "dormant Class Ring for an Archdruid" in pre_grove_description
    assert "Ring location: equipped" in pre_grove_description
    assert "Activation: Fourfold Balance and Ancient Grove rituals" in pre_grove_description
    assert "Attunement:" in pre_grove_description

    _unlock_grove(player)
    grove_description = player.equipment["Ring"].get_description(player)
    assert "Activation: complete all four Grove aspects" in grove_description
    assert "Aspects:" in grove_description
    assert "Active effect: inactive until awakened" in grove_description

    state = player.ensure_archdruid_attunement()
    state["ring_awakened"] = True
    state["aspects"] = {affinity: True for affinity in archdruid.AFFINITIES}
    state["attunement"] = {affinity: 75 for affinity in archdruid.AFFINITIES}
    player.archdruid_attunement = state
    player.equipment["Ring"] = items.NoRing()
    player.storage = {"Class Ring": [items.ClassRing()]}

    stored_description = player.storage["Class Ring"][0].get_description(player)
    assert "awakened Class Ring for an Archdruid" in stored_description
    assert "Ring location: stored" in stored_description
    assert "Current Harmony Bonus: +0%" in stored_description
    assert "Potential while equipped: +24%" in stored_description
    assert "Active effect: equip the ring to use it" in stored_description

    player.equipment["Ring"] = items.ClassRing()
    player.storage = {}
    equipped_description = player.equipment["Ring"].get_description(player)
    assert "Ring location: equipped" in equipped_description
    assert "Current Harmony Bonus: +24%" in equipped_description
    assert "Active effect: active while equipped" in equipped_description


def test_harmony_bonus_and_class_ring_description_and_mod():
    player = _archdruid()
    player.equipment["Ring"] = items.ClassRing()
    state = player.ensure_archdruid_attunement()
    state["ring_awakened"] = True
    state["aspects"] = {affinity: True for affinity in archdruid.AFFINITIES}
    state["attunement"] = {affinity: 75 for affinity in archdruid.AFFINITIES}
    player.archdruid_attunement = state

    assert archdruid.harmony_bonus(player) == 0.24

    player.equipment["Ring"].class_mod(player)
    assert player.equipment["Ring"].mod == "Harmony +24%"
    assert "Current Harmony Bonus: +24%" in player.equipment["Ring"].get_description(player)
    assert "Potential while equipped: +24%" in player.equipment["Ring"].get_description(player)


def test_archdruid_state_save_round_trip():
    player = _archdruid()
    _unlock_grove(player)
    player.equipment["Ring"] = items.ClassRing()
    for item_cls, affinity in (
        (items.SerpentVenomHeart, "Venom"),
        (items.HeartstoneShard, "Stone"),
        (items.VerdantSeed, "Growth"),
        (items.StormglassFeather, "Storm"),
    ):
        player.modify_inventory(item_cls(), rare=True)
        archdruid.perform_ritual(player, affinity)

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )

    assert restored.archdruid_attunement["grove_unlocked"] is True
    assert restored.archdruid_attunement["ring_awakened"] is True
    assert all(restored.archdruid_attunement["aspects"].values())
