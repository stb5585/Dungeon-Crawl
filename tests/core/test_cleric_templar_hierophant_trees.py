"""Regression coverage for authored Cleric promotion paths."""

from src.core import abilities, enemies, items
from src.core.classes import ability_mechanics, class_rings, promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState
from tests.test_framework import TestGameState


def _player(class_name: str, level: int = 90):
    player = TestGameState.create_player(class_name=class_name, level=level)
    player.progression = ProgressionState(level=level)
    return player


def _grant(player, *talent_keys: str) -> None:
    talents = {
        node.payload["talent_key"]: node
        for tree_name in ("Cleric", "Templar", "Hierophant")
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    for talent_key in talent_keys:
        player.progression.purchased_node_ids.add(talents[talent_key].id)


def _closure_cost(tree, node):
    by_id = {entry.id: entry for entry in tree.nodes}
    seen = set()

    def visit(entry):
        if entry.id in seen:
            return 0
        seen.add(entry.id)
        return entry.cost + sum(visit(by_id[parent]) for parent in entry.prerequisites)

    return visit(node)


def test_cleric_has_five_disciplines_and_two_affordable_promotion_routes():
    tree = ABILITY_TREES["Cleric"]
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]
    promotions = [node for node in tree.nodes if node.kind == NodeKind.PROMOTION]

    assert tree.branches == (
        "Devotion",
        "Sacred Office",
        "Bulwark",
        "Judgment",
        "Shared Ministry",
    )
    assert len(development) == 26
    assert sum(node.cost for node in development) == 26
    assert {node.payload["target_class"] for node in promotions} == {
        "Hierophant",
        "Templar",
    }
    for promotion in promotions:
        assert promotion.payload["prerequisite_mode"] == "any"
        assert len(promotion.prerequisites) == 2
        cheapest_endpoint = min(
            _closure_cost(tree, next(node for node in tree.nodes if node.id == endpoint))
            for endpoint in promotion.prerequisites
        )
        assert cheapest_endpoint == 5
        assert 15 - promotion.cost - cheapest_endpoint == 7


def test_terminal_trees_each_cost_thirty_points_for_two_thirds_coverage():
    for class_name in ("Templar", "Hierophant"):
        tree = ABILITY_TREES[class_name]
        assert len(tree.nodes) == 28
        assert sum(node.cost for node in tree.nodes) == 30
        assert 0.60 <= 20 / 30 <= 0.70
        assert max(node.position[1] for node in tree.nodes) == 6
        assert sum(node.cost > 1 for node in tree.nodes) == 2
    assert ABILITY_TREES["Templar"].branches == (
        "Relic Discipline",
        "Vanguard",
        "Sacred Rites",
        "Judgment",
        "Ordered Blessings",
    )
    assert ABILITY_TREES["Hierophant"].branches == (
        "Consecrated Conduit",
        "Devotional Grace",
        "Radiant Office",
        "Pastoral Office",
    )


def test_templar_ring_modifiers_are_terminal_and_do_not_gate_sacred_rites():
    tree = ABILITY_TREES["Templar"]
    nodes = {node.name: node for node in tree.nodes}
    ring_modifiers = ("Ordered Purpose", "Liturgical Renewal", "Perfect Order")

    assert nodes["Regen II"].prerequisites == (nodes["Smite III"].id,)
    assert nodes["Bless"].prerequisites == (nodes["Regen II"].id,)
    assert nodes["Dispel"].prerequisites == (nodes["Bless"].id,)
    assert nodes["Regen II"].payload["level_requirement"] == 70
    assert nodes["Bless"].payload["level_requirement"] == 75
    assert nodes["Dispel"].payload["level_requirement"] == 80
    for name in ring_modifiers:
        node = nodes[name]
        assert node.lane == "Ordered Blessings"
        assert not any(node.id in candidate.prerequisites for candidate in tree.nodes)


def test_cleric_level_bands_and_promotion_rows_fit_the_standard_panel():
    tree = ABILITY_TREES["Cleric"]
    expected = {1: 35, 2: 40, 3: 45, 4: 50, 5: 55}

    assert max(node.position[1] for node in tree.nodes) == 7
    for node in tree.nodes:
        row = node.position[1]
        if node.kind == NodeKind.PROMOTION:
            assert row == 7
        elif row == 0:
            assert "level_requirement" not in node.payload
        else:
            assert node.payload["level_requirement"] == expected[row]


def test_cleric_devotion_talents_improve_held_and_spent_defense():
    cleric = _player("Cleric", 60)
    _grant(
        cleric,
        "cleric.held-faith",
        "cleric.lasting-sanctuary",
        "cleric.overflowing-grace",
    )
    promotion_kits.gain_meter(cleric, "devotion", 4, "test")

    _hit, message, damage = cleric.damage_reduction(
        100,
        enemies.Goblin(),
        typ="Physical",
    )

    assert promotion_kits.cap_for(cleric, "devotion") == 4
    assert damage == 84
    assert "reduces damage by 16" in message
    abilities.SanctuaryWard().use(cleric)
    assert cleric.magic_effects["Nature Shield"].duration == 3


