"""Regression coverage for the authored Spellblade tree and combat loop."""

from __future__ import annotations

import pytest

from src.core import abilities, enemies, items
from src.core.classes import promotion_kits
from src.core.combat import TargetScope
from src.core.progression import (
    ABILITY_TREES,
    NodeKind,
    NodeState,
    ProgressionState,
    available_nodes,
)
from tests.test_framework import TestGameState


def _player(class_name: str = "Spellblade", *, mana=(200, 200)):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=60,
        health=(500, 500),
        mana=mana,
        stats={
            "strength": 30,
            "intel": 30,
            "wisdom": 30,
            "con": 30,
            "charisma": 30,
            "dex": 30,
        },
    )
    player.progression = ProgressionState(
        level=60,
        unspent_points=100,
        unspent_attribute_points=100,
    )
    return player


def _nodes(class_name: str = "Spellblade"):
    return {node.name: node for node in ABILITY_TREES[class_name].nodes}


def _record_spell_hit(actor, target, damage_type: str, name: str) -> None:
    promotion_kits.record_damage_event(
        actor,
        target,
        20,
        damage_type,
        metadata={
            "ability_name": name,
            "attack_source": "spell",
            "source": "spell",
        },
    )


def _record_weapon_hit(actor, target, amount: int = 100) -> None:
    promotion_kits.record_damage_event(
        actor,
        target,
        amount,
        "Physical",
        metadata={"attack_source": "weapon", "ability_name": "Attack"},
    )


def test_spellblade_tree_has_exact_authored_columns_and_nodes():
    tree = ABILITY_TREES["Spellblade"]
    nodes = _nodes()

    assert tree.branches == (
        "Weapon Enhancements",
        "Armor Enhancements",
        "Spell Enhancements",
        "Universal / Extra Abilities",
    )
    assert len([node for node in tree.nodes if node.kind != NodeKind.PROMOTION]) == 20
    assert {
        name: nodes[name].position
        for name in (
            "Counter Charge",
            "+20 Attack",
            "Breakdown",
            "Mana Slice",
            "Enhance Blade",
            "Reflect",
            "+20 Magic Defense",
            "Novel Shielding",
            "+20 Defense",
            "Enhance Armor",
            "Kinetic Explosion",
            "+20 Magic",
            "Mana Tap",
            "Amplify Arcane",
            "Amplify Elemental",
            "Storage Capacity",
            "Boost",
            "True Strike",
            "Parry",
            "Double Strike",
            "Promote: Knight Enchanter",
        )
    } == {
        "Counter Charge": (0, 1),
        "+20 Attack": (0, 2),
        "Breakdown": (0, 3),
        "Mana Slice": (0, 4),
        "Enhance Blade": (0, 5),
        "Reflect": (1, 1),
        "+20 Magic Defense": (1, 2),
        "Novel Shielding": (1, 3),
        "+20 Defense": (1, 4),
        "Enhance Armor": (1, 6),
        "Boost": (2, 1),
        "Kinetic Explosion": (2, 2),
        "+20 Magic": (2, 3),
        "Mana Tap": (2, 4),
        "Amplify Arcane": (1.5, 5),
        "Amplify Elemental": (2.5, 5),
        "Storage Capacity": (2, 6),
        "True Strike": (3, 2),
        "Parry": (3, 3),
        "Double Strike": (3, 4),
        "Promote: Knight Enchanter": (1.5, 7),
    }
    assert {
        "Imbue Weapon",
        "Arcane Edge",
        "Spellguard",
        "Elemental Strike",
    }.isdisjoint(nodes)


