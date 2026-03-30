"""
This module defines the player character and its attributes and actions.
"""

import glob
import json
import os
import random
import xml.etree.ElementTree as ET

from .constants import (
    BASE_CRIT_PER_POINT,
    EXP_SCALE_BASE,
    LEVELUP_ATK_LUCK_FACTOR,
    LEVELUP_DEF_LUCK_FACTOR,
    LEVELUP_LUCK_DIVISOR_BASE,
    LEVELUP_LUCK_FACTOR_HP_MP,
    LEVELUP_MAG_LUCK_FACTOR,
    LEVELUP_MDEF_LUCK_FACTOR,
    LEVELUP_STAT_DIVISOR,
    TOWN_LOCATION,
)

import numpy

from . import abilities, enemies
from .character import Character
from .items import remove_equipment
from .save_system import SaveManager


DIRECTIONS = {
    "north": {
        "move": (0, -1),
        "char": "\u2191"
        },
    "south": {
        "move": (0, 1),
        "char": "\u2193"
        },
    "east": {
        "move": (1, 0),
        "char": "\u2192"
        },
    "west": {"move": (-1, 0),
             "char": "\u2190"
             }
    }


REALM_OF_CAMBION_LEVEL = 8


def load_char(char=None, filename=None, is_tmp=False):
    """
    Initializes the character based on the save file using the data-driven save system.

    Args:
        char: Optional character instance; if provided, loads from tmp_files/<name>.save
        filename: Explicit filename to load (e.g., "myhero.save")
        is_tmp: Whether to load from tmp_files instead of save_files
    """
    target_filename = filename
    target_tmp = is_tmp

    if char and not filename:
        target_filename = f"{str(char.name).lower()}.save"
        target_tmp = True

    if not target_filename:
        return None

    # Skip tiles when loading for transform (only need character stats)
    player = SaveManager.load_player(target_filename, is_tmp=target_tmp, skip_tiles=True)
    if player and target_tmp:
        try:
            os.remove(f"tmp_files/{target_filename}")
        except FileNotFoundError:
            pass
    return player


def _parse_tiled_properties(props):
    if not props:
        return {}
    return {prop.get("name"): prop.get("value") for prop in props}


def _extract_tile_type(tile_data):
    tile_type = tile_data.get("type") or tile_data.get("class")
    if tile_type:
        return tile_type
    props = _parse_tiled_properties(tile_data.get("properties"))
    return props.get("tile") or props.get("type") or props.get("class")


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

    tile_layer = next(
        (layer for layer in map_data.get("layers", []) if layer.get("type") == "tilelayer"),
        None,
    )
    if not tile_layer:
        raise ValueError(f"No tile layer found in {map_file}")

    width = map_data.get("width", 0)
    height = map_data.get("height", 0)
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
                    if map_x < 0 or map_y < 0:
                        continue
                    if width and height and (map_x >= width or map_y >= height):
                        continue
                    add_tile(map_x, map_y, chunk_data[row_offset + x])

    return world_dict


