"""Regression coverage for flat player progression and ability trees."""

from __future__ import annotations

import random

import pytest

from src.core import items
from src.core.abilities import (
    Adrenaline,
    Chastise,
    Dishearten,
    DrivingThrust,
    HonedAttack,
    NaturalAttunement,
    Rally,
    WeaponFocus,
)
from src.core.character import Combat, Level, Resource, Stats
from src.core.classes import (
    Footpad,
    GrandmasterOfArms,
    Healer,
    Mage,
    Pathfinder,
    Troubadour,
    Warrior,
    WeaponMaster,
)
from src.core.classes.promotion_kits import cap_for
from src.core.combat.combat_result import CombatResult
from src.core.effects.skills import ShieldSlamEffect
from src.core.player import Player
from src.core.progression import (
    ABILITY_TREES,
    CLASS_CHILDREN,
    CLASS_DETAILS,
    NodeKind,
    NodeState,
    ProgressionState,
    apply_progression_plan,
    award_experience,
    available_nodes,
    attribute_points_through_level,
    cumulative_experience_for_level,
    experience_for_level,
    has_talent,
    increase_attribute,
    initialize_progression,
    level_up_message,
    progression_points_through_level,
    promotion_combat_bonuses,
    promotion_preview,
    purchase_node,
    validate_trees,
)
from src.core.races import Human, races_dict
from src.core.save_system import PlayerDataSerializer
from src.core.save_system.player import UnsupportedSaveVersionError


def _player(class_type=Pathfinder, stats=30):
    player = Player(
        5,
        10,
        0,
        Level(),
        Resource(60, 60),
        Resource(60, 60),
        Stats(stats, stats, stats, stats, stats, stats),
        Combat(5, 5, 5, 5),
        0,
        {},
    )
    player.cls = class_type()
    player.race = Human()
    player.equipment = dict(player.cls.equipment)
    return player


def test_all_tree_manifests_validate_and_scale_rating_values_by_stage():
    assert validate_trees() == ()
    for tree in ABILITY_TREES.values():
        rating_nodes = [node for node in tree.nodes if node.kind == NodeKind.RATING]
        assert all(
            node.payload["amount"] == CLASS_DETAILS[node.tree_id][1] * 10
            for node in rating_nodes
        )
        assert all(
            node.payload["description"].startswith("Permanently increase")
            for node in rating_nodes
        )
        assert all("level_requirement" not in node.payload for node in rating_nodes)
        resource_nodes = [
            node
            for node in tree.nodes
            if node.kind in {NodeKind.HEALTH, NodeKind.MANA}
        ]
        expected_resources = {1: 25, 2: 50, 3: 100}
        assert all(
            node.payload["amount"]
            == expected_resources[CLASS_DETAILS[node.tree_id][1]]
            for node in resource_nodes
        )
        talent_nodes = [
            node
            for node in tree.nodes
            if node.kind == NodeKind.TALENT
        ]
        if (
            tree.stage > 1
            and tree.class_name not in {"Weapon Master", "Berserker"}
        ):
            assert talent_nodes
        for node in talent_nodes:
            expected_bonus = CLASS_DETAILS[node.tree_id][1] * 10
            assert all(
                amount == expected_bonus
                for amount in node.payload.get("bonuses", {}).get(
                    "ratings",
                    {},
                ).values()
            )
        for node in tree.nodes:
            if node.kind == NodeKind.PROMOTION:
                assert node.payload["level_requirement"] == (
                    30 if tree.stage == 1 else 60
                )
                assert node.cost == (2 if tree.stage == 1 else 3)


def test_talent_purchase_applies_bonus_and_modifies_class_kit_cap():
    player = _player(Troubadour)
    initialize_progression(player)
    player.progression.level = 100
    player.progression.unspent_points = 2
    talent = next(
        node
        for node in ABILITY_TREES["Troubadour"].nodes
        if node.payload.get("talent_key") == "troubadour.resonant-finale"
    )
    before_magic = player.combat.magic
    before_cap = cap_for(player, "crescendo")

    result = purchase_node(player, talent.id)

    assert result.success
    assert has_talent(player, "troubadour.resonant-finale")
    assert player.combat.magic == before_magic + 30
    assert cap_for(player, "crescendo") == before_cap + 1
    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert has_talent(restored, "troubadour.resonant-finale")
    assert cap_for(restored, "crescendo") == before_cap + 1


