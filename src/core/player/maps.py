"""Tiled and legacy player-map loading helpers."""

import json
import os
import xml.etree.ElementTree as ET


def _parse_tiled_properties(props):
    if not props:
        return {}
    return {prop.get("name"): prop.get("value") for prop in props}

def _tiled_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)

def _extract_tile_type(tile_data):
    tile_type = tile_data.get("type") or tile_data.get("class")
    if tile_type:
        return tile_type
    props = _parse_tiled_properties(tile_data.get("properties"))
    return props.get("tile") or props.get("type") or props.get("class")

def _select_tiled_gameplay_layer(layers):
    visible_tile_layers = [
        layer
        for layer in layers
        if layer.get("type") == "tilelayer" and layer.get("visible", True)
    ]
    if not visible_tile_layers:
        return None

    for layer in visible_tile_layers:
        props = _parse_tiled_properties(layer.get("properties"))
        if layer.get("name") == "Tiles" or _tiled_bool(props.get("gameplay"), False):
            return layer

    for layer in visible_tile_layers:
        props = _parse_tiled_properties(layer.get("properties"))
        if not _tiled_bool(props.get("decorative"), False):
            return layer

    return visible_tile_layers[0]

def _load_tiled_tileset(tileset_entry, map_dir):
    if "source" in tileset_entry:
        tileset_path = os.path.join(map_dir, tileset_entry["source"])

        # Check if it's XML or JSON based on file content
        with open(tileset_path, "r", encoding="utf-8") as tileset_file:
            first_line = tileset_file.readline().strip()
            tileset_file.seek(0)  # Reset to beginning

            if first_line.startswith("<?xml") or first_line.startswith("<tileset"):
                # Parse XML tileset
                tree = ET.parse(tileset_file)
                root = tree.getroot()

                # Convert XML to the expected dict format
                tileset_data = {"tiles": []}
                for tile_elem in root.findall("tile"):
                    tile_id = int(tile_elem.get("id", 0))
                    tile_type = tile_elem.get("type", "")
                    if tile_type:
                        tileset_data["tiles"].append({
                            "id": tile_id,
                            "type": tile_type
                        })
                return tileset_data, tileset_entry["firstgid"]
            else:
                # Parse JSON tileset
                tileset_data = json.load(tileset_file)
                return tileset_data, tileset_entry["firstgid"]

    return tileset_entry, tileset_entry.get("firstgid", 1)

def _load_tiled_map(map_file, z, map_tiles):
    with open(map_file, "r", encoding="utf-8") as file_handle:
        map_data = json.load(file_handle)

    map_dir = os.path.dirname(map_file)
    map_props = _parse_tiled_properties(map_data.get("properties"))
    default_tile = map_props.get("default_tile", "Wall")

    gid_to_type = {}
    for tileset_entry in map_data.get("tilesets", []):
        tileset_data, first_gid = _load_tiled_tileset(tileset_entry, map_dir)
        for tile in tileset_data.get("tiles", []):
            tile_type = _extract_tile_type(tile)
            if not tile_type:
                continue
            gid_to_type[first_gid + tile["id"]] = tile_type

    tile_layer = _select_tiled_gameplay_layer(map_data.get("layers", []))
    if not tile_layer:
        raise ValueError(f"No tile layer found in {map_file}")

    width = map_data.get("width", 0)
    height = map_data.get("height", 0)
    infinite = _tiled_bool(map_data.get("infinite"), False)
    world_dict = {}

    def add_tile(x, y, gid):
        if gid == 0:
            tile_name = default_tile
        else:
            tile_name = gid_to_type.get(gid)
        if not tile_name:
            raise ValueError(f"Missing tile mapping for gid {gid} in {map_file}")
        tile = getattr(map_tiles, tile_name)(x, y, z)
        world_dict[(x, y, z)] = tile

    if "data" in tile_layer:
        data = tile_layer["data"]
        for y in range(height):
            row_offset = y * width
            for x in range(width):
                add_tile(x, y, data[row_offset + x])
    else:
        for chunk in tile_layer.get("chunks", []):
            chunk_width = chunk["width"]
            chunk_height = chunk["height"]
            chunk_data = chunk["data"]
            for y in range(chunk_height):
                row_offset = y * chunk_width
                for x in range(chunk_width):
                    map_x = chunk["x"] + x
                    map_y = chunk["y"] + y
                    if not infinite and width and height and (map_x >= width or map_y >= height):
                        continue
                    add_tile(map_x, map_y, chunk_data[row_offset + x])

    return world_dict
