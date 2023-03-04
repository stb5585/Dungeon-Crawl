###########################################
""" enemy manager """

# Imports
import random
import time

import items
import spells


# Functions
def random_enemy(level):
    """

    """
    monsters = {'0': [GreenSlime(), Goblin(), GiantRat(), Bandit(), Skeleton()],
                '1': [GiantHornet(), Zombie(), Imp(), GiantSpider(),  Quasit(), Panther(), TwistedDwarf()],
                '2': [Gnoll(), GiantOwl(), Orc(), Vampire(), Direwolf(), RedSlime(), GiantSnake(), GiantScorpion(),
                      Warrior(), Harpy(), Naga(), Wererat()],
                '3': [Ghoul(), Troll(), Direbear(), EvilCrusader(), Ogre(), BlackSlime(), GoldenEagle(), PitViper(),
                      Alligator(), Disciple(), Werewolf()],
                '4': [BrownSlime(), Troll(), Gargoyle(), Conjurer(), Chimera(), Dragonkin(), Griffin(), DrowAssassin(),
                      Cyborg(), DarkKnight(), Myrmidon()],
                '5': [ShadowSerpent(), Aboleth(), Beholder(), Behemoth(), Basilisk(), Hydra(), Lich(), MindFlayer(),
                      Warforged(), Wyrm(), Wyvern()]}

    random_monster = random.choice(monsters[level])
    if random_monster.name == "Myrmidon":
        random_monster = random.choice([FireMyrmidon(), IceMyrmidon(), ElectricMyrmidon(),
                                        WaterMyrmidon(), EarthMyrmidon(), WindMyrmidon()])

    return random_monster


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
        self.enemy_typ = ""

    def __str__(self, inspect=False):
        if inspect:
            return self.inspect()
        else:
            return "Enemy: {}  Health: {}/{}  Mana: {}/{}".format(self.name, self.health, self.health_max, self.mana,
                                                                  self.mana_max)

    def weapon_damage(self, defender):
        pass

    def inspect(self):
        specials = list(self.spellbook['Spells'].keys()) + list(self.spellbook['Skills'].keys())
        specials = ", ".join(specials)
        text = """
        Name: {}
        Type: {}
        Strength: {}
        Intelligence: {}
        Wisdom: {}
        Constitution: {}
        Charisma: {}
        Dexterity: {}
        Resistances: Fire: {}, Ice: {}, Electric: {}, Water: {}, Earth: {}, Wind: {}, 
                     Shadow: {}, Death: {}, Holy: {}, Poison: {}, Physical: {}
        Specials: {}
        """.format(self.name, self.enemy_typ,
                   self.strength, self.intel, self.wisdom, self.con, self.charisma,  self.dex,
                   self.resistance['Fire'], self.resistance['Ice'], self.resistance['Electric'],
                   self.resistance['Water'], self.resistance['Earth'], self.resistance['Wind'],
                   self.resistance['Shadow'], self.resistance['Death'], self.resistance['Holy'],
                   self.resistance['Poison'], self.resistance['Physical'],
                   specials)
        return text

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
        elif mod == 'offhand':
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
        self.resistance['Death'] = 0.75
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
    """
    Electric will heal, immune to poison, strong against physical and earth, weak against water
    """
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Construct'
        self.resistance['Electric'] = 1.25
        self.resistance['Water'] = -0.75
        self.resistance['Earth'] = 0.5
        self.resistance['Poison'] = 1.
        self.resistance['Physical'] = 0.5


# Natural weapons
class NaturalWeapon(items.Weapon):

    def __init__(self, name, damage, crit, description, off):
        super().__init__(name=name, damage=damage, crit=crit, subtyp='Natural', description=description, handed=1,
                         off=off, rarity=0, unequip=False, value=0)


