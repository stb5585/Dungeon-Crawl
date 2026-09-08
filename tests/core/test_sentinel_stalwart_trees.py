"""Focused coverage for authored Sentinel and Stalwart Defender progression."""

from __future__ import annotations

from types import SimpleNamespace

from src.core import abilities, items
from src.core.abilities.descriptions import presented_abilities
from src.core.classes import ability_mechanics, class_rings, promotion_kits
from src.core.combat.battle_engine.actions import BattleActionMixin
from src.core.progression import (
    ABILITY_TREES,
    NodeKind,
    ProgressionState,
    apply_progression_plan,
    purchase_node,
)
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


def _complete_mastery(player, *mastery_keys: str) -> None:
    mastery = class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"]
    for mastery_key in mastery_keys:
        mastery[mastery_key] = 4


def test_sentinel_tree_has_authored_paths_and_compact_geometry():
    tree = ABILITY_TREES["Sentinel"]
    nodes = _nodes("Sentinel")
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]

    assert len(development) == 24
    assert max(node.position[1] for node in tree.nodes) == 7
    assert "Shield Check" not in nodes
    assert nodes["Retaliate"].position == (0, 0)
    assert nodes["Swing & Bash"].position == (0, 1)
    assert nodes["Focused Assault"].position == (0, 3)
    assert nodes["Repercussion"].position == (0, 4)
    assert nodes["Watchful Reprisal"].position == (0, 5)
    assert nodes["Hold the Line"].position == (1, 0)
    assert nodes["Shield Riposte"].position == (1, 1)
    assert nodes["Resolute Guard"].position == (1, 5)
    assert nodes["Adrenaline"].position == (2.5, 0)
    assert nodes["Spell Block"].position == (2, 1)
    assert nodes["Spell Reflection"].position == (2, 4)
    assert nodes["Purge Weakness"].position == (3, 1)
    assert nodes["Boast"].position == (3, 3)
    assert "Parry" not in nodes
    assert nodes["Goad"].position == (4, 1)
    assert nodes["Charge"].position == (4, 2)
    assert nodes["Double Strike"].position == (4, 3)
    assert nodes["Charge"].prerequisites == ()
    assert nodes["Double Strike"].prerequisites == ()
    promotion = nodes["Promote: Stalwart Defender"]
    assert promotion.position == (1.5, 7)
    assert promotion.prerequisites == (
        nodes["Watchful Reprisal"].id,
        nodes["Resolute Guard"].id,
        nodes["Shielding Ward"].id,
        nodes["Braggadocious"].id,
    )
    assert promotion.payload["prerequisite_mode"] == "any"
    assert promotion.payload["requirements"] == {"con": 20}