def test_spellblade_gates_branches_and_promotion_are_authored():
    nodes = _nodes()

    assert nodes["+20 Attack"].payload["amount"] == 20
    assert nodes["+20 Magic Defense"].payload["amount"] == 20
    assert nodes["+20 Defense"].payload["amount"] == 20
    assert nodes["+20 Magic"].payload["amount"] == 20
    for name in ("Counter Charge", "Reflect", "Boost"):
        assert nodes[name].prerequisites == ()
        assert "level_requirement" not in nodes[name].payload
        assert nodes[name].position[1] == 1
    assert nodes["+20 Attack"].payload["level_requirement"] == 35
    assert nodes["+20 Magic Defense"].payload["level_requirement"] == 35
    assert nodes["Breakdown"].payload["level_requirement"] == 40
    assert nodes["Mana Slice"].payload["level_requirement"] == 45
    assert nodes["Enhance Blade"].payload["level_requirement"] == 50
    assert nodes["Novel Shielding"].payload["level_requirement"] == 40
    assert nodes["+20 Defense"].payload["level_requirement"] == 45
    assert nodes["Enhance Armor"].payload["level_requirement"] == 55
    assert nodes["Kinetic Explosion"].payload["level_requirement"] == 35
    assert nodes["+20 Magic"].payload["level_requirement"] == 40
    assert nodes["Mana Tap"].payload["level_requirement"] == 45
    assert nodes["Amplify Arcane"].payload["level_requirement"] == 50
    assert nodes["Amplify Elemental"].payload["level_requirement"] == 50
    assert nodes["Storage Capacity"].payload["level_requirement"] == 55
    assert nodes["Kinetic Explosion"].prerequisites == (nodes["Boost"].id,)
    assert nodes["True Strike"].payload["level_requirement"] == 35
    assert nodes["Parry"].payload["level_requirement"] == 40
    assert nodes["Double Strike"].payload["level_requirement"] == 45
    level_by_row = {1: None, 2: 35, 3: 40, 4: 45, 5: 50, 6: 55}
    for node in ABILITY_TREES["Spellblade"].nodes:
        if node.kind == NodeKind.PROMOTION:
            continue
        assert node.payload.get("level_requirement") == level_by_row[node.position[1]]
    assert nodes["Storage Capacity"].prerequisites == (
        nodes["Amplify Arcane"].id,
        nodes["Amplify Elemental"].id,
    )
    assert nodes["Storage Capacity"].payload["prerequisite_mode"] == "any"
    promotion = nodes["Promote: Knight Enchanter"]
    assert promotion.cost == 3
    assert promotion.payload["level_requirement"] == 60
    assert promotion.payload["requirements"] == {
        "strength": 16,
        "con": 16,
        "intel": 15,
        "dex": 11,
    }
    assert promotion.payload["prerequisite_mode"] == "any"
    assert promotion.prerequisites == (
        nodes["Enhance Blade"].id,
        nodes["Enhance Armor"].id,
        nodes["Storage Capacity"].id,
    )
    for capstone_name in ("Enhance Blade", "Enhance Armor", "Storage Capacity"):
        player = _player()

        def purchase_path(node_id: str) -> None:
            node = next(
                tree_node
                for tree_node in ABILITY_TREES["Spellblade"].nodes
                if tree_node.id == node_id
            )
            for prerequisite in node.prerequisites:
                purchase_path(prerequisite)
            player.progression.purchased_node_ids.add(node_id)

        purchase_path(nodes[capstone_name].id)
        promotion_status = next(
            status
            for status in available_nodes(player, "Spellblade")
            if status.node.name == "Promote: Knight Enchanter"
        )
        assert promotion_status.state == NodeState.AVAILABLE


def test_spellblade_and_knight_enchanter_adopt_known_catchup_abilities():
    spellblade = _player()
    spellblade.spellbook["Skills"].update({
        "Imbue Weapon": abilities.ImbueWeapon(),
        "True Strike": abilities.TrueStrike(),
        "Parry": abilities.Parry(),
        "Double Strike": abilities.DoubleStrike(),
    })
    spellblade.spellbook["Spells"].update({
        "Reflect": abilities.Reflect(),
        "Boost": abilities.Boost(),
    })
    before = spellblade.progression.unspent_points
    statuses = {
        status.node.name: status.state
        for status in available_nodes(spellblade, "Spellblade")
    }

    for name in ("Reflect", "Boost", "True Strike", "Parry", "Double Strike"):
        assert statuses[name] == NodeState.OWNED
    assert "Imbue Weapon" not in statuses
    assert spellblade.progression.unspent_points == before

    knight = _player("Knight Enchanter")
    knight.spellbook["Skills"].update({
        "Double Strike": abilities.DoubleStrike(),
        "Mana Tap": abilities.ManaTap(),
        "Enhance Armor": abilities.EnhanceArmor(),
        "Parry": abilities.Parry(),
    })
    knight_statuses = {
        status.node.name: status.state
        for status in available_nodes(knight, "Knight Enchanter")
    }
    for name in ("Double Strike", "Enhance Armor", "Mana Tap", "Parry"):
        assert knight_statuses[name] == NodeState.OWNED

    untrained_knight = _player("Knight Enchanter")
    untrained_knight.progression.level = 100
    untrained_statuses = {
        status.node.name: status.state
        for status in available_nodes(untrained_knight, "Knight Enchanter")
    }
    for name in ("Double Strike", "Enhance Armor", "Mana Tap", "Parry"):
        assert untrained_statuses[name] == NodeState.AVAILABLE


