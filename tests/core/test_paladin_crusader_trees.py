"""Focused coverage for authored Paladin and Crusader progression."""

from __future__ import annotations

import pytest

from src.core import abilities
from src.core import enemies
from src.core import items
from src.core.classes import class_rings
from src.core.classes import paladin
from src.core.classes import promotion_kits
from src.core.combat import CombatEncounter
from src.core.combat.battle_engine.outcomes import BattleOutcomeMixin
from src.core.progression import ABILITY_TREES
from src.core.progression import NodeKind
from src.core.progression import NodeState
from src.core.progression import ProgressionState
from src.core.progression import apply_progression_plan
from src.core.progression import available_nodes
from tests.test_framework import TestGameState


def _nodes(class_name: str):
    return {node.name: node for node in ABILITY_TREES[class_name].nodes}


def _closure(class_name: str, node_name: str) -> tuple[str, ...]:
    tree = ABILITY_TREES[class_name]
    nodes = {node.id: node for node in tree.nodes}
    target = _nodes(class_name)[node_name]
    selected: list[str] = []

    def add(node_id: str) -> None:
        if node_id in selected:
            return
        prerequisites = nodes[node_id].prerequisites
        if (
            nodes[node_id].payload.get("prerequisite_mode") == "any"
            and prerequisites
        ):
            prerequisites = prerequisites[:1]
        for prerequisite in prerequisites:
            add(prerequisite)
        selected.append(node_id)

    add(target.id)
    return tuple(selected)


def _player(class_name: str, *, level: int = 100):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=level,
        health=(500, 250),
        mana=(200, 200),
        stats={
            "strength": 30,
            "intel": 20,
            "wisdom": 30,
            "con": 30,
            "charisma": 30,
            "dex": 20,
        },
    )
    player.progression = ProgressionState(
        level=level,
        unspent_points=100,
        unspent_attribute_points=100,
    )
    player.equipment["Weapon"] = items.Rapier()
    player.equipment["OffHand"] = items.KiteShield()
    return player


def test_paladin_tree_has_oath_roots_and_compact_four_branch_geometry():
    tree = ABILITY_TREES["Paladin"]
    nodes = _nodes("Paladin")
    development = [
        node for node in tree.nodes if node.kind != NodeKind.PROMOTION
    ]

    assert len(development) == 20
    assert max(node.position[1] for node in tree.nodes) == 7
    assert nodes["Oath's Judgment"].position == (1, 0)
    assert nodes["Oath's Shelter"].position == (4, 0)
    assert nodes["Oath's Judgment"].id == "paladin.ability.oath-judgment"
    assert nodes["Oath's Shelter"].id == "paladin.ability.oath-shelter"
    assert nodes["Oath's Judgment"].prerequisites == ()
    assert nodes["Oath's Shelter"].prerequisites == ()
    assert nodes["Smite"].position == (2, 1)
    assert nodes["Smite"].prerequisites == (nodes["Oath's Judgment"].id,)
    assert nodes["Repel the Wicked"].position == (2, 3)
    assert nodes["Repel the Wicked"].prerequisites == (nodes["Smite"].id,)
    assert nodes["Repel the Wicked"].payload["level_requirement"] == 40
    assert nodes["+20 Magic"].position == (2, 4)
    assert nodes["+20 Magic"].prerequisites == (
        nodes["Repel the Wicked"].id,
    )
    assert nodes["Tempered Conviction"].payload["level_requirement"] == 45
    assert nodes["Tempered Conviction"].payload["bonuses"] == {
        "ratings": {"Defense": 20},
    }
    assert nodes["Hallowed Ground"].position == (2, 6)
    assert nodes["Hallowed Ground"].payload["level_requirement"] == 55
    assert nodes["Hallowed Ground"].prerequisites == (nodes["+20 Magic"].id,)
    judgment_path = set(_closure("Paladin", "+20 Attack"))
    repel_path = set(_closure("Paladin", "Hallowed Ground"))
    assert judgment_path & repel_path == {nodes["Oath's Judgment"].id}
    assert nodes["Heal"].position == (3, 1)
    assert nodes["Heal"].prerequisites == (nodes["Oath's Shelter"].id,)
    assert nodes["+50 MP"].position == (3, 2)
    assert nodes["+50 MP"].prerequisites == (nodes["Heal"].id,)
    assert nodes["Sworn Purpose"].position == (3, 5)
    assert nodes["Blessed Light"].position == (3, 6)
    assert nodes["Blessed Light"].payload["level_requirement"] == 55
    assert nodes["Blessed Light"].prerequisites == (
        nodes["Sworn Purpose"].id,
    )
    assert nodes["Bless"].position == (5, 1)
    assert nodes["Bless"].prerequisites == (nodes["Oath's Shelter"].id,)
    assert "level_requirement" not in nodes["Bless"].payload
    assert nodes["Bless"].payload["available_on_promotion"]
    assert nodes["+20 Magic Defense"].prerequisites == ()
    assert nodes["Resist Shadow"].position == (3, 4)
    assert nodes["Resist Shadow"].payload["level_requirement"] == 45
    assert nodes["Resist Shadow"].prerequisites == ()
    assert nodes["Parry"].position == (5, 3)
    assert nodes["Parry"].prerequisites == (
        nodes["+20 Magic Defense"].id,
    )
    assert nodes["+20 Defense"].position == (5, 4)
    assert nodes["+20 Defense"].prerequisites == (
        nodes["Parry"].id,
    )
    assert nodes["Divine Protection"].position == (5, 5)
    assert nodes["Divine Protection"].payload["level_requirement"] == 50
    assert nodes["Divine Protection"].prerequisites == (
        nodes["+20 Defense"].id,
    )
    assert "+50 HP" not in nodes
    assert nodes["Sworn Purpose"].payload["level_requirement"] == 50
    assert nodes["Sworn Purpose"].payload["bonuses"] == {
        "ratings": {"Magic": 20, "Magic Defense": 20},
    }
    assert nodes["Double Strike"].position == (0, 1)
    assert nodes["Double Strike"].prerequisites == (
        nodes["Oath's Judgment"].id,
    )
    assert nodes["True Strike"].position == (0, 5)
    assert nodes["True Strike"].prerequisites == (
        nodes["Tempered Conviction"].id,
    )
    promotion = nodes["Promote: Crusader"]
    assert promotion.position == (2.5, 7)
    assert promotion.prerequisites == (
        nodes["Oath's Judgment"].id,
        nodes["Oath's Shelter"].id,
    )
    assert promotion.payload["prerequisite_mode"] == "any"
    assert promotion.payload["connector_join_at_target_row"] is True
    assert promotion.payload["requirements"] == {
        "strength": 15,
        "con": 17,
        "wisdom": 16,
        "charisma": 13,
    }