class Bite(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="bites", damage=2, crit=9, description="", off=False)
        self.special = True
        self.disease = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not random.randint(0, 39 // crit):
            print("The bite is diseased, crippling {} and lowering their constitution by 1.".format(target.name))
            target.con -= 1


class Bite2(Bite):
    """

    """
    def __init__(self):
        super().__init__()
        self.damage = 15
        self.crit = 4
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        print("The bite is diseased.")
        if not random.randint(0, 19 // crit):
            print("The disease cripples {}, lowering their constitution by 1.".format(target.name))
            target.con -= 1
        else:
            print("{} resists the disease.".format(target.name))


class WolfClaw(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="swipes", damage=6, crit=6, description="", off=True)


class WolfClaw2(WolfClaw):
    """

    """
    def __init__(self):
        super().__init__()
        self.damage = 8
        self.crit = 4

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.dex // 2) * crit, wielder.dex * crit)\
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.dex // 10)
                bleed_dmg = int(max(wielder.dex // 2, damage) * crit * (1 - resist))
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = duration
                target.status_effects['Bleed'][2] = bleed_dmg
                print("{} is bleeding for {} turns.".format(target.name, duration))


class BearClaw(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="mauls", damage=12, crit=5, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.strength // 2) * crit, wielder.strength * crit)\
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.strength // 10)
                bleed_dmg = int(max(wielder.strength // 2, damage) * crit * (1 - resist))
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = duration
                target.status_effects['Bleed'][2] = bleed_dmg
                print("{} is bleeding for {} turns.".format(target.name, duration))


class Stinger(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="stings", damage=3, crit=4, description="", off=False)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Poison')
        if resist < 1:
            if random.randint((wielder.dex * crit) // 2, (wielder.dex * crit)) \
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.dex // 10)
                pois_dmg = max(1, int(damage * (1 - resist)) * crit)
                target.status_effects['Poison'][0] = True
                target.status_effects['Poison'][1] = duration
                target.status_effects['Poison'][2] = pois_dmg
                print("{} is poisoned for {} turns.".format(target.name, duration))


class BirdClaw(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="claws", damage=5, crit=5, description="", off=True)


class BirdClaw2(BirdClaw):
    """

    """
    def __init__(self):
        super().__init__()
        self.damage = 7
        self.crit = 3

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.dex // 2) * crit, wielder.dex * crit)\
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.dex // 10)
                bleed_dmg = int(max(wielder.dex // 2, damage) * crit * (1 - resist))
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = duration
                target.status_effects['Bleed'][2] = bleed_dmg
                print("{} is bleeding for {} turns.".format(target.name, duration))


class DemonClaw(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="claws", damage=5, crit=3, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', typ=self.subtyp)
        t_chance = target.check_mod('luck', luck_factor=10)
        if resist < 1:
            if random.randint(0, damage) * crit * (1 - resist) \
                    > random.randint(target.con // 2, target.con) + t_chance:
                timer = max(1, 5 // crit)
                target.status_effects["Doom"][0] = True
                target.status_effects["Doom"][1] = timer
                print("{} has been marked by {} for death and "
                      "will expire in {} turns.".format(target.name, wielder.name, timer))


class DemonClaw2(DemonClaw):
    """

    """
    def __init__(self):
        super().__init__()
        self.damage = 10
        self.crit = 2
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', typ=self.subtyp)
        t_chance = target.check_mod('luck', luck_factor=8)
        if resist < 1:
            if random.randint(0, damage) * crit * (1 - resist) \
                    > random.randint(target.con // 2, target.con) + t_chance:
                target.health = 0
                print("{} has there soul ripped from their body.".format(target.name))


class SnakeFang(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="strikes", damage=3, crit=4, description="", off=False)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Poison')
        if resist < 1:
            if random.randint((wielder.dex * crit) // 2, (wielder.dex * crit)) \
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.dex // 10)
                pois_dmg = int(damage * (1 - resist)) * crit
                target.status_effects['Poison'][0] = True
                target.status_effects['Poison'][1] = duration
                target.status_effects['Poison'][2] = pois_dmg
                print("{} is poisoned for {} turns.".format(target.name, duration))


class AlligatorTail(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="swipes", damage=8, crit=8, description="", off=False)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint(0, wielder.strength * crit) \
                    > random.randint(target.con // 2, target.con):
                target.status_effects['Stun'][0] = True
                target.status_effects['Stun'][1] = max(1, wielder.strength // 10)
                print("{} is stunned for {} turns.".format(target.name, max(1, wielder.strength // 10)))


class LionPaw(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="swipes", damage=14, crit=5, description="", off=True)


class Laser(NaturalWeapon):
    """
    ignores armor
    """
    def __init__(self):
        super().__init__(name="zaps", damage=12, crit=3, description="", off=True)
        self.ignore = True


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player to stone
    """
    def __init__(self):
        super().__init__(name="leers", damage=0, crit=5, description="", off=False)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        print("{} {} at {}.".format(wielder.name, self.name, target.name))
        spells.Petrify().cast(wielder, target)


class DragonClaw(NaturalWeapon):
    """
    ignores armor
    """
    def __init__(self):
        super().__init__(name="rakes", damage=10, crit=5, description="", off=True)
        self.ignore = True


class DragonClaw2(DragonClaw):
    """

    """
    def __init__(self):
        super().__init__()
        self.damage = 12
        self.crit = 4
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.strength // 2) * crit, wielder.strength * crit)\
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.strength // 10)
                bleed_dmg = int(max(wielder.strength // 2, damage) * crit * (1 - resist))
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = duration
                target.status_effects['Bleed'][2] = bleed_dmg
                print("{} is bleeding for {} turns.".format(target.name, duration))


class DragonTail(NaturalWeapon):
    """

    """
    def __init__(self):
        super().__init__(name="swipes", damage=14, crit=6, description="", off=True)


class DragonTail2(DragonTail):
    """

    """
    def __init__(self):
        super().__init__()
        self.damage = 25
        self.crit = 4
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint(0, wielder.strength * crit) \
                    > random.randint(target.con // 2, target.con):
                target.status_effects['Stun'][0] = True
                target.status_effects['Stun'][1] = max(1, wielder.strength // 10)
                print("{} is stunned for {} turns.".format(target.name, max(1, wielder.strength // 10)))


class HorseHoof(NaturalWeapon):
    """
    Natural weapon of Nightmare; additional fire damage
    """
    def __init__(self):
        super().__init__(name="stomps", damage=8, crit=4, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Fire')
        damage = int(random.randint(damage // 2, damage) * (1 - resist))
        target.health -= damage
        if damage > 0:
            print("The fire from {}'s hooves burns {} for {} damage.".format(wielder.name, target.name, damage))
        elif damage < 0:
            print("{} absorbs the fire damage and is healed for {} hit points.".format(target.name, abs(damage)))
        else:
            print("The fire is ineffective, dealing {} damage.".format(damage))


class ElementalBlade(NaturalWeapon):
    """
    Innate weapon possessed by Myrmidons; does elemental damage based on the enemy type
    """
    def __init__(self):
        super().__init__(name="attacks", damage=10, crit=3, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        elemental_type = max(wielder.resistance, key=wielder.resistance.get)
        resist = target.check_mod('resist', typ=elemental_type)
        damage = int(damage * (1 - resist))
        if damage < 0:
            print("{} absorbs the {} damage, gaining {} hit points.".format(target.name, elemental_type.lower(),
                                                                            abs(damage)))
        elif damage > 0:
            print("{}'s blade deals {} additional {} damage to {}.".format(wielder.name, damage, elemental_type.lower(),
                                                                           target.name))
        else:
            print("{} damage was not effective against {}.".format(elemental_type, target.name))
        time.sleep(0.25)
        target.health -= damage
        if damage != 0 and elemental_type == "Fire" and target.is_alive():
            print("{} is on fire and will burn for the next 3 turns.".format(target.name))
            target.status_effects['DOT'][0] = True
            target.status_effects['DOT'][1] = 3
            target.status_effects['DOT'][2] = int(damage // 2)
            time.sleep(0.25)


class NaturalArmor(items.Armor):

    def __init__(self, name, armor, description):
        super().__init__(name=name, armor=armor, description=description, rarity=0, subtyp="Natural",
                         unequip=False, value=0)


class AnimalHide(NaturalArmor):

    def __init__(self):
        super().__init__(name='Animal Hide', armor=2, description="")


class AnimalHide2(AnimalHide):

    def __init__(self):
        super().__init__()
        self.armor = 6


class Carapace(NaturalArmor):

    def __init__(self):
        super().__init__(name='Carapace', armor=3, description="")


class StoneArmor(NaturalArmor):

    def __init__(self):
        super().__init__(name='Stone Armor', armor=4, description="")


class MetalPlating(NaturalArmor):

    def __init__(self):
        super().__init__(name='Metal Plating', armor=5, description="")


class DragonScale(NaturalArmor):

    def __init__(self):
        super().__init__(name='Dragon Scales', armor=6, description="")


class NaturalShield(items.OffHand):

    def __init__(self, name, mod, subtyp):
        super().__init__(name=name, mod=mod, subtyp=subtyp, description="", rarity=0, unequip=False, value=0)
        self.name = name
        self.mod = mod
        self.subtyp = subtyp


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
        super().__init__(name="Test", health=999, mana=999, strength=0, intel=0, wisdom=0, con=0, charisma=99, dex=99,
                         exp=0)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {},
                          "Skills": {"Shapeshift": spells.Shapeshift}}


# Starting enemies
class GreenSlime(Slime):
    """

    """
    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(1, 10), mana=0, strength=6, intel=1, wisdom=99,
                         con=8, charisma=1, dex=4, exp=random.randint(1, 20))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(1, 8), Key=items.Key)


class GiantRat(Animal):
    """

    """
    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=0, strength=4, intel=3, wisdom=3, con=6,
                         charisma=6, dex=15, exp=random.randint(7, 14))
        self.equipment = dict(Weapon=Bite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(1, 5))


class Goblin(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(3, 7), mana=0, strength=6, intel=5, wisdom=2, con=8,
                         charisma=12, dex=16, exp=random.randint(7, 16))
        self.gold = random.randint(5, 15)
        self.equipment = dict(Weapon=items.BronzeSword, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=self.gold)
        self.spellbook = {"Spells": {},
                          "Skills": {"Gold Toss": spells.GoldToss}}


class Bandit(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=16, strength=8, intel=8, wisdom=5, con=8,
                         charisma=10, dex=10, exp=random.randint(8, 18))
        self.equipment = dict(Weapon=items.BronzeDagger, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(15, 25))
        self.spellbook = {"Spells": {},
                          "Skills": {'Steal': spells.Steal,
                                     'Disarm': spells.Disarm}}


class Skeleton(Undead):
    """

    """
    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=0, strength=10, intel=4, wisdom=8, con=12,
                         charisma=1, dex=6, exp=random.randint(11, 20))
        self.equipment = dict(Weapon=items.BronzeSword, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(10, 20), Potion=items.HealthPotion)


# Level 1
class GiantHornet(Insect):
    """

    """
    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=0, strength=6, intel=4, wisdom=6,
                         con=6, charisma=8, dex=18, exp=random.randint(13, 24))
        self.equipment = dict(Weapon=Stinger, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(6, 15))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Zombie(Undead):
    """

    """
    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(11, 14), mana=20, strength=15, intel=1, wisdom=5, con=8,
                         charisma=1, dex=8, exp=random.randint(11, 22))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(15, 30), Misc=items.Key)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike}}


class Imp(Fiend):
    """

    """
    def __init__(self):
        super().__init__(name='Imp', health=random.randint(9, 14), mana=25, strength=6, intel=12, wisdom=10,
                         con=8, charisma=12, dex=12, exp=random.randint(15, 24))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(15, 30))
        self.spellbook = {"Spells": {'Shadow Bolt': spells.ShadowBolt,
                                     'Corruption': spells.Corruption,
                                     'Terrify': spells.Terrify},
                          "Skills": {}}


class GiantSpider(Insect):
    """

    """
    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=0, strength=9, intel=10, wisdom=10,
                         con=8, charisma=10, dex=12, exp=random.randint(15, 24))
        self.equipment = dict(Weapon=Stinger, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(15, 30), Potion=items.ManaPotion)
        self.resistance['Poison'] = 0.25


class Quasit(Monster):
    """

    """
    def __init__(self):
        super().__init__(name='Quasit', health=random.randint(13, 17), mana=15, strength=5, intel=8, wisdom=10,
                         con=11, charisma=14, dex=16, exp=random.randint(25, 44))
        self.equipment = dict(Weapon=DemonClaw, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(25, 40))
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike}}


class Panther(Animal):
    """
    Transform Level 1 creature
    """
    def __init__(self):
        super().__init__(name='Panther', health=random.randint(10, 14), mana=25, strength=10, intel=8, wisdom=8,
                         con=10, charisma=10, dex=13, exp=random.randint(19, 28))
        self.equipment = dict(Weapon=WolfClaw, Armor=AnimalHide, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(18, 35))
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': spells.Backstab,
                                     'Kidney Punch': spells.KidneyPunch,
                                     'Disarm': spells.Disarm,
                                     'Parry': spells.Parry}}
        self.resistance['Physical'] = 0.25


class TwistedDwarf(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Twisted Dwarf', health=random.randint(15, 19), mana=10, strength=12, intel=8, wisdom=10,
                         con=12, charisma=8, dex=12, exp=random.randint(25, 44))
        self.equipment = dict(Weapon=items.Axe, Armor=items.HideArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(25, 40), Weapon=items.Axe)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}


class Minotaur(Monster):
    """
    Level 1 Boss
    """
    def __init__(self):
        super().__init__(name='Minotaur', health=random.randint(40, 64), mana=20, strength=18, intel=8, wisdom=10,
                         con=14, charisma=14, dex=12, exp=random.randint(110, 250))
        self.equipment = dict(Weapon=items.BattleAxe, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(30, 75), Weapon=items.BattleAxe, Armor=items.Cuirboulli)
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': spells.MortalStrike,
                                     'Disarm': spells.Disarm,
                                     'Parry': spells.Parry}}
        self.resistance['Death'] = 1


class Barghest(Fiend):
    """
    Level 1 Extra Boss - guards first of six relics required to beat the final boss
    Can shapeshift between Direwolf, Goblin, and Hybrid (natural) forms
    """
    def __init__(self):
        super().__init__(name='Barghest', health=random.randint(100, 145), mana=80, strength=25, intel=15, wisdom=14,
                         con=18, charisma=14, dex=16, exp=random.randint(300, 500))
        self.gold = random.randint(150, 280)
        self.equipment = dict(Weapon=WolfClaw2, Armor=AnimalHide, OffHand=WolfClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=self.gold)
        self.spellbook = {"Spells": {'Disease Breath': spells.DiseaseBreath},
                          "Skills": {'Shapeshift': spells.Shapeshift}}
        self.resistance['Death'] = 1
        self.resistance['Physical'] = 0.25
        self.transform = [Barghest, Goblin, Direwolf]


# Level 2
class Gnoll(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Gnoll', health=random.randint(16, 24), mana=20, strength=13, intel=10, wisdom=5, con=8,
                         charisma=12, dex=16, exp=random.randint(45, 85))
        self.equipment = dict(Weapon=items.Spear, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(30, 60), Weapon=items.Spear)
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': spells.Disarm}}


class GiantSnake(Reptile):
    """

    """
    def __init__(self):
        super().__init__(name='Giant Snake', health=random.randint(18, 26), mana=0, strength=15, intel=5, wisdom=6,
                         con=14, charisma=10, dex=16, exp=random.randint(60, 100))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 75))
        self.resistance['Poison'] = 0.25


class Orc(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Orc', health=random.randint(17, 28), mana=14, strength=12, intel=6, wisdom=5, con=10,
                         charisma=8, dex=14, exp=random.randint(45, 80))
        self.equipment = dict(Weapon=items.IronSword, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(20, 65), Weapon=items.IronSword)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}


class GiantOwl(Animal):
    """

    """
    def __init__(self):
        super().__init__(name='Giant Owl', health=random.randint(12, 17), mana=0, strength=11, intel=12, wisdom=10,
                         con=10, charisma=1, dex=14, exp=random.randint(45, 80))
        self.equipment = dict(Weapon=BirdClaw, Armor=items.NoArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(20, 65))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Vampire(Undead):
    """

    """
    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(20, 28), mana=30, strength=20, intel=14, wisdom=12,
                         con=15, charisma=1, dex=14, exp=random.randint(50, 90))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 90), Potion=items.GreatHealthPotion)
        self.spellbook = {"Spells": {},
                          "Skills": {'Health Drain': spells.HealthDrain}}


class Direwolf(Animal):
    """

    """
    def __init__(self):
        super().__init__(name='Direwolf', health=random.randint(16, 20), mana=0, strength=17, intel=7, wisdom=6, con=14,
                         charisma=10, dex=16, exp=random.randint(60, 100))
        self.equipment = dict(Weapon=WolfClaw, Armor=AnimalHide, OffHand=WolfClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 75))
        self.spellbook = {"Spells": {},
                          "Skills": {'Howl': spells.Howl}}
        self.resistance['Physical'] = 0.25


class Wererat(Monster):
    """

    """
    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(14, 17), mana=0, strength=14, intel=6, wisdom=12, con=11,
                         charisma=8, dex=18, exp=random.randint(57, 94))
        self.equipment = dict(Weapon=Bite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 65))


class RedSlime(Slime):
    """

    """
    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(8, 20), mana=30, strength=10, intel=15, wisdom=99,
                         con=12, charisma=10, dex=5, exp=random.randint(43, 150))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(20, 120), Potion=items.SuperHealthPotion)
        self.spellbook = {'Spells': {'Firebolt': spells.Firebolt},
                          'Skills': {}}


class GiantScorpion(Insect):
    """

    """
    def __init__(self):
        super().__init__(name='Giant Scorpion', health=random.randint(13, 18), mana=0, strength=14, intel=5, wisdom=10,
                         con=12, charisma=10, dex=9, exp=random.randint(65, 105))
        self.equipment = dict(Weapon=Stinger, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 65))
        self.resistance['Poison'] = 0.25


class Warrior(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(22, 31), mana=25, strength=14, intel=10, wisdom=8,
                         con=12, charisma=10, dex=8, exp=random.randint(65, 110))
        self.equipment = dict(Weapon=items.IronSword, Armor=items.RingMail, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(25, 100), Weapon=items.IronSword, Armor=items.RingMail)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike,
                                     'Disarm': spells.Disarm2,
                                     'Parry': spells.Parry}}


class Harpy(Monster):
    """

    """
    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=0, strength=18, intel=13, wisdom=13,
                         con=14, charisma=14, dex=23, exp=random.randint(65, 115))
        self.equipment = dict(Weapon=BirdClaw, Armor=items.NoArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Naga(Monster):
    """

    """
    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=0, strength=15, intel=13, wisdom=15,
                         con=15, charisma=12, dex=17, exp=random.randint(67, 118))
        self.equipment = dict(Weapon=items.Spear, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(55, 75), Weapon=items.Spear, Potion=items.GreatManaPotion)
        self.resistance['Electric'] = -0.5
        self.resistance['Water'] = 0.75


class Pseudodragon(Dragon):
    """
    Level 2 Boss
    """
    def __init__(self):
        super().__init__(name='Pseudodragon', health=random.randint(90, 135), mana=100, strength=28, intel=16,
                         wisdom=16, con=20, charisma=20, dex=14, exp=random.randint(250, 450))
        self.gold = random.randint(100, 400)
        self.equipment = dict(Weapon=DragonClaw, Armor=DragonScale, OffHand=DragonClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=self.gold, Potion=items.SuperManaPotion)
        self.spellbook = {'Spells': {'Fireball': spells.Fireball,
                                     'Blinding Fog': spells.BlindingFog},
                          'Skills': {'Gold Toss': spells.GoldToss}}


class Nightmare(Fiend):
    """
    Level 2 Extra Boss - guards second of six relics required to beat the final boss
    """
    def __init__(self):
        super().__init__(name='Nightmare', health=random.randint(180, 310), mana=100, strength=30, intel=17,
                         wisdom=15, con=22, charisma=16, dex=15, exp=random.randint(400, 550))
        self.equipment = dict(Weapon=HorseHoof, Armor=AnimalHide2, OffHand=HorseHoof,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(250, 400))
        self.spellbook = {'Spells': {'Sleep': spells.Sleep,
                                     'Firestorm': spells.Fireball},
                          'Skills': {}}
        self.resistance['Fire'] = 1
        self.resistance['Ice'] = -0.25
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25
        self.resistance['Death'] = 1
        self.resistance['Physical'] = 0.5
        self.flying = True


# Level 3
class Direbear(Animal):
    """
    Transform Level 2 creature
    """
    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=0, strength=25, intel=6, wisdom=6, con=26,
                         charisma=12, dex=18, exp=random.randint(110, 210))
        self.equipment = dict(Weapon=BearClaw, Armor=AnimalHide2, OffHand=BearClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(45, 60))
        self.spellbook = {'Spells': {},
                          'Skills': {'Piercing Strike': spells.PiercingStrike,
                                     'Parry': spells.Parry}}
        self.resistance['Physical'] = 0.5


class Ghoul(Undead):
    """

    """
    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=50, strength=23, intel=10, wisdom=8, con=24,
                         charisma=1, dex=12, exp=random.randint(110, 190))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 45), Potion=items.SuperHealthPotion)
        self.spellbook = {"Spells": {'Disease Breath': spells.DiseaseBreath},
                          "Skills": {}}


class PitViper(Reptile):
    """

    """
    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=30, strength=17, intel=6, wisdom=8,
                         con=16, charisma=10, dex=18, exp=random.randint(115, 190))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 85))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Poison'] = 0.25


class Disciple(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=70, strength=16, intel=17, wisdom=15,
                         con=16, charisma=12, dex=16, exp=random.randint(110, 190))
        self.equipment = dict(Weapon=items.SteelDagger, Armor=items.SilverCloak, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(55, 95), Potion=items.SuperManaPotion, Weapon=items.SteelDagger,
                              Armor=items.SilverCloak)
        self.spellbook = {'Spells': {'Firebolt': spells.Firebolt,
                                     'Ice Lance': spells.IceLance,
                                     'Shock': spells.Shock,
                                     'Blinding Fog': spells.BlindingFog},
                          'Skills': {}}


class BlackSlime(Slime):
    """

    """
    def __init__(self):
        super().__init__(name='Black Slime', health=random.randint(25, 60), mana=80, strength=13, intel=20, wisdom=99,
                         con=15, charisma=12, dex=6, exp=random.randint(85, 260))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(30, 180), Potion=items.Elixir)
        self.spellbook = {'Spells': {'Shadow Bolt': spells.ShadowBolt,
                                     'Corruption': spells.Corruption},
                          'Skills': {}}


class Ogre(Monster):
    """

    """
    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=40, strength=22, intel=14, wisdom=14, con=20,
                         charisma=10, dex=14, exp=random.randint(115, 195))
        self.equipment = dict(Weapon=items.IronHammer, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75), Weapon=items.IronHammer, Armor=items.Cuirboulli)
        self.spellbook = {"Spells": {'Magic Missile': spells.MagicMissile},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}


class Alligator(Reptile):
    """

    """
    def __init__(self):
        super().__init__(name='Alligator', health=random.randint(60, 75), mana=20, strength=21, intel=8, wisdom=7,
                         con=20, charisma=10, dex=15, exp=random.randint(120, 200))
        self.equipment = dict(Weapon=AlligatorTail, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(40, 50))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}


class Troll(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=20, strength=21, intel=10, wisdom=8, con=24,
                         charisma=12, dex=15, exp=random.randint(125, 210))
        self.equipment = dict(Weapon=items.GreatAxe, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(35, 45), Weapon=items.GreatAxe, Armor=items.Cuirboulli)
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': spells.MortalStrike}}


class GoldenEagle(Animal):
    """

    """
    def __init__(self):
        super().__init__(name='Golden Eagle', health=random.randint(40, 50), mana=0, strength=19, intel=15, wisdom=15,
                         con=17, charisma=15, dex=25, exp=random.randint(130, 220))
        self.equipment = dict(Weapon=BirdClaw2, Armor=items.NoArmor, OffHand=BirdClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(50, 75))
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class EvilCrusader(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=50, strength=21, intel=18, wisdom=17,
                         con=26, charisma=14, dex=14, exp=random.randint(140, 225))
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


class Werewolf(Monster):
    """
    Transform Level 3 creature
    """
    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(55, 75), mana=0, strength=24, intel=10, wisdom=10,
                         con=20, charisma=14, dex=20, exp=random.randint(120, 200))
        self.equipment = dict(Weapon=WolfClaw2, Armor=AnimalHide2, OffHand=WolfClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(45, 55))
        self.spellbook = {"Spells": {'Howl': spells.Howl},
                          "Skills": {'Multi-Strike': spells.TripleStrike,
                                     'Parry': spells.Parry}}
        self.resistance['Physical'] = 0.5


class Cockatrice(Monster):
    """
    Level 3 Boss
    """
    def __init__(self):
        super().__init__(name='Cockatrice', health=random.randint(200, 350), mana=99, strength=30, intel=16, wisdom=15,
                         con=16, charisma=16, dex=22, exp=random.randint(500, 675))
        self.equipment = dict(Weapon=BirdClaw2, Armor=items.NoArmor, OffHand=DragonTail,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 670), Potion=items.MasterHealthPotion)
        self.spellbook = {"Spells": {'Petrify': spells.Petrify},
                          "Skills": {}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25
        self.resistance['Death'] = 1


class Wendigo(Fey):
    """
    Level 3 Special Boss - guards third of six relics required to beat the final boss
    """
    def __init__(self):
        super().__init__(name='Wendigo', health=random.randint(280, 410), mana=130, strength=32, intel=16, wisdom=19,
                         con=21, charisma=14, dex=22, exp=random.randint(650, 875))
        self.equipment = dict(Weapon=Bite2, Armor=items.NoArmor, OffHand=DemonClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(800, 1050))
        self.spellbook = {"Spells": {'Regen': spells.Regen2},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.flying = True
        self.resistance['Fire'] = -0.75
        self.resistance['Ice'] = 1
        self.resistance['Earth'] = 1
        self.resistance['Death'] = 1
        self.resistance['Poison'] = 1


# Level 4
class BrownSlime(Slime):
    """

    """
    def __init__(self):
        super().__init__(name='Brown Slime', health=random.randint(50, 80), mana=85, strength=17, intel=30, wisdom=99,
                         con=15, charisma=10, dex=8, exp=random.randint(190, 460))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(150, 280), Potion=items.Vedas)
        self.spellbook = {'Spells': {'Mudslide': spells.Mudslide},
                          'Skills': {}}


class Gargoyle(Construct):
    """

    """
    def __init__(self):
        super().__init__(name='Gargoyle', health=random.randint(55, 75), mana=20, strength=26, intel=10, wisdom=12,
                         con=18, charisma=15, dex=21, exp=random.randint(210, 330))
        self.equipment = dict(Weapon=BirdClaw2, Armor=StoneArmor, OffHand=BirdClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(75, 125))
        self.spellbook = {"Spells": {},
                          "Skills": {'Blind': spells.Blind}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Conjurer(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(40, 65), mana=150, strength=14, intel=22, wisdom=18,
                         con=14, charisma=12, dex=13, exp=random.randint(215, 340))
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
    """

    """
    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(60, 95), mana=140, strength=26, intel=14, wisdom=16,
                         con=20, charisma=14, dex=14, exp=random.randint(230, 380))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide2, OffHand=LionPaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(100, 250), Potion=items.SuperManaPotion)
        self.spellbook = {"Spells": {'Molten Rock': spells.MoltenRock},
                          "Skills": {}}
        self.resistance['Physical'] = 0.5


class Dragonkin(Dragon):
    """

    """
    def __init__(self):
        super().__init__(name='Dragonkin', health=random.randint(80, 115), mana=90, strength=26, intel=10, wisdom=18,
                         con=20, charisma=18, dex=20, exp=random.randint(250, 480))
        self.equipment = dict(Weapon=items.Halberd, Armor=items.Breastplate, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(150, 300), Weapon=items.Halberd, Armor=items.Breastplate)
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': spells.Disarm2}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Griffin(Monster):
    """

    """
    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(75, 105), mana=110, strength=26, intel=21, wisdom=18,
                         con=18, charisma=16, dex=25, exp=random.randint(240, 450))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide2, OffHand=BirdClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(140, 280), Potion=items.Elixir)
        self.spellbook = {"Spells": {'Hurricane': spells.Hurricane},
                          "Skills": {}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25
        self.resistance['Physical'] = 0.5


class DrowAssassin(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Drow Assassin', health=random.randint(65, 85), mana=75, strength=24, intel=16, wisdom=15,
                         con=14, charisma=22, dex=28, exp=random.randint(280, 480))
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
    """

    """
    def __init__(self):
        super().__init__(name='Cyborg', health=random.randint(90, 120), mana=80, strength=28, intel=13, wisdom=10,
                         con=18, charisma=10, dex=14, exp=random.randint(290, 500))
        self.equipment = dict(Weapon=Laser, Armor=MetalPlating, OffHand=Laser,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(200, 300))
        self.spellbook = {"Spells": {'Shock': spells.Shock},
                          "Skills": {}}


class DarkKnight(Humanoid):
    """

    """
    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(85, 110), mana=60, strength=28, intel=15, wisdom=12,
                         con=21, charisma=14, dex=17, exp=random.randint(300, 550))
        self.equipment = dict(Weapon=items.Trident, Armor=items.PlateMail, OffHand=items.TowerShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(300, 420), Weapon=items.Trident,
                              Armor=items.PlateMail, OffHand=items.TowerShield)
        self.spellbook = {"Spells": {'Enhance Blade': spells.EnhanceBlade},
                          "Skills": {'Shield Slam': spells.ShieldSlam2,
                                     'Disarm': spells.Disarm3,
                                     'Shield Block': spells.ShieldBlock}}


class Myrmidon(Elemental):
    """

    """
    def __init__(self):
        super().__init__(name='Myrmidon', health=random.randint(75, 125), mana=75, strength=26, intel=18, wisdom=16,
                         con=18, charisma=10, dex=14, exp=random.randint(320, 600))
        self.equipment = dict(Weapon=ElementalBlade, Armor=items.PlateMail, OffHand=items.KiteShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(300, 450), Armor=items.PlateMail, OffHand=items.KiteShield)
        self.resistance['Poison'] = 1


class FireMyrmidon(Myrmidon):
    """
    Fire elemental; gains fire DOT applied to elemental blade
    """
    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Scorch': spells.Scorch},
                          "Skills": {'Shield Slam': spells.ShieldSlam2}}
        self.resistance['Fire'] = 1.5
        self.resistance['Ice'] = -0.5


class IceMyrmidon(Myrmidon):
    """
    Ice elemental; gains Mortal Strike
    """
    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Ice Lance': spells.IceLance},
                          "Skills": {'Shield Slam': spells.ShieldSlam2,
                                     'Mortal Strike': spells.MortalStrike}}
        self.resistance['Fire'] = -0.5
        self.resistance['Ice'] = 1.5


class ElectricMyrmidon(Myrmidon):
    """
    Electric elemental; gains Piercing Strike
    """
    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Shock': spells.Shock},
                          "Skills": {'Shield Slam': spells.ShieldSlam2,
                                     'Piercing Strike': spells.PiercingStrike}}
        self.resistance['Electric'] = 1.5
        self.resistance['Water'] = -0.5


class WaterMyrmidon(Myrmidon):
    """
    Water elemental; gains Parry
    """
    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Water Jet': spells.WaterJet},
                          "Skills": {'Shield Slam': spells.ShieldSlam2,
                                     'Parry': spells.Parry}}
        self.resistance['Electric'] = -0.5
        self.resistance['Water'] = 1.5


class EarthMyrmidon(Myrmidon):
    """
    Earth elemental; gains Shield Block
    """
    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Tremor': spells.Tremor},
                          "Skills": {'Shield Slam': spells.ShieldSlam2,
                                     'Shield Block': spells.ShieldBlock}}
        self.resistance['Earth'] = 1.5
        self.resistance['Wind'] = -0.5


class WindMyrmidon(Myrmidon):
    """
    Wind elemental; gains Double Strike
    """
    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Gust': spells.Gust},
                          "Skills": {'Shield Slam': spells.ShieldSlam2,
                                     'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Earth'] = -0.5
        self.resistance['Wind'] = 1.5


class Golem(Construct):
    """
    Level 4 boss
    """
    def __init__(self):
        super().__init__(name='Golem', health=random.randint(300, 500), mana=100, strength=35, intel=10, wisdom=18,
                         con=28, charisma=12, dex=20, exp=random.randint(500, 800))
        self.equipment = dict(Weapon=Laser, Armor=StoneArmor, OffHand=ForceField2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 600), Potion=items.AardBeing)
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}


class Jester(Humanoid):
    """
    Level 4 Special Boss - guards fourth of six relics required to beat the final boss
    """
    def __init__(self):
        super().__init__(name="Jester", health=random.randint(50, 500), mana=random.randint(25, 200),
                         strength=random.randint(10, 40), intel=random.randint(10, 40), wisdom=random.randint(10, 40),
                         con=random.randint(10, 40), charisma=99, dex=random.randint(10, 40),
                         exp=random.randint(1, 1000))
        self.gold = random.randint(25, 10000)
        self.equipment = dict(Weapon=items.MithrilDagger, Armor=items.StuddedCuirboulli, OffHand=items.MithrilDagger,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=self.gold, Item=items.random_item(random.randint(1, 5)))
        self.spellbook = {"Spells": {},
                          "Skills": {'Gold Toss': spells.GoldToss,
                                     'Slot Machine': spells.SlotMachine}}
        self.resistance = {'Fire': random.uniform(-1, 1),
                           'Ice': random.uniform(-1, 1),
                           'Electric': random.uniform(-1, 1),
                           'Water': random.uniform(-1, 1),
                           'Earth': random.uniform(-1, 1),
                           'Wind': random.uniform(-1, 1),
                           'Shadow': random.uniform(-1, 1),
                           'Death': random.uniform(-1, 1),
                           'Holy': random.uniform(-1, 1),
                           'Poison': random.uniform(-1, 1),
                           'Physical': random.uniform(-1, 1)}


# Level 5
class ShadowSerpent(Reptile):
    """

    """
    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=100, strength=28, intel=18,
                         wisdom=15, con=22, charisma=16, dex=23, exp=random.randint(480, 790))
        self.equipment = dict(Weapon=SnakeFang, Armor=items.NoArmor, OffHand=SnakeFang,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(280, 485), Potion=items.Megalixir)
        self.spellbook = {"Spells": {'Corruption': spells.Corruption2},
                          "Skills": {}}
        self.resistance['Shadow'] = 0.9
        self.resistance['Holy'] = -0.75
        self.resistance['Poison'] = 0.25


class Aboleth(Slime):
    """

    """
    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(110, 500), mana=120, strength=25, intel=45, wisdom=50,
                         con=25, charisma=12, dex=10, exp=random.randint(350, 930))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(130, 750), Potion=items.AardBeing)
        self.spellbook = {"Spells": {'Poison Breath': spells.PoisonBreath,
                                     'Disease Breath': spells.DiseaseBreath,
                                     'Terrify': spells.Terrify2},
                          "Skills": {}}
        self.resistance['Poison'] = 1.5


class Beholder(Aberration):
    """

    """
    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=100, strength=25, intel=40, wisdom=35,
                         con=28, charisma=20, dex=20, exp=random.randint(500, 900))
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
    """

    """
    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=100, strength=38, intel=25, wisdom=20,
                         con=30, charisma=18, dex=25, exp=random.randint(620, 950))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide2, OffHand=LionPaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 550))
        self.spellbook = {"Spells": {'Holy': spells.Holy3},
                          "Skills": {}}
        self.resistance['Death'] = 0.9
        self.resistance['Holy'] = 0.75
        self.resistance['Physical'] = 0.5


class Lich(Undead):
    """

    """
    def __init__(self):
        super().__init__(name='Lich', health=random.randint(210, 300), mana=120, strength=25, intel=35, wisdom=40,
                         con=20, charisma=16, dex=22, exp=random.randint(580, 920))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.WizardRobe, OffHand=items.Necronomicon,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 530), Armor=items.WizardRobe, OffHand=items.Necronomicon)
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
    """

    """
    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(220, 325), mana=120, strength=29, intel=26, wisdom=30,
                         con=27, charisma=17, dex=20, exp=random.randint(630, 900))
        self.equipment = dict(Weapon=SnakeFang, Armor=StoneArmor, OffHand=Gaze,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(380, 520))
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Death'] = 1
        self.resistance['Poison'] = 0.75


class MindFlayer(Aberration):
    """

    """
    def __init__(self):
        super().__init__(name='Mind Flayer', health=random.randint(190, 285), mana=150, strength=28, intel=40,
                         wisdom=35, con=25, charisma=22, dex=18, exp=random.randint(590, 850))
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
    """

    """
    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=200, strength=40, intel=20, wisdom=16,
                         con=33, charisma=12, dex=10, exp=random.randint(580, 880))
        self.equipment = dict(Weapon=items.GreatMaul, Armor=StoneArmor, OffHand=ForceField3,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(380, 490))
        self.spellbook = {"Spells": {'Earthquake': spells.Earthquake},
                          "Skills": {'Piercing Strike': spells.PiercingStrike,
                                     'Parry': spells.Parry}}


class Wyrm(Dragon):
    """

    """
    def __init__(self):
        super().__init__(name='Wyrm', health=random.randint(320, 400), mana=150, strength=38, intel=28, wisdom=30,
                         con=28, charisma=22, dex=23, exp=random.randint(620, 880))
        self.equipment = dict(Weapon=DragonTail2, Armor=DragonScale, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(650, 830))
        self.spellbook = {'Spells': {'Volcano': spells.Volcano},
                          'Skills': {'Multi-Strike': spells.DoubleStrike}}


class Hydra(Monster):
    """

    """
    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(260, 375), mana=150, strength=37, intel=30, wisdom=26,
                         con=28, charisma=24, dex=22, exp=random.randint(600, 850))
        self.equipment = dict(Weapon=Bite2, Armor=DragonScale, OffHand=DragonTail,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(400, 550))
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
    """

    """
    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(320, 410), mana=150, strength=35, intel=33, wisdom=24,
                         con=30, charisma=25, dex=40, exp=random.randint(650, 900))
        self.equipment = dict(Weapon=DragonClaw2, Armor=DragonScale, OffHand=DragonClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict(Gold=random.randint(420, 570))
        self.spellbook = {"Spells": {'Tornado': spells.Tornado},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}
        self.flying = True
        self.resistance['Earth'] = 1
        self.resistance['Wind'] = -0.25


class Domingo(Aberration):
    """
    Special enemy; casts enemy skill Ultima
    """
    def __init__(self):
        super().__init__(name='Domingo', health=random.randint(500, 700), mana=999, strength=0, intel=50, wisdom=40,
                         con=45, charisma=60, dex=50, exp=random.randint(2000, 3000))
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
    Transform Level 5 creature
    Highly resistant to spells and will heal from fire spells
    """
    def __init__(self):
        super().__init__(name='Red Dragon', health=random.randint(750, 1000), mana=500, strength=50, intel=28,
                         wisdom=35, con=30, charisma=40, dex=22, exp=random.randint(5000, 10000))
        self.equipment = dict(Weapon=DragonTail2, Armor=DragonScale, OffHand=DragonClaw2,
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
                           'Earth': 1.,
                           'Wind': -0.25,
                           'Shadow': 0.5,
                           'Death': 1.,
                           'Holy': 0.5,
                           'Poison': 0.75}


# Final Boss
class Cthulhu(Aberration):
    """
    Final Boss; highly resistant to spells; immune to weapon damage except ultimate weapons TODO
    """
    def __init__(self):
        super().__init__(name='Cthulhu', health=3000, mana=1000, strength=48, intel=45, wisdom=60, con=45, charisma=80,
                         dex=28, exp=0)
        self.equipment = dict(Weapon=Gaze, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory = dict()
        self.spellbook = {"Spells": {'Magic Missile': spells.MagicMissile3,
                                     'Regen': spells.Regen3,
                                     'Boost': spells.Boost,
                                     'Desoul': spells.Desoul,
                                     'Terrify': spells.Terrify3},
                          "Skills": {'Slot Machine': spells.SlotMachine}}
        self.flying = True
        self.resistance = {'Fire': 0.5,
                           'Ice': 0.5,
                           'Electric': 0.5,
                           'Water': 0.5,
                           'Earth': 1.,
                           'Wind': 0.5,
                           'Shadow': 0.5,
                           'Death': 1.,
                           'Holy': 0.5,
                           'Poison': 1.,
                           'Physical': 1.}


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
            print_list = []
            for skill in skill_list:
                time.sleep(0.5)
                print_list.append(skill().name)
                self.spellbook['Skills'][skill().name] = skill
            print("Specials: " + ", ".join(print_list))
        else:
            self.pro_level = 3
            time.sleep(0.5)
            print_list = [spells.Resurrection().name]
            self.spellbook['Spells']['Resurrection'] = spells.Resurrection
            time.sleep(0.5)
            print_list.append(spells.Disarm3().name)
            self.spellbook['Skills']['Disarm'] = spells.Disarm3
            print("Specials: " + ", ".join(print_list))


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
            print_list = []
            for spell in spell_list:
                time.sleep(0.5)
                print_list.append(spell().name)
                self.spellbook['Spells'][spell().name] = spell
            print("Specials: " + ", ".join(print_list))
        else:
            self.pro_level = 3
            spell_list = [spells.Cleanse, spells.Heal3, spells.Regen3]
            print_list = []
            for spell in spell_list:
                time.sleep(0.5)
                print_list.append(spell().name)
                self.spellbook['Spells'][spell().name] = spell
            print("Specials: " + ", ".join(print_list))


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
            print_list = []
            for spell in spell_list:
                time.sleep(0.5)
                print_list.append(spell().name)
                self.spellbook['Spells'][spell().name] = spell
            print("Specials: " + ", ".join(print_list))
        else:
            self.pro_level = 3
            spell_list = [spells.Firestorm, spells.IceBlizzard, spells.Electrocution,
                          spells.MagicMissile3, spells.Ultima]
            print_list = []
            for spell in spell_list:
                time.sleep(0.5)
                print_list.append(spell().name)
                self.spellbook['Spells'][spell().name] = spell
            print("Specials: " + ", ".join(print_list))


class Jinkin(Fey):
    """
    Familiar - cast (mostly) helpful luck abilities
    Level 1: Can cast Corruption and use Gold Toss (uses player gold) and Steal (items go to player inventory)
    Level 2: Gains Sleeping Powder and will unlock Treasure chests
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
            skill_list = [spells.SleepingPowder, spells.Lockpick]
            print_list = []
            for skill in skill_list:
                time.sleep(0.5)
                print_list.append(skill().name)
                self.spellbook['Spells'][skill().name] = skill
            time.sleep(0.5)
            print_list.append(spells.Corruption2().name)
            self.spellbook['Spells']['Corruption'] = spells.Corruption2
            print("Specials: " + ", ".join(print_list))
        else:
            self.pro_level = 3
            print("Specials: " + spells.SlotMachine().name)
            self.spellbook['Skills']['Slot Machine'] = spells.SlotMachine
