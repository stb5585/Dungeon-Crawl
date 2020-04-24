###########################################
""" enemy manager """

# Imports
import random
import time

import items


# Functions
def random_enemy(level):
    monsters = {'1': [Chest(), LockedChest(), GreenSlime(), Goblin(), GiantRat(), Bandit(), Skeleton(), GiantHornet(),
                      Zombie(), GiantSpider(), TwistedDwarf()],
                '2': [Chest(), LockedChest(), Gnoll(), Minotaur(), GiantOwl(), Orc(), Vampire(), Direwolf(), RedSlime(),
                      GiantSnake(), GiantScorpion(), Warrior(), Harpy(), Naga(), Wererat()],
                '3': [Chest(), LockedChest(), Warrior(), Pseudodragon(), Ghoul(), Troll(), Direbear(), EvilCrusader(),
                      Ogre(), BlackSlime(), GoldenEagle(), PitViper(), Alligator(), Disciple(), Werewolf()],
                '4': [Chest(), LockedChest(), Troll(), Direbear(), Cockatrice(), Gargoyle(), Conjurer(), Chimera(),
                      Dragonkin(), Griffin(), DrowAssassin(), Cyborg(), DarkKnight()],
                '5': [Chest(), LockedChest(), DrowAssassin(), DarkKnight(), Golem(), ShadowSerpent(), Aboleth(),
                      Beholder(), Behemoth(), Basilisk(), Hydra(), Lich(), MindFlayer(), Warforged(), Wyrm(), Wyvern()]}
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
        return "#== {} ==#\n\nHealth: {}\n".format(self.name, self.health)

    def is_alive(self):
        return self.health > 0

    def weapon_damage(self, enemy, crit=1, off_crit=1, ignore=False, stun=False, dmg_mod=0):
        """
        Function that controls the character's basic attack during combat
        """
        blk = False
        off_blk = False
        blk_amt = 0
        off_blk_amt = 0
        dodge = False
        off_dodge = False
        off_damage = 0
        if self.equipment['Weapon']().typ == 'Natural':
            att_typ = self.equipment['Weapon']().name
            off_att_typ = self.equipment['Weapon']().name
        else:
            att_typ = 'damages'
            off_att_typ = 'damages'
        if ignore:
            dmg = max(1, (self.strength + self.equipment['Weapon']().damage + dmg_mod))
            damage = random.randint(dmg // 2, dmg)
            if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage + dmg_mod // 2))
                off_damage = random.randint(off_dmg // 4, off_dmg // 2)
        elif stun:
            dmg = max(1, (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor
                          + dmg_mod))
            damage = random.randint(dmg // 2, dmg)
            if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage
                                  - enemy.equipment['Armor']().armor + dmg_mod // 2))
                off_damage = random.randint(off_dmg // 4, off_dmg // 2)
        else:
            dmg = max(1,
                      (self.strength + self.equipment['Weapon']().damage - enemy.equipment['Armor']().armor + dmg_mod))
            damage = random.randint(dmg // 2, dmg)
            if enemy.equipment['OffHand']().subtyp == 'Shield':
                if not random.randint(0, int(enemy.equipment['OffHand']().mod)):
                    blk = True
                    blk_amt = (100 / enemy.equipment['OffHand']().mod +
                               random.randint(enemy.strength // 2, enemy.strength) -
                               random.randint(self.strength // 2, self.strength)) / 100
                    damage *= (1 - blk_amt)
            if random.randint(0, enemy.dex // 2) > random.randint(self.dex // 2, self.dex):
                print("%s evades %s's attack." % (enemy.name, self.name))
                time.sleep(0.25)
                dodge = True
            if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
                off_crit = 1
                off_dmg = max(1, (self.strength // 2 + self.equipment['OffHand']().damage -
                                  enemy.equipment['Armor']().armor + dmg_mod // 2))
                off_damage = random.randint(off_dmg // 4, off_dmg // 2)
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
                print("%s blocked %s\'s attack and mitigated %d percent of the damage." % (
                    enemy.name, self.name, int(blk_amt * 100)))
            if damage == 0:
                print("%s attacked %s but did 0 damage" % (self.name, enemy.name))
                time.sleep(0.25)
            else:
                print("%s %s %s for %s hit points." % (self.name, att_typ, enemy.name, damage))
                time.sleep(0.25)
            enemy.health -= damage
        if self.equipment['OffHand']().typ == 'Weapon' or self.equipment['OffHand']().typ == 'Natural':
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
                    print("%s blocked %s\'s attack and mitigated %d percent of the damage." % (
                        enemy.name, self.name, int(off_blk_amt * 100)))
                if off_damage == 0:
                    print("%s attacked %s but did 0 damage" % (self.name, enemy.name))
                    time.sleep(0.25)
                else:
                    print("%s %s %s for %s hit points." % (self.name, off_att_typ, enemy.name, off_damage))
                    time.sleep(0.25)
                enemy.health -= off_damage
            else:
                print("%s evades %s's off-hand attack." % (enemy.name, self.name))
                time.sleep(0.25)


# Natural weapons
class NaturalWeapon:

    def __init__(self, name, damage, crit, subtyp):
        self.name = name
        self.damage = damage
        self.crit = crit
        self.subtyp = subtyp
        self.typ = "Natural"


class RatBite(NaturalWeapon):

    def __init__(self):
        super().__init__(name="bites", damage=2, crit=9, subtyp='Natural')


class WolfClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=4, crit=6, subtyp='Natural')


class BearClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="mauls", damage=5, crit=7, subtyp='Natural')


class Stinger(NaturalWeapon):
    """
    Add a poison chance
    """
    def __init__(self):
        super().__init__(name="stings", damage=3, crit=4, subtyp='Natural')


class BirdClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="claws", damage=3, crit=5, subtyp='Natural')


class SnakeFang(NaturalWeapon):
    """
    Add a poison chance
    """
    def __init__(self):
        super().__init__(name="strikes", damage=3, crit=4, subtyp='Natural')


class AlligatorTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=8, crit=8, subtyp='Natural')


class LionPaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=5, crit=5, subtyp='Natural')


class Laser(NaturalWeapon):

    def __init__(self):
        super().__init__(name="zaps", damage=5, crit=3, subtyp='Natural')


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player to stone
    """
    def __init__(self):
        super().__init__(name="leers", damage=0, crit=5, subtyp='Natural')


class DragonClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="rakes", damage=6, crit=5, subtyp='Natural')


class DragonTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=18, crit=6, subtyp='Natural')


class NaturalArmor:

    def __init__(self, name, armor, subtyp):
        self.name = name
        self.armor = armor
        self.subtyp = subtyp
        self.typ = "Natural"


class AnimalHide(NaturalArmor):

    def __init__(self):
        super().__init__(name='Animal Hide', armor=2, subtyp='Natural')


class Carapace(NaturalArmor):

    def __init__(self):
        super().__init__(name='Carapace', armor=3, subtyp='Natural')


class StoneArmor(NaturalArmor):

    def __init__(self):
        super().__init__(name='Stone Armor', armor=4, subtyp='Natural')


class MetalPlating(NaturalArmor):

    def __init__(self):
        super().__init__(name='Metal Plating', armor=5, subtyp='Natural')


class DragonScale(NaturalArmor):

    def __init__(self):
        super().__init__(name='Dragon Scales', armor=6, subtyp='Natural')


# Enemies
class Chest(Enemy):

    def __init__(self):
        super().__init__(name='Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0, exp=0)
        self.loot = dict()
        self.lock = False


class LockedChest(Enemy):

    def __init__(self):
        super().__init__(name='Locked Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0,
                         exp=0)
        self.loot = dict()
        self.lock = True


class GreenSlime(Enemy):

    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(1, 6), mana=0, strength=6, intel=0, wisdom=15, con=8,
                         charisma=0, dex=4, exp=random.randint(1, 4))
        self.loot = dict(Gold=random.randint(1, 8))


class GiantRat(Enemy):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=0, strength=4, intel=0, wisdom=3, con=6,
                         charisma=0, dex=15, exp=random.randint(2, 4))
        self.equipment['Weapon'] = RatBite
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
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=0, strength=10, intel=0, wisdom=8, con=12,
                         charisma=0, dex=6, exp=random.randint(6, 10))
        self.equipment['Weapon'] = items.BronzeSword
        self.loot = dict(Gold=random.randint(10, 20), Potion=items.HealthPotion)


class GiantHornet(Enemy):

    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=0, strength=6, intel=0, wisdom=6,
                         con=6, charisma=0, dex=18, exp=random.randint(8, 14))
        self.equipment['Weapon'] = Stinger
        self.loot = dict(Gold=random.randint(6, 15))


class Zombie(Enemy):

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(8, 12), mana=0, strength=15, intel=0, wisdom=5, con=8,
                         charisma=0, dex=4, exp=random.randint(6, 12))
        self.loot = dict(Gold=random.randint(15, 30), Misc=items.Key)


class GiantSpider(Enemy):

    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=0, strength=12, intel=0, wisdom=10,
                         con=10, charisma=0, dex=12, exp=random.randint(10, 14))
        self.equipment['Weapon'] = Stinger
        self.equipment['Armor'] = Carapace
        self.loot = dict(Gold=random.randint(15, 30), Potion=items.ManaPotion)


class TwistedDwarf(Enemy):

    def __init__(self):
        super().__init__(name='Twisted Dwarf', health=random.randint(15, 19), mana=0, strength=14, intel=0, wisdom=10,
                         con=14, charisma=0, dex=12, exp=random.randint(15, 24))
        self.equipment['Weapon'] = items.Axe
        self.equipment['Armor'] = items.HideArmor
        self.loot = dict(Gold=random.randint(25, 40), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


# Level 1 Boss
class Minotaur(Enemy):

    def __init__(self):
        super().__init__(name='Minotaur', health=random.randint(20, 24), mana=0, strength=14, intel=0, wisdom=10,
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


class GiantSnake(Enemy):

    def __init__(self):
        super().__init__(name='Giant Snake', health=random.randint(13, 16), mana=0, strength=14, intel=0, wisdom=6,
                         con=14, charisma=0, dex=16, exp=random.randint(35, 50))
        self.equipment['Weapon'] = SnakeFang
        self.loot = dict(Gold=random.randint(35, 75))


class Orc(Enemy):

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(8, 12), mana=0, strength=10, intel=0, wisdom=5, con=10,
                         charisma=0, dex=14, exp=random.randint(20, 30))
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.PaddedArmor
        self.loot = dict(Gold=random.randint(20, 65), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class GiantOwl(Enemy):

    def __init__(self):
        super().__init__(name='Giant Owl', health=random.randint(8, 12), mana=0, strength=10, intel=0, wisdom=5, con=10,
                         charisma=0, dex=14, exp=random.randint(20, 30))
        self.equipment['Weapon'] = BirdClaw
        self.loot = dict(Gold=random.randint(20, 65))


class Vampire(Enemy):

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(10, 15), mana=0, strength=19, intel=0, wisdom=12, con=15,
                         charisma=0, dex=14, exp=random.randint(25, 40))
        self.loot = dict(Gold=random.randint(40, 90), Potion=items.GreatHealthPotion)


class Direwolf(Enemy):

    def __init__(self):
        super().__init__(name='Direwolf', health=random.randint(13, 16), mana=0, strength=17, intel=0, wisdom=6, con=14,
                         charisma=0, dex=16, exp=random.randint(35, 50))
        self.equipment['Weapon'] = WolfClaw
        self.equipment['Armor'] = AnimalHide
        self.loot = dict(Gold=random.randint(35, 75))


class Wererat(Enemy):

    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(12, 14), mana=0, strength=12, intel=0, wisdom=12, con=11,
                         charisma=0, dex=18, exp=random.randint(32, 44))
        self.equipment['Weapon'] = RatBite
        self.loot = dict(Gold=random.randint(40, 65))


class RedSlime(Enemy):

    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(8, 20), mana=0, strength=10, intel=0, wisdom=22,
                         con=12, charisma=0, dex=5, exp=random.randint(18, 55))
        self.loot = dict(Gold=random.randint(20, 120), Potion=items.SuperHealthPotion)


class GiantScorpion(Enemy):

    def __init__(self):
        super().__init__(name='Giant Scorpion', health=random.randint(13, 18), mana=0, strength=12, intel=0, wisdom=10,
                         con=12, charisma=0, dex=9, exp=random.randint(30, 55))
        self.equipment['Weapon'] = Stinger
        self.equipment['Armor'] = Carapace
        self.loot = dict(Gold=random.randint(40, 65))


class Warrior(Enemy):

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(12, 17), mana=0, strength=14, intel=0, wisdom=8, con=12,
                         charisma=0, dex=8, exp=random.randint(40, 60))
        self.equipment['Weapon'] = items.IronSword
        self.equipment['Armor'] = items.RingMail
        self.loot = dict(Gold=random.randint(25, 100), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Harpy(Enemy):

    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=0, strength=18, intel=13, wisdom=13,
                         con=14, charisma=0, dex=23, exp=random.randint(40, 65))
        self.equipment['Weapon'] = BirdClaw
        self.loot = dict(Gold=random.randint(50, 75))


class Naga(Enemy):

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=0, strength=15, intel=13, wisdom=15,
                         con=15, charisma=0, dex=17, exp=random.randint(42, 68))
        self.equipment['Weapon'] = items.Spear
        self.loot = dict(Gold=random.randint(55, 75), Weapon=self.equipment['Weapon'], Potion=items.GreatManaPotion)


# Level 2 Boss
class Pseudodragon(Enemy):

    def __init__(self):
        super().__init__(name='Pseudodragon', health=random.randint(40, 55), mana=0, strength=22, intel=12, wisdom=16,
                         con=20, charisma=0, dex=14, exp=random.randint(75, 125))
        self.equipment['Weapon'] = DragonClaw
        self.equipment['Armor'] = DragonScale
        self.loot = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)


class Ghoul(Enemy):

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=0, strength=23, intel=0, wisdom=8, con=24,
                         charisma=0, dex=12, exp=random.randint(60, 90))
        self.loot = dict(Gold=random.randint(35, 45), Potion=items.SuperHealthPotion)


class PitViper(Enemy):

    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=0, strength=17, intel=0, wisdom=8,
                         con=16, charisma=0, dex=18, exp=random.randint(65, 90))
        self.equipment['Weapon'] = SnakeFang
        self.loot = dict(Gold=random.randint(50, 85))


class Disciple(Enemy):

    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=0, strength=16, intel=17, wisdom=15,
                         con=16, charisma=0, dex=16, exp=random.randint(60, 90))
        self.equipment['Weapon'] = items.SteelDagger
        self.equipment['Armor'] = items.SilverCloak
        self.loot = dict(Gold=random.randint(55, 95), Potion=items.SuperManaPotion)


class Werewolf(Enemy):

    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(45, 55), mana=0, strength=18, intel=0, wisdom=10,
                         con=20, charisma=0, dex=18, exp=random.randint(70, 100))
        self.equipment['Weapon'] = WolfClaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = WolfClaw
        self.loot = dict(Gold=random.randint(45, 55))


class BlackSlime(Enemy):

    def __init__(self):
        super().__init__(name='Black Slime', health=random.randint(25, 60), mana=0, strength=13, intel=0, wisdom=30,
                         con=15, charisma=0, dex=6, exp=random.randint(35, 110))
        self.loot = dict(Gold=random.randint(30, 180), Potion=items.Elixir)


class Ogre(Enemy):

    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=0, strength=20, intel=10, wisdom=14, con=20,
                         charisma=0, dex=14, exp=random.randint(65, 95))
        self.equipment['Weapon'] = items.IronHammer
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(50, 75), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Alligator(Enemy):

    def __init__(self):
        super().__init__(name='Alligator', health=random.randint(60, 75), mana=0, strength=19, intel=0, wisdom=7,
                         con=20, charisma=0, dex=15, exp=random.randint(70, 100))
        self.equipment['Weapon'] = AlligatorTail
        self.loot = dict(Gold=random.randint(40, 50))


class Troll(Enemy):

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=0, strength=19, intel=0, wisdom=8, con=24,
                         charisma=0, dex=15, exp=random.randint(75, 110))
        self.equipment['Weapon'] = items.GreatAxe
        self.equipment['Armor'] = items.LeatherArmor
        self.loot = dict(Gold=random.randint(35, 45), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'])


class Direbear(Enemy):

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=0, strength=23, intel=0, wisdom=6, con=26,
                         charisma=0, dex=18, exp=random.randint(60, 110))
        self.equipment['Weapon'] = BearClaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = BearClaw
        self.loot = dict(Gold=random.randint(45, 60))


class GoldenEagle(Enemy):

    def __init__(self):
        super().__init__(name='Golden Eagle', health=random.randint(40, 50), mana=0, strength=16, intel=15, wisdom=15,
                         con=17, charisma=0, dex=25, exp=random.randint(80, 120))
        self.equipment['Weapon'] = BirdClaw
        self.equipment['OffHand'] = BirdClaw
        self.loot = dict(Gold=random.randint(50, 75))


class EvilCrusader(Enemy):

    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=0, strength=18, intel=18, wisdom=17,
                         con=26, charisma=0, dex=14, exp=random.randint(90, 125))
        self.equipment['Weapon'] = items.SteelSword
        self.equipment['Armor'] = items.Splint
        self.equipment['OffHand'] = items.KiteShield
        self.loot = dict(Gold=random.randint(65, 90), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])


# Level 3 Boss
class Cockatrice(Enemy):

    def __init__(self):
        super().__init__(name='Cockatrice', health=random.randint(60, 75), mana=0, strength=23, intel=0, wisdom=15,
                         con=16, charisma=0, dex=20, exp=random.randint(150, 175))
        self.equipment['Weapon'] = BirdClaw
        self.equipment['OffHand'] = BirdClaw
        self.loot = dict(Gold=random.randint(120, 150), Potion=items.MasterHealthPotion)


class Gargoyle(Enemy):

    def __init__(self):
        super().__init__(name='Gargoyle', health=random.randint(35, 55), mana=0, strength=23, intel=10, wisdom=0,
                         con=18, charisma=0, dex=21, exp=random.randint(110, 130))
        self.equipment['Weapon'] = BirdClaw
        self.equipment['Armor'] = StoneArmor
        self.loot = dict(Gold=random.randint(75, 125))


class Conjurer(Enemy):

    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(30, 45), mana=0, strength=12, intel=22, wisdom=18,
                         con=14, charisma=0, dex=13, exp=random.randint(115, 140))
        self.equipment['Weapon'] = items.SerpentStaff
        self.equipment['Armor'] = items.GoldCloak
        self.loot = dict(Gold=random.randint(110, 145), Potion=items.MasterManaPotion)


class Chimera(Enemy):

    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(40, 75), mana=0, strength=23, intel=14, wisdom=16,
                         con=20, charisma=0, dex=14, exp=random.randint(130, 180))
        self.equipment['Weapon'] = LionPaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = BirdClaw
        self.loot = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)


class Dragonkin(Enemy):

    def __init__(self):
        super().__init__(name='Dragonkin', health=random.randint(50, 75), mana=0, strength=23, intel=10, wisdom=18,
                         con=20, charisma=0, dex=20, exp=random.randint(150, 280))
        self.equipment['Weapon'] = items.Halberd
        self.equipment['Armor'] = items.Breastplate
        self.loot = dict(Gold=random.randint(150, 300), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         Potion=items.Elixir)


class Griffin(Enemy):

    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(60, 80), mana=0, strength=23, intel=10, wisdom=18,
                         con=18, charisma=0, dex=25, exp=random.randint(140, 250))
        self.equipment['Weapon'] = LionPaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = BearClaw
        self.loot = dict(Gold=random.randint(140, 280))


class DrowAssassin(Enemy):

    def __init__(self):
        super().__init__(name='Drow Assassin', health=random.randint(45, 65), mana=0, strength=15, intel=16, wisdom=15,
                         con=14, charisma=0, dex=22, exp=random.randint(180, 280))
        self.equipment['Weapon'] = items.Carnwennan
        self.equipment['Armor'] = items.Studded
        self.equipment['OffHand'] = items.AdamantiteDagger
        self.loot = dict(Gold=random.randint(160, 250), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])


class Cyborg(Enemy):

    def __init__(self):
        super().__init__(name='Cyborg', health=random.randint(70, 95), mana=0, strength=28, intel=13, wisdom=0, con=18,
                         charisma=0, dex=14, exp=random.randint(190, 300))
        self.equipment['Weapon'] = Laser
        self.equipment['Armor'] = MetalPlating
        self.loot = dict(Gold=random.randint(200, 300))


class DarkKnight(Enemy):

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(60, 80), mana=0, strength=20, intel=15, wisdom=12,
                         con=21, charisma=0, dex=17, exp=random.randint(200, 350))
        self.equipment['Weapon'] = items.Gungnir
        self.equipment['Armor'] = items.PlateMail
        self.equipment['OffHand'] = items.TowerShield
        self.loot = dict(Gold=random.randint(300, 420), Weapon=self.equipment['Weapon'], Armor=self.equipment['Armor'],
                         OffHand=self.equipment['OffHand'])


# Level 4 boss
class Golem(Enemy):

    def __init__(self):
        super().__init__(name='Golem', health=random.randint(150, 200), mana=0, strength=27, intel=10, wisdom=18,
                         con=28, charisma=0, dex=20, exp=random.randint(300, 500))
        self.equipment['Weapon'] = Laser
        self.equipment['Armor'] = StoneArmor
        self.equipment['OffHand'] = Laser
        self.loot = dict(Gold=random.randint(400, 600), Potion=items.Aegis)


class ShadowSerpent(Enemy):

    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=0, strength=24, intel=10,
                         wisdom=15, con=22, charisma=0, dex=23, exp=random.randint(280, 490))
        self.equipment['Weapon'] = SnakeFang
        self.loot = dict(Gold=random.randint(280, 485), Potion=items.Megalixir)


class Aboleth(Enemy):

    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(110, 500), mana=0, strength=18, intel=20, wisdom=50,
                         con=25, charisma=0, dex=8, exp=random.randint(150, 630))
        self.loot = dict(Gold=random.randint(130, 750), Potion=items.AardBeing)


class Beholder(Enemy):

    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=0, strength=25, intel=40, wisdom=35,
                         con=28, charisma=0, dex=20, exp=random.randint(300, 600))
        self.equipment['Weapon'] = Gaze
        self.loot = dict(Gold=random.randint(300, 500), OffHand=items.MedusaShield)


class Behemoth(Enemy):

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=0, strength=33, intel=25, wisdom=20,
                         con=30, charisma=0, dex=18, exp=random.randint(420, 650))
        self.equipment['Weapon'] = LionPaw
        self.equipment['Armor'] = AnimalHide
        self.equipment['OffHand'] = LionPaw
        self.loot = dict(Gold=random.randint(400, 550), Potion=items.Jarnbjorn)


class Lich(Enemy):

    def __init__(self):
        super().__init__(name='Lich', health=random.randint(160, 240), mana=0, strength=20, intel=35, wisdom=40,
                         con=20, charisma=0, dex=22, exp=random.randint(380, 620))
        self.equipment['Armor'] = items.MerlinRobe
        self.equipment['OffHand'] = items.Necronomicon
        self.loot = dict(Gold=random.randint(400, 530), Armor=self.equipment['Armor'], OffHand=self.equipment[
            'OffHand'])


class Basilisk(Enemy):

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(180, 275), mana=0, strength=29, intel=26, wisdom=30,
                         con=27, charisma=0, dex=20, exp=random.randint(430, 600))
        self.equipment['Weapon'] = Gaze
        self.equipment['Armor'] = StoneArmor
        self.loot = dict(Gold=random.randint(380, 520), Potion=items.PrincessGuard)


class MindFlayer(Enemy):

    def __init__(self):
        super().__init__(name='Mind Flayer', health=random.randint(190, 285), mana=0, strength=22, intel=40, wisdom=35,
                         con=25, charisma=0, dex=18, exp=random.randint(390, 550))
        self.equipment['Weapon'] = items.DragonStaff
        self.equipment['OffHand'] = items.Magus
        self.loot = dict(Gold=random.randint(450, 600), Weapon=self.equipment['Weapon'], OffHand=self.equipment[
            'OffHand'])


class Warforged(Enemy):

    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=0, strength=30, intel=20, wisdom=0,
                         con=33, charisma=0, dex=10, exp=random.randint(380, 580))
        self.equipment['Weapon'] = items.Skullcrusher
        self.equipment['Armor'] = StoneArmor
        self.loot = dict(Gold=random.randint(380, 490), Weapon=self.equipment['Weapon'])


class Wyrm(Enemy):

    def __init__(self):
        super().__init__(name='Wyrm', health=random.randint(220, 300), mana=0, strength=28, intel=28, wisdom=30,
                         con=28, charisma=0, dex=18, exp=random.randint(420, 580))
        self.equipment['Weapon'] = DragonTail
        self.equipment['Armor'] = DragonScale
        self.loot = dict(Gold=random.randint(650, 830), Weapon=items.Mjolnir)


class Hydra(Enemy):

    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(200, 275), mana=0, strength=31, intel=30, wisdom=26,
                         con=28, charisma=0, dex=18, exp=random.randint(400, 550))
        self.equipment['Weapon'] = DragonClaw
        self.equipment['Armor'] = DragonScale
        self.loot = dict(Gold=random.randint(400, 550), Weapon=items.Excalibur)


class Wyvern(Enemy):

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(220, 300), mana=0, strength=30, intel=33, wisdom=24,
                         con=30, charisma=0, dex=33, exp=random.randint(450, 600))
        self.equipment['Weapon'] = DragonClaw
        self.equipment['Armor'] = DragonScale
        self.equipment['OffHand'] = DragonClaw
        self.loot = dict(Gold=random.randint(420, 570), Armor=items.DragonHide)


# Level 5 Boss
class RedDragon(Enemy):

    def __init__(self):
        super().__init__(name='Red Dragon', health=random.randint(500, 700), mana=0, strength=35, intel=28, wisdom=35,
                         con=30, charisma=0, dex=15, exp=random.randint(800, 1200))
        self.equipment['Weapon'] = DragonTail
        self.equipment['Armor'] = DragonScale
        self.equipment['OffHand'] = DragonClaw
        self.loot = dict(Gold=random.randint(1500, 3000), Armor=items.Genji)
