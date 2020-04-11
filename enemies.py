###########################################
""" enemy manager """

# Imports
import random
import time

import items


# Functions
def random_enemy(level):
    monsters = {'1': [Chest(), Slime(), Goblin(), GiantRat(), Bandit(), Skeleton(), Zombie(), GiantSpider()],
                '2': [Chest(), Gnoll(), Zombie(), Minotaur(), Orc(), Vampire(), Direwolf(), Warrior(), Harpy(), Naga()],
                '3': [Chest(), Warrior(), Pseudodragon(), Ghoul(), Troll(), Direbear(), EvilCrusader(), Ogre()],
                '4': [Chest(), Cockatrice(), Chimera(), Dragonkin(), Griffon(), DarkKnight()],
                '5': [Chest(), Golem(), Beholder(), Behemoth(), Basilisk(), Hydra(), Wyvern()]}
    enemy = random.choice(monsters[level])

    return enemy


class Enemy:

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        self.name = name
        self.health = health + con
        self.mana = mana + intel
        self.strength = strength
        self.intel = intel
        self.wisdom = wisdom
        self.con = con
        self.charisma = charisma
        self.dex = dex
        self.experience = exp
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand)
        self.inventory = {}

    def __str__(self):
        return "{}\n=====\nHealth: {}\n".format(self.name, self.health)

    def is_alive(self):
        return self.health > 0

    def do_damage(self, enemy):
        dmg = max(1, (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor))
        damage = random.randint(dmg // 2, dmg)
        crit = 1
        if not random.randint(0, int(self.equipment['Weapon']().crit)):
            crit = 2
        damage *= crit
        blk = False
        blk_amt = 0
        if enemy.equipment['OffHand']().subtyp == 'Shield':
            if not random.randint(0, int(enemy.equipment['OffHand']().mod)):
                blk = True
                blk_amt = 1 / (int(enemy.equipment['OffHand']().mod) + 1)
                damage *= (1 - blk_amt)
        damage = int(damage)
        damage += self.equipment['Weapon']().damage
        damage = max(0, damage - enemy.equipment['Armor']().armor)
        if random.randint(0, enemy.dex // 2) > random.randint(self.dex // 2, self.dex):
            print("%s evades %s's attack." % (enemy.name, self.name))
            time.sleep(0.25)
        else:
            if crit == 2:
                print("Critical Hit!")
                time.sleep(0.25)
            if blk:
                print("%s blocked %s\'s attack and mitigated %d percent of the damage." % (
                    enemy.name, self.name, int(blk_amt * 100)))
            if damage == 0:
                print("%s attacked %s but did 0 damage" % (self.name, enemy.name))
                time.sleep(0.25)
            else:
                print("%s damages %s for %s hit points." % (self.name, enemy.name, damage))
                time.sleep(0.25)
            enemy.health -= damage

        return enemy.health <= 0


class Chest(Enemy):

    def __init__(self):
        super().__init__(name='Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0, exp=0)
        self.loot = dict()


class Slime(Enemy):

    def __init__(self):
        super().__init__(name='Slime', health=random.randint(1, 6), mana=0, strength=6, intel=0, wisdom=15, con=8,
                         charisma=0, dex=4, exp=random.randint(1, 4))
        self.loot = dict(Gold=random.randint(1, 8))


class GiantRat(Enemy):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(1, 3), mana=0, strength=4, intel=0, wisdom=3, con=6,
                         charisma=0, dex=15, exp=random.randint(2, 4))
        self.loot = dict(Gold=random.randint(1, 5))


class Goblin(Enemy):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(2, 4), mana=0, strength=6, intel=0, wisdom=2, con=8,
                         charisma=0, dex=8, exp=random.randint(2, 6))
        self.equipment['Weapon'] = items.BronzeSword
        self.loot = dict(Gold=random.randint(4, 10), Weapon=self.equipment['Weapon'])


class Bandit(Enemy):

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=0, strength=8, intel=0, wisdom=5, con=8,
                         charisma=0, dex=10, exp=random.randint(3, 8))
        self.equipment['Weapon'] = items.BronzeDagger
        self.equipment['Armor'] = items.PaddedArmor
        self.loot = dict(Gold=random.randint(15, 25), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Skeleton(Enemy):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=0, strength=12, intel=0, wisdom=8, con=12,
                         charisma=0, dex=6, exp=random.randint(6, 10))
        self.loot = dict(Gold=random.randint(10, 20), Potion=items.HealthPotion)


