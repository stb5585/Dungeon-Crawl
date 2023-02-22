###########################################
""" Character creator and manager """

# Imports
import os
import re
import sys
import glob
import random
import time
import numpy
import _pickle as pickle

import items
import storyline
import world
import actions
import spells
import races
import classes


def rand_stats(race, cls) -> tuple:
    """
    Each race has a range of values per stat that the stat will fall in; the class has minimum values for each stat
    that is allowed, and will set it to the minimum required if the random value is lower
    """
    strength = random.randint(race.str_rng[0], race.str_rng[1]) + cls.str_plus
    intel = random.randint(race.int_rng[0], race.int_rng[1]) + cls.int_plus
    wisdom = random.randint(race.wis_rng[0], race.wis_rng[1]) + cls.wis_plus
    con = random.randint(race.con_rng[0], race.con_rng[1]) + cls.con_plus
    charisma = random.randint(race.cha_rng[0], race.cha_rng[1]) + cls.cha_plus
    dex = random.randint(race.dex_rng[0], race.dex_rng[1]) + cls.dex_plus
    stats = (strength, intel, wisdom, con, charisma, dex)
    return stats


def new_char() -> object:
    """
    Defines a new character and places them in the town to start
    Initial HP: 3 x constitution score
    Level HP: (0.75 * level * promotion level) + (con // 2) (Average)
    Initial MP: 2 x intel score + 1 x wisdom score
    Level MP: (0.75 * level * promotion level) + (intel // 2) (Average)
    """
    exp_scale = 1  # TODO
    world.load_tiles()
    location_x, location_y, location_z = world.starting_position
    name = ''
    # storyline.read_story("story_files/new_player.txt")
    os.system('cls' if os.name == 'nt' else 'clear')
    while name == '':
        storyline.slow_type("What is your character's name?\n")
        name = input("").capitalize()
        print("You have chosen to name your character {}. Is this correct? ".format(name))
        keep = storyline.get_response(['Yes', 'No'])
        if keep == 1:
            name = ''
    os.system('cls' if os.name == 'nt' else 'clear')
    race = races.define_race()
    cls = classes.define_class(race)
    created = {1: {"Options": [],
                   "Text": ["Welcome to {}, the {} {}.\nNow let's determine your statistics.".format(name,
                                                                                                     race.name,
                                                                                                     cls.name)]}}
    storyline.story_flow(created)
    time.sleep(1)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        stats = rand_stats(race, cls)
        stats = stats + (sum(stats),)
        specs = ("Strength", "Intelligence", "Wisdom", "Constitution", "Charisma", "Dexterity", "Total")
        spec_stat = list(zip(specs, stats))
        for i, l in enumerate(spec_stat):
            n = len(spec_stat[i][0]) + len(str(spec_stat[i][1]))
            print(l[0] + ":".ljust(16 - n) + str(l[1]))
        options = ["Reroll", "Keep"]
        keep = storyline.get_response(options)
        if options[keep] == "Keep":
            os.system('cls' if os.name == 'nt' else 'clear')
            break
    # stats = (18, 18, 18, 18, 18, 18)  # TODO delete
    hp = stats[3] * 2  # starting HP equal to constitution x 2
    mp = stats[1] + int(stats[2] * 0.5)  # starting MP equal to intel and wis x 0.5
    gil = stats[4] * 25  # starting gold equal to charisma x 25
    player = Player(location_x, location_y, location_z, state='normal', level=1, exp=0,
                    exp_to_gain=exp_scale, health=hp, health_max=hp, mana=mp, mana_max=mp,
                    strength=stats[0], intel=stats[1], wisdom=stats[2], con=stats[3], charisma=stats[4], dex=stats[5],
                    pro_level=1, gold=gil, resistance=race.resistance)
    player.name = name.capitalize()
    player.race = race.name
    player.cls = cls.name
    player.equipment = cls.equipment
    return player


