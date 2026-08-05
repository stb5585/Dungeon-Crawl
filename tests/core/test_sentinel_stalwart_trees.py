"""Focused coverage for authored Sentinel and Stalwart Defender progression."""

from __future__ import annotations

from types import SimpleNamespace

from src.core import abilities
from src.core import items
from src.core.classes import class_rings
from src.core.classes import promotion_kits
from src.core.combat.battle_engine.actions import BattleActionMixin
from src.core.data.data_driven_abilities.base import DataDrivenSpell
from src.core.progression import ABILITY_TREES
from src.core.progression import NodeKind
from src.core.progression import ProgressionState
from src.core.progression import apply_progression_plan
from src.core.progression import purchase_node
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
        for prerequisite in nodes[node_id].prerequisites:
            add(prerequisite)
        selected.append(node_id)

    add(target.id)
    return tuple(selected)


def _player(class_name: str, *, level: int = 100):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=level,
        health=(500, 500),
        mana=(200, 200),
        stats={
            "strength": 30,
            "intel": 20,
            "wisdom": 20,
            "con": 30,
            "charisma": 20,
            "dex": 20,
        },
    )
    player.progression = ProgressionState(
        level=level,
        unspent_points=100,
        unspent_attribute_points=100,
    )
    return player


def test_sentinel_tree_has_authored_paths_and_compact_geometry():
    tree = ABILITY_TREES["Sentinel"]
    nodes = _nodes("Sentinel")
    development = [
        node for node in tree.nodes if node.kind != NodeKind.PROMOTION
    ]

    assert len(development) == 15
    assert max(node.position[1] for node in tree.nodes) == 6
    assert "Shield Block" not in nodes
    assert nodes["Goad"].position == (0, 0)
    assert nodes["Shield Check"].prerequisites == (nodes["Goad"].id,)
    assert nodes["Retaliate"].payload["level_requirement"] == 40
    assert nodes["Watchful Reprisal"].position == (0, 4)
    assert nodes["Hold the Line"].position == (2, 0)
    assert nodes["Resolute Guard"].position == (2, 4)
    assert nodes["Spell Reflection"].id == (
        "sentinel.ability.deflect-spell"
    )
    assert nodes["Spell Reflection"].position == (4, 0)
    promotion = nodes["Promote: Stalwart Defender"]
    assert promotion.position == (1, 6)
    assert promotion.prerequisites == (
        nodes["Watchful Reprisal"].id,
        nodes["Resolute Guard"].id,
    )
    assert promotion.payload["requirements"] == {"con": 20}


def test_stalwart_tree_keeps_surges_out_of_progression_nodes():
    tree = ABILITY_TREES["Stalwart Defender"]
    nodes = _nodes("Stalwart Defender")

    assert len(tree.nodes) == 11
    assert max(node.position[1] for node in tree.nodes) == 3
    assert not {
        "Citadel Aegis",
        "Ironwall Reprisal",
        "Last Bastion",
    } & set(nodes)
    assert nodes["Fortified Citadel"].id == (
        "stalwart-defender.talent.fortified-citadel"
    )
    assert nodes["Crushing Reprisal"].payload["level_requirement"] == 70
    assert nodes["Final Redoubt"].payload["level_requirement"] == 80
    assert nodes["Mirror Bastion"].payload["requires_known_ability"] == (
        "Spell Reflection"
    )


def test_human_sentinel_second_promotion_uses_separate_point_pools():
    player = _player("Sentinel", level=60)
    player.stats.con = 19
    player.progression.unspent_points = 18
    player.progression.unspent_attribute_points = 15
    player.spellbook["Skills"]["Spell Reflection"] = (
        abilities.SpellReflection()
    )

    route = set(_closure("Sentinel", "Promote: Stalwart Defender"))
    result = apply_progression_plan(player, tuple(route), {"con": 1})

    assert result.success
    assert player.cls.name == "Stalwart Defender"
    assert player.progression.unspent_points == 5
    assert player.progression.unspent_attribute_points == 14
    assert "Sentinel" in player.progression.completed_trees
    assert {
        "Citadel Aegis",
        "Ironwall Reprisal",
        "Last Bastion",
    } <= set(player.spellbook["Skills"])
    assert "Spell Reflection" in player.spellbook["Skills"]
    assert "Deflect Spell" not in player.spellbook["Skills"]


