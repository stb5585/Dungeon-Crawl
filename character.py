###########################################
""" Character and enemy creator """

import os
import sys
import jsonpickle
import glob
import random
from typing import List, Union, Any

import items


# import movement
# import enemy


# Define functions
def game_help():
    print(list(Commands.keys()))


def game_quit():
    print("Goodbye!")
    sys.exit(0)


def new_char():
    player = Player(state='normal', level=1, exp=0, health=10, max_health=10, attack=5, defense=2, speed=10, gold=0,
                    equipment={}, inventory={})
    player.name = input("What is your character's name? ")
    player.equipment = dict(Weapon=items.Unarmed, Armor=items.Naked)
    return player


def load(char=None):
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
                choice = input("> ")
                if 'save_files/' + choice + '.save' in save_files:
                    save_file = 'save_files/' + choice + '.save'
                    break
                else:
                    print("Character file does not exist. Please choose a valid save file.")
        with open(save_file, 'rb') as save_file:
            player_dict = jsonpickle.decode(save_file.read())
    else:
        if os.path.exists('save_files/' + char + '.save'):
            with open('save_files/' + char + '.save', 'rb') as save_file:
                player_dict = jsonpickle.decode(save_file.read())
        else:
            return {}
    return player_dict


def load_char(char=None) -> object:
    if char is None:
        player_dict = load()
    else:
        player_dict = load(char)
    player = Player('normal',
                    player_dict['Level'],
                    player_dict['Experience'],
                    player_dict['Current health'],
                    player_dict['Max health'],
                    player_dict['Attack'],
                    player_dict['Defense'],
                    player_dict['Speed'],
                    player_dict['Gold'],
                    player_dict['Equipment'],
                    player_dict['Inventory'])
    player.name = player_dict['Player name']
    return player


class Character:

    def __init__(self):
        self.name = ""
        self.health = 0
        self.health_max = 0
        self.attack = 0
        self.defense = 0
        self.speed = 0
        self.equipment = {}
        self.inventory = {}

    def do_damage(self, enemy):
        dmg = max(1, self.attack - enemy.defense)
        damage = random.randint(1, dmg)
        if self.equipment['Weapon'] != items.Unarmed:
            damage += self.equipment['Weapon']().damage
        if self.equipment['Armor'] != items.Naked:
            damage = max(1, damage - enemy.equipment['Armor']().armor)

        # higher speed means slower character
        if not random.randint(0, enemy.speed - 1):
            print("%s evades %s's attack." % (enemy.name, self.name))
        else:
            print("%s damages %s for %s hit points." % (self.name, enemy.name, damage))
            enemy.health = enemy.health - damage

        return enemy.health <= 0


class Enemy(Character):

    def __init__(self, name, health, attack, defense, speed, exp):
        Character.__init__(self)
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.experience = exp
        self.equipment = dict(Weapon=items.Unarmed, Armor=items.Naked)
        self.inventory = dict(Gold=0)


class Goblin(Enemy):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(2, 4), attack=1, defense=2, speed=10,
                         exp=random.randint(2, 3))
        self.equipment['Weapon'] = items.Sword
        self.loot = dict(Gold=random.randint(4, 10), Weapon=self.equipment['Weapon'])


class GiantRat(Enemy):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(1, 3), attack=2, defense=1, speed=5,
                         exp=random.randint(1, 2))
        self.loot = dict(Gold=random.randint(1, 5))


class Bandit(Enemy):

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), attack=6, defense=1, speed=10,
                         exp=random.randint(3, 8))
        self.equipment['Armor'] = items.Breastplate
        self.loot = dict(Gold=random.randint(15, 25), Armor=self.equipment['Armor'])


class Skeleton(Enemy):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), attack=8, defense=5, speed=20,
                         exp=random.randint(4, 10))
        self.loot = dict(Gold=random.randint(10, 50), Potion=items.HealthPotion)


