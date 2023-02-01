###########################################
""" enemy manager """

# Imports
import random

import character
import items
import spells


# Functions
def random_enemy(level):
    monsters = {'1': [GreenSlime(), Goblin(), GiantRat(), Bandit(), Skeleton(), GiantHornet(), Zombie(), GiantSpider(),
                      Panther(), TwistedDwarf()],
                '2': [Gnoll(), Minotaur(), GiantOwl(), Orc(), Vampire(), Direwolf(), RedSlime(), GiantSnake(),
                      GiantScorpion(), Warrior(), Harpy(), Naga(), Wererat()],
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

    return enemy


class Enemy(character.Character):

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__()
        self.name = name
        self.status_effects = {"Stun": [False, 0], "Poison": [False, 0, 0], "DOT": [False, 0, 0], "Doom": [False, 0],
                               "Blind": [False, 0], "Bleed": [False, 0, 0], "Disarm": [False, 0]}
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
        self.equipment = dict()
        self.inventory = {}
        self.spellbook = {'Spells': {},
                          'Skills': {}}

    def __str__(self):
        return "Enemy: {}  Health: {}/{}  Mana: {}/{}".format(self.name, self.health, self.health_max, self.mana,
                                                              self.mana_max)

    def is_alive(self):
        return self.health > 0

    def check_mod(self, mod, typ=None):
        if mod == 'weapon':
            weapon_mod = self.strength
            if not self.status_effects['Disarm']:
                weapon_mod += self.equipment['Weapon']().damage
            if 'Physical Damage' in self.equipment['Ring']().mod:
                weapon_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            return weapon_mod
        elif mod == 'off':
            try:
                off_mod = (self.strength + self.equipment['OffHand']().damage) // 2
                if 'Physical Damage' in self.equipment['Ring']().mod:
                    off_mod += (int(self.equipment['Ring']().mod.split(' ')[0]) // 2)
                return off_mod
            except AttributeError:
                return 0
        elif mod == 'armor':
            armor_mod = self.equipment['Armor']().armor
            if 'Physical Defense' in self.equipment['Ring']().mod:
                armor_mod += int(self.equipment['Ring']().mod.split(' ')[0])
            return armor_mod
        elif mod == 'magic':
            magic_mod = self.intel * self.pro_level
            if 'Magic Damage' in self.equipment['Pendant']().mod:
                magic_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            return magic_mod
        elif mod == 'magic def':
            m_def_mod = self.wisdom
            if 'Magic Defense' in self.equipment['Pendant']().mod:
                m_def_mod += int(self.equipment['Pendant']().mod.split(' ')[0])
            return m_def_mod
        elif mod == 'heal':
            heal_mod = self.wisdom * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                heal_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                heal_mod += self.equipment['Weapon']().damage * 1.5
            return heal_mod
        elif mod == 'resist':  # TODO add resistances here and in enemies.py
            pass


class Misc(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Misc'


class Slime(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Slime'


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


class Undead(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Undead'


class Dragon(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Dragon'


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
        self.typ = "Natural"


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
        super().__init__(name="bites", damage=8, crit=4, subtyp='Natural')
        self.disease = True


class DragonClaw(NaturalWeapon):
    """
    TODO add ignore
    """
    def __init__(self):
        super().__init__(name="rakes", damage=10, crit=5, subtyp='Natural')
        self.ignore = False


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
class Chest(Misc):

    def __init__(self, level):
        super().__init__(name='Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0, exp=0)
        self.level = level
        self.inventory = dict()
        self.lock = False


class LockedChest(Misc):

    def __init__(self, level):
        super().__init__(name='Locked Chest', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0,
                         exp=0)
        self.level = level
        self.inventory = dict()
        self.lock = True


class LockedDoor(Misc):

    def __init__(self):
        super().__init__(name='Locked Door', health=1, mana=0, strength=0, intel=0, wisdom=0, con=0, charisma=0, dex=0,
                         exp=0)
        self.inventory = dict()
        self.lock = True


class GreenSlime(Slime):

    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(1, 6), mana=0, strength=6, intel=1, wisdom=99, con=8,
                         charisma=0, dex=4, exp=random.randint(1, 20))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(1, 8), Key=items.Key)
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class GiantRat(Animal):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=0, strength=4, intel=3, wisdom=3, con=6,
                         charisma=0, dex=15, exp=random.randint(7, 14))
        self.equipment = dict(Weapon=RatBite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(1, 5))
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class Goblin(Humanoid):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(2, 4), mana=0, strength=6, intel=5, wisdom=2, con=8,
                         charisma=0, dex=8, exp=random.randint(7, 16))
        self.equipment = dict(Weapon=items.BronzeSword, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(4, 10))
        self.spellbook = {"Spells": {},
                          "Skills": {}}


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
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class GiantHornet(Insect):

    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=0, strength=6, intel=4, wisdom=6,
                         con=6, charisma=0, dex=18, exp=random.randint(13, 24))
        self.equipment = dict(Weapon=Stinger, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(6, 15))
        self.spellbook = {"Spells": {},
                          "Skills": {}}
        self.flying = True


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
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class Panther(Animal):

    def __init__(self):
        super().__init__(name='Panther', health=random.randint(10, 14), mana=0, strength=10, intel=8, wisdom=8,
                         con=10, charisma=0, dex=13, exp=random.randint(19, 28))
        self.equipment = dict(Weapon=WolfClaw, Armor=AnimalHide, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(18, 35))
        self.spellbook = {"Spells": {},
                          "Skills": {}}


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
        self.spellbook = {"Spells": {},
                          "Skills": {}}


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
        self.spellbook = {"Spells": {},
                          "Skills": {}}
        self.flying = True


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
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class Wererat(Monster):

    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(14, 17), mana=0, strength=14, intel=6, wisdom=12, con=11,
                         charisma=0, dex=18, exp=random.randint(57, 94))
        self.equipment = dict(Weapon=RatBite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 65))
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class RedSlime(Slime):

    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(8, 20), mana=30, strength=10, intel=10, wisdom=99,
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
        self.spellbook = {"Spells": {},
                          "Skills": {}}


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
        self.spellbook = {"Spells": {},
                          "Skills": {}}
        self.flying = True


