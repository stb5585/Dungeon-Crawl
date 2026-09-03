"""Focused coverage for full legacy class-kit completion helpers."""

from types import SimpleNamespace

from src.core import abilities, enemies, items
from src.core.character import Combat, Resource, Stats
from src.core.classes import bard, berserker, class_rings, lycan, spell_stealer, wizard
from src.core.companions import Summons
from src.core.save_system import ItemSerializer, PlayerDataSerializer
from tests.test_framework import TestGameState


class _Always:
    def random(self):
        return 0.0

    def choice(self, values):
        return values[0]


def test_berserker_battle_scars_roll_cap_and_bonus():
    player = TestGameState.create_player(class_name="Berserker", health=(1000, 100))

    gained, message = berserker.record_battle_scar(player, rng=_Always())

    assert gained is True
    assert "Battle Scar" in message
    assert berserker.scar_count(player) == 1
    assert player.health.max == 1010
    assert berserker.bloodied_weapon_bonus(player) == 0.005

    class_rings.ensure_state(player)["data"]["Berserker"]["battle_scars"] = 20
    gained, _message = berserker.record_battle_scar(player, rng=_Always())

    assert gained is False
    assert berserker.scar_count(player) == 20


def test_spell_steal_requires_blank_scroll_and_creates_inscribed_scroll():
    player = TestGameState.create_player(class_name="Spell Stealer", skills=["Steal Spell"])
    enemy = SimpleNamespace(
        name="Acolyte",
        spellbook={"Spells": {"Firebolt": abilities.Firebolt()}},
        class_ring_trial_enemy=False,
    )

    success, message = spell_stealer.steal_spell(player, enemy, rng=_Always())
    assert success is False
    assert "Blank Scroll" in message

    player.modify_inventory(items.BlankScroll())
    success, message = spell_stealer.steal_spell(player, enemy, rng=_Always())

    assert success is True
    assert "steals Firebolt" in message
    assert "Blank Scroll" not in player.inventory
    assert "Stolen Firebolt Scroll" in player.inventory
    scroll = player.inventory["Stolen Firebolt Scroll"][0]
    assert isinstance(scroll, items.InscribedSpellScroll)
    assert scroll.spell_class_name == "Firebolt"

    restored = ItemSerializer.deserialize(ItemSerializer.serialize(scroll))
    assert isinstance(restored, items.InscribedSpellScroll)
    assert restored.spell_class_name == "Firebolt"
    assert restored.spell.name == "Firebolt"


def test_spell_steal_trial_enemy_is_immune():
    player = TestGameState.create_player(class_name="Arcane Trickster")
    player.modify_inventory(items.BlankScroll())
    enemy = SimpleNamespace(
        name="Trial Shade",
        spellbook={"Spells": {"Shock": abilities.Shock()}},
        class_ring_trial_enemy=True,
    )

    success, message = spell_stealer.steal_spell(player, enemy, rng=_Always())

    assert success is False
    assert "no stealable spell" in message
    assert "Blank Scroll" in player.inventory


def test_spell_steal_allows_thieves_guild_arcane_trial_enemy():
    player = TestGameState.create_player(class_name="Arcane Trickster")
    player.modify_inventory(items.BlankScroll())
    enemy = enemies.GuildArcaneBoss()

    success, message = spell_stealer.steal_spell(player, enemy, rng=_Always())

    assert success is True
    assert "steals" in message
    assert "Blank Scroll" not in player.inventory
    assert any(name.startswith("Stolen ") for name in player.inventory)


def test_wizard_affinity_hex_opposites_and_save_load():
    player = TestGameState.create_player(class_name="Wizard")

    wizard.record_cast(player, "Water")
    wizard.record_cast(player, "Earth")

    assert player.wizard_affinity["Water"] == 1.8
    assert player.wizard_affinity["Electric"] == 0
    assert player.wizard_affinity["Earth"] == 2
    assert player.wizard_affinity["Wind"] == 0
    player.wizard_affinity["Water"] = 10
    assert wizard.affinity_damage_bonus(player, "Water") == 0.01

    restored = PlayerDataSerializer.deserialize(PlayerDataSerializer.serialize(player), skip_tiles=True)
    assert restored.wizard_affinity["Water"] == 10
    assert restored.wizard_affinity["Electric"] == 0


def test_sorcerer_affinity_caps_without_automatically_upgrading_spells():
    player = TestGameState.create_player(class_name="Sorcerer", spells=["Firebolt"])
    player.wizard_affinity["Fire"] = 49

    message = wizard.process_cast(player, abilities.Firebolt())

    assert player.wizard_affinity["Fire"] == 50
    assert "Firebolt" in player.spellbook["Spells"]
    assert "Fireball" not in player.spellbook["Spells"]
    assert "upgrades to Fireball" not in message