class Zombie(Enemy):

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(8, 12), mana=0, strength=13, intel=0, wisdom=5, con=8,
                         charisma=0, dex=4, exp=random.randint(6, 12))
        self.loot = dict(Gold=random.randint(15, 30))


class GiantSpider(Enemy):

    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=0, strength=12, intel=0, wisdom=4,
                         con=10, charisma=0, dex=12, exp=random.randint(10, 14))
        self.loot = dict(Gold=random.randint(15, 30), Potion=items.ManaPotion)


# Level 1 Boss
class Minotaur(Enemy):

    def __init__(self):
        super().__init__(name='Minotaur', health=random.randint(15, 19), mana=0, strength=14, intel=0, wisdom=10,
                         con=14, charisma=0, dex=12, exp=random.randint(30, 60))
        self.equipment['Weapon'] = items.BattleAxe
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(30, 75), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Gnoll(Enemy):

    def __init__(self):
        super().__init__(name='Gnoll', health=random.randint(10, 14), mana=0, strength=12, intel=0, wisdom=5, con=8,
                         charisma=0, dex=16, exp=random.randint(20, 35))
        self.equipment['Weapon'] = items.Spear
        self.equipment['Armor'] = items.PaddedArmor
        self.loot = dict(Gold=random.randint(30, 60), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Orc(Enemy):

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(8, 12), mana=0, strength=10, intel=0, wisdom=5, con=10,
                         charisma=0, dex=14, exp=random.randint(20, 30))
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.PaddedArmor
        self.loot = dict(Gold=random.randint(20, 65), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Vampire(Enemy):

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(10, 15), mana=0, strength=16, intel=0, wisdom=12, con=15,
                         charisma=0, dex=14, exp=random.randint(25, 40))
        self.loot = dict(Gold=random.randint(40, 90), Potion=items.GreatHealthPotion)


class Direwolf(Enemy):

    def __init__(self):
        super().__init__(name='Direwolf', health=random.randint(13, 16), mana=0, strength=17, intel=0, wisdom=6, con=14,
                         charisma=0, dex=16, exp=random.randint(35, 50))
        self.loot = dict(Gold=random.randint(35, 75))


class Warrior(Enemy):

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(10, 15), mana=0, strength=14, intel=0, wisdom=8, con=12,
                         charisma=0, dex=8, exp=random.randint(40, 60))
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.RingMail
        self.loot = dict(Gold=random.randint(25, 100), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Harpy(Enemy):

    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=0, strength=18, intel=13, wisdom=13,
                         con=14, charisma=0, dex=23, exp=random.randint(40, 65))
        self.loot = dict(Gold=random.randint(50, 75), Potion=items.SuperHealthPotion)


class Naga(Enemy):

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=0, strength=15, intel=13, wisdom=15,
                         con=15, charisma=0, dex=17, exp=random.randint(42, 68))
        self.equipment['Weapon'] = items.IronshodStaff
        self.loot = dict(Gold=random.randint(55, 75), Weapon=self.equipment['Weapon'])


# Level 2 Boss
class Pseudodragon(Enemy):

    def __init__(self):
        super().__init__(name='Pseudodragon', health=random.randint(38, 50), mana=0, strength=20, intel=12, wisdom=16,
                         con=18, charisma=0, dex=8, exp=random.randint(75, 125))
        self.loot = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)


class Ghoul(Enemy):

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=0, strength=20, intel=0, wisdom=8, con=24,
                         charisma=0, dex=12, exp=random.randint(60, 90))
        self.loot = dict(Gold=random.randint(35, 45), Potion=items.SuperHealthPotion)


class Werewolf(Enemy):

    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(45, 55), mana=0, strength=23, intel=0, wisdom=10,
                         con=20, charisma=0, dex=18, exp=random.randint(70, 100))
        self.loot = dict(Gold=random.randint(45, 55))


class Ogre(Enemy):

    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=0, strength=20, intel=10, wisdom=14, con=20,
                         charisma=0, dex=14, exp=random.randint(65, 95))
        self.equipment['Weapon'] = items.IronHammer
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(50, 75), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Troll(Enemy):

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=0, strength=19, intel=0, wisdom=8, con=24,
                         charisma=0, dex=15, exp=random.randint(75, 110))
        self.equipment['Weapon'] = items.GreatAxe
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(35, 45), Weapon=items.GreatAxe, Armor=self.equipment['Armor'])