def test_resolve_sources_use_one_backing_value_and_locked_gain_amounts(
    monkeypatch,
):
    player = _player("Sentinel")
    player.equipment["OffHand"] = items.KiteShield()
    player.spellbook["Skills"]["Hold the Line"] = abilities.HoldTheLine()
    engine = SimpleNamespace(
        attacker=player,
        player=player,
        defender=_player("Sentinel"),
        _event_bus=SimpleNamespace(emit=lambda *_args, **_kwargs: None),
    )

    assert "holds the line" in BattleActionMixin._execute_defend(engine)
    assert promotion_kits.current_resolve(player) == 5
    assert "already active" in BattleActionMixin._execute_defend(engine)
    assert promotion_kits.current_resolve(player) == 5

    promotion_kits.combat_state(player)["hold_the_line"] = 0
    class_rings.ensure_state(player)["data"]["Stalwart Defender"][
        "guard_meter"
    ] = 0
    assert "5 Resolve" in promotion_kits.hold_the_line(player)
    assert promotion_kits.current_resolve(player) == 5

    class_rings.ensure_state(player)["data"]["Stalwart Defender"][
        "guard_meter"
    ] = 0
    promotion_kits.record_damage_taken(player, 20, "Physical")
    assert promotion_kits.current_resolve(player) == 4
    assert "mitigated pressure" in promotion_kits.pop_messages(player)

    attacker = _player("Sentinel")
    defender = _player("Sentinel")
    attacker.equipment["Weapon"] = items.Rapier()
    defender.equipment["OffHand"] = items.KiteShield()
    monkeypatch.setattr(
        defender,
        "check_mod",
        lambda mod, **_kwargs: 50 if mod == "shield" else 0,
    )
    monkeypatch.setattr(
        "src.core.character.defense.random.random",
        lambda: 0.0,
    )
    damage, message, _absorbed = attacker._apply_absorption(
        defender,
        50,
        50,
        1.0,
        "Weapon",
        False,
        1,
    )
    assert damage == 25
    assert "blocks" in message
    assert promotion_kits.current_resolve(defender) == 5


def test_spell_reflection_spends_once_expires_and_mirror_bastion_rewards():
    player = _player("Stalwart Defender")
    player.equipment["OffHand"] = items.KiteShield()
    player.progression.purchased_node_ids.add(
        "stalwart-defender.talent.mirror-bastion"
    )
    promotion_kits.build_resolve(player, 100, "setup")

    message = abilities.SpellReflection().use(player)
    assert "spends 25 Resolve" in message
    assert player.stat_effects["Magic Defense"].active
    assert player.stat_effects["Magic Defense"].duration == 3
    assert player.stat_effects["Magic Defense"].extra == 6
    assert promotion_kits.current_resolve(player) == 75
    reflected = promotion_kits.consume_spell_reflection(player, "Firebolt")
    assert "turns Firebolt back" in reflected
    assert "Mirror Bastion" in reflected
    assert promotion_kits.current_resolve(player) == 95
    assert promotion_kits.consume_spell_reflection(player, "Shock") == ""

    promotion_kits.build_resolve(player, 5, "setup")
    abilities.SpellReflection().use(player)
    assert promotion_kits.tick_spell_reflection(player) == ""
    assert promotion_kits.tick_spell_reflection(player) == ""
    assert "expires" in promotion_kits.tick_spell_reflection(player)