@pytest.mark.parametrize("class_type", [Warrior, Mage, Footpad, Healer, Pathfinder])
def test_new_character_starts_with_one_freely_allocatable_point(class_type):
    player = _player(class_type)

    result = initialize_progression(player)

    assert result.success
    assert player.progression.unspent_points == 1
    assert player.progression.purchased_node_ids == set()
    assert player.spellbook["Skills"] == {}
    assert player.spellbook["Spells"] == {}


@pytest.mark.parametrize(
    ("class_type", "expected_roots"),
    [
        (
            Warrior,
            {
                "Piercing Strike",
                "Shield Slam",
                "Disarm",
                "Battle Cry",
                "Adrenaline",
                "Honed Attack",
                "Parry",
                "Double Strike",
            },
        ),
        (Mage, {"Firebolt", "Enfeeble", "Mana Shield", "+10 Magic Defense"}),
        (Footpad, {"Quickstep", "Disarm", "Pocket Sand", "+10 Magic"}),
        (Healer, {"Holy", "+10 Defense", "Heal", "+10 Magic Defense"}),
        (
            Pathfinder,
            {"Natural Attunement", "Tremor", "+10 Magic Defense", "Quickstep"},
        ),
    ],
)
def test_base_trees_expose_independent_first_tier_choices(
    class_type,
    expected_roots,
):
    player = _player(class_type)
    initialize_progression(player)
    roots = {
        status.node.name
        for status in available_nodes(player)
        if not status.node.prerequisites
    }

    assert roots == expected_roots


def test_pathfinder_has_no_automatic_root_and_keeps_both_styles():
    player = _player()
    initialize_progression(player)
    statuses = {status.node.name: status for status in available_nodes(player)}

    assert "Tremor" not in player.spellbook["Spells"]
    assert "Natural Attunement" not in player.spellbook["Skills"]
    for name in (
        "Tremor",
        "Water Jet",
        "Gust",
        "Scorch",
        "Quickstep",
        "Piercing Strike",
        "Parry",
        "True Strike",
    ):
        assert name in statuses
    assert statuses["Tremor"].node.lane == "Divination"
    assert statuses["Piercing Strike"].node.lane == "Huntsmanship"