def test_crusader_tree_has_four_authored_paths_and_exclusive_melee_styles():
    tree = ABILITY_TREES["Crusader"]
    nodes = _nodes("Crusader")

    assert len(tree.nodes) == 19
    assert max(node.position[1] for node in tree.nodes) == 5
    assert tree.branches == ("Melee", "Spells", "Healing", "Protection")
    assert nodes["Condemnation"].position == (1, 0)
    assert nodes["Condemnation"].prerequisites == ()
    assert nodes["Two-Handed Weapon Proficiency"].prerequisites == (
        nodes["Condemnation"].id,
    )
    assert nodes["Sword & Board"].prerequisites == (
        nodes["Condemnation"].id,
    )
    assert (
        nodes["Two-Handed Weapon Proficiency"].payload["exclusive_group"]
        == "crusader.melee-style"
    )
    assert (
        nodes["Sword & Board"].payload["exclusive_group"]
        == "crusader.melee-style"
    )
    assert nodes["Mortal Strike"].position == (0, 3)
    assert nodes["Mortal Strike"].payload["level_requirement"] == 75
    assert nodes["Righteous Advance"].prerequisites == (
        nodes["Mortal Strike"].id,
    )
    assert nodes["True Piercing Strike"].position == (2, 2)
    assert nodes["True Piercing Strike"].payload["level_requirement"] == 70
    assert nodes["True Piercing Strike"].prerequisites == (
        nodes["Sword & Board"].id,
    )
    assert nodes["Triple Strike"].position == (2, 5)
    assert nodes["Triple Strike"].payload["level_requirement"] == 85
    assert nodes["Triple Strike"].prerequisites == (
        nodes["True Piercing Strike"].id,
    )
    assert nodes["Parry"].prerequisites == (
        nodes["Consecrated Bulwark"].id,
    )
    assert nodes["Posturing"].prerequisites == (nodes["Parry"].id,)
    assert nodes["Smite II"].prerequisites == ()
    assert nodes["Repel the Wicked"].position == (3, 1)
    assert nodes["Repel the Wicked"].prerequisites == (
        nodes["Smite II"].id,
    )
    assert nodes["Repel the Wicked"].payload["owned_if_known"] is True
    assert nodes["Smite III"].prerequisites == (nodes["Smite II"].id,)
    assert nodes["Heal II"].prerequisites == ()
    assert nodes["Cleanse"].prerequisites == (nodes["Heal II"].id,)
    assert "Turn Undead II" not in nodes
    assert "True Strike" not in nodes


