"""
This module defines the player character and its attributes and actions.
"""

# Imports
import os
import re
import glob
import random
import time
import pickle

import numpy

import combat
import enemies
import items
import storyline
import abilities
import races
import classes
import town
from character import Character, Stats, Resource, Level


def new_char() -> object:
    """
    Defines a new character and places them in the town to start
    Initial HP: 2 x constitution score
    Level HP: (0.75 * level * promotion level) + (con // 2) (Average)
    Initial MP: intelligence score + 0.5 x wisdom score
    Level MP: (0.75 * level * promotion level) + (intel // 2) (Average)
    Initial Gold: 25 x charisma score
    """
    exp_scale = 25
    location_x, location_y, location_z = (5, 10, 0)
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        race = races.define_race()
        os.system('cls' if os.name == 'nt' else 'clear')
        cls = classes.define_class(race)
        if cls:
            break
        time.sleep(0.5)
        os.system('cls' if os.name == 'nt' else 'clear')
    name = ''
    while name == '':
        os.system('cls' if os.name == 'nt' else 'clear')
        storyline.slow_type("What is your character's name?\n")
        name = input("").capitalize()
        if name == '' or len(name) > 20:
            print("Please enter a valid name.")
            time.sleep(1)
            name = ''
        else:
            print(f"You have chosen to name your character {name}. Is this correct? ")
            keep = storyline.get_response(['Yes', 'No'])
            if keep == 1:
                name = ''
    created = f"Welcome {name}, the {race.name} {cls.name}.\nReport to the barracks for your orders."
    storyline.slow_type(created)
    time.sleep(1)
    stats = tuple(map(lambda x, y: x + y, (race.strength, race.intel, race.wisdom, race.con, race.charisma, race.dex),
                     (cls.str_plus, cls.int_plus, cls.wis_plus, cls.con_plus, cls.cha_plus, cls.dex_plus)))
    hp = stats[3] * 2  # starting HP equal to constitution x 2
    mp = stats[1] + int(stats[2] * 0.5)  # starting MP equal to intel and wis x 0.5
    gil = stats[4] * 25  # starting gold equal to charisma x 25
    player_char = Player(location_x, location_y, location_z, level=Level(1, 1, 0, exp_scale),
                         health=Resource(hp, hp), mana=Resource(mp, mp),
                         stats=Stats(stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]),
                         gold=gil, resistance=race.resistance)
    player_char.name = name
    player_char.race = race
    player_char.cls = cls
    player_char.equipment = cls.equipment
    player_char.load_tiles()
    return player_char


def load(char=None):
    """
    Loads a save file and returns 2 dictionaries: one for the character and another for the world setup
    """
    if char is None:
        save_files = glob.glob("*.save")
        if len(save_files) == 0:
            return {}
        chars = []
        for f in save_files:
            chars.append(f.split('.')[0].capitalize())
        chars.append('Go Back')
        print("Select the name of the character you want to load.")
        choice = storyline.get_response(chars)
        if chars[choice] == 'Go Back':
            return {}
        save_file = chars[choice] + ".save"
        with open(save_file, "rb") as save_file:
            player_dict = pickle.load(save_file)
        return player_dict
    if os.path.exists(char + ".save"):
        with open(char + ".save", "rb") as save_file:
            player_dict = pickle.load(save_file)
        return player_dict
    return {}


def load_char(char=None, tmp=False):
    """
    Initializes the character based on the load file
    """
    if tmp:
        load_file = "tmp_files/" + str(char.name).lower() + ".tmp"
        with open(load_file, "rb") as l_file:
            l_dict = pickle.load(l_file)
        os.system(f"rm {load_file}")
        return l_dict
    if char is None:
        player_dict = load()
    else:
        player_dict = load(char)
    if player_dict == {}:
        return player_dict
    player_char = Player(player_dict['location_x'], player_dict['location_y'], player_dict['location_z'],
                         player_dict['level'], player_dict['health'], player_dict['mana'], 
                         player_dict['stats'], player_dict['gold'], player_dict['resistance'])
    player_char.name = player_dict['name']
    player_char.race = player_dict['race']
    player_char.cls = player_dict['cls']
    player_char.status_effects = player_dict['status_effects']
    player_char.equipment = player_dict['equipment']
    player_char.inventory = player_dict['inventory']
    player_char.special_inventory = player_dict['special_inventory']
    player_char.spellbook = player_dict['spellbook']
    player_char.familiar = player_dict['familiar']
    player_char.transform = player_dict['transform']
    player_char.teleport = player_dict['teleport']
    player_char.world_dict = player_dict['world_dict']
    player_char.quest_dict = player_dict['quest_dict']
    player_char.kill_dict = player_dict['kill_dict']
    player_char.invisible = player_dict['invisible']
    player_char.flying = player_dict['flying']
    player_char.storage = player_dict['storage']
    player_char.quit = False
    return player_char


