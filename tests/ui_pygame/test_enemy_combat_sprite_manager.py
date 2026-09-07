#!/usr/bin/env python3
"""Focused coverage for transparent enemy combat sprite loading."""

from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest
from PIL import Image

from src.core import enemies
from src.ui_pygame.assets.enemy_combat_sprite_manager import (
    POLYMORPH_SPRITE_SCALE,
    EnemyCombatSpriteManager,
)
from tools.build_enemy_combat_sprites import mapped_sprite_keys

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    yield


def _write_sprite(
    path: Path, color: tuple[int, int, int, int], size: tuple[int, int] = (32, 48)
) -> None:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surface, color, pygame.Rect(4, 2, size[0] - 8, size[1] - 4))
    pygame.image.save(surface, path)


def test_enemy_combat_sprite_manager_loads_mapping_and_exact_sprite(tmp_path):
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "goblin.png", (220, 30, 20, 255))
    _write_sprite(sprite_root / "boss.png", (20, 220, 30, 255))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255))
    (sprite_root / "enemy_combat_sprite_map.json").write_text(
        json.dumps({"Goblin Raider": "goblin", "Named Boss": "boss"}),
        encoding="utf-8",
    )

    manager = EnemyCombatSpriteManager(sprite_root=sprite_root)

    assert manager.get_sprite_key_for_enemy(SimpleNamespace(name="Goblin Raider")) == "goblin"
    assert manager.get_sprite_by_name("Goblin Raider").get_at((5, 5)) == pygame.Color(
        220, 30, 20, 255
    )
    assert manager.get_sprite_by_key("goblin") is manager.get_sprite_by_key("goblin")


def test_enemy_combat_sprite_manager_uses_tamed_species_after_rename():
    manager = EnemyCombatSpriteManager()

    hornet = SimpleNamespace(name="Needle (Giant Hornet)", enemy_class="GiantHornet")
    wolf = SimpleNamespace(name="Scout (Direwolf)", enemy_class="Direwolf")

    assert manager.get_sprite_key_for_enemy(hornet) == "giant_hornet"
    assert manager.get_sprite_key_for_enemy(wolf) == "dire_wolf"


def test_enemy_combat_sprite_manager_scaled_cache_fallbacks_and_aspect_ratio(tmp_path):
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "boss.png", (20, 220, 30, 255), size=(20, 40))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255), size=(20, 40))
    (sprite_root / "enemy_combat_sprite_map.json").write_text(
        json.dumps({"Goblin Raider": "goblin", "Named Boss": "boss"}),
        encoding="utf-8",
    )

    manager = EnemyCombatSpriteManager(sprite_root=sprite_root)

    assert (
        manager.get_sprite_key_for_enemy(SimpleNamespace(name="Goblin Raider")) == "generic_enemy"
    )
    assert (
        manager.get_sprite_key_for_enemy(SimpleNamespace(name="Goblin Raider", boss=True)) == "boss"
    )

    scaled = manager.get_scaled_sprite_by_name("Named Boss", (40, 40))
    scaled_again = manager.get_scaled_sprite_by_name("Named Boss", (40, 40))
    assert scaled.get_size() == (40, 40)
    assert scaled_again is scaled
    assert scaled.get_at((0, 20)).a == 0
    assert scaled.get_at((20, 20)).a > 0

    manager.clear_cache()
    assert manager.get_scaled_sprite_by_name("Named Boss", (40, 40)) is not scaled


def test_enemy_combat_sprite_manager_loads_combat_scale_map(tmp_path):
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "boss.png", (20, 220, 30, 255))
    _write_sprite(sprite_root / "minotaur.png", (220, 30, 20, 255))
    _write_sprite(sprite_root / "red_dragon.png", (220, 120, 20, 255))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255))
    (sprite_root / "enemy_combat_sprite_map.json").write_text(
        json.dumps({"Minotaur": "minotaur", "Scaled By Key": "red_dragon"}),
        encoding="utf-8",
    )
    (sprite_root / "enemy_combat_sprite_scale.json").write_text(
        json.dumps(
            {
                "boss": 1.1,
                "Minotaur": 1.4,
                "red_dragon": 1.25,
                "Too Small": 0.1,
                "Too Large": 3.0,
                "Invalid": "large",
            }
        ),
        encoding="utf-8",
    )

    manager = EnemyCombatSpriteManager(sprite_root=sprite_root)

    assert manager.get_combat_scale_for_enemy("Minotaur") == 1.4
    assert manager.get_combat_scale_for_enemy("Scaled By Key") == 1.25
    assert manager.get_combat_scale_for_enemy(SimpleNamespace(name="Named Boss", boss=True)) == 1.1
    assert manager.combat_scale_map["Too Small"] == 0.25
    assert manager.combat_scale_map["Too Large"] == 2.5
    assert "Invalid" not in manager.combat_scale_map
    assert manager.get_combat_scale_for_enemy("Goblin") == 1.0