def test_stalwart_tree_keeps_surges_out_of_progression_nodes():
    tree = ABILITY_TREES["Stalwart Defender"]
    nodes = _nodes("Stalwart Defender")

    assert len(tree.nodes) == 25
    assert max(node.position[1] for node in tree.nodes) == 6
    assert max(node.position[0] for node in tree.nodes) == 4
    assert not {
        "Citadel Aegis",
        "Ironwall Revenge",
        "Last Bastion",
        "Stronghold",
    } & set(nodes)
    assert nodes["Fortified Citadel"].id == ("stalwart-defender.talent.fortified-citadel")
    assert nodes["Punishing Guard"].payload["level_requirement"] == 70
    assert nodes["Crushing Vengeance"].payload["level_requirement"] == 75
    assert nodes["Double Payback"].payload["level_requirement"] == 80
    assert nodes["Final Redoubt"].payload["level_requirement"] == 80
    assert nodes["Mirror Bastion"].payload["level_requirement"] == 75
    assert nodes["Focused Assault"].prerequisites == (nodes["Repercussion"].id,)
    assert nodes["Brace Wall"].prerequisites == (nodes["Hold the Line"].id,)
    assert nodes["Bulwark Guard"].prerequisites == (nodes["Spell Block"].id,)
    assert nodes["Spell Reflection"].prerequisites == (nodes["Bulwark Guard"].id,)
    assert nodes["Boast"].prerequisites == (nodes["Purge Weakness"].id,)
    assert nodes["Punishing Guard"].cost == 2
    assert nodes["Double Payback"].cost == 2
    assert nodes["Unbroken Wall"].cost == 2
    assert nodes["Iron Maiden"].cost == 2
    assert nodes["Fortified Citadel"].cost == 2
    assert nodes["Final Redoubt"].cost == 2
    assert nodes["Repercussion"].position == (0, 1)
    assert "Defense" not in nodes
    assert "Health" not in nodes
    assert nodes["Iron Maiden"].position == (1, 6)
    assert nodes["Retaliate"].position == (2, 1)
    assert nodes["Retaliate"].prerequisites == ()
    assert "level_requirement" not in nodes["Retaliate"].payload
    assert nodes["Shield Ricochet"].position == (2, 2)
    assert nodes["Shield Ricochet"].payload["level_requirement"] == 65
    assert nodes["Tower Offense"].position == (2, 3)
    assert nodes["Tower Offense"].payload["level_requirement"] == 70
    assert nodes["Get Even"].position == (2, 4)
    assert nodes["Get Even"].payload["level_requirement"] == 75
    assert nodes["Generator Shield"].position == (2, 5)
    assert nodes["Generator Shield"].payload["level_requirement"] == 80
    assert nodes["Fortified Citadel"].position == (3, 5)
    assert nodes["Battle Cry"].position == (4, 3)
    assert nodes["Battle Cry"].payload["level_requirement"] == 70
    assert nodes["Battle Determination"].position == (4, 4)
    assert nodes["Battle Determination"].payload["level_requirement"] == 75
    assert nodes["Final Redoubt"].position == (4, 5)


def test_stalwart_bursts_are_hidden_from_ordinary_specials():
    player = _player("Stalwart Defender")
    for ability_type in (
        abilities.CitadelAegis,
        abilities.IronwallReprisal,
        abilities.LastBastionSurge,
        abilities.Stronghold,
    ):
        ability = ability_type()
        player.spellbook["Skills"][ability.name] = ability

    assert {ability.name for ability in presented_abilities(player, "Skills")}.isdisjoint(
        {
            "Citadel Aegis",
            "Ironwall Revenge",
            "Last Bastion",
            "Stronghold",
        }
    )


