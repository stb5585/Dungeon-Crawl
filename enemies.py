###########################################
""" enemy manager """

# Imports
import random
import time

import items
import spells


# Functions
def random_enemy(level):
    monsters = {'1': [GreenSlime(), Goblin(), GiantRat(), Quasit(), Bandit(), Skeleton(), GiantHornet(), Zombie(),
                      GiantSpider(), Panther(), TwistedDwarf()],
                '2': [TwistedDwarf(), Gnoll(), Minotaur(), GiantOwl(), Orc(), Vampire(), Direwolf(), RedSlime(),
                      GiantSnake(), GiantScorpion(), Warrior(), Harpy(), Naga(), Wererat()],
                '3': [Warrior(), Pseudodragon(), Ghoul(), Troll(), Direbear(), EvilCrusader(), Ogre(), BlackSlime(),
                      GoldenEagle(), PitViper(), Alligator(), Disciple(), Werewolf()],
                '4': [BrownSlime(), Troll(), Direbear(), Cockatrice(), Gargoyle(), Conjurer(), Chimera(), Dragonkin(),
                      Griffin(), DrowAssassin(), Cyborg(), DarkKnight()],
                '5': [DrowAssassin(), DarkKnight(), Golem(), ShadowSerpent(), Aboleth(), Beholder(), Behemoth(),
                      Basilisk(), Hydra(), Lich(), MindFlayer(), Warforged(), Wyrm(), Wyvern()]}

    # 5% to randomly get a chest instead of a monster
    if not random.randint(0, 19):
        # 20% chance (1% overall) to get a locked chest
        if not random.randint(0, 4):
            enemy = LockedChest(level)
        else:
            enemy = Chest(level)
    else:
        enemy = random.choice(monsters[level])

    return enemy  # Test()


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
        self.resistance = {'Fire': 0.,
                           'Ice': 0.,
                           'Electric': 0.,
                           'Water': 0.,
                           'Earth': 0.,
                           'Wind': 0.,
                           'Shadow': 0.,
                           'Death': 0.,
                           'Holy': 0.,
                           'Poison': 0.,
                           'Physical': 0.}
        self.flying = False


