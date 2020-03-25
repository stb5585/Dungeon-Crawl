###########################################
""" Character and enemy creator """

import os
import sys
import jsonpickle
import glob
import random

import items
import storyline

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
    player.equipment = dict(Weapon=items.Unarmed, Armor=items.Naked, Shield=items.NoShield)
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
        crit = 1
        if not random.randint(0, int(self.equipment['Weapon']().crit) - 1):
            crit = 2
        damage *= crit
        blk = False
        blk_amt = 0
        if not random.randint(0, int(enemy.equipment['Shield']().block) - 1):
            blk = True
            blk_amt = 1 / int(enemy.equipment['Shield']().block)
            damage *= (1 - blk_amt)
            damage = int(damage)
        if self.equipment['Weapon'] != items.Unarmed:
            damage += self.equipment['Weapon']().damage
        if self.equipment['Armor'] != items.Naked:
            damage = max(1, damage - enemy.equipment['Armor']().armor)

        # higher speed means slower character
        if not random.randint(0, enemy.speed - 1):
            print("%s evades %s's attack." % (enemy.name, self.name))
        else:
            if crit == 2:
                print("Critical Hit!")
            if blk:
                print("%s blocked %s\'s attack and mitigated %d percent of the damage." % (
                    enemy.name, self.name, int(blk_amt*100)))
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
        self.equipment = dict(Weapon=items.Unarmed, Armor=items.Naked, Shield=items.NoShield)
        self.inventory = dict(Gold=0)


class Goblin(Enemy):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(2, 4), attack=1, defense=2, speed=10,
                         exp=random.randint(2, 3))
        self.equipment['Weapon'] = items.BronzeSword
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
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(15, 25), Armor=self.equipment['Armor'])


class Skeleton(Enemy):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), attack=8, defense=5, speed=20,
                         exp=random.randint(4, 10))
        self.loot = dict(Gold=random.randint(10, 50), Potion=items.HealthPotion)