def test_enemy_combat_sprite_manager_loads_dungeon_scale_map(tmp_path):
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "jester.png", (220, 30, 20, 255))
    _write_sprite(sprite_root / "boss.png", (20, 220, 30, 255))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255))
    (sprite_root / "enemy_combat_sprite_map.json").write_text(
        json.dumps({"Jester": "jester"}),
        encoding="utf-8",
    )
    (sprite_root / "enemy_dungeon_sprite_scale.json").write_text(
        json.dumps({"Jester": 0.65, "boss": 1.25}),
        encoding="utf-8",
    )

    manager = EnemyCombatSpriteManager(sprite_root=sprite_root)

    assert manager.get_dungeon_scale_for_enemy("Jester") == 0.65
    assert (
        manager.get_dungeon_scale_for_enemy(SimpleNamespace(name="Unknown Boss", boss=True)) == 1.25
    )
    assert manager.get_dungeon_scale_for_enemy("Goblin") == 1.0


def test_enemy_combat_sprite_manager_prefers_explicit_png_picture_key(tmp_path):
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "jester.png", (220, 30, 20, 255))
    _write_sprite(sprite_root / "jester2.png", (120, 30, 220, 255))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255))
    (sprite_root / "enemy_combat_sprite_map.json").write_text(
        json.dumps({"Jester": "jester"}),
        encoding="utf-8",
    )

    manager = EnemyCombatSpriteManager(sprite_root=sprite_root)

    assert (
        manager.get_sprite_key_for_enemy(SimpleNamespace(name="Jester", picture="jester2.png"))
        == "jester2"
    )
    assert (
        manager.get_sprite_key_for_enemy(SimpleNamespace(name="Jester", picture="jester.txt"))
        == "jester"
    )


def test_enemy_combat_sprite_manager_strict_map_avoids_broad_render_reuse(tmp_path):
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()
    _write_sprite(sprite_root / "battle_toad.png", (220, 30, 20, 255))
    _write_sprite(sprite_root / "bear.png", (20, 220, 30, 255))
    _write_sprite(sprite_root / "evil_crusader.png", (220, 220, 30, 255))
    _write_sprite(sprite_root / "generic_enemy.png", (20, 30, 220, 255))
    (sprite_root / "enemy_combat_sprite_map.json").write_text(
        json.dumps(
            {"Battle Toad": "battle_toad", "Direbear": "bear", "Evil Crusader": "evil_crusader"}
        ),
        encoding="utf-8",
    )

    manager = EnemyCombatSpriteManager(sprite_root=sprite_root)

    assert manager.get_sprite_key_for_enemy("Battle Toad") == "battle_toad"
    assert manager.get_sprite_key_for_enemy("Direbear") == "bear"
    assert manager.get_sprite_key_for_enemy("Evil Crusader") == "evil_crusader"
    assert manager.get_sprite_key_for_enemy("Alligator") == "generic_enemy"


def test_enemy_combat_sprite_manager_missing_sprite_uses_runtime_fallback(tmp_path):
    sprite_root = tmp_path / "enemy_combat_sprites"
    sprite_root.mkdir()

    manager = EnemyCombatSpriteManager(sprite_root=sprite_root)

    fallback = manager.get_sprite_by_key("goblin")

    assert fallback.get_size() == (384, 384)
    assert fallback.get_at((0, 0)).a == 0
    assert manager.get_sprite_by_name("Unknown Thing").get_size() == (384, 384)


def test_default_enemy_combat_sprite_assets_cover_render_archetypes():
    manager = EnemyCombatSpriteManager()
    expected_keys = {
        "boss",
        "generic_enemy",
        "goblin",
        "skeleton",
        "dragon",
        "demon",
        "wolf",
        "slime",
    }

    assert expected_keys
    assert expected_keys <= manager.available_keys
    assert manager.get_sprite_key_for_enemy("Evil Crusader") == "evil_crusader"
    assert manager.get_sprite_key_for_enemy("Battle Toad") == "battle_toad"
    assert manager.get_sprite_key_for_enemy("Alligator") == "alligator"
    assert manager.get_sprite_key_for_enemy("Water Myrmidon") == "water_myrmidon"
    for enemy_name in (
        "Goblin",
        "Skeleton",
        "Giant Rat",
        "Battle Toad",
        "Evil Crusader",
        "Satyr",
        "Gnoll",
        "Alligator",
        "Werewolf",
        "Troll",
        "Necromancer",
        "Water Myrmidon",
        "Dragonkin",
        "Warforged",
    ):
        sprite = manager.get_sprite_by_name(enemy_name)
        assert sprite.get_width() > 0
        assert sprite.get_height() > 0
        assert sprite.get_at((0, 0)).a == 0