class Naga(Monster):

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=0, strength=15, intel=13, wisdom=15,
                         con=15, charisma=0, dex=17, exp=random.randint(67, 118))
        self.equipment = dict(Weapon=items.Spear, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(55, 75), Weapon=items.Spear, Potion=items.GreatManaPotion)
        self.spellbook = {"Spells": {},
                          "Skills": {}}


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
                          'Skills': {}}


class Ghoul(Undead):

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=30, strength=23, intel=1, wisdom=8, con=24,
                         charisma=0, dex=12, exp=random.randint(110, 190))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 45), Potion=items.SuperHealthPotion)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike}}


class PitViper(Reptile):

    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=0, strength=17, intel=6, wisdom=8,
                         con=16, charisma=0, dex=18, exp=random.randint(115, 190))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 85))
        self.spellbook = {"Spells": {},
                          "Skills": {spells.DoubleStrike}}


class Disciple(Humanoid):

    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=50, strength=16, intel=17, wisdom=15,
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
        super().__init__(name='Black Slime', health=random.randint(25, 60), mana=50, strength=13, intel=12, wisdom=99,
                         con=15, charisma=0, dex=6, exp=random.randint(85, 260))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(30, 180), Potion=items.Elixir)
        self.spellbook = {'Spells': {'Shadow Bolt': spells.ShadowBolt,
                                     'Corruption': spells.Corruption},
                          'Skills': {}}


class Ogre(Monster):

    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=0, strength=22, intel=10, wisdom=14, con=20,
                         charisma=0, dex=14, exp=random.randint(115, 195))
        self.equipment = dict(Weapon=items.IronHammer, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75), Weapon=items.IronHammer, Armor=items.Cuirboulli)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}


