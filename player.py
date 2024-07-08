###########################################
""" Character creator and manager """

# Imports
import os
import re
import glob
import random
import time
import numpy
import pickle

import combat
import enemies
from character import Character
from classes import classes_dict
import items
import storyline
import actions
import spells
import races
import classes
import town


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
            print("You have chosen to name your character {}. Is this correct? ".format(name))
            keep = storyline.get_response(['Yes', 'No'])
            if keep == 1:
                name = ''
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        race = races.define_race()
        cls = classes.define_class(race)
        if cls:
            break
        time.sleep(0.5)
    created = "Welcome {}, the {} {}.\n" \
              "Report to the barracks for your orders.".format(name, race.name, cls.name)
    storyline.slow_type(created)
    time.sleep(1)
    stats = tuple(map(lambda x, y: x + y, race.stats, cls.stat_plus))
    hp = stats[3] * 2  # starting HP equal to constitution x 2
    mp = stats[1] + int(stats[2] * 0.5)  # starting MP equal to intel and wis x 0.5
    gil = stats[4] * 25  # starting gold equal to charisma x 25
    player_char = Player(location_x, location_y, location_z, state='normal', level=1, exp=0,
                         exp_to_gain=exp_scale, health=hp, health_max=hp, mana=mp, mana_max=mp,
                         strength=stats[0], intel=stats[1], wisdom=stats[2], con=stats[3], charisma=stats[4],
                         dex=stats[5], pro_level=1, gold=gil, resistance=race.resistance)
    player_char.name = name
    player_char.race = race.name
    player_char.cls = cls.name
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
            return dict()
        else:
            chars = []
            for f in save_files:
                chars.append(f.split('.')[0].capitalize())
            chars.append('Go Back')
            print("Select the name of the character you want to load.")
            choice = storyline.get_response(chars)
            if chars[choice] == 'Go Back':
                return dict()
            save_file = chars[choice] + ".save"
            with open(save_file, 'rb') as save_file:
                player_dict = pickle.load(save_file)
            return player_dict
    else:
        if os.path.exists(char + ".save"):
            with open(char + ".save", "rb") as save_file:
                player_dict = pickle.load(save_file)
            return player_dict
        else:
            return dict()