def test_default_enemy_combat_sprite_map_covers_concrete_enemy_names():
    manager = EnemyCombatSpriteManager()
    enemy_names = _concrete_enemy_names()
    ignored = {"Test", "Myrmidon"}
    missing = sorted(
        name for name in enemy_names if name not in manager.sprite_map and name not in ignored
    )

    assert missing == []


def test_default_jester_form_combat_sprites_exist_and_resolve():
    manager = EnemyCombatSpriteManager()

    for picture in ("jester.png", "jester1.png", "jester2.png", "jester3.png", "jester4.png"):
        key = Path(picture).stem
        assert key in manager.available_keys
        assert (
            manager.get_sprite_key_for_enemy(SimpleNamespace(name="Jester", picture=picture)) == key
        )


def test_default_guild_trial_bosses_resolve_expected_combat_art():
    manager = EnemyCombatSpriteManager()

    cutpurse = enemies.GuildCutpurseBoss()
    assert manager.get_sprite_key_for_enemy(cutpurse) == "guild_cutpurse"
    assert manager.sprite_map[cutpurse.name] == "guild_cutpurse"
    assert "guild_cutpurse" in manager.available_keys
    sprite = manager.get_sprite_by_name(cutpurse.name)
    assert sprite.get_at((0, 0)).a == 0

    arcane = enemies.GuildArcaneBoss()
    assert manager.get_sprite_key_for_enemy(arcane) == "guild_cutpurse"
    assert manager.sprite_map[arcane.name] == "guild_cutpurse"

    for enemy in (enemies.GuildInquestBoss(), enemies.GuildContractBoss()):
        assert manager.get_sprite_key_for_enemy(enemy) == "bandit"
        assert manager.sprite_map[enemy.name] == "bandit"


def test_default_vesperion_combat_sprite_uses_separate_full_body_asset():
    manager = EnemyCombatSpriteManager()
    sprite_path = manager.sprite_root / "vesperion.png"
    portrait_path = PROJECT_ROOT / "src" / "ui_pygame" / "assets" / "npc_art" / "vesperion.png"

    assert manager.get_sprite_key_for_enemy("Vesperion") == "vesperion"
    assert "vesperion" in manager.available_keys
    assert "vesperion" in mapped_sprite_keys(manager.sprite_root)
    assert sprite_path.exists()
    assert sprite_path.read_bytes() != portrait_path.read_bytes()

    with Image.open(sprite_path) as image:
        assert image.mode == "RGBA"
        assert image.getchannel("A").getbbox() is not None

    sprite = manager.get_sprite_by_name("Vesperion")
    assert sprite.get_width() > 0
    assert sprite.get_height() > 0
    assert sprite.get_at((0, 0)).a == 0


def test_polymorph_uses_transparent_bunny_combat_sprite():
    manager = EnemyCombatSpriteManager()
    enemy = SimpleNamespace(
        name="Goblin",
        status_effects={"Polymorph": SimpleNamespace(active=True)},
    )

    assert manager.get_sprite_key_for_enemy(enemy) == "polymorph_bunny"
    assert manager.get_combat_scale_for_enemy(enemy) == POLYMORPH_SPRITE_SCALE
    assert manager.get_dungeon_scale_for_enemy(enemy) == POLYMORPH_SPRITE_SCALE
    path = manager.sprite_root / "polymorph_bunny.png"
    with Image.open(path) as image:
        assert image.mode == "RGBA"
        assert image.getchannel("A").getextrema() == (0, 255)


def _concrete_enemy_names() -> set[str]:
    enemy_package = PROJECT_ROOT / "src" / "core" / "enemies"
    enemies_source = "\n".join(
        (enemy_package / filename).read_text(encoding="utf-8")
        for filename in ("early.py", "midgame.py", "endgame.py")
    )
    class_pattern = re.compile(r"^class\s+\w+\([^)]*\):", re.MULTILINE)
    starts = [match.start() for match in class_pattern.finditer(enemies_source)]
    names: set[str] = set()

    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(enemies_source)
        block = enemies_source[start:end]
        super_name = re.search(r"super\(\)\.__init__\(\s*name\s*=\s*(['\"])(.*?)\1", block)
        if super_name:
            names.add(super_name.group(2))
        for assigned_name in re.finditer(r"self\.name\s*=\s*(['\"])(.*?)\1", block):
            names.add(assigned_name.group(2))

    return names
