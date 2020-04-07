###########################################
""" Character creator and manager """

# Imports
import os
import re
import sys
import jsonpickle
import glob
import random
import time
import numpy
import pygame

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
    strength = random.randint(race.str_rng[0], race.str_rng[1])
    if cls.min_str > strength:
        strength = cls.min_str
    intel = random.randint(race.int_rng[0], race.int_rng[1])
    if cls.min_int > intel:
        intel = cls.min_int
    wisdom = random.randint(race.wis_rng[0], race.wis_rng[1])
    if cls.min_wis > wisdom:
        wisdom = cls.min_wis
    con = random.randint(race.con_rng[0], race.con_rng[1])
    if cls.min_con > con:
        con = cls.min_con
    charisma = random.randint(race.cha_rng[0], race.cha_rng[1])
    if cls.min_cha > charisma:
        charisma = cls.min_cha
    dex = random.randint(race.dex_rng[0], race.dex_rng[1])
    if cls.min_dex > dex:
        dex = cls.min_dex
    stats = (strength, intel, wisdom, con, charisma, dex)
    return stats


def new_char() -> object:
    """
    Defines a new character and places them in the town to start
    """
    location_x, location_y, location_z = world.starting_position
    race = races.define_race()
    cls = classes.define_class()
    stats = rand_stats(race, cls)
    print(stats)
    player = Player(location=[location_x, location_y, location_z], state='normal', level=1, exp=0,
                    health=stats[3] * 2, health_max=stats[3] * 2, mana=stats[1], mana_max=stats[1], strength=stats[0],
                    intel=stats[1], wisdom=stats[2], con=stats[3], charisma=stats[4], dex=stats[5], gold=stats[4] * 10,
                    equipment=cls.equipment, inventory={}, spellbook={})
    while player.name == '':
        player.name = input("What is your character's name? ").upper()
    player.race = race.name
    player.cls = cls.name
    return player


