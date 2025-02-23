"""
This module defines the player character and its attributes and actions.
"""

import glob
import os
import random
import re
import time

import dill
import numpy

import abilities
import utils
from character import Character
from items import remove_equipment


def load_char(char=None, player_dict=None):
    """
    Initializes the character based on the load file
    """
    if char:
        load_file = "tmp_files/" + str(char.name).lower() + ".tmp"
        with open(load_file, "rb") as l_file:
            player_dict = dill.load(l_file)
        os.system(f"rm {load_file}")
    player_char = Player(player_dict['location_x'], player_dict['location_y'], player_dict['location_z'],
                         player_dict['level'], player_dict['health'], player_dict['mana'], 
                         player_dict['stats'], player_dict["combat"],
                         player_dict['gold'], player_dict['resistance'])
    player_char.name = player_dict['name']
    player_char.race = player_dict['race']
    player_char.cls = player_dict['cls']
    player_char.equipment = player_dict['equipment']
    player_char.inventory = player_dict['inventory']
    player_char.special_inventory = player_dict['special_inventory']
    player_char.spellbook = player_dict['spellbook']
    player_char.familiar = player_dict['familiar']
    player_char.summons = player_dict["summons"]
    player_char.transform_type = player_dict['transform_type']
    player_char.teleport = player_dict['teleport']
    player_char.world_dict = player_dict['world_dict']
    player_char.quest_dict = player_dict['quest_dict']
    player_char.kill_dict = player_dict['kill_dict']
    player_char.invisible = player_dict['invisible']
    player_char.flying = player_dict['flying']
    player_char.storage = player_dict['storage']
    player_char.power_up = player_dict['power_up']
    player_char.sight = player_dict['sight']
    player_char.warp_point = player_dict['warp_point']
    return player_char