def test_wizard_ring_accelerates_affinity_without_auto_upgrading_spells(monkeypatch):
    player = TestGameState.create_player(class_name="Wizard", spells=["Fireball"])
    player.equipment["Ring"] = items.ClassRing()
    ok, _message = player.awaken_class_ring()
    assert ok is True
    player.wizard_affinity["Fire"] = 78
    monkeypatch.setattr(wizard.random, "random", lambda: 1.0)

    message = wizard.process_cast(player, abilities.Fireball())

    assert player.wizard_affinity["Fire"] == 81
    assert "Fireball" in player.spellbook["Spells"]
    assert "Firestorm" not in player.spellbook["Spells"]
    assert "upgrades to Firestorm" not in message


def test_legacy_affinity_values_migrate_from_centered_model():
    player = TestGameState.create_player(class_name="Wizard")
    player.wizard_affinity = {"Fire": 55, "Ice": 45, "Water": 50, "Electric": 50, "Earth": 60, "Wind": 40}
    player.wizard_affinity_version = 1

    migrated = wizard.ensure_affinity(player)

    assert migrated["Fire"] == 5
    assert migrated["Ice"] == 0
    assert migrated["Earth"] == 10
    assert player.wizard_affinity_version == 2


def test_wizard_mastery_ring_proc_adds_stacking_school_buff(monkeypatch):
    player = TestGameState.create_player(class_name="Wizard", spells=["Shock"])
    enemy = SimpleNamespace(name="Target", health=Resource(100, 100))
    player.equipment["Ring"] = items.ClassRing()
    ok, _message = player.awaken_class_ring()
    assert ok is True
    player.wizard_affinity["Electric"] = 100
    monkeypatch.setattr(wizard.random, "random", lambda: 0.0)

    message = wizard.process_cast(player, abilities.Shock(), enemy)

    assert "electric affinity arcs" in message
    assert player.wizard_school_buffs["Electric"] == 1
    assert enemy.health.current < 100


def test_frozen_armor_is_a_mage_enhancement_proc(monkeypatch):
    player = TestGameState.create_player(class_name="Sorcerer")
    player.spellbook["Skills"]["Frozen Armor"] = abilities.FrozenArmor()
    monkeypatch.setattr("src.core.classes.mage_mechanics.random.random", lambda: 0.0)

    message = wizard.process_cast(player, abilities.IceLance())

    assert "Frozen Armor protects" in message
    assert player.mage_enhancement_state["frozen_armor"] == 1
    assert player.stat_effects["Defense"].extra == 10


def test_bard_songs_require_instrument_and_tick_renewal():
    player = TestGameState.create_player(class_name="Bard", health=(100, 50), mana=(80, 40))
    player.equipment["OffHand"] = items.NoOffHand()

    success, message = bard.start_song(player, "Valor")
    assert success is False
    assert "instrument" in message

    player.equipment["OffHand"] = items.Lute()
    success, message = bard.start_song(player, "Renewal")

    assert success is True
    assert "Song of Renewal" in message
    assert bard.active_song(player) == "Renewal"
    tick = bard.tick_song(player)
    assert "restores" in tick
    assert player.health.current > 50
    assert player.mana.current > 40


def test_lycan_moon_cycle_and_frenzy_state_persist():
    player = TestGameState.create_player(class_name="Lycan")

    lycan.record_steps(player, 120)
    assert player.lycan_state["moon_phase"] == "Waxing"
    lycan.record_steps(player, 240)
    assert player.lycan_state["moon_phase"] == "Waning"

    player.progression.purchased_node_ids.add("lycan.ability.transform3")
    player.transform()
    triggered, message = lycan.maybe_trigger_frenzy(player, reason="kill", rng=_Always())
    assert triggered is True
    assert "frenzy" in message
    assert player.lycan_state["frenzy_turns"] > 0

    restored = PlayerDataSerializer.deserialize(PlayerDataSerializer.serialize(player), skip_tiles=True)
    assert restored.lycan_state["moon_phase"] == "Waning"
    assert restored.cls.name == "Werewolf"


def test_thaumaturgist_awakened_ring_scales_future_xenids():
    player = TestGameState.create_player(class_name="Thaumaturgist")
    player.equipment["Ring"] = items.ClassRing()
    ok, _message = player.awaken_class_ring()
    assert ok is True

    summon = Summons(
        "Spirit",
        Resource(100, 100),
        Resource(20, 20),
        Stats(10, 10, 10, 10, 10, 10),
        Combat(attack=20, defense=5, magic=30, magic_def=5),
    )
    summon.start_stats = [100, 20, 10, 10, 10, 10, 10, 10]
    summon.start_combat = [20, 5, 30, 5]
    summon.initialize_stats(player)

    assert summon.health.max > 100
    assert summon.combat.attack > 20
    assert summon.combat.magic > 30