def test_known_gated_abilities_adopt_only_their_matching_nodes():
    player = _player("Paladin")
    player.spellbook["Skills"]["Double Strike"] = abilities.DoubleStrike()
    player.spellbook["Skills"]["True Strike"] = abilities.TrueStrike()

    statuses = {
        status.node.name: status
        for status in available_nodes(player, "Paladin")
    }

    assert statuses["Double Strike"].state == NodeState.OWNED
    assert statuses["True Strike"].state == NodeState.OWNED
    assert statuses["Oath's Judgment"].state == NodeState.AVAILABLE
    assert statuses["Tempered Conviction"].state != NodeState.OWNED
    assert player.progression.purchased_node_ids == {
        "paladin.ability.double-strike",
        "paladin.ability.true-strike",
    }


def test_legacy_recursive_paladin_adoption_is_repaired_on_load():
    player = _player("Paladin")
    player.spellbook["Skills"]["True Strike"] = abilities.TrueStrike()
    player.progression.purchased_node_ids.update({
        "paladin.ability.oath-judgment",
        "paladin.ability.double-strike",
        "paladin.rating.attack-1",
        "paladin.talent.tempered-conviction",
        "paladin.ability.true-strike",
    })

    statuses = {
        status.node.name: status
        for status in available_nodes(player, "Paladin")
    }

    assert statuses["Oath's Judgment"].state == NodeState.AVAILABLE
    assert statuses["Double Strike"].state != NodeState.OWNED
    assert statuses["True Strike"].state == NodeState.OWNED
    assert player.progression.purchased_node_ids == {
        "paladin.ability.true-strike",
    }


def test_inherited_repel_adopts_without_owning_crusader_smite_path():
    player = _player("Crusader")
    player.spellbook["Spells"]["Repel the Wicked"] = (
        abilities.RepelTheWicked()
    )

    statuses = {
        status.node.name: status
        for status in available_nodes(player, "Crusader")
    }

    assert statuses["Repel the Wicked"].state == NodeState.OWNED
    assert statuses["Smite II"].state == NodeState.AVAILABLE
    assert "crusader.ability.smite-2" not in (
        player.progression.purchased_node_ids
    )


def test_crusader_melee_style_choice_permanently_closes_the_other_style():
    player = _player("Crusader")

    assert apply_progression_plan(
        player,
        (
            "crusader.ability.condemnation",
            "crusader.ability.two-handed-proficiency",
        ),
        {},
    ).success

    blocked = apply_progression_plan(
        player,
        ("crusader.ability.sword-and-board",),
        {},
    )

    assert not blocked.success
    assert "permanently closed this style path" in blocked.message


def test_paladin_mana_and_sworn_purpose_nodes_apply_both_support_bonuses():
    player = _player("Paladin")
    old_mana = (player.mana.current, player.mana.max)
    old_magic = player.combat.magic
    old_magic_defense = player.combat.magic_def

    assert apply_progression_plan(
        player,
        (
            "paladin.ability.heal",
            "paladin.mana.mana-1",
            "paladin.ability.oath-shelter",
            "paladin.talent.sworn-purpose",
        ),
        {},
    ).success

    assert (player.mana.current, player.mana.max) == (
        old_mana[0] + 50,
        old_mana[1] + 50,
    )
    assert player.combat.magic == old_magic + 20
    assert player.combat.magic_def == old_magic_defense + 20


def test_hallowed_ground_damages_and_heals_for_three_turns(monkeypatch):
    player = _player("Paladin")
    target = _player("Sentinel")
    nearby_target = _player("Berserker")
    player.health.current = 200
    player.mana.current = 100
    target.health.current = 500
    nearby_target.health.current = 500
    monkeypatch.setattr(
        "src.core.character.status.random.randint",
        lambda *_args: 0,
    )

    message = abilities.HallowedGround().cast(
        player,
        target,
        targets=(nearby_target,),
    )

    assert "hallows the ground" in message
    assert player.mana.current == 80
    assert player.magic_effects["Hallowed Ground"].duration == 3
    assert target.magic_effects["Hallowed Ground"].duration == 3
    assert nearby_target.magic_effects["Hallowed Ground"].duration == 3
    for _turn in range(3):
        player.effects()
        target.effects()
        nearby_target.effects()

    assert player.health.current > 200
    assert target.health.current < 500
    assert nearby_target.health.current < 500
    assert not player.magic_effects["Hallowed Ground"].active
    assert not target.magic_effects["Hallowed Ground"].active
    assert not nearby_target.magic_effects["Hallowed Ground"].active