def load_char(char=None, tmp=False):
    """
    Initializes the character based on the load file
    """
    if tmp:
        load_file = "tmp_files/" + str(char.name).lower() + ".tmp"
        with open(load_file, "rb") as l_file:
            l_dict = pickle.load(l_file)
        os.system("rm {}".format(load_file))
        return l_dict
    else:
        if char is None:
            player_dict = load()
        else:
            player_dict = load(char)
        if player_dict == dict():
            return player_dict
        player_char = Player(player_dict['location_x'], player_dict['location_y'], player_dict['location_z'],
                             player_dict['state'], player_dict['level'], player_dict['experience'],
                             player_dict['exp_to_gain'], player_dict['health'], player_dict['health_max'],
                             player_dict['mana'], player_dict['mana_max'], player_dict['strength'],
                             player_dict['intel'], player_dict['wisdom'], player_dict['con'], player_dict['charisma'],
                             player_dict['dex'], player_dict['pro_level'], player_dict['gold'],
                             player_dict['resistance'])
        player_char.name = player_dict['name']
        player_char.race = player_dict['race']
        player_char.cls = player_dict['cls']
        player_char.status_effects = player_dict['status_effects']
        player_char.equipment = player_dict['equipment']
        player_char.inventory = player_dict['inventory']
        player_char.special_inventory = player_dict['special_inventory']
        player_char.spellbook = player_dict['spellbook']
        player_char.familiar = player_dict['familiar']
        player_char.transform_list = player_dict['transform_list']
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

    def __init__(self, location_x, location_y, location_z, state, level, exp, exp_to_gain, health, health_max, mana,
                 mana_max, strength, intel, wisdom, con, charisma, dex, pro_level, gold, resistance):
        super().__init__()
        self.location_x = location_x
        self.location_y = location_y
        self.location_z = location_z
        self.state = state
        self.level = level
        self.experience = exp
        self.exp_to_gain = exp_to_gain
        self.health = health
        self.health_max = health_max
        self.mana = mana
        self.mana_max = mana_max
        self.strength = strength
        self.intel = intel
        self.wisdom = wisdom
        self.con = con
        self.charisma = charisma
        self.dex = dex
        self.pro_level = pro_level
        self.gold = gold
        self.resistance = resistance
        self.equipment = {'Weapon': items.NoWeapon,
                          'Armor': items.NoArmor,
                          'OffHand': items.NoOffHand,
                          'Ring': items.NoRing,
                          'Pendant': items.NoPendant}
        self.world_dict = dict()
        self.teleport = None
        self.quest_dict = dict(Bounty=dict(),
                               Main=dict(),
                               Side=dict())
        self.kill_dict = dict()
        self.storage = dict()
        self.warp_point = False
        self.quit = False

    def __str__(self):
        return "Player: {} | Health: {}/{} | Mana: {}/{}".format(self.name, self.health, self.health_max,
                                                                 self.mana, self.mana_max)

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
                    elif 'Stairs' in self.world_dict[tile].__str__():
                        map_array[tile_x][tile_y] = "\u25E3"
                    elif 'DoorEast' in self.world_dict[tile].__str__() or \
                            'DoorWest' in self.world_dict[tile].__str__():
                        if not self.world_dict[tile].open:
                            map_array[tile_x][tile_y] = "|"
                        else:
                            map_array[tile_x][tile_y] = "."
                    elif 'DoorNorth' in self.world_dict[tile].__str__() or \
                            'DoorSouth' in self.world_dict[tile].__str__():
                        if not self.world_dict[tile].open:
                            map_array[tile_x][tile_y] = "_"
                        else:
                            map_array[tile_x][tile_y] = "."
                    elif 'Wall' in self.world_dict[tile].__str__():
                        map_array[tile_x][tile_y] = "#"
                    elif 'Chest' in self.world_dict[tile].__str__():
                        if self.world_dict[tile].open:
                            map_array[tile_x][tile_y] = "\u25A1"
                        else:
                            map_array[tile_x][tile_y] = "\u25A0"
                    elif 'Relic' in self.world_dict[tile].__str__():
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
        for i, l in enumerate(map_array):
            print(" ".join(l))

    def load_tiles(self):
        """Parses a file that describes the world space into the _world object"""
        world_dict = {(5, 10, 0): getattr(__import__('map'), 'Town')(5, 10, 0)}
        map_files = glob.glob('map_files/map_level_*')
        for map_file in map_files:
            z = map_file.split('_')[-1]
            z = int(z.split('.')[0])
            with open(map_file, 'r') as f:
                rows = f.readlines()
            x_max = len(rows[0].split('\t'))  # Assumes all rows contain the same number of tabs
            for y in range(len(rows)):
                cols = rows[y].split('\t')
                for x in range(x_max):
                    tile_name = cols[x].replace('\n', '')  # Windows users may need to replace '\r\n'
                    tile = getattr(__import__('map'), tile_name)(x, y, z)
                    world_dict[(x, y, z)] = tile
        self.world_dict = world_dict

    def options(self, action_list=None):
        """
        Controls the listed options during combat
        """
        print("Choose an action:")
        if action_list is not None:
            option_list = []
            for action in action_list:
                option_list.append(action.name)
            if self.status_effects['Mana Shield'][0]:
                option_list.append("Remove Shield")
            if self.cls not in list(classes_dict.keys()):
                option_list.append("Untransform")
            action_input = storyline.get_response(option_list)
            return option_list[action_input]

    def combat_turn(self, enemy, action, in_combat, tile=None):
        valid_entry = False
        flee = False
        if action == 'Remove Shield':
            print("The mana shield dissolves around {}.".format(self.name))
            self.status_effects['Mana Shield'][0] = False
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
                _, _ = self.weapon_damage(enemy)
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
                    elif self.spellbook['Spells'][entry]().cost <= self.mana:
                        spell_list.append(str(entry) + '  ' + str(self.spellbook['Spells'][entry]().cost))
                spell_list.append('Go Back')
                spell_index = storyline.get_response(spell_list)
                if spell_list[spell_index] == 'Go Back':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return False, in_combat, flee
                else:
                    spell = self.spellbook['Spells'][spell_list[spell_index].split('  ')[0]]
                    spell().cast(self, enemy)
                    valid_entry = True
            if action == 'Use Skill':
                skill_list = []
                for entry in self.spellbook['Skills']:
                    if self.spellbook['Skills'][entry]().cost <= self.mana:
                        if self.spellbook['Skills'][entry]().passive:
                            continue
                        elif self.spellbook['Skills'][entry]().name == 'Smoke Screen' and 'Boss' in \
                                tile.intro_text(self):
                            continue
                        elif self.spellbook['Skills'][entry]().name == 'Lockpick':
                            continue
                        elif self.spellbook['Skills'][entry]().name == 'Shield Slam' and \
                                self.equipment['OffHand']().subtyp != 'Shield':
                            continue
                        else:
                            skill_list.append(str(entry) + '  ' + str(self.spellbook['Skills'][entry]().cost))
                skill_list.append('Go Back')
                skill_index = storyline.get_response(skill_list)
                if skill_list[skill_index] == 'Go Back':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    return False, in_combat, flee
                else:
                    valid = True
                    skill = self.spellbook['Skills'][skill_list[skill_index].split('  ')[0]]
                    if skill().name == 'Smoke Screen':
                        skill().use(self, enemy)
                        flee = self.flee(enemy, smoke=True)
                    elif skill().name == 'Transform':
                        self.transform()
                        valid = False
                    else:
                        skill().use(self, enemy)
                    valid_entry = valid
        if flee:
            """Moves the player_char randomly to an adjacent tile"""
            time.sleep(1.5)
            available_moves = tile.adjacent_moves(self)
            r = random.choice(available_moves)
            self.do_action(r)
            in_combat = False
        return valid_entry, in_combat, flee

    def has_relics(self):
        relics = ["Triangulus", "Quadrata", "Hexagonum", "Luna", "Polaris", "Infinitas"]
        return all(item in self.special_inventory.keys() for item in relics)

    def max_level(self):
        return any([(self.level == 50 and self.pro_level == 3), (self.level == 30 and self.pro_level < 3)])

    def in_town(self):
        return (self.location_x, self.location_y, self.location_z) == (5, 10, 0)

    def usable_skills(self):
        for name, skill in self.spellbook['Skills'].items():
            if not skill().passive:
                return True
        return False

    def game_quit(self):
        """
        Function that allows for exiting the game
        """
        print("Are you sure you want to quit? Any unsaved data will be lost. ")
        yes_no = ["Yes", "No"]
        q = storyline.get_response(yes_no)
        if yes_no[q] == "Yes":
            print("Goodbye, {}!".format(self.name))
            time.sleep(2)
            self.quit = True
            return True

    def character_menu(self, tile=None):
        """
        Lists character options
        """
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self.__str__())
            option_list = [actions.Status(), actions.ViewInventory(), actions.Equip(),
                           actions.UseItem(), actions.ViewQuests(), actions.Quit()]
            options = ["Status", "Inventory", "Equip", "Use Item", "Quests", "Quit Game", "Leave"]
            action_input = storyline.get_response(options)
            try:
                action = option_list[action_input]
                if options[action_input] == "Use Item":
                    self.use_item(tile=tile)
                else:
                    self.do_action(action, **action.kwargs)
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
        print("#" + (10 * "-") + "#")
        print("Name: {}".format(self.name))
        print("Race: {}".format(self.race))
        print("Class: {}".format(self.cls))
        print("Level: {}  Experience: {}/{}".format(self.level, self.experience, self.exp_to_gain))
        print("HP: {}/{}  MP: {}/{}".format(self.health, self.health_max, self.mana, self.mana_max))
        print("Strength: {}".format(self.strength))
        print("Intelligence: {}".format(self.intel))
        print("Wisdom: {}".format(self.wisdom))
        print("Constitution: {}".format(self.con))
        print("Charisma: {}".format(self.charisma))
        print("Dexterity: {}".format(self.dex))
        main_dmg = self.check_mod('weapon')
        main_crit = round(self.equipment['Weapon']().crit * 100)
        if self.equipment['OffHand']().typ == 'Weapon':
            off_dmg = self.check_mod('offhand')
            off_crit = round(self.equipment['OffHand']().crit * 100)
            print("Attack: {}/{}".format(str(main_dmg), str(off_dmg)))
            print("Critical Chance: {}%/{}%".format(str(main_crit), str(off_crit)))
        else:
            print("Attack: {}".format(str(main_dmg)))
            print("Critical Chance: {}%".format(str(main_crit)))
        print("Armor: {}".format(self.check_mod('armor')))
        if self.equipment['OffHand']().subtyp == 'Shield':
            print("Block Chance: {}%".format(round(self.equipment['OffHand']().mod * 100)))
        if len(self.spellbook['Spells']) > 0:
            spell_mod = self.check_mod('magic')
            print("Spell Modifier: +{}".format(str(spell_mod)))
            if any([x().subtyp == 'Heal' for x in self.spellbook['Spells'].values()]):
                heal_mod = self.check_mod('heal')
                print("Heal Modifier: +{}".format(str(heal_mod)))
        buffs = []
        if any([self.flying, self.invisible]):
            if self.flying:
                buffs.append("Flying")
            if self.invisible:
                buffs.append("Invisible")
            print("Buffs: " + ", ".join(buffs))
        print("#" + (10 * "-") + "#")
        if self.cls in ['Warlock', 'Shadowcaster']:
            print("Familiar Name: {}".format(self.familiar.name))
            print("Familiar Type: {}".format(self.familiar.typ))
            print("Specialty: {}".format(self.familiar.spec))
        option_list = ["Specials", "Go Back"]
        option_input = storyline.get_response(option_list)
        if option_list[option_input] == "Specials":
            self.do_action(actions.ListSpecials(), **actions.ListSpecials().kwargs)

    def flee(self, enemy, smoke=False) -> bool:
        stun = enemy.status_effects['Stun'][0]
        if smoke or stun:
            print("{} flees from the {}.".format(self.name, enemy.name))
            self.state = 'normal'
            return True
        else:
            chance = self.check_mod('luck', luck_factor=10)
            if random.randint(self.dex // 2, self.dex) + chance > \
                    random.randint(enemy.dex // 2, enemy.dex):
                print("{} flees from the {}.".format(self.name, enemy.name))
                self.state = 'normal'
                return True
            else:
                print("{} couldn't escape from the {}.".format(self.name, enemy.name))
                return False

    def use_item(self, enemy=None, tile=None):
        """

        """

        valid = False
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
            if 'Locked' in tile.__str__():
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
        cat_list.append('Go Back')
        cat_choice = storyline.get_response(cat_list)
        if cat_list[cat_choice] == 'Go Back':
            pass
        else:
            item_list = cat_dict[cat_list[cat_choice]].copy()
            if len(item_list) == 0:
                print("You do not have any items to use.")
                time.sleep(0.5)
            else:
                item_list.append('Go Back')
                print("Which item would you like to use?")
                use_itm = storyline.get_response(item_list)
                if item_list[use_itm] == 'Go Back':
                    pass
                else:
                    itm = self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]
                    valid = itm().use(self, target=enemy, tile=tile)
        return valid

    def level_up(self):
        exp_scale = 25
        print("You gained a level.")
        if (self.level + 1) % 4 == 0:
            print("Strength: {}".format(self.strength))
            print("Intelligence: {}".format(self.intel))
            print("Wisdom: {}".format(self.wisdom))
            print("Constitution: {}".format(self.con))
            print("Charisma: {}".format(self.charisma))
            print("Dexterity: {}".format(self.dex))
            time.sleep(0.5)
            print("Pick the stat you would like to increase.")
            stat_option = ['Strength', 'Intelligence', 'Wisdom', 'Constitution', 'Charisma', 'Dexterity']
            stat_index = storyline.get_response(stat_option)
            if stat_option[stat_index] == 'Strength':
                self.strength += 1
                print("You are now at {} strength.".format(self.strength))
            if stat_option[stat_index] == 'Intelligence':
                self.intel += 1
                print("You are now at {} intelligence.".format(self.intel))
            if stat_option[stat_index] == 'Wisdom':
                self.wisdom += 1
                print("You are now at {} wisdom.".format(self.wisdom))
            if stat_option[stat_index] == 'Constitution':
                self.con += 1
                print("You are now at {} constitution.".format(self.con))
            if stat_option[stat_index] == 'Charisma':
                self.charisma += 1
                print("You are now at {} charisma.".format(self.charisma))
            if stat_option[stat_index] == 'Dexterity':
                self.dex += 1
                print("You are now at {} dexterity.".format(self.dex))
        health_gain = random.randint(self.con // 3, self.con) * max(1, self.check_mod('luck', luck_factor=12))
        self.health_max += health_gain
        mana_gain = int((self.intel // 2 + self.wisdom // 3))
        mana_gain = random.randint(mana_gain // 3, mana_gain) * max(1, self.check_mod('luck', luck_factor=12))
        self.mana_max += mana_gain
        self.level += 1
        print("You are now level {}.".format(self.level))
        print("You have gained {} health points and {} mana points.".format(health_gain, mana_gain))
        if str(self.level) in spells.spell_dict[self.cls]:
            time.sleep(0.5)
            spell_gain = spells.spell_dict[self.cls][str(self.level)]
            if spell_gain().name in self.spellbook['Spells'].keys():
                print("{} goes up a level.".format(spell_gain().name))
            else:
                print("You have gained the ability to cast {}.".format(spell_gain().name))
            self.spellbook['Spells'][spell_gain().name] = spell_gain
            time.sleep(0.5)
        if str(self.level) in spells.skill_dict[self.cls]:
            time.sleep(0.5)
            skill_gain = spells.skill_dict[self.cls][str(self.level)]
            if skill_gain().name in self.spellbook['Skills'].keys():
                print("{} goes up a level.".format(skill_gain().name))
            else:
                print("You have gained the ability to use {}.".format(skill_gain().name))
            self.spellbook['Skills'][skill_gain().name] = skill_gain
            if skill_gain().name == 'Health/Mana Drain':
                del self.spellbook['Skills']['Health Drain']
                del self.spellbook['Skills']['Mana Drain']
            time.sleep(0.5)
            if skill_gain().name == 'Familiar':
                self.familiar.level_up()
            if skill_gain().name == "Transform":
                self.transform_list.append(enemies.Direbear())
        if not self.max_level():
            self.experience -= self.exp_to_gain
            self.exp_to_gain = (exp_scale ** self.pro_level) * self.level
        else:
            self.experience = "Max"
            self.exp_to_gain = "Max"
        time.sleep(0.5)

    def open_up(self, tile):
        if 'Chest' in tile.__str__():
            locked = int('Locked' in tile.__str__())
            plus = int('ChestRoom2' in tile.__str__())
            enemy = enemies.Mimic(self.location_z + locked + plus)
            if not random.randint(0, 4 + self.check_mod('luck', luck_factor=10)) and self.level >= 10:
                print("There is a Mimic in the chest!")
                time.sleep(1)
                self.state = 'fight'
                win = combat.battle(self, enemy)
            else:
                win = True
            if win:
                tile.open = True
                print("{} opens the chest, containing a {}.".format(self.name, tile.loot().name))
                self.modify_inventory(tile.loot, 1)
                input("Press enter to continue")
        elif 'Door' in tile.__str__():
            tile.open = True
            print("{} opens the door.".format(self.name))
            input("Press enter to continue")
        else:
            raise BaseException

    def loot(self, enemy, tile):
        rare = False
        print("{} dropped {} gold.".format(enemy.name, enemy.gold))
        self.gold += enemy.gold
        for item in enemy.inventory.values():
            drop = False
            chance = self.check_mod('luck', luck_factor=16) + self.pro_level
            if item[0]().rarity > (random.random() / chance) and 'Boss' not in tile.__str__():
                if item[0]().subtyp == 'Enemy':
                    for quest, info in self.quest_dict['Side'].items():
                        if info['What'] == item[0] and not info['Completed']:
                            rare = True
                            drop = True
                            break
                else:
                    drop = True
            elif 'Boss' in tile.__str__():
                drop = True
            else:
                pass
            if drop:
                print("{} dropped a {}.".format(enemy.name, item[0]().name))
                self.modify_inventory(item[0], num=item[1], rare=rare)
                self.quests(item=item[0])

    def print_inventory(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self.__str__())
            options = ["Equipment", "Inventory", "Go Back"]
            choice = storyline.get_response(options)
            if options[choice] == "Go Back":
                break
            elif options[choice] == "Equipment":
                equip_list = ["Weapon - " + self.equipment['Weapon']().name,
                              "Armor - " + self.equipment['Armor']().name,
                              "Ring - " + self.equipment['Ring']().name,
                              "Pendant - " + self.equipment['Pendant']().name]
                if self.equipment['Weapon']().handed == 1 or self.cls == 'Lancer' or self.cls == 'Dragoon' \
                        or self.cls == 'Berserker':
                    equip_list.insert(2, "OffHand - " + self.equipment['OffHand']().name)
                equip_list.append("Go Back")
                equip_input = storyline.get_response(equip_list)
                equip_choice = equip_list[equip_input].split(" ")[0]
                try:
                    print(self.equipment[equip_choice]().__str__())
                except KeyError:
                    break
            else:
                inv_option = ['Inventory', 'Special Inventory']
                inv_choice = storyline.get_response(inv_option)
                if inv_option[inv_choice] == 'Inventory':
                    print("  Gold: {}".format(self.gold))
                    if len(self.inventory) > 0:
                        inv_list = []
                        for key in self.inventory:
                            inv_list.append(key + ": " + str(self.inventory[key][1]))
                        inv_list.append("Go Back")
                        inv_input = storyline.get_response(inv_list)
                        inv_inspect = inv_list[inv_input].split(":")[0]
                        try:
                            print(self.inventory[inv_inspect][0]().__str__())
                        except KeyError:
                            break
                else:
                    if len(self.special_inventory) > 0:
                        inv_list = []
                        for key in self.special_inventory:
                            inv_list.append(key)
                        inv_list.append("Go Back")
                        inv_input = storyline.get_response(inv_list)
                        inv_inspect = inv_list[inv_input]
                        try:
                            print(self.special_inventory[inv_inspect][0]().__str__())
                        except KeyError:
                            break
            input("Press enter to continue")

    def specials(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        if len(self.spellbook['Spells']) == 0 and len(self.spellbook['Skills']) == 0:
            print("You do not have any abilities.")
            time.sleep(0.5)
            return
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(self.__str__())
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
                print(self.__str__())
                inspect_list = []
                for name, special in self.spellbook[specs[spec_input]].items():
                    inspect_list.append(name)
                    if special().subtyp == 'Heal' and self.mana >= special().cost:
                        if not special().combat:
                            cast_list.append(name)
                    elif special().subtyp == 'Movement' and self.mana >= special().cost:
                        cast_list.append(name)
                inspect_list.append("Go Back")
                inspect_input = storyline.get_response(inspect_list)
                if inspect_list[inspect_input] == 'Go Back':
                    break
                else:
                    choose_list = ["Inspect"]
                    if inspect_list[inspect_input] in cast_list:
                        choose_list.append("Cast")
                    choose_input = storyline.get_response(choose_list)
                    if choose_list[choose_input] == "Inspect":
                        print(self.spellbook[specs[spec_input]][inspect_list[inspect_input]]())
                        if inspect_list[inspect_input] == "Familiar":
                            fam_inspect = ["Inspect Familiar", "Go Back"]
                            fam_input = storyline.get_response(fam_inspect)
                            if fam_inspect[fam_input] == "Go Back":
                                break
                            else:
                                while True:
                                    os.system('cls' if os.name == 'nt' else 'clear')
                                    print("{}'s Specials".format(self.familiar.name))
                                    spec_input = storyline.get_response(specs)
                                    if specs[spec_input] == "Go Back":
                                        break
                                    else:
                                        while True:
                                            os.system('cls' if os.name == 'nt' else 'clear')
                                            print("{}'s Specials".format(self.familiar.name))
                                            if len(self.familiar.spellbook[specs[spec_input]]) == 0:
                                                print("{} does not have any {}.".format(self.familiar.name,
                                                                                        specs[spec_input].lower()))
                                                time.sleep(1)
                                                break
                                            else:
                                                fam_specials = []
                                                for name in self.familiar.spellbook[specs[spec_input]].keys():
                                                    fam_specials.append(name)
                                                fam_specials.append("Go Back")
                                                fam_special = storyline.get_response(fam_specials)
                                                if fam_specials[fam_special] == "Go Back":
                                                    break
                                                else:
                                                    print(self.familiar.spellbook[
                                                              specs[spec_input]][fam_specials[fam_special]]())
                                                    input("Press enter to continue")
                        else:
                            input("Press enter to continue")
                        break
                    elif choose_list[choose_input] == "Cast":
                        self.spellbook[specs[spec_input]][inspect_list[inspect_input]]().cast_out(self)
                        input("Press enter to continue")
                        if self.spellbook[specs[spec_input]][inspect_list[inspect_input]]().subtyp == 'Movement':
                            return
                        break

            time.sleep(0.5)

    def save(self, tmp=False):
        if tmp:
            tmp_dir = "tmp_files"
            save_file = tmp_dir + "/{0}.tmp".format(str(self.name))
            with open(save_file, 'wb') as save_game:
                pickle.dump(self.__dict__, save_game)
        else:
            while True:
                save_file = "save_files/{0}.save".format(str(self.name).lower())
                if os.path.exists(save_file):
                    print("A save file under this name already exists. Are you sure you want to overwrite it? (Y or N)")
                    yes_no = ["Yes", "No"]
                    over = storyline.get_response(yes_no)
                    if yes_no[over] == "No":
                        break
                with open(save_file, 'wb') as save_game:
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
            elif equip_slot == 'Ring' or equip_slot == 'Pendant':
                item_type = 'Accessory'
            inv_list = []
            while equip:
                yes_no = ["Yes", "No"]
                if self.equipment['Weapon']().handed == 2 and equip_slot == 'OffHand' and \
                        (self.cls != 'Lancer' and self.cls != 'Crusader' and self.cls != 'Berserker'):
                    print("You are currently equipped with a 2-handed weapon. Equipping an off-hand will remove the "
                          "2-hander.")
                    print("Do you wish to continue?")
                    cont = storyline.get_response(yes_no)
                    if yes_no[cont] == 'No':
                        break
                print("You are currently equipped with {}.".format(self.equipment[equip_slot]().name))
                old = self.equipment[equip_slot]
                if item_type == 'Accessory':
                    if old().mod in self.resistance or old().mod == 'Elemental':
                        print("You current {} gives {} resistance.".format(equip_slot, old().mod))
                    else:
                        print("You current {} gives {}.".format(equip_slot, old().mod))
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
                                    if self.inventory[item][0]().typ == self.equipment['OffHand']().typ:
                                        if self.inventory[item][0]().subtyp == 'Shield':
                                            diff = int((self.inventory[item][0]().mod -
                                                        self.equipment['OffHand']().mod) * 100)
                                            shield = True
                                        elif self.inventory[item][0]().subtyp == 'Tome':
                                            diff = self.inventory[item][0]().mod - self.equipment['OffHand']().mod
                                        else:
                                            diff = self.inventory[item][0]().damage - self.equipment['OffHand']().damage
                                if shield:
                                    inv_list.append(item + '   ' + str(diff) + '%')
                                elif diff == '':
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
                print("Which {} would you like to equip? ".format(equip_slot.lower()))
                replace = storyline.get_response(inv_list)
                if inv_list[replace] == 'Unequip':
                    self.equipment[equip_slot] = items.remove(equip_slot)
                    self.modify_inventory(old, 1)
                    print("Your {} slot is now empty.".format(equip_slot.lower()))
                elif inv_list[replace] == 'Keep Current':
                    print("No equipment was changed.")
                elif old().name == self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]][0]().name:
                    print("You are already equipped with a {}.".format(old().name))
                else:
                    if classes.equip_check(self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]],
                                           item_type, self.cls):
                        self.equipment[equip_slot] = \
                            self.inventory[re.split(r"\s{2,}", inv_list[replace])[0]][0]
                        if self.cls != 'Lancer' and self.cls != 'Dragoon' and self.cls != 'Berserker':
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
                        print("You are now equipped with {}.".format(self.equipment[equip_slot]().name))
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
        if self.level > 9 or self.pro_level > 1:
            cost = self.level * self.pro_level * 100 * self.location_z
            cost = random.randint(cost // 2, cost)
            if cost > self.gold:
                cost = self.gold
            print("Resurrection costs you {} gold.".format(cost))
            self.gold -= cost
            if not random.randint(0, self.charisma):
                print("Complications occurred during your resurrection.")
                stat_index = random.randint(0, 5)
                stat_name = stat_list[stat_index]
                if stat_name == 'strength':
                    self.strength -= 1
                if stat_name == 'intelligence':
                    self.intel -= 1
                if stat_name == 'wisdom':
                    self.wisdom -= 1
                if stat_name == 'constitution':
                    self.con -= 1
                if stat_name == 'charisma':
                    self.charisma -= 1
                if stat_name == 'dexterity':
                    self.dex -= 1
                print("You have lost 1 {}.".format(stat_name))
        self.state = 'normal'
        self.status_effects['Poison'][0] = False
        self.status_effects['DOT'][0] = False
        self.status_effects['Doom'][0] = False
        self.status_effects['Stun'][0] = False
        self.status_effects['Blind'][0] = False
        self.status_effects['Bleed'][0] = False
        self.status_effects['Disarm'][0] = False
        self.location_x, self.location_y, self.location_z = (5, 10, 0)
        print("You wake up in town.")
        time.sleep(2)
        town.town(self)

    def do_action(self, action, **kwargs):
        action_method = getattr(self, action.method.__name__)
        if action_method:
            action_method(**kwargs)

    def class_upgrades(self, enemy):
        """

        """
        if self.cls == "Soulcatcher":
            chance = max(1, 19 - self.check_mod('luck', luck_factor=20))
            if not random.randint(0, chance):  # 5% chance on kill
                print("You absorb part of the {}'s soul.".format(enemy.name))
                time.sleep(1)
                if enemy.enemy_typ == 'Reptile':
                    print("Gain 1 strength.")
                    self.strength += 1
                if enemy.enemy_typ == 'Aberration':
                    print("Gain 1 intelligence.")
                    self.intel += 1
                if enemy.enemy_typ == 'Slime':
                    print("Gain 1 wisdom.")
                    self.wisdom += 1
                if enemy.enemy_typ == 'Construct':
                    print("Gain 1 constitution.")
                    self.con += 1
                if enemy.enemy_typ == 'Humanoid':
                    print("Gain 1 charisma.")
                    self.charisma += 1
                if enemy.enemy_typ == 'Insect':
                    print("Gain 1 dexterity.")
                    self.dex += 1
                if enemy.enemy_typ == 'Animal':
                    print("Gain 5 hit points.")
                    self.health_max += 5
                if enemy.enemy_typ == 'Monster':
                    print("Gain 5 mana points.")
                    self.mana_max += 5
                if enemy.enemy_typ == 'Undead':
                    print("Gain enough experience to level.")
                    self.experience = self.exp_to_gain
                    if self.max_level():
                        self.level_up()
                if enemy.enemy_typ == 'Dragon':
                    print("Your gold has been doubled.")
                    self.gold *= 2
                time.sleep(1)
        if self.cls == "Lycan" and enemy.name == 'Red Dragon':
            if not any([x.name == "Red Dragon" for x in self.transform_list]):
                print("{} has harnessed the power of the Red Dragon and can now transform into one!".format(
                    self.name))
                time.sleep(1)
                self.spellbook['Skills']['Transform'] = spells.Transform4
                self.transform_list.append(spells.Transform4().t_creature)

    def familiar_turn(self, enemy):
        if self.familiar:
            special = None
            target = enemy
            if not random.randint(0, 1):
                if self.familiar.spec == "Defense":  # skills and spells
                    while True:
                        if not random.randint(0, 1):
                            special_list = list(self.familiar.spellbook['Spells'].keys())
                            special_type = "Spells"
                        else:
                            special_list = list(self.familiar.spellbook['Skills'].keys())
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
                    if not random.randint(0, 4) and self.mana < self.mana_max:
                        mana_regen = int(self.mana_max * 0.05)
                        if (self.mana + mana_regen) > self.mana_max:
                            mana_regen = self.mana_max - self.mana
                        self.mana += mana_regen
                        print("{} restores {}'s mana by {}.".format(self.familiar.name, self.name, mana_regen))
                    else:
                        if self.health < self.health_max and random.randint(0, 1):
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']['Regen']
                        elif not self.status_effects['Attack'][0]:
                            special = self.familiar.spellbook['Spells']['Bless']
                        elif self.familiar.level > 1 and not self.status_effects['Reflect'][0]:
                            special = self.familiar.spellbook['Spells']['Reflect']
                        elif self.familiar.level == 3 and random.randint(0, 1):
                            special = self.familiar.spellbook['Spells']['Cleanse']
                        else:
                            if random.randint(0, 1):
                                special = self.familiar.spellbook['Spells']['Heal']
                            else:
                                special = self.familiar.spellbook['Spells']['Regen']
                if self.familiar.spec == "Arcane":  # just spells
                    spell_list = list(self.familiar.spellbook['Spells'].keys())
                    choice = random.choice(spell_list)
                    if choice == "Boost" and not random.randint(0, 1) and not self.status_effects['Magic'][0]:
                        special = self.familiar.spellbook['Spells']['Boost']
                        target = self
                    else:
                        special = self.familiar.spellbook['Spells'][choice]
                if self.familiar.spec == "Luck":
                    if not random.randint(0, 1):
                        spell_list = list(self.familiar.spellbook['Spells'].keys())
                        choice = random.choice(spell_list)
                        special = self.familiar.spellbook['Spells'][choice]
                    else:
                        while True:
                            skill_list = list(self.familiar.spellbook['Skills'].keys())
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
            print("{} transforms back into their normal self.".format(self.name))
            time.sleep(1)
            health_diff = self.health_max - self.health
            mana_diff = self.mana_max - self.mana
            player_char_dict = load_char(char=self, tmp=True)
            self.cls = player_char_dict.cls
            if self.is_alive():
                self.health = max(1, player_char_dict.health_max - health_diff)
            self.health_max = player_char_dict.health_max
            self.mana = max(0, player_char_dict.mana_max - mana_diff)
            self.mana_max = player_char_dict.mana_max
            self.strength = player_char_dict.strength
            self.intel = player_char_dict.intel
            self.wisdom = player_char_dict.wisdom
            self.con = player_char_dict.con
            self.dex = player_char_dict.dex
            self.equipment = player_char_dict.equipment
            self.spellbook = player_char_dict.spellbook
            self.resistance = player_char_dict.resistance
        else:
            t_options = [x.name for x in self.transform_list]
            t_input = storyline.get_response(t_options)
            t_creature = self.transform_list[t_input]
            self.save(tmp=True)
            print("{} transforms into a {}.".format(self.name, t_creature.name))
            self.cls = t_creature.name
            self.health += t_creature.health
            self.health_max += t_creature.health_max
            self.mana += t_creature.mana
            self.mana_max += t_creature.mana_max
            self.strength += t_creature.strength
            self.intel += t_creature.intel
            self.wisdom += t_creature.wisdom
            self.con += t_creature.con
            self.dex += t_creature.dex
            self.equipment['Weapon'] = t_creature.equipment['Weapon']
            self.equipment['Armor'] = t_creature.equipment['Armor']
            self.equipment['OffHand'] = t_creature.equipment['OffHand']
            self.spellbook = t_creature.spellbook
            self.resistance = t_creature.resistance
            time.sleep(1)

    def end_combat(self, enemy, tile, flee=False):
        time.sleep(0.5)
        self.state = 'normal'
        if self.cls not in classes_dict.keys():
            self.transform(back=True)
        self.statuses(end=True)
        if all([self.is_alive(), not flee]):
            print("{} killed {}.".format(self.name, enemy.name))
            print("{} gained {} experience.".format(self.name, enemy.experience))
            if enemy.name not in list(self.kill_dict.keys()):
                self.kill_dict[enemy.name] = 0
            self.kill_dict[enemy.name] += 1
            self.loot(enemy, tile)
            if self.experience != 'Max':
                self.experience += enemy.experience
            self.class_upgrades(enemy)
            while self.experience >= self.exp_to_gain and not self.max_level():
                self.level_up()
            self.quests(enemy=enemy)
        elif flee:
            pass
        else:
            print("{} was slain by {}.".format(self.name, enemy.name))
            enemy.statuses(end=True)
            enemy.health = enemy.health_max
            enemy.mana = enemy.mana_max
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
                for quest in self.quest_dict['Main'].keys():
                    if self.quest_dict['Main'][quest]['What'] == enemy.name:
                        self.quest_dict['Main'][quest]['Completed'] = True
                        print("You have completed the quest {}.".format(quest))
        elif item is not None:
            for quest in list(self.quest_dict['Side'].keys()):
                if self.quest_dict['Side'][quest]['What'] == item:
                    if self.special_inventory[item().name][1] >= self.quest_dict['Side'][quest]['Total'] and \
                            not self.quest_dict['Side'][quest]['Completed'] and \
                            not self.quest_dict['Side'][quest]['Turned In']:
                        self.quest_dict['Side'][quest]['Completed'] = True
                        print("You have completed the quest {}.".format(quest))
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
                    print("  {}: Completed".format(quest))
                else:
                    print("  {}: {}/{}".format(quest, info[1], info[0]))
            print("#" + (30 * "-") + "#")
            print("  Quests")
            inspect_list = []
            completed_list = []
            for typ in ["Main", "Side"]:
                for quest in self.quest_dict[typ].keys():
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
            elif quest == "Completed Quests":
                for i in completed_list:
                    print("  " + i)
            else:
                if quest in self.quest_dict['Main']:
                    info = self.quest_dict['Main'][quest]
                elif quest in self.quest_dict['Side']:
                    info = self.quest_dict['Side'][quest]
                else:
                    print("You shouldn't reach here.")
                    raise BaseException
                if info['Type'] == 'Collect':
                    item_name = info['What']().name
                    if item_name in list(self.special_inventory.keys()):
                        if self.special_inventory[item_name][1] < info['Total']:
                            print("  Collect {} {}s: {}/{}".format(
                                info['Total'], item_name, self.special_inventory[item_name][1], info['Total']))
                        else:
                            print("  Collect {} {}s: Completed".format(
                                info['Total'], item_name))
                    else:
                        print("  Collect {} {}s: {}/{}".format(info['Total'], item_name, 0, info['Total']))
                elif info['Type'] == 'Defeat':
                    if info['What'] in list(self.kill_dict.keys()):
                        print("  {} {}: Completed".format(info['Type'], info['What']))
                    else:
                        print("  {} {}".format(info['Type'], info['What']))
                else:
                    if info['Completed']:
                        print("  {} {}: Completed".format(info['Type'], info['What']))
                    else:
                        print("  {} {}".format(info['Type'], info['What']))
                print("  Quest Giver: {}".format(info['Who']))
            input("Press enter to continue")

    def check_mod(self, mod, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = self.equipment['Weapon']().damage + self.strength
            if 'Monk' in self.cls:
                class_mod += (self.wisdom // 2)
            if self.cls in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level + ((self.pro_level - 1) * 20)) * (self.mana / self.mana_max)
            if self.cls in ['Thief', 'Rogue', 'Assassin', 'Ninja', 'Druid', 'Lycan']:
                class_mod += (self.dex // 2)
            if 'Physical Damage' in self.equipment['Ring']().mod:
                weapon_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            if self.status_effects['Attack'][0]:
                weapon_mod += self.status_effects['Attack'][2]
            return weapon_mod + class_mod
        elif mod == 'offhand':
            if 'Monk' in self.cls:
                class_mod += self.wisdom
            if self.cls in ['Spellblade', 'Knight Enchanter']:
                class_mod += (self.level + ((self.pro_level - 1) * 20)) * (self.mana / self.mana_max)
            if self.cls in ['Thief', 'Rogue', 'Assassin', 'Ninja', 'Druid', 'Lycan']:
                class_mod += (self.dex // 2)
            try:
                off_mod = self.equipment['OffHand']().damage + self.strength
                if 'Physical Damage' in self.equipment['Ring']().mod:
                    off_mod += int(self.equipment['Ring']().mod.split(' ')[0])
                if self.status_effects['Attack'][0]:
                    off_mod += self.status_effects['Attack'][2]
                return int((off_mod + class_mod) * 0.75)
            except AttributeError:
                return 0
        elif mod == 'armor':
            armor_mod = self.equipment['Armor']().armor
            if self.cls == 'Knight Enchanter':
                class_mod += self.intel * (self.mana / self.mana_max)
            if self.cls in ['Warlock', 'Shadowcaster']:
                if self.familiar.typ == 'Homunculus' and random.randint(0, 1) and self.familiar.pro_level > 1:
                    fam_mod = random.randint(0, 3) ** self.familiar.pro_level
                    print("{} improves {}'s armor by {}.".format(self.familiar.name, self.name, fam_mod))
                    class_mod += fam_mod
            if 'Physical Defense' in self.equipment['Ring']().mod:
                armor_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            if self.status_effects['Defense'][0]:
                armor_mod += self.status_effects['Defense'][2]
            return armor_mod * int(not ignore) + class_mod
        elif mod == 'magic':
            magic_mod = int(self.intel // 2) * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                magic_mod += (self.equipment['OffHand']().mod + (self.equipment['Weapon']().damage // 2))
            if self.equipment['Weapon']().subtyp == 'Staff' or \
                    (self.cls in ['Spellblade', 'Knight Enchanter'] and
                     self.equipment['Weapon']().subtyp == 'Longsword'):
                magic_mod += int(self.equipment['Weapon']().damage * 1.5)
            if 'Magic Damage' in self.equipment['Pendant']().mod:
                magic_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            if self.status_effects['Magic'][0]:
                magic_mod += self.status_effects['Magic'][2]
            return magic_mod + class_mod
        elif mod == 'magic def':
            m_def_mod = self.wisdom
            if 'Magic Defense' in self.equipment['Pendant']().mod:
                m_def_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            if self.status_effects['Magic Defense'][0]:
                m_def_mod += self.status_effects['Magic Defense'][2]
            return m_def_mod + class_mod
        elif mod == 'heal':
            heal_mod = self.wisdom * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                heal_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                heal_mod += int(self.equipment['Weapon']().damage * 1.5)
            if self.status_effects['Magic'][0]:
                heal_mod += self.status_effects['Magic'][2]
            return heal_mod + class_mod
        elif mod == 'resist':
            res_mod = self.resistance[typ]
            if self.flying:
                if typ == 'Earth':
                    res_mod = 1
                elif typ == 'Wind':
                    res_mod = -0.25
            if self.cls in ['Warlock', 'Shadowcaster']:
                if self.familiar.typ == 'Mephit' and random.randint(0, 1) and self.familiar.pro_level > 1:
                    fam_mod = 0.25 * random.randint(1, max(1, self.charisma // 10))
                    print("{} increases {}'s resistance to {} by {}%.".format(self.familiar.name, self.name,
                                                                              typ, int(fam_mod * 100)))
                    res_mod += fam_mod
            if self.equipment['Pendant']().mod == typ:
                res_mod = 1
            elif self.equipment['Pendant']().mod == "Elemental" and \
                    typ in ['Fire', 'Ice', 'Electric', 'Water', 'Earth', 'Wind']:
                res_mod += 0.25
            return res_mod
        elif mod == 'luck':
            luck_mod = self.charisma // luck_factor
            return luck_mod