def test_base_trees_use_authored_specializations_and_terminal_level_gates():
    warrior = ABILITY_TREES["Warrior"]
    by_name = {node.name: node for node in warrior.nodes}

    assert warrior.branches == (
        "Arms",
        "Vanguard",
        "Bulwark",
        "Command",
        "Independent",
    )
    expected_paths = {
        "Promote: Weapon Master": (
            "Piercing Strike",
            "Charge",
            "Weapon Focus",
            "+10 Attack",
            "Cripple",
            "True Strike",
        ),
        "Promote: Lancer": (
            "Piercing Strike",
            "Charge",
            "Weapon Focus",
            "Driving Thrust",
            "+10 Defense",
            "Retaliate",
        ),
        "Promote: Sentinel": (
            "Shield Slam",
            "Shield Block",
            "Rally",
            "+10 Defense",
            "Dishearten",
            "+25 HP",
        ),
        "Promote: Paladin": (
            "Shield Slam",
            "Shield Block",
            "Rally",
            "Goad",
            "+10 Magic Defense",
            "Chastise",
        ),
    }
    for promotion_name, path_names in expected_paths.items():
        promotion = by_name[promotion_name]
        current = promotion
        actual = []
        while current.prerequisites:
            current = next(
                node
                for node in warrior.nodes
                if node.id == current.prerequisites[0]
            )
            actual.append(current.name)
        assert tuple(reversed(actual)) == path_names
        assert promotion.cost == 2

    disarm = by_name["Disarm"]
    battle_cry = by_name["Battle Cry"]
    adrenaline = by_name["Adrenaline"]
    honed_attack = by_name["Honed Attack"]
    parry = by_name["Parry"]
    double_strike = by_name["Double Strike"]
    assert disarm.prerequisites == ()
    assert disarm.position == (4, 1)
    assert battle_cry.prerequisites == ()
    assert battle_cry.position == (4, 2)
    assert adrenaline.prerequisites == ()
    assert adrenaline.position == (4, 3)
    assert honed_attack.prerequisites == ()
    assert honed_attack.position == (4, 4)
    assert double_strike.position == (4, 5)
    assert parry.position == (4, 6)
    assert all(
        disarm.id not in node.prerequisites
        and battle_cry.id not in node.prerequisites
        for node in warrior.nodes
        if node.kind == NodeKind.PROMOTION
    )

    weapon_master = by_name["Promote: Weapon Master"]
    lancer = by_name["Promote: Lancer"]
    paladin = by_name["Promote: Paladin"]
    assert by_name["Charge"].prerequisites == (by_name["Piercing Strike"].id,)
    assert by_name["Weapon Focus"].prerequisites == (by_name["Charge"].id,)
    assert by_name["Driving Thrust"].prerequisites == (
        by_name["Weapon Focus"].id,
    )
    assert weapon_master.prerequisites == (by_name["True Strike"].id,)
    assert lancer.prerequisites == (by_name["Retaliate"].id,)
    assert paladin.prerequisites == (by_name["Chastise"].id,)
    assert by_name["Shield Block"].id in by_name["Retaliate"].prerequisites
    assert by_name["Retaliate"].payload["connector_channel_columns"] == {
        by_name["Shield Block"].id: 1.5,
    }
    sentinel_defense = next(
        node
        for node in warrior.nodes
        if node.name == "+10 Defense" and node.lane == "Bulwark"
    )
    assert by_name["Rally"].prerequisites == (by_name["Shield Block"].id,)
    assert sentinel_defense.prerequisites == (
        by_name["Rally"].id,
    )
    assert by_name["Shield Slam"].prerequisites == ()
    assert by_name["Shield Block"].prerequisites == (
        by_name["Shield Slam"].id,
    )
    assert by_name["Dishearten"].prerequisites == (sentinel_defense.id,)
    assert by_name["Goad"].prerequisites == (by_name["Rally"].id,)
    assert sentinel_defense.id not in by_name["Goad"].prerequisites
    assert by_name["Shield Slam"].position == (2.5, 1)
    assert by_name["Shield Block"].position == (2.5, 2)
    assert sentinel_defense.position == (2, 4)
    assert by_name["Goad"].position == (3, 4)
    assert by_name["Driving Thrust"].position == (1, 4)
    assert by_name["Cripple"].position == (0, 5)
    assert by_name["True Strike"].position == (0, 6)
    assert by_name["Retaliate"].position == (1, 6)
    assert by_name["Promote: Weapon Master"].payload["requirements"] == {
        "strength": 15,
        "dex": 12,
        "intel": 11,
    }
    assert by_name["Promote: Sentinel"].payload["requirements"]["con"] == 16
    assert by_name["Promote: Paladin"].payload["requirements"]["wisdom"] == 13
    expected_levels = {
        "Charge": 5,
        "Weapon Focus": 10,
        "Goad": 10,
        "Adrenaline": 10,
        "Driving Thrust": 15,
        "Dishearten": 15,
        "Honed Attack": 15,
        "Chastise": 20,
        "Cripple": 20,
        "Double Strike": 20,
        "True Strike": 25,
        "Retaliate": 25,
        "Parry": 25,
    }
    assert {
        name: by_name[name].payload["level_requirement"]
        for name in expected_levels
    } == expected_levels
    assert "level_requirement" not in by_name["Battle Cry"].payload

    development_rows = [
        node.position[1]
        for node in warrior.nodes
        if node.kind != NodeKind.PROMOTION
    ]
    for node in warrior.nodes:
        if node.kind == NodeKind.PROMOTION:
            assert node.position[1] > max(development_rows)
            assert node.payload["level_requirement"] == 30


def test_healer_upgrade_order_preserves_regen_before_heal_two():
    healer = ABILITY_TREES["Healer"]
    regen = next(node for node in healer.nodes if node.id.endswith(".regen"))
    heal_two = next(node for node in healer.nodes if node.id.endswith(".heal2"))

    assert regen.position[1] < heal_two.position[1]
    assert heal_two.prerequisites == (regen.id,)
    assert heal_two.name == "Heal II"


