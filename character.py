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


def rand_stats(race, cls: object) -> tuple:
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
    HP: 3 x constitution score
    MP:
    """
    world.load_tiles()
    location_x, location_y, location_z = world.starting_position
    name = ''
    storyline.read_story("story_files/new_player.txt")
    os.system('cls' if os.name == 'nt' else 'clear')
    while name == '':
        storyline.slow_type("What is your character's name?\n")
        name = input("").upper()
        keep = input("You have chosen to name your character {}. Is this correct? ".format(name)).lower()
        if keep not in ['y', 'yes']:
            name = ''
    os.system('cls' if os.name == 'nt' else 'clear')
    race = races.define_race()
    cls = classes.define_class(race)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        stats = rand_stats(race, cls)
        stats = stats + (sum(stats),)
        specs = ("Strength", "Intelligence", "Wisdom", "Constitution", "Charisma", "Dexterity", "Total")
        spec_stat = list(zip(specs, stats))
        for i, l in enumerate(spec_stat):
            n = len(spec_stat[i][0]) + len(str(spec_stat[i][1]))
            print(l[0] + ":".ljust(16 - n) + str(l[1]))
        keep = input("Would you like to keep these stats? (type Y or Yes to keep or else they will be re-rolled) "
                     "").lower()
        if keep in ['y', 'yes']:
            os.system('cls' if os.name == 'nt' else 'clear')
            break
    hp = stats[3] * 3  # starting HP equal to constitution x 3
    mp = stats[1] * 2  # TODO only uses intelligence x 2; should use wisdom (or maybe only for some classes?)
    gil = stats[4] * 25  # starting gold equal to charisma x 25
    player = Player(location=[location_x, location_y, location_z], state='normal', level=1, exp=0,
                    health=hp, health_max=hp, mana=mp, mana_max=mp,
                    strength=stats[0], intel=stats[1], wisdom=stats[2], con=stats[3], charisma=stats[4], dex=stats[5],
                    pro_level=1, gold=gil, status_effects={"Stun": [False, 0], "Poison": [False, 0, 0],
                                                           "DOT": [False, 0, 0], "Doom": [False, 0]},
                    equipment=cls.equipment, inventory={}, spellbook={'Spells': {}, 'Skills': {}})
    player.name = name.upper()
    player.race = race.name
    player.cls = cls.name
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
            i = 1
            for save_file in save_files:
                print(str(i) + ': ' + save_file.split('.save')[0].capitalize())
                i += 1
            while True:
                print("Type in the name of the character you want to load.")
                choice = input("> ").lower()
                if choice + ".save" in save_files:
                    save_file = choice + ".save"
                    break
                else:
                    print("Character file does not exist. Please choose a valid save file.")
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


def load_char(char=None) -> object:
    """
    Initializes the character based on the load file
    """
    if char is None:
        player_dict, world_dict = load()
    else:
        player_dict, world_dict = load(char)
    player = Player(player_dict['Player location'],
                    player_dict['State'],
                    player_dict['Level'],
                    player_dict['Experience'],
                    player_dict['Current health'],
                    player_dict['Max health'],
                    player_dict['Current mana'],
                    player_dict['Max mana'],
                    player_dict['Strength'],
                    player_dict['Intelligence'],
                    player_dict['Wisdom'],
                    player_dict['Constitution'],
                    player_dict['Charisma'],
                    player_dict['Dexterity'],
                    player_dict['Promotion Level'],
                    player_dict['Gold'],
                    player_dict['Status Effects'],
                    player_dict['Equipment'],
                    player_dict['Inventory'],
                    player_dict['Spellbook'])
    player.name = player_dict['Player name']
    player.race = player_dict['Race']
    player.cls = player_dict['Class']
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
        self.pro_level = 0
        self.status_effects = {"Stun": [False, 0], "Poison": [False, 0, 0], "DOT": [False, 0, 0], "Doom": [False, 0]}
        self.equipment = {}
        self.inventory = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}


class Player(Character):
    """
    Player character class
    Health is defined based on initial value and is modified by the constitution parameter
    Mana is defined based on the initial value and is modified by the intelligence and half the wisdom parameters
    """

    def __init__(self, location, state, level, exp, health, health_max, mana, mana_max, strength, intel, wisdom,
                 con, charisma, dex, pro_level, gold, status_effects, equipment, inventory, spellbook):
        super().__init__()
        self.location_x = location[0]
        self.location_y = location[1]
        self.location_z = location[2]
        self.state = state
        self.level = level
        self.experience = exp
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
        self.status_effects = status_effects
        self.equipment = equipment
        self.inventory = inventory
        self.spellbook = spellbook

    def cast_spell(self, enemy, ability):
        """
        Function that controls the character's abilities and spells during combat
        """
        stun = enemy.status_effects['Stun'][0]
        print("{} casts {}.".format(self.name.capitalize(), ability().name))
        spell_mod = 0
        if 'Damage' in self.equipment['Pendant']().mod:
            spell_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
        enemy_dam_red = 0
        try:
            if 'Defense' in enemy.equipment['Pendant']().mod:
                enemy_dam_red += int(enemy.equipment['Pendant']().mod.split(' ')[0])
        except KeyError:
            pass
        if ability().cat == 'Attack':
            damage = 0
            if self.equipment['OffHand']().subtyp == 'Tome':
                damage += self.equipment['OffHand']().mod
                spell_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                spell_mod += self.equipment['Weapon']().damage * 2
            damage += random.randint(((ability().damage * self.pro_level + self.intel) // 2) + spell_mod,
                                     (ability().damage * self.pro_level + self.intel) + spell_mod)
            damage -= random.randint((enemy.wisdom // 4) + enemy_dam_red, (enemy.wisdom // 2) + enemy_dam_red)
            crit = 1
            if not random.randint(0, ability().crit):
                crit = 2
            damage *= crit
            if crit == 2:
                print("Critical Hit!")
                time.sleep(0.25)
            if random.randint(0, enemy.dex // 2) > \
                    random.randint(self.intel // 2, self.intel) and not stun:
                print("{} dodged the {} and was unhurt.".format(enemy.name.capitalize(), ability().name))
                time.sleep(0.25)
            elif random.randint(0, enemy.con // 2) > \
                    random.randint(self.intel // 2, self.intel):
                damage //= 2
                print("{} shrugs off the {} and only receives half of the damage.".format(enemy.name, ability().name))
                print("{} damages {} for {} hit points.".format(self.name.capitalize(), enemy.name, damage))
                time.sleep(0.25)
                enemy.health = enemy.health - damage
            else:
                if damage == 0:
                    print("{} was ineffective and did 0 damage".format(ability().name))
                    time.sleep(0.25)
                else:
                    print("{} damages {} for {} hit points.".format(self.name.capitalize(), enemy.name, damage))
                    time.sleep(0.25)
                    enemy.health = enemy.health - damage
        elif ability().cat == 'Enhance':
            self.weapon_damage(enemy, dmg_mod=ability().mod * self.pro_level)
        elif ability().cat == 'Heal':
            heal = int(random.randint((self.health_max + self.wisdom) // 2, (self.health_max + self.wisdom))
                       * ability().heal)
            self.health += heal
            print("You healed yourself for {} hit points.".format(heal))
            if self.health >= self.health_max:
                self.health = self.health_max
                print("You are at full health!")
        elif ability().cat == 'Kill':
            if ability().name == 'Desoul':
                if random.randint(0, self.intel) \
                        > random.randint(enemy.con // 2, enemy.con):
                    enemy.health = 0
                    print("You rip the soul right out of the {} and it falls to the ground dead!".format(enemy.name))
                else:
                    print("The spell has no effect.")
            else:
                pass
        if ability().name == 'Terrify':
            if random.randint(self.intel // 2, self.intel) \
                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                enemy.status_effects["Stun"][0] = True
                enemy.status_effects["Stun"][1] = ability().stun
                print("You stun the {} for {} turns.".format(enemy.name, ability().stun))
        if ability().name == 'Corruption':
            if random.randint(self.intel // 2, self.intel) \
                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                enemy.status_effects["DOT"][0] = True
                enemy.status_effects["DOT"][1] = ability().dot_turns
                enemy.status_effects["DOT"][2] = ability().damage + self.intel - enemy_dam_red
                print("{}'s magic penetrates {}'s defenses.".format(self.name.capitalize(), enemy.name))
            else:
                print("The magic has no effect.")
        if ability().name == 'Doom':
            if random.randint(self.intel // 4, self.intel) \
                    > random.randint(enemy.wisdom // 2, enemy.wisdom):
                enemy.status_effects["Doom"][0] = True
                enemy.status_effects["Doom"][1] = ability().timer
                print("{}'s magic places a timer on {}'s life!".format(self.name.capitalize(), enemy.name))
            else:
                print("The magic has no effect.")
        self.mana -= ability().cost

    def use_ability(self, enemy, ability):
        print("{} uses {}.".format(self.name.capitalize(), ability().name))
        time.sleep(0.25)
        self.mana -= ability().cost
        dmg_mod = 0
        if 'Attack' in self.equipment['Ring']().mod:
            dmg_mod += int(self.equipment['Ring']().mod.split(' ')[0])
        enemy_dam_red = 0
        try:
            if 'Defense' in enemy.equipment['Ring']().mod:
                enemy_dam_red += int(enemy.equipment['Ring']().mod.split(' ')[0])
        except KeyError:
            pass
        if ability().name == 'Steal':
            if len(enemy.loot) != 0:
                if random.randint(0, self.dex) > random.randint(0, enemy.dex):
                    i = random.randint(0, len(enemy.loot) - 1)
                    item_key = list(enemy.loot.keys())[i]
                    item = enemy.loot[item_key]
                    del enemy.loot[item_key]
                    if item_key == 'Gold':
                        print("You steal {} gold from the {}!".format(item, enemy.name))
                        self.gold += item
                    else:
                        self.modify_inventory(item, num=1)
                        print("You steal {} from the {}!".format(item().name, enemy.name))
                else:
                    print("You couldn't steal anything.")
            else:
                print("The {} doesn't have anything to steal.".format(enemy.name))
        if ability().subtyp == 'Drain':
            if 'Health' in ability().name:
                drain = random.randint((enemy.health + self.intel) // 5,
                                       (enemy.health + self.intel) // 1.5)
                if not random.randint(self.wisdom // 2, self.wisdom) > random.randint(0, enemy.wisdom // 2):
                    drain = drain // 2
                if drain > enemy.health:
                    drain = enemy.health
                enemy.health -= drain
                self.health += drain
                print("You drain {} health from the {}.".format(drain, enemy.name))
            if 'Mana' in ability().name:
                drain = random.randint((enemy.mana + self.intel) // 5,
                                       (enemy.mana + self.intel) // 1.5)
                if not random.randint(self.wisdom // 2, self.wisdom) > random.randint(0, enemy.wisdom // 2):
                    drain = drain // 2
                if drain > enemy.mana:
                    drain = enemy.mana
                enemy.mana -= drain
                self.mana += drain
                print("You drain {} mana from the {}.".format(drain, enemy.name))
        if ability().name == "Shield Slam":
            if random.randint(self.dex // 2, self.dex) > random.randint(0, enemy.dex // 2):
                damage = max(1, int(self.strength * (2 / self.equipment['OffHand']().mod)) + dmg_mod)
                damage = max(0, (damage - enemy_dam_red))
                enemy.health -= damage
                print("You damage the {} with your shield for {} hit points.".format(enemy.name, damage))
                if random.randint(self.strength // 2, self.strength) \
                        > random.randint(enemy.strength // 2, enemy.strength):
                    print("You stun the {} for {} turns.".format(enemy.name, ability().stun))
                    enemy.status_effects['Stun'][0] = True
                    enemy.status_effects['Stun'][1] = ability().stun
                else:
                    print("You failed to stun the {}.".format(enemy.name))
            else:
                print("You swing your shield at the {} but miss entirely!".format(enemy.name))
        if ability().name == 'Poison Strike':
            self.weapon_damage(enemy)
            if random.randint(self.dex // 2, self.dex) \
                    > random.randint(enemy.con // 2, enemy.con):
                enemy.status_effects['Poison'][0] = True
                enemy.status_effects['Poison'][1] = ability().poison_rounds
                enemy.status_effects['Poison'][2] = ability().poison_damage
            else:
                print("The {} resisted the poison.".format(enemy.name))
        if ability().name == 'Kidney Punch':
            self.weapon_damage(enemy)
            if random.randint(self.dex // 2, self.dex) \
                    > random.randint(enemy.con // 2, enemy.con):
                enemy.status_effects['Stun'][0] = True
                enemy.status_effects['Stun'][1] = ability().stun
                print("You stunned the {} for {} turns.".format(enemy.name, ability().stun))
            else:
                print("You failed to stun the {}.".format(enemy.name))
        if ability().name == 'Lockpick':
            enemy.lock = False
        if ability().name == 'Multi-Strike':
            for _ in range(ability().strikes):
                self.weapon_damage(enemy)
        if ability().name == 'Jump':
            for _ in range(ability().strikes):
                self.weapon_damage(enemy, crit=2)
        if ability().name == 'Backstab' or ability().name == 'Piercing Strike':
            self.weapon_damage(enemy, ignore=True)
        if ability().name == 'Mortal Strike':
            self.weapon_damage(enemy, crit=ability().crit)

    def weapon_damage(self, enemy, crit=1, off_crit=1, ignore=False, dmg_mod=0):
        """
        Function that controls the character's basic attack during combat
        """
        if 'Attack' in self.equipment['Ring']().mod:
            dmg_mod += int(self.equipment['Ring']().mod.split(' ')[0])
        enemy_dam_red = 0
        try:
            if 'Defense' in enemy.equipment['Ring']().mod:
                enemy_dam_red += int(enemy.equipment['Ring']().mod.split(' ')[0])
        except KeyError:
            pass
        stun = enemy.status_effects['Stun'][0]
        blk = False
        off_blk = False
        blk_amt = 0
        off_blk_amt = 0
        dodge = False
        off_dodge = False
        off_damage = 0
        if ignore:
            dmg = max(1, (self.strength + self.equipment['Weapon']().damage + dmg_mod))
            damage = random.randint(((dmg // 2) - enemy_dam_red), (dmg - enemy_dam_red))
            if self.equipment['OffHand']().typ == 'Weapon':
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage + dmg_mod // 2))
                off_damage = random.randint(((off_dmg // 4) - enemy_dam_red), ((off_dmg // 2) - enemy_dam_red))
        elif stun:
            dmg = max(1, (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor
                          + dmg_mod))
            damage = random.randint(((dmg // 2) - enemy_dam_red), (dmg - enemy_dam_red))
            if self.equipment['OffHand']().typ == 'Weapon':
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage
                                  - enemy.equipment['Armor']().armor + dmg_mod // 2))
                off_damage = random.randint(((off_dmg // 4) - enemy_dam_red), ((off_dmg // 2) - enemy_dam_red))
        else:
            dmg = max(1,
                      (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor + dmg_mod))
            damage = random.randint(((dmg // 2) - enemy_dam_red), (dmg - enemy_dam_red))
            if enemy.equipment['OffHand']().subtyp == 'Shield':
                if not random.randint(0, int(enemy.equipment['OffHand']().mod)):
                    blk = True
                    blk_amt = (100 / enemy.equipment['OffHand']().mod +
                               random.randint(enemy.strength // 2, enemy.strength) -
                               random.randint(self.strength // 2, self.strength)) / 100
                    damage *= (1 - blk_amt)
            if random.randint(0, enemy.dex // 2) > random.randint(self.dex // 2, self.dex):
                print("{} evades {}'s attack.".format(enemy.name, self.name.capitalize()))
                time.sleep(0.25)
                dodge = True
            if self.equipment['OffHand']().typ == 'Weapon':
                off_crit = 1
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage -
                                  enemy.equipment['Armor']().armor + dmg_mod // 2))
                off_damage = random.randint(((off_dmg // 4) - enemy_dam_red), ((off_dmg // 2) - enemy_dam_red))
                if enemy.equipment['OffHand']().subtyp == 'Shield':
                    if not random.randint(0, int(enemy.equipment['OffHand']().mod)):
                        off_blk = True
                        off_blk_amt = (100 / enemy.equipment['OffHand']().mod +
                                       random.randint(enemy.strength // 2, enemy.strength) -
                                       random.randint(self.strength // 2, self.strength)) / 100
                        off_damage *= (1 - off_blk_amt)
                if random.randint(0, enemy.dex // 2) > random.randint(self.dex // 2, self.dex):
                    off_dodge = True
        if not dodge:
            if not random.randint(0, int(self.equipment['Weapon']().crit)):
                crit = 2
            damage *= crit
            damage = int(damage)
            damage = max(0, damage)
            if crit == 2:
                print("Critical Hit!")
                time.sleep(0.25)
            if blk:
                print("{} blocked {}'s attack and mitigated {} percent of the damage.".format(
                    enemy.name, self.name.capitalize(), int(blk_amt * 100)))
            if damage == 0:
                print("{} attacked {} but did 0 damage".format(self.name.capitalize(), enemy.name))
                time.sleep(0.25)
            else:
                print("{} damages {} for {} hit points.".format(self.name.capitalize(), enemy.name, damage))
                time.sleep(0.25)
            enemy.health -= damage
        if self.equipment['OffHand']().typ == 'Weapon':
            if not off_dodge:
                if not random.randint(0, int(self.equipment['OffHand']().crit)):
                    off_crit = 2
                off_damage *= off_crit
                off_damage = int(off_damage)
                off_damage = max(0, off_damage)
                if off_crit == 2:
                    print("Critical Hit!")
                    time.sleep(0.25)
                if off_blk:
                    print("{} blocked {}'s attack and mitigated {} percent of the damage.".format(
                        enemy.name, self.name.capitalize(), int(off_blk_amt * 100)))
                if off_damage == 0:
                    print("{} attacked {} but did 0 damage".format(self.name.capitalize(), enemy.name))
                    time.sleep(0.25)
                else:
                    print("{} damages {} for {} hit points.".format(self.name.capitalize(), enemy.name, off_damage))
                    time.sleep(0.25)
                enemy.health -= off_damage
            else:
                print("{} evades {}'s off-hand attack.".format(enemy.name, self.name.capitalize()))
                time.sleep(0.25)

    def game_quit(self):
        """
        Function that allows for exiting the game
        """
        q = input("Are you sure you want to quit? Any unsaved data will be lost. ").lower()
        if q in ['y', 'yes']:
            print("Goodbye, {}!".format(self.name))
            sys.exit(0)

    def minimap(self, world_dict: dict):
        """
        Function that allows the player to view the current dungeon level in terminal
        15 x 10 grid
        """
        level = self.location_z
        map_array = numpy.zeros((15, 10)).astype(str)
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

    def status(self):
        """
        Prints the status of the character
        """
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("#" + (10 * "-") + "#")
            print("Name: {}".format(self.name.capitalize()))
            print("Race: {}".format(self.race.capitalize()))
            print("Class: {}".format(self.cls.capitalize()))
            print(
                "Level: {}  Experience: {}/{}".format(self.level, self.experience, (25 ** self.pro_level) * self.level))
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
            print("Armor: {}".format(self.equipment['Armor']().armor))
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
                if 'Damage' in self.equipment['Pendant']().mod:
                    spell_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
                print("Spell Modifier: +{}".format(str(spell_mod)))
            if 'Defense' in self.equipment['Ring']().mod:
                print('Physical Resistance: {}'.format(str(int(self.equipment['Ring']().mod.split(' ')[0]))))
            if 'Defense' in self.equipment['Pendant']().mod:
                print('Magical Resistance: {}'.format(str(int(self.equipment['Pendant']().mod.split(' ')[0]))))
            print("#" + (10 * "-") + "#")
            input("Press enter to continue")
            option_dict = {
                "i": actions.ViewInventory(),
                "e": actions.Equip(),
                "b": actions.ListSpecials(),
                "p": actions.UseItem(),
                "q": actions.Quit(),
            }
            options = [actions.ViewInventory(),
                       actions.Equip(),
                       actions.ListSpecials(),
                       actions.UseItem(),
                       actions.Quit(),
                       "l: Leave"]
            for action in options:
                print(action)
            action_input = input('Action: ').lower()
            if action_input == "l":
                break
            elif action_input in list(option_dict.keys()):
                action = option_dict[action_input]
                self.do_action(action, **action.kwargs)
            else:
                print("Please enter a valid input.")
            time.sleep(1)

    def flee(self, enemy, smoke=False) -> bool:
        stun = enemy.status_effects['Stun'][0]
        if not smoke:
            if random.randint(1, self.health + self.level) > random.randint(1, enemy.health):
                print("{} flees from the {}.".format(self.name.capitalize(), enemy.name))
                self.state = 'normal'
                return True
            else:
                print("{} couldn't escape from the {}!".format(self.name.capitalize(), enemy.name))
                return False
        elif smoke:
            print("{} disappears in a cloud of smoke!".format(self.name.capitalize()))
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
        i = 0
        if self.state == 'fight':
            if enemy.name == 'Locked Chest':
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().subtyp) == 'Key':
                        item_list.append((str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]), i))
                        i += 1
            else:
                for itm in self.inventory:
                    if str(self.inventory[itm][0]().subtyp) == 'Health' \
                            or str(self.inventory[itm][0]().subtyp) == 'Mana':
                        item_list.append((str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]), i))
                        i += 1
        else:
            for itm in self.inventory:
                if str(self.inventory[itm][0]().typ) == 'Potion':
                    item_list.append((str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]), i))
                    i += 1
        if len(item_list) == 0:
            print("You do not have any items to use.")
            time.sleep(1)
            return False
        item_list.append(('Go back', i))
        while item:
            print("Which potion would you like to use?")
            use_itm = storyline.get_response(item_list)
            if item_list[use_itm][0] == 'Go back':
                return False
            itm = self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]
            if 'Health' in itm().subtyp:
                if self.health == self.health_max:
                    print("You are already at full health.")
                else:
                    self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] -= 1
                    if self.state != 'fight':
                        heal = int(self.health_max *
                                   self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        print("The potion healed you for {} life.".format(heal))
                        self.health += heal
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health!")
                    else:
                        rand_heal = int(self.health_max *
                                        self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        heal = random.randint(rand_heal // 2, rand_heal)
                        self.health += heal
                        print("The potion healed you for {} life.".format(heal))
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health!")
            elif 'Mana' in itm().subtyp:
                if self.mana == self.mana_max:
                    print("You are already at full mana.")
                else:
                    self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] -= 1
                    if self.state != 'fight':
                        heal = int(self.mana_max *
                                   self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        print("The potion restored {} mana points.".format(heal))
                        self.mana += heal
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana!")
                    else:
                        rand_res = int(self.mana_max *
                                       self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        heal = random.randint(rand_res // 2, rand_res)
                        self.mana += heal
                        print("The potion restored {} mana points.".format(heal))
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana!")
            elif 'Elixir' in itm().subtyp:
                if self.health == self.health_max and self.mana == self.mana_max:
                    print("You are already at full health and mana.")
                else:
                    self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] -= 1
                    if self.state != 'fight':
                        health_heal = int(self.health_max *
                                          self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        mana_heal = int(self.mana_max *
                                        self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        print("The potion restored {} health points and {} mana points.".format(health_heal, mana_heal))
                        self.health += health_heal
                        self.mana += mana_heal
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health!")
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana!")
                    else:
                        rand_heal = int(self.health_max *
                                        self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        rand_res = int(self.mana_max *
                                       self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        health_heal = random.randint(rand_heal // 2, rand_heal)
                        mana_heal = random.randint(rand_res // 2, rand_res)
                        self.health += health_heal
                        self.mana += mana_heal
                        print("The potion restored {} health points and {} mana points.".format(health_heal, mana_heal))
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health!")
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana!")
            elif 'Stat' in itm().subtyp:
                self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] -= 1
                if itm().stat == 'hp':
                    self.health += 5
                    self.health_max += 5
                if itm().stat == 'mp':
                    self.mana += 5
                    self.mana_max += 5
                if itm().stat == 'str': self.strength += 1
                if itm().stat == 'int': self.intel += 1
                if itm().stat == 'wis': self.wisdom += 1
                if itm().stat == 'con': self.con += 1
                if itm().stat == 'cha': self.charisma += 1
                if itm().stat == 'dex': self.dex += 1
                if itm().stat == 'all':
                    self.strength += 1
                    self.intel += 1
                    self.wisdom += 1
                    self.con += 1
                    self.charisma += 1
                    self.dex += 1
                    print("All your stats have increased by 1!")
                elif itm().stat == 'hp' or itm().stat == 'mp':
                    print("Your {} has been increased by 5!".format(str(itm().stat.upper())))
                else:
                    print("Your {} has been increased by 1!".format(str(itm().name.split(' ')[0]).lower()))
            elif 'Key' in itm().subtyp:
                self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] -= 1
                enemy.lock = False
                print("You unlock the chest!")
            if self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] == 0:
                del self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]]
            break
        return True

    def level_up(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("You gained a level!")
        if (self.level + 1) % 4 == 0:
            print("Strength: {}".format(self.strength))
            print("Intelligence: {}".format(self.intel))
            print("Wisdom: {}".format(self.wisdom))
            print("Constitution: {}".format(self.con))
            print("Charisma: {}".format(self.charisma))
            print("Dexterity: {}".format(self.dex))
            print("Pick the stat you would like to increase.")
            stat_option = [('Strength', 0), ('Intelligence', 1), ('Wisdom', 2),
                           ('Constitution', 3), ('Charisma', 4), ('Dexterity', 5)]
            stat_index = storyline.get_response(stat_option)
            if stat_option[stat_index][1] == 0:
                self.strength += 1
                print("You are now at {} strength.".format(self.strength))
            if stat_option[stat_index][1] == 1:
                self.intel += 1
                print("You are now at {} intelligence.".format(self.intel))
            if stat_option[stat_index][1] == 2:
                self.wisdom += 1
                print("You are now at {} wisdom.".format(self.wisdom))
            if stat_option[stat_index][1] == 3:
                self.con += 1
                print("You are now at {} constitution.".format(self.con))
            if stat_option[stat_index][1] == 4:
                self.charisma += 1
                print("You are now at {} charisma.".format(self.charisma))
            if stat_option[stat_index][1] == 5:
                self.dex += 1
                print("You are now at {} dexterity.".format(self.dex))
        self.experience %= (25 ** self.pro_level) * self.level
        health_gain = random.randint(self.level // 2, self.level) * self.pro_level + (self.con // 2)
        self.health_max += health_gain
        mana_gain = random.randint(self.level // 2, self.level) * self.pro_level + (self.intel // 2)
        self.mana_max += mana_gain
        self.level += 1
        print("You are now level {}.".format(self.level))
        print("You have gained {} health points and {} mana points!".format(health_gain, mana_gain))
        if str(self.level) in spells.spell_dict[self.cls]:
            spell_gain = spells.spell_dict[self.cls][str(self.level)]
            self.spellbook['Spells'][spell_gain().name] = spell_gain
            print(spell_gain())
            print("You have gained the ability to cast {}!".format(spell_gain().name))
        if str(self.level) in spells.skill_dict[self.cls]:
            skill_gain = spells.skill_dict[self.cls][str(self.level)]
            self.spellbook['Skills'][skill_gain().name] = skill_gain
            print(skill_gain())
            print("You have gained the ability to use {}!".format(skill_gain().name))
        input("Press enter to continue")

    def chest(self, enemy, unlock=False):
        # add possible monsters to the chests
        if enemy.lock:
            if unlock:
                enemy.health -= 1
                if random.randint(0, 2):
                    treasure = items.random_item(self.location_z + 1)
                    print("The chest contained a {}.".format(treasure().name))
                    self.modify_inventory(treasure, 1)
                # elif random.randint(0, 2):
                #     combat.battle(self, enemies.random_enemy(str(self.location_z + 1)))
                else:
                    gld = random.randint(100, 300) * (self.location_z + 1)
                    print("You have found {} gold!".format(gld))
                    self.gold += gld
        else:
            enemy.health -= 1
            if random.randint(0, 2):
                treasure = items.random_item(self.location_z)
                print("The chest contained a {}.".format(treasure().name))
                self.modify_inventory(treasure, 1)
            else:
                gld = random.randint(100, 300) * self.location_z
                print("You have found {} gold!".format(gld))
                self.gold += gld
        input("Press enter to continue")

    def loot(self, enemy: object):
        for item in enemy.loot:
            if item == "Gold":
                print("{} dropped {} gold.".format(enemy.name, enemy.loot['Gold']))
                self.gold += enemy.loot['Gold']
            else:
                if not random.randint(0, int(enemy.loot[item]().rarity)):
                    print("{} dropped a {}.".format(enemy.name, enemy.loot[item]().name))
                    self.modify_inventory(enemy.loot[item], 1)
        input("Press enter to continue")  # Allows time to look at output

    def print_inventory(self):
        print("Equipment:")
        print("Weapon - " + self.equipment['Weapon']().name.title())
        if self.equipment['Weapon']().handed == 1 or self.cls == 'LANCER' or self.cls == 'DRAGOON' \
                or self.cls == 'BERSERKER':
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
            i = 0
            if len(self.spellbook['Spells']) > 0:
                print("#" + (14 * "-") + "#")
                print("#--- Spells ---#")
                print("Name - Mana Cost")
                for spell in self.spellbook['Spells']:
                    print(self.spellbook['Spells'][spell]().name + " - " + str(self.spellbook['Spells'][spell]().cost))
                    if self.spellbook['Spells'][spell]().cat == 'Heal':
                        cast_list.append((self.spellbook['Spells'][spell]().name, i))
                        i += 1
            if len(self.spellbook['Skills']) > 0:
                print("#" + (14 * "-") + "#")
                print("#--- Skills ---#")
                print("Name - Mana Cost")
                for skill in self.spellbook['Skills']:
                    print(self.spellbook['Skills'][skill]().name + " - " + str(self.spellbook['Skills'][skill]().cost))
            input("Press enter to continue")
            if len(cast_list) > 0:
                cast_list.append(('Go back', i))
                while True:
                    if self.health == self.health_max:
                        print("You are already at full health.")
                        break
                    print("Pick the spell you'd like to cast.")
                    cast_index = storyline.get_response(cast_list)
                    print(cast_index)
                    if cast_list[cast_index][0] == 'Go back':
                        break
                    else:
                        heal = int(self.health_max * self.spellbook['Spells'][cast_list[cast_index][0]]().heal)
                        self.health += heal
                        print("You have been healed for {} hit points.".format(heal))
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at full health!")
                        break

    def save(self, wmap):
        while True:
            save_file = "save_files/{0}.save".format(str(self.name).lower())
            if os.path.exists(save_file):
                print("A save file under this name already exists. Are you sure you want to overwrite it? (Y or N)")
                over = input("> ").lower()
                if over != 'y':
                    break
            player_dict = {"Player": {'Player location': [self.location_x, self.location_y, self.location_z],
                                      'State': self.state,
                                      'Race': self.race,
                                      'Class': self.cls,
                                      'Player name': self.name,
                                      'Level': self.level,
                                      'Current health': self.health,
                                      'Max health': self.health_max,
                                      'Current mana': self.mana,
                                      'Max mana': self.mana_max,
                                      'Experience': self.experience,
                                      'Strength': self.strength,
                                      'Intelligence': self.intel,
                                      'Wisdom': self.wisdom,
                                      'Constitution': self.con,
                                      'Charisma': self.charisma,
                                      'Dexterity': self.dex,
                                      'Promotion Level': self.pro_level,
                                      'Gold': self.gold,
                                      'Status Effects': self.status_effects,
                                      'Equipment': self.equipment,
                                      'Inventory': self.inventory,
                                      'Spellbook': self.spellbook}}
            _world = world.world_return()
            for tile in wmap['World']:
                x, y, z = tile
                try:
                    _world['World'][(x, y, z)].visited = wmap['World'][(x, y, z)].visited
                except KeyError:
                    pass
            save_dict = dict(list(player_dict.items()) + list(_world.items()))
            with open(save_file, 'wb') as save_game:
                pickle.dump(save_dict, save_game)
            print("Your game is now saved.")
            break

    def equip(self, unequip=None):
        if unequip is None:
            equip = True
            print("Which piece of equipment would you like to replace? ")
            option_list = [('Weapon', 0), ('Armor', 1), ('OffHand', 2), ('Pendant', 3), ('Ring', 4), ('None', 5)]
            slot = storyline.get_response(option_list)
            equip_slot = option_list[slot][0]
            item_type = option_list[slot][0]
            if equip_slot == 'None':
                equip = False
            elif equip_slot == 'Ring' or equip_slot == 'Pendant':
                item_type = 'Accessory'
            inv_list = []
            while equip:
                cont = 'y'
                if self.equipment['Weapon']().handed == 2 and equip_slot == 'OffHand' and \
                        (self.cls != 'LANCER' and self.cls != 'CRUSADER' and self.cls != 'BERSERKER'):
                    print("You are currently equipped with a 2-handed weapon. Equipping an off-hand will remove the "
                          "2-hander.")
                    cont = input("Do you wish to continue? ").lower()
                    if cont != 'y':
                        break
                if cont == 'y':
                    print("You are currently equipped with {}.".format(self.equipment[equip_slot]().name))
                    old = self.equipment[equip_slot]
                    i = 0
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
                                                diff = int(((1 / self.inventory[item][0]().mod) -
                                                            (1 / self.equipment['OffHand']().mod)) * 100)
                                                shield = True
                                            elif self.inventory[item][0]().subtyp == 'Tome':
                                                diff = self.inventory[item][0]().mod - self.equipment['OffHand']().mod
                                            else:
                                                diff = self.inventory[item][0]().damage - self.equipment[
                                                    'OffHand']().damage
                                    if shield:
                                        inv_list.append((item.title() + '   ' + str(diff) + '%', i))
                                    elif diff == '':
                                        inv_list.append((item.title(), i))
                                    elif diff < 0:
                                        inv_list.append((item.title() + '  ' + str(diff), i))
                                    else:
                                        inv_list.append((item.title() + '  +' + str(diff), i))
                                    i += 1
                        else:
                            if str(self.inventory[item][0]().subtyp) == equip_slot:
                                print("You current {} gives {}.".format(equip_slot, old().mod))
                                mod = self.inventory[item][0]().mod
                                inv_list.append((item.title() + '  ' + mod, i))

                    inv_list.append(('UNEQUIP'.title(), i))
                    inv_list.append(('KEEP CURRENT'.title(), i + 1))
                    print("Which {} would you like to equip? ".format(equip_slot.lower()))
                    replace = storyline.get_response(inv_list)
                    if inv_list[replace][0] == 'UNEQUIP'.title():
                        self.equipment[equip_slot] = items.remove(equip_slot)
                        self.modify_inventory(old, 1)
                        print("Your {} slot is now empty.".format(equip_slot.lower()))
                    elif inv_list[replace][0] == 'KEEP CURRENT'.title():
                        print("No equipment was changed.")
                    elif old().name == self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0].upper()][0]().name:
                        print("You are already equipped with a {}.".format(old().name))
                    else:
                        if classes.equip_check(self.inventory[re.split(r"\s{2,}", inv_list[replace][0].upper())[0]],
                                               item_type, self.cls):
                            self.equipment[equip_slot] = \
                                self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0].upper()][0]
                            if self.cls != 'LANCER' and self.cls != 'DRAGOON' and self.cls != 'BERSERKER':
                                if option_list[slot][0] == 'Weapon':
                                    if self.equipment['Weapon']().handed == 2:
                                        if self.equipment['OffHand'] != items.NoOffHand:
                                            self.modify_inventory(self.equipment['OffHand'], 1)
                                            self.equipment['OffHand'] = items.remove('OffHand')
                                elif self.equipment['Weapon']().handed == 2 and equip_slot == 'OffHand':
                                    old = self.equipment['Weapon']
                                    self.equipment['Weapon'] = items.remove('Weapon')
                            self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0].upper()][1] -= 1
                            if self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0].upper()][1] <= 0:
                                del self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0].upper()]
                            if not old().unequip:
                                self.modify_inventory(old, 1)
                            print("You are now equipped with {}.".format(self.equipment[equip_slot]().name))
                    time.sleep(0.5)
                    break
        elif unequip:
            for item in self.equipment:
                self.modify_inventory(self.equipment[item], 1)

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
        stat_list = ['strength', 'intelligence', 'wisdom', 'constitution', 'charisma', 'dexterity']
        if self.level > 9 or self.pro_level > 1:
            if not random.randint(0, 9):  # 10% chance to lose a stats
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

    def do_action(self, action, **kwargs):
        action_method = getattr(self, action.method.__name__)
        if action_method:
            action_method(**kwargs)