class Player(Character):

    def __init__(self, state, level, exp, health, max_health, attack, defense, speed, gold, equipment, inventory):
        Character.__init__(self)
        self.enemy = None
        self.state = state
        self.level = level
        self.experience = exp
        self.health = health
        self.health_max = max_health
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.gold = gold
        self.equipment = equipment
        self.inventory = inventory

    def status(self):
        print("%s is level %s with %s experience points" % (self.name, self.level, self.experience))
        print("%s's health: %d/%d" % (self.name, self.health, self.health_max))
        print("%s has %s attack." % (self.name, self.attack + int(self.equipment['Weapon']().damage)))
        print("%s has %s defense and a %d percent chance to evade attack." % (self.name, (self.defense + self.equipment[
            "Armor"]().armor), int((1 / self.speed) * 100)))

    def tired(self):
        print("%s feels tired." % self.name)
        self.health = max(1, self.health - 1)

    def rest(self):
        if self.state != 'normal':
            print("%s can't rest now!" % self.name)
            self.enemy_attacks()
        else:
            print("%s rests." % self.name)

        if not random.randint(0, 3):
            monsters = [Goblin(), GiantRat(), Bandit(), Skeleton()]
            self.enemy = random.choice(monsters)
            print("%s is rudely awakened by a %s!" % (self.name, self.enemy.name))
            self.state = 'fight'
            self.enemy_attacks()
        else:
            if self.health < self.health_max:
                heal = random.randint(1, self.health_max - self.health)
                self.health += heal
                print("You rested and feel refreshed! You healed for %d hit points." % heal)
                if self.health >= self.health_max:
                    self.health = self.health_max
                    print("You are at full strength!")
            else:
                print("%s slept too much." % self.name)
                self.health = self.health - 1

    def explore(self):
        if self.state != 'normal':
            print("%s is too busy right now!" % self.name)
        else:
            print("%s explores a twisty passage." % self.name)
            if not random.randint(0, 2):
                monsters = [Goblin(), GiantRat(), Bandit(), Skeleton()]
                self.enemy = random.choice(monsters)
                print("%s encounters a %s!" % (self.name, self.enemy.name))
                self.state = 'fight'
            elif not random.randint(0, 2):
                self.tired()
            elif not random.randint(0, 2):
                self.chest()

    def flee(self):
        if self.state != 'fight':
            print("%s runs in circles for a while." % self.name)
            self.tired()
        else:
            if random.randint(1, self.health + 5) > random.randint(1, self.enemy.health):
                print("%s flees from the %s." % (self.name, self.enemy.name))
                self.state = 'normal'
            else:
                print("%s couldn't escape from the %s!" % (self.name, self.enemy.name))
                self.enemy_attacks()

    def attack(self):
        if self.state != 'fight':
            print("%s swats the air, without notable results." % self.name)
            self.tired()
        else:
            if self.do_damage(self.enemy):
                print("%s executes the %s!" % (self.name, self.enemy.name))
                print("%s gained %s experience." % (self.name, self.enemy.experience))
                self.experience += self.enemy.experience
                if self.experience >= 10 * self.level:
                    self.level_up()
                self.loot()
                self.state = 'normal'
                self.enemy = None
            else:
                self.enemy_attacks()

    def use_potion(self):
        self.inventory['Potion'][1] -= 1
        if self.inventory['Potion'][1] < 0:
            print("You are out of potions!")
            self.inventory['Potion'][1] = 0
        elif self.health == self.health_max:
            print("You are already at full health.")
        else:
            if self.state != 'fight':
                heal = int(self.health * self.inventory['Potion'][0]().percent)
                print("The potion healed you for %d life." % heal)
                self.health += heal
                if self.health >= self.health_max:
                    self.health = self.health_max
                    print("You are at max health!")
            else:
                heal = random.randint(self.level, int(self.health * self.inventory['Potion'][0]().percent))
                self.health += heal
                print("The potion healed you for %d life." % heal)
                if self.health >= self.health_max:
                    self.health = self.health_max
                    print("You are at max health!")
                self.enemy_attacks()

    def level_up(self):
        self.experience %= 10 * self.level
        health_gain = random.randint(self.level // 2, self.level)
        self.health_max += health_gain
        self.health += health_gain
        self.attack += random.randint(0, self.level // 2)
        self.defense += random.randint(0, self.level // 3)
        self.level += 1
        print("%s gained a level! %s is now level %s." % (self.name, self.name, self.level))

    def chest(self):
        print("You stumble upon a chest and open it.")
        if not random.randint(0, 1):
            treasure = random.choice([items.HealthPotion, items.Sword, items.Breastplate])
            typ = str(treasure().typ)
            print("You have found a %s." % treasure().name)
            if 'Weapon' in typ:
                if self.equipment['Weapon'] == items.Unarmed:
                    self.equipment['Weapon'] = treasure
                    print("You have equipped the %s." % treasure().name)
                else:
                    if typ not in self.inventory:
                        self.inventory[typ] = treasure
                    else:
                        self.inventory[typ][1] += 1
            elif 'Armor' in typ:
                if self.equipment['Armor'] == items.Unarmed:
                    self.equipment['Armor'] = treasure
                    print("You have equipped the %s." % treasure().name)
                else:
                    if typ not in self.inventory:
                        self.inventory[typ] = treasure
                    else:
                        self.inventory[typ][1] += 1
            elif typ not in self.inventory:
                self.inventory[typ] = [treasure, 1]
            else:
                self.inventory[typ][1] += 1
        else:
            print("You have found 100 gold!")
            self.gold += 100

    def loot(self):
        for item in self.enemy.loot:
            if item == "Gold":
                print("%s dropped %d gold." % (self.enemy.name, self.enemy.loot['Gold']))
                self.gold += self.enemy.loot['Gold']
            elif item == "Weapon":
                if not random.randint(0, int(self.enemy.loot['Weapon']().rarity - 1)):
                    print("%s dropped a %s." % (self.enemy.name, self.enemy.loot['Weapon']().name))
                    if self.equipment['Weapon'] == items.Unarmed:
                        self.equipment['Weapon'] = self.enemy.loot['Weapon']
                        print("The %s was equipped." % self.equipment['Weapon']().name)
                    elif 'Weapon' not in self.inventory:
                        self.inventory['Weapon'] = [self.enemy.loot['Weapon'], 1]
                    else:
                        self.inventory['Weapon'][1] += 1
            elif item == "Armor":
                if not random.randint(0, int(self.enemy.loot['Armor']().rarity - 1)):
                    print("%s dropped a %s." % (self.enemy.name, self.enemy.loot['Armor']().name))
                    if self.equipment['Armor'] == items.Naked:
                        self.equipment['Armor'] = self.enemy.loot['Armor']
                        print("The %s was equipped." % self.equipment['Armor']().name)
                    elif 'Armor' not in self.inventory:
                        self.inventory['Armor'] = [self.enemy.loot['Armor'], 1]
                    else:
                        self.inventory['Armor'][1] += 1
            elif item == "Potion":
                if not random.randint(0, int(self.enemy.loot['Potion']().rarity - 1)):
                    print("%s dropped a %s." % (self.enemy.name, self.enemy.loot['Potion']().name))
                    if 'Potion' not in self.inventory:
                        self.inventory['Potion'] = [self.enemy.loot['Potion'], 1]
                    else:
                        self.inventory['Potion'][1] += 1

    def enemy_attacks(self):
        if self.enemy.do_damage(self):
            print("%s was slaughtered by the %s!" % (self.name, self.enemy.name))
            game_quit()

    #            if bool(os.path.exists('save_files/'+str(self.name)+'.save')):
    #                cont = input("Would you like to load from the last save point?: ").lower()
    #                if cont == 'yes':
    #                    load_char(self.name)
    #            else:
    #                game_quit()

    def print_inventory(self):
        print("Equipment:")
        for key in self.equipment.keys():
            print(key + " - " + self.equipment[key]().name)
        print("Inventory:")
        for key in self.inventory.keys():
            print(key + " - " + self.inventory[key][0]().name + " " + str(self.inventory[key][1]))
        print("Gold: %d" % self.gold)

    def save(self):
        save_file = "save_files/{0}.save".format(str(self.name))
        player_dict = {'Player name': self.name,
                       'Level': self.level,
                       'Current health': self.health,
                       'Max health': self.health_max,
                       'Experience': self.experience,
                       'Attack': self.attack,
                       'Defense': self.defense,
                       'Speed': self.speed,
                       'Gold': self.gold,
                       'Equipment': self.equipment,
                       'Inventory': self.inventory}
        with open(save_file, 'w') as save_game:
            save_game.write(jsonpickle.encode(player_dict))
        print("Your game is now saved.")

    def equip(self, equipment):
        pass


# Define Parameters
Commands = \
    {'quit': game_quit, 'help': game_help, 'status': Player.status, 'rest': Player.rest, 'explore': Player.explore,
     'flee': Player.flee, 'attack': Player.attack, 'save': Player.save, 'inv': Player.print_inventory,
     'potion': Player.use_potion}
