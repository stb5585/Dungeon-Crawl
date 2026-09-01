"""Focused coverage for the Knight Enchanter ability tree and Blade Weaves."""

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies
from src.core.classes import mage_mechanics, promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind
from tests.test_framework import TestGameState


def _player():
    player = TestGameState.create_player(
        class_name="Knight Enchanter",
        race_name="Human",
        level=75,
        health=(500, 500),
        mana=(200, 200),
        stats={
            "strength": 30,
            "intel": 30,
            "wisdom": 30,
            "con": 30,
            "charisma": 30,
            "dex": 30,
        },
    )
    player._active_combat = True
    return player


def _spell(name: str, subtype: str, school: str | None = None):
    return SimpleNamespace(name=name, typ="Spell", subtyp=subtype, school=school)


def _charge(player, arcane=1, elemental=1):
    promotion_kits.combat_state(player)["blade_charge"] = {
        "Arcane": arcane,
        "Elemental": elemental,
    }


def test_third_eye_is_an_aegis_release_option_after_defensive_release():
    tree = ABILITY_TREES["Knight Enchanter"]
    nodes = {node.name: node for node in tree.nodes}
    third_eye = nodes["Third Eye"]

    assert third_eye.kind == NodeKind.ABILITY
    assert third_eye.lane == "Aegis Release"
    assert third_eye.position == (2, 2)
    assert third_eye.payload["level_requirement"] == 70
    assert third_eye.prerequisites == (nodes["Defensive Release"].id,)
    assert third_eye.payload["ability_class"] is abilities.ThirdEye


def test_third_eye_describes_its_intelligence_scaling():
    third_eye = abilities.ThirdEye()

    assert third_eye.passive is True
    assert "Intelligence" in third_eye.description
    assert "critical-hit" in third_eye.description
    assert "dodge" in third_eye.description


def test_tree_matches_the_authored_release_lanes_and_independent_options():
    tree = ABILITY_TREES["Knight Enchanter"]
    nodes = {node.name: node for node in tree.nodes}

    assert tree.branches == (
        "Advanced Spells",
        "Assault Release",
        "Aegis Release",
        "Spellbind Release",
        "Universal / Extra Abilities",
    )
    expected = {
        "Fireball": ((0, 0), 70),
        "Icicle": ((0, 1), 70),
        "Lightning": ((0, 2), 70),
        "Hurricane": ((0, 3), 70),
        "Aqualung": ((0, 4), 70),
        "Mudslide": ((0, 5), 70),
        "Magic Missile II": ((0, 6), 70),
        "Double Strike": ((1, 0), None),
        "Cleaving Edge": ((1, 1), 65),
        "Re-debuff": ((1, 2), 70),
        "Resonant Strike": ((1, 3), 75),
        "Mana Slice II": ((1, 5), 85),
        "Quick Recharge": ((1, 6), 90),
        "Enhance Armor": ((2, 0), None),
        "Defensive Release": ((2, 1), 65),
        "Third Eye": ((2, 2), 70),
        "Aegis Weave": ((2, 3), 75),
        "Weave Reservoir": ((2, 4), 80),
        "Arcane Riposte": ((2, 5), 85),
        "Mana Tap": ((3, 0), None),
        "Dispel Slash": ((3, 1), 65),
        "Storage Capacity II": ((3, 3), 75),
        "Spellbind": ((3, 4), 80),
        "Echoing Blade": ((3, 5), 85),
        "Parry": ((4, 0), None),
        "Riposte": ((4, 1), 65),
        "True Piercing Strike": ((4, 3), 75),
        "Triple Strike": ((4, 5), 85),
    }
    assert len(tree.nodes) == len(expected)
    assert {
        node.name: node.cost
        for node in tree.nodes
        if node.cost == 2
    } == {
        "Quick Recharge": 2,
        "Storage Capacity II": 2,
        "Third Eye": 2,
    }
    assert all(
        node.cost == 1
        for node in tree.nodes
        if node.name not in {"Quick Recharge", "Storage Capacity II", "Third Eye"}
    )
    assert {
        name: (
            node.position,
            node.payload.get("level_requirement"),
        )
        for name, node in nodes.items()
    } == expected
    assert nodes["Spellbind"].prerequisites == (
        nodes["Storage Capacity II"].id,
    )
    assert nodes["Parry"].prerequisites == ()
    assert nodes["True Piercing Strike"].prerequisites == ()
    assert nodes["Triple Strike"].prerequisites == ()
    assert all(
        not nodes[name].prerequisites
        for name in {
            "Fireball",
            "Icicle",
            "Lightning",
            "Hurricane",
            "Aqualung",
            "Mudslide",
            "Magic Missile II",
        }
    )
    assert nodes["Parry"].payload["owned_if_known"] is True
    assert {"Charged Blade", "Runic Plate"}.isdisjoint(nodes)
    assert nodes["Aegis Weave"].payload["ability_class"] is abilities.AegisWeave
    assert nodes["Spellbind"].payload["ability_class"] is abilities.Spellbind