class Enemy(Character):

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__()
        self.name = name
        self.health = health + con
        self.health_max = health + con
        self.mana = mana + intel
        self.mana_max = mana + intel
        self.strength = strength
        self.intel = intel
        self.wisdom = wisdom
        self.con = con
        self.charisma = charisma
        self.dex = dex
        self.experience = exp
        self.gold = 0

    def __str__(self, inspect=False):
        if inspect:
            return self.inspect()
        else:
            return "Enemy: {}  Health: {}/{}  Mana: {}/{}".format(self.name, self.health, self.health_max, self.mana,
                                                                  self.mana_max)

    def inspect(self):
        pass

    def is_alive(self):
        return self.health > 0

    def check_mod(self, mod, typ=None, luck_factor=1):
        if mod == 'weapon':
            weapon_mod = self.strength
            if not self.status_effects['Disarm']:
                weapon_mod += self.equipment['Weapon']().damage
            if 'Physical Damage' in self.equipment['Ring']().mod:
                weapon_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            weapon_mod += self.status_effects['Attack'][2]
            return weapon_mod
        elif mod == 'off':
            try:
                off_mod = (self.strength + self.equipment['OffHand']().damage) // 2
                if 'Physical Damage' in self.equipment['Ring']().mod:
                    off_mod += (int(self.equipment['Ring']().mod.split(' ')[0]) // 2)
                off_mod += self.status_effects['Attack'][2]
                return off_mod
            except AttributeError:
                return 0
        elif mod == 'armor':
            armor_mod = self.equipment['Armor']().armor
            if 'Physical Defense' in self.equipment['Ring']().mod:
                armor_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            armor_mod += self.status_effects['Defense'][2]
            return armor_mod
        elif mod == 'magic':
            magic_mod = self.intel * self.pro_level
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
                heal_mod += self.equipment['Weapon']().damage * 1.5
            return heal_mod
        elif mod == 'resist':
            try:
                return self.resistance[typ]
            except KeyError:
                return 0
        elif mod == 'luck':
            luck_mod = self.charisma // luck_factor
            return luck_mod


class Misc(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Misc'


class Slime(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Slime'
        self.resistance['Fire'] = 0.75
        self.resistance['Ice'] = 0.75
        self.resistance['Electric'] = 0.75
        self.resistance['Water'] = 0.75
        self.resistance['Earth'] = 0.75
        self.resistance['Wind'] = 0.75
        self.resistance['Shadow'] = 0.75
        self.resistance['Holy'] = 0.75
        self.resistance['Physical'] = -0.5


class Animal(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Animal'


class Reptile(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Reptile'


class Insect(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Insect'


class Humanoid(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Humanoid'


class Fey(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Fey'
        self.resistance['Shadow'] = 0.25


class Fiend(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Fiend'
        self.resistance['Shadow'] = 0.25
        self.resistance['Holy'] = -0.25


class Undead(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Undead'
        self.resistance['Fire'] = -0.25
        self.resistance['Shadow'] = 0.5
        self.resistance['Death'] = 1.
        self.resistance['Holy'] = -0.75
        self.resistance['Poison'] = 0.5


class Elemental(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Elemental'
        self.resistance['Physical'] = 0.75


class Dragon(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Dragon'
        self.resistance['Fire'] = 0.25
        self.resistance['Ice'] = 0.25
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = 0.25
        self.resistance['Earth'] = 0.25
        self.resistance['Wind'] = 0.25
        self.resistance['Death'] = 0.25
        self.resistance['Physical'] = 0.1


class Monster(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Monster'


class Aberration(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Aberration'


class Construct(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Construct'
        self.resistance['Electric'] = -0.75
        self.resistance['Earth'] = 0.5
        self.resistance['Poison'] = 1.
        self.resistance['Physical'] = 0.5


# Natural weapons
class NaturalWeapon:

    def __init__(self, name, damage, crit, subtyp):
        self.name = name
        self.damage = damage
        self.crit = crit
        self.subtyp = subtyp
        self.ignore = False
        self.poison = False
        self.disease = False
        self.disarm = False
        self.typ = "Weapon"


class RatBite(NaturalWeapon):
    """
    TODO Add disease chance
    """

    def __init__(self):
        super().__init__(name="bites", damage=2, crit=9, subtyp='Natural')
        self.disease = True


class WolfClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=4, crit=6, subtyp='Natural')


class BearClaw(NaturalWeapon):
    """
    TODO add bleed effect
    """

    def __init__(self):
        super().__init__(name="mauls", damage=5, crit=7, subtyp='Natural')


class Stinger(NaturalWeapon):
    """
    TODO Add a poison chance
    """

    def __init__(self):
        super().__init__(name="stings", damage=3, crit=4, subtyp='Natural')
        self.poison = True


class BirdClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="claws", damage=3, crit=5, subtyp='Natural')


class BirdClaw2(BirdClaw):

    def __init__(self):
        super().__init__()
        self.damage = 5
        self.crit = 3


class DemonClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="claws", damage=5, crit=3, subtyp='Natural')


class SnakeFang(NaturalWeapon):
    """
    TODO Add a poison chance
    """

    def __init__(self):
        super().__init__(name="strikes", damage=3, crit=4, subtyp='Natural')
        self.poison = True


class AlligatorTail(NaturalWeapon):
    """
    TODO add stun
    """

    def __init__(self):
        super().__init__(name="swipes", damage=8, crit=8, subtyp='Natural')
        self.stun = True


class LionPaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="swipes", damage=5, crit=5, subtyp='Natural')


class Laser(NaturalWeapon):
    """
    TODO add ignore
    """

    def __init__(self):
        super().__init__(name="zaps", damage=5, crit=3, subtyp='Natural')
        self.ignore = True


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player to stone
    """

    def __init__(self):
        super().__init__(name="leers", damage=0, crit=5, subtyp='Natural')


class DragonBite(NaturalWeapon):
    """
    TODO add disease
    """

    def __init__(self):
        super().__init__(name="bites", damage=15, crit=4, subtyp='Natural')
        self.disease = True


class DragonClaw(NaturalWeapon):
    """
    TODO add ignore
    """

    def __init__(self):
        super().__init__(name="rakes", damage=10, crit=5, subtyp='Natural')
        self.ignore = False


class DragonClaw2(DragonClaw):
    """
    TODO add ignore
    """

    def __init__(self):
        super().__init__()
        self.damage = 15
        self.crit = 4


class DragonTail(NaturalWeapon):
    """
    TODO add stun
    """

    def __init__(self):
        super().__init__(name="swipes", damage=18, crit=6, subtyp='Natural')
        self.stun = True


class NaturalArmor:

    def __init__(self, name, armor, subtyp):
        self.name = name
        self.armor = armor
        self.subtyp = subtyp
        self.typ = "Armor"


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


class NaturalShield:

    def __init__(self, name, mod, subtyp):
        self.name = name
        self.mod = mod
        self.subtyp = subtyp
        self.typ = "OffHand"


class ForceField(NaturalShield):

    def __init__(self):
        super().__init__(name="Force Field", mod=8, subtyp="Shield")


class ForceField2(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 5


class ForceField3(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 2


# Enemies
class Test(Misc):
    """
    Used for testing new implementations
    """
    def __init__(self):
        super().__init__(name="Test", health=999, mana=999, strength=0, intel=0, wisdom=0, con=0, charisma=99, dex=0,
                         exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {},
                          "Skills": {"Slot Machine": spells.SlotMachine}}


class Chest(Misc):

    def __init__(self, level):
        super().__init__(name='Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0, exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.level = level
        self.lock = False


class LockedChest(Misc):

    def __init__(self, level):
        super().__init__(name='Locked Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0,
                         exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.level = level
        self.lock = True


class LockedDoor(Misc):

    def __init__(self):
        super().__init__(name='Locked Door', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0,
                         exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.lock = True


class GreenSlime(Slime):

    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(1, 6), mana=0, strength=6, intel=1, wisdom=99, con=8,
                         charisma=0, dex=4, exp=random.randint(1, 20))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(1, 8), Key=items.Key)


class GiantRat(Animal):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=0, strength=4, intel=3, wisdom=3, con=6,
                         charisma=0, dex=15, exp=random.randint(7, 14))
        self.equipment = dict(Weapon=RatBite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(1, 5))


class Goblin(Humanoid):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(3, 7), mana=0, strength=6, intel=5, wisdom=2, con=8,
                         charisma=10, dex=16, exp=random.randint(7, 16))
        self.gold = random.randint(15, 50)
        self.equipment = dict(Weapon=items.BronzeSword, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=self.gold)
        self.spellbook = {"Spells": {},
                          "Skills": {"Gold Toss": spells.GoldToss}}


class Bandit(Humanoid):

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=16, strength=8, intel=8, wisdom=5, con=8,
                         charisma=0, dex=10, exp=random.randint(8, 18))
        self.equipment = dict(Weapon=items.BronzeDagger, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(15, 25))
        self.spellbook = {"Spells": {},
                          "Skills": {'Steal': spells.Steal,
                                     'Disarm': spells.Disarm}}


class Skeleton(Undead):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=0, strength=10, intel=4, wisdom=8, con=12,
                         charisma=0, dex=6, exp=random.randint(11, 20))
        self.equipment = dict(Weapon=items.BronzeSword, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(10, 20), Potion=items.HealthPotion)


class GiantHornet(Insect):

    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=0, strength=6, intel=4, wisdom=6,
                         con=6, charisma=0, dex=18, exp=random.randint(13, 24))
        self.equipment = dict(Weapon=Stinger, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(6, 15))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Zombie(Undead):

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(11, 14), mana=20, strength=15, intel=1, wisdom=5, con=8,
                         charisma=0, dex=8, exp=random.randint(11, 22))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(15, 30), Misc=items.Key)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike}}


class GiantSpider(Insect):

    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=0, strength=9, intel=10, wisdom=10,
                         con=8, charisma=0, dex=12, exp=random.randint(15, 24))
        self.equipment = dict(Weapon=Stinger, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(15, 30), Potion=items.ManaPotion)
        self.resistance['Poison'] = 0.25


class Quasit(Monster):

    def __init__(self):
        super().__init__(name='Quasit', health=random.randint(13, 17), mana=15, strength=5, intel=8, wisdom=10,
                         con=11, charisma=0, dex=16, exp=random.randint(25, 44))
        self.equipment = dict(Weapon=DemonClaw, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(25, 40))
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike}}


class Panther(Animal):

    def __init__(self):
        super().__init__(name='Panther', health=random.randint(10, 14), mana=25, strength=10, intel=8, wisdom=8,
                         con=10, charisma=0, dex=13, exp=random.randint(19, 28))
        self.equipment = dict(Weapon=WolfClaw, Armor=AnimalHide, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(18, 35))
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': spells.Backstab,
                                     'Kidney Punch': spells.KidneyPunch,
                                     'Disarm': spells.Disarm,
                                     'Parry': spells.Parry}}


class TwistedDwarf(Humanoid):

    def __init__(self):
        super().__init__(name='Twisted Dwarf', health=random.randint(15, 19), mana=10, strength=12, intel=8, wisdom=10,
                         con=12, charisma=0, dex=12, exp=random.randint(25, 44))
        self.equipment = dict(Weapon=items.Axe, Armor=items.HideArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(25, 40), Weapon=items.Axe)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}


# Level 1 Boss
class Minotaur(Monster):

    def __init__(self):
        super().__init__(name='Minotaur', health=random.randint(30, 44), mana=20, strength=15, intel=8, wisdom=10,
                         con=14, charisma=0, dex=12, exp=random.randint(55, 110))
        self.equipment = dict(Weapon=items.BattleAxe, Armor=items.LeatherArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(30, 75), Weapon=items.BattleAxe, Armor=items.LeatherArmor)
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': spells.MortalStrike,
                                     'Disarm': spells.Disarm}}


class Gnoll(Humanoid):

    def __init__(self):
        super().__init__(name='Gnoll', health=random.randint(16, 24), mana=20, strength=13, intel=10, wisdom=5, con=8,
                         charisma=0, dex=16, exp=random.randint(45, 85))
        self.equipment = dict(Weapon=items.Spear, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(30, 60), Weapon=items.Spear)
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': spells.Disarm}}


class GiantSnake(Reptile):

    def __init__(self):
        super().__init__(name='Giant Snake', health=random.randint(18, 26), mana=0, strength=15, intel=5, wisdom=6,
                         con=14, charisma=0, dex=16, exp=random.randint(60, 100))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 75))
        self.resistance['Poison'] = 0.25


class Orc(Humanoid):

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(17, 28), mana=14, strength=12, intel=6, wisdom=5, con=10,
                         charisma=0, dex=14, exp=random.randint(45, 80))
        self.equipment = dict(Weapon=items.IronSword, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(20, 65), Weapon=items.IronSword)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}


class GiantOwl(Animal):

    def __init__(self):
        super().__init__(name='Giant Owl', health=random.randint(12, 17), mana=0, strength=11, intel=12, wisdom=10,
                         con=10, charisma=0, dex=14, exp=random.randint(45, 80))
        self.equipment = dict(Weapon=BirdClaw, Armor=items.NoArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(20, 65))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Vampire(Undead):

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(20, 28), mana=30, strength=20, intel=14, wisdom=12,
                         con=15, charisma=0, dex=14, exp=random.randint(50, 90))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 90), Potion=items.GreatHealthPotion)
        self.spellbook = {"Spells": {},
                          "Skills": {'Health Drain': spells.HealthDrain}}


class Direwolf(Animal):

    def __init__(self):
        super().__init__(name='Direwolf', health=random.randint(16, 20), mana=0, strength=17, intel=7, wisdom=6, con=14,
                         charisma=0, dex=16, exp=random.randint(60, 100))
        self.equipment = dict(Weapon=WolfClaw, Armor=AnimalHide, OffHand=WolfClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 75))


class Wererat(Monster):

    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(14, 17), mana=0, strength=14, intel=6, wisdom=12, con=11,
                         charisma=0, dex=18, exp=random.randint(57, 94))
        self.equipment = dict(Weapon=RatBite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 65))


class RedSlime(Slime):

    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(8, 20), mana=30, strength=10, intel=15, wisdom=99,
                         con=12, charisma=0, dex=5, exp=random.randint(43, 150))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(20, 120), Potion=items.SuperHealthPotion)
        self.spellbook = {'Spells': {'Firebolt': spells.Firebolt},
                          'Skills': {}}


class GiantScorpion(Insect):

    def __init__(self):
        super().__init__(name='Giant Scorpion', health=random.randint(13, 18), mana=0, strength=14, intel=5, wisdom=10,
                         con=12, charisma=0, dex=9, exp=random.randint(65, 105))
        self.equipment = dict(Weapon=Stinger, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 65))
        self.resistance['Poison'] = 0.25


class Warrior(Humanoid):

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(22, 31), mana=25, strength=14, intel=10, wisdom=8,
                         con=12, charisma=0, dex=8, exp=random.randint(65, 110))
        self.equipment = dict(Weapon=items.IronSword, Armor=items.RingMail, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(25, 100), Weapon=items.IronSword, Armor=items.RingMail)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike,
                                     'Disarm': spells.Disarm2,
                                     'Parry': spells.Parry}}


class Harpy(Monster):

    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=0, strength=18, intel=13, wisdom=13,
                         con=14, charisma=0, dex=23, exp=random.randint(65, 115))
        self.equipment = dict(Weapon=BirdClaw, Armor=items.NoArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Naga(Monster):

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=0, strength=15, intel=13, wisdom=15,
                         con=15, charisma=0, dex=17, exp=random.randint(67, 118))
        self.equipment = dict(Weapon=items.Spear, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(55, 75), Weapon=items.Spear, Potion=items.GreatManaPotion)
        self.resistance['Electric'] = -0.5
        self.resistance['Water'] = 0.75


# Level 2 Boss
class Pseudodragon(Dragon):

    def __init__(self):
        super().__init__(name='Pseudodragon', health=random.randint(60, 85), mana=100, strength=22, intel=12, wisdom=16,
                         con=20, charisma=0, dex=14, exp=random.randint(125, 225))
        self.equipment = dict(Weapon=DragonClaw, Armor=DragonScale, OffHand=DragonClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)
        self.spellbook = {'Spells': {'Fireball': spells.Fireball,
                                     'Blinding Fog': spells.BlindingFog},
                          'Skills': {'Gold Toss': spells.GoldToss}}


class Ghoul(Undead):

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=50, strength=23, intel=10, wisdom=8, con=24,
                         charisma=0, dex=12, exp=random.randint(110, 190))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 45), Potion=items.SuperHealthPotion)
        self.spellbook = {"Spells": {'Disease Breath': spells.DiseaseBreath},
                          "Skills": {}}


class PitViper(Reptile):

    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=30, strength=17, intel=6, wisdom=8,
                         con=16, charisma=0, dex=18, exp=random.randint(115, 190))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 85))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Poison'] = 0.25


class Disciple(Humanoid):

    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=70, strength=16, intel=17, wisdom=15,
                         con=16, charisma=0, dex=16, exp=random.randint(110, 190))
        self.equipment = dict(Weapon=items.SteelDagger, Armor=items.SilverCloak, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(55, 95), Potion=items.SuperManaPotion, Weapon=items.SteelDagger,
                              Armor=items.SilverCloak)
        self.spellbook = {'Spells': {'Firebolt': spells.Firebolt,
                                     'Ice Lance': spells.IceLance,
                                     'Shock': spells.Shock,
                                     'Blinding Fog': spells.BlindingFog},
                          'Skills': {}}


class Werewolf(Monster):
    """
    TODO improve for transform
    """

    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(45, 55), mana=0, strength=20, intel=10, wisdom=10,
                         con=20, charisma=0, dex=18, exp=random.randint(120, 200))
        self.equipment = dict(Weapon=WolfClaw, Armor=AnimalHide, OffHand=WolfClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(45, 55))
        self.spellbook = {"Spells": {},
                          "Skills": {'Parry': spells.Parry}}


class BlackSlime(Slime):

    def __init__(self):
        super().__init__(name='Black Slime', health=random.randint(25, 60), mana=80, strength=13, intel=20, wisdom=99,
                         con=15, charisma=0, dex=6, exp=random.randint(85, 260))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(30, 180), Potion=items.Elixir)
        self.spellbook = {'Spells': {'Shadow Bolt': spells.ShadowBolt,
                                     'Corruption': spells.Corruption},
                          'Skills': {}}


class Ogre(Monster):

    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=20, strength=22, intel=10, wisdom=14, con=20,
                         charisma=0, dex=14, exp=random.randint(115, 195))
        self.equipment = dict(Weapon=items.IronHammer, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75), Weapon=items.IronHammer, Armor=items.Cuirboulli)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}


class Alligator(Reptile):

    def __init__(self):
        super().__init__(name='Alligator', health=random.randint(60, 75), mana=20, strength=21, intel=8, wisdom=7,
                         con=20, charisma=0, dex=15, exp=random.randint(120, 200))
        self.equipment = dict(Weapon=AlligatorTail, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 50))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}


class Troll(Humanoid):

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=20, strength=21, intel=10, wisdom=8, con=24,
                         charisma=0, dex=15, exp=random.randint(125, 210))
        self.equipment = dict(Weapon=items.GreatAxe, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 45), Weapon=items.GreatAxe, Armor=items.Cuirboulli)
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': spells.MortalStrike}}


class Direbear(Animal):
    """
    TODO improve enemy for transform
    """

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=0, strength=25, intel=6, wisdom=6, con=26,
                         charisma=0, dex=18, exp=random.randint(110, 210))
        self.equipment = dict(Weapon=BearClaw, Armor=AnimalHide, OffHand=BearClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(45, 60))


class GoldenEagle(Animal):

    def __init__(self):
        super().__init__(name='Golden Eagle', health=random.randint(40, 50), mana=0, strength=19, intel=15, wisdom=15,
                         con=17, charisma=0, dex=25, exp=random.randint(130, 220))
        self.equipment = dict(Weapon=BirdClaw2, Armor=items.NoArmor, OffHand=BirdClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class EvilCrusader(Humanoid):

    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=50, strength=21, intel=18, wisdom=17,
                         con=26, charisma=0, dex=14, exp=random.randint(140, 225))
        self.equipment = dict(Weapon=items.SteelSword, Armor=items.Splint, OffHand=items.KiteShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(65, 90), Weapon=items.SteelSword, Armor=items.Splint,
                              OffHand=items.KiteShield)
        self.spellbook = {"Spells": {'Smite': spells.Smite},
                          "Skills": {'Shield Slam': spells.ShieldSlam,
                                     'Disarm': spells.Disarm2,
                                     'Shield Block': spells.ShieldBlock}}
        self.resistance['Shadow'] = 0.5
        self.resistance['Holy'] = -0.5


# Level 3 Boss
class Cockatrice(Monster):

    def __init__(self):
        super().__init__(name='Cockatrice', health=random.randint(80, 120), mana=99, strength=26, intel=12, wisdom=15,
                         con=16, charisma=0, dex=20, exp=random.randint(250, 375))
        self.equipment = dict(Weapon=BirdClaw2, Armor=items.NoArmor, OffHand=BirdClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(120, 150), Potion=items.MasterHealthPotion)
        self.spellbook = {"Spells": {'Petrify': spells.Petrify},
                          "Skills": {}}


class BrownSlime(Slime):

    def __init__(self):
        super().__init__(name='Brown Slime', health=random.randint(50, 80), mana=85, strength=17, intel=30, wisdom=99,
                         con=15, charisma=0, dex=8, exp=random.randint(190, 460))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(150, 280), Potion=items.Elixir)
        self.spellbook = {'Spells': {'Mudslide': spells.Mudslide},
                          'Skills': {}}


class Gargoyle(Construct):

    def __init__(self):
        super().__init__(name='Gargoyle', health=random.randint(55, 75), mana=20, strength=26, intel=10, wisdom=0,
                         con=18, charisma=0, dex=21, exp=random.randint(210, 330))
        self.equipment = dict(Weapon=BirdClaw2, Armor=StoneArmor, OffHand=BirdClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(75, 125))
        self.spellbook = {"Spells": {},
                          "Skills": {'Blind': spells.Blind}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Conjurer(Humanoid):

    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(40, 65), mana=150, strength=14, intel=22, wisdom=18,
                         con=14, charisma=0, dex=13, exp=random.randint(215, 340))
        self.equipment = dict(Weapon=items.SerpentStaff, Armor=items.GoldCloak, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(110, 145), Potion=items.MasterManaPotion, Weapon=items.SerpentStaff,
                              Armor=items.GoldCloak)
        self.spellbook = {"Spells": {'Fireball': spells.Fireball,
                                     'Icicle': spells.Icicle,
                                     'Lightning': spells.Lightning,
                                     'Aqualung': spells.Aqualung},
                          "Skills": {'Mana Drain': spells.ManaDrain}}


class Chimera(Monster):

    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(60, 95), mana=140, strength=26, intel=14, wisdom=16,
                         con=20, charisma=0, dex=14, exp=random.randint(230, 380))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide, OffHand=LionPaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)
        self.spellbook = {"Spells": {'Molten Rock': spells.MoltenRock},
                          "Skills": {}}


class Dragonkin(Dragon):

    def __init__(self):
        super().__init__(name='Dragonkin', health=random.randint(80, 115), mana=90, strength=26, intel=10, wisdom=18,
                         con=20, charisma=0, dex=20, exp=random.randint(250, 480))
        self.equipment = dict(Weapon=items.Halberd, Armor=items.Breastplate, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(150, 300), Weapon=items.Halberd, Armor=items.Breastplate,
                              Potion=items.Elixir)
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': spells.Disarm2}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Griffin(Monster):
    """
    TODO improve for transform
    """

    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(75, 105), mana=110, strength=26, intel=10, wisdom=18,
                         con=18, charisma=0, dex=25, exp=random.randint(240, 450))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide, OffHand=BirdClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(140, 280))
        self.spellbook = {"Spells": {'Hurricane': spells.Hurricane},
                          "Skills": {}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class DrowAssassin(Humanoid):

    def __init__(self):
        super().__init__(name='Drow Assassin', health=random.randint(65, 85), mana=75, strength=24, intel=16, wisdom=15,
                         con=14, charisma=0, dex=28, exp=random.randint(280, 480))
        self.equipment = dict(Weapon=items.AdamantiteDagger, Armor=items.StuddedLeather, OffHand=items.AdamantiteDagger,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(160, 250), Weapon=items.AdamantiteDagger,
                              Armor=items.StuddedLeather, OffHand=items.AdamantiteDagger)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike2,
                                     'Backstab': spells.Backstab,
                                     'Kidney Punch': spells.KidneyPunch2,
                                     'Mug': spells.Mug,
                                     'Disarm': spells.Disarm2,
                                     'Parry': spells.Parry}}


class Cyborg(Construct):

    def __init__(self):
        super().__init__(name='Cyborg', health=random.randint(90, 120), mana=80, strength=28, intel=13, wisdom=0, con=18,
                         charisma=0, dex=14, exp=random.randint(290, 500))
        self.equipment = dict(Weapon=Laser, Armor=MetalPlating, OffHand=Laser,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(200, 300))
        self.spellbook = {"Spells": {'Shock': spells.Shock},
                          "Skills": {}}


class DarkKnight(Humanoid):

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(85, 110), mana=60, strength=28, intel=15, wisdom=12,
                         con=21, charisma=0, dex=17, exp=random.randint(300, 550))
        self.equipment = dict(Weapon=items.Trident, Armor=items.PlateMail, OffHand=items.TowerShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(300, 420), Weapon=items.Trident,
                              Armor=items.PlateMail, OffHand=items.TowerShield)
        self.spellbook = {"Spells": {'Enhance Blade': spells.EnhanceBlade},
                          "Skills": {'Shield Slam': spells.ShieldSlam2,
                                     'Disarm': spells.Disarm3,
                                     'Shield Block': spells.ShieldBlock}}


# Level 4 boss
class Golem(Construct):

    def __init__(self):
        super().__init__(name='Golem', health=random.randint(180, 250), mana=100, strength=35, intel=10, wisdom=18,
                         con=28, charisma=0, dex=20, exp=random.randint(500, 800))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=StoneArmor, OffHand=ForceField2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 600), Potion=items.AardBeing)
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}


class ShadowSerpent(Reptile):

    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=100, strength=28, intel=18,
                         wisdom=15, con=22, charisma=0, dex=23, exp=random.randint(480, 790))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=SnakeFang,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(280, 485), Potion=items.Megalixir)
        self.spellbook = {"Spells": {'Corruption': spells.Corruption2},
                          "Skills": {}}
        self.resistance['Shadow'] = 0.9
        self.resistance['Holy'] = -0.75
        self.resistance['Poison'] = 0.25


class Aboleth(Slime):

    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(110, 500), mana=120, strength=25, intel=45, wisdom=50,
                         con=25, charisma=0, dex=10, exp=random.randint(350, 930))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(130, 750), Potion=items.AardBeing)
        self.spellbook = {"Spells": {'Poison Breath': spells.PoisonBreath,
                                     'Disease Breath': spells.DiseaseBreath,
                                     'Terrify': spells.Terrify2},
                          "Skills": {}}
        self.resistance['Poison'] = 1.5


class Beholder(Aberration):

    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=100, strength=25, intel=40, wisdom=35,
                         con=28, charisma=0, dex=20, exp=random.randint(500, 900))
        self.equipment = dict(Weapon=Gaze, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(300, 500), OffHand=items.MedusaShield)
        self.spellbook = {"Spells": {'Magic Missile': spells.MagicMissile2},
                          "Skills": {'Mana Drain': spells.ManaDrain}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25
        self.resistance['Death'] = 1


class Behemoth(Aberration):

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=100, strength=38, intel=25, wisdom=20,
                         con=30, charisma=0, dex=25, exp=random.randint(620, 950))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide, OffHand=LionPaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 550))
        self.spellbook = {"Spells": {'Holy': spells.Holy3},
                          "Skills": {}}
        self.resistance['Death'] = 0.9
        self.resistance['Holy'] = 0.75


class Lich(Undead):

    def __init__(self):
        super().__init__(name='Lich', health=random.randint(210, 300), mana=120, strength=25, intel=35, wisdom=40,
                         con=20, charisma=0, dex=22, exp=random.randint(580, 920))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.MerlinRobe, OffHand=items.Necronomicon,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 530), Armor=items.MerlinRobe, OffHand=items.Necronomicon)
        self.spellbook = {"Spells": {'Ice Blizzard': spells.IceBlizzard,
                                     'Desoul': spells.Desoul},
                          "Skills": {'Health/Mana Drain': spells.HealthManaDrain}}
        self.resistance = {'Fire': -0.5,
                           'Ice': 0.9,
                           'Electric': 0,
                           'Water': 0,
                           'Earth': 0,
                           'Wind': 0,
                           'Shadow': 0.5,
                           'Death': 1,
                           'Holy': -0.5,
                           'Poison': 0.5}


class Basilisk(Reptile):

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(220, 325), mana=120, strength=29, intel=26, wisdom=30,
                         con=27, charisma=0, dex=20, exp=random.randint(630, 900))
        self.equipment = dict(Weapon=SnakeFang, Armor=StoneArmor, OffHand=Gaze,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(380, 520))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Death'] = 1
        self.resistance['Poison'] = 0.75


class MindFlayer(Aberration):

    def __init__(self):
        super().__init__(name='Mind Flayer', health=random.randint(190, 285), mana=150, strength=28, intel=40,
                         wisdom=35, con=25, charisma=0, dex=18, exp=random.randint(590, 850))
        self.equipment = dict(Weapon=items.MithrilshodStaff, Armor=items.NoArmor, OffHand=items.Magus,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(450, 600), OffHand=items.Magus)
        self.spellbook = {"Spells": {'Doom': spells.Doom,
                                     'Terrify': spells.Terrify2,
                                     'Corruption': spells.Corruption},
                          "Skills": {'Mana Drain': spells.ManaDrain}}
        self.resistance['Shadow'] = 0.5
        self.resistance['Death'] = 1
        self.resistance['Holy'] = -0.25


class Warforged(Construct):

    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=200, strength=40, intel=20, wisdom=0,
                         con=33, charisma=0, dex=10, exp=random.randint(580, 880))
        self.equipment = dict(Weapon=items.GreatMaul, Armor=StoneArmor, OffHand=ForceField3,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(380, 490))
        self.spellbook = {"Spells": {'Earthquake': spells.Earthquake},
                          "Skills": {'Piercing Strike': spells.PiercingStrike,
                                     'Parry': spells.Parry}}


class Wyrm(Dragon):

    def __init__(self):
        super().__init__(name='Wyrm', health=random.randint(320, 400), mana=150, strength=38, intel=28, wisdom=30,
                         con=28, charisma=0, dex=23, exp=random.randint(620, 880))
        self.equipment = dict(Weapon=DragonTail, Armor=DragonScale, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(650, 830))
        self.spellbook = {'Spells': {'Volcano': spells.Volcano},
                          'Skills': {'Multi-Strike': spells.DoubleStrike}}


class Hydra(Monster):

    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(260, 375), mana=150, strength=37, intel=30, wisdom=26,
                         con=28, charisma=0, dex=22, exp=random.randint(600, 850))
        self.equipment = dict(Weapon=DragonBite, Armor=DragonScale, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 550), Armor=items.Genji)
        self.spellbook = {'Spells': {'Tsunami': spells.Tsunami},
                          'Skills': {'Multi-Strike': spells.TripleStrike}}
        self.resistance = {'Fire': 0,
                           'Ice': 0,
                           'Electric': -1,
                           'Water': 1.5,
                           'Earth': 0,
                           'Wind': 0,
                           'Shadow': 0,
                           'Death': 1,
                           'Holy': 0,
                           'Poison': 0.75}


class Wyvern(Dragon):

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(320, 410), mana=0, strength=35, intel=33, wisdom=24,
                         con=30, charisma=0, dex=40, exp=random.randint(650, 900))
        self.equipment = dict(Weapon=DragonClaw2, Armor=DragonScale, OffHand=DragonClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(420, 570), Armor=items.DragonHide)
        self.spellbook = {"Spells": {'Tornado': spells.Tornado},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Domingo(Aberration):

    def __init__(self):
        super().__init__(name='Domingo', health=random.randint(500, 700), mana=999, strength=0, intel=50, wisdom=40,
                         con=45, charisma=0, dex=50, exp=random.randint(2000, 3000))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(2500, 5000))
        self.spellbook = {"Spells": {'Ultima': spells.Ultima},
                          "Skills": {'Multi-Cast': spells.DoubleCast}}
        self.flying = True
        self.resistance = {'Fire': 0.25,
                           'Ice': 0.25,
                           'Electric': 0.25,
                           'Water': 0.25,
                           'Earth': 1,
                           'Wind': -0.25,
                           'Shadow': 0.25,
                           'Death': 1,
                           'Holy': 0.25,
                           'Poison': 0.25}


# Level 5 Boss
class RedDragon(Dragon):
    """
    Final Boss; highly resistant to spells and will heal from fire spells; immune to weapon damage except
     ultimate weapons
    """

    def __init__(self):
        super().__init__(name='Red Dragon', health=random.randint(750, 1000), mana=500, strength=50, intel=28,
                         wisdom=35, con=30, charisma=0, dex=22, exp=0)
        self.equipment = dict(Weapon=DragonTail, Armor=DragonScale, OffHand=DragonClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict()
        self.spellbook = {"Spells": {'Heal': spells.Heal3,
                                     'Volcano': spells.Volcano,
                                     'Ultima': spells.Ultima},
                          "Skills": {'Mortal Strike': spells.MortalStrike2,
                                     'Multi-Cast': spells.TripleCast}}
        self.flying = True
        self.resistance = {'Fire': 1.5,
                           'Ice': 0.5,
                           'Electric': 0.5,
                           'Water': 0.5,
                           'Earth': 1,
                           'Wind': -0.25,
                           'Shadow': 0.5,
                           'Death': 1,
                           'Holy': 0.5,
                           'Poison': 0.75}


# Familiars
class Homunculus(Construct):
    """
    Familiar - cast helpful defensive abilities; abilities upgrade when the familiar upgrades
    Level 1: Can use Disarm, Blind, and Stupefy
    Level 2: Gains Cover and bonus to defense
    Level 3: Gains Resurrection
    """

    def __init__(self):
        super().__init__(name='Homunculus', health=0, mana=0, strength=0, intel=0, wisdom=0,
                         con=0, charisma=0, dex=0, exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {'Stupefy': spells.Stupefy},
                          "Skills": {'Disarm': spells.Disarm,
                                     'Blind': spells.Blind}}
        self.spec = 'Defense'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; A tiny construct that serves and protects its master from anything that challenges them, regardless of
        the enemy's size or toughness. The Homunculus specializes in defensive abilities, either to prevent direct 
        damage or to limit the enemy's ability to deal damage. Choose this familiar if you are a tad bit squishy, or 
        your favorite movie is The Bodyguard.
        """

    def level_up(self):
        print("{} has leveled up!".format(self.name))
        if self.pro_level == 1:
            self.pro_level = 2
            skill_list = [spells.Cover, spells.Disarm2]
            for skill in skill_list:
                time.sleep(0.5)
                print(skill())
                self.spellbook['Skills'][skill().name] = skill
        else:
            self.pro_level = 3
            time.sleep(0.5)
            print(spells.Resurrection())
            self.spellbook['Spells']['Resurrection'] = spells.Resurrection
            time.sleep(0.5)
            print(spells.Disarm3())
            self.spellbook['Skills']['Disarm'] = spells.Disarm3


class Fairy(Fey):
    """
    Familiar - cast helpful support abilities; abilities upgrade when the familiar upgrades
    Level 1: Can cast Heal, Regen, and Bless
    Level 2: Gains Reflect and will randomly restore percentage of mana
    Level 3: Gains Cleanse
    """

    def __init__(self):
        super().__init__(name='Fairy', health=0, mana=0, strength=0, intel=0, wisdom=0,
                         con=0, charisma=0, dex=0, exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {'Heal': spells.Heal,
                                     'Regen': spells.Regen,
                                     'Bless': spells.Bless},
                          "Skills": {}}
        self.spec = 'Support'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; These small, flying creatures hail from a parallel plane of existence and are typically associated 
        with a connection to nature. While Faeries are not known for their constitution, they more than make up for it 
        with support magics. If you hate having to stock up on potions, this familiar is the one for you!
        """

    def level_up(self):
        print("{} has leveled up!".format(self.name))
        if self.pro_level == 1:
            self.pro_level = 2
            spell_list = [spells.Reflect, spells.Heal2, spells.Regen2, spells.Bless2]
            for spell in spell_list:
                time.sleep(0.5)
                print(spell())
                self.spellbook['Spells'][spell().name] = spell
        else:
            self.pro_level = 3
            spell_list = [spells.Cleanse, spells.Heal3, spells.Regen3]
            for spell in spell_list:
                time.sleep(0.5)
                print(spell())
                self.spellbook['Spells'][spell().name] = spell


class Mephit(Elemental):
    """
    Familiar - cast helpful arcane abilities
    Level 1: Can cast the 3 arcane elementals Firebolt, Ice Lance, and Shock and Magic Missile
    Level 2: Gains Boost and sometimes provides elemental resistance
    Level 3: Gains Ultima
    """

    def __init__(self):
        super().__init__(name='Mephit', health=0, mana=0, strength=0, intel=0, wisdom=0,
                         con=0, charisma=0, dex=0, exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {'Firebolt': spells.Firebolt,
                                     'Ice Lance': spells.IceLance,
                                     'Shock': spells.Shock,
                                     'Magic Missile': spells.MagicMissile},
                          "Skills": {}}
        self.spec = 'Arcane'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; A mephit is similar to an imp, except this little guy can blast arcane spells. Typically mephits
        embody a single elemental school but these are more Jack-of-all-trades than specialist, even gaining the ability
        to boost its master's magic and magic defense. Who wouldn't want a their very own pocket caster?
        """

    def level_up(self):
        print("{} has leveled up!".format(self.name))
        if self.pro_level == 1:
            self.pro_level = 2
            spell_list = [spells.Fireball, spells.Icicle, spells.Lightning, spells.MagicMissile2, spells.Boost]
            for spell in spell_list:
                time.sleep(0.5)
                print(spell())
                self.spellbook['Spells'][spell().name] = spell
        else:
            self.pro_level = 3
            spell_list = [spells.Firestorm, spells.IceBlizzard, spells.Electrocution,
                          spells.MagicMissile3, spells.Ultima]
            for spell in spell_list:
                time.sleep(0.5)
                print(spell())
                self.spellbook['Spells'][spell().name] = spell


class Jinkin(Fey):
    """
    Familiar - cast (mostly) helpful luck abilities
    Level 1: Can cast Corruption and use Gold Toss (uses player gold) and Steal (items go to player inventory)
    Level 2: Gains Mug and will unlock Treasure chests
    Level 3: Gains Slot Machine and will randomly find items at the end of combat
    """

    def __init__(self):
        super().__init__(name='Jinkin', health=0, mana=0, strength=0, intel=0, wisdom=0,
                         con=0, charisma=0, dex=0, exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {'Corruption': spells.Corruption},
                          "Skills": {'Gold Toss': spells.GoldToss,
                                     'Steal': spells.Steal}}
        self.spec = 'Luck'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; Jinkins are vindictive little tricksters. While they mostly rely on (their very good) luck, Jinkins 
        also enjoy the occasional curse to really add a thorn to your enemy's paw. You may not always like what you get
        but you also may just love it! (low charisma characters should probably avoid this familiar)...
        """

    def level_up(self):
        print("{} has leveled up!".format(self.name))
        time.sleep(0.5)
        if self.pro_level == 1:
            self.pro_level = 2
            skill_list = [spells.Mug, spells.Lockpick]
            for skill in skill_list:
                time.sleep(0.5)
                print(skill())
                self.spellbook['Spells'][skill().name] = skill
            time.sleep(0.5)
            print(spells.Corruption2())
            self.spellbook['Spells']['Corruption'] = spells.Corruption2
        else:
            self.pro_level = 3
            print(spells.SlotMachine())
            self.spellbook['Skills']['Slot Machine'] = spells.SlotMachine