class Alligator(Reptile):

    def __init__(self):
        super().__init__(name='Alligator', health=random.randint(60, 75), mana=0, strength=21, intel=8, wisdom=7,
                         con=20, charisma=0, dex=15, exp=random.randint(120, 200))
        self.equipment = dict(Weapon=AlligatorTail, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 50))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}


class Troll(Humanoid):

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=0, strength=21, intel=10, wisdom=8, con=24,
                         charisma=0, dex=15, exp=random.randint(125, 210))
        self.equipment = dict(Weapon=items.GreatAxe, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 45), Weapon=items.GreatAxe, Armor=items.Cuirboulli)
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': spells.MortalStrike}}


class Direbear(Animal):

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=0, strength=25, intel=6, wisdom=6, con=26,
                         charisma=0, dex=18, exp=random.randint(110, 210))
        self.equipment = dict(Weapon=BearClaw, Armor=AnimalHide, OffHand=BearClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(45, 60))
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class GoldenEagle(Animal):

    def __init__(self):
        super().__init__(name='Golden Eagle', health=random.randint(40, 50), mana=0, strength=19, intel=15, wisdom=15,
                         con=17, charisma=0, dex=25, exp=random.randint(130, 220))
        self.equipment = dict(Weapon=BirdClaw, Armor=items.NoArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75))
        self.spellbook = {"Spells": {},
                          "Skills": {}}
        self.flying = True


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


# Level 3 Boss
class Cockatrice(Monster):

    def __init__(self):
        super().__init__(name='Cockatrice', health=random.randint(80, 120), mana=99, strength=26, intel=12, wisdom=15,
                         con=16, charisma=0, dex=20, exp=random.randint(250, 375))
        self.equipment = dict(Weapon=BirdClaw, Armor=items.NoArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(120, 150), Potion=items.MasterHealthPotion)
        self.spellbook = {"Spells": {'Petrify': spells.Petrify},
                          "Skills": {}}


class BrownSlime(Slime):

    def __init__(self):
        super().__init__(name='Brown Slime', health=random.randint(50, 80), mana=85, strength=17, intel=15, wisdom=99,
                         con=15, charisma=0, dex=8, exp=random.randint(190, 460))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(150, 280), Potion=items.Elixir)
        self.spellbook = {'Spells': {'Mudslide': spells.Mudslide},
                          'Skills': {}}


class Gargoyle(Construct):

    def __init__(self):
        super().__init__(name='Gargoyle', health=random.randint(55, 75), mana=60, strength=26, intel=10, wisdom=0,
                         con=18, charisma=0, dex=21, exp=random.randint(210, 330))
        self.equipment = dict(Weapon=BirdClaw, Armor=StoneArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(75, 125))
        self.spellbook = {"Spells": {},
                          "Skills": {'Blind': spells.Blind}}
        self.flying = True


class Conjurer(Humanoid):

    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(40, 65), mana=100, strength=14, intel=22, wisdom=18,
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


class Griffin(Monster):

    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(75, 105), mana=110, strength=26, intel=10, wisdom=18,
                         con=18, charisma=0, dex=25, exp=random.randint(240, 450))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(140, 280))
        self.spellbook = {"Spells": {'Hurricane': spells.Hurricane},
                          "Skills": {}}
        self.flying = True


class DrowAssassin(Humanoid):

    def __init__(self):
        super().__init__(name='Drow Assassin', health=random.randint(65, 85), mana=40, strength=24, intel=16, wisdom=15,
                         con=14, charisma=0, dex=28, exp=random.randint(280, 480))
        self.equipment = dict(Weapon=items.AdamantiteDagger, Armor=items.StuddedLeather, OffHand=items.AdamantiteDagger,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(160, 250), Weapon=items.AdamantiteDagger,
                              Armor=items.StuddedLeather, OffHand=items.AdamantiteDagger)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike,
                                     'Backstab': spells.Backstab,
                                     'Kidney Punch': spells.KidneyPunch,
                                     'Mug': spells.Mug,
                                     'Disarm': spells.Disarm2,
                                     'Parry': spells.Parry}}