def test_natural_attunement_cost_duration_and_defenses():
    player = _player()
    ability = NaturalAttunement()

    result = ability.use(player)

    assert player.mana.current == 55
    assert player.stat_effects["Defense"].active
    assert player.stat_effects["Defense"].duration == 3
    assert player.stat_effects["Defense"].extra == 1
    assert player.stat_effects["Magic Defense"].active
    assert player.stat_effects["Magic Defense"].duration == 3
    assert player.stat_effects["Magic Defense"].extra == 1
    assert "Defense" in result.message


def test_weapon_focus_only_improves_weapon_accuracy():
    player = _player(Warrior)
    defender = _player(Warrior)
    random.seed(19)
    weapon_without_focus = player.hit_chance(defender, typ="weapon")
    random.seed(19)
    spell_without_focus = player.hit_chance(defender, typ="magic")

    player.spellbook["Skills"]["Weapon Focus"] = WeaponFocus()
    random.seed(19)
    weapon_with_focus = player.hit_chance(defender, typ="weapon")
    random.seed(19)
    spell_with_focus = player.hit_chance(defender, typ="magic")

    assert weapon_with_focus == pytest.approx(weapon_without_focus + 0.05)
    assert spell_with_focus == pytest.approx(spell_without_focus)


def test_dishearten_reduces_melee_damage_by_twenty_five_percent():
    user = _player(Warrior)
    target = _player(Warrior)
    before = target.check_mod("weapon")

    result = Dishearten().use(user, target)

    assert target.stat_effects["Attack"].active
    assert target.stat_effects["Attack"].duration == 3
    assert target.stat_effects["Attack"].source == "Dishearten"
    assert target.check_mod("weapon") == int(before * 0.75)
    assert "reducing their melee damage" in result.message


def test_chastise_increases_shield_slam_damage(monkeypatch):
    actor = _player(Warrior)
    target = _player(Warrior)
    actor.equipment["OffHand"] = items.Buckler()
    target.dodge_chance = lambda _actor: 0
    target.status_immunity.append("Stun")
    monkeypatch.setattr(random, "uniform", lambda _low, _high: 1.0)
    effect = ShieldSlamEffect()
    ordinary = CombatResult("Shield Slam", actor=actor, target=target)

    effect.apply(actor, target, ordinary)
    actor.spellbook["Skills"]["Chastise"] = Chastise()
    enhanced = CombatResult("Shield Slam", actor=actor, target=target)
    effect.apply(actor, target, enhanced)

    assert enhanced.damage == int(ordinary.damage * 1.25)


def test_adrenaline_only_heals_below_ten_percent_health():
    player = _player(Warrior)
    player.health.max = 100
    player.health.current = 9
    ability = Adrenaline()

    result = ability.use(player)

    assert result.healing == 20
    assert player.health.current == 29
    player.health.current = 10

    blocked = ability.use(player)

    assert blocked.healing == 0
    assert player.health.current == 10
    assert "below 10% health" in blocked.message


def test_honed_attack_increases_only_critical_bonus_damage():
    player = _player(Warrior)

    assert player._honed_attack_critical_multiplier(1.0) == 1.0
    assert player._honed_attack_critical_multiplier(1.5) == 1.5

    player.spellbook["Skills"]["Honed Attack"] = HonedAttack()

    assert player._honed_attack_critical_multiplier(1.0) == 1.0
    assert player._honed_attack_critical_multiplier(1.5) == pytest.approx(1.625)


def test_rally_cost_duration_and_refresh_without_stacking():
    player = _player(Warrior)
    ability = Rally()

    first = ability.use(player)
    second = ability.use(player)

    assert player.mana.current == 50
    assert player.stat_effects["Defense"].duration == 3
    assert player.stat_effects["Defense"].extra == 1
    assert player.stat_effects["Magic Defense"].duration == 3
    assert player.stat_effects["Magic Defense"].extra == 1
    assert "Defense" in first.message
    assert "Magic Defense" in second.message


