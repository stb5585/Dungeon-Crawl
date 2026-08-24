"""Runtime regressions for bespoke Mage mechanics."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies
from src.core.abilities.descriptions import (
    ability_modifications,
    composed_description,
    presented_abilities,
)
from src.core.character import Resource
from src.core.classes import mage_mechanics, wizard
from src.core.progression import ProgressionState
from tests.test_framework import TestGameState


class FixedRng:
    """Deterministic helper for Enhancement and companion tests."""

    @staticmethod
    def random():
        return 0.0

    @staticmethod
    def choice(values):
        return values[0]

    @staticmethod
    def uniform(low, high):
        del high
        return low


def _player(class_name="Mage"):
    player = TestGameState.create_player(
        class_name=class_name,
        level=30,
        health=(200, 100),
        mana=(160, 80),
    )
    player.progression = ProgressionState(level=30)
    return player


def test_specialization_reduces_only_the_competing_school_by_twenty_five_percent():
    elemental = _player()
    elemental.spellbook["Skills"]["Classical Force"] = abilities.ClassicalForce()
    arcane = _player()
    arcane.spellbook["Skills"]["Arcane Tradition"] = abilities.ArcaneTradition()

    assert mage_mechanics.spell_potency_multiplier(
        elemental, abilities.MagicMissile()
    ) == 0.75
    assert mage_mechanics.spell_potency_multiplier(
        elemental, abilities.Firebolt()
    ) == 1.0
    assert mage_mechanics.spell_potency_multiplier(
        arcane, abilities.Firebolt()
    ) == 0.75
    assert mage_mechanics.spell_potency_multiplier(
        arcane, abilities.MagicMissile()
    ) == 1.0

    elemental.spellbook["Skills"]["Classical Enrichment"] = (
        abilities.ClassicalEnrichment()
    )
    arcane.spellbook["Skills"]["Arcane Ritual"] = abilities.ArcaneRitual()

    assert mage_mechanics.spell_potency_multiplier(
        elemental, abilities.MagicMissile()
    ) == 0.50
    assert mage_mechanics.spell_potency_multiplier(
        arcane, abilities.Firebolt()
    ) == 0.50


def test_targeted_passives_are_embedded_in_affected_spell_descriptions():
    player = _player()
    player.spellbook["Spells"]["Magic Missile"] = abilities.MagicMissile()
    player.spellbook["Spells"]["Mirror Image"] = abilities.MirrorImage()
    player.spellbook["Skills"]["Classical Force"] = abilities.ClassicalForce()
    player.spellbook["Skills"]["Illusory Link"] = abilities.IllusoryLink()

    presented_spells = presented_abilities(player, "Spells")
    presented_skills = presented_abilities(player, "Skills")
    by_name = {spell.name: spell for spell in presented_spells}

    assert [modifier.name for modifier in by_name["Magic Missile"].presentation_modifications] == [
        "Classical Force"
    ]
    assert [modifier.name for modifier in by_name["Mirror Image"].presentation_modifications] == [
        "Illusory Link"
    ]
    assert presented_skills == []


def test_arcane_fundamentals_boosts_critical_bonus_by_twenty_percent_only():
    player = _player()
    player.progression.purchased_node_ids.add(
        "mage.talent.arcane-fundamentals"
    )
    magic_before = player.combat.magic

    assert mage_mechanics.arcane_critical_multiplier(
        player,
        2.0,
        abilities.MagicMissile(),
    ) == 2.2
    assert mage_mechanics.arcane_critical_multiplier(
        player,
        2.0,
        abilities.ManaRupture(),
    ) == 2.0
    player.spellbook["Spells"]["Magic Missile"] = abilities.MagicMissile()
    missile = presented_abilities(player, "Spells")[0]
    assert [
        modifier.name for modifier in missile.presentation_modifications
    ] == ["Guidance Upgrade"]
    assert player.combat.magic == magic_before


def test_affinity_mastery_is_logged_when_the_cast_reaches_the_cap():
    player = _player("Sorcerer")
    player.wizard_affinity = wizard.default_affinity()
    player.wizard_affinity_version = 2
    player.wizard_affinity["Fire"] = 49

    message = wizard.process_cast(player, abilities.Fireball())

    assert player.wizard_affinity["Fire"] == 50
    assert "mastered Fire affinity" in message


def test_multiplicity_heals_for_each_duplicate_remaining_at_combat_end():
    player = _player("Wizard")
    player.health.current = 50
    player.health.max = 200
    player.spellbook["Skills"]["Multiplicity"] = abilities.Multiplicity()
    duplicates = player.magic_effects["Duplicates"]
    duplicates.active = True
    duplicates.duration = 3

    mage_mechanics.tick_combat_state(player, end=True)

    assert player.health.current == 80


def test_enhancements_proc_refresh_without_stacking():
    player = _player("Sorcerer")
    player.spellbook["Skills"]["Wind Currents"] = abilities.WindCurrents()

    first = mage_mechanics.process_cast(
        player, abilities.Gust(), rng=FixedRng
    )
    second = mage_mechanics.process_cast(
        player, abilities.Gust(), rng=FixedRng
    )

    assert "Wind Currents" in first
    assert "Wind Currents" in second
    assert player.mage_enhancement_state["wind_currents"] == 3
    assert player.stat_effects["Speed"].extra == 3
    assert mage_mechanics.melee_accuracy_bonus(player) == 0.10


def test_refreshment_restores_five_percent_of_max_resources():
    player = _player()
    player.spellbook["Skills"]["Refreshment"] = abilities.Refreshment()

    message = mage_mechanics.process_cast(
        player, abilities.WaterJet(), rng=FixedRng
    )

    assert player.health.current == 110
    assert player.mana.current == 88
    assert "10 HP and 8 MP" in message


def test_transient_companion_replaces_prior_one_acts_and_expires():
    player = _player()
    first = mage_mechanics.set_transient_companion(
        player,
        name="Wolf",
        kind="animal",
        source="Conjure Animal",
        damage=10,
    )
    assert first["steps_remaining"] == 50
    mage_mechanics.set_transient_companion(
        player,
        name="Undead Goblin",
        kind="undead",
        source="Enliven Dead",
        damage=12,
    )
    enemy = SimpleNamespace(
        name="Target",
        health=Resource(100, 100),
        is_alive=lambda: True,
    )

    message = mage_mechanics.transient_companion_action(
        player, [enemy], rng=FixedRng
    )

    assert "Undead Goblin acts independently" in message
    assert enemy.health.current == 91
    mage_mechanics.tick_exploration(player, 49)
    assert player.transient_companion["steps_remaining"] == 1
    mage_mechanics.tick_exploration(player, 1)
    assert player.transient_companion is None


def test_conjure_animal_uses_defined_animals_nearest_the_current_floor():
    player = _player()
    player.location_z = 4
    player.mana.current = 100

    message = abilities.ConjureAnimal().cast_out(player)

    assert "answers the call" in message
    assert player.transient_companion["enemy_type"] == "Animal"
    floor_animals = {
        factory().name
        for _name, factory in enemies.random_enemy_candidates("4")
        if factory().enemy_typ == "Animal"
    }
    assert player.transient_companion["name"] in floor_animals


def test_conjurer_calling_uses_an_ordinary_transient_not_a_xenid():
    player = _player("Conjurer")
    player.location_z = 0
    player.mana.current = 100

    message = abilities.ConjureHumanoid().cast(player)

    assert "fight independently for 50 steps" in message
    assert player.transient_companion["enemy_type"] == "Humanoid"
    assert player.transient_companion["name"] in {"Goblin", "Bandit"}
    assert player.xenid_choices == {}
    assert not getattr(player, "summons", {})


def test_torchlight_halves_encounter_rate_for_fifty_steps():
    player = _player("Conjurer")
    player.mana.current = 100

    message = abilities.Torchlight().cast_out(player)

    assert "driving away enemies for 50 steps" in message
    assert mage_mechanics.torchlight_encounter_multiplier(player) == 0.50
    mage_mechanics.tick_exploration(player, 49)
    assert mage_mechanics.torchlight_encounter_multiplier(player) == 0.50
    mage_mechanics.tick_exploration(player, 1)
    assert mage_mechanics.torchlight_encounter_multiplier(player) == 1.0


def test_arcane_specialization_tracks_arcane_affinity_only():
    player = _player("Sorcerer")
    player.spellbook["Skills"]["Arcane Tradition"] = abilities.ArcaneTradition()

    wizard.process_cast(player, abilities.Firebolt())
    wizard.process_cast(player, abilities.MagicMissile())

    assert player.wizard_affinity["Fire"] == 0
    assert player.wizard_affinity["Arcane"] == 1


def test_binding_circle_and_summoner_talents_scale_permanent_summons():
    player = _player("Thaumaturgist")
    player.progression.purchased_node_ids.update(
        {
            "mage.talent.binding-circle",
            "summoner.talent.summoner-conduit-mastery",
            "summoner.talent.summoner-conduit-mastery.rank-2",
            "summoner.talent.summoner-true-name-ward",
        }
    )

    health, damage = mage_mechanics.permanent_summon_multipliers(player)

    assert health == pytest.approx(1.155)
    assert damage == pytest.approx(1.21)


def test_polymorph_controls_for_two_turns_and_inflate_health_absorbs_damage():
    caster = _player()
    target = _player("Warlock")
    target.name = "Target"

    assert "harmless bunny for 2 turns" in abilities.Polymorph().cast(
        caster,
        target,
    )
    assert target.status_effects["Polymorph"].active
    assert target.status_effects["Polymorph"].duration == 2
    assert target.incapacitated()
    active, reason = target.check_active()
    assert not active
    assert "polymorphed" in reason

    abilities.InflateHealth().cast(target)
    temporary_hp = target.temporary_health["amount"]
    _, message, remaining = target.damage_reduction(
        temporary_hp + 10,
        caster,
        typ="Physical",
    )
    assert "inflated health absorbs" in message
    assert remaining > 0
    assert target.temporary_health is None


def test_bosses_strongly_resist_polymorph_without_immunity(monkeypatch):
    caster = _player()
    boss = enemies.Minotaur()
    spell = abilities.Polymorph()
    mana_before = caster.mana.current

    monkeypatch.setattr("src.core.abilities.mage.random.random", lambda: 0.99)
    assert spell.cast(caster, boss) == "Minotaur resists the polymorph.\n"
    assert not boss.status_effects["Polymorph"].active
    assert caster.mana.current == mana_before - spell.cost

    monkeypatch.setattr("src.core.abilities.mage.random.random", lambda: 0.05)
    assert "transformed into a harmless bunny" in spell.cast(caster, boss)
    assert boss.status_effects["Polymorph"].active


def test_enliven_dead_uses_last_nonboss_enemy_and_forbidden_studies(monkeypatch):
    player = _player()
    player.progression.purchased_node_ids.add(
        "mage.talent.forbidden-studies"
    )
    player.last_defeated_enemy = {
        "name": "Goblin",
        "enemy_type": "Humanoid",
        "level": 4,
    }
    monkeypatch.setattr("src.core.abilities.mage.random.randint", lambda *_: 20)

    message = abilities.EnlivenDead().cast_out(player)

    assert "Undead Goblin" in message
    assert player.transient_companion["kind"] == "undead"
    assert player.transient_companion["steps_remaining"] == 75
    base_damage = player.transient_companion["damage"]
    enemy = SimpleNamespace(
        name="Target",
        health=Resource(100, 100),
        is_alive=lambda: True,
    )
    mage_mechanics.transient_companion_action(
        player,
        [enemy],
        rng=FixedRng,
    )
    expected_damage = int(base_damage * 0.8)
    assert enemy.health.current == 100 - expected_damage


def test_forbidden_studies_only_increases_shadow_bolt_spell_damage():
    player = _player()
    player.progression.purchased_node_ids.add(
        "mage.talent.forbidden-studies"
    )

    assert mage_mechanics.spell_damage_multiplier(
        player,
        abilities.ShadowBolt(),
    ) == pytest.approx(1.2)
    assert mage_mechanics.spell_damage_multiplier(
        player,
        abilities.Enfeeble(),
    ) == pytest.approx(1.0)


def test_conjure_shackles_and_potion_apply_first_pass_rules(monkeypatch):
    player = _player()
    target = _player("Warlock")
    target.name = "Target"
    target.stats.dex = 0
    monkeypatch.setattr("src.core.abilities.mage.random.randint", lambda low, high: high)

    message = abilities.ConjureShackles().cast(player, target)

    assert "hold Target prone" in message
    assert target.physical_effects["Prone"].active
    assert target.conjured_shackles["turns"] == 3

    player.in_town = False
    monkeypatch.setattr(
        "src.core.abilities.mage.random.choice",
        lambda values: values[0],
    )
    potion_message = abilities.ConjurePotion().cast(player)
    assert "conjures" in potion_message
    assert player.conjure_potion_cooldown == 50
    assert any("Health Potion" in name for name in player.inventory)
    assert {
        item.subtyp
        for item_list in player.inventory.values()
        for item in item_list
    } <= {"Health", "Mana"}


def test_classical_force_reduces_mana_shield_and_imbue_weapon_by_twenty_five_percent(
    monkeypatch,
):
    attacker = _player("Warlock")
    defender = _player()
    defender.spellbook["Skills"]["Classical Force"] = abilities.ClassicalForce()
    defender.magic_effects["Mana Shield"].active = True
    defender.magic_effects["Mana Shield"].duration = 25
    defender.mana.current = 100

    damage, _, absorbed = attacker._apply_mana_shield(
        defender,
        10,
        physical=True,
    )
    assert damage == 9
    assert not absorbed
    assert defender.mana.current == 99

    recorded = {}

    def weapon_damage(_target, **kwargs):
        recorded.update(kwargs)
        return "", True, 1

    monkeypatch.setattr(defender, "weapon_damage", weapon_damage)
    defender.stats.intel = 30
    abilities.ImbueWeapon().use(defender, attacker)
    assert recorded["dmg_mod"] == pytest.approx(1.75)


def test_force_multiplier_increases_arcane_cost_and_damage():
    player = _player("Sorcerer")
    player.spellbook["Skills"]["Force Multiplier"] = abilities.ForceMultiplier()
    spell = abilities.MagicMissile2()

    assert mage_mechanics.spell_mana_cost(player, spell) == 23
    assert mage_mechanics.spell_damage_multiplier(player, spell) == pytest.approx(1.25)
    mana_rupture = abilities.ManaRupture()
    assert mage_mechanics.spell_mana_cost(player, mana_rupture) == 20
    assert mage_mechanics.spell_damage_multiplier(player, mana_rupture) == 1.0


def test_arcane_empowerment_builds_to_five_stacks_from_kinetic_explosion_hits():
    player = _player("Sorcerer")
    player.spellbook["Skills"]["Arcane Empowerment"] = abilities.ArcaneEmpowerment()

    for _ in range(8):
        mage_mechanics.record_spell_damage_hit(
            player,
            {"ability_name": "Kinetic Explosion", "attack_source": "spell"},
        )

    assert player.mage_enhancement_state["arcane_empowerment"] == 5
    assert mage_mechanics.spell_damage_multiplier(
        player,
        abilities.Fireball(),
    ) == pytest.approx(1.25)


def test_fragmentation_shards_persist_until_detonation_cascade(monkeypatch):
    player = _player("Wizard")
    target = enemies.Goblin()
    target.health.current = target.health.max = 1000
    player.spellbook["Skills"]["Fragmentation"] = abilities.Fragmentation()
    player.spellbook["Skills"]["Detonation Cascade"] = (
        abilities.DetonationCascade()
    )
    player.spellbook["Skills"]["Arcane Empowerment"] = (
        abilities.ArcaneEmpowerment()
    )
    player._combat_encounter = SimpleNamespace(
        living_members=[SimpleNamespace(enemy=target)]
    )
    monkeypatch.setattr(mage_mechanics.random, "random", lambda: 0.0)

    for _index in range(3):
        mage_mechanics.record_spell_damage_hit(
            player,
            target,
            {"ability_name": "Magic Missile III", "attack_source": "spell"},
        )
    assert player.mage_enhancement_state["arcane_crystal_shards"] == 3

    message = mage_mechanics.process_cast(
        player,
        abilities.KineticExplosion(),
        target,
    )

    assert "Detonation Cascade" in message
    assert "arcane_crystal_shards" not in player.mage_enhancement_state
    assert player.mage_enhancement_state["arcane_empowerment"] == 3


def test_mana_rupture_modifiers_consume_empowerment_and_shards():
    player = _player("Wizard")
    target = enemies.Goblin()
    target.mana.current = target.mana.max = 100
    player.spellbook["Skills"]["Mana Leak"] = abilities.ManaLeak()
    player.spellbook["Skills"]["Mana Splinters"] = abilities.ManaSplinters()
    player.mage_enhancement_state = {
        "arcane_empowerment": 3,
        "arcane_crystal_shards": 4,
    }
    player._combat_encounter = SimpleNamespace(
        living_members=[SimpleNamespace(enemy=target)]
    )
    player.mana.current = 0

    message = mage_mechanics.resolve_mana_rupture(player, target)

    assert "Mana Leak" in message
    assert "Mana Splinters" in message
    assert target.mana.current == 70
    assert player.mana.current > 0
    assert player.mage_enhancement_state == {}


def test_mana_rupture_damage_scales_with_target_remaining_mana():
    player = _player("Mage")
    low_mana_target = enemies.Goblin()
    high_mana_target = enemies.Goblin()
    low_mana_target.mana.current = 10
    high_mana_target.mana.current = 100
    low_result = abilities.ManaRupture().cast(player, low_mana_target)
    high_result = abilities.ManaRupture().cast(player, high_mana_target)

    assert high_result.damage > low_result.damage


def test_wizard_elemental_passives_do_not_disclose_cross_school_interactions():
    passives = (
        abilities.Inferno(),
        abilities.Subzero(),
        abilities.ElectricalBurns(),
        abilities.DivineWind(),
        abilities.UnrelentingWaves(),
        abilities.Aftershock(),
    )

    assert all("synergy" not in passive.description.lower() for passive in passives)


def test_refueling_restores_twenty_percent_of_maximum_mana_each_tick():
    player = _player("Sorcerer")
    player.mana.current = 10

    assert "begins channeling" in abilities.Refueling().cast(player)
    message = mage_mechanics.tick_combat_state(player)

    assert player.mana.current == 42
    assert "refuels 32 MP" in message


def test_school_modifiers_are_separate_from_spell_descriptions_and_support_multiple():
    player = _player()
    firebolt = abilities.Firebolt()
    player.spellbook["Spells"][firebolt.name] = firebolt
    player.spellbook["Skills"]["Fire Inside"] = abilities.FireInside()
    focused_flame = SimpleNamespace(
        name="Focused Flame",
        description="Firebolt gains a second focused modifier.",
        presentation_modifier=True,
        modifies_abilities=("Firebolt",),
    )
    player.spellbook["Skills"][focused_flame.name] = focused_flame

    description = composed_description(player, firebolt)
    modifications = ability_modifications(player, firebolt)
    presented_firebolt = presented_abilities(player, "Spells")[0]
    skill_names = [ability.name for ability in presented_abilities(player, "Skills")]

    assert description == firebolt.description
    assert "Fire Inside" not in description
    assert [modifier.name for modifier in modifications] == [
        "Fire Inside",
        "Focused Flame",
    ]
    assert presented_firebolt.presentation_modifications == modifications
    assert "Fire Inside" not in skill_names
    assert "Focused Flame" not in skill_names
