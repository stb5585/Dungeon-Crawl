#!/usr/bin/env python3
"""
Additional save-system coverage for serializers and SaveManager flows.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import abilities, enemies, items
from src.core.save_system import (
    AbilitySerializer,
    EnemyStateSerializer,
    ItemSerializer,
    PlayerDataSerializer,
    SaveManager,
)
from tests.test_framework import TestGameState


def test_item_serializer_handles_none_and_accessory_deserialization():
    none_data = ItemSerializer.serialize(None)
    ring_data = ItemSerializer.serialize(items.PowerRing())
    ring_data["typ"] = "Accessory"

    restored_none = ItemSerializer.deserialize({"name": "None", "typ": "Weapon", "subtyp": "None"})
    restored_ring = ItemSerializer.deserialize(ring_data)

    assert none_data == {"name": "None", "typ": "None", "subtyp": "None"}
    assert restored_none.subtyp == "None"
    assert restored_ring.name == "Power Ring"


def test_item_serializer_falls_back_to_empty_equipment_for_unknown_class():
    restored = ItemSerializer.deserialize(
        {"name": "Mystery Blade", "typ": "Weapon", "subtyp": "Sword", "class": "MissingItem"}
    )

    assert restored.subtyp == "None"


def test_ability_serializer_supports_class_name_display_name_and_yaml_override():
    heal = abilities.Heal()
    heal._class_name = "HealYaml"

    assert AbilitySerializer.serialize(heal) == "HealYaml"
    assert AbilitySerializer.deserialize("Heal2").name == "Heal"
    assert AbilitySerializer.deserialize("Heal").name == "Heal"
    assert AbilitySerializer.deserialize("") is None


def test_enemy_state_serializer_round_trips_class_and_instance_state():
    goblin = enemies.Goblin()
    goblin.health.current = 7

    class_state = EnemyStateSerializer.serialize(enemies.Goblin)
    instance_state = EnemyStateSerializer.serialize(goblin)

    restored_class = EnemyStateSerializer.deserialize(class_state)
    restored_enemy = EnemyStateSerializer.deserialize(instance_state)

    assert restored_class is enemies.Goblin
    assert restored_enemy.name == "Goblin"
    assert restored_enemy.health.current == 7
    assert EnemyStateSerializer.deserialize({"class_type": "MissingEnemy"}) is None


def test_player_data_deserialize_marks_killed_boss_tiles_defeated_without_world_state(monkeypatch):
    player = TestGameState.create_player(name="BossSlayer", class_name="Warrior", race_name="Human", level=12)
    player.kill_dict = {"Boss": {"Minotaur": 1}}
    serialized = PlayerDataSerializer.serialize(player)
    serialized.pop("world_state", None)

    class DummyTile:
        def __init__(self, enemy=None):
            self.enemy = enemy
            self.defeated = False

    def fake_load_tiles(self):
        self.world_dict = {
            (1, 1, 0): DummyTile(enemy=SimpleNamespace(name="Minotaur")),
            (2, 2, 0): DummyTile(enemy=SimpleNamespace(name="Goblin")),
        }

    monkeypatch.setattr("src.core.player.Player.load_tiles", fake_load_tiles)

    restored = PlayerDataSerializer.deserialize(serialized, skip_tiles=False)

    assert restored.world_dict[(1, 1, 0)].defeated is True
    assert restored.world_dict[(1, 1, 0)].enemy is None
    assert restored.world_dict[(2, 2, 0)].defeated is False


def test_save_manager_round_trip_list_and_delete(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    tmp_dir = tmp_path / "tmp"
    monkeypatch.setattr(SaveManager, "SAVE_DIR", str(save_dir))
    monkeypatch.setattr(SaveManager, "TMP_DIR", str(tmp_dir))

    player = TestGameState.create_player(name="Saver", class_name="Warrior", race_name="Human", level=10)

    assert SaveManager.save_player(player, "hero.save") is True
    assert "hero.save" in SaveManager.list_saves()

    restored = SaveManager.load_player("hero.save", skip_tiles=True)
    assert restored is not None
    assert restored.name == "Saver"

    assert SaveManager.save_player(player, "hero.tmp", is_tmp=True) is True
    restored_tmp = SaveManager.load_player("hero.tmp", is_tmp=True, skip_tiles=True)
    assert restored_tmp is not None
    assert restored_tmp.name == "Saver"

    assert SaveManager.delete_save("hero.save") is True
    assert SaveManager.load_player("hero.save", skip_tiles=True) is None


def test_save_manager_returns_false_or_none_on_failures(monkeypatch, tmp_path):
    save_dir = tmp_path / "saves"
    tmp_dir = tmp_path / "tmp"
    monkeypatch.setattr(SaveManager, "SAVE_DIR", str(save_dir))
    monkeypatch.setattr(SaveManager, "TMP_DIR", str(tmp_dir))

    player = TestGameState.create_player(name="Broken", class_name="Warrior", race_name="Human", level=10)

    monkeypatch.setattr("src.core.save_system.json.dump", lambda *args, **kwargs: (_ for _ in ()).throw(TypeError("dump fail")))
    assert SaveManager.save_player(player, "broken.save") is False

    assert SaveManager.load_player("missing.save", skip_tiles=True) is None
    assert SaveManager.delete_save("missing.save") is False