def test_human_sentinel_second_promotion_uses_separate_point_pools():
    player = _player("Sentinel", level=60)
    player.stats.con = 19
    player.progression.unspent_points = 18
    player.progression.unspent_attribute_points = 15
    player.spellbook["Skills"]["Spell Reflection"] = abilities.SpellReflection()
    for index in range(3):
        promotion_kits.begin_action(player, action=f"training-{index}")
        promotion_kits.record_resolve_mastery(
            player,
            "ironwall_revenge",
            "Retaliate",
            action_deduplicated=True,
        )

    route = set(_closure("Sentinel", "Watchful Reprisal"))
    route.add(_nodes("Sentinel")["Promote: Stalwart Defender"].id)
    result = apply_progression_plan(player, tuple(route), {"con": 1})

    assert result.success
    assert player.cls.name == "Stalwart Defender"
    assert player.progression.unspent_points == 9
    assert player.progression.unspent_attribute_points == 14
    assert "Sentinel" in player.progression.completed_trees
    assert {
        "Citadel Aegis",
        "Ironwall Revenge",
        "Last Bastion",
        "Stronghold",
    } <= set(player.spellbook["Skills"])
    assert "Spell Reflection" in player.spellbook["Skills"]
    assert "Deflect Spell" not in player.spellbook["Skills"]
    rows = {row["mastery_key"]: row for row in promotion_kits.resolve_surge_rows(player)}
    assert rows["ironwall_revenge"]["progress"] == 3
    assert not rows["ironwall_revenge"]["learned"]


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
    mastery = class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"]
    assert mastery["citadel_aegis"] == 1
    assert mastery["stronghold"] == 1
    assert "already active" in BattleActionMixin._execute_defend(engine)
    assert promotion_kits.current_resolve(player) == 5

    promotion_kits.combat_state(player)["hold_the_line"] = 0
    class_rings.ensure_state(player)["data"]["Stalwart Defender"]["guard_meter"] = 0
    assert "5 Resolve" in promotion_kits.hold_the_line(player)
    assert promotion_kits.current_resolve(player) == 5

    class_rings.ensure_state(player)["data"]["Stalwart Defender"]["guard_meter"] = 0
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

    monkeypatch.setattr(
        defender,
        "check_mod",
        lambda mod, **_kwargs: 200 if mod == "shield" else 0,
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
    assert damage == 0
    assert "defensive mastery deepens" in message
    assert (
        class_rings.ensure_state(defender)["data"]["Stalwart Defender"]["resolve_mastery"][
            "stronghold"
        ]
        == 1
    )


def test_resolve_mastery_tracks_associated_successes_and_deduplicates_actions():
    player = _player("Sentinel")
    player.equipment["OffHand"] = items.KiteShield()

    promotion_kits.begin_action(player, action="training")
    first = promotion_kits.record_resolve_mastery(
        player,
        "citadel_aegis",
        "Brace Wall",
        action_deduplicated=True,
    )
    duplicate = promotion_kits.record_resolve_mastery(
        player,
        "citadel_aegis",
        "Brace Wall",
        action_deduplicated=True,
    )
    separate = promotion_kits.record_resolve_mastery(
        player,
        "stronghold",
        "Defend",
        action_deduplicated=True,
    )

    assert "defensive mastery deepens" in first
    assert "/4" not in first
    assert duplicate == ""
    assert "defensive mastery deepens" in separate
    assert "/4" not in separate
    assert promotion_kits.build_resolve(player, 10, "unrelated pressure")
    rows = {row["mastery_key"]: row for row in promotion_kits.resolve_surge_rows(player)}
    assert rows["citadel_aegis"]["progress"] == 1
    assert rows["stronghold"]["progress"] == 1
    assert rows["ironwall_revenge"]["progress"] == 0
    assert rows["last_bastion"]["progress"] == 0
    assert not any(row["unlocked"] for row in rows.values())


def test_resolve_mastery_caps_at_four_and_requires_stalwart_for_surge():
    player = _player("Sentinel")
    messages = []
    for index in range(5):
        promotion_kits.begin_action(player, action=f"boast-{index}")
        message = promotion_kits.record_resolve_mastery(
            player,
            "last_bastion",
            "Boast",
            action_deduplicated=True,
        )
        messages.append(message)

    assert message == ""
    assert all("Last Bastion" not in progress for progress in messages[:3])
    assert "discovers Last Bastion" in messages[3]
    rows = {row["mastery_key"]: row for row in promotion_kits.resolve_surge_rows(player)}
    assert rows["last_bastion"]["progress"] == 4
    assert rows["last_bastion"]["learned"]
    assert not rows["last_bastion"]["unlocked"]
    assert not promotion_kits.resolve_surge_unlocked(player, "Last Bastion")

    player.cls = SimpleNamespace(name="Stalwart Defender")
    assert promotion_kits.resolve_surge_unlocked(player, "Last Bastion")

    player.cls = SimpleNamespace(name="Warrior")
    assert (
        promotion_kits.record_resolve_mastery(
            player,
            "last_bastion",
            "Boast",
        )
        == ""
    )
    assert (
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"][
            "last_bastion"
        ]
        == 4
    )