def test_driving_thrust_uses_stunned_target_damage_multiplier(monkeypatch):
    player = _player(Warrior)
    target = _player(Warrior)
    damage_modifiers = []

    def weapon_damage(_target, **kwargs):
        damage_modifiers.append(kwargs["dmg_mod"])
        return "", True, 1

    monkeypatch.setattr(player, "weapon_damage", weapon_damage)
    ability = DrivingThrust()

    ability.use(player, target)
    target.status_effects["Stun"].active = True
    ability.use(player, target)

    assert damage_modifiers == [1.0, 1.5]
    assert player.mana.current == 46


def test_xp_curve_multi_level_points_and_level_100_cap():
    player = _player()
    initialize_progression(player)

    result = award_experience(
        player,
        cumulative_experience_for_level(4),
        rng=random.Random(7),
    )

    assert result.new_level == 4
    assert result.points_awarded == 2
    assert result.attribute_points_awarded == 1
    assert player.progression.unspent_points == 3
    assert player.progression.unspent_attribute_points == 1
    assert progression_points_through_level(1) == 1
    assert progression_points_through_level(2) == 2
    assert progression_points_through_level(3) == 2
    assert progression_points_through_level(4) == 3
    assert progression_points_through_level(100) == 51
    assert attribute_points_through_level(4) == 1
    assert attribute_points_through_level(100) == 25
    assert cumulative_experience_for_level(70) == pytest.approx(985875, abs=5)

    award_experience(
        player,
        cumulative_experience_for_level(100) * 2,
        rng=random.Random(11),
    )
    assert player.level.level == 100
    assert player.level.exp_to_gain == "MAX"
    assert experience_for_level(100) == 0


def test_promotion_combat_bonuses_scale_more_for_second_promotions():
    first = promotion_combat_bonuses(WeaponMaster())
    second = promotion_combat_bonuses(GrandmasterOfArms())

    assert first == {
        "attack": 8,
        "defense": 4,
        "magic": 0,
        "magic defense": 4,
    }
    assert second == {
        "attack": 15,
        "defense": 9,
        "magic": 0,
        "magic defense": 6,
    }


def test_odd_level_growth_does_not_award_a_progression_point():
    player = _player()
    initialize_progression(player)
    award_experience(
        player,
        cumulative_experience_for_level(2),
        rng=random.Random(3),
    )
    points_at_two = player.progression.unspent_points

    result = award_experience(
        player,
        (
            cumulative_experience_for_level(3)
            - cumulative_experience_for_level(2)
        ),
        rng=random.Random(4),
    )

    assert result.new_level == 3
    assert len(result.growth) == 1
    assert result.points_awarded == 0
    assert player.progression.unspent_points == points_at_two
    message = level_up_message(result)
    assert "No progression point awarded" in message
    assert "+0 progression" not in message


def test_attribute_and_node_purchases_are_permanent_and_outside_combat_only():
    player = _player()
    initialize_progression(player)
    player.progression.unspent_points = 2
    player.progression.unspent_attribute_points = 2
    old_strength = player.stats.strength

    result = increase_attribute(player, "strength")

    assert result.success
    assert player.stats.strength == old_strength + 1
    assert player.progression.trained_attributes == {"strength": 1}
    player.in_combat = True
    assert not increase_attribute(player, "wisdom").success
    assert not purchase_node(player, "pathfinder.ability.tremor").success


def test_warrior_rating_cross_requirement_and_promotion_point_cost():
    player = _player(Warrior)
    initialize_progression(player)
    player.progression.level = 30
    player.progression.unspent_points = 20
    old_attack = player.combat.attack

    assert purchase_node(player, "warrior.ability.piercingstrike").success
    assert purchase_node(player, "warrior.ability.charge").success
    assert purchase_node(player, "warrior.ability.weaponfocus").success
    assert purchase_node(player, "warrior.rating.attack.1").success
    assert purchase_node(player, "warrior.ability.cripple").success
    assert player.combat.attack == old_attack + 10
    assert purchase_node(player, "warrior.ability.truestrike").success
    promoted = purchase_node(
        player,
        "warrior.promotion.weapon-master",
        confirm_promotion=True,
    )

    assert promoted.success
    assert promoted.points_remaining == 12
    assert player.cls.name == "Weapon Master"