def test_resist_shadow_uses_exploration_time_and_expires_after_100_steps():
    player = _player("Paladin")
    player.mana.current = 100
    baseline = player.check_mod("resist", typ="Shadow")
    spell = abilities.ResistShadow()

    assert "outside battle" in spell.cast(player)
    assert spell.cast_out(player).endswith("game time.\n")
    assert player.mana.current == 85
    assert player.temporary_exploration_effects["resist_shadow"] == 100
    assert player.check_mod("resist", typ="Shadow") == pytest.approx(
        baseline + 0.5,
    )

    player.effects(end=True)
    assert player.magic_effects["Resist Shadow"].active
    player.record_step(99)
    assert player.magic_effects["Resist Shadow"].active
    player.record_step()
    assert not player.magic_effects["Resist Shadow"].active
    assert player.check_mod("resist", typ="Shadow") == pytest.approx(baseline)


def test_blessed_light_triggers_only_from_successful_combat_healing():
    player = _player("Paladin")
    player.spellbook["Skills"]["Blessed Light"] = abilities.BlessedLight()
    player.spellbook["Spells"]["Heal"] = abilities.Heal()
    player.health.current = 100
    player._active_combat = True
    player.spellbook["Spells"]["Heal"].cast(player)

    attack = player.stat_effects["Attack"]
    assert attack.active
    assert attack.duration == 3
    assert attack.extra == 10
    assert attack.source == "Blessed Light"

    attack.duration = 1
    player.health.current = 100
    player.spellbook["Spells"]["Heal"].cast(player)
    assert attack.duration == 3
    player.effects(end=True)
    player._active_combat = True
    player.health.current = player.health.max
    player.spellbook["Spells"]["Heal"].cast(player)
    assert not player.stat_effects["Attack"].active
    player._active_combat = False
    player.health.current = 100
    player.spellbook["Spells"]["Heal"].cast(player)
    assert not player.stat_effects["Attack"].active


def test_human_paladin_second_promotion_uses_separate_point_pools():
    player = _player("Paladin", level=60)
    player.stats.strength = 13
    player.stats.con = 16
    player.stats.wisdom = 15
    player.stats.charisma = 11
    player.progression.unspent_points = 18
    player.progression.unspent_attribute_points = 15
    player.choose_paladin_vow("Protection")

    route = set(_closure("Paladin", "Promote: Crusader"))
    result = apply_progression_plan(
        player,
        tuple(route),
        {
            "strength": 2,
            "con": 1,
            "wisdom": 1,
            "charisma": 2,
        },
    )

    assert result.success
    assert player.cls.name == "Crusader"
    assert player.progression.unspent_points == 14
    assert player.progression.unspent_attribute_points == 9
    assert "Paladin" in player.progression.completed_trees


def test_tempered_conviction_produces_effective_caps_three_and_four():
    paladin_player = _player("Paladin")
    crusader = _player("Crusader")
    for player in (paladin_player, crusader):
        player.progression.purchased_node_ids.add(
            "paladin.talent.tempered-conviction"
        )

    assert promotion_kits.cap_for(
        paladin_player,
        "oath_conviction",
    ) == 3
    assert promotion_kits.cap_for(crusader, "oath_conviction") == 4


def test_signature_vow_actions_generate_basic_and_clean_conviction():
    redemption = _player("Paladin")
    redemption.choose_paladin_vow("Redemption")
    target = _player("Sentinel")
    message = paladin.attempt_redeem(
        redemption,
        target,
        rng=type("FixedRng", (), {"random": staticmethod(lambda: 0.0)})(),
    )
    assert "yields to mercy" in message
    assert promotion_kits.combat_state(redemption)["oath_conviction"] == 2

    conquest = _player("Paladin")
    conquest.choose_paladin_vow("Conquest")
    foe = _player("Sentinel")
    paladin.start_challenge(conquest, foe)
    assert promotion_kits.combat_state(conquest)["oath_conviction"] == 1
    paladin.on_enemy_defeated(conquest, foe)
    assert promotion_kits.combat_state(conquest)["oath_conviction"] == 2

    protection = _player("Paladin")
    protection.choose_paladin_vow("Protection")
    paladin.start_interpose(protection)
    paladin.block_succeeded(protection)
    assert promotion_kits.combat_state(protection)["oath_conviction"] == 2

    retribution = _player("Paladin")
    retribution.choose_paladin_vow("Retribution")
    paladin.start_riposte(retribution)
    paladin.resolve_riposte(retribution, _player("Sentinel"))
    assert promotion_kits.combat_state(retribution)["oath_conviction"] == 2