def test_resolve_active_sources_advance_only_after_successful_validation():
    player = _player("Stalwart Defender")
    player.equipment["OffHand"] = items.KiteShield()
    target = _player("Warrior")

    promotion_kits.begin_action(player, action="Brace Wall")
    assert "requires 15 Resolve" in promotion_kits.brace_wall(player)
    rows = {row["mastery_key"]: row for row in promotion_kits.resolve_surge_rows(player)}
    assert rows["citadel_aegis"]["progress"] == 0

    class_rings.ensure_state(player)["data"]["Stalwart Defender"]["guard_meter"] = 30
    promotion_kits.begin_action(player, action="Repercussion")
    empty_group = promotion_kits.repercussion(
        player,
        [],
        battle_engine=SimpleNamespace(current_actor_id="player"),
    )
    assert "no targets" in empty_group.results[0].message
    assert promotion_kits.current_resolve(player) == 30
    assert (
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"][
            "ironwall_revenge"
        ]
        == 0
    )

    actions = (
        ("Brace Wall", 15, promotion_kits.brace_wall, "citadel_aegis"),
        ("Bulwark Guard", 25, promotion_kits.bulwark_guard, "citadel_aegis"),
        ("Purge Weakness", 40, promotion_kits.purge_weakness, "last_bastion"),
        ("Boast", 20, promotion_kits.boast, "last_bastion"),
        ("Focused Assault", 15, promotion_kits.focused_assault, "ironwall_revenge"),
    )
    expected = {
        key: 0
        for key in (
            "citadel_aegis",
            "ironwall_revenge",
            "last_bastion",
            "stronghold",
        )
    }
    for name, resolve, action, mastery_key in actions:
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["guard_meter"] = resolve
        promotion_kits.begin_action(player, action=name)
        assert "spends" in action(player)
        expected[mastery_key] += 1
        mastery = class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"]
        assert mastery == expected

    class_rings.ensure_state(player)["data"]["Stalwart Defender"]["guard_meter"] = 30
    promotion_kits.begin_action(player, action="Repercussion")
    group = promotion_kits.repercussion(
        player,
        [("target", target)],
        battle_engine=SimpleNamespace(current_actor_id="player"),
    )
    assert "defensive mastery deepens" in group.results[0].message
    assert (
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"][
            "ironwall_revenge"
        ]
        == 2
    )

    player.spellbook["Skills"]["Retaliate"] = abilities.Retaliate()
    player.weapon_damage = lambda *_args, **_kwargs: ("Counter misses.\n", False, 0)
    missed = ability_mechanics.retaliate_after_block(
        player,
        target,
        rng=SimpleNamespace(random=lambda: 0.0),
    )
    assert "defensive mastery deepens" not in missed
    assert (
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"][
            "ironwall_revenge"
        ]
        == 2
    )

    player.weapon_damage = lambda *_args, **_kwargs: ("Counter lands.\n", True, 1)
    message = ability_mechanics.retaliate_after_block(
        player,
        target,
        rng=SimpleNamespace(random=lambda: 0.0),
    )
    assert "defensive mastery deepens" in message
    assert (
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"][
            "ironwall_revenge"
        ]
        == 3
    )


def test_spell_block_spends_once_and_reflection_modifies_it(monkeypatch):
    player = _player("Stalwart Defender")
    caster = _player("Paladin")
    player.equipment["OffHand"] = items.KiteShield()
    player.spellbook["Skills"]["Spell Reflection"] = abilities.SpellReflection()
    player.progression.purchased_node_ids.add("stalwart-defender.talent.mirror-bastion")
    promotion_kits.build_resolve(player, 100, "setup")
    _complete_mastery(player, "citadel_aegis")
    monkeypatch.setattr(
        "src.core.classes.promotion_kits.resolve.random.random",
        lambda: 0.0,
    )

    message = abilities.SpellBlock().use(player)
    assert "prepares to block" in message
    assert promotion_kits.current_resolve(player) == 75
    spell = SimpleNamespace(cost=10, subtyp="Fire", reflectable=True)
    caster_before = caster.health.current
    remaining, block_message = promotion_kits.apply_spell_block(
        player,
        caster,
        100,
        spell=spell,
    )
    assert remaining < 100
    assert "Spell Block" in block_message
    assert "Spell Reflection" in block_message
    assert "defensive mastery deepens" in block_message
    assert caster.health.current < caster_before
    assert player.stat_effects["Magic Defense"].extra == 50
    assert not promotion_kits.spell_block_ready(player)
    assert (
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"][
            "stronghold"
        ]
        == 1
    )