def test_race_and_staged_promotion_exclusions_are_closed():
    player = _player(Warrior)
    player.race = races_dict["Half Giant"]()
    initialize_progression(player)
    player.progression.level = 30
    player.progression.unspent_points = 20

    statuses = {
        status.node.name: status
        for status in available_nodes(player, "Warrior")
        if status.node.kind == NodeKind.PROMOTION
    }

    assert statuses["Promote: Paladin"].state == NodeState.CLOSED
    assert statuses["Promote: Lancer"].state == NodeState.CLOSED

    weapon_master = statuses["Promote: Weapon Master"].node.id
    staged = {
        status.node.name: status
        for status in available_nodes(
            player,
            "Warrior",
            planned_node_ids=(weapon_master,),
        )
        if status.node.kind == NodeKind.PROMOTION
    }

    assert staged["Promote: Weapon Master"].state == NodeState.OWNED
    assert staged["Promote: Sentinel"].state == NodeState.CLOSED
    assert "Another promotion is already distributed." in (
        staged["Promote: Sentinel"].reasons
    )


def test_human_warrior_can_reach_every_first_promotion_at_level_thirty():
    warrior = ABILITY_TREES["Warrior"]
    by_id = {node.id: node for node in warrior.nodes}
    base_stats = {
        "strength": 12,
        "intel": 10,
        "wisdom": 10,
        "con": 12,
        "charisma": 10,
        "dex": 11,
    }

    def required_nodes(node):
        result = {node.id}
        for prerequisite in node.prerequisites:
            result.update(required_nodes(by_id[prerequisite]))
        return result

    totals = {}
    for promotion in (
        node
        for node in warrior.nodes
        if node.kind == NodeKind.PROMOTION
    ):
        node_points = sum(
            by_id[node_id].cost
            for node_id in required_nodes(promotion)
        )
        stat_points = sum(
            max(0, requirement - base_stats[stat_name])
            for stat_name, requirement
            in promotion.payload["requirements"].items()
        )
        totals[promotion.payload["target_class"]] = (
            node_points,
            stat_points,
        )

        player = _player(Warrior)
        for stat_name, value in base_stats.items():
            setattr(player.stats, stat_name, value)
        initialize_progression(player)
        player.progression.level = 30
        player.progression.unspent_points = progression_points_through_level(30)
        player.progression.unspent_attribute_points = (
            attribute_points_through_level(30)
        )
        node_ids = tuple(required_nodes(promotion))
        attributes = {
            stat_name: max(
                0,
                requirement - getattr(player.stats, stat_name),
            )
            for stat_name, requirement
            in promotion.payload["requirements"].items()
        }
        attributes = {
            stat_name: amount
            for stat_name, amount in attributes.items()
            if amount
        }
        choices = (
            {promotion.id: {"vow": "Protection"}}
            if promotion.payload["target_class"] == "Paladin"
            else {}
        )
        result = apply_progression_plan(
            player,
            node_ids,
            attributes,
            promotion_choices=choices,
        )
        assert result.success
        assert player.cls.name == promotion.payload["target_class"]

    assert totals == {
        "Weapon Master": (8, 5),
        "Lancer": (10, 3),
        "Sentinel": (8, 5),
        "Paladin": (8, 5),
    }
    assert all(
        node_cost <= progression_points_through_level(30)
        and attribute_cost <= attribute_points_through_level(30)
        for node_cost, attribute_cost in totals.values()
    )


def _promotion_path_cost(tree, target_class, stats):
    by_id = {node.id: node for node in tree.nodes}
    promotion = next(
        node
        for node in tree.nodes
        if (
            node.kind == NodeKind.PROMOTION
            and node.payload["target_class"] == target_class
        )
    )

    def required_node_ids(node):
        result = {node.id}
        prerequisite_sets = [
            required_node_ids(by_id[prerequisite])
            for prerequisite in node.prerequisites
        ]
        if node.payload.get("prerequisite_mode") == "any" and prerequisite_sets:
            result.update(min(
                prerequisite_sets,
                key=lambda node_ids: sum(by_id[node_id].cost for node_id in node_ids),
            ))
        else:
            for node_ids in prerequisite_sets:
                result.update(node_ids)
        return result

    node_cost = sum(
        by_id[node_id].cost
        for node_id in required_node_ids(promotion)
    )
    trained = {
        stat_name: max(0, required - stats[stat_name])
        for stat_name, required in promotion.payload["requirements"].items()
    }
    updated = {
        stat_name: value + trained.get(stat_name, 0)
        for stat_name, value in stats.items()
    }
    target = CLASS_DETAILS[target_class][0]()
    for stat_name, bonus_name in (
        ("strength", "str_plus"),
        ("intel", "int_plus"),
        ("wisdom", "wis_plus"),
        ("con", "con_plus"),
        ("charisma", "cha_plus"),
        ("dex", "dex_plus"),
    ):
        updated[stat_name] += getattr(target, bonus_name)
    return node_cost, sum(trained.values()), updated