class Player(Character):
    """
    Player character class
    Health is defined based on initial value and is modified by the constitution parameter
    Mana is defined based on the initial value and is modified by the intelligence and half the wisdom parameters
    """

    def __init__(self, location_x, location_y, location_z, level, health, mana, stats, gold, resistance):
        super().__init__(name="", health=health, mana=mana, stats=stats)
        self.location_x = location_x
        self.location_y = location_y
        self.location_z = location_z
        self.state = "normal"
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
        self.transform = None

    def __str__(self):
        return f"Player: {self.name} | Health: {self.health.current}/{self.health.max} | Mana: {self.mana.current}/{self.mana.max}"

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
                if self.world_dict[tile].near:
                    if self.world_dict[tile] is None:
                        continue
                    if 'Stairs' in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "\u25E3"
                    elif 'DoorEast' in str(self.world_dict[tile]) or \
                            'DoorWest' in str(self.world_dict[tile]):
                        if not self.world_dict[tile].open:
                            map_array[tile_x][tile_y] = "|"
                        else:
                            map_array[tile_x][tile_y] = "."
                    elif 'DoorNorth' in str(self.world_dict[tile]) or \
                            'DoorSouth' in str(self.world_dict[tile]):
                        if not self.world_dict[tile].open:
                            map_array[tile_x][tile_y] = "_"
                        else:
                            map_array[tile_x][tile_y] = "."
                    elif 'Wall' in str(self.world_dict[tile]):
                        map_array[tile_x][tile_y] = "#"
                    elif 'Chest' in str(self.world_dict[tile]):
                        if self.world_dict[tile].open:
                            map_array[tile_x][tile_y] = "\u25A1"
                        else:
                            map_array[tile_x][tile_y] = "\u25A0"
                    elif 'Relic' in str(self.world_dict[tile]):
                        if not self.world_dict[tile].read:
                            map_array[tile_x][tile_y] = "\u25C9"
                        else:
                            map_array[tile_x][tile_y] = "\u25CB"
                    else:
                        map_array[tile_x][tile_y] = "."
        map_array[self.location_y][self.location_x] = "\u001b[5m+\u001b[0m"
        map_array[map_array == "0.0"] = " "
        map_array = numpy.insert(map_array, 0, numpy.zeros(map_array.shape[1]), 0)
        map_array[map_array == "0.0"] = "\u203E"  # overline character
        map_array = numpy.vstack([map_array, numpy.zeros(map_array.shape[1])])
        map_array[map_array == "0.0"] = "_"
        map_array = numpy.insert(map_array, 0, numpy.zeros(map_array.shape[0]), 1)
        map_array[map_array == "0.0"] = "|"
        map_array = numpy.append(map_array, numpy.zeros(map_array.shape[0]).reshape(-1, 1), 1)
        map_array[map_array == "0.0"] = "|"
        for i in map_array:
            print(" ".join(i))

    def load_tiles(self):
        """Parses a file that describes the world space into the _world object"""
        world_dict = {(5, 10, 0): getattr(__import__('map'), 'Town')(5, 10, 0)}
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
                    tile = getattr(__import__('map'), tile_name)(x, y, z)
                    world_dict[(x, y, z)] = tile
        self.world_dict = world_dict

    def options(self, action_list):
        """
        Controls the listed options during combat
        """
        print("Choose an action:")
        option_list = []
        for action in action_list:
            try:
                option_list.append(action["name"])
            except TypeError:
                option_list.append(action)
        if self.status_effects['Mana Shield'].active:
            option_list.append("Remove Shield")
        if not self.cls:
            option_list.append("Untransform")
        action_input = storyline.get_response(option_list)
        return option_list[action_input]

    def combat_turn(self, enemy, action, in_combat):
        valid_entry = False
        flee = False
        tile = self.world_dict[(self.location_x, self.location_y, self.location_z)]
        if action == 'Remove Shield':
            print(f"The mana shield dissolves around {self.name}.")
            self.status_effects['Mana Shield'].active = False
            valid_entry = False
            time.sleep(0.1)
        elif action == 'Untransform':
            self.transform(back=True)
            valid_entry = False
        else:
            if action == 'Open':
                self.open_up(enemy)
                in_combat = False
                valid_entry = True
            if action == 'Attack':
                self.weapon_damage(enemy)
                valid_entry = True
            if action == 'Use Item':
                valid_entry = self.use_item(enemy=enemy)
            if action == 'Flee':
                flee = self.flee(enemy)
                valid_entry = True
            if action == 'Cast Spell':
                spell_list = []
                for entry in self.spellbook['Spells']:
                    if self.spellbook['Spells'][entry]().subtyp == "Movement":
                        continue
                    if self.spellbook['Spells'][entry]().cost <= self.mana.current:
                        spell_list.append(str(entry) + '  ' + str(self.spellbook['Spells'][entry]().cost))
                spell_list.append('Go Back')
                spell_index = storyline.get_response(spell_list)
                if spell_list[spell_index] == 'Go Back':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return False, in_combat, flee
                spell = self.spellbook['Spells'][spell_list[spell_index].split('  ')[0]]
                spell().cast(self, target=enemy)
                valid_entry = True
            if action == 'Use Skill':
                skill_list = []
                for entry in self.spellbook['Skills']:
                    if self.spellbook['Skills'][entry]().cost <= self.mana.current:
                        if self.spellbook['Skills'][entry]().passive:
                            continue
                        if self.spellbook['Skills'][entry]().name == 'Smoke Screen' and 'Boss' in \
                                tile.intro_text(self):
                            continue
                        if self.spellbook['Skills'][entry]().name == 'Lockpick':
                            continue
                        if self.spellbook['Skills'][entry]().name == 'Shield Slam' and \
                                self.equipment['OffHand']().subtyp != 'Shield':
                            continue
                        skill_list.append(str(entry) + '  ' + str(self.spellbook['Skills'][entry]().cost))
                skill_list.append('Go Back')
                skill_index = storyline.get_response(skill_list)
                if skill_list[skill_index] == 'Go Back':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return False, in_combat, flee
                valid = True
                skill = self.spellbook['Skills'][skill_list[skill_index].split('  ')[0]]
                if skill().name == 'Smoke Screen':
                    skill().use(self, target=enemy)
                    flee = self.flee(enemy, smoke=True)
                elif skill().name == 'Transform':
                    self.transform()
                    valid = False
                else:
                    skill().use(self, target=enemy)
                valid_entry = valid
        if flee:
            # Moves the player_char randomly to an adjacent tile
            time.sleep(1.5)
            available_moves = tile.adjacent_moves(self)
            r = random.choice(available_moves)
            r['method'](self)
            in_combat = False
        return valid_entry, in_combat, flee

    def has_relics(self):
        relics = ["Triangulus", "Quadrata", "Hexagonum", "Luna", "Polaris", "Infinitas"]
        return all(item in self.special_inventory for item in relics)

    def max_level(self):
        return any([(self.level.level == 50 and self.level.pro_level == 3), 
                    (self.level.level == 30 and self.level.pro_level < 3)])

    def in_town(self):
        return (self.location_x, self.location_y, self.location_z) == (5, 10, 0)

    def usable_abilities(self, typ):
        assert typ in ["Skills", "Spells"]
        for ability in self.spellbook[typ].values():
            if not ability().passive and ability().cost <= self.mana.current:
                if ability().name == 'Shield Slam' and self.equipment['OffHand']().subtyp != 'Shield':
                    continue
                return True
        return False
    
    def max_weight(self):
        return self.stats.strength * 10
    
    def current_weight(self):
        weight = 0
        for item in self.equipment.values():
            weight += item().weight
        for item in self.inventory.values():
            weight += item[0]().weight * item[1]
        return round(weight, 1)
    
    def add_weight(self, item):
        """
        Calculates weight of equipment/inventory and returns whether the item can be added
        item (list): a list containing the item object and how many items you are trying to add
        """
        total_weight = item[0]().weight * item[1]
        return self.max_weight() > self.current_weight() + total_weight

    def game_quit(self):
        """
        Function that allows for exiting the game
        """
        print("Are you sure you want to quit? Any unsaved data will be lost. ")
        q = storyline.get_response(["Yes", "No"])
        if not q:
            print(f"Goodbye, {self.name}!")
            time.sleep(2)
            self.quit = True
            return True
        return False

    def character_menu(self):
        """
        Lists character options
        """
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(str(self))
            option_list = [actions_dict['Status'], actions_dict['ViewInventory'], actions_dict['Equip'],
                           actions_dict['UseItem'], actions_dict['ViewQuests'], actions_dict['Quit']]
            options = ["Status", "Inventory", "Equip", "Use Item", "Quests", "Quit Game", "Leave"]
            action_input = storyline.get_response(options)
            try:
                action = option_list[action_input]
                if options[action_input] == "Use Item":
                    done = False
                    while not done:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print(str(self))
                        done = self.use_item()
                        time.sleep(0.5)
                else:
                    action['method'](self)
            except IndexError:
                break
            if self.quit:
                break
            time.sleep(0.5)

    def status(self):
        """
        Prints the status of the character
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print("#" + (20 * "=") + "#")
        print(f"Name: {self.name}")
        print(f"Race: {self.race.name}")
        print(f"Class: {self.cls.name}")
        print(f"Level: {self.level.level}")
        print(f"Experience: {self.level.exp}/{self.level.exp_to_gain}")
        print(f"HP: {self.health.current}/{self.health.max}")
        print(f"MP: {self.mana.current}/{self.mana.max}")
        print(f"Strength: {self.stats.strength}")
        print(f"Intelligence: {self.stats.intel}")
        print(f"Wisdom: {self.stats.wisdom}")
        print(f"Constitution: {self.stats.con}")
        print(f"Charisma: {self.stats.charisma}")
        print(f"Dexterity: {self.stats.dex}")
        main_dmg = self.check_mod('weapon')
        main_crit = int(self.equipment['Weapon']().crit * 100)
        if self.equipment['OffHand']().typ == 'Weapon':
            off_dmg = self.check_mod('offhand')
            off_crit = int(self.equipment['OffHand']().crit * 100)
            print(f"Attack: {str(main_dmg)}/{str(off_dmg)}")
            print(f"Critical Chance: {str(main_crit)}%/{str(off_crit)}%")
        else:
            print(f"Attack: {str(main_dmg)}")
            print(f"Critical Chance: {str(main_crit)}%")
        print(f"Armor: {self.check_mod('armor')}")
        if self.equipment['OffHand']().subtyp == 'Shield':
            block = round(self.equipment['OffHand']().mod * (1 + ('Shield Block' in self.spellbook['Skills'])) * 100)
            print(f"Block Chance: {block}%")
        if len(self.spellbook['Spells']) > 0:
            spell_mod = self.check_mod('magic')
            print(f"Spell Modifier: +{str(spell_mod)}")
            if any(x().subtyp == 'Heal' for x in self.spellbook['Spells'].values()):
                heal_mod = self.check_mod('heal')
                print(f"Heal Modifier: +{str(heal_mod)}")
        buffs = []
        if any([self.flying, self.invisible]):
            if self.flying:
                buffs.append("Flying")
            if self.invisible:
                buffs.append("Invisible")
            print("Buffs: " + ", ".join(buffs))
        print("#" + (20 * "=") + "#")
        if self.cls.name in ['Warlock', 'Shadowcaster']:
            print(f"Familiar Name: {self.familiar.name}")
            print(f"Familiar Type: {self.familiar.typ}")
            print(f"Specialty: {self.familiar.spec}")
        option_list = ["Equipment", "Specials", "Go Back"]
        option_input = storyline.get_response(option_list)
        if option_list[option_input] == "Specials":
            self.specials()
        elif option_list[option_input] == "Equipment":
            print("Equipment")
            equip_list = ["Weapon - " + self.equipment['Weapon']().name,
                          "Armor - " + self.equipment['Armor']().name,
                          "Ring - " + self.equipment['Ring']().name,
                          "Pendant - " + self.equipment['Pendant']().name]
            if self.equipment['Weapon']().handed == 1 or self.cls.name == 'Lancer' or self.cls.name == 'Dragoon' \
                    or self.cls.name == 'Berserker':
                equip_list.insert(2, "OffHand - " + self.equipment['OffHand']().name)
            equip_list.append("Go Back")
            equip_input = storyline.get_response(equip_list)
            if equip_list[equip_input] == "Go Back":
                return
            equip_choice = equip_list[equip_input].split(" ")[0]
            print(str(self.equipment[equip_choice]()))
        input("Press enter to continue")


    def flee(self, enemy, smoke=False) -> bool:
        stun = enemy.status_effects['Stun'].active
        if smoke or stun:
            print(f"{self.name} flees from the {enemy.name}.")
            self.state = 'normal'
            return True
        chance = self.check_mod('luck', luck_factor=10)
        if random.randint(self.stats.dex // 2, self.stats.dex) + chance > \
                random.randint(enemy.stats.dex // 2, enemy.stats.dex):
            print(f"{self.name} flees from the {enemy.name}.")
            self.state = 'normal'
            return True
        print(f"{self.name} couldn't escape from the {enemy.name}.")
        return False

    def use_item(self, enemy=None):
        tile = self.world_dict[(self.location_x, self.location_y, self.location_z)]
        cat_dict = {'Health': [],
                    'Mana': [],
                    'Elixir': [],
                    'Stat': [],
                    'Status': [],
                    'Scroll': [],
                    'Key': []}
        if enemy is not None:
            cat_list = ['Health', 'Mana', 'Elixir', 'Status', 'Scroll']
            for itm in self.inventory:
                if str(self.inventory[itm][0]().subtyp) in cat_list:
                    cat_dict[str(self.inventory[itm][0]().subtyp)].append(
                        str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
        else:
            cat_list = ['Health', 'Mana', 'Elixir', 'Status', 'Scroll', 'Key']
            if 'Locked' in str(tile):
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().subtyp) in cat_list:
                        cat_dict[str(self.inventory[itm][0]().subtyp)].append(
                            str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
            elif self.in_town():
                cat_list = ['Stat']
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().subtyp) == 'Stat':
                        cat_dict[str(self.inventory[itm][0]().subtyp)].append(
                            str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
            else:
                cat_list = ['Health', 'Mana', 'Elixir', 'Stat']
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().subtyp) in cat_list:
                        cat_dict[str(self.inventory[itm][0]().subtyp)].append(
                            str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
        cat_dict = {k: v for k, v in cat_dict.items() if v}
        cat_list = [x for x in cat_list if x in cat_dict.keys()]
        done = True if enemy is None else False
        if not cat_list:
            print("You do not have any items to use.")
            time.sleep(0.5)
            return done
        cat_list.append('Go Back')
        cat_choice = storyline.get_response(cat_list)
        if cat_list[cat_choice] == 'Go Back':
            return done
        item_list = cat_dict[cat_list[cat_choice]].copy()
        if len(item_list) == 0:
            print("You do not have any items to use.")
            time.sleep(0.5)
            return done
        item_list.append('Go Back')
        print("Which item would you like to use?")
        use_itm = storyline.get_response(item_list)
        if item_list[use_itm] == 'Go Back':
            return done
        itm = self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]
        target = None
        if itm().subtyp == "Scroll":
            if itm().spell().subtyp != "Support":
                target = enemy
        done = itm().use(self, target=target)
        time.sleep(0.5)
        return done

    def level_up(self):
        exp_scale = 25
        print("You gained a level.")
        if (self.level.level + 1) % 4 == 0:
            print(f"Strength: {self.stats.strength}")
            print(f"Intelligence: {self.stats.intel}")
            print(f"Wisdom: {self.stats.wisdom}")
            print(f"Constitution: {self.stats.con}")
            print(f"Charisma: {self.stats.charisma}")
            print(f"Dexterity: {self.stats.dex}")
            time.sleep(0.5)
            print("Pick the stat you would like to increase.")
            stat_option = ['Strength', 'Intelligence', 'Wisdom', 'Constitution', 'Charisma', 'Dexterity']
            stat_index = storyline.get_response(stat_option)
            if stat_option[stat_index] == 'Strength':
                self.stats.strength += 1
                print(f"You are now at {self.stats.strength} strength.")
            if stat_option[stat_index] == 'Intelligence':
                self.stats.intel += 1
                print(f"You are now at {self.stats.intel} intelligence.")
            if stat_option[stat_index] == 'Wisdom':
                self.stats.wisdom += 1
                print(f"You are now at {self.stats.wisdom} wisdom.")
            if stat_option[stat_index] == 'Constitution':
                self.stats.con += 1
                print(f"You are now at {self.stats.con} constitution.")
            if stat_option[stat_index] == 'Charisma':
                self.stats.charisma += 1
                print(f"You are now at {self.stats.charisma} charisma.")
            if stat_option[stat_index] == 'Dexterity':
                self.stats.dex += 1
                print(f"You are now at {self.stats.dex} dexterity.")
        health_gain = random.randint(self.stats.con // 3, self.stats.con) * max(1, self.check_mod('luck', luck_factor=12))
        self.health.max += health_gain
        mana_gain = int((self.stats.intel // 2 + self.stats.wisdom // 3))
        mana_gain = random.randint(mana_gain // 3, mana_gain) * max(1, self.check_mod('luck', luck_factor=12))
        self.mana.max += mana_gain
        self.level.level += 1
        print(f"You are now level {self.level.level}.")
        print(f"You have gained {health_gain} health points and {mana_gain} mana points.")
        if str(self.level.level) in abilities.spell_dict[self.cls.name]:
            time.sleep(0.5)
            spell_gain = abilities.spell_dict[self.cls.name][str(self.level.level)]
            if spell_gain().name in self.spellbook['Spells']:
                print(f"{spell_gain().name} goes up a level.")
            else:
                print(f"You have gained the ability to cast {spell_gain().name}.")
            self.spellbook['Spells'][spell_gain().name] = spell_gain
            time.sleep(0.5)
        if str(self.level.level) in abilities.skill_dict[self.cls.name]:
            time.sleep(0.5)
            skill_gain = abilities.skill_dict[self.cls.name][str(self.level.level)]
            if skill_gain().name in self.spellbook['Skills']:
                print(f"{skill_gain().name} goes up a level.")
            else:
                print(f"You have gained the ability to use {skill_gain().name}.")
            self.spellbook['Skills'][skill_gain().name] = skill_gain
            if skill_gain().name == 'Health/Mana Drain':
                del self.spellbook['Skills']['Health Drain']
                del self.spellbook['Skills']['Mana Drain']
            time.sleep(0.5)
            if skill_gain().name == 'Familiar':
                self.familiar.level_up()
            if skill_gain().name == "Transform":
                skill_gain().use(self)
        if not self.max_level():
            self.level.exp -= self.level.exp_to_gain
            self.level.exp_to_gain = (exp_scale ** self.level.pro_level) * self.level.level
        else:
            self.level.exp = "Max"
            self.level.exp_to_gain = "Max"
        time.sleep(0.5)

    def open_up(self):
        tile = self.world_dict[(self.location_x, self.location_y, self.location_z)]
        if 'Chest' in str(tile):
            locked = int('Locked' in str(tile))
            plus = int('ChestRoom2' in str(tile))
            enemy = enemies.Mimic(self.location_z + locked + plus)
            if not random.randint(0, 4 + self.check_mod('luck', luck_factor=10)) and self.level.level >= 10:
                print("There is a Mimic in the chest!")
                time.sleep(1)
                self.state = 'fight'
                win = combat.battle(self, enemy)
            else:
                win = True
            if win:
                tile.open = True
                print(f"{self.name} opens the chest, containing a {tile.loot().name}.")
                self.modify_inventory(tile.loot, 1)
                input("Press enter to continue")
        elif 'Door' in str(tile):
            tile.open = True
            print(f"{self.name} opens the door.")
            input("Press enter to continue")
        else:
            raise AssertionError("Something is not working. Check code.")

    def loot(self, enemy, tile):
        rare = False
        print(f"{enemy.name} dropped {enemy.gold} gold.")
        self.gold += enemy.gold
        for item in enemy.inventory.values():
            drop = False
            chance = self.check_mod('luck', luck_factor=16) + self.level.pro_level
            if item[0]().rarity > (random.random() / chance) and 'Boss' not in str(tile):
                if item[0]().subtyp == 'Enemy':
                    for info in self.quest_dict['Side'].values():
                        if info['What'] == item[0] and not info['Completed']:
                            rare = True
                            drop = True
                            break
                else:
                    drop = True
            elif 'Boss' in str(tile):
                drop = True
            else:
                pass
            if drop:
                print(f"{enemy.name} dropped a {item[0]().name}.")
                while not self.add_weight(item):
                    print(f"You cannot carry anymore. Would you like to drop items to make room?")
                    response = storyline.get_response(["Yes", "No"])
                    if response:
                        print(f"You have chosen to leave the {item[0]().name} behind.")
                        return
                    self.character_menu()
                self.modify_inventory(item[0], num=item[1], rare=rare)
                self.quests(item=item[0])

    def print_inventory(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(str(self))
            print(f"  Gold: {self.gold} | Weight/Max: {self.current_weight()}/{self.max_weight()}")
            inv_list = []
            if len(self.inventory) > 0:
                for key in self.inventory:
                    inv_list.append(key + ": " + str(self.inventory[key][1]))
            if len(self.special_inventory) > 0:
                inv_list.append("Special Inventory")
            inv_list.append("Go Back")
            inv_input = storyline.get_response(inv_list)
            if inv_list[inv_input] == "Go Back":
                break
            if inv_list[inv_input] == "Special Inventory":
                sp_list = []
                for key in self.special_inventory:
                    sp_list.append(key)
                sp_list.append("Go Back")
                sp_input = storyline.get_response(sp_list)
                if sp_list[sp_input] == "Go Back":
                    continue
                sp_inspect = sp_list[sp_input]
                print(str(self.special_inventory[sp_inspect][0]()))
            else:
                inv_choice = inv_list[inv_input].split(": ")[0]
                print(str(self.inventory[inv_choice][0]()))
            input("Press enter to continue")

    def specials(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        if len(self.spellbook['Spells']) == 0 and len(self.spellbook['Skills']) == 0:
            print("You do not have any abilities.")
            time.sleep(0.5)
            return
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(str(self))
            specs = ['Go Back']
            for typ in self.spellbook:
                if len(self.spellbook[typ]) > 0:
                    specs.insert(0, typ)
            if len(specs) == 1:
                print("You do not have any specials.")
                time.sleep(1)
                return
            spec_input = storyline.get_response(specs)
            if specs[spec_input] == 'Go Back':
                time.sleep(0.5)
                return
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                cast_list = []
                print(str(self))
                inspect_list = []
                for name, special in self.spellbook[specs[spec_input]].items():
                    inspect_list.append(name)
                    if special().subtyp == 'Heal' and self.mana.current >= special().cost:
                        if not special().combat:
                            cast_list.append(name)
                    elif special().subtyp == 'Movement' and self.mana.current >= special().cost:
                        cast_list.append(name)
                inspect_list.append("Go Back")
                inspect_input = storyline.get_response(inspect_list)
                if inspect_list[inspect_input] == 'Go Back':
                    break
                choose_list = ["Inspect"]
                if inspect_list[inspect_input] in cast_list:
                    choose_list.append("Cast")
                choose_input = storyline.get_response(choose_list)
                if choose_list[choose_input] == "Inspect":  # TODO fix inspect of specials
                    print(str(self.spellbook[specs[spec_input]][inspect_list[inspect_input]]))
                    if inspect_list[inspect_input] == "Familiar":
                        fam_inspect = ["Inspect Familiar", "Go Back"]
                        fam_input = storyline.get_response(fam_inspect)
                        if fam_inspect[fam_input] == "Go Back":
                            break
                        while True:
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(f"{self.familiar.name}'s Specials")
                            spec_input = storyline.get_response(specs)
                            if specs[spec_input] == "Go Back":
                                break
                            while True:
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print(f"{self.familiar.name}'s Specials")
                                if len(self.familiar.spellbook[specs[spec_input]]) == 0:
                                    print(f"{self.familiar.name} does not have any {specs[spec_input].lower()}.")
                                    time.sleep(1)
                                    break
                                fam_specials = []
                                for name in self.familiar.spellbook[specs[spec_input]]:
                                    fam_specials.append(name)
                                fam_specials.append("Go Back")
                                fam_special = storyline.get_response(fam_specials)
                                if fam_specials[fam_special] == "Go Back":
                                    break
                                print(self.familiar.spellbook[
                                          specs[spec_input]][fam_specials[fam_special]]())
                            input("Press enter to continue")
                        break
                    if choose_list[choose_input] == "Cast":
                        self.spellbook[specs[spec_input]][inspect_list[inspect_input]]().cast_out(self)
                        input("Press enter to continue")
                        if self.spellbook[specs[spec_input]][inspect_list[inspect_input]]().subtyp == 'Movement':
                            return
                        break
            input("Press enter to continue")
            time.sleep(0.5)

    def save(self, tmp=False):
        if tmp:
            tmp_dir = "tmp_files"
            save_file = tmp_dir + f"/{str(self.name)}.tmp"
            with open(save_file, "wb") as save_game:
                pickle.dump(self.__dict__, save_game)
        else:
            while True:
                save_file = f"save_files/{str(self.name).lower()}.save"
                if os.path.exists(save_file):
                    print("A save file under this name already exists. Are you sure you want to overwrite it? (Y or N)")
                    over = storyline.get_response(["Yes", "No"])
                    if over:
                        break
                with open(save_file, "wb") as save_game:
                    pickle.dump(self.__dict__, save_game)
                print("Your game is now saved.")
                time.sleep(1)
                break

    def equip(self, unequip=None, promo=False):
        if unequip is None:
            equip = True
            print("Which piece of equipment would you like to replace? ")
            option_list = ['Weapon', 'Armor', 'OffHand', 'Pendant', 'Ring', 'Go Back']
            slot = storyline.get_response(option_list)
            equip_slot = option_list[slot]
            item_type = option_list[slot]
            if equip_slot == 'Go Back':
                equip = False
            elif equip_slot in ['Ring', 'Pendant']:
                item_type = 'Accessory'
            inv_list = []
            while equip:
                if self.equipment["Weapon"]().handed == 2 and equip_slot == "OffHand" and \
                        (self.cls.name not in ["Lancer", "Crusader", "Berserker"]):
                    print("You are currently equipped with a 2-handed weapon. Equipping an off-hand will remove the "
                          "2-hander.")
                    print("Do you wish to continue?")
                    cont = storyline.get_response(["Yes", "No"])
                    if cont:
                        break
                print(f"You are currently equipped with {self.equipment[equip_slot]().name}.")
                old = self.equipment[equip_slot]
                if item_type == 'Accessory':
                    if old().mod in self.resistance or old().mod == 'Elemental':
                        print(f"You current {equip_slot} gives {old().mod} resistance.")
                    else:
                        print(f"You current {equip_slot} gives {old().mod}.")
                shield = False
                for item in self.inventory:
                    if item_type == equip_slot:
                        if (str(self.inventory[item][0]().typ) == item_type or
                                (equip_slot == 'OffHand' and str(self.inventory[item][0]().typ) == 'Weapon'
                                 and classes.equip_check(self.inventory[item], item_type, self.cls))):
                            diff = ''
                            if classes.equip_check(self.inventory[item], item_type, self.cls):
                                if equip_slot == 'Weapon':
                                    diff = self.inventory[item][0]().damage - self.equipment['Weapon']().damage
                                elif equip_slot == 'Armor':
                                    diff = self.inventory[item][0]().armor - self.equipment['Armor']().armor
                                elif equip_slot == 'OffHand':
                                    if self.inventory[item][0]().subtyp == 'Shield':
                                        if self.equipment['OffHand']().subtyp == 'Shield':
                                            diff = int((self.inventory[item][0]().mod -
                                                        self.equipment['OffHand']().mod) * 100)
                                        else:
                                            diff = int(self.inventory[item][0]().mod * 100)
                                        shield = True
                                    elif self.inventory[item][0]().subtyp == 'Tome':
                                        if self.equipment['OffHand']().subtyp == 'Tome':
                                            diff = self.inventory[item][0]().mod - self.equipment['OffHand']().mod
                                        else:
                                            diff = self.inventory[item][0]().mod
                                    else:
                                        if self.equipment['OffHand']().typ == 'Weapon':
                                            diff = self.inventory[item][0]().damage - self.equipment['OffHand']().damage
                                        else:
                                            diff = self.inventory[item][0]().damage
                                if shield:
                                    inv_list.append(item + '   ' + str(diff) + '%')
                                if diff == '':
                                    inv_list.append(item)
                                elif diff < 0:
                                    inv_list.append(item + '  ' + str(diff))
                                else:
                                    inv_list.append(item + '  +' + str(diff))
                    else:
                        if str(self.inventory[item][0]().subtyp) == equip_slot:
                            inv_list.append(item + '  ' + self.inventory[item][0]().mod)

                if not self.equipment[equip_slot]().unequip:
                    inv_list.append('Unequip')
                inv_list.append('Keep Current')
                print(f"Which {equip_slot.lower()} would you like to equip? ")
                replace = storyline.get_response(inv_list)
                if inv_list[replace] == 'Unequip':
                    self.equipment[equip_slot] = items.remove(equip_slot)
                    self.modify_inventory(old, 1)
                    print(f"Your {equip_slot.lower()} slot is now empty.")
                elif inv_list[replace] == 'Keep Current':
                    print("No equipment was changed.")
                elif old().name == self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]][0]().name:
                    print(f"You are already equipped with a {old().name}.")
                else:
                    if classes.equip_check(self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]],
                                           item_type, self.cls):
                        self.equipment[equip_slot] = \
                            self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]][0]
                        if self.cls.name not in ['Lancer', 'Dragoon', 'Berserker']:
                            if option_list[slot] == 'Weapon':
                                if self.equipment['Weapon']().handed == 2:
                                    if self.equipment['OffHand'] != items.NoOffHand:
                                        self.modify_inventory(self.equipment['OffHand'], 1)
                                        self.equipment['OffHand'] = items.remove('OffHand')
                            elif self.equipment['Weapon']().handed == 2 and equip_slot == 'OffHand':
                                old = self.equipment['Weapon']
                                self.equipment['Weapon'] = items.remove('Weapon')
                        self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]][1] -= 1
                        if self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]][1] <= 0:
                            del self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]]
                        if not old().unequip:
                            self.modify_inventory(old, 1)
                        print(f"You are now equipped with {self.equipment[equip_slot]().name}.")
                    if equip_slot == "Pendant":
                        self.flying = "Flying" in self.equipment[equip_slot]().mod
                        self.invisible = "Invisible" in self.equipment[equip_slot]().mod
                time.sleep(0.5)
                break
        elif unequip:
            for item in self.equipment:
                if promo:
                    if item in ['Weapon', 'Armor', 'OffHand']:
                        self.modify_inventory(self.equipment[item], 1)
                else:
                    if item in ['Weapon', 'Armor', 'OffHand', 'Ring', 'Pendant']:
                        self.modify_inventory(self.equipment[item], 1)

    def move(self, dx, dy):
        new_x = self.location_x + dx
        new_y = self.location_y + dy
        if self.world_dict[(new_x, new_y, self.location_z)].enter:
            self.location_x += dx
            self.location_y += dy

    def stairs(self, dz):
        self.location_z += dz

    def move_north(self):
        self.move(dx=0, dy=-1)

    def move_south(self):
        self.move(dx=0, dy=1)

    def move_east(self):
        self.move(dx=1, dy=0)

    def move_west(self):
        self.move(dx=-1, dy=0)

    def stairs_up(self):
        self.stairs(dz=-1)

    def stairs_down(self):
        self.stairs(dz=1)

    def change_location(self, x, y, z):
        self.location_x = x
        self.location_y = y
        self.location_z = z

    def death(self):
        """
        Controls what happens when you die; no negative affect will occur for players under level 10
        """
        time.sleep(2)
        stat_list = ['strength', 'intelligence', 'wisdom', 'constitution', 'charisma', 'dexterity']
        if self.level.level > 9 or self.level.pro_level > 1:
            cost = self.level.level * self.level.pro_level * 100 * self.location_z
            cost = random.randint(cost // 2, cost)
            cost = min(cost, self.gold)
            print(f"Resurrection costs you {cost} gold.")
            self.gold -= cost
            if not random.randint(0, self.stats.charisma):
                print("Complications occurred during your resurrection.")
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
                print(f"You have lost 1 {stat_name}.")
        self.state = 'normal'
        self.statuses(end=True)
        self.location_x, self.location_y, self.location_z = (5, 10, 0)
        print("You wake up in town.")
        time.sleep(2)
        town.town(self)

    def class_upgrades(self, enemy):
        """

        """
        if self.cls.name == "Soulcatcher":
            chance = max(1, 19 - self.check_mod('luck', luck_factor=20))
            if not random.randint(0, chance):  # 5% chance on kill
                print(f"You absorb part of the {enemy.name}'s soul.")
                time.sleep(1)
                if enemy.enemy_typ == 'Reptile':
                    print("Gain 1 strength.")
                    self.stats.strength += 1
                if enemy.enemy_typ == 'Aberration':
                    print("Gain 1 intelligence.")
                    self.stats.intel += 1
                if enemy.enemy_typ == 'Slime':
                    print("Gain 1 wisdom.")
                    self.stats.wisdom += 1
                if enemy.enemy_typ == 'Construct':
                    print("Gain 1 constitution.")
                    self.stats.con += 1
                if enemy.enemy_typ == 'Humanoid':
                    print("Gain 1 charisma.")
                    self.stats.charisma += 1
                if enemy.enemy_typ == 'Insect':
                    print("Gain 1 dexterity.")
                    self.stats.dex += 1
                if enemy.enemy_typ == 'Animal':
                    print("Gain 5 hit points.")
                    self.health.max += 5
                if enemy.enemy_typ == 'Monster':
                    print("Gain 5 mana points.")
                    self.mana.max += 5
                if enemy.enemy_typ == 'Undead':
                    print("Gain enough experience to level.")
                    self.level.exp = self.level.exp_to_gain
                    if self.max_level():
                        self.level_up()
                if enemy.enemy_typ == 'Dragon':
                    print("Your gold has been doubled.")
                    self.gold *= 2
                time.sleep(1)
        if self.cls.name == "Lycan" and enemy.name == 'Red Dragon':
            print(f"{self.name} has harnessed the power of the Red Dragon and can now transform into one!")
            time.sleep(1)
            self.spellbook['Skills']['Transform'] = abilities.Transform4
            self.spellbook['Skills']['Transform']().use(self)

    def familiar_turn(self, enemy):
        if self.familiar:
            special = None
            target = enemy
            if not random.randint(0, 1):
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
                        if special().name not in ['Resurrection', 'Cover']:
                            break
                if self.familiar.spec == "Support":  # just spells
                    target = self
                    if not random.randint(0, 4) and self.mana.current < self.mana.max:
                        mana_regen = int(self.mana.max * 0.05)
                        mana_regen = min(mana_regen, self.mana.max - self.mana)
                        self.mana.current += mana_regen
                        print(f"{self.familiar.name} restores {self.name}'s mana by {mana_regen}.")
                    else:
                        if self.health.current < self.health.max and random.randint(0, 1):
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']['Regen']
                        elif not self.status_effects['Attack'].active:
                            special = self.familiar.spellbook['Spells']['Bless']
                        elif self.familiar.level.level > 1 and not self.status_effects['Reflect'].active:
                            special = self.familiar.spellbook['Spells']['Reflect']
                        elif self.familiar.level.level == 3 and random.randint(0, 1):
                            special = self.familiar.spellbook['Spells']['Cleanse']
                        else:
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']['Regen']
                if self.familiar.spec == "Arcane":  # just spells
                    spell_list = list(self.familiar.spellbook['Spells'])
                    choice = random.choice(spell_list)
                    if choice == "Boost" and not random.randint(0, 1) and not self.status_effects['Magic'].active:
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
                    if special().typ == 'Skill':
                        special().use(self, target=target, fam=True)
                    elif special().typ == 'Spell':
                        special().cast(self, target=target, fam=True)

    def transform(self, back=False):
        if back:
            print(f"{self.name} transforms back into their normal self.")
            time.sleep(1)
            health_diff = self.health.max - self.health.current
            mana_diff = self.mana.max - self.mana.current
            player_char_dict = load_char(char=self, tmp=True)
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
        else:
            self.save(tmp=True)
            print(f"{self.name} transforms into a {self.transform.name}.")
            self.cls = None
            self.health.current = max(self.health.current + self.transform.health.max, self.health.max)
            self.health.max += self.transform.health.max
            self.mana.current = max(self.mana.current + self.transform.mana.max, self.mana.max)
            self.mana.max += self.transform.mana.max
            self.stats.strength += self.transform.stats.strength
            self.stats.intel += self.transform.stats.intel
            self.stats.wisdom += self.transform.stats.wisdom
            self.stats.con += self.transform.stats.con
            self.stats.charisma += self.transform.stats.charisma
            self.stats.dex += self.transform.stats.dex
            self.equipment['Weapon'] = self.transform.equipment['Weapon']
            self.equipment['Armor'] = self.transform.equipment['Armor']
            self.equipment['OffHand'] = self.transform.equipment['OffHand']
            self.spellbook = self.transform.spellbook
            self.resistance = self.transform.resistance
            time.sleep(1)

    def end_combat(self, enemy, tile, flee=False):
        time.sleep(0.5)
        self.state = 'normal'
        if not self.cls:
            self.transform(back=True)
        self.statuses(end=True)
        if all([self.is_alive(), not flee]):
            print(f"{self.name} killed {enemy.name}.")
            print(f"{self.name} gained {enemy.experience} experience.")
            if enemy.name not in self.kill_dict:
                self.kill_dict[enemy.name] = 0
            self.kill_dict[enemy.name] += 1
            self.loot(enemy, tile)
            if self.level.exp != 'Max':
                self.level.exp += enemy.experience
            self.class_upgrades(enemy)
            while self.level.exp >= self.level.exp_to_gain and not self.max_level():
                self.level_up()
            self.quests(enemy=enemy)
        elif flee:
            pass
        else:
            print(f"{self.name} was slain by {enemy.name}.")
            enemy.statuses(end=True)
            enemy.health.current = enemy.health.max
            enemy.mana.current = enemy.mana.max
            self.death()

    def quests(self, enemy=None, item=None):
        if enemy is not None:
            if enemy.name in self.quest_dict['Bounty']:
                if not self.quest_dict['Bounty'][enemy.name][2]:
                    self.quest_dict['Bounty'][enemy.name][1] += 1
                    if self.quest_dict['Bounty'][enemy.name][1] == self.quest_dict['Bounty'][enemy.name][0]:
                        self.quest_dict['Bounty'][enemy.name][2] = True
                        print("You have completed a bounty.")
            else:
                for quest in self.quest_dict['Main']:
                    if self.quest_dict['Main'][quest]['What'] == enemy.name:
                        self.quest_dict['Main'][quest]['Completed'] = True
                        print(f"You have completed the quest {quest}.")
        elif item is not None:
            for quest in self.quest_dict['Side']:
                if self.quest_dict['Side'][quest]['What'] == item:
                    if item().name in self.special_inventory:
                        if self.special_inventory[item().name][1] >= self.quest_dict['Side'][quest]['Total'] and \
                                not self.quest_dict['Side'][quest]['Completed'] and \
                                not self.quest_dict['Side'][quest]['Turned In']:
                            self.quest_dict['Side'][quest]['Completed'] = True
                            print(f"You have completed the quest {quest}.")
        else:
            if self.has_relics():
                if 'The Holy Relics' in self.quest_dict['Main']:
                    print("You have completed the quest The Holy Relics.")
                    self.quest_dict['The Holy Relics']['Completed'] = True

    def view_quests(self):
        """
        Bounty Quests:
        """

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("#" + (30 * "-") + "#")
            print("  Bounties: Remaining/Total")
            for quest, info in self.quest_dict["Bounty"].items():
                if info[2]:
                    print(f"  {quest}: Completed")
                else:
                    print(f"  {quest}: {info[1]}/{info[0]}")
            print("#" + (30 * "-") + "#")
            print("  Quests")
            inspect_list = []
            completed_list = []
            for typ in ["Main", "Side"]:
                for quest in self.quest_dict[typ]:
                    if not self.quest_dict[typ][quest]['Turned In']:
                        inspect_list.append(quest)
                    else:
                        completed_list.append(quest)
            if len(completed_list) > 0:
                inspect_list.append("Completed Quests")
            inspect_list.append("Go Back")
            inspect_input = storyline.get_response(inspect_list)
            quest = inspect_list[inspect_input]
            if quest == "Go Back":
                break
            if quest == "Completed Quests":
                for i in completed_list:
                    print("  " + i)
            else:
                if quest in self.quest_dict['Main']:
                    info = self.quest_dict['Main'][quest]
                elif quest in self.quest_dict['Side']:
                    info = self.quest_dict['Side'][quest]
                else:
                    raise AssertionError("You shouldn't reach here.")
                if info['Type'] == 'Collect':
                    item_name = info['What']().name
                    if item_name in self.special_inventory:
                        if self.special_inventory[item_name][1] < info['Total']:
                            print(f"  Collect {info['Total']} {item_name}s: "
                                  f"{self.special_inventory[item_name][1]}/{info['Total']}")
                        else:
                            print(f"  Collect {info['Total']} {item_name}s: Completed")
                    else:
                        print(f"  Collect {info['Total']} {item_name}s: {0}/{info['Total']}")
                elif info['Type'] == 'Defeat':
                    if info['What'] in self.kill_dict:
                        print(f"  {info['Type']} {info['What']}: Completed")
                    else:
                        print(f"  {info['Type']} {info['What']}")
                else:
                    if info['Completed']:
                        print(f"  {info['Type']} {info['What']}: Completed")
                    else:
                        print(f"  {info['Type']} {info['What']}")
                print(f"  Quest Giver: {info['Who']}")
            input("Press enter to continue")

    def check_mod(self, mod, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = self.equipment['Weapon']().damage + self.stats.strength
            if 'Monk' in self.cls.name:
                class_mod += (self.stats.wisdom // 2)
            if self.cls.name in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level.level + ((self.level.pro_level - 1) * 20)) * (self.mana.current / self.mana.max)
            if self.cls.name in ['Thief', 'Rogue', 'Assassin', 'Ninja', 'Druid', 'Lycan']:
                class_mod += (self.stats.dex // 2)
            if 'Physical Damage' in self.equipment['Ring']().mod:
                weapon_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            weapon_mod += self.status_effects['Attack'].extra * self.status_effects['Attack'].active
            return weapon_mod + class_mod
        if mod == 'offhand':
            if 'Monk' in self.cls.name:
                class_mod += self.stats.wisdom
            if self.cls.name in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level.level + ((self.level.pro_level - 1) * 20)) * (self.mana.current / self.mana.max)
            if self.cls.name in ['Thief', 'Rogue', 'Assassin', 'Ninja', 'Druid', 'Lycan']:
                class_mod += (self.stats.dex // 2)
            try:
                off_mod = self.equipment['OffHand']().damage + self.stats.strength
                if 'Physical Damage' in self.equipment['Ring']().mod:
                    off_mod += int(self.equipment['Ring']().mod.split(' ')[0])
                off_mod += self.status_effects['Attack'].extra * self.status_effects['Attack'].active
                return int((off_mod + class_mod) * 0.75)
            except AttributeError:
                return 0
        if mod == 'armor':
            armor_mod = self.equipment['Armor']().armor
            if self.cls.name == 'Knight Enchanter':
                class_mod += self.stats.intel * (self.mana.current / self.mana.max)
            if self.cls.name in ['Warlock', 'Shadowcaster']:
                if self.familiar.typ == 'Homunculus' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
                    fam_mod = random.randint(0, 3) ** self.familiar.level.pro_level
                    print(f"{self.familiar.name} improves {self.name}'s armor by {fam_mod}.")
                    class_mod += fam_mod
            if 'Physical Defense' in self.equipment['Ring']().mod:
                armor_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            armor_mod += self.status_effects['Defense'].extra * self.status_effects['Defense'].active
            return armor_mod * int(not ignore) + class_mod
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 2) * self.level.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                magic_mod += (self.equipment['OffHand']().mod + (self.equipment['Weapon']().damage // 2))
            if self.equipment['Weapon']().subtyp == 'Staff' or \
                    (self.cls.name in ['Spellblade', 'Knight Enchanter'] and
                     self.equipment['Weapon']().subtyp == 'Longsword'):
                magic_mod += int(self.equipment['Weapon']().damage * 1.5)
            if 'Magic Damage' in self.equipment['Pendant']().mod:
                magic_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            magic_mod += self.status_effects['Magic'].extra * self.status_effects['Magic'].active
            return magic_mod + class_mod
        if mod == 'magic def':
            m_def_mod = self.stats.wisdom
            if 'Magic Defense' in self.equipment['Pendant']().mod:
                m_def_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            m_def_mod += self.status_effects['Magic Defense'].extra * self.status_effects['Magic Defense'].active
            return m_def_mod + class_mod
        if mod == 'heal':
            heal_mod = self.stats.wisdom * self.level.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                heal_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                heal_mod += int(self.equipment['Weapon']().damage * 1.5)
            heal_mod += self.status_effects['Magic'].extra * self.status_effects['Magic'].active
            return heal_mod + class_mod
        if mod == 'resist':
            res_mod = self.resistance[typ]
            if self.flying:
                if typ == 'Earth':
                    res_mod = 1
                elif typ == 'Wind':
                    res_mod = -0.25
            if self.cls.name in ['Warlock', 'Shadowcaster']:
                if self.familiar.typ == 'Mephit' and random.randint(0, 1) and self.familiar.level.pro_level > 1:
                    fam_mod = 0.25 * random.randint(1, max(1, self.stats.charisma // 10))
                    print(f"{self.familiar.name} increases {self.name}'s resistance to {typ} by {int(fam_mod * 100)}%.")
                    res_mod += fam_mod
            if self.equipment['Pendant']().mod == typ:
                res_mod = 1
            elif self.equipment['Pendant']().mod == "Elemental" and \
                    typ in ['Fire', 'Ice', 'Electric', 'Water', 'Earth', 'Wind']:
                res_mod += 0.25
            return res_mod
        if mod == 'luck':
            luck_mod = self.stats.charisma // luck_factor
            return luck_mod
        return 0


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
        'method': Player.print_inventory,
        'name': 'Inventory',
        'hotkey': None
    },
    'ViewQuests': {
        'method': Player.view_quests,
        'name': 'Quests',
        'hotkey': None
    },
    'Flee': {
        'method': Player.flee,
        'name': 'Flee',
        'hotkey': None
    },
    'Status': {
        'method': Player.status,
        'name': 'Status',
        'hotkey': None
    },
    'Equip': {
        'method': Player.equip,
        'name': 'Equip',
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
