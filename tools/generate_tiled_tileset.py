"""
Generate a Tiled tileset (.tsx) from images in map_files/tileset/.

Usage:
  python3 tools/generate_tiled_tileset.py
"""

import json
from pathlib import Path
from PIL import Image


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
    "boss_path": "BossPath",
    "fire_path": "FirePath",
    "fire_path_special": "FirePathSpecial",
    "sandworm_lair": "SandwormLair",
    "underground_spring": "UndergroundSpring",
    "boulder": "Boulder",
    "portal": "Portal",
    "rotator": "Rotator",
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
    "minotaur_room": "MinotaurBossRoom",
    "barghest_room": "BarghestBossRoom",
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
    tileset_dir = Path("map_files/tileset")
    output_file = Path("map_files/dungeon_tiles.tsx")
    
    if not tileset_dir.exists():
        raise FileNotFoundError(f"Tileset directory not found: {tileset_dir}")
    
    # Scan for PNG images
    images = sorted(tileset_dir.glob("*.png"))
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
        
        # Use absolute path
        abs_path = img_path.resolve()
        tiles_xml.append(
            f'  <tile id="{idx}" type="{tile_type}">\n'
            f'    <image width="{width}" height="{height}" source="{abs_path}"/>\n'
            f'  </tile>'
        )
    
    if tile_width is None:
        tile_width = tile_height = 32
    
    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<tileset version="1.10" tiledversion="1.10.2" name="DungeonTiles" '
        f'tilewidth="{tile_width}" tileheight="{tile_height}" '
        f'tilecount="{len(tiles_xml)}" columns="0">\n'
        ' <grid orientation="orthogonal" width="1" height="1"/>\n'
        + '\n'.join(tiles_xml) + '\n'
        '</tileset>'
    )
    
    output_file.write_text(xml_content, encoding="utf-8")
    print(f"Created tileset: {output_file}")
    print(f"Total tiles: {len(tiles_xml)}")
    print(f"Tile dimensions: {tile_width}x{tile_height}")


if __name__ == "__main__":
    generate_tileset()