class Player(Character):
    """
    Player character class
    Health is defined based on initial value and is modified by the constitution stat
    Mana is defined based on the initial value and is modified by the intelligence stat

    encumbered(bool): signifies whether player is over carry weight
    power_up(bool): switch for power-up for retrieving Power Core
    """

    def __init__(self, location_x, location_y, location_z, level, health, mana, stats, combat, gold, resistance):
        super().__init__(name="", health=health, mana=mana, stats=stats, combat=combat)
        self.location_x = location_x
        self.location_y = location_y
        self.location_z = location_z
        self.previous_location = (5, 10, 0)  # starts at town location
        self.state = "normal"
        self.exp_scale = 25
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

    def __str__(self):
        return (
            f"{self.name} | "
            f"Health: {self.health.current}/{self.health.max} | "
            f"Mana: {self.mana.current}/{self.mana.max}"
            )

    def minimap(self):
        """
        Function that allows the player_char to view the current dungeon level in terminal
        20 x 20 grid
        """
        map_size = (20, 20)
        map_array = numpy.zeros(map_size).astype(str)
        for tile in self.world_dict:
            if self.location_z == tile[2]:
                tile_x, tile_y = tile[1], tile[0]
                if self.world_dict[tile].near or self.cls.name == "Seeker":
                    if 'Stairs' in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u25E3"
                    elif "Door" in str(self.world_dict[tile]):
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
                    else:
                        map_array[tile_x][tile_y] = "."
        map_array[self.location_y][self.location_x] = "\u002b"
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
        world_dict = {}
        map_files = glob.glob('map_files/map_level_*')
        for map_file in map_files:
            z = map_file.split('_')[-1]
            z = int(z.split('.')[0])
            with open(map_file, 'r', encoding="utf-8") as f:
                rows = f.readlines()
            x_max = len(rows[0].split('\t'))  # Assumes all rows contain the same number of tabs
            for y, _ in enumerate(rows):
                cols = rows[y].split('\t')
                for x in range(x_max):
                    tile_name = cols[x].replace('\n', '')  # Windows users may need to replace '\r\n'
                    tile = getattr(__import__('map_tiles'), tile_name)(x, y, z)
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
        if self.physical_effects["Disarm"].active:
            action_list.insert(1, "Pickup Weapon")
        if "Summon" in self.spellbook["Skills"] and \
            any([x.is_alive() for x in self.summons.values()]) and \
                not self.status_effects["Silence"].active:
            action_list.insert(1, "Summon")
        if self.cls.name in ["Shaman", "Soulcatcher"]:
            action_list.insert(1, "Totem")
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
        total player level
        """
        return self.level.level + (30 * (self.level.pro_level - 1))

    def max_level(self):
        return any([(self.level.level == 50 and self.level.pro_level == 3),
                    (self.level.level == 30 and self.level.pro_level < 3)])

    def in_town(self):
        return (self.location_x, self.location_y, self.location_z) == (5, 10, 0)

    def to_town(self):
        (self.location_x, self.location_y, self.location_z) = (5, 10, 0)

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

    def game_quit(self, game):
        """
        Function that allows for exiting the game
        """
        confirm_str = "Are you sure you want to quit? Any unsaved data will be lost."
        confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=8)
        if confirm.navigate_popup():
            gamequitbox = utils.TextBox(game)
            gamequitbox.print_text_in_rectangle(f"Goodbye, {self.name}!")
            game.stdscr.getch()
            gamequitbox.clear_rectangle()
            self.quit = True
            return True

    def character_menu(self, game):
        """
        Lists character options
        """
        class_option = "Class Menu"
        class_action = None
        if "Summoner" in self.cls.name:
            class_option = "Summons"
            class_action = actions_dict["Summons"]
        character_options = [actions_dict['ViewInventory'], actions_dict["ViewKeyItems"], actions_dict["Equipment"],
                             actions_dict['Specials'], actions_dict['ViewQuests'], class_action, "Exit Menu", actions_dict['Quit']]
        options = ["Inventory", "Key Items", "Equipment", "Specials", "Quests", class_option, "Exit Menu", "Quit Game"]
        menu = utils.CharacterMenu(game, options)
        menu.draw_all()
        while True:
            character_idx = menu.navigate_menu()
            action = character_options[character_idx]
            if action == "Exit Menu":
                break
            if action is None:
                textbox = utils.TextBox(game)
                textbox.print_text_in_rectangle("Your class does not have a special menu.\n")
                game.stdscr.getch()
                textbox.clear_rectangle()
            else:
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
        return status_message

    def combat_str(self):
        combat_message = ""
        main_dmg = self.check_mod('weapon')
        main_crit = int((self.equipment['Weapon'].crit + (0.005 * self.check_mod("speed"))) * 100)
        if self.equipment['OffHand'].typ == 'Weapon':
            off_dmg = self.check_mod('offhand')
            off_crit = int((self.equipment['OffHand'].crit + (0.005 * self.check_mod("speed"))) * 100)
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
        return (f"{'Armor'}:     {self.equipment['Armor'].name:<30}\n"
                f"{'Weapon'}:    {self.equipment['Weapon'].name:<30}\n"
                f"{'Ring'}:      {self.equipment['Ring'].name:<30}\n"
                f"{'OffHand'}:   {self.equipment['OffHand'].name:<30}\n"
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

    def use_item(self, game, enemy):
        item_message = "Items"
        popup = utils.CombatPopupMenu(game, item_message)
        useitembox = utils.TextBox(game)
        item_options = []
        cat_options = ['Health', 'Mana', 'Elixir', 'Status', 'Scroll']
        for itm in self.inventory:
            if str(self.inventory[itm][0].subtyp) in cat_options:
                item_options.append(str(self.inventory[itm][0].name) + '  ' + str(len(self.inventory[itm])))
        if len(item_options) == 0:
            useitembox.print_text_in_rectangle("You do not have any items to use.")
            game.stdscr.getch()
            useitembox.clear_rectangle()
            return "", False
        item_options.append('Go Back')
        popup.update_options(item_options, item_message)
        item_idx = popup.navigate_popup()
        if item_options[item_idx] == 'Go Back':
            return "", False
        itm = self.inventory[re.split(r"\s{2,}", item_options[item_idx])[0]][0]
        target = None
        if itm.subtyp == "Scroll":
            if itm.spell.subtyp != "Support":
                target = enemy
        return itm.use(self, target=target)

    def level_up(self, game):
        dv = max(1, 5 - self.check_mod('luck', luck_factor=8))
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
        attack_gain = random.randint(0, self.check_mod("luck", luck_factor=12) +
                                    (self.stats.strength // 12) + max(1, self.cls.att_plus // 2))
        self.combat.attack += attack_gain
        defense_gain = random.randint(0, self.check_mod("luck", luck_factor=15) + 
                                    (self.stats.con // 12) + max(1, self.cls.def_plus // 2))
        self.combat.defense += defense_gain
        magic_gain = random.randint(0, self.check_mod("luck", luck_factor=12) +
                                    (self.stats.intel // 12) + max(1, self.cls.int_plus // 2))
        self.combat.magic += magic_gain
        magic_def_gain = random.randint(0, self.check_mod("luck", luck_factor=15) +
                                    (self.stats.wisdom // 12) + max(1, self.cls.wis_plus // 2))
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
        if not self.max_level():
            self.level.exp_to_gain += (self.exp_scale ** self.level.pro_level) * self.level.level
        else:
            self.level.exp_to_gain = "MAX"
        levelupbox = utils.TextBox(game)
        levelupbox.print_text_in_rectangle(level_str)
        game.stdscr.getch()
        levelupbox.clear_rectangle()
        if self.level.level % 4 == 0:
            stat_message = "Pick the stat you would like to increase."
            stat_options = [f'Strength - {self.stats.strength}',
                            f'Intelligence - {self.stats.intel}',
                            f'Wisdom - {self.stats.wisdom}',
                            f'Constitution - {self.stats.con}',
                            f'Charisma - {self.stats.charisma}',
                            f'Dexterity - {self.stats.dex}']
            menu = utils.SelectionPopupMenu(game, stat_message, stat_options, box_height=12, confirm=False)
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
            levelupbox.print_text_in_rectangle(statup_message)
            game.stdscr.getch()
            levelupbox.clear_rectangle()

    def open_up(self, game):
        tile = self.world_dict[(self.location_x, self.location_y, self.location_z)]
        openupbox = utils.TextBox(game)
        if 'Chest' in str(tile):
            locked = int('Locked' in str(tile))
            plus = int('ChestRoom2' in str(tile))
            gold = random.randint(5, 50) * (self.location_z + locked + plus) * self.stats.charisma
            if not random.randint(0, 9 + self.check_mod('luck', luck_factor=3)) and self.level.level >= 10:
                import enemies
                enemy = enemies.Mimic(self.location_z + locked + plus)
                tile.enemy = enemy
                openupbox.print_text_in_rectangle("There is a Mimic in the chest!")
                self.state = 'fight'
                game.battle(enemy)
            if self.is_alive():
                tile.open = True
                loot = tile.loot()
                openupbox.print_text_in_rectangle(
                    f"{self.name} opens the chest, containing {gold} gold and a {loot.name}.")
                game.stdscr.getch()
                openupbox.clear_rectangle()
                self.modify_inventory(loot, 1)
                self.gold += gold
        elif 'Door' in str(tile):
            tile.open = True
            openupbox.print_text_in_rectangle(f"{self.name} opens the door.")
            game.stdscr.getch()
            openupbox.clear_rectangle()
        else:
            raise AssertionError("Something is not working. Check code.")
        openupbox.clear_rectangle()

    def loot(self, enemy, tile):
        loot_message = ""
        items = sum(enemy.inventory.values(), [])
        rare = [False] * len(items)
        drop = [False] * len(items)
        if enemy.gold > 0:
            loot_message += f"{enemy.name} dropped {enemy.gold} gold.\n"
            self.gold += enemy.gold
        for i, item_typ in enumerate(items):
            try:
                item = item_typ()
            except TypeError:
                item = item_typ
            drop[i] = item.subtyp == "Special"
            rare[i] = item.subtyp == "Special"
            if item.subtyp == "Quest":
                for info in self.quest_dict['Side'].values():
                    try:
                        if info['What']().name == item.name and not info['Completed']:
                            rarity = item.rarity
                            if item.name == "Bird Fat" and "Summoner" not in self.cls.name:
                                rarity = 0.75
                            rare[i] = True
                            drop[i] = True if rarity > random.random() else False
                            break
                    except (AttributeError, TypeError):
                        pass
            elif 'Boss' in str(tile):
                drop[i] = True  # all non-quest items will drop from bosses
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
        return loot_message

    def inventory_screen(self, game):
        inv_popup = utils.InventoryPopupMenu(game, "Inventory")
        while True:
            item = inv_popup.navigate_popup()
            if item == "Go Back":
                return
            if self.usable_item(item):
                popup = utils.ConfirmPopupMenu(game, f"Do you want to use the {item.name}", box_height=7)
                if popup.navigate_popup():
                    use_str, _ = item.use(self)
                    if use_str:
                        useitembox = utils.TextBox(game)
                        useitembox.print_text_in_rectangle(use_str)
                        game.stdscr.getch()
                        useitembox.clear_rectangle()
                    if "Sanctuary" in item.name:
                        return

    def key_item_screen(self, game):
        inv_popup = utils.InventoryPopupMenu(game, "Key Items")
        while True:
            item = inv_popup.navigate_popup()
            if item == "Go Back":
                return

    def equipment_screen(self, game):
        e_popup = utils.EquipPopupMenu(game, "Select Equipment", 15)
        e_popup.navigate_popup()

    def abilities_screen(self, game):
        s_popup = utils.AbilitiesPopupMenu(game, "Abilities")
        s_popup.navigate_popup()

    def save(self, game=None, tmp=False):
        if tmp:
            tmp_dir = "tmp_files"
            save_file = tmp_dir + f"/{str(self.name)}.tmp"
            if not os.path.isdir(tmp_dir):
                os.mkdir(tmp_dir)
            with open(save_file, "wb") as save_game:
                dill.dump(self.__dict__, save_game)
        else:
            while True:
                if not os.path.isdir("save_files"):
                    os.mkdir("save_files")
                save_file = f"save_files/{str(self.name).lower()}.save"
                if os.path.exists(save_file):
                    confirm_str = "A save file under this name already exists. Are you sure you want to overwrite it?"
                    confirm = utils.ConfirmPopupMenu(game, confirm_str, box_height=8)
                    if not confirm.navigate_popup():
                        break
                utils.save_file_popup(game)
                with open(save_file, "wb") as save_game:
                    dill.dump(self.__dict__, save_game)
                break

    def equip(self, equip_slot, item, check=False):
        """
        Handles equiping and character modification effects of equipment

        Args:
            equip_slot(str): Equipment slot where item is to be equipped. Must be one of the following: "Weapon",
                "OffHand", "Armor", "Ring", "Pendant"
            item(Equipment): Equipment object to be equipped
            check(bool, optional): A flag signifying whether this is an equipment check or an actual equipment change.
                Default is False.

        Returns:
            None: This function does not return a value.

        Example:
            >>> equip("Weapon", Dirk)
            >>> equip("Armor", LeatherArmor, check=True)

        """
        equip_slots = {"Weapon", "OffHand", "Armor", "Ring", "Pendant"}
        if equip_slot not in equip_slots:
            raise ValueError(f"'equip_slot' must be one of {equip_slots}. Got {equip_slot} instead.")

        if self.equipment[equip_slot].subtyp != 'None' and not check:
            self.modify_inventory(self.equipment[equip_slot])
        if self.equipment[equip_slot].name == "Pendant of Vision" and (self.cls.name not in ["Inquisitor", "Seeker"]):
            self.sight = False
        if self.equipment[equip_slot].name in ["Invisibility Amulet", "Tarnkappe"]:
            self.invisible = False
        if self.equipment[equip_slot].name == 'Levitation Necklace':
            self.flying = False
        if self.cls.name not in ["Lancer", "Dragoon", "Berserker"]:
            if equip_slot == "Weapon":
                if item.handed == 2:
                    if self.equipment["OffHand"].subtyp != 'None' and not check:
                        self.modify_inventory(self.equipment["OffHand"])
                    if not check:
                        self.equipment["OffHand"] = remove_equipment("OffHand")
            if equip_slot == "OffHand":
                if self.equipment["Weapon"].handed == 2:
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

    def equip_diff(self, item, equip_slot, buy=False):
        """
        function to analyze impact of item on player
        """
        if equip_slot == "Accessory":
            equip_slot = item.subtyp
        current_equipment = self.equipment.copy()  # copy old equipment to use at end
        main_dmg = self.check_mod('weapon')
        main_crit = int((self.equipment['Weapon'].crit + (0.005 * self.check_mod("speed"))) * 100)
        attack = f"{str(main_dmg)}"
        crit = f"{str(main_crit)}%"
        if self.equipment['OffHand'].typ == 'Weapon':
            off_dmg = self.check_mod('offhand')
            off_crit = int((self.equipment['OffHand'].crit  + (0.005 * self.check_mod("speed"))) * 100)
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

        # equip new item
        self.equip(equip_slot, item, check=True)
        if equip_slot == "Weapon" and item.subtyp in self.cls.restrictions["OffHand"] and buy:
            self.equip("OffHand", item)
        new_main_dmg = self.check_mod('weapon')
        if new_main_dmg != main_dmg:
            diff_dict["Attack"] = f"{main_dmg} -> {new_main_dmg}"
        new_main_crit = int((self.equipment['Weapon'].crit + (0.005 * self.check_mod("speed"))) * 100)
        if new_main_crit != main_crit:
            diff_dict["Critical Chance"] = f"{main_crit}% -> {new_main_crit}%"
        if equip_slot == 'Weapon':
            if current_equipment['OffHand'].typ == 'Weapon':
                if item.handed == 2 and self.cls.name not in ["Lancer", "Dragoon", "Berserker"]:
                    diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {new_main_dmg}"
                    diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {new_main_crit}%"
                else:
                    new_off_dmg = self.check_mod('offhand')
                    new_off_crit = int((self.equipment['OffHand'].crit + (0.005 * self.check_mod("speed"))) * 100)
                    if new_main_dmg != main_dmg or new_off_dmg != off_dmg:
                        diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {new_main_dmg}/{new_off_dmg}"
                    if new_main_crit != main_crit or new_off_crit != off_crit:
                        diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {new_main_crit}%/{new_off_crit}%"                    
            elif item.subtyp in self.cls.restrictions["OffHand"] and buy:
                new_off_dmg = self.check_mod('offhand')
                new_off_crit = int((self.equipment['OffHand'].crit + (0.005 * self.check_mod("speed"))) * 100)
                if current_equipment["OffHand"].typ == "Weapon":
                    diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {new_main_dmg}/{new_off_dmg}"
                    diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {new_main_crit}%/{new_off_crit}%"
                else:
                    diff_dict["Attack"] = f"{main_dmg} -> {new_main_dmg}/{new_off_dmg}"
                    diff_dict["Critical Chance"] = f"{main_crit}% -> {new_main_crit}%/{new_off_crit}%"
            else:
                pass
        if equip_slot == 'OffHand':
            if item.typ == "Weapon":
                new_off_dmg = self.check_mod('offhand')
                new_off_crit = int((self.equipment['OffHand'].crit + (0.005 * self.check_mod("speed"))) * 100)
                diff_dict["Attack"] = f"{main_dmg} -> {main_dmg}/{new_off_dmg}"
                diff_dict["Critical Chance"] = f"{main_crit}% -> {main_crit}%/{new_off_crit}%"
                if current_equipment["OffHand"].typ == 'Weapon':
                    diff_dict["Attack"] = f"{main_dmg}/{off_dmg} -> {main_dmg}/{new_off_dmg}"
                    diff_dict["Critical Chance"] = f"{main_crit}%/{off_crit}% -> {main_crit}%/{new_off_crit}%"
            if item.subtyp == "None" and current_equipment["OffHand"].typ == "Weapon":
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

        # revert equipment to before
        self.equip(equip_slot, current_equipment[equip_slot], check=True)
        if equip_slot == "Weapon" and item.subtyp in self.cls.restrictions["OffHand"] and buy:
            self.equip("OffHand", current_equipment[equip_slot])
        return "\n".join([f"{x:16}{' ':2}{y:>6}" for x, y in diff_dict.items()])

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
        self.previous_location = (self.location_x, self.location_y, self.location_z)
        new_x = self.location_x + dx
        new_y = self.location_y + dy
        if self.world_dict[(new_x, new_y, self.location_z)].enter:
            self.location_x += dx
            self.location_y += dy

    def stairs(self, dz):
        self.previous_location = (self.location_x, self.location_y, self.location_z)
        self.location_z += dz

    def move_north(self, game):
        self.move(dx=0, dy=-1)

    def move_south(self, game):
        self.move(dx=0, dy=1)

    def move_east(self, game):
        self.move(dx=1, dy=0)

    def move_west(self, game):
        self.move(dx=-1, dy=0)

    def stairs_up(self, game):
        self.stairs(dz=-1)

    def stairs_down(self, game):
        self.stairs(dz=1)

    def change_location(self, x, y, z):
        self.location_x = x
        self.location_y = y
        self.location_z = z

    def death(self, game):
        """
        Controls what happens when you die; no negative affect will occur for players under level 10
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
        deathbox = utils.TextBox(game)
        deathbox.print_text_in_rectangle(death_message)
        game.stdscr.getch()
        deathbox.clear_rectangle()

    def class_upgrades(self, game, enemy):
        upgrade_str = ""
        if self.cls.name == "Soulcatcher":
            limiter = 1  # TODO 
            chance = max(limiter, 19 - self.check_mod('luck', enemy=enemy, luck_factor=20))
            if not random.randint(0, chance):  # 5% chance on kill
                upgrade_str += f"You absorb part of the {enemy.name}'s soul.\n"
                if enemy.name in ['Behemoth', 'Golem', 'Iron Golem']:
                    upgrade_str += "Gain 1 strength.\n"
                    self.stats.strength += 1
                if enemy.name in ['Lich', 'Brain Gorger']:
                    upgrade_str += "Gain 1 intelligence.\n"
                    self.stats.intel += 1
                if enemy.name in ['Aboleth', 'Hydra']:
                    upgrade_str += "Gain 1 wisdom.\n"
                    self.stats.wisdom += 1
                if enemy.name in ['Warforged', 'Archvile']:
                    upgrade_str += "Gain 1 constitution.\n"
                    self.stats.con += 1
                if enemy.name in ['Beholder', 'Wyrm']:
                    upgrade_str += "Gain 1 charisma.\n"
                    self.stats.charisma += 1
                if enemy.name in ['Shadow Serpent', 'Wyvern']:
                    upgrade_str += "Gain 1 dexterity.\n"
                    self.stats.dex += 1
                if enemy.name in ['Basilisk', 'Sandworm']:
                    upgrade_str += "Gain 5 hit points.\n"
                    self.health.max += 5
                if enemy.name == 'Mind Flayer':
                    upgrade_str += "Gain 5 mana points.\n"
                    self.mana.max += 5
                if enemy.name in ['Jester', 'Domingo', 'Cerberus']:
                    if not self.max_level():
                        upgrade_str += "Gain enough experience to level.\n"
                        self.level.exp += self.level.exp_to_gain
                        self.level.exp_to_gain = 0
                        self.level_up(game)
                if enemy.name == 'Red Dragon':
                    upgrade_str += "You find a cache of gold, doubling your current stash.\n"
                    self.gold *= 2
        if self.cls.name == "Lycan" and enemy.name == 'Red Dragon':
            upgrade_str += f"{self.name} has harnessed the power of the Red Dragon and can now transform into one!\n"
            self.spellbook['Skills']['Transform'] = abilities.Transform4()
            self.spellbook['Skills']['Transform'].use(self)

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

    def end_combat(self, game, enemy, tile, flee=False, summon=None):
        self.state = 'normal'
        endcombatbox = utils.TextBox(game)
        self.transform(back=True)
        self.effects(end=True)
        if all([self.is_alive(), not flee]):
            endcombat_str = (f"{self.name} killed {enemy.name}.\n"
                             f"{self.name} gained {enemy.experience} experience.\n")
            if summon:
                summon.effects(end=True)
                endcombat_str += f"{summon.name} gained {enemy.experience} experience.\n"
                summon.level.exp += enemy.experience
                if summon.level.level < 10:
                    summon.level.exp_to_gain -= enemy.experience
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
            endcombatbox.print_text_in_rectangle(endcombat_str)
            time.sleep(0.25)
            game.stdscr.getch()
            endcombatbox.clear_rectangle()
            self.level.exp += enemy.experience
            self.class_upgrades(game, enemy)
            if not self.max_level():
                self.level.exp_to_gain -= enemy.experience
                while self.level.exp_to_gain <= 0:
                    self.level_up(game)
                    if self.max_level():
                        break
        elif flee:
            pass
        else:
            endcombatbox.print_text_in_rectangle(f"{self.name} was slain by {enemy.name}.")
            time.sleep(0.5)
            game.stdscr.getch()
            endcombatbox.clear_rectangle()
            enemy.effects(end=True)
            enemy.health.current = enemy.health.max
            enemy.mana.current = enemy.mana.max
            self.death(game)

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
        elif item is not None:
            for quest in self.quest_dict['Side']:
                try:
                    if self.quest_dict['Side'][quest]['What']().name == item.name:
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

    def quests_screen(self, game):
        q_popup = utils.QuestListPopupMenu(game, "Quests")
        q_popup.navigate_popup()

    def check_mod(self, mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        berserk_per = int(self.status_effects["Berserk"].active) * 0.1  # berserk increases damage by 10%
        if self.cls.name == "Soulcatcher" and self.power_up:
            if enemy:
                class_mod += (sum(self.kill_dict[enemy.enemy_typ].values()) // 20)
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.physical_effects["Disarm"].active))
            if 'Monk' in self.cls.name:
                class_mod += self.stats.wisdom
            if self.cls.name in ["Thief", "Rogue", "Assassin", "Ninja"]:
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
            total_mod = weapon_mod + class_mod + self.combat.attack
            return max(0, int(total_mod * (1 + berserk_per)))
        if mod == 'shield':
            block_mod = 0
            if self.equipment['OffHand'].subtyp == 'Shield':
                block_mod = round(self.equipment['OffHand'].mod * 100)
            if self.equipment['Ring'].mod == "Block":
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
                if 'Physical Damage' in self.equipment['Ring'].mod:
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
                if self.familiar.spec == 'Homunculus' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
                    fam_mod = random.randint(0, 3) ** self.familiar.level.pro_level
                    class_mod += fam_mod
            if self.cls.name == "Berserker" and self.power_up and (self.health.current / self.health.max) < 0.3:
                class_mod += (self.player_level() // 11)
            if self.cls.name == 'Dragoon' and self.power_up:
                class_mod = armor_mod * self.class_effects["Power Up"].active * self.class_effects["Power Up"].duration
            if 'Physical Defense' in self.equipment['Ring'].mod:
                armor_mod += int(self.equipment['Ring'].mod.split(' ')[0])
            armor_mod += self.stat_effects["Defense"].extra * self.stat_effects["Defense"].active
            return max(0, (armor_mod * int(not ignore)) + class_mod + self.combat.defense)
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                magic_mod += self.equipment['OffHand'].mod
            if self.equipment['Weapon'].subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon'].damage * 0.75)
            if 'Magic Damage' in self.equipment['Pendant'].mod:
                magic_mod += int(self.equipment['Pendant'].mod.split(' ')[0])
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            if self.cls.name == "Shadowcaster" and self.class_effects["Power Up"].active:
                class_mod += magic_mod
            return max(0, magic_mod + class_mod + self.combat.magic)
        if mod == 'magic def':
            m_def_mod = self.stats.wisdom * self.level.pro_level
            if "Magic Defense" in self.equipment['Pendant'].mod:
                m_def_mod += int(self.equipment['Pendant'].mod.split(' ')[0])
            m_def_mod += self.stat_effects["Magic Defense"].extra * self.stat_effects["Magic Defense"].active
            return max(0, m_def_mod + class_mod + self.combat.magic_def)
        if mod == 'heal':
            heal_mod = self.stats.wisdom * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                heal_mod += self.equipment['OffHand'].mod
            elif self.equipment['Weapon'].subtyp == 'Staff':
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
                if self.familiar.spec == 'Mephit' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
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
            luck_mod = self.stats.charisma // luck_factor
            return luck_mod
        if mod == "speed":
            speed_mod = self.stats.dex
            speed_mod += self.stat_effects["Speed"].extra * self.stat_effects["Speed"].active
            return speed_mod
        return 0

    def special_power(self, game):
        """
        Player attains power up following quest to find the Power Core, used to give Golems life
        Each class has a unique combat ability (* means implemented)

        *Berserker - Blood Rage(passive): attack increases as health decreases; if below 30% health, bonus to defense
        *Crusader - Divine Aegis: create shell that absorbs damage and increases healing; if the shield survives
          the full duration, it will explode and deal holy damage to the enemy
        *Dragoon - Dragon's Fury(passive): attack and defense double for each successive hit; a miss resets this buff
        Stalwart Defender - 
        *Wizard - Spell Mastery(passive): automatically triggers when no spells can be cast due to low mana; all spells
          become free for a short time and mana regens based on damage dealt
        *Shadowcaster - Veil of Shadows(passive): become one with the darkness, making the player invisible to most enemies
          and making them harder to hit; increases damage of initial attack if first
        *Knight Enchanter - Arcane Blast: blast the enemy with a powerful attack, draining all remaining mana points; mana
          will regen in full over the next 4 turns (25% per turn)
        Summoner - 
        *Rogue - Stroke of Luck(passive): the Rogue is incredibly lucky, gaining bonuses to all luck-based checks, including
          dodge and critical chance
        *Seeker - Eyes of the Unseen(passive): gain increased awareness of battle situations, increasing critical chance as 
          well as chance to dodge/parry attacks
        *Ninja - Blade of Fatalities: sacrifice percentage of health to imbue blade with the spirit of Muramasa, increasing
          damage dealt and absorbing it into the user
        Arcane Trickster - 
        *Templar - Holy Retribution: a radiant shield envelopes the Templar, reflecting damage back at the attacker; while
          the shield is active, attack damage and chance to dodge/parry increase
        *Archbishop - Great Gospel: regens health and mana over time, and restores status; increases magic resistance and 
          holy damage for duration
        *Master Monk - Dim Mak: unleash a powerful attack that deals heavy damage and can either stun or in some cases 
          kill the target; if the target is killed, the user will absorb the enemy's essence and will be regenerated by
          its max health and mana
        Troubadour - 
        *Lycan - Lunar Frenzy(passive): the longer the Lycan is transformed, the further into madness they fall, increasing
          damage and regenerating health on critical hits; if the Lycan stays transformed for longer than 5 turns, they 
          will be unable to transform back until after the battle
        *Geomancer - Tetra-Disaster: unleash a powerful attack consisting of all 4 elements; this will also increase resistance
          of caster to the 4 elements by 50%
        *Soulcatcher - Soul Harvest(passive): each enemy killed of a particular type will increase attack damage against
          that enemy type
        Beast Master - 
        """

        powerup_dict = {
            "Berserker": abilities.BloodRage,
            "Crusader": abilities.DivineAegis,
            "Dragoon": abilities.DragonsFury,
            "Wizard": abilities.SpellMastery,
            "Shadowcaster": abilities.VeilShadows,
            "Knight Enchanter": abilities.ArcaneBlast,
            "Rogue": abilities.StrokeLuck,
            "Seeker": abilities.EyesUnseen,
            "Ninja": abilities.BladeFatalities,
            "Templar": abilities.HolyRetribution,
            "Archbishop": abilities.GreatGospel,
            "Master Monk": abilities.DimMak,
            "Lycan": abilities.LunarFrenzy,
            "Geomancer": abilities.TetraDisaster,
            "Soulcatcher": abilities.SoulHarvest
        }
        game.special_event("Power Up")
        skill = powerup_dict[self.cls.name]()
        self.spellbook['Skills'][skill.name] = skill
        self.power_up = True
        if self.cls.name == "Shadowcaster":
            self.invisible = True
        return f"You gain the skill {skill.name}.\n"

    def summon_menu(self, game):
        summon_names = list(self.summons)
        summonpopup = utils.SelectionPopupMenu(game, "Summons", summon_names, confirm=False)
        summon_idx = summonpopup.navigate_popup()
        summon = self.summons[summon_names[summon_idx]]
        summonbox = utils.TextBox(game)
        summonbox.print_text_in_rectangle(summon.inspect())
        game.stdscr.getch()
        summonbox.clear_rectangle()


actions_dict = {
    'MoveNorth': {
        'method': Player.move_north,
        'name': 'Move north (w)',
        'hotkey': 'w'
    },
    'MoveSouth': {
        'method': Player.move_south,
        'name': 'Move south (s)',
        'hotkey': 's'
    },
    'MoveEast': {
        'method': Player.move_east,
        'name': 'Move east (d)',
        'hotkey': 'd'
    },
    'MoveWest': {
        'method': Player.move_west,
        'name': 'Move west (a)',
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
        'name': 'Inventory',
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
    'Flee': {
        'method': Player.flee,
        'name': 'Flee',
        'hotkey': None
    },
    'UseItem': {
        'method': Player.use_item,
        'name': 'Use Item',
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