def test_spell_block_honors_projectile_compatibility_and_expires():
    player = _player("Stalwart Defender")
    caster = _player("Paladin")
    player.equipment["OffHand"] = items.KiteShield()
    promotion_kits.build_resolve(player, 100, "setup")
    abilities.SpellBlock().use(player)
    area_spell = SimpleNamespace(
        cost=10,
        subtyp="Fire",
        area=True,
    )
    remaining, _message = promotion_kits.apply_spell_block(
        player,
        caster,
        50,
        spell=area_spell,
    )
    assert remaining == 50
    assert (
        class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"][
            "stronghold"
        ]
        == 0
    )
    assert promotion_kits.spell_block_ready(player)
    assert promotion_kits.tick_resolve_effects(player) == ""
    assert promotion_kits.tick_resolve_effects(player) == ""
    assert "expires" in promotion_kits.tick_resolve_effects(player)


def test_new_resolve_spends_cover_cleanse_barrier_focus_and_passive_riposte(
    monkeypatch,
):
    player = _player("Sentinel")
    attacker = _player("Warrior")
    player.equipment["OffHand"] = items.KiteShield()
    promotion_kits.build_resolve(player, 50, "setup")
    player.status_effects["Poison"].active = True
    player.status_effects["Poison"].duration = 3

    assert "becomes immune" in abilities.PurgeWeakness().use(player)
    assert not player.status_effects["Poison"].active
    assert player.has_status_protection("Stun")

    promotion_kits.build_resolve(player, 40, "setup")
    assert "temporary health" in abilities.Boast().use(player)
    assert player.temporary_health["amount"] == 75
    before = promotion_kits.current_resolve(player)
    promotion_kits.build_resolve(player, 10, "pressure")
    assert promotion_kits.current_resolve(player) - before == 15

    assert "focuses" in abilities.FocusedAssault().use(player)
    assert promotion_kits.focused_assault_accuracy(player) == 0.15
    assert promotion_kits.focused_assault_critical_multiplier(player, 2.0) == 2.3

    promotion_kits.build_resolve(player, 50, "setup")
    assert "Bulwark Guard" in abilities.BulwarkGuard().use(player)
    assert player.temporary_health["turns"] == 1

    player.spellbook["Skills"]["Shield Riposte"] = abilities.ShieldRiposte()
    monkeypatch.setattr(
        "src.core.classes.promotion_kits.resolve.random.random",
        lambda: 0.0,
    )
    assert "knocks" in promotion_kits.shield_riposte_after_full_block(
        player,
        attacker,
    )
    assert attacker.physical_effects["Prone"].active


def test_stalwart_citadel_absorbs_magic_and_fortified_release_returns_it():
    player = _player("Stalwart Defender")
    caster = _player("Paladin")
    enemy = _player("Warrior")
    player.equipment["OffHand"] = items.KiteShield()
    player.progression.purchased_node_ids.add("stalwart-defender.talent.fortified-citadel")
    promotion_kits.build_resolve(player, 100, "setup")
    _complete_mastery(player, "citadel_aegis")
    member = SimpleNamespace(enemy=enemy)
    engine = SimpleNamespace(encounter=SimpleNamespace(living_members=(member,)))

    assert "half of incoming magic" in promotion_kits.citadel_aegis(
        player,
        battle_engine=engine,
    )
    remaining, message = promotion_kits.apply_spell_block(
        player,
        caster,
        100,
        spell=SimpleNamespace(cost=10, subtyp="Fire"),
    )
    assert remaining == 50
    assert "absorbs 50" in message
    enemy_before = enemy.health.current
    assert promotion_kits.tick_resolve_effects(player) == ""
    promotion_kits.tick_resolve_effects(player)
    promotion_kits.tick_resolve_effects(player)
    expiry = promotion_kits.tick_resolve_effects(player)
    assert "Fortified Citadel" in expiry
    assert enemy.health.current == enemy_before - 50


