"""
Convert tab-delimited map text files into Tiled JSON maps.

Usage:
  python3 tools/convert_maps_to_tiled_json.py
  python3 tools/convert_maps_to_tiled_json.py --input map_files --force
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


# Mapping from tile class name to image filename (without .png)
# This must match the order used in generate_tiled_tileset.py
TILE_NAME_TO_IMAGE = {
    "Wall": "wall",
    "FakeWall": "fake_wall",
    "StairsUp": "stairs_up",
    "StairsDown": "stairs_down",
    "LadderUp": "ladder_up",
    "LadderDown": "ladder_down",
    "CavePath0": "cave_path_0",
    "CavePath1": "cave_path_1",
    "CavePath2": "cave_path_2",
    "EmptyCavePath": "empty_cave_path",
    "BossPath": "boss_path",
    "FirePath": "fire_path",
    "FirePathSpecial": "fire_path_special",
    "SandwormLair": "sandworm_lair",
    "UndergroundSpring": "underground_spring",
    "Boulder": "boulder",
    "Portal": "portal",
    "Rotator": "rotator",
    "UnlockedChestRoom": "unlocked_chest",
    "UnlockedChestRoom2": "unlocked_chest_2",
    "LockedChestRoom": "locked_chest",
    "LockedChestRoom2": "locked_chest_2",
    "LockedDoor": "door",
    "OreVaultDoor": "ore_vault_door",
    "WarningTile": "warning_tile",
    "UnobtainiumRoom": "unobtainium",
    "RelicRoom": "relic_room",
    "DeadBody": "dead_body",
    "FinalBlocker": "final_blocker",
    "FinalRoom": "final_room",
    "SecretShop": "secret_shop",
    "UltimateArmorShop": "ultimate_armor_room",
    "WarpPoint": "warp_point",
    "MinotaurBossRoom": "minotaur_room",
    "BarghestBossRoom": "barghest_room",
    "PseudodragonBossRoom": "pseudodragon_room",
    "NightmareBossRoom": "nightmare_room",
    "CockatriceBossRoom": "cockatrice_room",
    "WendigoBossRoom": "wendigo_room",
    "IronGolemBossRoom": "iron_golem_room",
    "GolemBossRoom": "golem_room",
    "JesterBossRoom": "jester_room",
    "DomingoBossRoom": "domingo_room",
    "RedDragonBossRoom": "red_dragon_room",
    "CerberusBossRoom": "cerberus_room",
    "FinalBossRoom": "devil_room",
}


def _build_gid_map_from_tileset() -> dict[str, int]:
    """Build a map from tile class name to GID in dungeon_tiles.tsx."""
    # Read the external tileset to determine GID order
    tileset_dir = Path("map_files/tileset")
    image_files = sorted(tileset_dir.glob("*.png"))
    
    gid_map = {}
    for gid_idx, img_path in enumerate(image_files):
        stem = img_path.stem
        # Find the tile class name that maps to this image
        for tile_class, img_name in TILE_NAME_TO_IMAGE.items():
            if img_name == stem:
                gid_map[tile_class] = gid_idx + 1  # GIDs start at 1
                break
    
    return gid_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert map_level_*.txt to Tiled JSON maps.")
    parser.add_argument(
        "--input",
        default="map_files",
        help="Directory containing map_level_*.txt files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing map_level_*.json files.",
    )
    return parser.parse_args()
    parser = argparse.ArgumentParser(description="Convert map_level_*.txt to Tiled JSON maps.")
    parser.add_argument(
        "--input",
        default="map_files",
        help="Directory containing map_level_*.txt files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing map_level_*.json files.",
    )
    return parser.parse_args()


def read_txt_map(path: Path) -> tuple[list[list[str]], int, int]:
    rows = [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if line]
    grid = [row.split("\t") for row in rows]
    if not grid:
        raise ValueError(f"{path} is empty")
    width = len(grid[0])
    for idx, row in enumerate(grid):
        if len(row) != width:
            raise ValueError(f"{path} row {idx + 1} has {len(row)} columns; expected {width}")
    height = len(grid)
    return grid, width, height


def build_map_json(grid: list[list[str]], width: int, height: int, name: str, gid_map: dict[str, int]) -> dict:
    """Build a Tiled JSON map that references the external dungeon_tiles.tsx tileset."""
    data = [gid_map.get(tile_name, 1) for row in grid for tile_name in row]  # Default to gid 1 (Wall) if unknown

    return {
        "compressionlevel": -1,
        "height": height,
        "infinite": False,
        "layers": [
            {
                "id": 1,
                "name": "Tiles",
                "type": "tilelayer",
                "visible": True,
                "opacity": 1,
                "width": width,
                "height": height,
                "x": 0,
                "y": 0,
                "data": data,
            }
        ],
        "nextlayerid": 2,
        "nextobjectid": 1,
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "tiledversion": "1.10.2",
        "tileheight": 32,
        "tilewidth": 32,
        "type": "map",
        "version": "1.10",
        "width": width,
        "tilesets": [
            {
                "firstgid": 1,
                "source": "dungeon_tiles.tsx"
            }
        ],
        "properties": [
            {"name": "default_tile", "type": "string", "value": "Wall"}
        ],
    }


def convert_file(path: Path, force: bool, gid_map: dict[str, int]) -> Path | None:
    grid, width, height = read_txt_map(path)
    name = path.stem
    out_path = path.with_suffix(".json")
    if out_path.exists() and not force:
        return None
    map_json = build_map_json(grid, width, height, name, gid_map)
    out_path.write_text(json.dumps(map_json, indent=2), encoding="utf-8")
    return out_path


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input)
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    txt_files = sorted(input_dir.glob("map_level_*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No map_level_*.txt files found in {input_dir}")

    # Build the GID map once from the external tileset
    gid_map = _build_gid_map_from_tileset()
    
    created = []
    for path in txt_files:
        out_path = convert_file(path, args.force, gid_map)
        if out_path:
            created.append(out_path)

    if created:
        print("Created JSON maps:")
        for out_path in created:
            print(f"- {out_path}")
    else:
        print("No JSON maps created (already existed). Use --force to overwrite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
