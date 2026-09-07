"""Regression coverage for the authored Assassin toxin and item paths."""

from src.core import abilities, items, progression
from src.core.classes import footpad
from src.core.save_system import ItemSerializer
from tests.test_framework import TestGameState


def _player():
    return TestGameState.create_player(class_name="Assassin", level=50)


def test_assassin_tree_preserves_columns_gates_and_blank_rows():
    tree = progression.ABILITY_TREES["Assassin"]
    by_name = {node.payload["name"]: node for node in tree.nodes}

    assert len([node for node in tree.nodes if node.kind.value != "promotion"]) == 25
    assert by_name["Steal"].position == (0, 0)
    assert by_name["Disruption"].position == (0, 3)
    assert by_name["Apply Toxin"].payload["level_requirement"] == 35
    assert by_name["Hidden Blade"].position == (3, 2)
    assert by_name["Riposte"].position == (4, 5)

    ninja = by_name["Promote: Ninja"]
    assert ninja.position == (2, 7)
    assert ninja.prerequisites == (by_name["Cutthroat"].id,)
    assert ninja.payload.get("prerequisite_mode", "all") == "all"


def test_toxins_are_craftable_coatable_and_excluded_from_random_loot():
    player = _player()
    player.modify_inventory(items.SnakeVenom())

    assert "Mild Toxin" in footpad.make_toxin(player)
    assert player.inventory["Mild Toxin"]

    player.equipment["Weapon"] = items.Dirk()
    assert "applies Mild Toxin" in footpad.apply_toxin(player)
    assert not player.inventory.get("Mild Toxin")

    random_drop_classes = {
        item_class for bucket in items._build_rarity_table().values() for item_class in bucket
    }
    assert items.MildToxin not in random_drop_classes
    assert items.Necrotoxin not in random_drop_classes


def test_throwing_dagger_pack_round_trips_charges():
    pack = items.ThrowingDaggers(charges=6)

    restored = ItemSerializer.deserialize(ItemSerializer.serialize(pack))

    assert restored.name == "Throwing Daggers"
    assert restored.charges == 6


def test_apply_and_make_toxin_are_exploration_abilities():
    assert abilities.ApplyToxin.exploration_cast
    assert abilities.MakeToxin.exploration_cast