def test_spellblade_catalog_and_kinetic_explosion_profile():
    names = {
        ability().name
        for catalog in (abilities.skill_dict, abilities.spell_dict)
        for raw in catalog["Spellblade"].values()
        for ability in abilities.ability_classes_for(raw)
    }
    assert {
        "Breakdown",
        "Counter Charge",
        "Double Strike",
        "Novel Shielding",
        "Kinetic Explosion",
        "Amplify Arcane",
        "Amplify Elemental",
        "Storage Capacity",
    }.issubset(names)
    assert "Imbue Weapon" not in names
    assert "Elemental Strike" not in names
    kinetic = abilities.KineticExplosion()
    assert kinetic.cost == 18
    assert kinetic.dmg_mod == 1.5
    assert kinetic.subtyp == "Arcane"
    assert kinetic.target_scope == TargetScope.ALL_ENEMIES
    assert kinetic._effects == []


def test_breakdown_is_per_target_capped_and_consumed_after_spell_damage():
    player = _player()
    player.spellbook["Skills"]["Breakdown"] = abilities.Breakdown()
    first = enemies.Goblin()
    second = enemies.Goblin()
    base_magic_defense = first.check_mod("magic def", enemy=player)

    for _ in range(7):
        _record_weapon_hit(player, first, 20)
    _record_weapon_hit(player, second, 20)

    assert promotion_kits.breakdown_magic_defense_penalty(player, first) == 20
    assert promotion_kits.breakdown_magic_defense_penalty(player, second) == 4
    assert first.check_mod("magic def", enemy=player) == max(
        0,
        base_magic_defense - 20,
    )

    promotion_kits.begin_action(player)
    _record_spell_hit(player, first, "Fire", "Firebolt")

    assert promotion_kits.breakdown_magic_defense_penalty(player, first) == 0
    assert promotion_kits.breakdown_magic_defense_penalty(player, second) == 4


def test_blade_charges_stack_by_broad_type_once_per_action():
    player = _player()
    player.spellbook["Skills"]["Storage Capacity"] = abilities.StorageCapacity()
    first = enemies.Goblin()
    second = enemies.Goblin()

    promotion_kits.begin_action(player)
    _record_spell_hit(player, first, "Fire", "Firebolt")
    _record_spell_hit(player, second, "Fire", "Firebolt")
    assert promotion_kits.combat_state(player)["blade_charge"] == {
        "Arcane": 0,
        "Elemental": 1,
    }

    promotion_kits.begin_action(player)
    _record_spell_hit(player, first, "Shadow", "Shadow Bolt")
    assert promotion_kits.combat_state(player)["blade_charge"] == {
        "Arcane": 1,
        "Elemental": 1,
    }

    promotion_kits.begin_action(player)
    _record_spell_hit(player, first, "Ice", "Ice Lance")
    assert promotion_kits.combat_state(player)["blade_charge"] == {
        "Arcane": 1,
        "Elemental": 2,
    }

    promotion_kits.begin_action(player)
    _record_spell_hit(player, first, "Non-elemental", "Magic Missile")
    assert promotion_kits.combat_state(player)["blade_charge"] == {
        "Arcane": 2,
        "Elemental": 2,
    }

    promotion_kits.begin_action(player)
    _record_spell_hit(player, first, "Non-elemental", "Ultima")
    assert promotion_kits.combat_state(player)["blade_charge"] == {
        "Arcane": 2,
        "Elemental": 2,
    }

    player.spellbook["Skills"].pop("Storage Capacity")
    promotion_kits.combat_state(player)["blade_charge"] = None
    promotion_kits.begin_action(player)
    _record_spell_hit(player, first, "Arcane", "Kinetic Explosion")
    assert promotion_kits.combat_state(player)["blade_charge"] == {
        "Arcane": 1,
        "Elemental": 0,
    }