def test_repercussion_hits_every_target_and_punishing_guard_can_knock_down(
    monkeypatch,
):
    player = _player("Stalwart Defender")
    enemies = (_player("Warrior"), _player("Warrior"))
    player.progression.purchased_node_ids.add("stalwart-defender.talent.punishing-guard")
    promotion_kits.build_resolve(player, 100, "setup")
    monkeypatch.setattr(
        "src.core.classes.promotion_kits.resolve.random.random",
        lambda: 0.0,
    )
    engine = SimpleNamespace(current_actor_id="player")

    group = abilities.Repercussion().use_group(
        player,
        [(f"enemy-{index}", enemy) for index, enemy in enumerate(enemies)],
        battle_engine=engine,
    )

    assert len(group.results) == 2
    assert all(result.damage > 0 for result in group.results)
    assert all(enemy.physical_effects["Prone"].active for enemy in enemies)
    assert promotion_kits.current_resolve(player) == 70


def test_surge_modifiers_apply_locked_tuning(monkeypatch):
    player = _player("Stalwart Defender")
    target = _player("Sentinel")
    player.equipment["Weapon"] = items.Rapier()
    player.equipment["OffHand"] = items.KiteShield()
    target.equipment["OffHand"] = items.KiteShield()
    player.progression.purchased_node_ids.update(
        {
            "stalwart-defender.talent.fortified-citadel",
            "stalwart-defender.talent.final-redoubt",
        }
    )
    player.spellbook["Skills"]["Crushing Vengeance"] = abilities.CrushingVengeance()
    player.spellbook["Skills"]["Double Payback"] = abilities.DoublePayback()
    monkeypatch.setattr(
        "src.core.character.offense.random.random",
        lambda: 0.0,
    )

    promotion_kits.build_resolve(player, 100, "setup")
    _complete_mastery(player, "citadel_aegis")
    assert "Citadel Aegis" in promotion_kits.citadel_aegis(player)
    assert promotion_kits.combat_state(player)["citadel_aegis"]["turns"] == 3
    mastery = class_rings.ensure_state(player)["data"]["Stalwart Defender"]["resolve_mastery"]
    assert mastery == {
        "citadel_aegis": 4,
        "ironwall_revenge": 0,
        "last_bastion": 0,
        "stronghold": 0,
    }

    _complete_mastery(
        player,
        "ironwall_revenge",
        "last_bastion",
        "stronghold",
    )
    promotion_kits.build_resolve(player, 100, "setup")
    revenge = promotion_kits.ironwall_reprisal(
        player,
        target,
    )
    assert "Ironwall Revenge" in revenge
    assert "4 strikes" in revenge
    assert "Crushing Vengeance" in revenge
    assert target.stat_effects["Attack"].extra == -3
    assert target.stat_effects["Speed"].extra == -3

    player.health.current = 1
    promotion_kits.build_resolve(player, 100, "setup")
    assert "Last Bastion" in promotion_kits.last_bastion(player)
    assert player.health.current >= 1 + int(player.health.max * 0.40)
    assert player.magic_effects["Nature Shield"].extra >= 75

    promotion_kits.build_resolve(player, 100, "setup")
    assert "Stronghold" in promotion_kits.stronghold(player)
    reduced, message = promotion_kits.stronghold_melee_reduction(
        player,
        100,
        target,
    )
    assert reduced == 70
    assert "reduces melee damage by 30" in message


