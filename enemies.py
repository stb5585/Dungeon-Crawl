###########################################
""" enemy manager """

# Imports
import random

import character
import items


# Functions
def random_enemy(level):
    monsters = {'1': [Goblin(), GiantRat(), Bandit(), Skeleton(), Zombie(), Minotaur()],
                '2': [Zombie(), Minotaur(), Orc(), Vampire(), Warrior(), Pseudodragon()],
                }
    enemy = random.choice(monsters[level])

    return enemy


class Enemy(character.Character):

    def __init__(self, name, health, mana, attack, defense, speed, exp):
        super().__init__()
        self.name = name
        self.health = health
        self.mana = mana
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.experience = exp
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand)
        self.inventory = {}

    def is_alive(self):
        return self.health > 0


class Chest(Enemy):

    def __init__(self):
        super().__init__(name='Chest', health=1, mana=0, attack=0, defense=0, speed=99, exp=0)
        self.loot = dict()


class Slime(Enemy):

    def __init__(self):
        super().__init__(name='Slime', health=random.randint(1, 2), mana=0, attack=1, defense=8, speed=10,
                         exp=random.randint(1, 2))
        self.loot = dict(Gold=random.randint(1, 3))


class GiantRat(Enemy):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(1, 3), mana=0, attack=2, defense=1, speed=5,
                         exp=random.randint(1, 2))
        self.loot = dict(Gold=random.randint(1, 5))


class Goblin(Enemy):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(2, 4), mana=0, attack=1, defense=2, speed=10,
                         exp=random.randint(2, 3))
        self.equipment['Weapon'] = items.BronzeSword
        self.loot = dict(Gold=random.randint(4, 10), Weapon=self.equipment['Weapon'])


class Bandit(Enemy):

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=0, attack=6, defense=1, speed=8,
                         exp=random.randint(3, 8))
        self.equipment['Weapon'] = items.BronzeSword
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(15, 25), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Skeleton(Enemy):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=0, attack=10, defense=5, speed=20,
                         exp=random.randint(6, 10))
        self.loot = dict(Gold=random.randint(10, 20), Potion=items.HealthPotion)


class Zombie(Enemy):

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(8, 12), mana=0, attack=8, defense=8, speed=20,
                         exp=random.randint(6, 12))
        self.loot = dict(Gold=random.randint(15, 30))


class Minotaur(Enemy):

    def __init__(self):
        super().__init__(name='Minotaur', health=random.randint(10, 15), mana=0, attack=8, defense=4, speed=10,
                         exp=random.randint(10, 20))
        self.equipment['Weapon'] = items.BattleAxe
        self.loot = dict(Gold=random.randint(30, 75), Weapon=self.equipment['Weapon'])


class Orc(Enemy):

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(8, 12), mana=0, attack=8, defense=4, speed=6,
                         exp=random.randint(12, 25))
        self.equipment['Weapon'] = items.IronSword
        self.loot = dict(Gold=random.randint(20, 65), Weapon=self.equipment['Weapon'])


class Vampire(Enemy):

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(10, 15), mana=0, attack=16, defense=6, speed=6,
                         exp=random.randint(15, 30))
        self.loot = dict(Gold=random.randint(40, 90), Potion=items.SuperHealthPotion)


class Warrior(Enemy):

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(10, 15), mana=0, attack=8, defense=4, speed=10,
                         exp=random.randint(18, 32))
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.ChainMail
        self.equipment['OffHand'] = items.IronShield
        self.loot = dict(Gold=random.randint(25, 100), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])


class Pseudodragon(Enemy):

    def __init__(self):
        super().__init__(name='Pseudodragon', health=random.randint(25, 35), mana=0, attack=20, defense=8, speed=12,
                         exp=random.randint(30, 50))
        self.loot = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)