class Cyborg(Construct):

    def __init__(self):
        super().__init__(name='Cyborg', health=random.randint(90, 120), mana=0, strength=28, intel=13, wisdom=0, con=18,
                         charisma=0, dex=14, exp=random.randint(290, 500))
        self.equipment = dict(Weapon=Laser, Armor=MetalPlating, OffHand=Laser,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(200, 300))
        self.spellbook = {"Spells": {},
                          "Skills": {}}


class DarkKnight(Humanoid):

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(85, 110), mana=50, strength=28, intel=15, wisdom=12,
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
        super().__init__(name='Golem', health=random.randint(180, 250), mana=0, strength=35, intel=10, wisdom=18,
                         con=28, charisma=0, dex=20, exp=random.randint(500, 800))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=StoneArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 600), Potion=items.AardBeing)
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}


class ShadowSerpent(Reptile):

    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=0, strength=28, intel=18,
                         wisdom=15, con=22, charisma=0, dex=23, exp=random.randint(480, 790))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=SnakeFang,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(280, 485), Potion=items.Megalixir)
        self.spellbook = {"Spells": {'Corruption': spells.Corruption2},
                          "Skills": {}}


class Aboleth(Slime):

    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(110, 500), mana=120, strength=25, intel=20, wisdom=50,
                         con=25, charisma=0, dex=10, exp=random.randint(350, 930))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(130, 750), Potion=items.AardBeing)
        self.spellbook = {"Spells": {'Poison Breath': spells.PoisonBreath,
                                     'Terrify': spells.Terrify2},
                          "Skills": {}}


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


class Behemoth(Aberration):

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=100, strength=38, intel=25, wisdom=20,
                         con=30, charisma=0, dex=25, exp=random.randint(620, 950))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide, OffHand=LionPaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 550))
        self.spellbook = {"Spells": {'Holy': spells.Holy3},
                          "Skills": {}}


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


class Basilisk(Reptile):

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(220, 325), mana=120, strength=29, intel=26, wisdom=30,
                         con=27, charisma=0, dex=20, exp=random.randint(630, 900))
        self.equipment = dict(Weapon=SnakeFang, Armor=StoneArmor, OffHand=Gaze,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(380, 520))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}


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


class Warforged(Construct):

    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=200, strength=40, intel=20, wisdom=0,
                         con=33, charisma=0, dex=10, exp=random.randint(580, 880))
        self.equipment = dict(Weapon=items.GreatMaul, Armor=StoneArmor, OffHand=items.NoOffHand,
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


class Wyvern(Dragon):

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(320, 410), mana=0, strength=35, intel=33, wisdom=24,
                         con=30, charisma=0, dex=40, exp=random.randint(650, 900))
        self.equipment = dict(Weapon=DragonClaw, Armor=DragonScale, OffHand=DragonClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(420, 570), Armor=items.DragonHide)
        self.spellbook = {"Spells": {'Tornado': spells.Tornado},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}
        self.flying = True


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


# Level 5 Boss
class RedDragon(Dragon):
    """
    Final Boss; immune to elemental spells and will heal from fire spells; immune to weapon damage except ultimate
      weapons
    """
    def __init__(self):
        super().__init__(name='Red Dragon', health=random.randint(750, 1000), mana=500, strength=50, intel=28,
                         wisdom=35, con=30, charisma=0, dex=22, exp=0)
        self.equipment = dict(Weapon=DragonTail, Armor=DragonScale, OffHand=DragonClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict()
        self.spellbook = {"Spells": {'Renew': spells.Renew,
                                     'Volcano': spells.Volcano,
                                     'Ultima': spells.Ultima},
                          "Skills": {'Mortal Strike': spells.MortalStrike2,
                                     'Multi-Cast': spells.TripleCast}}
        self.flying = True