class Direbear(Enemy):

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=0, strength=23, intel=0, wisdom=6, con=26,
                         charisma=0, dex=18, exp=random.randint(60, 110))
        self.loot = dict(Gold=random.randint(45, 60))


class EvilCrusader(Enemy):

    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=0, strength=18, intel=18, wisdom=25,
                         con=26, charisma=0, dex=14, exp=random.randint(90, 125))
        self.equipment['Weapon'] = items.SteelSword
        self.equipment['Armor'] = items.Splint
        self.equipment['OffHand'] = items.TowerShield
        self.loot = dict(Gold=random.randint(65, 90), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])


# Level 3 Boss
class Cockatrice(Enemy):

    def __init__(self):
        super().__init__(name='Cockatrice', health=random.randint(60, 75), mana=0, strength=21, intel=0, wisdom=15,
                         con=16, charisma=0, dex=20, exp=random.randint(150, 175))
        self.loot = dict(Gold=random.randint(35, 45), Potion=items.MasterHealthPotion)


class Chimera(Enemy):

    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(40, 75), mana=0, strength=23, intel=14, wisdom=16,
                         con=20, charisma=0, dex=14, exp=random.randint(130, 180))
        self.loot = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)


class Dragonkin(Enemy):

    def __init__(self):
        super().__init__(name='Dragonkin', health=random.randint(50, 75), mana=0, strength=23, intel=10, wisdom=18,
                         con=20, charisma=0, dex=20, exp=random.randint(250, 500))
        self.equipment['Weapon'] = items.Halberd
        self.equipment['Armor'] = items.Breastplate
        self.loot = dict(Gold=random.randint(350, 500), Weapon=items.Halberd, Armor=self.equipment['Armor'])


class Griffon(Enemy):

    def __init__(self):
        super().__init__(name='Griffon', health=random.randint(60, 80), mana=0, strength=23, intel=10, wisdom=18,
                         con=18, charisma=0, dex=25, exp=random.randint(280, 420))
        self.loot = dict(Gold=random.randint(350, 500))


class DarkKnight(Enemy):

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(60, 80), mana=0, strength=22, intel=15, wisdom=12,
                         con=21, charisma=0, dex=17, exp=random.randint(300, 450))
        self.equipment['Weapon'] = items.AdamantiteSword
        self.equipment['Armor'] = items.PlateMail
        self.equipment['OffHand'] = items.TowerShield
        self.loot = dict(Gold=random.randint(400, 540), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])


# Level 4 boss
class Golem(Enemy):

    def __init__(self):
        super().__init__(name='Golem', health=random.randint(150, 200), mana=0, strength=27, intel=10, wisdom=18,
                         con=28, charisma=0, dex=20, exp=random.randint(300, 500))
        self.loot = dict(Gold=random.randint(400, 600))


class Beholder(Enemy):

    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=0, strength=25, intel=40, wisdom=35,
                         con=28, charisma=0, dex=20, exp=random.randint(300, 600))
        self.loot = dict(Gold=random.randint(300, 500), OffHand=items.MedusaShield)


class Behemoth(Enemy):

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=0, strength=33, intel=25, wisdom=20,
                         con=30, charisma=0, dex=18, exp=random.randint(420, 650))
        self.loot = dict(Gold=random.randint(400, 550), Potion=items.Megalixir)


class Basilisk(Enemy):

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(180, 275), mana=0, strength=29, intel=33, wisdom=30,
                         con=27, charisma=0, dex=20, exp=random.randint(430, 600))
        self.loot = dict(Gold=random.randint(380, 520), Potion=items.MasterManaPotion)


class Hydra(Enemy):

    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(200, 275), mana=0, strength=31, intel=30, wisdom=26,
                         con=28, charisma=0, dex=18, exp=random.randint(400, 550))
        self.loot = dict(Gold=random.randint(400, 550))


class Wyvern(Enemy):

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(220, 300), mana=0, strength=30, intel=33, wisdom=24,
                         con=30, charisma=0, dex=33, exp=random.randint(450, 600))
        self.loot = dict(Gold=random.randint(420, 570))


# Level 5 Boss
class RedDragon(Enemy):

    def __init__(self):
        super().__init__(name='Red Dragon', health=random.randint(500, 700), mana=0, strength=35, intel=28, wisdom=35,
                         con=30, charisma=0, dex=15, exp=random.randint(800, 1200))
        self.loot = dict(Gold=random.randint(1500, 3000), Armor=items.Genji, Potion=items.AardBeing)