class Minotaur(Enemy):

    def __init__(self):
        super().__init__(name='Minotaur', health=random.randint(10, 15), attack=8, defense=4, speed=10,
                         exp=random.randint(10, 20))
        self.equipment['Weapon'] = items.BattleAxe
        self.loot = dict(Gold=random.randint(30, 75), Weapon=items.BattleAxe)


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

    def random_enemy(self):
        monsters = [Goblin(), GiantRat(), Bandit(), Skeleton(), Minotaur()]
        self.enemy = random.choice(monsters)

    def status(self):
        print("%s is level %s with %s experience points" % (self.name, self.level, self.experience))
        print("%s's health: %d/%d" % (self.name, self.health, self.health_max))
        print("%s has %s attack and has a %d percent chance to crit." % (self.name, self.attack +
                                                                         int(self.equipment['Weapon']().damage),
                                                                         int(1 / float(
                                                                             self.equipment['Weapon']().crit) *
                                                                             100)))
        print("%s has %s defense and a %d percent chance to evade attack." % (self.name, (self.defense + self.equipment[
            "Armor"]().armor), int((1 / self.speed) * 100)))
        print("%s has a %d percent chance to block %d percent of damage." % (self.name,
                                                                             int((1 / self.equipment['Shield']().block)
                                                                                 * 100),
                                                                             int((1 / self.equipment['Shield']().block)
                                                                                 * 100)))

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
            self.random_enemy()
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
                self.random_enemy()
                print("%s encounters a %s!" % (self.name, self.enemy.name))
                self.state = 'fight'
            elif not random.randint(0, 2):
                self.tired()
            elif not random.randint(0, 2):
                self.chest()

    def flee(self):
        if self.state != 'fight':
            print("There is nothing to run from.")
        else:
            if random.randint(1, self.health + 5) > random.randint(1, self.enemy.health):
                print("%s flees from the %s." % (self.name, self.enemy.name))
                self.state = 'normal'
            else:
                print("%s couldn't escape from the %s!" % (self.name, self.enemy.name))
                self.enemy_attacks()

    def attack(self):
        if self.state != 'fight':
            print("You are not in combat.")
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
        pot = True
        pot_list = []
        i = 0
        for item in self.inventory:
            if str(self.inventory[item][0]().typ) == 'Potion':
                pot_list.append((self.inventory[item][0]().name, i))
                i += 1
        if len(pot_list) == 0:
            print("You do not have any potions.")
            pot = False
        if pot:
            print("Which potion would you like to use?")
            use_pot = storyline.get_response(pot_list)
            if self.health == self.health_max:
                print("You are already at full health.")
            else:
                self.inventory[pot_list[use_pot][0]][1] -= 1
                if self.state != 'fight':
                    heal = int(self.health * self.inventory[pot_list[use_pot][0]][0]().percent)
                    print("The potion healed you for %d life." % heal)
                    self.health += heal
                    if self.health >= self.health_max:
                        self.health = self.health_max
                        print("You are at max health!")
                else:
                    heal = random.randint(self.level, int(self.health *
                                                          self.inventory[pot_list[use_pot][0]][0]().percent))
                    self.health += heal
                    print("The potion healed you for %d life." % heal)
                    if self.health >= self.health_max:
                        self.health = self.health_max
                        print("You are at max health!")
                    self.enemy_attacks()
                if self.inventory[pot_list[use_pot][0]][1] == 0:
                    del self.inventory[pot_list[use_pot][0]]

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
            treasure = items.random_item()
            typ = str(treasure().typ)
            print("You have found a %s." % treasure().name)
            if 'Weapon' in typ:
                if self.equipment['Weapon'] == items.Unarmed:
                    self.equipment['Weapon'] = treasure
                    print("You have equipped the %s." % treasure().name)
                else:
                    if typ not in self.inventory:
                        self.inventory[treasure().name] = [treasure, 1]
                    else:
                        self.inventory[treasure().name][1] += 1
            elif 'Armor' in typ:
                if self.equipment['Armor'] == items.Naked:
                    self.equipment['Armor'] = treasure
                    print("You have equipped the %s." % treasure().name)
                else:
                    if typ not in self.inventory:
                        self.inventory[treasure().name] = [treasure, 1]
                    else:
                        self.inventory[treasure().name][1] += 1
            elif 'Shield' in typ:
                if self.equipment['Shield'] == items.NoShield:
                    self.equipment['Shield'] = treasure
                    print("You have equipped the %s." % treasure().name)
                else:
                    if typ not in self.inventory:
                        self.inventory[treasure().name] = [treasure, 1]
                    else:
                        self.inventory[treasure().name][1] += 1
            elif typ not in self.inventory:
                self.inventory[treasure().name] = [treasure, 1]
            else:
                self.inventory[treasure().name][1] += 1
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
                    elif self.enemy.loot['Weapon']().name not in self.inventory:
                        self.inventory[self.enemy.loot['Weapon']().name] = [self.enemy.loot['Weapon'], 1]
                    else:
                        self.inventory[self.enemy.loot['Weapon']().name][1] += 1
            elif item == "Armor":
                if not random.randint(0, int(self.enemy.loot['Armor']().rarity - 1)):
                    print("%s dropped a %s." % (self.enemy.name, self.enemy.loot['Armor']().name))
                    if self.equipment['Armor'] == items.Naked:
                        self.equipment['Armor'] = self.enemy.loot['Armor']
                        print("The %s was equipped." % self.equipment['Armor']().name)
                    elif self.enemy.loot['Armor']().name not in self.inventory:
                        self.inventory[self.enemy.loot['Armor']().name] = [self.enemy.loot['Armor'], 1]
                    else:
                        self.inventory[self.enemy.loot['Armor']().name][1] += 1
            elif item == "Shield":
                if not random.randint(0, int(self.enemy.loot['Shield']().rarity - 1)):
                    print("%s dropped a %s." % (self.enemy.name, self.enemy.loot['Shield']().name))
                    if self.equipment['Shield'] == items.Naked:
                        self.equipment['Shield'] = self.enemy.loot['Shield']
                        print("The %s was equipped." % self.equipment['Shield']().name)
                    elif self.enemy.loot['Shield']().name not in self.inventory:
                        self.inventory[self.enemy.loot['Shield']().name] = [self.enemy.loot['Shield'], 1]
                    else:
                        self.inventory[self.enemy.loot['Shield']().name][1] += 1
            elif item == "Potion":
                if not random.randint(0, int(self.enemy.loot['Potion']().rarity - 1)):
                    print("%s dropped a %s." % (self.enemy.name, self.enemy.loot['Potion']().name))
                    if self.enemy.loot['Potion']().name not in self.inventory:
                        self.inventory[self.enemy.loot['Potion']().name] = [self.enemy.loot['Potion'], 1]
                    else:
                        self.inventory[self.enemy.loot['Potion']().name][1] += 1

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
        print("Weapon - " + self.equipment['Weapon']().name)
        print("Armor - " + self.equipment['Armor']().name)
        print("Shield - " + self.equipment['Shield']().name)
        print("Inventory:")
        for key in self.inventory:
            print(key + " " + str(self.inventory[key][1]))
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

    def equip(self):
        print("Which piece of equipment would you like to replace? ")
        option_list = [('Weapon', 0), ('Armor', 1), ('Shield', 2)]
        slot = storyline.get_response(option_list)
        inv_list = []
        print("You are currently equipped with %s." % self.equipment[option_list[slot][0]]().name)
        old = self.equipment[option_list[slot][0]]
        while True:
            i = 0
            for item in self.inventory:
                if str(self.inventory[item][0]().typ) == option_list[slot][0]:
                    inv_list.append((item, i))
                    i += 1
            if len(inv_list) == 0:
                print("You do not have any %ss to equip." % option_list[slot][0].lower())
                break
            else:
                print("Which %s would you like to equip? " % option_list[slot][0].lower())
                replace = storyline.get_response(inv_list)
                self.equipment[option_list[slot][0]] = self.inventory[inv_list[replace][0]][0]
                self.inventory[inv_list[replace][0]][1] -= 1
                if self.inventory[inv_list[replace][0]][1] == 0:
                    del self.inventory[inv_list[replace][0]]
                if old().name not in self.inventory:
                    self.inventory[old().name] = [old, 1]
                else:
                    self.inventory[old().name][1] += 1
                print("You are now equipped with %s." % self.equipment[option_list[slot][0]]().name)
                break


# Define Parameters
Commands = \
    {'quit': game_quit, 'help': game_help, 'status': Player.status, 'rest': Player.rest, 'explore': Player.explore,
     'flee': Player.flee, 'attack': Player.attack, 'save': Player.save, 'inv': Player.print_inventory,
     'potion': Player.use_potion, 'equip': Player.equip}