def test_eligible_redeem_refusal_still_grants_one_conviction():
    player = _player("Paladin")
    target = _player("Sentinel")
    player.choose_paladin_vow("Redemption")

    message = paladin.attempt_redeem(
        player,
        target,
        rng=type("FixedRng", (), {"random": staticmethod(lambda: 1.0)})(),
    )

    assert "rejects mercy" in message
    assert promotion_kits.combat_state(player)["oath_conviction"] == 1
    assert "even if the foe refuses" in paladin.SIGNATURE_DESCRIPTIONS[
        "Redemption"
    ]


def test_condemnation_marks_wicked_targets_for_repel_disintegration(
    monkeypatch,
):
    player = _player("Crusader")
    target = enemies.Skeleton()
    target.health.current = target.health.max = 100
    monkeypatch.setattr(
        player,
        "weapon_damage",
        lambda *_args, **_kwargs: ("Weapon hit.\n", True, False),
    )

    condemn_message = abilities.Condemnation().use(
        player,
        target,
        rng=type("FixedRng", (), {"random": staticmethod(lambda: 0.0)})(),
    )
    repel_message = abilities.RepelTheWicked().cast(
        player,
        target,
        rng=type("FixedRng", (), {"random": staticmethod(lambda: 0.0)})(),
    )

    assert "marked by Condemnation" in condemn_message
    assert target.condemned_by_crusader
    assert "disintegrates" in repel_message
    assert target.paladin_disintegrated
    assert not getattr(target, "paladin_repelled", False)
    assert not target.is_alive()


def test_repel_the_wicked_can_end_combat_without_victory_rewards():
    player = _player("Paladin")
    target = enemies.Skeleton()
    player_exp = player.level.exp
    player.choose_paladin_vow("Protection")

    message = abilities.RepelTheWicked().cast(
        player,
        target,
        rng=type("FixedRng", (), {"random": staticmethod(lambda: 0.0)})(),
    )
    engine = BattleOutcomeMixin()
    engine.player = player
    engine.encounter = CombatEncounter.singleton(target)
    engine.summon = None
    outcome = engine._process_victory()

    assert "flees from the sacred force" in message
    assert target.paladin_repelled
    assert "flees from the battle" in outcome
    assert player.level.exp == player_exp
    assert target.name not in player.kill_dict.get(target.enemy_typ, {})


def test_sword_and_board_requires_one_handed_weapon_and_shield():
    player = _player("Crusader")
    player.spellbook["Skills"]["Sword & Board"] = abilities.SwordAndBoard()

    assert paladin.sword_and_board_accuracy_bonus(player) == pytest.approx(
        0.10
    )
    assert paladin.sword_and_board_damage_multiplier(player) == pytest.approx(
        1.10
    )

    player.equipment["OffHand"] = items.NoOffHand()
    assert paladin.sword_and_board_accuracy_bonus(player) == 0.0
    assert paladin.sword_and_board_damage_multiplier(player) == 1.0


@pytest.mark.parametrize(
    "vow",
    paladin.PATHS,
)
def test_signature_actions_build_and_judgment_spends_for_each_vow(
    vow,
    monkeypatch,
):
    player = _player("Paladin")
    target = _player("Sentinel")
    player.choose_paladin_vow(vow)
    player.progression.purchased_node_ids.add(
        "paladin.talent.tempered-conviction"
    )
    monkeypatch.setattr(
        "src.core.character.offense.random.random",
        lambda: 0.0,
    )

    promotion_kits.conviction_action(player, paladin.SKILL_NAMES[vow])
    promotion_kits.conviction_action(player, "clean outcome", clean=True)
    assert promotion_kits.combat_state(player)["oath_conviction"] == 2
    message = abilities.OathsJudgment().use(player, target)

    assert "spends 2 Oath Conviction" in message
    assert promotion_kits.combat_state(player)["oath_conviction"] == 0
    if vow == "Protection":
        assert player.magic_effects["Nature Shield"].extra >= 20
        assert target.stat_effects["Attack"].extra <= -4
    elif vow == "Retribution":
        assert promotion_kits.combat_state(player)[
            "oath_judgment_counter"
        ] is not None
    elif vow == "Redemption":
        assert player.health.current > 250