def test_storage_capacity_two_adds_two_and_stacks_with_spellblade_training():
    from src.core.classes.promotion_kits import meters

    player = _player()
    player.spellbook["Skills"]["Storage Capacity II"] = (
        abilities.StorageCapacity2()
    )

    assert meters._blade_charge_capacity(player) == 3

    player.spellbook["Skills"]["Storage Capacity"] = abilities.StorageCapacity()

    assert meters._blade_charge_capacity(player) == 4


@pytest.mark.parametrize(
    ("spell", "signature"),
    (
        (_spell("Fireball", "Fire", "Elemental"), "Element"),
        (_spell("Magic Missile", "Non-elemental", "Arcane"), "Force"),
        (_spell("Mana Shield", "Support", "Abjuration"), "Protection"),
        (_spell("Teleport", "Movement", "Conjuration"), "Conjuration"),
    ),
)
def test_spell_categories_map_to_four_signatures(spell, signature):
    assert promotion_kits.spell_weave_signature(spell) == signature


def test_foundation_is_stable_and_latest_different_signature_replaces_accent():
    player = _player()

    assert "Force weave Foundation" in promotion_kits.record_spell_signature(
        player,
        _spell("Magic Missile", "Non-elemental", "Arcane"),
    )
    promotion_kits.record_spell_signature(player, _spell("Fireball", "Fire"))
    assert promotion_kits.weave_pattern(player) == ("Force", "Element")

    promotion_kits.record_spell_signature(
        player,
        _spell("Mana Shield", "Support", "Abjuration"),
    )
    assert promotion_kits.weave_pattern(player) == ("Force", "Protection")
    assert promotion_kits.weave_preview(player) == (
        "Force: defense break; Protection: returned ward"
    )

    promotion_kits.record_spell_signature(
        player,
        _spell("Kinetic Explosion", "Arcane", "Arcane"),
    )
    assert promotion_kits.weave_pattern(player) == ("Force", "Protection")


def test_successful_cast_processing_records_signature_in_combat_only():
    player = _player()
    fire = _spell("Fireball", "Fire", "Elemental")

    message = mage_mechanics.process_cast(player, fire)

    assert "Element weave Foundation" in message
    assert promotion_kits.weave_pattern(player) == ("Element", None)
    promotion_kits.clear_combat_state(player)
    player._active_combat = False

    assert mage_mechanics.process_cast(player, fire) == ""
    assert promotion_kits.weave_pattern(player) == (None, None)


def test_status_rows_present_charge_pattern_preview_and_pending_release():
    player = _player()
    _charge(player)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Element"
    state["weave_accent"] = "Force"
    state["spellbind"] = {"turns": 2}

    rows = promotion_kits.status_summary_rows(player)

    assert ("Blade Charge", "Arcane ×1 · Elemental ×1") in rows
    assert ("Foundation", "Element") in rows
    assert ("Accent", "Force") in rows
    assert ("Weave", "Element: volatile damage; Force: deeper break") in rows
    assert ("Spellbind", "Ready · 2 turn(s)") in rows


def test_enchanted_assault_spends_pattern_and_applies_both_signature_rules():
    player = _player()
    target = enemies.Goblin()
    target.health.max = 500
    target.health.current = 500
    target.resistance["Non-elemental"] = 0.0
    _charge(player)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Element"
    state["weave_accent"] = "Protection"
    before = target.health.current

    promotion_kits.record_damage_event(
        player,
        target,
        100,
        "Physical",
        metadata={"attack_source": "weapon", "ability_name": "Attack"},
    )

    assert before - target.health.current == 36
    assert player.temporary_health == {
        "amount": 30,
        "turns": 2,
        "source": "enchantment ward",
    }
    assert state["blade_charge"] is None
    assert promotion_kits.weave_pattern(player) == (None, None)
    assert "Element > Protection" in promotion_kits.pop_messages(player)