def load(char=None) -> tuple:
    """
    Loads a save file and returns 2 dictionaries: one for the character and another for the world setup
    """
    if char is None:
        save_files = glob.glob("*.save")
        if len(save_files) == 0:
            return {}, {}
        else:
            chars = []
            for f in save_files:
                chars.append(f.split('.')[0].capitalize())
            print("Select the name of the character you want to load.")
            choice = storyline.get_response(chars)
            save_file = chars[choice] + ".save"
            with open(save_file, 'rb') as save_file:
                save_dict = pickle.load(save_file)
                player_dict = save_dict['Player']
                _world = save_dict['World']
            return player_dict, _world
    else:
        if os.path.exists(char + ".save"):
            with open(char + ".save", "rb") as save_file:
                save_dict = pickle.load(save_file)
                player_dict = save_dict['Player']
                _world = save_dict['World']
            return player_dict, _world
        else:
            return {}, {}


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
            player_dict, world_dict = load()
        else:
            player_dict, world_dict = load(char)
        player = Player(player_dict['location_x'], player_dict['location_y'], player_dict['location_z'],
                        player_dict['state'], player_dict['level'], player_dict['experience'],
                        player_dict['exp_to_gain'], player_dict['health'], player_dict['health_max'],
                        player_dict['mana'], player_dict['mana_max'], player_dict['strength'], player_dict['intel'],
                        player_dict['wisdom'], player_dict['con'], player_dict['charisma'], player_dict['dex'],
                        player_dict['pro_level'], player_dict['gold'], player_dict['resistance'])
        player.name = player_dict['name']
        player.race = player_dict['race']
        player.cls = player_dict['cls']
        player.status_effects = player_dict['status_effects']
        player.equipment = player_dict['equipment']
        player.inventory = player_dict['inventory']
        player.spellbook = player_dict['spellbook']
        return player, world_dict