def test_bastion_prayer_and_shield_litany_allow_partial_spending():
    cleric = _player("Cleric", 60)
    cleric.equipment["OffHand"] = items.KiteShield()
    _grant(cleric, "cleric.bastion-practice", "cleric.shield-litany")
    promotion_kits.gain_meter(cleric, "devotion", 3, "test")

    result = abilities.BastionPrayer().use(cleric)

    assert result.hit is True
    assert promotion_kits.combat_state(cleric)["devotion"] == 2
    assert cleric.stat_effects["Defense"].extra == 10
    promotion_kits.begin_action(cleric)
    promotion_kits.combat_state(cleric)["devotion"] = 0
    assert "gains 2 Devotion" in promotion_kits.record_devotion_block(cleric)


def test_shared_ministry_actions_support_both_cleric_promotions():
    for class_name in ("Templar", "Hierophant"):
        cleric = _player(class_name)
        cleric.health.current = cleric.health.max // 2
        _grant(cleric, "cleric.open-ministry", "cleric.common-purpose")

        healing = abilities.SacredMending().use(cleric)
        guard = abilities.HallowedReadiness().use(cleric)

        assert healing.healing > 0
        assert guard.hit is True
        assert cleric.stat_effects["Defense"].extra == 12
        assert cleric.stat_effects["Magic Defense"].duration == 3


def test_devotional_rebuke_adds_holy_damage_and_consecrated_devotion(monkeypatch):
    cleric = _player("Cleric", 60)
    target = enemies.Goblin()
    _grant(cleric, "cleric.measured-judgment", "cleric.consecrated-blows")

    def weapon_hit(enemy, **_kwargs):
        enemy.health.current -= 10
        return "Weapon hit.\n", True, 1

    monkeypatch.setattr(cleric, "weapon_damage", weapon_hit)
    result = abilities.DevotionalRebuke().use(cleric, target)

    assert result.damage > 10
    assert "Holy damage" in result.message
    promotion_kits.combat_state(cleric)["devotion"] = 0
    promotion_kits.pop_messages(cleric)
    promotion_kits.begin_action(cleric)
    message = promotion_kits.record_devotion_source(
        cleric,
        "Holy pressure",
        holy_or_shield=True,
    )
    assert "gains 2 Devotion" in message


def test_templar_talents_strengthen_relic_blessing_and_last_stand():
    templar = _player("Templar")
    templar.equipment["OffHand"] = items.KiteShield()
    templar.equipment["Ring"] = items.ClassRing()
    class_rings.ensure_state(templar)["awakened"]["Templar"] = True
    templar.equipment["Ring"].class_mod(templar)
    _grant(
        templar,
        "templar.reinforced-relic",
        "templar.enduring-aegis",
        "templar.ordered-purpose",
        "templar.liturgical-renewal",
        "templar.perfect-order",
        "templar.last-line",
        "templar.unbroken-reliquary",
    )
    templar.spellbook["Skills"]["Last Stand"] = abilities.LastStand()
    promotion_kits.gain_meter(templar, "devotion", 2, "test")
    templar.health.current = max(1, templar.health.max // 4)
    mana_before = templar.mana.current

    message = abilities.RelicAegis().use(templar)

    assert "Relic Aegis" in message
    assert "Liturgical Renewal restores 2 MP" in message
    assert templar.mana.current == mana_before - 10
    assert templar.magic_effects["Nature Shield"].extra == 56
    assert templar.magic_effects["Nature Shield"].duration == 4
    assert templar.stat_effects["Magic Defense"].active is True
    last_stand = ability_mechanics.activate_last_stand(templar)
    assert "gains 1 Devotion" in last_stand


def test_hierophant_grace_and_conduit_talents_modify_existing_loops():
    hierophant = _player("Hierophant")
    hierophant.equipment["Weapon"] = items.Quarterstaff()
    hierophant.health.current -= 30
    _grant(
        hierophant,
        "hierophant.gentle-grace",
        "hierophant.greater-intercession",
        "hierophant.abundant-grace",
        "hierophant.luminous-doctrine",
        "hierophant.merciful-ward",
    )
    promotion_kits.begin_action(hierophant)

    healing_message = promotion_kits.record_healing_done(
        hierophant,
        max(30, hierophant.health.max // 10),
        source="Heal II",
    )

    assert "gains 2 Devotion" in healing_message
    assert "Merciful Ward" in healing_message
    assert hierophant.magic_effects["Nature Shield"].active is True
    assert promotion_kits.cap_for(hierophant, "devotion") == 6
    result = abilities.GracefulIntercession().use(hierophant)
    assert result.healing > 0
    assert hierophant.magic_effects["Nature Shield"].duration == 3
    assert promotion_kits.combat_state(hierophant)["devotion"] == 1

    promotion_kits.combat_state(hierophant)["devotion"] = 0
    promotion_kits.begin_action(hierophant)
    holy_message = promotion_kits.record_devotion_source(
        hierophant,
        "Holy pressure",
        holy_or_shield=True,
    )
    assert "gains 2 Devotion" in holy_message


def test_conduit_strike_requires_staff_and_remains_an_active_weapon_choice(
    monkeypatch,
):
    hierophant = _player("Hierophant")
    target = enemies.Goblin()
    strike = abilities.ConduitStrike()

    assert "requires a staff" in strike.use(hierophant, target).message
    hierophant.equipment["Weapon"] = items.Quarterstaff()
    target.health.current = target.health.max = 100

    def weapon_hit(enemy, **_kwargs):
        enemy.health.current -= 12
        return "Staff hit.\n", True, 1

    monkeypatch.setattr(hierophant, "weapon_damage", weapon_hit)
    result = strike.use(hierophant, target)
    assert result.damage == 12
    assert result.hit is True