def test_awakened_arcane_duel_preserves_accent_as_foundation(monkeypatch):
    player = _player()
    target = enemies.Goblin()
    target.health.max = 500
    target.health.current = 500
    _charge(player, arcane=1, elemental=0)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Force"
    state["weave_accent"] = "Conjuration"
    monkeypatch.setattr(
        "src.core.classes.promotion_kits.weaves._ring_awakened_equipped",
        lambda *_args: True,
    )

    promotion_kits.record_damage_event(
        player,
        target,
        100,
        "Physical",
        metadata={"attack_source": "weapon", "ability_name": "Attack"},
    )

    assert promotion_kits.weave_pattern(player) == ("Conjuration", None)
    assert "Arcane Duel preserves Conjuration" in promotion_kits.pop_messages(player)


def test_aegis_weave_consumes_protection_conjuration_pattern():
    player = _player()
    _charge(player)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Protection"
    state["weave_accent"] = "Conjuration"
    skill = abilities.AegisWeave()

    assert skill.is_available(player) is True
    message = skill.use(player)

    assert "120 temporary HP for 4 turns" in message
    assert player.temporary_health == {
        "amount": 120,
        "turns": 4,
        "source": "enchantment ward",
    }
    assert state["blade_charge"] is None
    assert promotion_kits.weave_pattern(player) == (None, None)
    assert skill.is_available(player) is False


def test_spellbind_spends_old_weave_then_next_spell_starts_new_charge():
    player = _player()
    target = enemies.Goblin()
    target.health.max = 500
    target.health.current = 500
    target.resistance["Non-elemental"] = 0.0
    _charge(player)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Force"
    state["weave_accent"] = "Conjuration"
    before = target.health.current

    message = abilities.Spellbind().use(player)
    assert "binds Force > Conjuration" in message
    assert state["blade_charge"] is None

    promotion_kits.begin_action(player)
    promotion_kits.record_damage_event(
        player,
        target,
        100,
        "Fire",
        metadata={
            "attack_source": "spell",
            "ability_name": "Fireball",
            "source": "spell",
        },
    )

    assert before - target.health.current == 24
    assert target.stat_effects["Magic Defense"].extra == -8
    assert state["spellbind"] is None
    assert state["blade_charge"] == {"Arcane": 0, "Elemental": 1}


def test_combat_reset_clears_weave_pattern_and_pending_spellbind():
    player = _player()
    _charge(player)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Protection"
    abilities.Spellbind().use(player)

    promotion_kits.clear_combat_state(player)

    state = promotion_kits.combat_state(player)
    assert state["blade_charge"] is None
    assert state["weave_foundation"] is None
    assert state["weave_accent"] is None
    assert state["spellbind"] is None


def test_spellbind_expires_after_three_turn_ticks_without_a_damage_hit():
    player = _player()
    _charge(player, arcane=1, elemental=0)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Force"
    abilities.Spellbind().use(player)

    assert promotion_kits.tick_combat_state(player) == ""
    assert promotion_kits.tick_combat_state(player) == ""
    message = promotion_kits.tick_combat_state(player)

    assert "Spellbind fades" in message
    assert state["spellbind"] is None


def test_defensive_release_stacks_three_times_and_empowers_next_aegis():
    player = _player()
    player.spellbook["Skills"]["Defensive Release"] = abilities.DefensiveRelease()
    _charge(player, arcane=1, elemental=0)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Protection"

    for expected in (1, 2, 3, 3):
        assert f"({expected}/3)" in promotion_kits.defensive_release(player)
    message = abilities.AegisWeave().use(player)

    assert "105 temporary HP" in message
    assert state["defensive_release"] == 0


def test_resonant_strike_preserves_foundation_matching_charge():
    player = _player()
    player.spellbook["Skills"]["Resonant Strike"] = abilities.ResonantStrike()
    _charge(player)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Element"

    abilities.AegisWeave().use(player)

    assert state["blade_charge"] == {"Arcane": 0, "Elemental": 1}