def _race_class_stats(race, class_name):
    job = CLASS_DETAILS[class_name][0]()
    return {
        "strength": race.strength + job.str_plus,
        "intel": race.intel + job.int_plus,
        "wisdom": race.wisdom + job.wis_plus,
        "con": race.con + job.con_plus,
        "charisma": race.charisma + job.cha_plus,
        "dex": race.dex + job.dex_plus,
    }


def test_all_eligible_races_can_reach_first_promotions_at_level_thirty():
    for base_class in ("Warrior", "Mage", "Footpad", "Healer", "Pathfinder"):
        for target_class in CLASS_CHILDREN[base_class]:
            for race_ctor in races_dict.values():
                race = race_ctor()
                if (
                    base_class not in race.cls_res.get("Base", ())
                    or target_class not in race.cls_res.get("First", ())
                ):
                    continue
                node_cost, _attribute_cost, _stats = _promotion_path_cost(
                    ABILITY_TREES[base_class],
                    target_class,
                    _race_class_stats(race, base_class),
                )
                assert node_cost <= progression_points_through_level(30), (
                    race.name,
                    base_class,
                    target_class,
                    node_cost,
                )


def test_all_eligible_races_can_reach_second_promotions_at_level_sixty():
    for base_class in ("Warrior", "Mage", "Footpad", "Healer", "Pathfinder"):
        for first_class in CLASS_CHILDREN[base_class]:
            for second_class in CLASS_CHILDREN[first_class]:
                for race_ctor in races_dict.values():
                    race = race_ctor()
                    if (
                        base_class not in race.cls_res.get("Base", ())
                        or first_class not in race.cls_res.get("First", ())
                        or second_class not in race.cls_res.get("Second", ())
                    ):
                        continue
                    first_node_cost, first_attribute_cost, stats = _promotion_path_cost(
                        ABILITY_TREES[base_class],
                        first_class,
                        _race_class_stats(race, base_class),
                    )
                    second_node_cost, second_attribute_cost, _stats = _promotion_path_cost(
                        ABILITY_TREES[first_class],
                        second_class,
                        stats,
                    )
                    total_node_cost = first_node_cost + second_node_cost
                    total_attribute_cost = (
                        first_attribute_cost + second_attribute_cost
                    )
                    assert total_node_cost <= progression_points_through_level(60), (
                        race.name,
                        first_class,
                        second_class,
                        total_node_cost,
                    )
                    if race.name == "Human":
                        assert (
                            total_attribute_cost
                            <= attribute_points_through_level(60)
                        ), (
                            race.name,
                            first_class,
                            second_class,
                            total_attribute_cost,
                        )


def test_staged_plan_uses_hypothetical_prerequisites_and_commits_atomically():
    player = _player(Warrior)
    initialize_progression(player)
    player.progression.unspent_points = 3
    player.progression.unspent_attribute_points = 1
    planned = (
        "warrior.ability.piercingstrike",
        "warrior.ability.charge",
    )
    player.progression.level = 10

    statuses = {
        status.node.id: status
        for status in available_nodes(
            player,
            planned_node_ids=planned[:1],
        )
    }

    assert statuses[planned[1]].state == NodeState.AVAILABLE
    assert player.spellbook["Skills"] == {}
    result = apply_progression_plan(
        player,
        planned,
        {"strength": 1},
    )
    assert result.success
    assert player.progression.unspent_points == 1
    assert player.progression.unspent_attribute_points == 0
    assert player.stats.strength == 31
    assert "Piercing Strike" in player.spellbook["Skills"]
    assert "Charge" in player.spellbook["Skills"]


