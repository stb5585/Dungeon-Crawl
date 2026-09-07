"""
Generate a Tiled tileset from the packaged runtime map images.

Usage:
  python3 tools/generate_tiled_tileset.py
"""

from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAP_FILES_DIR = PROJECT_ROOT / "src" / "core" / "data" / "maps"


APPENDED_TILE_STEMS = (
    "funhouse_teleporter",
    "funhouse_path",
    "funhouse_mimic_chest",
    "mirror_wall",
    "golden_chalice",
    "incubus_lair",
    "merzhin_room",
    "trap_room",
    "anti_magic_switch",
    "circe_room",
    "funhouse_empty_path",
    "bone_pile_tile",
    "broken_gear_tile",
    "crystal_cluster_tile",
    "fungus_patch_tile",
    "jester_blocker",
    "root_growth_tile",
    "rubble_tile",
    "funhouse_boundary_wall",
)
APPENDED_TILE_STEM_SET = set(APPENDED_TILE_STEMS)

# Mapping from image filename (without .png) to MapTile class name
TILE_MAPPING = {
    "wall": "Wall",
    "fake_wall": "FakeWall",
    "stairs_up": "StairsUp",
    "stairs_down": "StairsDown",
    "ladder_up": "LadderUp",
    "ladder_down": "LadderDown",
    "cave_path_0": "CavePath0",
    "cave_path_1": "CavePath1",
    "cave_path_2": "CavePath2",
    "empty_cave_path": "EmptyCavePath",
    "rubble_tile": "RubbleTile",
    "root_growth_tile": "RootGrowthTile",
    "fungus_patch_tile": "FungusPatchTile",
    "crystal_cluster_tile": "CrystalClusterTile",
    "bone_pile_tile": "BonePileTile",
    "broken_gear_tile": "BrokenGearTile",
    "boss_path": "BossPath",
    "fire_path": "FirePath",
    "fire_path_special": "FirePathSpecial",
    "sandworm_lair": "SandwormLair",
    "underground_spring": "UndergroundSpring",
    "anti_magic_switch": "AntiMagicSwitch",
    "boulder": "Boulder",
    "portal": "Portal",
    "rotator": "Rotator",
    "trap_room": "Trap",
    "unlocked_chest": "UnlockedChestRoom",
    "unlocked_chest_2": "UnlockedChestRoom2",
    "locked_chest": "LockedChestRoom",
    "locked_chest_2": "LockedChestRoom2",
    "door": "LockedDoor",
    "ore_vault_door": "OreVaultDoor",
    "warning_tile": "WarningTile",
    "unobtainium": "UnobtainiumRoom",
    "relic_room": "RelicRoom",
    "dead_body": "DeadBody",
    "final_blocker": "FinalBlocker",
    "final_room": "FinalRoom",
    "secret_shop": "SecretShop",
    "ultimate_armor_room": "UltimateArmorShop",
    "warp_point": "WarpPoint",
    "funhouse_empty_path": "FunhouseEmptyPath",
    "funhouse_path": "FunhousePath",
    "funhouse_mimic_chest": "FunhouseMimicChest",
    "funhouse_teleporter": "FunhouseTeleporter",
    "golden_chalice": "GoldenChaliceRoom",
    "jester_blocker": "FunhouseEmptyPath",
    "mirror_wall": "FunhouseWall",
    "funhouse_boundary_wall": "FunhouseBoundaryWall",
    "minotaur_room": "MinotaurBossRoom",
    "barghest_room": "BarghestBossRoom",
    "circe_room": "CirceBossRoom",
    "incubus_lair": "IncubusLair",
    "merzhin_room": "MerzhinBossRoom",
    "pseudodragon_room": "PseudodragonBossRoom",
    "nightmare_room": "NightmareBossRoom",
    "cockatrice_room": "CockatriceBossRoom",
    "wendigo_room": "WendigoBossRoom",
    "iron_golem_room": "IronGolemBossRoom",
    "golem_room": "GolemBossRoom",
    "jester_room": "JesterBossRoom",
    "domingo_room": "DomingoBossRoom",
    "red_dragon_room": "RedDragonBossRoom",
    "cerberus_room": "CerberusBossRoom",
    "devil_room": "FinalBossRoom",
}


def generate_tileset():
    tileset_dir = MAP_FILES_DIR / "tileset"
    output_file = MAP_FILES_DIR / "dungeon_tiles.tsx"

    if not tileset_dir.exists():
        raise FileNotFoundError(f"Tileset directory not found: {tileset_dir}")

    # Scan for PNG images
    all_images = sorted(tileset_dir.glob("*.png"))
    image_by_stem = {image.stem: image for image in all_images}
    images = [
        *[image for image in all_images if image.stem not in APPENDED_TILE_STEM_SET],
        *[image_by_stem[stem] for stem in APPENDED_TILE_STEMS if stem in image_by_stem],
    ]
    if not images:
        raise FileNotFoundError(f"No PNG images found in {tileset_dir}")

    tiles_xml = []
    tile_width = None
    tile_height = None

    for idx, img_path in enumerate(images):
        stem = img_path.stem
        tile_type = TILE_MAPPING.get(stem)

        if not tile_type:
            print(f"Warning: No mapping for {stem}.png, skipping")
            continue

        # Read actual image dimensions
        try:
            img = Image.open(img_path)
            width, height = img.size
        except Exception as e:
            print(f"Error reading {img_path}: {e}, using 32x32")
            width, height = 32, 32

        # Track consistent dimensions
        if tile_width is None:
            tile_width = width
            tile_height = height

        tiles_xml.append(
            f'  <tile id="{idx}" type="{tile_type}">\n'
            f'    <image width="{width}" height="{height}" '
            f'source="tileset/{img_path.name}"/>\n'
            f"  </tile>"
        )

    if tile_width is None:
        tile_width = tile_height = 32

    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<tileset version="1.10" tiledversion="1.10.2" name="DungeonTiles" '
        f'tilewidth="{tile_width}" tileheight="{tile_height}" '
        f'tilecount="{len(tiles_xml)}" columns="0">\n'
        ' <grid orientation="orthogonal" width="1" height="1"/>\n' + "\n".join(tiles_xml) + "\n"
        "</tileset>"
    )

    output_file.write_text(xml_content, encoding="utf-8")
    print(f"Created tileset: {output_file}")
    print(f"Total tiles: {len(tiles_xml)}")
    print(f"Tile dimensions: {tile_width}x{tile_height}")


if __name__ == "__main__":
    generate_tileset()