def test_spell_reflection_honors_priority_compatibility_and_both_spell_paths():
    player = _player("Stalwart Defender")
    caster = _player("Paladin")
    player.equipment["OffHand"] = items.KiteShield()
    promotion_kits.build_resolve(player, 100, "setup")
    abilities.SpellReflection().use(player)

    legacy_spell = abilities.FireSpell(
        "Test Flame",
        "A focused hostile spell.",
        0,
        0.25,
        1,
    )
    player.magic_effects["Reflect"].active = True
    legacy_spell.cast(caster, player, special=True)
    assert promotion_kits.spell_reflection_ready(player)

    player.magic_effects["Reflect"].active = False
    legacy_spell.unreflectable = True
    legacy_spell.cast(caster, player, special=True)
    assert promotion_kits.spell_reflection_ready(player)

    legacy_spell.unreflectable = False
    legacy_spell.cast(caster, player, special=True)
    assert not promotion_kits.spell_reflection_ready(player)

    promotion_kits.build_resolve(player, 25, "setup")
    abilities.SpellReflection().use(player)
    data_spell = DataDrivenSpell(
        name="Test Spark",
        description="A focused hostile data-driven spell.",
        cost=0,
        dmg_mod=0.25,
        crit=1,
        subtyp="Electric",
    )
    data_spell.cast(caster, player, special=True)
    assert not promotion_kits.spell_reflection_ready(player)


def test_surge_modifiers_apply_locked_tuning(monkeypatch):
    player = _player("Stalwart Defender")
    target = _player("Sentinel")
    player.equipment["Weapon"] = items.Rapier()
    player.equipment["OffHand"] = items.KiteShield()
    target.equipment["OffHand"] = items.KiteShield()
    player.progression.purchased_node_ids.update({
        "stalwart-defender.talent.fortified-citadel",
        "stalwart-defender.talent.crushing-reprisal",
        "stalwart-defender.talent.final-redoubt",
    })
    monkeypatch.setattr(
        "src.core.character.offense.random.random",
        lambda: 0.0,
    )

    promotion_kits.build_resolve(player, 100, "setup")
    assert "Citadel Aegis" in promotion_kits.citadel_aegis(player)
    assert player.magic_effects["Nature Shield"].extra == 125
    assert player.magic_effects["Nature Shield"].duration == 4

    promotion_kits.gain_resolve_mastery(player, 8, "setup")
    promotion_kits.build_resolve(player, 100, "setup")
    assert "Crushing Reprisal" in promotion_kits.ironwall_reprisal(
        player,
        target,
    )
    assert target.stat_effects["Attack"].extra == -3
    assert target.stat_effects["Speed"].extra == -3

    player.health.current = 1
    promotion_kits.build_resolve(player, 100, "setup")
    assert "Last Bastion" in promotion_kits.last_bastion(player)
    assert player.health.current >= 1 + int(player.health.max * 0.40)
    assert player.magic_effects["Nature Shield"].extra >= 75


def test_known_sentinel_actions_are_adopted_but_leftovers_close():
    player = _player("Sentinel", level=60)
    player.spellbook["Skills"]["Goad"] = abilities.Goad()
    player.spellbook["Skills"]["Retaliate"] = abilities.Retaliate()
    from src.core.progression import ensure_progression

    ensure_progression(player)
    assert "sentinel.ability.goad" in player.progression.purchased_node_ids
    assert "sentinel.ability.retaliate" in (
        player.progression.purchased_node_ids
    )

    promotion_id = "sentinel.promotion.stalwart-defender"
    player.progression.purchased_node_ids.update(
        set(_closure("Sentinel", "Promote: Stalwart Defender")) - {promotion_id}
    )
    player.stats.con = 20
    result = purchase_node(
        player,
        promotion_id,
        confirm_promotion=True,
    )
    assert result.success
    blocked = purchase_node(player, "sentinel.ability.deflect-spell")
    assert not blocked.success
    assert "current class tree" in blocked.message


def test_legacy_reflection_node_and_deflect_skill_migrate():
    from src.core.progression import ProgressionState, ensure_progression

    state = ProgressionState.from_dict({
        "purchased_node_ids": ["sentinel.ability.spell-reflection"],
    })
    assert "sentinel.ability.spell-reflection" not in state.purchased_node_ids
    assert "sentinel.ability.deflect-spell" in state.purchased_node_ids

    player = _player("Sentinel")
    player.spellbook["Skills"] = {
        "Deflect Spell": abilities.DeflectSpell(),
    }
    ensure_progression(player)

    assert "Deflect Spell" not in player.spellbook["Skills"]
    assert isinstance(
        player.spellbook["Skills"]["Spell Reflection"],
        abilities.SpellReflection,
    )