def test_health_node_permanently_increases_maximum_and_current_hp():
    player = _player(Warrior)
    initialize_progression(player)
    player.progression.unspent_points = 5
    player.progression.level = 15
    player.progression.purchased_node_ids.update({
        "warrior.ability.shieldblock",
        "warrior.ability.shieldslam",
        "warrior.rating.defense.2",
        "warrior.ability.dishearten",
    })
    old_max = player.health.max
    old_current = player.health.current

    result = purchase_node(player, "warrior.health.25")

    assert result.success
    assert player.health.max == old_max + 25
    assert player.health.current == old_current + 25


def test_extreme_one_stat_training_has_no_cap_but_does_not_bypass_other_gates():
    player = _player(stats=10)
    initialize_progression(player)
    player.progression.unspent_attribute_points = 40

    for _ in range(40):
        assert increase_attribute(player, "strength").success

    assert player.stats.strength == 50
    assert player.progression.trained_attributes["strength"] == 40
    player.progression.unspent_points = 3
    player.progression.level = 30
    assert purchase_node(player, "pathfinder.ability.naturalattunement").success
    assert purchase_node(player, "pathfinder.rating.defense.1").success
    blocked = purchase_node(
        player,
        "pathfinder.promotion.druid",
        confirm_promotion=True,
    )
    assert not blocked.success
    assert "Intelligence 12" in blocked.message


def test_promotion_retains_abilities_does_not_reset_level_and_closes_branch():
    player = _player()
    initialize_progression(player)
    award_experience(
        player,
        cumulative_experience_for_level(30),
        rng=random.Random(3),
    )
    player.progression.unspent_points = 11
    assert purchase_node(player, "pathfinder.ability.naturalattunement").success
    assert purchase_node(player, "pathfinder.ability.quickstep").success
    assert purchase_node(player, "pathfinder.ability.piercingstrike").success
    assert purchase_node(player, "pathfinder.ability.parry").success
    assert purchase_node(player, "pathfinder.ability.truestrike").success
    preview = promotion_preview(player, "pathfinder.promotion.ranger")
    old_level = player.level.level

    result = purchase_node(
        player,
        "pathfinder.promotion.ranger",
        confirm_promotion=True,
    )

    assert preview.target_class == "Ranger"
    assert result.success
    assert player.cls.name == "Ranger"
    assert player.level.level == old_level
    assert player.level.pro_level == 2
    assert "Natural Attunement" in player.spellbook["Skills"]
    assert "Piercing Strike" in player.spellbook["Skills"]
    old_statuses = available_nodes(player, "Pathfinder")
    assert any(
        status.node.name == "Promote: Diviner" and status.state == NodeState.CLOSED
        for status in old_statuses
    )


def test_progression_save_round_trip_and_legacy_rejection():
    player = _player()
    initialize_progression(player)
    player.progression.unspent_attribute_points = 1
    assert increase_attribute(player, "dex").success
    player.spellbook["Skills"]["Adrenaline"] = Adrenaline()
    player.spellbook["Skills"]["Honed Attack"] = HonedAttack()
    serialized = PlayerDataSerializer.serialize(player)

    restored = PlayerDataSerializer.deserialize(serialized, skip_tiles=True)

    assert restored.progression.to_dict() == player.progression.to_dict()
    assert "Natural Attunement" not in restored.spellbook["Skills"]
    assert isinstance(restored.spellbook["Skills"]["Adrenaline"], Adrenaline)
    assert isinstance(
        restored.spellbook["Skills"]["Honed Attack"],
        HonedAttack,
    )
    serialized["version"] = 4
    with pytest.raises(UnsupportedSaveVersionError):
        PlayerDataSerializer.deserialize(serialized, skip_tiles=True)


def test_legacy_progression_refunds_attribute_training_node_currency():
    state = ProgressionState.from_dict({
        "level": 12,
        "unspent_points": 2,
        "trained_attributes": {"strength": 2},
    })

    assert state.unspent_points == 4
    assert state.unspent_attribute_points == 1
    assert state.trained_attributes == {"strength": 2}