def test_multimissile_cast_stores_only_one_arcane_charge():
    player = _player()
    player.spellbook["Skills"]["Storage Capacity"] = abilities.StorageCapacity()
    target = _player("Mage")
    target.status_effects["Stun"].active = True
    promotion_kits.begin_action(player)

    abilities.MagicMissile2().cast(player, target)

    assert promotion_kits.combat_state(player)["blade_charge"] == {
        "Arcane": 1,
        "Elemental": 0,
    }


def test_counter_charge_gains_once_per_incoming_spell_action():
    caster = _player("Mage")
    defender = _player()
    defender.spellbook["Skills"].update({
        "Counter Charge": abilities.CounterCharge(),
        "Storage Capacity": abilities.StorageCapacity(),
    })

    promotion_kits.begin_action(caster)
    _record_spell_hit(caster, defender, "Holy", "Holy")
    _record_spell_hit(caster, defender, "Holy", "Holy")
    assert promotion_kits.combat_state(defender)["blade_charge"] == {
        "Arcane": 1,
        "Elemental": 0,
    }

    promotion_kits.begin_action(caster)
    _record_spell_hit(caster, defender, "Fire", "Firebolt")
    assert promotion_kits.combat_state(defender)["blade_charge"] == {
        "Arcane": 1,
        "Elemental": 1,
    }


def test_typed_charge_pools_release_with_matching_amplify_and_resistance():
    player = _player()
    player.spellbook["Skills"].update({
        "Storage Capacity": abilities.StorageCapacity(),
        "Amplify Elemental": abilities.AmplifyElemental(),
    })
    target = _player("Mage")
    target.resistance["Fire"] = 1.0
    promotion_kits.begin_action(player)
    _record_spell_hit(player, target, "Fire", "Firebolt")
    promotion_kits.begin_action(player)
    _record_spell_hit(player, target, "Shadow", "Shadow Bolt")
    before = int(target.health.current)

    promotion_kits.begin_action(player)
    _record_weapon_hit(player, target, 100)

    # Arcane contributes 12. Elemental contributes 24 before the average of
    # six elemental resistances (1/6), leaving 20.
    assert before - int(target.health.current) == 32
    assert promotion_kits.combat_state(player)["blade_charge"] is None


def test_missed_weapon_attack_preserves_stored_charge(monkeypatch):
    player = _player()
    target = _player("Mage")
    promotion_kits.begin_action(player)
    _record_spell_hit(player, target, "Arcane", "Kinetic Explosion")
    stored = dict(promotion_kits.combat_state(player)["blade_charge"])
    monkeypatch.setattr(target, "dodge_chance", lambda *_args, **_kwargs: 1.0)

    _message, hit, _crit = player.weapon_damage(target)

    assert hit is False
    assert promotion_kits.combat_state(player)["blade_charge"] == stored


