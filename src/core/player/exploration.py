"""Player exploration, navigation, travel, and death behavior."""

import glob
import os
import random

import numpy

from src.paths import MAP_FILES_DIR
from .. import thieves_guild
from ..constants import TOWN_LOCATION
from .config import (
    DIRECTIONS,
    LIMINAL_GAP_ENTRY_FACING,
    LIMINAL_GAP_ENTRY_POS,
    LIMINAL_GAP_LEVEL,
    REALM_OF_CAMBION_LEVEL,
)
from .maps import _load_tiled_map


class PlayerExplorationMixin:
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
        from .. import map_tiles

        world_dict = {}
        map_dir = MAP_FILES_DIR
        map_files = glob.glob(str(map_dir / "map_level_*"))
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
        funhouse_path = map_dir / "map_funhouse.json"
        if os.path.exists(funhouse_path) and 7 not in files_by_level:
            files_by_level[7] = {"path": funhouse_path, "ext": ".json"}

        cambion_path = map_dir / "map_realm_cambion.json"
        if os.path.exists(cambion_path) and REALM_OF_CAMBION_LEVEL not in files_by_level:
            files_by_level[REALM_OF_CAMBION_LEVEL] = {"path": cambion_path, "ext": ".json"}

        liminal_path = map_dir / "map_liminal_gap.txt"
        if os.path.exists(liminal_path) and LIMINAL_GAP_LEVEL not in files_by_level:
            files_by_level[LIMINAL_GAP_LEVEL] = {"path": liminal_path, "ext": ".txt"}

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

        wind_pos = getattr(map_tiles, "WIND_COMMUNION_POS", None)
        if wind_pos and wind_pos in world_dict:
            world_dict[wind_pos] = map_tiles.StrangeDraftTile(*wind_pos)

        if thieves_guild.TRIAL_ENTRY_POS in world_dict:
            world_dict[thieves_guild.TRIAL_ENTRY_POS] = map_tiles.CavePath0(*thieves_guild.TRIAL_ENTRY_POS)
        if thieves_guild.TRIAL_FAKE_WALL_POS in world_dict:
            guild_wall = map_tiles.ThievesGuildTrialFakeWall(*thieves_guild.TRIAL_FAKE_WALL_POS)
            guild_wall.sync_for_player(self)
            world_dict[thieves_guild.TRIAL_FAKE_WALL_POS] = guild_wall
        if thieves_guild.TRIAL_BOSS_POS in world_dict:
            world_dict[thieves_guild.TRIAL_BOSS_POS] = map_tiles.ThievesGuildTrialBossRoom(*thieves_guild.TRIAL_BOSS_POS)

        self.world_dict = world_dict
        map_tiles.sync_rookie_body_drop_marker(self)

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
        if "Steal As Well" in self.spellbook["Skills"] and not self.abilities_suppressed():
            action_list.insert(1, "Steal As Well")
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

    def in_liminal_gap(self):
        return self.location_z == LIMINAL_GAP_LEVEL

    def enter_liminal_gap(self, return_location=None):
        """Enter the Liminal Gap hub after Vesperion's false-final transition."""
        story_state = self.ensure_main_story_state()
        story_state["vesperion_false_final_triggered"] = True
        story_state["pending_liminal_gap_entry"] = False
        story_state["liminal_gap_entered"] = True

        if return_location and len(return_location) >= 4:
            self.liminal_gap_return = tuple(return_location[:4])

        self.location_x, self.location_y, self.location_z = LIMINAL_GAP_ENTRY_POS
        self.facing = LIMINAL_GAP_ENTRY_FACING
        self.state = "normal"
        self.effects(end=True)
        self.health.current = max(1, self.health.max // 2)
        self.mana.current = max(0, self.mana.max // 2)

    def enter_liminal_gap_stub(self, return_location):
        """Compatibility wrapper for the old non-map Liminal stub."""
        self.enter_liminal_gap(return_location)

    def return_from_liminal_gap(self):
        """Return from the Liminal Gap after the true-final path unlocks."""
        story_state = self.ensure_main_story_state()
        if not story_state.get("true_final_unlocked"):
            return False
        if hasattr(self, "liminal_gap_return") and self.liminal_gap_return:
            self.location_x, self.location_y, self.location_z, self.facing = self.liminal_gap_return
            self.liminal_gap_return = None
            story_state["returned_from_liminal_gap"] = True
            self.state = "normal"
            return True
        return False

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

    def move(self, dx, dy):
        """Moves the character by dx, dy if the target tile allows entry."""
        self.previous_location = (self.location_x, self.location_y, self.location_z)
        new_x, new_y = self.location_x + dx, self.location_y + dy
        try:
            from .. import map_tiles
            current_tile = self.world_dict.get((self.location_x, self.location_y, self.location_z))
            if current_tile and map_tiles.jester_force_field_blocks(current_tile, self, self.facing):
                return False
        except Exception:
            pass

        target_tile = self.world_dict.get((new_x, new_y, self.location_z), {})
        can_enter_wall = (
            getattr(self, "enter_wall", False)
            and "Wall" in target_tile.__class__.__name__
            and "Boundary" not in target_tile.__class__.__name__
        )
        if getattr(target_tile, "enter", False) or can_enter_wall:
            self.location_x, self.location_y = new_x, new_y
            self.record_step()
            if getattr(self, "dwarf_hangover_steps", 0) > 0:
                self.dwarf_hangover_steps = max(0, int(self.dwarf_hangover_steps) - 1)
            return True
        return False

    def move_forward(self, game):
        """Moves the character in the direction they are facing."""
        try:
            from .. import map_tiles
            current_tile = self.world_dict.get((self.location_x, self.location_y, self.location_z))
            if current_tile and map_tiles.jester_force_field_blocks(current_tile, self, self.facing):
                if game is not None and hasattr(game, "special_event"):
                    game.special_event(map_tiles.JESTER_FORCE_FIELD_EVENT)
                return False
        except Exception:
            pass
        dx, dy = DIRECTIONS[self.facing]["move"]
        return self.move(dx, dy)

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
        self.record_stairs_used()
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
        self.record_death()
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
        death_message += self._drop_rookie_body_on_death()
        self.to_town()
        death_message += "You wake up in town.\n"
        if textbox:
            textbox.print_text_in_rectangle(death_message)
        return death_message

    def _drop_rookie_body_on_death(self):
        """Leave the Rookie Mistake body where the player fell."""
        quest = self.quest_dict.get("Side", {}).get("Rookie Mistake")
        if not quest or "Dead Soldier" not in self.special_inventory:
            return ""

        self.special_inventory.pop("Dead Soldier", None)
        quest["Completed"] = False
        dropped_at = [self.location_x, self.location_y, self.location_z]
        quest["Body Dropped At"] = dropped_at
        try:
            tile = self.world_dict.get(tuple(dropped_at))
            if tile is not None:
                setattr(tile, "dropped_rookie_body", True)
                setattr(tile, "read", False)
        except Exception:
            pass
        return "The rookie's body slips from your grasp and remains where you fell.\n"