class Player(Character):
    """
    Player character class
    Health is defined based on initial value and is modified by the constitution stat
    Mana is defined based on the initial value and is modified by the intelligence stat

    encumbered(bool): signifies whether player is over carry weight
    power_up(bool): switch for power-up for retrieving Power Core
    """

    ABSORB_ESSENCE_MAX_PROCS_PER_FLOOR = 3
    ABSORB_ESSENCE_MAX_PROCS_PER_ENEMY_PER_FLOOR = 1
    ABSORB_ESSENCE_MAX_STAT_GAINS = 12
    ABSORB_ESSENCE_MAX_HEALTH_GAINS = 60
    ABSORB_ESSENCE_MAX_MANA_GAINS = 60
    ABSORB_ESSENCE_MAX_LEVEL_GAINS = 3

    def __init__(self, location_x, location_y, location_z, level, health, mana, stats, combat, gold, resistance):
        super().__init__(name="", health=health, mana=mana, stats=stats, combat=combat)
        self.location_x = location_x
        self.location_y = location_y
        self.location_z = location_z
        self.facing = "east"
        self.previous_location = TOWN_LOCATION  # starts at town location
        self.state = "normal"
        self.exp_scale = EXP_SCALE_BASE
        self.gold = gold
        self.level = level
        self.resistance = resistance
        self.inventory = {}
        self.special_inventory = {}
        self.world_dict = {}
        self.quest_dict = {'Bounty': {}, 'Main': {}, 'Side': {}}
        self.kill_dict = {}
        self.storage = {}
        self.warp_point = False
        self.quit = False
        self.teleport = None
        self.familiar = None
        self.summons = {}
        self.transform_type = self.cls
        self.encumbered = False
        self.power_up = False
        # Dwarf Gluttony (racial sin): out-of-combat hangover that can affect initiative
        # for a number of steps after using combat consumables.
        self.dwarf_hangover_steps = 0
        self.absorb_essence_state = {
            'floor': self.location_z,
            'procs_this_floor': 0,
            'procs_by_enemy': {},
            'stat_gains': {
                'strength': 0,
                'intel': 0,
                'wisdom': 0,
                'con': 0,
                'charisma': 0,
                'dex': 0,
            },
            'health_gains': 0,
            'mana_gains': 0,
            'level_gains': 0,
            'dragon_gold_claimed': False,
        }

    def __str__(self):
        return (
            f"{self.name} | "
            f"Health: {self.health.current}/{self.health.max} | "
            f"Mana: {self.mana.current}/{self.mana.max}"
            )

    def exp_gain_multiplier(self) -> float:
        """Race-based experience gain multiplier (used by combat and quests)."""
        try:
            from .constants import HUMAN_EXP_MULTIPLIER, HALF_GIANT_EXP_MULTIPLIER
            race_name = getattr(getattr(self, "race", None), "name", None)
            if race_name == "Human":
                return HUMAN_EXP_MULTIPLIER
            if race_name == "Half Giant":
                return HALF_GIANT_EXP_MULTIPLIER
        except Exception:
            pass
        return 1.0

    def minimap(self):
        """
        Function that allows the player_char to view the current dungeon level in terminal
        20 x 20 grid
        """
        def is_direction_visible_from_current(direction: str) -> bool:
            current_tile = self.world_dict.get((self.location_x, self.location_y, self.location_z))
            if not current_tile:
                return True

            blocked = getattr(current_tile, 'blocked', None)
            if blocked and blocked.lower() == direction:
                if hasattr(current_tile, 'open') and getattr(current_tile, 'open', False):
                    return True
                return False

            return True

        visible_adjacent = set()
        adjacent_dirs = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
        }
        for direction, (dx, dy) in adjacent_dirs.items():
            if not is_direction_visible_from_current(direction):
                continue
            pos = (self.location_x + dx, self.location_y + dy, self.location_z)
            if pos in self.world_dict:
                visible_adjacent.add((pos[0], pos[1]))

        map_size = (20, 20)
        map_array = numpy.zeros(map_size).astype(str)
        for tile in self.world_dict:
            if self.location_z == tile[2]:
                tile_x, tile_y = tile[1], tile[0]
                if self.world_dict[tile].near or self.cls.name == "Seeker" or (tile[0], tile[1]) in visible_adjacent:
                    if 'Stairs' in str(self.world_dict[tile]) or 'Ladder' in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u25E3"
                    elif "Door" in str(self.world_dict[tile]):
                        # Special handling for OreVaultDoor - only show as door if detected or open
                        if "OreVaultDoor" in str(self.world_dict[tile]):
                            if self.world_dict[tile].open:
                                map_array[tile_x][tile_y] = "."
                            elif hasattr(self.world_dict[tile], 'detected') and self.world_dict[tile].detected:
                                map_array[tile_x][tile_y] = "\u2593"
                            else:
                                # Show as wall if not detected
                                map_array[tile_x][tile_y] = "#"
                        else:
                            map_array[tile_x][tile_y] = "\u2593" if not self.world_dict[tile].open else "."
                    elif 'Wall' in str(self.world_dict[tile]):
                        if "FakeWall" in str(self.world_dict[tile]) and self.world_dict[tile].visited:
                            map_array[tile_x][tile_y] = ":"
                        else:
                            map_array[tile_x][tile_y] = "#"
                    elif 'Chest' in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u25A1" if self.world_dict[tile].open else "\u25A0"
                    elif 'Relic' in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u25CB" if self.world_dict[tile].read else "\u25C9"
                    elif 'BossRoom' in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u2620" if not self.world_dict[tile].defeated else "."
                    elif "SecretShop" in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u2302"
                    elif "WarpPoint" in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u25C9"
                    else:
                        map_array[tile_x][tile_y] = "."
        map_array[self.location_y][self.location_x] = DIRECTIONS[self.facing]["char"]
        map_array[map_array == "0.0"] = " "
        map_array = numpy.insert(map_array, 0, numpy.zeros(map_array.shape[1]), 0)
        map_array[map_array == "0.0"] = "#"
        map_array = numpy.vstack([map_array, numpy.zeros(map_array.shape[1])])
        map_array[map_array == "0.0"] = "#"
        map_array = numpy.insert(map_array, 0, numpy.zeros(map_array.shape[0]), 1)
        map_array[map_array == "0.0"] = "#"
        map_array = numpy.append(map_array, numpy.zeros(map_array.shape[0]).reshape(-1, 1), 1)
        map_array[map_array == "0.0"] = "#"
        map_str = map_str = "\n".join(" ".join(row) for row in map_array)
        return map_str

    def load_tiles(self):
        """Parses a file that describes the world space into the _world object"""
        from . import map_tiles
            
        world_dict = {}
        map_files = glob.glob('map_files/map_level_*')
        files_by_level = {}
        for map_file in map_files:
            base_name = os.path.basename(map_file)
            root_name, ext = os.path.splitext(base_name)
            if ext not in {".txt", ".json"}:
                continue
            try:
                z = int(root_name.split('_')[-1])
            except ValueError:
                continue
            existing = files_by_level.get(z)
            if not existing or (ext == ".json" and existing["ext"] != ".json"):
                files_by_level[z] = {"path": map_file, "ext": ext}

        # Optional side-area map: funhouse challenge level (level 4 boss area).
        funhouse_path = os.path.join('map_files', 'map_funhouse.json')
        if os.path.exists(funhouse_path) and 7 not in files_by_level:
            files_by_level[7] = {"path": funhouse_path, "ext": ".json"}

        cambion_path = os.path.join('map_files', 'map_realm_cambion.json')
        if os.path.exists(cambion_path) and REALM_OF_CAMBION_LEVEL not in files_by_level:
            files_by_level[REALM_OF_CAMBION_LEVEL] = {"path": cambion_path, "ext": ".json"}

        for z in sorted(files_by_level):
            map_file = files_by_level[z]["path"]
            ext = files_by_level[z]["ext"]
            if ext == ".json":
                world_dict.update(_load_tiled_map(map_file, z, map_tiles))
                continue
            with open(map_file, 'r', encoding="utf-8") as f:
                rows = f.readlines()
            x_max = len(rows[0].split('\t'))  # Assumes all rows contain the same number of tabs
            for y, _ in enumerate(rows):
                cols = rows[y].split('\t')
                for x in range(x_max):
                    tile_name = cols[x].replace('\n', '')  # Windows users may need to replace '\r\n'
                    tile = getattr(map_tiles, tile_name)(x, y, z)
                    world_dict[(x, y, z)] = tile

        self.world_dict = world_dict

    def additional_actions(self, action_list):
        """
        Controls the listed options during combat
        """
        if self.transform_type:
            if self.cls.name in ["Druid", "Lycan"]:
                action_list.insert(1, "Transform")
            if self.transform_type == self.cls and self.class_effects["Power Up"].duration < 5:
                action_list.append("Untransform")
                for action in ["Flee", "Use Item"]:
                    if action in action_list:
                        action_list.pop(action_list.index(action))
        if self.is_disarmed():
            action_list.insert(1, "Pickup Weapon")
        if "Summon" in self.spellbook["Skills"] and \
            any([x.is_alive() for x in self.summons.values()]) and \
                not self.abilities_suppressed():
            action_list.insert(1, "Summon")
        # Note: Totem was previously duplicated here for Shaman/Soulcatcher
        # It's already accessible via the Skills submenu, so no need for separate action
        return action_list

    def has_relics(self):
        relics = ["Triangulus", "Quadrata", "Hexagonum", "Luna", "Polaris", "Infinitas"]
        return all(item in self.special_inventory for item in relics)

    def level_exp(self):
        """
        total experience required to level up for current level; different from exp_to_gain
        """
        return (self.exp_scale ** self.level.pro_level) * self.level.level

    def player_level(self):
        """
        total player level (cumulative across all promotions)
        Base class: levels 1-30
        First promotion: levels 31-60 (reset to 1, gain 30 more)
        Second promotion: levels 61-110 (reset to 1, gain 50 more)
        """
        if self.level.pro_level == 1:
            return self.level.level
        elif self.level.pro_level == 2:
            return 30 + self.level.level
        else:  # pro_level == 3
            return 60 + self.level.level

    def max_level(self):
        return any([(self.level.level == 50 and self.level.pro_level == 3),
                    (self.level.level == 30 and self.level.pro_level < 3)])

    def in_town(self):
        return (self.location_x, self.location_y, self.location_z) == TOWN_LOCATION

    def to_town(self):
        (self.location_x, self.location_y, self.location_z) = TOWN_LOCATION

    def exit_funhouse(self):
        """Exit the funhouse and return to the saved location."""
        if hasattr(self, 'funhouse_return') and self.funhouse_return:
            self.location_x, self.location_y, self.location_z, self.facing = self.funhouse_return
            self.funhouse_return = None
        else:
            # Fallback: return to town if no saved location
            self.to_town()

    def enter_realm_of_cambion(self, x, y, z, facing="east"):
        """Enter the Realm of Cambion from the current location."""
        self.cambion_return = (
            self.location_x,
            self.location_y,
            self.location_z,
            self.facing,
        )
        self.location_x = x
        self.location_y = y
        self.location_z = z
        self.facing = facing
        self.anti_magic_active = True

    def exit_realm_of_cambion(self):
        """Exit the Realm of Cambion and return to the saved location."""
        if hasattr(self, 'cambion_return') and self.cambion_return:
            self.location_x, self.location_y, self.location_z, self.facing = self.cambion_return
            self.cambion_return = None
        self.anti_magic_active = False

    def in_realm_of_cambion(self):
        return self.location_z == REALM_OF_CAMBION_LEVEL

    def town_heal(self):
        self.state = 'normal'
        self.health.current = self.health.max
        self.mana.current = self.mana.max
        for summon in self.summons.values():
            summon.health.current = summon.health.max
            summon.mana.current = summon.mana.max

    def usable_item(self, item):
        if self.in_town():
            cat_list = ["Stat"]
        else:
            cat_list = ['Health', 'Mana', 'Elixir', 'Stat']
        if item.subtyp in cat_list or item.name == "Sanctuary Scroll":
            return True
        return False

    def usable_abilities(self, typ):
        if self.abilities_suppressed():
            return False
        for ability in self.spellbook[typ].values():
            if not ability.passive and ability.cost <= self.mana.current:
                if any([ability.name == 'Shield Slam' and self.equipment['OffHand'].subtyp != 'Shield',
                        ability.name == "Mortal Strike" and self.equipment['Weapon'].handed == 1]):
                    continue
                return True
        # should only reach if not enough mana to cast spells; lasts for 4 turns
        if self.cls.name == "Wizard" and self.power_up and typ == "Spells":
            self.class_effects["Power Up"].active = True
            self.class_effects["Power Up"].duration = 4
            return True
        return False
    
    def max_weight(self):
        return self.stats.strength * 10 * self.level.pro_level
    
    def current_weight(self):
        weight = 0
        for item in self.equipment.values():
            weight += item.weight
        for item in self.inventory.values():
            weight += item[0].weight * len(item)
        for item in self.special_inventory.values():
            weight += item[0].weight * len(item)
        return round(weight, 1)

    def game_quit(self, game=None, confirm_popup=None, textbox=None):
        """
        Function that allows for exiting the game. UI logic must be provided by the frontend.
        Args:
            game: Game instance (optional, for UI context)
            confirm_popup: Optional ConfirmPopupMenu UI component or factory
            textbox: Optional TextBox UI component
        Returns True if quit confirmed, else None.
        """
        confirm_str = "Are you sure you want to quit? Any unsaved data will be lost."
        popup = None
        # If confirm_popup is a class/factory, instantiate with message; else assume it's already an instance
        if confirm_popup and callable(confirm_popup):
            popup = confirm_popup(game, header_message=confirm_str)
        elif confirm_popup:
            popup = confirm_popup
        if popup and popup.navigate_popup():
            if textbox:
                textbox.print_text_in_rectangle(f"Goodbye, {self.name}!")
            self.quit = True
            return True

    def character_menu(self, game=None, menu=None, textbox=None, actions_dict=None, ui_factory=None):
        """
        Lists character options. UI logic must be provided by the frontend.
        Args:
            game: Game instance (optional, for UI context)
            menu: Optional menu UI component
            textbox: Optional TextBox UI component
            actions_dict: Optional dict of action callbacks
            ui_factory: Optional dict of UI component factory functions/classes
        Returns True if quit, else None.
        """
        if not (menu and actions_dict):
            return
        jump_skill = None
        skills = getattr(self, "spellbook", {}).get("Skills", {})
        if "Jump" in skills:
            jump_skill = skills["Jump"]
        else:
            for skill in skills.values():
                if getattr(skill, "name", "") == "Jump":
                    jump_skill = skill
                    break

        has_jump_mods = bool(jump_skill and hasattr(jump_skill, "modifications"))

        totem_skill = None
        skills = getattr(self, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            totem_skill = skills["Totem"]
        else:
            for skill in skills.values():
                if getattr(skill, "name", "") == "Totem":
                    totem_skill = skill
                    break
        has_totem_aspects = bool(totem_skill and hasattr(totem_skill, "get_unlocked_aspects"))

        character_options = [
            actions_dict.get('ViewInventory'),
            actions_dict.get("ViewKeyItems"),
            actions_dict.get("Equipment"),
            actions_dict.get('Specials'),
            actions_dict.get('ViewQuests'),
        ]
        options = ["Inventory", "Key Items", "Equipment", "Specials", "Quests"]

        if has_jump_mods:
            character_options.append(actions_dict.get("JumpMods"))
            options.append("Jump Mods")

        if has_totem_aspects:
            character_options.append(actions_dict.get("TotemAspects"))
            options.append("Totem Aspects")

        character_options.extend(["Exit Menu", actions_dict.get('Quit')])
        options.extend(["Exit Menu", "Quit Game"])
        menu.set_options(options)
        menu.draw_all()
        while True:
            character_idx = menu.navigate_menu()
            action = character_options[character_idx]
            if action == "Exit Menu":
                break
            if action is None and textbox:
                textbox.print_text_in_rectangle("Your class does not have a special menu.\n")
            elif isinstance(action, dict) and 'method' in action:
                # Use UI factory to create components if provided
                if ui_factory:
                    if action['name'] == 'Inventory':
                        inv_popup = ui_factory['InventoryPopup'](game, "Inventory")
                        confirm_popup = ui_factory['ConfirmPopup']
                        useitembox = ui_factory['TextBox'](game)
                        action['method'](self, game, inv_popup=inv_popup, confirm_popup=confirm_popup, useitembox=useitembox)
                    elif action['name'] == 'Key Items':
                        inv_popup = ui_factory['InventoryPopup'](game, "Key Items")
                        action['method'](self, game, inv_popup=inv_popup)
                    elif action['name'] == 'Equipment':
                        popup = ui_factory['EquipmentPopup'](game, action['name'], 25)
                        action['method'](self, game, popup=popup)
                    elif action['name'] == 'Specials':
                        popup = ui_factory['SpecialsPopup'](game, action['name'])
                        action['method'](self, game, popup=popup)
                    elif action['name'] == 'Quests':
                        popup = ui_factory['QuestsPopup'](game, action['name'])
                        action['method'](self, game, popup=popup)
                    elif action['name'] == 'Jump Mods':
                        popup = ui_factory['JumpModsPopup'](game, action['name'])
                        action['method'](self, game, jump_popup=popup)
                    elif action['name'] == 'Totem Aspects':
                        popup = ui_factory['TotemAspectsPopup'](game, action['name'])
                        action['method'](self, game, totem_popup=popup)
                    elif action['name'] == 'Quit':
                        confirm_popup = ui_factory['ConfirmPopup']
                        quit_textbox = ui_factory['TextBox'](game)
                        action['method'](self, game, confirm_popup=confirm_popup, textbox=quit_textbox)
                    else:
                        # For other actions (like Summons, Quit), call with game only
                        action['method'](self, game)
                else:
                    # Fallback: call without UI components (may raise error)
                    action['method'](self, game)
                if self.quit:
                    return True
            menu.draw_all()
            menu.refresh_all()

    def status_str(self):
        """
        Returns a string with the status of the player
        """
        status_message = (f"{'Hit Points:':13}{' ':1}{self.health.current:3}/{self.health.max:>3}\n"
                          f"{'Mana Points:':13}{' ':1}{self.mana.current:3}/{self.mana.max:>3}\n"
                          f"{'Strength:':13}{' ':1}{self.stats.strength:>7}\n"
                          f"{'Intelligence:':13}{' ':1}{self.stats.intel:>7}\n"
                          f"{'Wisdom:':13}{' ':1}{self.stats.wisdom:>7}\n"
                          f"{'Constitution:':13}{' ':1}{self.stats.con:>7}\n"
                          f"{'Charisma:':13}{' ':1}{self.stats.charisma:>7}\n"
                          f"{'Dexterity:':13}{' ':1}{self.stats.dex:>7}\n")
        try:
            virtue = getattr(getattr(self, "race", None), "virtue", None)
            sin = getattr(getattr(self, "race", None), "sin", None)
            if virtue and getattr(virtue, "name", ""):
                status_message += f"{'Virtue:':13} {virtue.name}\n"
            if sin and getattr(sin, "name", ""):
                status_message += f"{'Sin:':13} {sin.name}\n"
        except Exception:
            pass
        return status_message

    def combat_str(self):
        combat_message = ""
        main_dmg = self.check_mod('weapon')
        main_crit = int((self.equipment['Weapon'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
        if self.equipment['OffHand'].typ == 'Weapon':
            off_dmg = self.check_mod('offhand')
            off_crit = int((self.equipment['OffHand'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
            combat_message += f"{'Attack:':16}{' ':2}{str(main_dmg):>3}/{str(off_dmg):>3}\n"
            combat_message += f"{'Critical Chance:':16}{' ':2}{str(main_crit):2}%/{str(off_crit):>2}%\n"
        else:
            combat_message += f"{'Attack:':16}{' ':2}{str(main_dmg):>7}\n"
            combat_message += f"{'Critical Chance:':16}{' ':2}{str(main_crit):>6}%\n"
        combat_message += f"{'Defense:':16}{' ':2}{self.check_mod('armor'):>7}\n"
        combat_message += f"{'Block Chance:':16}{' ':2}{self.check_mod('shield'):>6}%\n"
        combat_message += f"{'Spell Defense:':16}{' ':2}{str(self.check_mod('magic def')):>7}\n"
        spell_mod = self.check_mod('magic')
        heal_mod = self.check_mod('heal')
        combat_message += f"{'Spell Modifier:':16}{' ':2}{str(spell_mod):>7}\n"
        combat_message += f"{'Heal Modifier:':16}{' ':2}{str(heal_mod):>7}\n"
        return combat_message
    
    def equipment_str(self):
        """
        Returns a string containing the current equipment of the player
        """

        buff_str = self.buff_str()
        # Format OffHand with buff info
        offhand_item = self.equipment['OffHand']
        if offhand_item.subtyp == 'Shield':
            offhand_str = f"{offhand_item.name} ({int(offhand_item.mod * 100)}% Block)"
        elif offhand_item.subtyp in ['Tome', 'Rod']:
            offhand_str = f"{offhand_item.name} (+{int(offhand_item.mod)} Magic)"
        elif offhand_item.subtyp == 'Musical Instrument':
            offhand_str = f"{offhand_item.name} (+{int(offhand_item.mod)} Heal)"
        elif offhand_item.typ == 'Weapon':
            offhand_str = offhand_item.name
        else:
            offhand_str = offhand_item.name
        
        return (f"{'Weapon'}:    {self.equipment['Weapon'].name:<30}\n"
                f"{'Armor'}:     {self.equipment['Armor'].name:<30}\n"
                f"{'Ring'}:      {self.equipment['Ring'].name:<30}\n"
                f"{'OffHand'}:   {offhand_str:<30}\n"
                f"{'Pendant'}:   {self.equipment['Pendant'].name:<30}\n"
                f"{'Buffs'}:     {buff_str:<30}\n")

    def resist_str(self):
        """
        Returns a string containing the current resistances of the player
        """

        rest_dict = {}
        for typ in self.resistance:
            rest_dict[typ] = self.check_mod("resist", typ=typ)
        return (f"{'Fire:'}     {rest_dict['Fire']:>5}       "
                f"{'Electric:'} {rest_dict['Electric']:>5}       "
                f"{'Earth:'}    {rest_dict['Earth']:>5}       "
                f"{'Shadow:'}   {rest_dict['Shadow']:>5}       "
                f"{'Poison:'}   {rest_dict['Poison']:>5}       \n"
                f"{'Ice:'}      {rest_dict['Ice']:>5}       "
                f"{'Water:'}    {rest_dict['Water']:>5}       "
                f"{'Wind:'}     {rest_dict['Wind']:>5}       "
                f"{'Holy:'}     {rest_dict['Holy']:>5}       "
                f"{'Physical:'} {rest_dict['Physical']:>5}       ")

    def level_up(self, game=None, textbox=None, menu=None):
        """Level up the player character.
        
        Args:
            game: Game instance (for UI interactions, optional)
            textbox: Optional TextBox UI component
            menu: Optional SelectionPopupMenu UI component
        """
        dv = max(1, LEVELUP_LUCK_DIVISOR_BASE - self.check_mod('luck', luck_factor=LEVELUP_LUCK_FACTOR_HP_MP))
        health_gain = random.randint(self.stats.con // dv, self.stats.con)
        self.health.max += health_gain
        mana_gain = random.randint(self.stats.intel // dv, self.stats.intel)
        self.mana.max += mana_gain
        if self.in_town():
            self.health.current = self.health.max
            self.mana.current = self.mana.max
        self.level.level += 1
        level_str = (f"You have gained a level.\n"
                     f"You are now level {self.level.level}.\n"
                     f"You have gained {health_gain} health points and {mana_gain} mana points.\n")
        attack_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_ATK_LUCK_FACTOR) +
                                    (self.stats.strength // LEVELUP_STAT_DIVISOR) + max(1, self.cls.att_plus // 2))
        self.combat.attack += attack_gain
        defense_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_DEF_LUCK_FACTOR) + 
                                    (self.stats.con // LEVELUP_STAT_DIVISOR) + max(1, self.cls.def_plus // 2))
        self.combat.defense += defense_gain
        magic_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_MAG_LUCK_FACTOR) +
                                    (self.stats.intel // LEVELUP_STAT_DIVISOR) + max(1, self.cls.int_plus // 2))
        self.combat.magic += magic_gain
        magic_def_gain = random.randint(0, self.check_mod("luck", luck_factor=LEVELUP_MDEF_LUCK_FACTOR) +
                                    (self.stats.wisdom // LEVELUP_STAT_DIVISOR) + max(1, self.cls.wis_plus // 2))
        self.combat.magic_def += magic_def_gain
        if attack_gain > 0:
            level_str += f"You have gained {attack_gain} attack.\n"
        if defense_gain > 0:
            level_str += f"You have gained {defense_gain} defense.\n"
        if magic_gain > 0:
            level_str += f"You have gained {magic_gain} magic.\n"
        if magic_def_gain > 0:
            level_str += f"You have gained {magic_def_gain} magic defense.\n"
        if str(self.level.level) in abilities.spell_dict[self.cls.name]:
            spell = abilities.spell_dict[self.cls.name][str(self.level.level)]
            spell_gain = spell()
            spell_name = spell_gain.name
            if spell_name in self.spellbook['Spells']:
                level_str += f"{spell_name} goes up a level.\n"
            else:
                try:
                    if spell.mro()[1]().name in self.spellbook['Spells']:
                        old_name = spell.mro()[1]().name
                        level_str += f"{old_name} is upgraded to {spell_name}."
                        del self.spellbook['Spells'][old_name]
                    else:
                        level_str += f"You have gained the ability to cast {spell_name}.\n"
                except TypeError:
                    level_str += f"You have gained the ability to cast {spell_name}.\n"
            self.spellbook['Spells'][spell_name] = spell_gain
        if str(self.level.level) in abilities.skill_dict[self.cls.name]:
            skill = abilities.skill_dict[self.cls.name][str(self.level.level)]
            skill_gain = skill()
            skill_name = skill_gain.name
            if skill_name in self.spellbook['Skills']:
                level_str += f"{skill_name} goes up a level.\n"
            else:
                try:
                    if skill.mro()[1]().name in self.spellbook['Skills']:
                        old_name = skill.mro()[1]().name
                        level_str += f"{old_name} is upgraded to {skill_name}."
                        del self.spellbook['Skills'][old_name]
                    else:
                        level_str += f"You have gained the ability to use {skill_name}.\n"
                except TypeError:
                    level_str += f"You have gained the ability to use {skill_name}.\n"
            self.spellbook['Skills'][skill_name] = skill_gain
            if skill_name == 'Health/Mana Drain':
                for skill in ["Health Drain", "Mana Drain"]:
                    if skill in self.spellbook["Skills"]:
                        del self.spellbook['Skills'][skill]
            elif skill_name == "True Piercing Strike":
                for skill in ["Piercing Strike", "True Strike"]:
                    if skill in self.spellbook["Skills"]:
                        del self.spellbook['Skills'][skill]
            elif skill_name == 'Familiar':
                level_str += self.familiar.level_up()
            elif skill_name in ["Transform", "Purity of Body"]:
                level_str += skill_gain.use(self)
            elif skill_name == 'Totem':
                # Initialize aspect unlocking for new Totem
                newly_unlocked = skill_gain.check_and_unlock_aspects(self.level.level)
                if newly_unlocked:
                    aspects_str = ", ".join(newly_unlocked)
                    level_str += f"Totem aspects unlocked: {aspects_str}.\n"
        # Unlock Jump modifications (Lancer/Dragoon)
        jump_skill = None
        skills = self.spellbook.get("Skills", {})
        if "Jump" in skills:
            jump_skill = skills["Jump"]
        else:
            for sk in skills.values():
                if getattr(sk, "name", "") == "Jump":
                    jump_skill = sk
                    break
        if jump_skill is not None:
            newly_unlocked = []
            if hasattr(jump_skill, "check_and_unlock_level_modifications"):
                newly_unlocked = jump_skill.check_and_unlock_level_modifications(
                    self.level.level, self.cls.name
                )
            elif hasattr(jump_skill, "check_and_unlock_level_modification"):
                newly_unlocked = jump_skill.check_and_unlock_level_modification(
                    self.level.level, self.cls.name
                )
            if newly_unlocked:
                mods_str = ", ".join(newly_unlocked)
                level_str += f"New Jump modifications unlocked: {mods_str}.\n"
        
        # Unlock Totem aspects (Shaman)
        totem_skill = None
        skills = self.spellbook.get("Skills", {})
        if "Totem" in skills:
            totem_skill = skills["Totem"]
        else:
            for sk in skills.values():
                if getattr(sk, "name", "") == "Totem":
                    totem_skill = sk
                    break
        if totem_skill is not None:
            newly_unlocked = []
            if hasattr(totem_skill, "check_and_unlock_aspects"):
                newly_unlocked = totem_skill.check_and_unlock_aspects(self.level.level)
            if newly_unlocked:
                aspects_str = ", ".join(newly_unlocked)
                level_str += f"New Totem aspects unlocked: {aspects_str}.\n"
        if not self.max_level():
            self.level.exp_to_gain += (self.exp_scale ** self.level.pro_level) * self.level.level
        else:
            self.level.exp_to_gain = "MAX"
        
        # Only show UI if components are provided
        if textbox and game:
            textbox.print_text_in_rectangle(level_str)
            game.stdscr.getch()
            textbox.clear_rectangle()
        
        if self.level.level % 4 == 0:
            stat_options = [f'Strength - {self.stats.strength}',
                            f'Intelligence - {self.stats.intel}',
                            f'Wisdom - {self.stats.wisdom}',
                            f'Constitution - {self.stats.con}',
                            f'Charisma - {self.stats.charisma}',
                            f'Dexterity - {self.stats.dex}']
            # Only show stat selection if menu is provided
            if menu and game:
                stat_idx = menu.navigate_popup()
                if 'Strength' in stat_options[stat_idx]:
                    self.stats.strength += 1
                    statup_message = f"You are now at {self.stats.strength} strength."
                if 'Intelligence' in stat_options[stat_idx]:
                    self.stats.intel += 1
                    statup_message = f"You are now at {self.stats.intel} intelligence."
                if 'Wisdom' in stat_options[stat_idx]:
                    self.stats.wisdom += 1
                    statup_message = f"You are now at {self.stats.wisdom} wisdom."
                if 'Constitution' in stat_options[stat_idx]:
                    self.stats.con += 1
                    statup_message = f"You are now at {self.stats.con} constitution."
                if 'Charisma' in stat_options[stat_idx]:
                    self.stats.charisma += 1
                    statup_message = f"You are now at {self.stats.charisma} charisma."
                if 'Dexterity' in stat_options[stat_idx]:
                    self.stats.dex += 1
                    statup_message = f"You are now at {self.stats.dex} dexterity."
                textbox.print_text_in_rectangle(statup_message)
                game.stdscr.getch()
                textbox.clear_rectangle()

    def open_up(self, game=None, textbox=None, battle_manager=None):
        """
        Handles opening chests and doors. UI and combat logic must be provided by the frontend.
        Args:
            game: Game instance (optional, for UI context)
            textbox: Optional TextBox UI component
            battle_manager: Optional callable/class for handling battles
        """
        tile = self.world_dict[(self.location_x, self.location_y, self.location_z)]
        if 'Chest' in str(tile):
            locked = int('Locked' in str(tile))
            plus = int('ChestRoom2' in str(tile))
            gold = random.randint(5, 50) * (self.location_z + locked + plus) * self.stats.charisma
            # FunhouseMimicChest always spawns a Mimic (level 4 difficulty); other chests have a random chance
            is_funhouse_mimic = 'FunhouseMimicChest' in str(tile)
            if is_funhouse_mimic or (not random.randint(0, 9 + self.check_mod('luck', luck_factor=3)) and self.level.level >= 10):
                # For funhouse mimic chest, spawn level 4 mimic; for other chests use normal scaling
                mimic_level = 4 if is_funhouse_mimic else (self.location_z + locked + plus)
                enemy = enemies.Mimic(mimic_level, player_level=self.player_level())
                enemy.anti_magic_active = self.anti_magic_active
                tile.enemy = enemy
                if textbox:
                    textbox.print_text_in_rectangle("There is a Mimic in the chest!")
                self.state = 'fight'
                if battle_manager:
                    battle_manager(game, enemy)
            if self.is_alive():
                tile.open = True
                loot = tile.loot()
                if textbox:
                    textbox.print_text_in_rectangle(
                        f"{self.name} opens the chest, containing {gold} gold and a {loot.name}.")
                self.modify_inventory(loot, 1)
                self.gold += gold
                
                # Funhouse Mimic Chest also drops a Jester Token
                if is_funhouse_mimic:
                    from src.core.items import JesterToken
                    token = JesterToken()
                    self.modify_inventory(token, 1)
                    if textbox:
                        textbox.print_text_in_rectangle(
                            f"A shimmering {token.name} manifests as the Mimic dissolves!")
        elif 'Door' in str(tile):
            tile.open = True
            if hasattr(tile, "locked"):
                tile.locked = False
            if hasattr(tile, "enter"):
                tile.enter = True
            if textbox:
                textbox.print_text_in_rectangle(f"{self.name} opens the door.")
        else:
            raise AssertionError("Something is not working. Check code.")

    def loot(self, enemy, tile):
        loot_message = ""
        items = sum(enemy.inventory.values(), [])
        rare = [False] * len(items)
        drop = [False] * len(items)
        if enemy.gold > 0:
            gold = int(enemy.gold)
            # Gnome Charity (virtue): charisma has a stronger effect on gold outcomes.
            try:
                if getattr(getattr(self, "race", None), "name", None) == "Gnome":
                    from .constants import GNOME_GOLD_CHARISMA_MULTIPLIER
                    eff_cha = int(getattr(self.stats, "charisma", 0) * GNOME_GOLD_CHARISMA_MULTIPLIER)
                    bonus_pct = min(0.25, max(0.0, eff_cha * 0.01))  # up to +25%
                    gold = max(0, int(gold * (1.0 + bonus_pct)))
            except Exception:
                pass
            loot_message += f"{enemy.name} dropped {gold} gold.\n"
            self.gold += gold
        for i, item_typ in enumerate(items):
            try:
                item = item_typ()
            except TypeError:
                item = item_typ
            
            # Check if item has class restrictions
            if hasattr(item, 'restricted_classes'):
                if self.cls.name not in item.restricted_classes:
                    drop[i] = False
                    continue
            
            drop[i] = item.subtyp == "Special"
            rare[i] = item.subtyp == "Special"
            if item.subtyp == "Quest":
                quest_found = False
                # Check both Main and Side quests
                for quest_type in ['Main', 'Side']:
                    for quest_name, info in self.quest_dict.get(quest_type, {}).items():
                        try:
                            quest_what = info['What']
                            # Handle different types of 'What': class, instance, or string
                            quest_item_name = None
                            quest_item_class_name = None
                            if isinstance(quest_what, str):
                                # JSON quests may store class name (e.g. ElementalMote) or display name.
                                quest_item_name = quest_what
                                quest_item_class_name = quest_what
                            elif callable(quest_what):
                                # It's a class, instantiate for display name and use class name too.
                                quest_item_name = quest_what().name
                                quest_item_class_name = quest_what.__name__
                            else:
                                # It's already an instance.
                                quest_item_name = quest_what.name
                                quest_item_class_name = quest_what.__class__.__name__
                            
                            is_completed = info.get('Completed', False)
                            item_class_name = item.__class__.__name__
                            matches_item = item.name == quest_item_name or item_class_name == quest_item_class_name
                            if matches_item and not is_completed:
                                rarity = item.rarity
                                if item.name == "Bird Fat" and "Summoner" not in self.cls.name:
                                    rarity = 0.75
                                rarity_roll = random.random()
                                rare[i] = True
                                drop[i] = True if rarity > rarity_roll else False
                                quest_found = True
                                break
                        except (AttributeError, TypeError, KeyError):
                            pass
                    if quest_found:
                        break
                # No matching active quest -> do not drop quest item.
                if not quest_found:
                    drop[i] = False
                    rare[i] = False
            elif 'Boss' in str(tile):
                if item.subtyp == "Special":
                    drop[i] = True if item.rarity > random.random() else False
                    rare[i] = True
                else:
                    drop[i] = True  # all non-quest, non-special items will drop from bosses
            elif item.subtyp == "Ability":
                drop[i] = True if item.rarity > random.random() else False
                rare[i] = True
            else:
                chance = self.check_mod('luck', enemy=enemy, luck_factor=16) + self.level.pro_level
                if item.rarity > (random.random() / chance):
                        try:
                            summon, name = item.subtyp.split(" - ")
                            summon_drop = item.name in self.special_inventory
                        except ValueError:
                            summon, name = None, None
                            summon_drop = False
                        if summon and "Summoner" not in self.cls.name:
                            continue
                        drop[i] = True if not summon_drop else False
                        rare[i] = True if summon else False
            if drop[i]:
                loot_message += f"{enemy.name} dropped a {item.name}.\n"
                self.modify_inventory(item, rare=rare[i])
                loot_message += self.quests(item=item)
                # Unlock Jump modification for special items
                if item.name and hasattr(self.spellbook.get("Skills", {}), "values"):
                    jump_skill = None
                    skills = self.spellbook.get("Skills", {})
                    if "Jump" in skills:
                        jump_skill = skills["Jump"]
                    else:
                        for sk in skills.values():
                            if getattr(sk, "name", "") == "Jump":
                                jump_skill = sk
                                break
                    if jump_skill is not None and hasattr(jump_skill, "unlock_item_modification"):
                        unlocked = jump_skill.unlock_item_modification(item.name)
                        if unlocked:
                            loot_message += f"New Jump modification unlocked: {unlocked}.\n"
        # Unlock Jump modification for boss defeats
        if 'Boss' in str(tile):
            skills = self.spellbook.get("Skills", {})
            jump_skill = skills.get("Jump")
            if jump_skill is None:
                for sk in skills.values():
                    if getattr(sk, "name", "") == "Jump":
                        jump_skill = sk
                        break
            if jump_skill is not None and hasattr(jump_skill, "unlock_boss_modification"):
                unlocked = jump_skill.unlock_boss_modification(enemy.name)
                if unlocked:
                    loot_message += f"New Jump modification unlocked: {unlocked}.\n"
        return loot_message

    def inventory_screen(self, game, inv_popup=None, confirm_popup=None, useitembox=None):
        """Inventory screen logic, now UI-agnostic. UI components must be provided by the frontend."""
        if inv_popup is None:
            raise ValueError("UI component 'inv_popup' must be provided by the frontend.")
        while True:
            item = inv_popup.navigate_popup()
            if item == "Go Back":
                return
            if self.usable_item(item):
                if confirm_popup is None:
                    raise ValueError("UI component 'confirm_popup' must be provided by the frontend.")
                popup = confirm_popup(game, f"Do you want to use the {item.name}", box_height=7)
                if popup.navigate_popup():
                    use_str = item.use(self)
                    if use_str:
                        if useitembox is None:
                            raise ValueError("UI component 'useitembox' must be provided by the frontend.")
                        useitembox.print_text_in_rectangle(use_str)
                        useitembox.clear_rectangle()
                    if "Sanctuary" in item.name:
                        return

    def key_item_screen(self, game, inv_popup=None):
        """Key item screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        if inv_popup is None:
            raise ValueError("UI component 'inv_popup' must be provided by the frontend.")
        while True:
            item = inv_popup.navigate_popup()
            if item == "Go Back":
                return

    def equipment_screen(self, game, popup):
        """Equipment screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        popup.navigate_popup()

    def abilities_screen(self, game, popup):
        """Abilities screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        popup.navigate_popup()

    def jump_mods_menu(self, game, jump_popup=None):
        """Jump modifications menu logic, now UI-agnostic. UI component must be provided by the frontend."""
        if jump_popup is None:
            raise ValueError("UI component 'jump_popup' must be provided by the frontend.")
        jump_popup.navigate_popup()

    def totem_aspects_menu(self, game, totem_popup=None):
        """Totem aspects menu logic, now UI-agnostic. UI component must be provided by the frontend."""
        if totem_popup is None:
            raise ValueError("UI component 'totem_popup' must be provided by the frontend.")
        totem_popup.navigate_popup()

    def save(self, game=None, tmp=False, filepath=None, confirm_popup=None, save_popup=None):
        """
        Save the player state using the new data-driven save system.

        Args:
            game: Game instance (for UI prompts)
            tmp: If True, save to tmp_files
            filepath: Direct filepath (bypasses all prompts)
            confirm_popup: Optional ConfirmPopupMenu component for overwrite confirmation
            save_popup: Optional function to show save file popup (e.g., menus.save_file_popup)
        """
        if filepath:
            # Direct save to specified path
            SaveManager.save_player(self, os.path.basename(filepath), is_tmp=False)
            return
        
        if tmp:
            # Save to tmp_files with player name
            filename = f"{str(self.name).lower()}.save"
            SaveManager.save_player(self, filename, is_tmp=True)
        else:
            # Interactive save with UI
            filename = f"{str(self.name).lower()}.save"
            
            if not os.path.isdir("save_files"):
                os.mkdir("save_files")
            
            filepath = f"save_files/{filename}"
            
            if os.path.exists(filepath):
                confirm_str = "A save file under this name already exists. Are you sure you want to overwrite it?"
                # Only show confirmation if popup component is provided
                if confirm_popup and game:
                    if not confirm_popup.navigate_popup():
                        return
            
            if game and save_popup:
                save_popup(game)
            
            SaveManager.save_player(self, filename, is_tmp=False)

    def equip(self, equip_slot: str, item, check: bool = False) -> bool:
        """
        Handles equiping and character modification effects of equipment

        Args:
            equip_slot: Equipment slot where item is to be equipped. Must be one of the following: "Weapon",
                "OffHand", "Armor", "Ring", "Pendant"
            item: Equipment object to be equipped
            check: A flag signifying whether this is an equipment check or an actual equipment change.
                Default is False.

        Returns:
            True if equipment was successful, False if item is not allowed for this class.

        Example:
            >>> equip("Weapon", Dirk)
            >>> equip("Armor", LeatherArmor, check=True)

        """
        equip_slots = {"Weapon", "OffHand", "Armor", "Ring", "Pendant"}
        if equip_slot not in equip_slots:
            raise ValueError(f"'equip_slot' must be one of {equip_slots}. Got {equip_slot} instead.")

        # Check if the class allows this item type (allow unequip items)
        if item.subtyp != "None" and not self.cls.equip_check(item, equip_slot):
            return False

        if self.equipment[equip_slot].subtyp != 'None' and not check:
            self.modify_inventory(self.equipment[equip_slot])
        if self.equipment[equip_slot].name == "Pendant of Vision" and (self.cls.name not in ["Inquisitor", "Seeker"]):
            self.sight = False
        if self.equipment[equip_slot].name in ["Invisibility Amulet", "Tarnkappe"]:
            self.invisible = False
        if self.equipment[equip_slot].name == 'Levitation Necklace':
            self.flying = False
        
        # Handle two-handed weapon conflicts with offhand items
        if equip_slot == "Weapon":
            if item.handed == 2:
                # Lancer/Dragoon can use 2H polearms with shields
                can_keep_offhand = (self.cls.name in ["Lancer", "Dragoon"] and 
                                   item.subtyp == 'Polearm' and 
                                   self.equipment["OffHand"].subtyp == 'Shield')
                
                if not can_keep_offhand:
                    if self.equipment["OffHand"].subtyp != 'None' and not check:
                        self.modify_inventory(self.equipment["OffHand"])
                    if not check:
                        self.equipment["OffHand"] = remove_equipment("OffHand")
        
        if equip_slot == "OffHand":
            if self.equipment["Weapon"].handed == 2:
                # Lancer/Dragoon can use 2H polearms with shields
                can_keep_weapon = (self.cls.name in ["Lancer", "Dragoon"] and 
                                  self.equipment["Weapon"].subtyp == 'Polearm' and 
                                  item.subtyp == 'Shield')
                
                if not can_keep_weapon:
                    if self.equipment["Weapon"].subtyp != 'None' and not check:
                        self.modify_inventory(self.equipment["Weapon"])
                    if not check:
                        self.equipment["Weapon"] = remove_equipment("Weapon")
        self.equipment[equip_slot] = item
        if item.name == "Pendant of Vision":
            self.sight = True
        if item.name in ["Invisibility Amulet", "Tarnkappe"]:
            self.invisible = True
        if item.name == 'Levitation Necklace':
            self.flying = True
        if not check and item.subtyp != "None":
            self.modify_inventory(item, subtract=True)
        
        # If Ring slot changed, check if we need to enforce Jump modification limits
        if equip_slot == "Ring" and not check:
            # Check if character has Jump skill
            jump_skill = None
            if "Skills" in self.spellbook and "Jump" in self.spellbook["Skills"]:
                jump_skill = self.spellbook["Skills"]["Jump"]
            else:
                for skill in self.spellbook.get("Skills", {}).values():
                    if getattr(skill, "name", "") == "Jump":
                        jump_skill = skill
                        break
            
            if jump_skill and hasattr(jump_skill, "enforce_modification_limit"):
                deactivated = jump_skill.enforce_modification_limit(self)
                # Could emit a message here if needed
                # if deactivated:
                #     print(f"Jump modifications deactivated due to equipment change: {', '.join(deactivated)}")
        
        return True

    def equip_diff(self, item, equip_slot, buy=False):
        """
        function to analyze impact of item on player
        Temporarily equips the item, calculates stat differences, then safely restores original equipment
        """
        if equip_slot == "Accessory":
            equip_slot = item.subtyp

        # Save the current equipment reference BEFORE any modifications
        original_item = self.equipment[equip_slot]
        original_offhand = self.equipment["OffHand"] if equip_slot == "Weapon" else None

        try:
            # Get current stats with original equipment
            main_dmg = self.check_mod('weapon')
            main_crit = int((self.equipment['Weapon'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
            attack = f"{str(main_dmg)}"
            crit = f"{str(main_crit)}%"
            if self.equipment['OffHand'].typ == 'Weapon':
                off_dmg = self.check_mod('offhand')
                off_crit = int((self.equipment['OffHand'].crit  + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
                attack = f"{str(main_dmg)}/{str(off_dmg)}"
                crit = f"{str(main_crit)}%/{str(off_crit)}%"
            armor = self.check_mod('armor')
            block = self.check_mod('shield')
            spell_def = self.check_mod('magic def')
            spell_mod = self.check_mod('magic')
            heal_mod = self.check_mod('heal')
            buffs = self.buff_str()
            diff_dict = {
                "Attack": attack,
                "Critical Chance": crit,
                "Armor": str(armor),
                "Block Chance": f"{block}%",
                "Spell Defense": str(spell_def),
                "Spell Modifier": str(spell_mod),
                "Heal Modifier": str(heal_mod),
                "Buffs": buffs
            }

            # return empty if item is not equipable by player
            if not self.cls.equip_check(item, equip_slot) and item.subtyp not in ["Ring", "Pendant", 'None']:
                return ""

            # Temporarily equip new item - directly modify equipment dict
            self.equipment[equip_slot] = item
            if equip_slot == "Weapon" and item.subtyp in self.cls.restrictions["OffHand"] and buy:
                self.equipment["OffHand"] = item

            # Handle two-handed weapon conflicts with offhand items (preview only)
            if equip_slot == "Weapon" and item.handed == 2:
                can_keep_offhand = (self.cls.name in ["Lancer", "Dragoon"] and
                                    item.subtyp == 'Polearm' and
                                    self.equipment["OffHand"].subtyp == 'Shield')
                if not can_keep_offhand:
                    self.equipment["OffHand"] = remove_equipment("OffHand")

            # Get new stats with test equipment
            new_main_dmg = self.check_mod('weapon')
            if new_main_dmg != main_dmg:
                diff_dict["Attack"] = f"{main_dmg} -> {new_main_dmg}"
            new_main_crit = int((self.equipment['Weapon'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
            if new_main_crit != main_crit:
                diff_dict["Critical Chance"] = f"{main_crit}% -> {new_main_crit}%"
            if equip_slot == 'Weapon':
                if original_offhand and original_offhand.typ == 'Weapon':
                    if item.handed == 2 and self.cls.name not in ["Lancer", "Dragoon", "Berserker"]:
                        diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {new_main_dmg}"
                        diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {new_main_crit}%"
                    else:
                        new_off_dmg = self.check_mod('offhand')
                        new_off_crit = int((self.equipment['OffHand'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
                        if new_main_dmg != main_dmg or new_off_dmg != off_dmg:
                            diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {new_main_dmg}/{new_off_dmg}"
                        if new_main_crit != main_crit or new_off_crit != off_crit:
                            diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {new_main_crit}%/{new_off_crit}%"
                elif item.subtyp in self.cls.restrictions["OffHand"] and buy:
                    new_off_dmg = self.check_mod('offhand')
                    new_off_crit = int((self.equipment['OffHand'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
                    if original_offhand and original_offhand.typ == "Weapon":
                        diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {new_main_dmg}/{new_off_dmg}"
                        diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {new_main_crit}%/{new_off_crit}%"
                    else:
                        diff_dict["Attack"] = f"{main_dmg} -> {new_main_dmg}/{new_off_dmg}"
                        diff_dict["Critical Chance"] = f"{main_crit}% -> {new_main_crit}%/{new_off_crit}%"
            if equip_slot == 'OffHand':
                if item.typ == "Weapon":
                    new_off_dmg = self.check_mod('offhand')
                    new_off_crit = int((self.equipment['OffHand'].crit + (BASE_CRIT_PER_POINT * self.check_mod("speed"))) * 100)
                    diff_dict["Attack"] = f"{main_dmg} -> {main_dmg}/{new_off_dmg}"
                    diff_dict["Critical Chance"] = f"{main_crit}% -> {main_crit}%/{new_off_crit}%"
                    if original_offhand and original_offhand.typ == 'Weapon':
                        diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {main_dmg}/{new_off_dmg}"
                        diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {main_crit}%/{new_off_crit}%"
                if item.subtyp == "None" and original_offhand and original_offhand.typ == "Weapon":
                    diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {main_dmg}"
                    diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {main_crit}%"
            if self.check_mod('shield') != block:
                diff_dict["Block Chance"] = f"{block}% -> {self.check_mod('shield')}%"
            if self.check_mod('armor') != armor:
                diff_dict["Armor"] = f"{armor} -> {self.check_mod('armor')}"
            if self.check_mod('magic def') != spell_def:
                diff_dict["Spell Defense"] = f"{spell_def} -> {self.check_mod('magic def')}"
            if self.check_mod('magic') != spell_mod:
                diff_dict["Spell Modifier"] = f"{spell_mod} -> {self.check_mod('magic')}"
            if self.check_mod('heal') != heal_mod:
                diff_dict["Heal Modifier"] = f"{heal_mod} -> {self.check_mod('heal')}"
            diff_dict['Buffs'] = self.buff_str()

            return "\n".join([f"{x:16}{' ':2}{y:>6}" for x, y in diff_dict.items()])
        finally:
            # ALWAYS restore original equipment, even if an exception occurs
            self.equipment[equip_slot] = original_item
            if equip_slot == "Weapon" and original_offhand:
                self.equipment["OffHand"] = original_offhand

    def unequip(self, typ=None, promo=False):
        if typ:
            return remove_equipment(typ)  # imported from items
        if promo:
            for item in ['Weapon', 'Armor', 'OffHand']:
                if self.equipment[item].subtyp != 'None':
                    self.modify_inventory(self.equipment[item], 1)
        else:
            raise NotImplementedError

    def move(self, dx, dy):
        """Moves the character by dx, dy if the target tile allows entry."""
        self.previous_location = (self.location_x, self.location_y, self.location_z)
        new_x, new_y = self.location_x + dx, self.location_y + dy

        if getattr(self.world_dict.get((new_x, new_y, self.location_z), {}), "enter"):
            self.location_x, self.location_y = new_x, new_y
            if getattr(self, "dwarf_hangover_steps", 0) > 0:
                self.dwarf_hangover_steps = max(0, int(self.dwarf_hangover_steps) - 1)

    def move_forward(self, game):
        """Moves the character in the direction they are facing."""
        dx, dy = DIRECTIONS[self.facing]["move"]
        self.move(dx, dy)

    def turn(self, direction):
        """Turns the character left, right, or around (180 degrees)."""
        directions = ["north", "east", "south", "west"]
        current_idx = directions.index(self.facing)

        if direction == "right":
            new_idx = (current_idx + 1) % 4
        elif direction == "left":
            new_idx = (current_idx - 1) % 4
        elif direction == "around":
            new_idx = (current_idx + 2) % 4  # Move 2 steps forward in the list (180-degree turn)
        else:
            raise ValueError(f"Invalid turn direction: {direction}")

        self.facing = directions[new_idx]

    def turn_left(self):
        self.turn("left")

    def turn_right(self):
        self.turn("right")

    def turn_around(self):
        self.turn("around")

    def stairs(self, dz):
        """Moves the character up or down a floor."""
        self.previous_location = (self.location_x, self.location_y, self.location_z)
        self.location_z += dz
        if getattr(self, "dwarf_hangover_steps", 0) > 0:
            self.dwarf_hangover_steps = max(0, int(self.dwarf_hangover_steps) - 1)

    def stairs_up(self):
        self.stairs(dz=-1)

    def stairs_down(self):
        self.stairs(dz=1)

    def change_location(self, x, y, z):
        self.location_x = x
        self.location_y = y
        self.location_z = z

    def death(self, textbox=None):
        """
        Controls what happens when you die; no negative affect will occur for players under level 10.
        UI logic must be provided by the frontend.

        Args:
            textbox: Optional TextBox UI component
        """
        death_message = ""
        stat_list = ['strength', 'intelligence', 'wisdom', 'constitution', 'charisma', 'dexterity']
        if self.level.level > 9 or self.level.pro_level > 1:
            cost = self.level.level * self.level.pro_level * 100 * self.location_z
            cost = random.randint(cost // 2, cost)
            cost = min(cost, self.gold)
            death_message += f"Resurrection costs you {cost} gold.\n"
            self.gold -= cost
            if not random.randint(0, self.stats.charisma):
                death_message += "Complications occurred during your resurrection.\n"
                stat_index = random.randint(0, 5)
                stat_name = stat_list[stat_index]
                if stat_name == 'strength':
                    self.stats.strength -= 1
                if stat_name == 'intelligence':
                    self.stats.intel -= 1
                if stat_name == 'wisdom':
                    self.stats.wisdom -= 1
                if stat_name == 'constitution':
                    self.stats.con -= 1
                if stat_name == 'charisma':
                    self.stats.charisma -= 1
                if stat_name == 'dexterity':
                    self.stats.dex -= 1
                death_message += f"You have lost 1 {stat_name}.\n"
        self.state = 'normal'
        self.effects(end=True)
        self.to_town()
        death_message += "You wake up in town.\n"
        if textbox:
            textbox.print_text_in_rectangle(death_message)

    def class_upgrades(self, game, enemy):
        upgrade_str = ""
        if self.cls.name == "Soulcatcher":
            state = getattr(self, 'absorb_essence_state', None)
            if not isinstance(state, dict):
                self.absorb_essence_state = {}
                state = self.absorb_essence_state

            state.setdefault('floor', self.location_z)
            state.setdefault('procs_this_floor', 0)
            state.setdefault('procs_by_enemy', {})
            state.setdefault('stat_gains', {
                'strength': 0,
                'intel': 0,
                'wisdom': 0,
                'con': 0,
                'charisma': 0,
                'dex': 0,
            })
            state.setdefault('health_gains', 0)
            state.setdefault('mana_gains', 0)
            state.setdefault('level_gains', 0)
            state.setdefault('dragon_gold_claimed', False)

            if state['floor'] != self.location_z:
                state['floor'] = self.location_z
                state['procs_this_floor'] = 0
                state['procs_by_enemy'] = {}

            if state['procs_this_floor'] >= self.ABSORB_ESSENCE_MAX_PROCS_PER_FLOOR:
                return upgrade_str

            enemy_proc_count = state['procs_by_enemy'].get(enemy.name, 0)
            if enemy_proc_count >= self.ABSORB_ESSENCE_MAX_PROCS_PER_ENEMY_PER_FLOOR:
                return upgrade_str

            luck_bonus = min(4, self.check_mod('luck', enemy=enemy, luck_factor=20))
            chance = max(12, 19 - luck_bonus)
            if not random.randint(0, chance):
                applied = False

                if enemy.name in ['Behemoth', 'Golem', 'Iron Golem'] and \
                        state['stat_gains']['strength'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 strength.\n"
                    self.stats.strength += 1
                    state['stat_gains']['strength'] += 1
                    applied = True

                if enemy.name in ['Lich', 'Brain Gorger'] and \
                        state['stat_gains']['intel'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 intelligence.\n"
                    self.stats.intel += 1
                    state['stat_gains']['intel'] += 1
                    applied = True

                if enemy.name in ['Aboleth', 'Hydra'] and \
                        state['stat_gains']['wisdom'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 wisdom.\n"
                    self.stats.wisdom += 1
                    state['stat_gains']['wisdom'] += 1
                    applied = True

                if enemy.name in ['Warforged', 'Archvile'] and \
                        state['stat_gains']['con'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 constitution.\n"
                    self.stats.con += 1
                    state['stat_gains']['con'] += 1
                    applied = True

                if enemy.name in ['Beholder', 'Wyrm'] and \
                        state['stat_gains']['charisma'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 charisma.\n"
                    self.stats.charisma += 1
                    state['stat_gains']['charisma'] += 1
                    applied = True

                if enemy.name in ['Shadow Serpent', 'Wyvern'] and \
                        state['stat_gains']['dex'] < self.ABSORB_ESSENCE_MAX_STAT_GAINS:
                    upgrade_str += "Gain 1 dexterity.\n"
                    self.stats.dex += 1
                    state['stat_gains']['dex'] += 1
                    applied = True

                if enemy.name in ['Basilisk', 'Sandworm'] and \
                        state['health_gains'] < self.ABSORB_ESSENCE_MAX_HEALTH_GAINS:
                    hp_gain = min(5, self.ABSORB_ESSENCE_MAX_HEALTH_GAINS - state['health_gains'])
                    if hp_gain > 0:
                        upgrade_str += f"Gain {hp_gain} hit points.\n"
                        self.health.max += hp_gain
                        self.health.current += hp_gain
                        state['health_gains'] += hp_gain
                        applied = True

                if enemy.name == 'Mind Flayer' and state['mana_gains'] < self.ABSORB_ESSENCE_MAX_MANA_GAINS:
                    mana_gain = min(5, self.ABSORB_ESSENCE_MAX_MANA_GAINS - state['mana_gains'])
                    if mana_gain > 0:
                        upgrade_str += f"Gain {mana_gain} mana points.\n"
                        self.mana.max += mana_gain
                        self.mana.current += mana_gain
                        state['mana_gains'] += mana_gain
                        applied = True

                if enemy.name in ['Jester', 'Domingo', 'Cerberus'] and \
                        state['level_gains'] < self.ABSORB_ESSENCE_MAX_LEVEL_GAINS and \
                        not self.max_level():
                    upgrade_str += "Gain enough experience to level.\n"
                    self.level.exp += self.level.exp_to_gain
                    self.level.exp_to_gain = 0
                    self.level_up(game)
                    state['level_gains'] += 1
                    applied = True

                if enemy.name == 'Red Dragon' and not state['dragon_gold_claimed']:
                    upgrade_str += "You find a cache of gold, doubling your current stash.\n"
                    self.gold *= 2
                    state['dragon_gold_claimed'] = True
                    applied = True

                if applied:
                    upgrade_str = f"You absorb part of the {enemy.name}'s soul.\n" + upgrade_str
                    state['procs_this_floor'] += 1
                    state['procs_by_enemy'][enemy.name] = enemy_proc_count + 1
        if self.cls.name == "Lycan" and enemy.name == 'Red Dragon':
            upgrade_str += f"{self.name} has harnessed the power of the Red Dragon and can now transform into one!\n"
            self.spellbook['Skills']['Transform'] = abilities.Transform4()
            self.spellbook['Skills']['Transform'].use(self)
        return upgrade_str

    def familiar_turn(self, enemy):
        familiar_str = ""
        if self.familiar:
            special = None
            target = enemy
            if not random.randint(0, 3):
                if self.familiar.spec == "Defense":  # skills and spells
                    while True:
                        if not random.randint(0, 1):
                            special_list = list(self.familiar.spellbook['Spells'])
                            special_type = "Spells"
                        else:
                            special_list = list(self.familiar.spellbook['Skills'])
                            special_type = "Skills"
                        if len(special_list) == 1:
                            special = self.familiar.spellbook[special_type][special_list[0]]
                        else:
                            choice = random.choice(special_list)
                            special = self.familiar.spellbook[special_type][choice]
                        if special.name not in ['Resurrection', 'Cover']:
                            break
                if self.familiar.spec == "Support":  # just spells
                    target = self
                    if not random.randint(0, 4) and self.mana.current < self.mana.max:
                        mana_regen = int(self.mana.max * 0.05)
                        mana_regen = min(mana_regen, self.mana.max - self.mana.current)
                        self.mana.current += mana_regen
                        familiar_str += f"{self.familiar.name} restores {self.name}'s mana by {mana_regen}.\n"
                    else:
                        if self.health.current < self.health.max and random.randint(0, 1):
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']["Regen"]
                        elif not self.stat_effects["Attack"].active:
                            special = self.familiar.spellbook['Spells']['Bless']
                        elif self.familiar.level.level > 1 and not self.magic_effects["Reflect"].active:
                            special = self.familiar.spellbook['Spells']["Reflect"]
                        elif self.familiar.level.level == 3 and random.randint(0, 1):
                            special = self.familiar.spellbook['Spells']['Cleanse']
                        else:
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']["Regen"]
                if self.familiar.spec == "Arcane":  # just spells
                    spell_list = list(self.familiar.spellbook['Spells'])
                    choice = random.choice(spell_list)
                    if choice == "Boost" and not random.randint(0, 1) and not self.stat_effects["Magic"].active:
                        special = self.familiar.spellbook['Spells']['Boost']
                        target = self
                    else:
                        special = self.familiar.spellbook['Spells'][choice]
                if self.familiar.spec == "Luck":
                    if not random.randint(0, 1):
                        spell_list = list(self.familiar.spellbook['Spells'])
                        choice = random.choice(spell_list)
                        special = self.familiar.spellbook['Spells'][choice]
                    else:
                        while True:
                            skill_list = list(self.familiar.spellbook['Skills'])
                            choice = random.choice(skill_list)
                            if choice == 'Lockpick':
                                pass
                            else:
                                special = self.familiar.spellbook['Skills'][choice]
                                break
                if special is not None:
                    if special.typ == 'Skill':
                        familiar_str += f"{self.familiar.name} uses {special.name}.\n"
                        familiar_str += special.use(self, target=target, fam=True)
                    elif special.typ == 'Spell':
                        familiar_str += f"{self.familiar.name} casts {special.name}.\n"
                        familiar_str += special.cast(self, target=target, fam=True)
        return familiar_str

    def transform(self, back=False):
        transform_str = ""
        if back:
            try:
                player_char_dict = load_char(char=self)
                if player_char_dict is None:
                    # No tmp file exists (player never transformed or already reverted)
                    return ""
                health_diff = self.health.max - self.health.current
                mana_diff = self.mana.max - self.mana.current
                self.cls = player_char_dict.cls
                if self.is_alive():
                    self.health.current = max(1, player_char_dict.health.max - health_diff)
                self.health.max = player_char_dict.health.max
                self.mana.current = max(0, player_char_dict.mana.max - mana_diff)
                self.mana.max = player_char_dict.mana.max
                self.stats = player_char_dict.stats
                self.equipment = player_char_dict.equipment
                self.spellbook = player_char_dict.spellbook
                self.resistance = player_char_dict.resistance
                self.transform_type = player_char_dict.transform_type
                transform_str = f"{self.name} transforms back into their normal self."
            except FileNotFoundError:
                pass
        else:
            self.save(tmp=True)
            transform_str = f"{self.name} transforms into a {self.transform_type.name}."
            self.cls = self.transform_type
            self.health.current += self.transform_type.health.max
            self.health.max += self.transform_type.health.max
            self.mana.current += self.transform_type.mana.max
            self.mana.max += self.transform_type.mana.max
            self.stats.strength += self.transform_type.stats.strength
            self.stats.intel += self.transform_type.stats.intel
            self.stats.wisdom += self.transform_type.stats.wisdom
            self.stats.con += self.transform_type.stats.con
            self.stats.charisma += self.transform_type.stats.charisma
            self.stats.dex += self.transform_type.stats.dex
            self.equipment['Weapon'] = self.transform_type.equipment['Weapon']
            self.equipment['Armor'] = self.transform_type.equipment['Armor']
            self.equipment['OffHand'] = self.transform_type.equipment['OffHand']
            self.spellbook = self.transform_type.spellbook
            self.resistance = self.transform_type.resistance
            if self.power_up:
                self.class_effects["Power Up"].active = True
                self.class_effects["Power Up"].duration = 1
        return transform_str

    def end_combat(self, game, enemy, tile, flee=False, summon=None, textbox=None):
        """
        Handles end of combat. UI logic must be provided by the frontend.
        Args:
            game: Game instance (optional, for UI context)
            enemy: Enemy instance
            tile: Tile instance
            flee: Whether the player fled
            summon: Summon instance (optional)
            textbox: Optional TextBox UI component
        """
        self.state = 'normal'
        # Only transform back if character is currently transformed
        if self.cls != self.transform_type:
            self.transform(back=True)
        self.effects(end=True)
        if all([self.is_alive(), not flee]):
            exp_gain = int(enemy.experience)
            try:
                exp_gain = max(0, int(exp_gain * float(self.exp_gain_multiplier())))
            except Exception:
                pass
            endcombat_str = (f"{self.name} killed {enemy.name}.\n"
                             f"{self.name} gained {exp_gain} experience.\n")
            if summon:
                summon.effects(end=True)
                endcombat_str += f"{summon.name} gained {exp_gain} experience.\n"
                summon.level.exp += exp_gain
                if summon.level.level < 10:
                    summon.level.exp_to_gain -= exp_gain
                    while summon.level.exp_to_gain <= 0:
                        endcombat_str += summon.level_up(self)
                        if summon.level.level == 10:
                            break
            if enemy.enemy_typ not in self.kill_dict:
                self.kill_dict[enemy.enemy_typ] = {}
            if enemy.name not in self.kill_dict[enemy.enemy_typ]:
                self.kill_dict[enemy.enemy_typ][enemy.name] = 0
            self.kill_dict[enemy.enemy_typ][enemy.name] += 1
            endcombat_str += self.loot(enemy, tile)
            endcombat_str += self.quests(enemy=enemy)
            if textbox:
                textbox.print_text_in_rectangle(endcombat_str)
            self.level.exp += exp_gain
            upgrade_message = self.class_upgrades(game, enemy)
            if upgrade_message and textbox:
                textbox.print_text_in_rectangle(upgrade_message)
            if not self.max_level():
                self.level.exp_to_gain -= exp_gain
                while self.level.exp_to_gain <= 0:
                    self.level_up(game)
                    if self.max_level():
                        break
        elif flee:
            pass
        else:
            if textbox:
                textbox.print_text_in_rectangle(f"{self.name} was slain by {enemy.name}.")
            enemy.effects(end=True)
            enemy.health.current = enemy.health.max
            enemy.mana.current = enemy.mana.max
            self.death()

    def quests(self, enemy=None, item=None):
        quest_message = ""
        if enemy is not None:
            if enemy.name in self.quest_dict['Bounty']:
                if not self.quest_dict['Bounty'][enemy.name][2]:
                    self.quest_dict['Bounty'][enemy.name][1] += 1
                    if self.quest_dict['Bounty'][enemy.name][1] >= self.quest_dict['Bounty'][enemy.name][0]['num']:
                        self.quest_dict['Bounty'][enemy.name][2] = True
                        quest_message += "You have completed a bounty.\n"
            elif enemy.name == "Waitress":
                self.quest_dict['Side']['Something to Cry About']["Completed"] = True
                quest_message += f"You have completed the quest Something to Cry About.\n"
            else:
                for quest in self.quest_dict['Main']:
                    if self.quest_dict['Main'][quest]['What'] == enemy.name and \
                        not self.quest_dict['Main'][quest]['Completed']:
                        self.quest_dict['Main'][quest]['Completed'] = True
                        quest_message += f"You have completed the quest {quest}.\n"

                for quest in self.quest_dict['Side']:
                    quest_info = self.quest_dict['Side'][quest]
                    if (
                        quest_info.get('Type') == 'Defeat'
                        and quest_info.get('What') == enemy.name
                        and not quest_info.get('Completed')
                    ):
                        quest_info['Completed'] = True
                        quest_message += f"You have completed the quest {quest}.\n"
        elif item is not None:
            for quest in self.quest_dict['Side']:
                try:
                    quest_what = self.quest_dict['Side'][quest]['What']
                    if isinstance(quest_what, str):
                        matches_item = quest_what in [item.name, item.__class__.__name__]
                    else:
                        matches_item = quest_what.name == item.name

                    if matches_item:
                        if item.name in self.special_inventory:
                            if len(self.special_inventory[item.name]) >= self.quest_dict['Side'][quest]['Total'] and \
                                    not self.quest_dict['Side'][quest]['Completed']:
                                self.quest_dict['Side'][quest]['Completed'] = True
                                quest_message += f"You have completed the quest {quest}.\n"
                        break
                except (AttributeError, TypeError):
                    pass
        else:
            if self.has_relics():
                if 'The Holy Relics' in self.quest_dict['Main']:
                    quest_message += "You have completed the quest The Holy Relics!\n"
                    self.quest_dict['Main']['The Holy Relics']['Completed'] = True
        return quest_message

    def quests_screen(self, game, popup):
        """Quests screen logic, now UI-agnostic. UI component must be provided by the frontend."""
        popup.navigate_popup()

    def check_mod(self, mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        berserk_per = int(self.status_effects["Berserk"].active) * 0.1  # berserk increases damage by 10%
        disarm_damage_multiplier = 0.5 if self.is_disarmed() else 1.0
        if self.cls.name == "Soulcatcher" and self.power_up:
            if enemy and getattr(enemy, "enemy_typ", None) in self.kill_dict:
                class_mod += (sum(self.kill_dict[enemy.enemy_typ].values()) // 20)
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.is_disarmed()))
            if 'Monk' in self.cls.name:
                class_mod += self.stats.wisdom
            # Footpad-line weapon damage is DEX-forward.
            if self.cls.name in ["Footpad", "Thief", "Rogue", "Assassin", "Ninja"]:
                class_mod += self.stats.dex
            if self.cls.name in ['Spellblade', 'Knight Enchanter']:
                class_mod += weapon_mod * int(2 * (self.mana.current / self.mana.max))
            if self.cls.name == "Berserker" and self.power_up:
                class_mod += int(min(self.health.max / self.health.current, 10) * (self.player_level() // 11))
            if self.cls.name in ['Dragoon', "Shadowcaster"] and self.power_up:
                class_mod += weapon_mod * self.class_effects["Power Up"].active * self.class_effects["Power Up"].duration
            if self.cls.name == "Ninja" and self.power_up:
                class_mod += self.class_effects["Power Up"].active * self.class_effects["Power Up"].extra
            if self.cls.name == "Templar" and self.power_up and self.class_effects["Power Up"].active:
                class_mod += (self.player_level() // 5)
            if self.cls.name == "Lycan" and self.power_up:
                class_mod += ((self.player_level() // 10) * self.class_effects["Power Up"].duration)
            if 'Physical Damage' in self.equipment['Ring'].mod:
                weapon_mod += int(self.equipment['Ring'].mod.split(' ')[0])
            weapon_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
            total_mod = (weapon_mod + class_mod + self.combat.attack) * disarm_damage_multiplier
            return max(0, int(total_mod * (1 + berserk_per)))
        if mod == 'shield':
            block_mod = 0
            if self.equipment['OffHand'] and self.equipment['OffHand'].subtyp == 'Shield':
                block_mod = round(self.equipment['OffHand'].mod * 100)
            if self.equipment['Ring'] and self.equipment['Ring'].mod == "Block":
                block_mod += 25
            return max(0, block_mod)
        if mod == 'offhand':
            if 'Monk' in self.cls.name:
                class_mod += self.stats.wisdom
            if self.cls.name in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level.level + ((self.level.pro_level - 1) * 20)) * (self.mana.current / self.mana.max)
            if self.cls.name in ['Thief', 'Rogue', 'Assassin', 'Ninja', 'Druid', 'Lycan']:
                class_mod += (self.stats.dex // 2)
            try:
                off_mod = self.equipment['OffHand'].damage
                if self.equipment['Ring'] is not None and 'Physical Damage' in self.equipment['Ring'].mod:
                    off_mod += int(self.equipment['Ring'].mod.split(' ')[0])
                off_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
                return max(0, int((off_mod + class_mod + self.combat.attack) * (0.75 + berserk_per)))
            except AttributeError:
                return 0
        if mod == 'armor':
            armor_mod = self.equipment['Armor'].armor
            if self.cls.name == 'Knight Enchanter':
                class_mod += int(armor_mod * max(0, min(5, self.mana.max / (self.mana.current + 1))))
            if self.cls.name in ['Warlock', 'Shadowcaster']:
                if self.familiar and self.familiar.spec == 'Homunculus' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
                    fam_mod = random.randint(0, 3) ** self.familiar.level.pro_level
                    class_mod += fam_mod
            if self.cls.name == "Berserker" and self.power_up and (self.health.current / self.health.max) < 0.3:
                class_mod += (self.player_level() // 11)
            if self.cls.name == 'Dragoon' and self.power_up:
                class_mod = armor_mod * self.class_effects["Power Up"].active * self.class_effects["Power Up"].duration
            if self.equipment['Ring'] is not None and 'Physical Defense' in self.equipment['Ring'].mod:
                armor_mod += int(self.equipment['Ring'].mod.split(' ')[0])
            armor_mod += self.stat_effects["Defense"].extra * self.stat_effects["Defense"].active
            return max(0, (armor_mod * int(not ignore)) + class_mod + self.combat.defense)
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * self.level.pro_level
            if self.equipment['OffHand'] is not None and self.equipment['OffHand'].subtyp == 'Tome':
                magic_mod += self.equipment['OffHand'].mod
            if self.equipment['Weapon'] is not None and self.equipment['Weapon'].subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon'].damage * 0.75)
            if self.equipment['Pendant'] is not None and 'Magic Damage' in self.equipment['Pendant'].mod:
                magic_mod += int(self.equipment['Pendant'].mod.split(' ')[0])
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            if self.cls.name == "Shadowcaster" and self.class_effects["Power Up"].active:
                class_mod += magic_mod
            return max(0, magic_mod + class_mod + self.combat.magic)
        if mod == 'magic def':
            # Wisdom is the primary magic-defense stat; charisma provides a secondary
            # willpower component so low-CHA physical builds have a tangible downside.
            m_def_mod = (self.stats.wisdom + (self.stats.charisma // 2)) * self.level.pro_level
            if self.equipment['Pendant'] is not None and "Magic Defense" in self.equipment['Pendant'].mod:
                m_def_mod += int(self.equipment['Pendant'].mod.split(' ')[0])
            m_def_mod += self.stat_effects["Magic Defense"].extra * self.stat_effects["Magic Defense"].active
            return max(0, m_def_mod + class_mod + self.combat.magic_def)
        if mod == 'heal':
            heal_mod = self.stats.wisdom * self.level.pro_level
            if self.equipment['OffHand'] is not None and self.equipment['OffHand'].subtyp == 'Tome':
                heal_mod += self.equipment['OffHand'].mod
            elif self.equipment['Weapon'] is not None and self.equipment['Weapon'].subtyp == 'Staff':
                heal_mod += self.equipment['Weapon'].damage
            heal_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, heal_mod + class_mod + self.combat.magic)
        if mod == 'resist':
            res_mod = 0
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                res_mod -= 1
            if typ in self.resistance:
                res_mod = self.resistance[typ]
            if self.flying:
                if typ == 'Earth':
                    res_mod = 1
                elif typ == 'Wind':
                    res_mod = -0.25
            if self.cls.name in ['Warlock', 'Shadowcaster']:
                if self.familiar and self.familiar.spec == 'Mephit' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
                    fam_mod = 0.25 * random.randint(1, max(1, self.stats.charisma // 10))
                    res_mod += fam_mod
            if self.equipment['Pendant'].mod.split("-")[-1] in [typ, "Elemental"] and \
                typ in ["Fire", "Ice", "Electric", "Water", "Earth", "Wind"]:
                if "Immune" in self.equipment['Pendant'].mod:
                    res_mod += 1
                elif "Resist" in self.equipment["Pendant"].mod:
                    res_mod += 0.5
            if self.equipment['OffHand'].name == "Svalinn" and typ == "Fire":
                res_mod += 0.25
            if self.cls.name == "Archbishop" and self.class_effects["Power Up"].active:
                res_mod += 0.25
            if self.cls.name == "Geomancer" and self.class_effects["Power Up"].active and \
                    typ in ["Fire", "Water", "Wind", "Earth"]:
                res_mod += 0.5
            return res_mod
        if mod == 'luck':
            if self.cls.name == "Rogue" and self.power_up:
                luck_factor = max(1, luck_factor // 2)
            lf = max(1, int(luck_factor))
            base = int(self.stats.charisma) + int(self.stats.wisdom)
            return max(0, (base * 2) // lf)
        if mod == "speed":
            speed_mod = self.stats.dex
            speed_mod += self.stat_effects["Speed"].extra * self.stat_effects["Speed"].active
            return speed_mod
        return 0

    def special_power(self, game):
            """
            Player attains power up following quest to find the Power Core, used to give Golems life
            Each class has a unique combat ability or passive that is activated upon receiving the Power Core

            Berserker - Blood Rage(passive): attack increases as health decreases; if below 30% health, bonus to defense
            Crusader - Divine Aegis: create shell that absorbs damage and increases healing; if the shield survives
                the full duration, it will explode and deal holy damage to the enemy
            Dragoon - Dragon's Fury(passive): attack and defense double for each successive hit; a miss resets this buff
            Stalwart Defender - 
            Wizard - Spell Mastery(passive): automatically triggers when no spells can be cast due to low mana; all spells
                become free for a short time and mana regens based on damage dealt
            Shadowcaster - Veil of Shadows(passive): become one with the darkness, making the player invisible to most enemies
                and making them harder to hit; increases damage of initial attack if first
            Knight Enchanter - Arcane Blast: blast the enemy with a powerful attack, draining all remaining mana points; mana
                will regen in full over the next 4 turns (25% per turn)
            Summoner - Eternal Conduit (passive): The Summoner's bond with their summons is so strong that they gain a portion of all healing and buffs their summons receive, and their summons gain a portion of all healing and buffs the Summoner receives.
            Rogue - Stroke of Luck(passive): the Rogue is incredibly lucky, gaining bonuses to all luck-based checks, including
                dodge and critical chance
            Seeker - Eyes of the Unseen(passive): gain increased awareness of battle situations, increasing critical chance as 
                well as chance to dodge/parry attacks
            Ninja - Blade of Fatalities: sacrifice percentage of health to imbue blade with the spirit of Muramasa, increasing
                damage dealt and absorbing it into the user
            Arcane Trickster - 
            Templar - Holy Retribution: a radiant shield envelopes the Templar, reflecting damage back at the attacker; while
                the shield is active, attack damage and chance to dodge/parry increase
            Archbishop - Great Gospel: regens health and mana over time, and restores status; increases magic resistance and 
                holy damage for duration
            Master Monk - Dim Mak: unleash a powerful attack that deals heavy damage and can either stun or in some cases 
                kill the target; if the target is killed, the user will absorb the enemy's essence and will be regenerated by
                its max health and mana
            Troubadour - Song of Inspiration (passive): The Troubadour's presence inspires allies and self, granting a small bonus to all stats and occasionally removing negative status effects at the start of combat.
            Lycan - Lunar Frenzy(passive): the longer the Lycan is transformed, the further into madness they fall, increasing
                damage and regenerating health on critical hits; if the Lycan stays transformed for longer than 5 turns, they 
                will be unable to transform back until after the battle
            Geomancer - Tetra-Disaster: unleash a powerful attack consisting of all 4 elements; this will also increase resistance
                of caster to the 4 elements by 50%
            Soulcatcher - Soul Harvest(passive): each enemy killed of a particular type will increase attack damage against
                that enemy type
            Beast Master - Pack Bond (passive): The Beast Master and their animal companion(s) share a deep bond, granting increased damage and defense when fighting alongside a companion. Occasionally, the companion will intercept attacks or provide a healing effect.
            """

            powerup_dict = {
                    "Berserker": abilities.BloodRage,
                    "Crusader": abilities.DivineAegis,
                    "Dragoon": abilities.DragonsFury,
                    "Wizard": abilities.SpellMastery,
                    "Shadowcaster": abilities.VeilShadows,
                    "Knight Enchanter": abilities.ArcaneBlast,
                    "Summoner": abilities.EternalConduit,
                    "Rogue": abilities.StrokeLuck,
                    "Seeker": abilities.EyesUnseen,
                    "Ninja": abilities.BladeFatalities,
                    "Templar": abilities.HolyRetribution,
                    "Archbishop": abilities.GreatGospel,
                    "Master Monk": abilities.DimMak,
                    "Troubadour": abilities.SongInspiration,
                    "Lycan": abilities.LunarFrenzy,
                    "Geomancer": abilities.TetraDisaster,
                    "Soulcatcher": abilities.SoulHarvest,
                    "Beast Master": abilities.PackBond
            }
            game.special_event("Power Up")
            skill = powerup_dict[self.cls.name]()
            self.spellbook['Skills'][skill.name] = skill
            self.power_up = True
            if self.cls.name == "Shadowcaster":
                    self.invisible = True
            return f"You gain the skill {skill.name}.\n"

    def summon_menu(self, game, summonpopup=None, summonbox=None):
        """Summon menu logic, now UI-agnostic. UI components must be provided by the frontend."""
        if summonpopup is None or summonbox is None:
            raise ValueError("UI components 'summonpopup' and 'summonbox' must be provided by the frontend.")
        summon_names = list(self.summons)
        summon_idx = summonpopup.navigate_popup()
        summon = self.summons[summon_names[summon_idx]]
        summonbox.print_text_in_rectangle(summon.inspect())
        summonbox.clear_rectangle()


actions_dict = {
    'MoveForward': {
        'method': Player.move_forward,
        'name': 'Move forward (w)',
        'hotkey': 'w'
    },
    'TurnAround': {
        'method': Player.turn_around,
        'name': 'Turn around (s)',
        'hotkey': 's'
    },
    'TurnRight': {
        'method': Player.turn_right,
        'name': 'Turn right (d)',
        'hotkey': 'd'
    },
    'TurnLeft': {
        'method': Player.turn_left,
        'name': 'Turn left (a)',
        'hotkey': 'a'
    },
    'StairsUp': {
        'method': Player.stairs_up,
        'name': 'Take stairs up',
        'hotkey': 'u'
    },
    'StairsDown': {
        'method': Player.stairs_down,
        'name': 'Take stairs down',
        'hotkey': 'j'
    },
    'ViewInventory': {
        'method': Player.inventory_screen,
        'name': 'Inventory',
        'hotkey': None
    },
    'ViewKeyItems': {
        'method': Player.key_item_screen,
        'name': 'Key Items',
        'hotkey': None
    },
    'Equipment': {
        'method': Player.equipment_screen,
        'name': 'Equipment',
        'hotkey': None
    },
    'Specials': {
        'method': Player.abilities_screen,
        'name': 'Specials',
        'hotkey': None
    },
    'ViewQuests': {
        'method': Player.quests_screen,
        'name': 'Quests',
        'hotkey': None
    },
    'Summons': {
        'method': Player.summon_menu,
        'name': 'Summons',
        'hotkey': None
    },
    'JumpMods': {
        'method': Player.jump_mods_menu,
        'name': 'Jump Mods',
        'hotkey': None
    },
    'TotemAspects': {
        'method': Player.totem_aspects_menu,
        'name': 'Totem Aspects',
        'hotkey': None
    },
    'Flee': {
        'method': Player.flee,
        'name': 'Flee',
        'hotkey': None
    },
    'Open': {
        'method': Player.open_up,
        'name': 'Open',
        'hotkey': 'o'
    },
    'Save': {
        'method': Player.save,
        'name': 'Save',
        'hotkey': None
    },
    'Quit': {
        'method': Player.game_quit,
        'name': 'Quit',
        'hotkey': None
    },
    'CharacterMenu': {
        'method': Player.character_menu,
        'name': 'Character Menu',
        'hotkey': 'c'
    }
}