class Character:
    """
    Basic definition of player character
    """

    def __init__(self):
        self.name = ""
        self.health = 0
        self.health_max = 0
        self.mana = 0
        self.mana_max = 0
        self.race = ""
        self.cls = ""
        self.strength = 0
        self.intel = 0
        self.wisdom = 0
        self.con = 0
        self.charisma = 0
        self.dex = 0
        self.pro_level = 1
        self.status_effects = {"Mana Shield": [False, 1],  # whether mana shield is active, health reduction per mana
                               "Stun": [False, 0],  # whether stunned, turns remaining
                               "Doom": [False, 0],  # whether doomed, turns until death
                               "Blind": [False, 0],  # whether blind, turns
                               "Disarm": [False, 0],  # whether disarmed, turns
                               "Sleep": [False, 0],  # whether asleep, turns
                               "Reflect": [False, 0],  # whether reflecting spells, turns
                               "Poison": [False, 0, 0],  # whether poisoned, turns, damage per turn
                               "DOT": [False, 0, 0],  # whether corrupted, turns, damage per turn
                               "Bleed": [False, 0, 0],  # whether bleeding, turns, damage per turn
                               "Regen": [False, 0, 0],  # whether HP is regenerating, turns, heal per turn
                               "Attack": [False, 0, 0],  # increased melee damage, turns, amount
                               "Defense": [False, 0, 0],  # increase armor rating, turns, amount
                               "Magic": [False, 0, 0],  # increase magic damage, turns, amount
                               "Magic Def": [False, 0, 0],  # increase magic defense, turns, amount
                               }
        self.equipment = {}
        self.inventory = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}
        self.resistance = {}
        self.flying = False


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

    def game_quit(self):
        """
        Function that allows for exiting the game
        """
        print("Are you sure you want to quit? Any unsaved data will be lost. ")
        yes_no = ["Yes", "No"]
        q = storyline.get_response(yes_no)
        if yes_no[q] == "Yes":
            print("Goodbye, {}!".format(self.name))
            sys.exit(0)

    def minimap(self, world_dict: dict):
        """
        Function that allows the player to view the current dungeon level in terminal
        15 x 10 grid
        """
        level = self.location_z
        map_size = (20, 20)
        map_array = numpy.zeros(map_size).astype(str)
        for tile in world_dict['World']:
            if level == tile[2]:
                tile_x, tile_y = tile[1], tile[0]
                if world_dict['World'][tile] is None:
                    continue
                elif 'stairs' in world_dict['World'][tile].intro_text(self) and world_dict['World'][tile].visited:
                    map_array[tile_x][tile_y] = "x"  # 75
                elif world_dict['World'][tile].enter:
                    map_array[tile_x][tile_y] = " "  # 255
                else:
                    if world_dict['World'][tile].visited:
                        map_array[tile_x][tile_y] = "#"
        map_array[self.location_y][self.location_x] = "+"  # 125
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

    def character_menu(self, town=False):
        """
        Lists character options in town
        """
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            if not town:
                pass  # TODO
            option_list = [actions.Status(), actions.ViewInventory(), actions.Equip(), actions.ListSpecials(),
                           actions.UseItem(), actions.Quit()]
            options = ["Status", "Inventory", "Equip", "Specials", "Use Item", "Quit Game", "Leave"]
            action_input = storyline.get_response(options)
            try:
                action = option_list[action_input]
                self.do_action(action, **action.kwargs)
            except IndexError:
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
        dmg_mod = 0
        if 'Damage' in self.equipment['Ring']().mod:
            dmg_mod += int(self.equipment['Ring']().mod.split(' ')[0])
        main_dmg = (self.strength + int(self.equipment['Weapon']().damage) + dmg_mod)
        if self.equipment['OffHand']().typ == 'Weapon':
            off_dmg = ((self.strength // 2) + (int(self.equipment['OffHand']().damage) // 2) + (dmg_mod // 2))
            print("Attack: {}/{}".format(str(main_dmg), str(off_dmg)))
            print("Critical Chance: {}%/{}%".format(str(int(1 / float(self.equipment['Weapon']().crit + 1) * 100)),
                                                    str(int(
                                                        1 / float(self.equipment['OffHand']().crit + 1) * 100))))
        else:
            print("Attack: {}".format(str(main_dmg)))
            print("Critical Chance: {}%".format(str(int(1 / float(self.equipment['Weapon']().crit + 1) * 100))))
        print("Armor: +{}".format(self.equipment['Armor']().armor))
        if self.equipment['OffHand']().subtyp == 'Shield':
            print(
                "Block Chance: {}%".format(str(int(100 / float(self.equipment['OffHand']().mod)) + self.strength)))
        elif self.equipment['Weapon']().subtyp == 'Staff' or 'Damage' in self.equipment['Pendant']().mod or \
                self.equipment['OffHand']().subtyp == 'Tome':
            spell_mod = 0
            if self.equipment['Weapon']().subtyp == 'Staff':
                spell_mod += (self.equipment['Weapon']().damage * 2)
            elif self.equipment['OffHand']().subtyp == 'Tome':
                spell_mod += self.equipment['OffHand']().mod
            if 'Magic Damage' in self.equipment['Pendant']().mod:
                spell_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            print("Spell Modifier: +{}".format(str(spell_mod)))
        if 'Physical Defense' in self.equipment['Ring']().mod:
            print('Physical Resistance: +{}'.format(str(int(self.equipment['Ring']().mod.split(' ')[0]))))
        if 'Magic Defense' in self.equipment['Pendant']().mod:
            print('Magical Resistance: +{}'.format(str(int(self.equipment['Pendant']().mod.split(' ')[0]))))
        print("#" + (10 * "-") + "#")
        if self.cls in ['Warlock', 'Shadowcaster']:
            print("Familiar Name: {}".format(self.familiar.name))
            print("Familiar Type: {}".format(self.familiar.typ))
            print("Specialty: {}".format(self.familiar.spec))
        input("Press enter to continue")

    def flee(self, enemy, smoke=False) -> bool:
        stun = enemy.status_effects['Stun'][0]
        if not smoke:
            if random.randint(1, self.health + self.level) + (self.charisma - 10) > \
                    random.randint(1, enemy.health) + (enemy.charisma - 10):
                print("{} flees from the {}.".format(self.name.capitalize(), enemy.name))
                self.state = 'normal'
                return True
            else:
                print("{} couldn't escape from the {}.".format(self.name.capitalize(), enemy.name))
                return False
        elif smoke:
            print("{} disappears in a cloud of smoke.".format(self.name.capitalize()))
            print("{} flees from the {}.".format(self.name.capitalize(), enemy.name))
            self.state = 'normal'
            return True
        elif stun:
            print("{} flees from the {}.".format(self.name.capitalize(), enemy.name))
            self.state = 'normal'
            return True

    def use_item(self, enemy=None):
        item = True
        item_list = []
        if self.state == 'fight':
            if enemy.name == 'Locked Chest':
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().name) == 'KEY':
                        item_list.append(str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
                    elif str(self.inventory[itm][0]().typ) == 'Potion':
                        item_list.append(str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
            elif enemy.name == 'Locked Door':
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().name) == 'OLDKEY':
                        item_list.append(str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
                    elif str(self.inventory[itm][0]().typ) == 'Potion':
                        item_list.append(str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
            else:
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().subtyp) == 'Health' \
                            or str(self.inventory[itm][0]().subtyp) == 'Mana':
                        item_list.append(str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
        else:
            for itm in self.inventory:
                if str(self.inventory[itm][0]().typ) == 'Potion':
                    item_list.append(str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]))
        if len(item_list) == 0:
            print("You do not have any items to use.")
            time.sleep(1)
            return False
        item_list.append('Go back')
        while item:
            print("Which potion would you like to use?")
            use_itm = storyline.get_response(item_list)
            if item_list[use_itm] == 'Go back':
                return False
            itm = self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]
            if 'Health' in itm().subtyp:
                if self.health == self.health_max:
                    print("You are already at full health.")
                else:
                    self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][1] -= 1
                    if self.state != 'fight':
                        heal = int(self.health_max *
                                   self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        print("The potion healed you for {} life.".format(heal))
                        self.health += heal
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health.")
                    else:
                        rand_heal = int(self.health_max *
                                        self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        heal = random.randint(rand_heal // 2, rand_heal) * \
                               max(1, self.check_mod('luck', luck_factor=12))
                        self.health += heal
                        print("The potion healed you for {} life.".format(heal))
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health.")
            elif 'Mana' in itm().subtyp:
                if self.mana == self.mana_max:
                    print("You are already at full mana.")
                else:
                    self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][1] -= 1
                    if self.state != 'fight':
                        heal = int(self.mana_max *
                                   self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        print("The potion restored {} mana points.".format(heal))
                        self.mana += heal
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana.")
                    else:
                        rand_res = int(self.mana_max *
                                       self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        heal = random.randint(rand_res // 2, rand_res) * max(1, self.check_mod('luck', luck_factor=12))
                        self.mana += heal
                        print("The potion restored {} mana points.".format(heal))
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana.")
            elif 'Elixir' in itm().subtyp:
                if self.health == self.health_max and self.mana == self.mana_max:
                    print("You are already at full health and mana.")
                else:
                    self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][1] -= 1
                    if self.state != 'fight':
                        health_heal = int(self.health_max *
                                          self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        mana_heal = int(self.mana_max *
                                        self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        print("The potion restored {} health points and {} mana points.".format(health_heal, mana_heal))
                        self.health += health_heal
                        self.mana += mana_heal
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health.")
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana.")
                    else:
                        rand_heal = int(self.health_max *
                                        self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        rand_res = int(self.mana_max *
                                       self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][0]().percent)
                        health_heal = random.randint(rand_heal // 2, rand_heal) * \
                                      max(1, self.check_mod('luck', luck_factor=12))
                        mana_heal = random.randint(rand_res // 2, rand_res) * \
                                    max(1, self.check_mod('luck', luck_factor=12))
                        self.health += health_heal
                        self.mana += mana_heal
                        print("The potion restored {} health points and {} mana points.".format(health_heal, mana_heal))
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health.")
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana.")
            elif 'Stat' in itm().subtyp:
                self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][1] -= 1
                if itm().stat == 'hp':
                    self.health += 5
                    self.health_max += 5
                if itm().stat == 'mp':
                    self.mana += 5
                    self.mana_max += 5
                if itm().stat == 'str':
                    self.strength += 1
                if itm().stat == 'int':
                    self.intel += 1
                if itm().stat == 'wis':
                    self.wisdom += 1
                if itm().stat == 'con':
                    self.con += 1
                if itm().stat == 'cha':
                    self.charisma += 1
                if itm().stat == 'dex':
                    self.dex += 1
                if itm().stat == 'all':
                    self.strength += 1
                    self.intel += 1
                    self.wisdom += 1
                    self.con += 1
                    self.charisma += 1
                    self.dex += 1
                    print("All your stats have increased by 1.")
                elif itm().stat == 'hp' or itm().stat == 'mp':
                    print("Your {} has been increased by 5.".format(str(itm().stat.upper())))
                else:
                    print("Your {} has been increased by 1.".format(str(itm().name.split(' ')[0]).lower()))
            elif 'Key' in itm().subtyp:
                self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][1] -= 1
                enemy.lock = False
                print("You unlock the {}.".format(enemy.name))
            if self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]][1] == 0:
                del self.inventory[re.split(r"\s{2,}", item_list[use_itm])[0]]
            break
        return True

    def level_up(self):
        exp_scale = 1  # changed from 25 to 50
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
        health_gain = int(self.pro_level * self.con)
        health_gain = random.randint(health_gain // 4, health_gain) * max(1, self.check_mod('luck', luck_factor=12))
        self.health_max += health_gain
        mana_gain = int(self.pro_level * (self.intel // 2 + self.wisdom // 3))
        mana_gain = random.randint(mana_gain // 4, mana_gain) * max(1, self.check_mod('luck', luck_factor=12))
        self.mana_max += mana_gain
        self.level += 1
        print("You are now level {}.".format(self.level))
        print("You have gained {} health points and {} mana points.".format(health_gain, mana_gain))
        if str(self.level) in spells.spell_dict[self.cls]:
            spell_gain = spells.spell_dict[self.cls][str(self.level)]
            self.spellbook['Spells'][spell_gain().name] = spell_gain
            print(spell_gain())
            print("You have gained the ability to cast {}.".format(spell_gain().name))
        if str(self.level) in spells.skill_dict[self.cls]:
            skill_gain = spells.skill_dict[self.cls][str(self.level)]
            self.spellbook['Skills'][skill_gain().name] = skill_gain
            if skill_gain().name == 'Health/Mana Drain':
                del self.spellbook['Skills']['Health Drain']
                del self.spellbook['Skills']['Mana Drain']
            print(skill_gain())
            print("You have gained the ability to use {}.".format(skill_gain().name))
            if skill_gain().name == 'Familiar':
                self.familiar.level_up()
        self.experience -= self.exp_to_gain
        self.exp_to_gain = (exp_scale ** self.pro_level) * self.level
        input("Press enter to continue")

    def open_up(self, enemy):
        # TODO add possible monsters to the chests
        if 'Chest' in enemy.name:
            if 'Locked' in enemy.name:
                enemy.health -= 1
                if random.randint(0, 2):
                    treasure = items.random_item(int(enemy.level) + max(1, self.check_mod('luck', luck_factor=10)))
                    print("The chest contained a {}.".format(treasure().name))
                    self.modify_inventory(treasure, 1)
                # elif random.randint(0, 2):
                #     combat.battle(self, enemies.random_enemy(str(self.location_z + 1)))
                else:
                    gld = random.randint(10, 50) * (int(enemy.level) + 1) * self.check_mod('luck', luck_factor=2)
                    print("You have found {} gold.".format(gld))
                    self.gold += gld
            else:
                enemy.health -= 1
                if random.randint(0, 2):
                    treasure = items.random_item(int(enemy.level) + max(0, self.check_mod('luck', luck_factor=16)))
                    print("The chest contained a {}.".format(treasure().name))
                    self.modify_inventory(treasure, 1)
                else:
                    gld = random.randint(10, 50) * int(enemy.level) * self.check_mod('luck', luck_factor=2)
                    print("You have found {} gold.".format(gld))
                    self.gold += gld
            input("Press enter to continue")
        elif 'Door' in enemy.name:
            enemy.health -= 1
            print("You open the door.")

    def loot(self, enemy):
        for item in enemy.inventory:
            if item == "Gold":
                print("{} dropped {} gold.".format(enemy.name, enemy.inventory['Gold']))
                self.gold += enemy.inventory['Gold']
            else:
                chance = max(1, int(enemy.inventory[item]().rarity / self.pro_level) -
                             self.check_mod('luck', luck_factor=16))
                if not random.randint(0, chance):
                    print("{} dropped a {}.".format(enemy.name, enemy.inventory[item]().name))
                    self.modify_inventory(enemy.inventory[item], 1)
        input("Press enter to continue")

    def print_inventory(self):  # TODO add feature to inspect items
        print("Equipment:")
        print("Weapon - " + self.equipment['Weapon']().name.title())
        if self.equipment['Weapon']().handed == 1 or self.cls == 'Lancer' or self.cls == 'Dragoon' \
                or self.cls == 'Berserker':
            print("OffHand - " + self.equipment['OffHand']().name.title())
        print("Armor - " + self.equipment['Armor']().name.title())
        print("Pendant - " + self.equipment['Pendant']().name.title())
        print("Ring - " + self.equipment['Ring']().name.title())
        print("Inventory:")
        for key in self.inventory:
            print(key.title() + ": " + str(self.inventory[key][1]))
        print("Gold: {}".format(self.gold))
        input("Press enter to continue")

    def modify_inventory(self, item, num=0, sell=False, steal=False):
        if not sell and not steal:
            if item().typ == 'Weapon' or item().typ == 'Armor' or item().typ == 'OffHand' or item().typ == 'Accessory':
                if not item().unequip:
                    if item().name not in self.inventory:
                        self.inventory[item().name] = [item, num]
                    else:
                        self.inventory[item().name][1] += num
            else:
                if item().name not in self.inventory:
                    self.inventory[item().name] = [item, num]
                else:
                    self.inventory[item().name][1] += num
        else:
            self.inventory[item().name][1] -= num
            if self.inventory[item().name][1] == 0:
                del self.inventory[item().name]

    def specials(self):
        if len(self.spellbook['Spells']) == 0 and len(self.spellbook['Skills']) == 0:
            print("You do not have any abilities.")
        else:
            cast_list = []
            if len(self.spellbook['Spells']) > 0:
                print("#" + (14 * "-") + "#")
                print("#--- Spells ---#")
                print("Name - Mana Cost")
                for name, spell in self.spellbook['Spells'].items():
                    print(name + " - " + str(spell().cost))
                    if spell().subtyp == 'Heal' and self.mana >= spell().cost:
                        if not spell().combat:
                            cast_list.append(name)
                    elif spell().subtyp == 'Movement' and self.mana >= spell().cost:
                        cast_list.append(name)
            if len(self.spellbook['Skills']) > 0:
                print("#" + (14 * "-") + "#")
                print("#--- Skills ---#")
                print("Name - Mana Cost")
                for name, skill in self.spellbook['Skills'].items():
                    print(name + " - " + str(skill().cost))
            if self.cls in ['Warlock', 'Shadowcaster']:
                print("")
                print("{}'s Specials".format(self.familiar.name))
                if len(self.familiar.spellbook['Spells']) > 0:
                    print("#" + (14 * "-") + "#")
                    print("#--- Spells ---#")
                    print("Name - Mana Cost")
                    for name, spell in self.familiar.spellbook['Spells'].items():
                        print(name + " - " + str(spell().cost))
                if len(self.familiar.spellbook['Skills']) > 0:
                    print("#" + (14 * "-") + "#")
                    print("#--- Skills ---#")
                    print("Name - Mana Cost")
                    for name, skill in self.familiar.spellbook['Skills'].items():
                        print(name + " - " + str(skill().cost))
            input("Press enter to continue")
            if len(cast_list) > 0:
                cast_list.append('Go back')
                while True:
                    print("Pick the spell you'd like to cast.")
                    cast_index = storyline.get_response(cast_list)
                    if cast_list[cast_index] == 'Go back':
                        break
                    self.spellbook['Spells'][cast_list[cast_index]]().cast_out(self)

    def save(self, wmap=None, tmp=False):
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
                _world = world.world_return()
                for tile in wmap['World']:
                    x, y, z = tile
                    try:
                        _world['World'][(x, y, z)].visited = wmap['World'][(x, y, z)].visited
                    except KeyError:
                        pass
                save_dict = {'Player': self.__dict__,
                             'World': _world}
                with open(save_file, 'wb') as save_game:
                    pickle.dump(save_dict, save_game)
                print("Your game is now saved.")
                time.sleep(1)
                break

    def equip(self, unequip=None):
        if unequip is None:
            equip = True
            print("Which piece of equipment would you like to replace? ")
            option_list = ['Weapon', 'Armor', 'OffHand', 'Pendant', 'Ring', 'None']
            slot = storyline.get_response(option_list)
            equip_slot = option_list[slot]
            item_type = option_list[slot]
            if equip_slot == 'None':
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
                    print("You current {} gives {}.".format(equip_slot, old().mod))  # TODO test
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
                                            try:
                                                current_mod = 1 / self.equipment['OffHand']().mod
                                            except ZeroDivisionError:
                                                current_mod = 0
                                            diff = int(((1 / self.inventory[item][0]().mod) -
                                                        current_mod) * 100)
                                            shield = True
                                        elif self.inventory[item][0]().subtyp == 'Tome':
                                            diff = self.inventory[item][0]().mod - self.equipment['OffHand']().mod
                                        else:
                                            diff = self.inventory[item][0]().damage - self.equipment[
                                                'OffHand']().damage
                                if shield:
                                    inv_list.append(item.title() + '   ' + str(diff) + '%')
                                elif diff == '':
                                    inv_list.append(item.title())
                                elif diff < 0:
                                    inv_list.append(item.title() + '  ' + str(diff))
                                else:
                                    inv_list.append(item.title() + '  +' + str(diff))
                    else:
                        if str(self.inventory[item][0]().subtyp) == equip_slot:
                            mod = self.inventory[item][0]().mod
                            inv_list.append(item.title() + '  ' + mod)

                if not self.equipment[equip_slot]().unequip:
                    inv_list.append('UNEQUIP'.title())
                inv_list.append('KEEP CURRENT'.title())
                print("Which {} would you like to equip? ".format(equip_slot.lower()))
                replace = storyline.get_response(inv_list)
                if inv_list[replace] == 'UNEQUIP'.title():
                    self.equipment[equip_slot] = items.remove(equip_slot)
                    self.modify_inventory(old, 1)
                    print("Your {} slot is now empty.".format(equip_slot.lower()))
                elif inv_list[replace] == 'KEEP CURRENT'.title():
                    print("No equipment was changed.")
                elif old().name == self.inventory[re.split(r"\s{2,}", inv_list[replace])[0].upper()][0]().name:
                    print("You are already equipped with a {}.".format(old().name))
                else:
                    if classes.equip_check(self.inventory[re.split(r"\s{2,}", inv_list[replace].upper())[0]],
                                           item_type, self.cls):
                        self.equipment[equip_slot] = \
                            self.inventory[re.split(r"\s{2,}", inv_list[replace])[0].upper()][0]
                        if self.cls != 'Lancer' and self.cls != 'Dragoon' and self.cls != 'Berserker':
                            if option_list[slot] == 'Weapon':
                                if self.equipment['Weapon']().handed == 2:
                                    if self.equipment['OffHand'] != items.NoOffHand:
                                        self.modify_inventory(self.equipment['OffHand'], 1)
                                        self.equipment['OffHand'] = items.remove('OffHand')
                            elif self.equipment['Weapon']().handed == 2 and equip_slot == 'OffHand':
                                old = self.equipment['Weapon']
                                self.equipment['Weapon'] = items.remove('Weapon')
                        self.inventory[re.split(r"\s{2,}", inv_list[replace])[0].upper()][1] -= 1
                        if self.inventory[re.split(r"\s{2,}", inv_list[replace])[0].upper()][1] <= 0:
                            del self.inventory[re.split(r"\s{2,}", inv_list[replace])[0].upper()]
                        if not old().unequip:
                            self.modify_inventory(old, 1)
                        print("You are now equipped with {}.".format(self.equipment[equip_slot]().name))
                time.sleep(0.5)
                break
        elif unequip:
            for item in self.equipment:
                if item in ['Weapon', 'Armor', 'OffHand']:
                    self.modify_inventory(self.equipment[item], 1)

    def check_mod(self, mod, typ=None, luck_factor=1):
        class_mod = 0
        if mod == 'weapon':
            if 'Monk' in self.cls and self.equipment['Weapon']().subtyp == 'Fist':
                class_mod += self.dex
            if self.cls == 'Spellblade' or self.cls == 'Knight Enchanter':
                class_mod = (self.level + ((self.pro_level - 1) * 20)) * (self.mana / self.mana_max)
            if self.cls in ['Thief', 'Rogue', 'Assassin', 'Ninja']:
                weapon_mod = self.dex + class_mod
            else:
                weapon_mod = self.strength + class_mod
            if not self.status_effects['Disarm']:
                weapon_mod += self.equipment['Weapon']().damage
            if 'Physical Damage' in self.equipment['Ring']().mod:
                weapon_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            weapon_mod += self.status_effects['Attack'][2]
            return weapon_mod
        elif mod == 'off':
            if 'Monk' in self.cls and self.equipment['OffHand']().subtyp == 'Fist':
                class_mod += int(self.dex * 0.5)
            try:
                off_mod = (self.strength + class_mod + self.equipment['OffHand']().damage) // 2
                if 'Physical Damage' in self.equipment['Ring']().mod:
                    off_mod += (int(self.equipment['Ring']().mod.split(' ')[0]) // 2)
                off_mod += self.status_effects['Attack'][2]
                return off_mod
            except AttributeError:
                return 0
        elif mod == 'armor':
            armor_mod = self.equipment['Armor']().armor
            if self.cls == 'Knight Enchanter':
                armor_mod += self.intel * (self.mana / self.mana_max)
            if self.cls in ['Warlock', 'Shadowcaster']:
                if self.familiar.typ == 'Homunculus' and random.randint(0, 1) and self.familiar.pro_level > 1:
                    fam_mod = random.randint(0, 3) ** self.familiar.pro_level
                    print("{} improves {}'s armor by {}.".format(self.familiar.name, self.name, fam_mod))
                    armor_mod += fam_mod
            if 'Physical Defense' in self.equipment['Ring']().mod:
                armor_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            armor_mod += self.status_effects['Defense'][2]
            return armor_mod
        elif mod == 'magic':
            magic_mod = int(self.intel // 2) * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                magic_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon']().damage * 1.5)
            if 'Magic Damage' in self.equipment['Pendant']().mod:
                magic_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            magic_mod += self.status_effects['Magic'][2]
            return magic_mod
        elif mod == 'magic def':
            m_def_mod = self.wisdom
            if 'Magic Defense' in self.equipment['Pendant']().mod:
                m_def_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            m_def_mod += self.status_effects['Magic Def'][2]
            return m_def_mod
        elif mod == 'heal':
            heal_mod = self.wisdom * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                heal_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                heal_mod += int(self.equipment['Weapon']().damage * 1.5)
            return heal_mod
        elif mod == 'resist':
            try:
                res_mod = self.resistance[typ]
                if self.cls in ['Warlock', 'Shadowcaster']:
                    if self.familiar.typ == 'Mephit' and random.randint(0, 1) and self.familiar.pro_level > 1:
                        fam_mod = 0.25 * random.randint(1, max(1, self.charisma // 10))
                        print("{} increases {}'s resistance to {} by {}%.".format(self.familiar.name, self.name,
                                                                                  typ, int(fam_mod * 100)))
                        res_mod += fam_mod
                return res_mod
            except KeyError:
                return 0
        elif mod == 'luck':
            luck_mod = self.charisma // luck_factor
            return luck_mod

    def move(self, dx, dy):
        world_dict = world.world_return()
        new_x = self.location_x + dx
        new_y = self.location_y + dy
        if world_dict['World'][(new_x, new_y, self.location_z)].enter:
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

    def is_alive(self):
        return self.health > 0

    def death(self):
        """
        Controls what happens when you die; no negative affect will occur for players under level 10
        """
        time.sleep(2)
        stat_list = ['strength', 'intelligence', 'wisdom', 'constitution', 'charisma', 'dexterity']
        if self.level > 9 or self.pro_level > 1:
            if not random.randint(0, (9 + (self.charisma // 15))):  # 10% chance to lose a stats
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
        self.health = self.health_max
        self.mana = self.mana_max
        self.location_x, self.location_y, self.location_z = world.starting_position
        print("You wake up in town.")
        time.sleep(2)

    def do_action(self, action, **kwargs):
        action_method = getattr(self, action.method.__name__)
        if action_method:
            action_method(**kwargs)