def test_weave_reservoir_regenerates_only_when_both_pools_are_full():
    player = _player()
    player.spellbook["Skills"]["Weave Reservoir"] = abilities.WeaveReservoir()
    player.health.current = 400
    player.mana.current = 100
    _charge(player)

    message = promotion_kits.tick_combat_state(player)

    assert "restores 15 HP and 6 MP" in message
    assert player.health.current == 415
    assert player.mana.current == 106


def test_cleaving_edge_and_re_debuff_affect_adjacent_enemy():
    player = _player()
    player.spellbook["Skills"].update({
        "Cleaving Edge": abilities.CleavingEdge(),
        "Re-debuff": abilities.ReDebuff(),
    })
    primary = enemies.Goblin()
    adjacent = enemies.Goblin()
    for target in (primary, adjacent):
        target.health.current = target.health.max = 500
        target.status_effects["Blind"].active = True
        target.status_effects["Blind"].duration = 1
    player._combat_encounter = SimpleNamespace(living_members=(
        SimpleNamespace(enemy=primary, slot=0),
        SimpleNamespace(enemy=adjacent, slot=1),
    ))
    _charge(player, arcane=1, elemental=0)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Element"

    promotion_kits.record_damage_event(
        player,
        primary,
        100,
        "Physical",
        metadata={"attack_source": "weapon", "ability_name": "Attack"},
    )

    assert primary.health.current == 482
    assert adjacent.health.current == 482
    assert primary.status_effects["Blind"].duration == 3
    assert adjacent.status_effects["Blind"].duration == 3


def test_echoing_blade_repeats_release_at_next_turn(monkeypatch):
    player = _player()
    player.spellbook["Skills"]["Echoing Blade"] = abilities.EchoingBlade()
    target = enemies.Goblin()
    target.health.current = target.health.max = 500
    _charge(player, arcane=1, elemental=0)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Element"
    monkeypatch.setattr(
        "src.core.classes.promotion_kits.weaves.random.random",
        lambda: 0.0,
    )

    promotion_kits.record_damage_event(
        player,
        target,
        100,
        "Physical",
        metadata={"attack_source": "weapon", "ability_name": "Attack"},
    )
    after_release = target.health.current
    message = promotion_kits.tick_combat_state(player)

    assert "Echoing Blade repeats" in message
    assert after_release - target.health.current == 18
    assert state["echoing_weave"] is None


def test_arcane_riposte_guarantees_parry_counter_releases_weave(monkeypatch):
    defender = _player()
    attacker = enemies.Goblin()
    defender.spellbook["Skills"].update({
        "Parry": abilities.Parry(),
        "Riposte": abilities.Riposte(),
        "Arcane Riposte": abilities.ArcaneRiposte(),
    })
    _charge(defender, arcane=1, elemental=0)
    state = promotion_kits.combat_state(defender)
    state["weave_foundation"] = "Element"
    monkeypatch.setattr(defender, "dodge_chance", lambda *_args, **_kwargs: 0.0)
    monkeypatch.setattr("src.core.character.offense.random.random", lambda: 0.0)

    message, _hit, _crit = attacker.weapon_damage(defender, hit=True)

    assert "Arcane Riposte releases the stored weave" in message
    assert state["blade_charge"] is None
    assert promotion_kits.weave_pattern(defender) == (None, None)


def test_quick_recharge_repeats_release_on_later_multi_hit_strikes():
    player = _player()
    player.spellbook["Skills"]["Quick Recharge"] = abilities.QuickRecharge()
    target = enemies.Goblin()
    target.health.current = target.health.max = 500
    target.resistance["Non-elemental"] = 0.0
    target.resistance["Arcane"] = 0.0
    _charge(player, arcane=1, elemental=0)
    state = promotion_kits.combat_state(player)
    state["weave_foundation"] = "Element"

    assert promotion_kits.begin_multi_hit_weave(player, 2) is True
    for _ in range(2):
        promotion_kits.record_damage_event(
            player,
            target,
            100,
            "Physical",
            metadata={"attack_source": "weapon", "ability_name": "Double Strike"},
        )
    promotion_kits.end_multi_hit_weave(player)

    assert target.health.current == 464
    assert "Quick Recharge repeats" in promotion_kits.pop_messages(player)
    assert "quick_recharge" not in state