@pytest.mark.parametrize(
    "vow",
    paladin.PATHS,
)
def test_shelter_has_distinct_vow_effects(vow):
    player = _player("Crusader")
    player.choose_paladin_vow(vow)
    player.progression.purchased_node_ids.update({
        "paladin.talent.tempered-conviction",
        "crusader.talent.consecrated-bulwark",
    })
    promotion_kits.combat_state(player)["oath_conviction"] = 2

    message = abilities.OathsShelter().use(player)

    assert "spends 2 Oath Conviction" in message
    if vow == "Redemption":
        assert player.health.current > 250
    elif vow == "Conquest":
        assert player.stat_effects["Attack"].extra >= 8
        assert player.stat_effects["Speed"].duration == 3
    elif vow == "Protection":
        guard = promotion_kits.combat_state(player)["oath_protection_guard"]
        assert guard["turns"] == 3
        assert player.magic_effects["Nature Shield"].extra >= 38
    else:
        shelter = promotion_kits.combat_state(player)[
            "oath_retribution_shelter"
        ]
        assert shelter["turns"] == 3
        assert shelter["reduction"] == pytest.approx(0.20)


def test_judgment_validates_before_spend_and_miss_still_consumes(monkeypatch):
    player = _player("Paladin")
    target = _player("Sentinel")
    player.choose_paladin_vow("Conquest")
    state = promotion_kits.combat_state(player)
    state["oath_conviction"] = 2

    player.equipment["Weapon"] = None
    assert "required" in abilities.OathsJudgment().use(player, target)
    assert state["oath_conviction"] == 2

    player.equipment["Weapon"] = items.Rapier()
    monkeypatch.setattr(player, "hit_chance", lambda *_args, **_kwargs: 0.0)
    monkeypatch.setattr(target, "dodge_chance", lambda *_args, **_kwargs: 0.0)
    monkeypatch.setattr(
        "src.core.character.offense.random.random",
        lambda: 0.5,
    )
    message = abilities.OathsJudgment().use(player, target)
    assert "misses" in message
    assert state["oath_conviction"] == 0


def test_vow_affirmation_preserves_once_and_invalid_or_death_state_clears():
    player = _player("Crusader")
    player.choose_paladin_vow("Conquest")
    player.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(player)["awakened"]["Crusader"] = True
    state = promotion_kits.combat_state(player)
    state["oath_conviction"] = 2

    assert "preserves 1" in abilities.OathsShelter().use(player)
    assert state["oath_conviction"] == 1
    state["oath_conviction"] = 2
    assert "preserves 1" not in abilities.OathsShelter().use(player)
    assert state["oath_conviction"] == 0

    state["oath_conviction"] = 2
    state["oath_judgment_counter"] = {"turns": 2}
    player.paladin_vow = {"path": "invalid"}
    assert paladin.path(player) is None
    assert state["oath_conviction"] == 0
    assert state["oath_judgment_counter"] is None

    player.choose_paladin_vow("Protection")
    state["oath_conviction"] = 2
    state["oath_protection_guard"] = {"turns": 2}
    player.health.current = 0
    promotion_kits.record_damage_taken(player, 10, "Physical")
    assert state["oath_conviction"] == 0
    assert state["oath_protection_guard"] is None


def test_crusader_upgrades_replace_inherited_spells():
    player = _player("Crusader")
    player.spellbook["Spells"]["Smite"] = abilities.Smite()
    player.spellbook["Spells"]["Heal"] = abilities.Heal()
    player.spellbook["Spells"]["Repel the Wicked"] = (
        abilities.RepelTheWicked()
    )

    assert apply_progression_plan(
        player,
        (
            "crusader.ability.smite-2",
            "crusader.ability.heal-2",
            "crusader.ability.smite-3",
        ),
        {},
    ).success
    assert player.spellbook["Spells"]["Smite"].cost == 32
    assert player.spellbook["Spells"]["Heal"].cost == 12
    assert player.spellbook["Spells"]["Repel the Wicked"].cost == 12
