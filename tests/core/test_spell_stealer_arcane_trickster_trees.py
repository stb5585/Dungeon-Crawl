"""Regression coverage for the authored stolen-magic progression trees."""

from types import SimpleNamespace

from src.core import abilities, enemies, items
from src.core.classes import promotion_kits
from src.core.combat.combat_result import CombatResult
from src.core.effects.common import DynamicMultiDebuffEffect
from src.core.progression import (
    ABILITY_TREES,
    NodeKind,
    ProgressionState,
)
from tests.test_framework import TestGameState


def _player(class_name: str, level: int = 90):
    player = TestGameState.create_player(class_name=class_name, level=level)
    player.progression = ProgressionState(level=level)
    return player


def _grant(player, *talent_keys: str) -> None:
    talents = {
        node.payload["talent_key"]: node
        for tree_name in ("Spell Stealer", "Arcane Trickster")
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    for talent_key in talent_keys:
        player.progression.purchased_node_ids.add(talents[talent_key].id)


class _CertainRng:
    @staticmethod
    def choice(values):
        return values[0]

    @staticmethod
    def random():
        return 0.0


def test_stolen_magic_trees_preserve_compact_build_pressure():
    stealer_tree = ABILITY_TREES["Spell Stealer"]
    stealer_nodes = [node for node in stealer_tree.nodes if node.kind != NodeKind.PROMOTION]
    promotion = next(node for node in stealer_tree.nodes if node.kind == NodeKind.PROMOTION)
    trickster_tree = ABILITY_TREES["Arcane Trickster"]

    assert len(stealer_nodes) == 12
    assert sum(node.cost for node in stealer_nodes) == 19
    assert 0.60 <= 12 / 19 <= 0.70
    assert promotion.cost == 3
    assert promotion.payload["prerequisite_mode"] == "any"
    assert len(promotion.prerequisites) == 2
    assert len(trickster_tree.nodes) == 11
    assert sum(node.cost for node in trickster_tree.nodes) == 28
    assert 0.70 <= 20 / 28 <= 0.72
    assert trickster_tree.branches == (
        "Spell Theft",
        "Stolen Spell Mastery",
        "Misdirection",
    )


def test_external_weaken_mind_does_not_gate_arcane_trickster_progression():
    tree = ABILITY_TREES["Arcane Trickster"]
    nodes = {node.name: node for node in tree.nodes}

    assert "Weaken Mind" not in nodes
    assert nodes["Neural Connection"].lane == "Stolen Spell Mastery"
    assert nodes["Neural Connection"].prerequisites == (nodes["Steal Spell 2"].id,)
    assert not any(
        nodes["Neural Connection"].id in candidate.prerequisites for candidate in tree.nodes
    )


def test_stolen_magic_rows_use_standard_level_bands_and_fit_eight_rows():
    expected = {
        "Spell Stealer": {1: 35, 2: 40, 3: 45, 4: 50, 5: 55},
        "Arcane Trickster": {1: 65, 2: 70, 3: 75, 4: 80, 5: 85},
    }
    for class_name, levels in expected.items():
        tree = ABILITY_TREES[class_name]
        assert max(node.position[1] for node in tree.nodes) <= 7
        for node in tree.nodes:
            row = node.position[1]
            if node.kind == NodeKind.PROMOTION:
                assert row == 7
            elif row == 0:
                assert "level_requirement" not in node.payload
            else:
                assert node.payload["level_requirement"] == levels[row]


def test_arcane_ledger_and_perfect_forgery_modify_successful_theft():
    stealer = _player("Spell Stealer", 60)
    stealer.mana.current = stealer.mana.max
    stealer.modify_inventory(items.BlankScroll())
    _grant(
        stealer,
        "spell-stealer.arcane-ledger",
        "spell-stealer.perfect-forgery",
    )
    target = SimpleNamespace(
        name="Acolyte",
        spellbook={"Spells": {"Firebolt": abilities.Firebolt()}},
        class_ring_trial_enemy=False,
        boss=False,
        boss_type=None,
    )
    before_mana = stealer.mana.current

    message = abilities.StealSpell().use(stealer, target, rng=_CertainRng())

    assert stealer.mana.current == before_mana - 6
    assert "Perfect Forgery preserves" in message
    assert "Blank Scroll" in stealer.inventory
    assert any(name.startswith("Stolen ") for name in stealer.inventory)


def test_charge_talents_accelerate_scroll_gain_and_retain_failed_discharge():
    stealer = _player("Spell Stealer", 60)
    _grant(
        stealer,
        "spell-stealer.counterfeit-casting",
        "spell-stealer.controlled-discharge",
    )
    state = promotion_kits.combat_state(stealer)

    promotion_kits.gain_stolen_charge(stealer, "stolen spell scroll")
    assert state["stolen_charge"] == 2

    promotion_kits.prepare_stolen_charge_payoff(stealer, "Attack")
    message = promotion_kits.record_action_resolution(
        stealer,
        CombatResult(
            action="Attack",
            actor=stealer,
            target=enemies.Goblin(),
            hit=False,
            damage=0,
        ),
    )
    assert "retains 1 Stolen Charge" in message
    assert state["stolen_charge"] == 1


def test_borrowed_ward_spends_charge_for_both_defenses():
    stealer = _player("Spell Stealer", 60)
    state = promotion_kits.combat_state(stealer)
    state["stolen_charge"] = 2

    result = abilities.BorrowedWard().use(stealer)

    assert result.hit is True
    assert result.extra["stolen_charge_spent"] == 2
    assert state["stolen_charge"] == 0
    assert stealer.stat_effects["Defense"].extra == 8
    assert stealer.stat_effects["Magic Defense"].extra == 8


def test_master_thief_and_mnemonic_larceny_reward_permanent_learning():
    trickster = _player("Arcane Trickster")
    trickster.stats.intel = 10
    trickster.stats.dex = 10
    trickster.mana.current = trickster.mana.max
    _grant(
        trickster,
        "arcane-trickster.master-thief",
        "arcane-trickster.mnemonic-larceny",
    )
    target = SimpleNamespace(
        name="Acolyte",
        spellbook={"Spells": {"Firebolt": abilities.Firebolt()}},
        class_ring_trial_enemy=False,
        boss=False,
        boss_type=None,
    )
    before_mana = trickster.mana.current

    message = abilities.StealSpell2().use(trickster, target, rng=_CertainRng())

    assert "permanently learns Firebolt" in message
    assert "Mnemonic Larceny restores 11 MP" in message
    assert trickster.mana.current == before_mana - 11


def test_neural_connection_mirrors_weaken_mind_amount_and_duration():
    trickster = _player("Arcane Trickster")
    target = enemies.Goblin()
    _grant(trickster, "arcane-trickster.neural-connection")
    effect = DynamicMultiDebuffEffect(
        stats=[
            {"stat_name": "Magic", "combat_attr": "magic"},
            {"stat_name": "Magic Defense", "combat_attr": "magic_def"},
        ],
        percentage=0.20,
        duration=4,
    )
    result = CombatResult(action="Weaken Mind", actor=trickster, target=target)

    effect.apply(trickster, target, result)

    for stat_name in ("Magic", "Magic Defense"):
        assert trickster.stat_effects[stat_name].extra == abs(target.stat_effects[stat_name].extra)
        assert trickster.stat_effects[stat_name].duration == 4
    assert any("lowered by 20%." in message for message in result.extra["messages"])
    assert all("(" not in message and "turn" not in message for message in result.extra["messages"])
    assert "Neural Connection" in "".join(result.extra["messages"])


def test_arcane_trickster_actives_and_grand_larceny_expand_combat_choices(
    monkeypatch,
):
    trickster = _player("Arcane Trickster")
    target = enemies.Goblin()
    _grant(
        trickster,
        "arcane-trickster.escape-artist",
        "arcane-trickster.grand-larceny",
    )
    promotion_kits.combat_state(trickster)["stolen_charge"] = 3

    vanishing = abilities.VanishingAct().use(trickster)

    assert vanishing.hit is True
    assert trickster.stat_effects["Speed"].extra == 12
    assert trickster.stat_effects["Speed"].duration == 4
    assert promotion_kits.cap_for(trickster, "stolen_charge") == 4

    def weapon_hit(enemy, **_kwargs):
        enemy.health.current -= 10
        return "Trickster hit.\n", True, 1

    monkeypatch.setattr(trickster, "weapon_damage", weapon_hit)
    opening = abilities.FalseOpening().use(trickster, target)

    assert opening.damage == 10
    assert target.stat_effects["Attack"].extra < 0
    assert target.stat_effects["Magic"].extra < 0