def load(char=None) -> dict:
    """
    Loads a save file and returns 2 dictionaries: one for the character and another for the world setup
    """
    if char is None:
        save_files = glob.glob("save_files/*.save")
        if len(save_files) == 0:
            return {}
        else:
            i = 1
            for save_file in save_files:
                save_file = save_file.split('/')[1]
                print(str(i) + ': ' + save_file.split('.save')[0])
                i += 1
            while True:
                print("Type in the name of the character you want to load.")
                choice = input("> ").upper()
                if 'save_files/' + choice + '.save' in save_files:
                    save_file = 'save_files/' + choice + '.save'
                    break
                else:
                    print("Character file does not exist. Please choose a valid save file.")
        with open(save_file, 'rb') as save_file:
            save_dict = jsonpickle.decode(save_file.read())
            player_dict = save_dict['Player']
            _world = save_dict['World']
        return player_dict, _world
    else:
        if os.path.exists('save_files/' + char + '.save'):
            with open('save_files/' + char + '.save', 'rb') as save_file:
                save_dict = jsonpickle.decode(save_file.read())
                player_dict = save_dict['Player']
                _world = save_dict['World']
            return player_dict, _world
        else:
            return {}


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
                    player_dict['Gold'],
                    player_dict['Equipment'],
                    player_dict['Inventory'],
                    player_dict['Spellbook'])
    player.name = player_dict['Player name']
    player.race = player_dict['Race']
    player.cls = player_dict['Class']
    return player


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
        self.equipment = {}
        self.inventory = {}
        self.spellbook = {}

    def special(self, enemy, ability: object):
        """
        Function that controls the character's abilities and spells during combat
        """
        print("%s casts %s." % (self.name, ability().name))
        if ability().typ == 'Skill':
            print("Skills don't work yet, so you just attack.")
            self.weapon_damage(enemy)
        if ability().typ == 'Spell':
            self.mana -= ability().cost
            damage = random.randint((ability().damage + self.intel) // 2, (ability().damage + self.intel))
            if self.equipment['OffHand']().subtyp == 'Grimoire':
                damage += self.equipment['OffHand']().mod
            damage -= random.randint(0, enemy.wisdom)
            crit = 1
            if not random.randint(0, ability().crit - 1):
                crit = 2
            damage *= crit
            if crit == 2:
                print("Critical Hit!")
            if random.randint(0, enemy.dex) > random.randint(self.intel // 2, self.intel):
                print("%s dodged the %s and was unhurt." % (enemy.name, ability().name))
            elif random.randint(0, enemy.con) > random.randint(self.intel // 2, self.intel):
                damage //= 2
                print("%s shrugs off the %s and only receives half of the damage." % (enemy.name, ability().name))
                print("%s damages %s for %s hit points." % (self.name, enemy.name, damage))
                enemy.health = enemy.health - damage
            else:
                if damage == 0:
                    print("%s was ineffective and did 0 damage" % ability().name)
                else:
                    print("%s damages %s for %s hit points." % (self.name, enemy.name, damage))
                    enemy.health = enemy.health - damage

    def weapon_damage(self, enemy: object):
        """
        Function that controls the character's basic attack during combat
        """
        dmg = max(1, (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor))
        damage = random.randint(dmg // 2, dmg)
        if self.equipment['OffHand']().typ == 'Weapon':
            off_dmg = self.equipment['OffHand']().damage
            damage += random.randint(off_dmg // 4, off_dmg // 2)
        crit = 1
        if not random.randint(0, int(self.equipment['Weapon']().crit) - 1):
            crit = 2
        damage *= crit
        blk = False
        blk_amt = 0
        if enemy.equipment['OffHand']().subtyp == 'Shield':
            if not random.randint(0, int(enemy.equipment['OffHand']().mod) - 1):
                blk = True
                blk_amt = 1 / int(enemy.equipment['OffHand']().mod)
                damage *= (1 - blk_amt)
        damage = int(damage)
        damage += self.equipment['Weapon']().damage
        damage = max(0, damage - enemy.equipment['Armor']().armor)
        if random.randint(0, enemy.dex // 2) > random.randint(self.dex // 2, self.dex):
            print("%s evades %s's attack." % (enemy.name, self.name))
        else:
            if crit == 2:
                print("Critical Hit!")
            if blk:
                print("%s blocked %s\'s attack and mitigated %d percent of the damage." % (
                    enemy.name, self.name, int(blk_amt * 100)))
            if damage == 0:
                print("%s attacked %s but did 0 damage" % (self.name, enemy.name))
            else:
                print("%s damages %s for %s hit points." % (self.name, enemy.name, damage))
            enemy.health = enemy.health - damage


class Player(Character):
    """
    Player character class
    Health is defined based on initial value and is modified by the constitution parameter
    Mana is defined based on the initial value and is modified by the intelligence and half the wisdom parameters
    """

    def __init__(self, location, state, level, exp, health, health_max, mana, mana_max, strength, intel, wisdom,
                 con, charisma, dex, gold, equipment, inventory, spellbook):
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
        self.gold = gold
        self.equipment = equipment
        self.inventory = inventory
        self.spellbook = spellbook

    def game_quit(self):
        """
        Function that allows for exiting the game
        """
        print("Goodbye, %s!" % self.name)
        sys.exit(0)

    def minimap(self, world_dict: dict):
        """
        Function that allows the player to view the current dungeon level in a window
        Window must be closed to continue playing
        """
        print("Hit the x on the minimap to continue")
        level = self.location_z
        map_array = numpy.zeros((10, 15))
        for tile in world_dict['World']:
            if level == tile[2]:
                x, y = tile[0], tile[1]
                if world_dict['World'][tile] is not None:
                    map_array[x][y] = 255
        map_array[self.location_x][self.location_y] = 125
        pygame.init()
        screen = pygame.display.set_mode((400, 400))
        surf = pygame.surfarray.make_surface(map_array)
        surf = pygame.transform.scale(surf, (300, 300))  # Scaled a bit.
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            screen.blit(surf, (50, 50))
            pygame.display.update()
        pygame.display.quit()

    def status(self):
        """
        Prints the status of the character
        """
        print("#" + (10 * "-") + "#")
        print("Name: %s" % self.name)
        print("Race: %s" % self.race)
        print("Class: %s" % self.cls)
        print("Level: %s  Experience: %s" % (self.level, self.experience))
        print("HP: %d/%d  MP: %d/%d" % (self.health, self.health_max, self.mana, self.mana_max))
        print("Strength: %d" % self.strength)
        print("Intelligence: %d" % self.intel)
        print("Wisdom: %d" % self.wisdom)
        print("Constitution: %d" % self.con)
        print("Charisma: %d" % self.charisma)
        print("Dexterity: %d" % self.dex)
        if self.equipment['OffHand']().typ == 'Weapon':
            print("Attack: %s" % str(self.strength + int(self.equipment['Weapon']().damage) +
                                     int(self.equipment['OffHand']().damage) // 2))
        else:
            print("Attack: %s" % str(self.strength + int(self.equipment['Weapon']().damage)))
        print("Critical Chance: %s%%" % str(int(1 / float(self.equipment['Weapon']().crit) * 100)))
        print("Armor: %d" % self.equipment['Armor']().armor)
        if self.equipment['OffHand']().subtyp == 'Shield':
            print("Block Chance: %s%%" % str(int((1 / self.equipment['OffHand']().mod) * 100)))
        print("#" + (10 * "-") + "#")
        input("Press enter to continue")
        world_dict = world.world_return()
        options = [actions.ViewInventory(),
                   actions.Equip(),
                   actions.ListSpecials(),
                   actions.UseItem(),
                   actions.Minimap(world_dict),
                   actions.Quit()]
        for action in options:
            print(action)
        action_input = input('Action: ')
        for action in options:
            if action_input == action.hotkey:
                self.do_action(action, **action.kwargs)
                break

    def flee(self, enemy: object) -> bool:
        if random.randint(1, self.health + self.level) > random.randint(1, enemy.health):
            print("%s flees from the %s." % (self.name, enemy.name))
            self.state = 'normal'
            return True
        else:
            print("%s couldn't escape from the %s!" % (self.name, enemy.name))
            return False

    def use_item(self):
        item = True
        item_list = []
        i = 0
        if self.state == 'fight':
            for itm in self.inventory:
                if str(self.inventory[itm][0]().subtyp) == 'Health' or str(self.inventory[itm][0]().subtyp) == 'Mana':
                    item_list.append((str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]), i))
                    i += 1
        else:
            for itm in self.inventory:
                if str(self.inventory[itm][0]().typ) == 'Potion':
                    item_list.append((str(self.inventory[itm][0]().name) + '  ' + str(self.inventory[itm][1]), i))
                    i += 1
        if len(item_list) == 0:
            print("You do not have any items to use.")
            item = False
        item_list.append(('None', i))
        while item:
            print("Which potion would you like to use?")
            use_itm = storyline.get_response(item_list)
            if item_list[use_itm][0] == 'None':
                break
            itm = self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]
            if 'Health' in itm().subtyp:
                if self.health == self.health_max:
                    print("You are already at full health.")
                else:
                    self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] -= 1
                    if self.state != 'fight':
                        heal = int(self.health_max *
                                   self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        print("The potion healed you for %d life." % heal)
                        self.health += heal
                        if self.health >= self.health_max:
                            self.health = self.health_max
                            print("You are at max health!")
                    else:
                        rand_heal = int(self.health_max *
                                        self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        heal = random.randint(rand_heal // 2, rand_heal)
                        self.health += heal
                        print("The potion healed you for %d life." % heal)
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
                        print("The potion restored %d mana points." % heal)
                        self.mana += heal
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana!")
                    else:
                        rand_res = int(self.mana_max *
                                       self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][0]().percent)
                        heal = random.randint(rand_res // 2, rand_res)
                        self.mana += heal
                        print("The potion restored %d mana points." % heal)
                        if self.mana >= self.mana_max:
                            self.mana = self.mana_max
                            print("You are at full mana!")
            elif 'Stat' in itm().subtyp:
                self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] -= 1
                if itm().stat == 'str': self.strength += 1
                if itm().stat == 'int': self.intel += 1
                if itm().stat == 'wis': self.wisdom += 1
                if itm().stat == 'con': self.con += 1
                if itm().stat == 'cha': self.charisma += 1
                if itm().stat == 'dex': self.dex += 1
                print("Your %s has been increased by 1!" % str(itm().name.split(' ')[0]).lower())
            if self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]][1] == 0:
                del self.inventory[re.split(r"\s{2,}", item_list[use_itm][0])[0]]
            break

    def level_up(self):
        print("You gained a level!")
        if (self.level + 1) % 4 == 0:
            print("Strength: %d" % self.strength)
            print("Intelligence: %d" % self.intel)
            print("Wisdom: %d" % self.wisdom)
            print("Constitution: %d" % self.con)
            print("Charisma: %d" % self.charisma)
            print("Dexterity: %d" % self.dex)
            print("Pick the stat you would like to increase.")
            stat_option = [('Strength', 0), ('Intelligence', 1), ('Wisdom', 2),
                           ('Constitution', 3), ('Charisma', 4), ('Dexterity', 5)]
            stat_index = storyline.get_response(stat_option)
            if stat_option[stat_index][1] == 0:
                self.strength += 1
                print("You are now at %s strength." % self.strength)
            if stat_option[stat_index][1] == 1:
                self.intel += 1
                print("You are now at %s intelligence." % self.intel)
            if stat_option[stat_index][1] == 2:
                self.wisdom += 1
                print("You are now at %s wisdom." % self.wisdom)
            if stat_option[stat_index][1] == 3:
                self.con += 1
                print("You are now at %s constitution." % self.con)
            if stat_option[stat_index][1] == 4:
                self.charisma += 1
                print("You are now at %s charisma." % self.charisma)
            if stat_option[stat_index][1] == 5:
                self.dex += 1
                print("You are now at %s dexterity." % self.dex)
        self.experience %= 25 * self.level
        health_gain = random.randint(self.level // 2, self.level) + (self.con // 2)
        self.health_max += health_gain
        mana_gain = random.randint(self.level // 2, self.level) + (self.intel // 2)
        self.mana_max += mana_gain
        self.level += 1
        print("You are now level %s." % self.level)
        print("You have gained %s health points and %s mana points!" %
              (health_gain, mana_gain))
        if str(self.level) in spells.spell_dict[self.cls]:
            spell_gain = spells.spell_dict[self.cls][str(self.level)]
            self.spellbook[spell_gain().name] = spell_gain
            print(spell_gain())
            print("You have gained the ability to cast %s!" % spell_gain().name)
        input("Press enter to continue")

    def chest(self, enemy: object):
        enemy.health -= 1
        if random.randint(0, 2):
            treasure = items.random_item(self.location_z)
            print("The chest contained a %s." % treasure().name)
            self.modify_inventory(treasure, 1)
        else:
            gld = random.randint(50, 100) * self.location_z
            print("You have found %s gold!" % gld)
            self.gold += gld
        input("Press enter to continue")

    def loot(self, enemy: object):
        for item in enemy.loot:
            if item == "Gold":
                print("%s dropped %d gold." % (enemy.name, enemy.loot['Gold']))
                self.gold += enemy.loot['Gold']
            else:
                if not random.randint(0, int(enemy.loot[item]().rarity)):
                    print("%s dropped a %s." % (enemy.name, enemy.loot[item]().name))
                    self.modify_inventory(enemy.loot[item], 1)
        input("Press enter to continue")  # Allows time to look at output

    def print_inventory(self):
        print("Equipment:")
        print("Weapon - " + self.equipment['Weapon']().name)
        if self.equipment['Weapon']().handed == 1:
            print("OffHand - " + self.equipment['OffHand']().name)
        print("Armor - " + self.equipment['Armor']().name)
        print("Inventory:")
        for key in self.inventory:
            print(key + " " + str(self.inventory[key][1]))
        print("Gold: %d" % self.gold)
        input("Press enter to continue")

    def modify_inventory(self, item, num=0, sell: object = False):
        if not sell:
            if item().name not in self.inventory:
                self.inventory[item().name] = [item, num]
            else:
                self.inventory[item().name][1] += num
        else:
            self.inventory[item().name][1] -= num
            if self.inventory[item().name][1] == 0:
                del self.inventory[item().name]

    def specials(self):
        print("Spells/Skills:")
        for spell in self.spellbook:
            print(spell, self.spellbook[spell]().cost)
        input("Press enter to continue")

    def save(self):
        while True:
            save_file = "save_files/{0}.save".format(str(self.name))
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
                                      'Gold': self.gold,
                                      'Equipment': self.equipment,
                                      'Inventory': self.inventory,
                                      'Spellbook': self.spellbook}}
            _world = world.world_return()
            save_dict = dict(list(player_dict.items()) + list(_world.items()))
            with open(save_file, 'w') as save_game:
                save_game.write(jsonpickle.encode(save_dict))
            print("Your game is now saved.")
            break

    def equip(self, unequip=None):
        if unequip is None:
            equip = True
            print("Which piece of equipment would you like to replace? ")
            option_list = [('Weapon', 0), ('Armor', 1), ('OffHand', 2), ('None', 3)]
            slot = storyline.get_response(option_list)
            if option_list[slot][0] == 'None':
                equip = False
            inv_list = []
            while equip:
                cont = 'y'
                if self.equipment['Weapon']().handed == 2 and option_list[slot][0] == 'OffHand':
                    print("You are currently equipped with a 2-handed weapon. Equipping an off-hand will remove the "
                          "2-hander.")
                    cont = input("Do you wish to continue? ").lower()
                    if cont != 'y':
                        break
                if cont == 'y':
                    print("You are currently equipped with %s." % self.equipment[option_list[slot][0]]().name)
                    old = self.equipment[option_list[slot][0]]
                    i = 0
                    for item in self.inventory:
                        if (str(self.inventory[item][0]().typ) == option_list[slot][0] or
                                (option_list[slot][0] == 'OffHand' and str(self.inventory[item][0]().typ) == 'Weapon'
                                 and classes.equip_check(self.inventory[item], option_list[slot][0], self.cls))):
                            diff = ''
                            if classes.equip_check(self.inventory[item], option_list[slot][0], self.cls):
                                if option_list[slot][0] == 'Weapon':
                                    diff = self.inventory[item][0]().damage - self.equipment['Weapon']().damage
                                elif option_list[slot][0] == 'Armor':
                                    diff = self.inventory[item][0]().armor - self.equipment['Armor']().armor
                                elif option_list[slot][0] == 'OffHand':
                                    try:
                                        diff = self.inventory[item][0]().mod - self.equipment['OffHand']().mod
                                    except AttributeError:
                                        diff = 0
                                if diff < 0:
                                    inv_list.append((item + '   ' + str(diff), i))
                                else:
                                    inv_list.append((item + '   +' + str(diff), i))
                                i += 1
                    inv_list.append(('UNEQUIP', i))
                    inv_list.append(('KEEP CURRENT', i + 1))
                    print("Which %s would you like to equip? " % option_list[slot][0].lower())
                    replace = storyline.get_response(inv_list)
                    if inv_list[replace][0] == 'UNEQUIP':
                        self.equipment[option_list[slot][0]] = items.remove(option_list[slot][0])
                        self.modify_inventory(old, 1)
                        print("Your %s slot is now empty." % option_list[slot][0].lower())
                    elif inv_list[replace][0] == 'KEEP CURRENT':
                        print("No equipment was changed.")
                    elif old().name == self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0]][0]().name:
                        print("You are already equipped with a %s" % old().name)
                    else:
                        if classes.equip_check(self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0]],
                                               option_list[slot][0], self.cls):
                            self.equipment[option_list[slot][0]] = \
                                self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0]][0]
                            if option_list[slot][0] == 'Weapon':
                                if self.equipment['Weapon']().handed == 2:
                                    if self.equipment['OffHand'] != items.NoOffHand:
                                        self.modify_inventory(self.equipment['OffHand'], 1)
                                        self.equipment['OffHand'] = items.remove('OffHand')
                            elif self.equipment['Weapon']().handed == 2 and option_list[slot][0] == 'OffHand':
                                old = self.equipment['Weapon']
                                self.equipment['Weapon'] = items.remove('Weapon')
                            self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0]][1] -= 1
                            if self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0]][1] <= 0:
                                del self.inventory[re.split(r"\s{2,}", inv_list[replace][0])[0]]
                            if not old().unequip:
                                self.modify_inventory(old, 1)
                            print("You are now equipped with %s." % self.equipment[option_list[slot][0]]().name)
                    time.sleep(0.5)
                    break
        elif unequip:
            for item in self.equipment:
                self.modify_inventory(self.equipment[item], 1)
                items.remove(self.equipment[item]().typ)

    def move(self, dx, dy):
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

    def do_action(self, action, **kwargs):
        action_method = getattr(self, action.method.__name__)
        if action_method:
            action_method(**kwargs)