def test_tower_offense_and_battle_determination_generate_resolve(monkeypatch):
    from types import SimpleNamespace

    player = _player("Stalwart Defender")
    target = _player("Warrior")
    player.equipment["OffHand"] = items.KiteShield()
    player.spellbook["Skills"]["Tower Offense"] = abilities.TowerOffense()
    player.spellbook["Skills"]["Battle Determination"] = abilities.BattleDetermination()
    monkeypatch.setattr(target, "dodge_chance", lambda _actor: 0.0)
    monkeypatch.setattr(
        player,
        "resolve_contact",
        lambda *_args, **_kwargs: SimpleNamespace(hit=True, attribution=None),
    )

    health_before = target.health.current
    abilities.ShieldSlam().use(player, target)

    damage = health_before - target.health.current
    assert damage > 0
    slam_resolve = promotion_kits.current_resolve(player)
    assert slam_resolve == min(20, max(1, damage // 5))

    abilities.BattleCry().use(player, player)
    assert promotion_kits.current_resolve(player) == slam_resolve + 20


def test_get_even_discounts_next_non_surge_resolve_ability():
    player = _player("Stalwart Defender")
    attacker = _player("Warrior")
    player.spellbook["Skills"]["Retaliate"] = abilities.Retaliate()
    player.spellbook["Skills"]["Get Even"] = abilities.GetEven()
    player.weapon_damage = lambda *_args, **_kwargs: ("Counter lands.\n", True, 1)
    rng = SimpleNamespace(random=lambda: 0.0)

    message = ability_mechanics.retaliate_after_block(player, attacker, rng=rng)

    assert "Get Even" in message
    assert promotion_kits.effective_resolve_cost(player, 15) == 5
    promotion_kits.build_resolve(player, 5, "setup")
    assert "focuses" in abilities.FocusedAssault().use(player)
    assert promotion_kits.current_resolve(player) == 0
    assert promotion_kits.combat_state(player).get("get_even_discount", 0) == 0


def test_generator_shield_rewards_each_hit_and_doubles_stuns(monkeypatch):
    player = _player("Stalwart Defender")
    enemies = (_player("Warrior"), _player("Warrior"))
    player.equipment["OffHand"] = items.KiteShield()
    player.spellbook["Skills"]["Generator Shield"] = abilities.GeneratorShield()
    for enemy in enemies:
        monkeypatch.setattr(
            enemy,
            "handle_defenses",
            lambda *_args, **_kwargs: (True, "", 10),
        )
        monkeypatch.setattr(
            enemy,
            "damage_reduction",
            lambda damage, *_args, **_kwargs: (True, "", damage),
        )
    engine = SimpleNamespace(current_actor_id="player")
    rng = SimpleNamespace(random=lambda: 0.0)

    group = abilities.ShieldRicochet().use_group(
        player,
        [(f"enemy-{index}", enemy) for index, enemy in enumerate(enemies)],
        battle_engine=engine,
        rng=rng,
    )

    assert len(group.results) == 2
    assert all(result.effects_applied["Status"] == ["Stun"] for result in group.results)
    assert promotion_kits.current_resolve(player) == 20


def test_known_sentinel_actions_are_adopted_but_leftovers_close():
    player = _player("Sentinel", level=60)
    player.spellbook["Skills"]["Goad"] = abilities.Goad()
    player.spellbook["Skills"]["Retaliate"] = abilities.Retaliate()
    from src.core.progression import ensure_progression

    ensure_progression(player)
    assert "sentinel.ability.goad" in player.progression.purchased_node_ids
    assert "sentinel.ability.retaliate" in (player.progression.purchased_node_ids)

    promotion_id = "sentinel.promotion.stalwart-defender"
    player.progression.purchased_node_ids.update(set(_closure("Sentinel", "Watchful Reprisal")))
    player.stats.con = 20
    result = purchase_node(
        player,
        promotion_id,
        confirm_promotion=True,
    )
    assert result.success
    blocked = purchase_node(player, "sentinel.ability.spell-block")
    assert not blocked.success
    assert "current class tree" in blocked.message