def test_novel_shielding_requires_tome_refreshes_and_expires():
    player = _player(mana=(100, 100))
    skill = abilities.NovelShielding()
    before_mana = player.mana.current

    rejected = skill.use(player)
    assert "must equip a Tome" in rejected.message
    assert player.mana.current == before_mana

    player.equipment["OffHand"] = items.Book()
    activated = skill.use(player)
    assert "12 absorption" in activated.message
    assert player.mana.current == 80
    player.equipment["OffHand"] = items.CodexEternity()
    assert promotion_kits.combat_state(player)["novel_shield"] == {
        "remaining": 12,
        "maximum": 12,
        "turns": 3,
    }
    remaining, _message, fully_absorbed = promotion_kits.absorb_novel_shield(
        player,
        10,
        source="spell",
    )
    assert remaining == 0
    assert fully_absorbed is True

    player.equipment["OffHand"] = items.Book()
    skill.use(player)
    assert player.mana.current == 60
    shield = promotion_kits.combat_state(player)["novel_shield"]
    assert shield == {"remaining": 12, "maximum": 12, "turns": 3}
    promotion_kits.tick_combat_state(player)
    promotion_kits.tick_combat_state(player)
    assert promotion_kits.combat_state(player)["novel_shield"]["turns"] == 1
    assert "fades" in promotion_kits.tick_combat_state(player)
    assert promotion_kits.combat_state(player)["novel_shield"] is None


@pytest.mark.parametrize("source", ["dot", "reflected", "field", "environmental"])
def test_novel_shielding_ignores_non_direct_damage_sources(source):
    player = _player()
    promotion_kits.activate_novel_shield(player, 20)

    damage, message, fully_absorbed = promotion_kits.absorb_novel_shield(
        player,
        8,
        source=source,
    )

    assert damage == 8
    assert message == ""
    assert fully_absorbed is False
    assert promotion_kits.combat_state(player)["novel_shield"]["remaining"] == 20


def test_partial_novel_shielding_does_not_suppress_on_hit_effects():
    player = _player()
    promotion_kits.activate_novel_shield(player, 5)

    damage, _message, fully_absorbed = promotion_kits.absorb_novel_shield(
        player,
        8,
        source="spell",
    )

    assert damage == 3
    assert fully_absorbed is False


def test_novel_shielding_fully_blocks_direct_spell_secondary_effects():
    caster = _player("Mage")
    defender = _player()
    defender.equipment["OffHand"] = items.CodexEternity()
    abilities.NovelShielding().use(defender)
    before = int(defender.health.current)

    result = abilities.Firebolt().cast(caster, defender)

    assert defender.health.current == before
    assert result.damage == 0
    assert not defender.magic_effects["DOT"].active


def test_novel_shielding_fully_blocks_weapon_on_hit_effects():
    attacker = _player()
    attacker.spellbook["Skills"]["Breakdown"] = abilities.Breakdown()
    defender = _player("Mage")
    defender.status_effects["Stun"].active = True
    promotion_kits.activate_novel_shield(defender, 10_000)
    before = int(defender.health.current)

    _message, hit, _crit = attacker.weapon_damage(defender)

    assert hit is False
    assert defender.health.current == before
    assert promotion_kits.breakdown_magic_defense_penalty(attacker, defender) == 0


def test_enhance_blade_and_armor_scale_from_current_mana():
    player = _player(mana=(100, 100))
    weapon_damage = int(player.equipment["Weapon"].damage)
    armor_rating = int(player.equipment["Armor"].armor)
    base_weapon = player.check_mod("weapon")
    base_armor = player.check_mod("armor")
    player.spellbook["Skills"].update({
        "Enhance Blade": abilities.EnhanceBlade(),
        "Enhance Armor": abilities.EnhanceArmor(),
    })

    assert player.check_mod("weapon") == base_weapon + weapon_damage
    assert player.check_mod("armor") == base_armor

    player.mana.current = 0
    assert player.check_mod("weapon") == base_weapon
    assert player.check_mod("armor") == base_armor + armor_rating


def test_spellblade_combat_state_clears_all_new_mechanics():
    player = _player()
    player.spellbook["Skills"].update({
        "Breakdown": abilities.Breakdown(),
        "Storage Capacity": abilities.StorageCapacity(),
    })
    target = enemies.Goblin()
    promotion_kits.begin_action(player)
    _record_spell_hit(player, target, "Fire", "Firebolt")
    _record_weapon_hit(player, target, 20)
    promotion_kits.activate_novel_shield(player, 20)

    promotion_kits.end_combat(player)

    state = promotion_kits.combat_state(player)
    assert state["blade_charge"] is None
    assert state["breakdown_stacks"] == {}
    assert state["novel_shield"] is None
