###########################################
""" enemy manager """

# Imports
import random
import time

from character import Character
import items
import spells


# Functions
def random_enemy(level):
    """
    Takes the current level a player is on and returns a random enemy
    """

    monsters = {'0': [GreenSlime(), Goblin(), GiantRat(), Bandit(), Skeleton(), Scarecrow()],
                '1': [GiantCentipede(), GiantHornet(), ElectricBat(), Zombie(), Imp(), GiantSpider(), Quasit(),
                      Panther(), TwistedDwarf(), BattleToad(), Satyr()],
                '2': [Panther(), TwistedDwarf(), BattleToad(), Satyr(), Gnoll(), GiantOwl(), Orc(), Vampire(),
                      VampireBat(), Direwolf(), RedSlime(), GiantSnake(), GiantScorpion(), Warrior(), Harpy(), Naga(),
                      Wererat(), Xorn(), SteelPredator()],
                '3': [Clannfear(), Ghoul(), Troll(), Direbear(), EvilCrusader(), Ogre(), BlackSlime(), GoldenEagle(),
                      PitViper(), Alligator(), Disciple(), Werewolf(), Antlion(), InvisibleStalker(), NightHag(),
                      Treant(), Ankheg()],
                '4': [Antlion(), InvisibleStalker(), NightHag(), BrownSlime(), Troll(), Gargoyle(), Conjurer(),
                      Chimera(), Dragonkin(), Griffin(), DrowAssassin(), Cyborg(), DarkKnight(), Myrmidon(),
                      DisplacerBeast()],
                '5': [Myrmidon(), DisplacerBeast(), ShadowSerpent(), Aboleth(), Beholder(), Behemoth(), Basilisk(),
                      Hydra(), Lich(), MindFlayer(), Sandworm(), Warforged(), Wyrm(), Wyvern(), Archvile(),
                      BrainGorger()],
                '6': [Beholder(), Behemoth(), Lich(), MindFlayer(), Wyvern(), Archvile(), BrainGorger()]}

    random_monster = random.choice(monsters[level])
    # random_monster = Cockatrice()
    if random_monster.name == "Myrmidon":
        random_monster = random.choice([FireMyrmidon(), IceMyrmidon(), ElectricMyrmidon(),
                                        WaterMyrmidon(), EarthMyrmidon(), WindMyrmidon()])

    return random_monster


class Enemy(Character):
    """
    Same as player character with notable exceptions
    cls: just the name of the enemy (used for transforming and other class checks)
    experience: number of experience points awarded for defeating the enemy
    enemy_typ: defines the base type template used for enemy
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__()
        self.name = name
        self.cls = name
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
        self.action_stack = []

    def __str__(self, inspect=False):
        if inspect:
            return self.inspect()
        else:
            return "Enemy: {}  Health: {}/{}  Mana: {}/{}".format(self.name, self.health, self.health_max, self.mana,
                                                                  self.mana_max)

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
                     Shadow: {}, Death: {}, Stone: {}, Holy: {}, Poison: {}, Physical: {}
        Specials: {}
        """.format(self.name, self.enemy_typ,
                   self.strength, self.intel, self.wisdom, self.con, self.charisma, self.dex,
                   self.resistance['Fire'], self.resistance['Ice'], self.resistance['Electric'],
                   self.resistance['Water'], self.resistance['Earth'], self.resistance['Wind'],
                   self.resistance['Shadow'], self.resistance['Death'], self.resistance['Stone'],
                   self.resistance['Holy'], self.resistance['Poison'], self.resistance['Physical'],
                   specials)
        return text

    def options(self, action_list=None):
        if not self.turtle:
            if self.name != 'Test':
                action_list = ['Attack']
            else:
                action_list = []
            if not self.status_effects['Silence'][0]:
                for spell_name, spell in self.spellbook['Spells'].items():
                    if self.spellbook['Spells'][spell_name]().passive:
                        continue
                    elif self.spellbook['Spells'][spell_name]().cost <= self.mana:
                        action_list.append(spell)
            for skill_name, skill in self.spellbook['Skills'].items():
                if self.spellbook['Skills'][skill_name]().passive:
                    continue
                elif self.spellbook['Skills'][skill_name]().cost <= self.mana:
                    action_list.append(skill)
            action = random.choice(action_list)
            if self.action_stack:
                pass  # TODO
            return action

    def combat_turn(self, enemy, action, combat, tile=None):
        valid_entry = True
        cover = False
        flee = False
        fail_flee = False
        if any([self.status_effects['Stun'][0], self.status_effects['Sleep'][0]]):
            combat = True
        else:
            time.sleep(0.5)
            if enemy.cls in ['Warlock', 'Shadowcaster']:
                if 'Cover' in list(enemy.familiar.spellbook['Skills'].keys()) and not random.randint(0, 3):
                    cover = True
            if (enemy.pro_level * enemy.level) >= 10 and enemy.pro_level > self.pro_level and \
                    random.randint(0, enemy.pro_level - self.pro_level) and 'Boss' not in tile.__str__() and \
                    self.name != 'Mimic':
                if not random.randint(0, 1):
                    if random.randint(0, self.dex) > random.randint(0, enemy.dex):
                        combat = False
                        flee = True
                        print("{} runs away!".format(self.name))
                        time.sleep(0.5)
                    else:
                        print("{} tries to run away...but fails.".format(self.name))
                        fail_flee = True
            if not flee and not fail_flee:
                if action == "Attack":
                    _, _ = self.weapon_damage(enemy, cover=cover)
                elif action().typ == "Skill":
                    _ = action().use(self, enemy, cover=cover)
                    if action().name == "Shapeshift":
                        _, _ = self.weapon_damage(enemy, cover=cover)
                    try:
                        if action().rank == 1:
                            if (enemy.cls in ["Diviner", "Geomancer"]) and \
                                    action().name not in enemy.spellbook['Skills']:
                                enemy.spellbook['Skills'][action().name] = action
                                print()
                                print(action())
                                print("You have gained the ability to cast {}.".format(action().name))
                        elif action().rank == 2:
                            if enemy.cls == "Geomancer" and action().name not in enemy.spellbook['Skills']:
                                enemy.spellbook['Skills'][action().name] = action
                                print()
                                print(action())
                                print("You have gained the ability to cast {}.".format(action().name))
                    except AttributeError:
                        pass
                elif action().typ == "Spell":
                    action().cast(self, enemy, cover=cover)
                    try:
                        if action().rank == 1:
                            if (enemy.cls == "Diviner" or enemy.cls == "Geomancer") and \
                                    action().name not in enemy.spellbook['Spells']:
                                enemy.spellbook['Spells'][action().name] = action
                                print(action())
                                print("You have gained the ability to cast {}.".format(action().name))
                        elif action().rank == 2:
                            if enemy.cls == "Geomancer" and action().name not in enemy.spellbook['Spells']:
                                enemy.spellbook['Spells'][action().name] = action
                                print(action())
                                print("You have gained the ability to cast {}.".format(action().name))
                    except AttributeError:
                        pass
                else:
                    print("{} doesn't do anything.".format(self.name))
        return valid_entry, combat, flee

    def check_mod(self, mod, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = self.equipment['Weapon']().damage + self.strength
            if self.cls in ['Panther', 'Drow Assassin', 'Barghest', 'Werewolf']:
                class_mod += (self.dex // 2)
            if self.status_effects['Attack'][0]:
                weapon_mod += self.status_effects['Attack'][2]
            return weapon_mod + class_mod
        elif mod == 'offhand':
            try:
                off_mod = self.equipment['OffHand']().damage + self.strength
                if self.status_effects['Attack'][0]:
                    off_mod += self.status_effects['Attack'][2]
                return int((off_mod + class_mod) * 0.75)
            except AttributeError:
                return 0
        elif mod == 'armor':
            armor_mod = self.equipment['Armor']().armor
            if self.turtle:
                class_mod += 99
            if self.status_effects['Defense'][0]:
                armor_mod += self.status_effects['Defense'][2]
            return armor_mod * int(not ignore) + class_mod
        elif mod == 'magic':
            magic_mod = int(self.intel // 2) * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                magic_mod += self.equipment['OffHand']().mod
            if self.equipment['Weapon']().subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon']().damage * 1.5)
            if self.status_effects['Magic'][0]:
                magic_mod += self.status_effects['Magic'][2]
            return magic_mod + class_mod
        elif mod == 'magic def':
            m_def_mod = self.wisdom
            if self.turtle:
                class_mod += 99
            if self.status_effects['Magic Defense'][0]:
                m_def_mod += self.status_effects['Magic Defense'][2]
            return m_def_mod + class_mod
        elif mod == 'heal':
            heal_mod = self.wisdom * self.pro_level
            if self.equipment['OffHand']().subtyp == 'Tome':
                heal_mod += self.equipment['OffHand']().mod
            elif self.equipment['Weapon']().subtyp == 'Staff':
                heal_mod += int(self.equipment['Weapon']().damage * 1.5)
            if self.status_effects['Magic'][0]:
                heal_mod += self.status_effects['Magic'][2]
            return heal_mod + class_mod
        elif mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return 0
            res_mod = self.resistance[typ]
            if self.flying:
                if typ == 'Earth':
                    res_mod = 1
                elif typ == 'Wind':
                    res_mod = -0.25
            return res_mod
        elif mod == 'luck':
            luck_mod = self.charisma // luck_factor
            return luck_mod


class Misc(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Misc'


class Slime(Enemy):
    """
    Slime type; resistance against all attack magic types; weak against physical damage
    """

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
    """
    Animal type; no special features
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Animal'
        self.inventory['Mystery Meat'] = [items.MysteryMeat, 1]


class Humanoid(Enemy):
    """
    Humanoid type; no special features
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Humanoid'


class Fey(Enemy):
    """
    Fey type; resistance against shadow damage
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Fey'
        self.resistance['Shadow'] = 0.25


class Fiend(Enemy):
    """
    Fiend type; resistance against shadow damage and weak against holy; high resistance against death
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Fiend'
        self.resistance['Shadow'] = 0.25
        self.resistance['Death'] = 0.75
        self.resistance['Holy'] = -0.25


class Undead(Enemy):
    """
    Undead type; resistance against shadow and poison and weak against fire; very weak against holy and immune to death
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Undead'
        self.resistance['Fire'] = -0.25
        self.resistance['Shadow'] = 0.5
        self.resistance['Death'] = 1.
        self.resistance['Holy'] = -0.75
        self.resistance['Poison'] = 0.5


class Elemental(Enemy):
    """
    Elemental type; high resistance against physical damage
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Elemental'
        self.resistance['Physical'] = 0.25


class Dragon(Enemy):
    """
    Dragon type; resistance against elemental and death magic types; mild resistance against physical
    """

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
        self.resistance['Stone'] = 0.25
        self.resistance['Physical'] = 0.1


class Monster(Enemy):
    """
    Monster type; no special resistances
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Monster'


class Aberration(Enemy):
    """
    Aberration type; no special resistances
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Aberration'


class Construct(Enemy):
    """
    Construct type: immune to death, stone, and poison, strong against physical
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Construct'
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Poison'] = 1.
        self.resistance['Physical'] = 0.5


# Natural weapons
class NaturalWeapon(items.Weapon):

    def __init__(self, name, damage, crit, description, off):
        super().__init__(name=name, damage=damage, crit=crit, subtyp='Natural', description=description, handed=1,
                         off=off, rarity=0, unequip=False, value=0)
        self.att_name = 'attacks'


class Bite(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Bite", damage=2, crit=0.05, description="", off=False)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, wielder, target, damage=0, crit=1):
        if self.crit > random.random():
            print("The bite is diseased.")
            if not random.randint(0, 39 // crit):
                print("The bite is diseased, crippling {} and lowering their constitution by 1.".format(target.name))
                target.con -= 1
            else:
                print("{} resists the disease.".format(target.name))


class Bite2(Bite):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 15
        self.crit = 0.2

    def special_effect(self, wielder, target, damage=0, crit=1):
        if self.crit > random.random():
            print("The bite is diseased.")
            if not random.randint(0, 19 // crit):
                print("The disease cripples {}, lowering their constitution by 1.".format(target.name))
                target.con -= 1
            else:
                print("{} resists the disease.".format(target.name))


class VampireBite(Bite):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 8
        self.crit = 0.15

    def special_effect(self, wielder, target, damage=0, crit=1):
        if damage > 0:
            if self.crit > random.random():
                print("{} drains {} and gains {} life.".format(wielder.name, target.name, damage))
                wielder.health += damage
                if wielder.health > wielder.health_max:
                    wielder.health = wielder.health_max


class Claw(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Claw", damage=4, crit=0.2, description="", off=True)
        self.att_name = 'swipes'


class Claw2(Claw):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 6
        self.crit = 0.25


class Claw3(Claw):
    """

    """

    def __init__(self):
        super().__init__()
        self.special = True
        self.damage = 8
        self.crit = 0.33

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.dex // 2) * crit, wielder.dex * crit) \
                    > random.randint(target.con // 2, target.con):
                if not target.status_effects['Bleed'][0]:
                    print("{} is bleeding.".format(target.name))
                duration = max(1, wielder.dex // 10)
                bleed_dmg = int(max(wielder.dex // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = max(duration, target.status_effects['Bleed'][1])
                target.status_effects['Bleed'][2] = max(bleed_dmg, target.status_effects['Bleed'][2])


class BearClaw(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Bear Claw", damage=12, crit=0.2, description="", off=True)
        self.special = True
        self.att_name = 'mauls'

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.strength // 2) * crit, wielder.strength * crit) \
                    > random.randint(target.con // 2, target.con):
                if not target.status_effects['Bleed'][0]:
                    print("{} is bleeding.".format(target.name))
                duration = max(1, wielder.strength // 10)
                bleed_dmg = int(max(wielder.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = max(duration, target.status_effects['Bleed'][1])
                target.status_effects['Bleed'][2] = max(bleed_dmg, target.status_effects['Bleed'][2])


class Stinger(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Stinger", damage=5, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'stings'

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Poison')
        if resist < 1:
            if random.randint((wielder.dex * crit) // 2, (wielder.dex * crit)) \
                    > random.randint(target.con // 2, target.con):
                if not target.status_effects['Poison'][0]:
                    print("{} is poisoned.".format(target.name))
                duration = max(1, wielder.dex // 10)
                damage += random.randint(wielder.dex // 4, wielder.dex // 2)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects['Poison'][0] = True
                target.status_effects['Poison'][1] = max(duration, target.status_effects['Poison'][1])
                target.status_effects['Poison'][2] = max(pois_dmg, target.status_effects['Poison'][2])


class Pincers(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Pincers", damage=2, crit=0.15, description="", off=True)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Poison')
        if resist < 1:
            if random.randint(wielder.dex // 2, wielder.dex) \
                    > random.randint(target.con // 2, target.con):
                if not target.status_effects['Poison'][0]:
                    print("{} is poisoned.".format(target.name))
                duration = max(1, wielder.dex // 10)
                damage += random.randint(wielder.dex // 4, wielder.dex // 2)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects['Poison'][0] = True
                target.status_effects['Poison'][1] = max(duration, target.status_effects['Poison'][1])
                target.status_effects['Poison'][2] = max(pois_dmg, target.status_effects['Poison'][2])
                if not target.status_effects['Stun'][0]:
                    p_resist = target.check_mod('resist', 'Physical')
                    if crit > 1:
                        if random.randint(wielder.strength // 2, wielder.strength) * (1 - p_resist) \
                                > random.randint(target.con // 2, target.con):
                            s_duration = max(1, wielder.strength // 10)
                            target.status_effects['Stun'][0] = True
                            target.status_effects['Stun'][1] = s_duration
                            print("{} is stunned.".format(target.name, s_duration))


class Pincers2(Pincers):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 6
        self.crit = 0.2


class DemonClaw(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Demon Claw", damage=5, crit=0.25, description="", off=True)
        self.special = True
        self.att_name = 'claws'

    def special_effect(self, wielder, target, damage=0, crit=1):
        spells.Doom().cast(wielder, target, special=True)


class DemonClaw2(DemonClaw):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 10
        self.crit = 0.33
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        spells.Desoul().cast(wielder, target, special=True)


class SnakeFang(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Snake Fang", damage=3, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'strikes'

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Poison')
        if resist < 1:
            if random.randint((wielder.dex * crit) // 2, (wielder.dex * crit)) \
                    > random.randint(target.con // 2, target.con):
                if not target.status_effects['Poison'][0]:
                    print("{} is poisoned.".format(target.name))
                duration = max(1, wielder.dex // 10)
                damage += random.randint(wielder.dex // 4, wielder.dex // 2)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects['Poison'][0] = True
                target.status_effects['Poison'][1] = max(duration, target.status_effects['Poison'][1])
                target.status_effects['Poison'][2] = max(pois_dmg, target.status_effects['Poison'][2])


class SnakeFang2(SnakeFang):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 7
        self.crit = 0.33


class AlligatorTail(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Alligator Tail", damage=8, crit=0.1, description="", off=False)
        self.special = True
        self.att_name = 'swipes'

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'][0]:
            resist = target.check_mod('resist', 'Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(wielder.strength // 2, wielder.strength) * (1 - resist) \
                            > random.randint(target.con // 2, target.con):
                        duration = max(1, wielder.strength // 10)
                        target.status_effects['Stun'][0] = True
                        target.status_effects['Stun'][1] = duration
                        print("{} is stunned.".format(target.name, duration))


class LionPaw(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Lion Paw", damage=14, crit=0.15, description="", off=True)
        self.att_name = 'swipes'


class Laser(NaturalWeapon):
    """
    ignores armor
    """

    def __init__(self):
        super().__init__(name="Laser", damage=12, crit=0.25, description="", off=True)
        self.ignore = True
        self.att_name = 'zaps'


class Laser2(Laser):
    """
    has a chance to permanently damage the enemy, reducing a random stat by 1
    """

    def __init__(self):
        super().__init__()
        self.damage = 20
        self.crit = 0.4
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        t_chance = target.check_mod('luck', luck_factor=5)
        if random.randint(0, wielder.strength // 2) * crit > \
                random.randint(target.con // 2, target.con) + t_chance:
            stat_list = ['strength', 'intelligence', 'wisdom', 'constitution', 'charisma', 'dexterity']
            stat_index = random.randint(0, 5)
            stat_name = stat_list[stat_index]
            if stat_name == 'strength':
                target.strength -= 1
            if stat_name == 'intelligence':
                target.intel -= 1
            if stat_name == 'wisdom':
                target.wisdom -= 1
            if stat_name == 'constitution':
                target.con -= 1
            if stat_name == 'charisma':
                target.charisma -= 1
            if stat_name == 'dexterity':
                target.dex -= 1
            print("The attack is devastating, causing {} to lose 1 {}.".format(target.name, stat_name))


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player_char to stone
    """

    def __init__(self):
        super().__init__(name="Gaze", damage=0, crit=0, description="", off=False)
        self.special = True
        self.att_name = 'leers'

    def special_effect(self, wielder, target, damage=0, crit=1):
        print("{} {} at {}.".format(wielder.name, self.name, target.name))
        spells.Petrify().cast(wielder, target, special=True)


class DragonClaw(NaturalWeapon):
    """
    ignores armor
    """

    def __init__(self):
        super().__init__(name="Dragon Claw", damage=10, crit=0.2, description="", off=True)
        self.ignore = True
        self.att_name = 'rakes'


class DragonClaw2(DragonClaw):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 12
        self.crit = 0.33
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.strength // 2) * crit, wielder.strength * crit) \
                    > random.randint(target.con // 2, target.con):
                if not target.status_effects['Bleed'][0]:
                    print("{} is bleeding.".format(target.name))
                duration = max(1, wielder.strength // 10)
                bleed_dmg = int(max(wielder.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = max(duration, target.status_effects['Bleed'][1])
                target.status_effects['Bleed'][2] = max(bleed_dmg, target.status_effects['Bleed'][2])


class DragonTail(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="Dragon Tail", damage=14, crit=0.15, description="", off=True)
        self.att_name = 'swipes'


class DragonTail2(DragonTail):
    """

    """

    def __init__(self):
        super().__init__()
        self.damage = 25
        self.crit = 0.3
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'][0]:
            resist = target.check_mod('resist', 'Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(wielder.strength // 2, wielder.strength) * (1 - resist) \
                            > random.randint(target.con // 2, target.con):
                        duration = max(1, wielder.strength // 10)
                        target.status_effects['Stun'][0] = True
                        target.status_effects['Stun'][1] = duration
                        print("{} is stunned.".format(target.name))


class NightmareHoof(NaturalWeapon):
    """
    Natural weapon of Nightmare; additional fire damage
    """

    def __init__(self):
        super().__init__(name="Nightmare Hoof", damage=8, crit=0.25, description="", off=True)
        self.special = True
        self.att_name = 'attacks'

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Fire')
        damage = int(random.randint(wielder.intel // 2, wielder.intel) * (1 - resist))
        target.health -= damage
        if damage > 0:
            print("The fire from {}'s attack burns {} for {} damage.".format(wielder.name, target.name, damage))
        elif damage < 0:
            print("{} absorbs the fire damage and is healed for {} hit points.".format(target.name, abs(damage)))
        else:
            print("The fire is ineffective, dealing {} damage.".format(damage))


class ElementalBlade(NaturalWeapon):
    """
    Innate weapon possessed by Myrmidons; does elemental damage based on the enemy type
    """

    def __init__(self):
        super().__init__(name="Elemental Blade", damage=10, crit=0.25, description="", off=True)
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
        if damage > 0 and elemental_type == "Fire" and target.is_alive():
            if not target.status_effects['DOT'][0]:
                print("{} is on fire.".format(target.name))
            target.status_effects['DOT'][0] = True
            target.status_effects['DOT'][1] = 3
            target.status_effects['DOT'][2] = max(int(damage // 2), target.status_effects['DOT'][2])
            time.sleep(0.25)


class Tentacle(NaturalWeapon):
    """
    Chance to trip and leave prone
    """

    def __init__(self):
        super().__init__(name="Tentacle", damage=8, crit=0.2, description="A slender, flexible limb or appendage in an "
                                                                          "animal, especially around the mouth of an "
                                                                          "invertebrate, used for grasping or moving "
                                                                          "about, or bearing sense organs.",
                         off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        spells.Trip().use(wielder, target, special=True)


class Tentacle2(Tentacle):
    """
    Chance to stun
    """

    def __init__(self):
        super().__init__()
        self.damage = 14
        self.crit = 0.3
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'][0]:
            resist = target.check_mod('resist', 'Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(wielder.strength // 2, wielder.strength) * (1 - resist) \
                            > random.randint(target.con // 2, target.con):
                        duration = max(1, wielder.strength // 10)
                        target.status_effects['Stun'][0] = True
                        target.status_effects['Stun'][1] = duration
                        print("{} is stunned.".format(target.name, duration))


class InvisibleBlade(NaturalWeapon):
    """
    Only stuns on crit
    """

    def __init__(self):
        super().__init__(name="Invisible Blade", damage=5, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'][0]:
            resist = target.check_mod('resist', 'Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(0, wielder.dex // 2) * (1 - resist) \
                            > random.randint(target.con // 4, target.con):
                        duration = max(1, wielder.dex // 15)
                        target.status_effects['Stun'][0] = True
                        target.status_effects['Stun'][1] = duration
                        print("{} is stunned.".format(target.name, duration))


class CerberusClaw(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name='claws', damage=10, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Physical')
        if resist < 1:
            if random.randint((wielder.strength // 2) * crit, wielder.strength * crit) \
                    > random.randint(target.con // 2, target.con):
                if not target.status_effects['Bleed'][0]:
                    print("{} is bleeding.".format(target.name))
                duration = max(1, wielder.strength // 10)
                bleed_dmg = int(max(wielder.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = max(duration, target.status_effects['Bleed'][1])
                target.status_effects['Bleed'][2] = max(bleed_dmg, target.status_effects['Bleed'][2])


class CerberusBite(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name="bites", damage=20, crit=0.25, description="", off=False)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Fire')
        damage = int(random.randint(damage // 2, damage) * (1 - resist))
        target.health -= damage
        if damage > 0:
            print("The fire from {}'s bite burns {} for {} damage.".format(wielder.name, target.name, damage))
        elif damage < 0:
            print("{} absorbs the fire damage and is healed for {} hit points.".format(target.name, abs(damage)))
        else:
            print("The fire is ineffective, dealing {} damage.".format(damage))


class LichHand(NaturalWeapon):
    """
    Chance to paralyze (stun) enemy
    """

    def __init__(self):
        super().__init__(name="touches", damage=12, crit=0.2, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'][0]:
            if crit > 1:
                if random.randint(wielder.intel // 4, wielder.intel) \
                        > random.randint(target.wisdom // 2, target.wisdom):
                    duration = max(1, wielder.intel // 10)
                    target.status_effects['Stun'][0] = True
                    target.status_effects['Stun'][1] = duration
                    print("{} is stunned.".format(target.name))


class Cannon(NaturalWeapon):
    """
    Chance to stun the target
    """

    def __init__(self):
        super().__init__(name="attacks", damage=40, crit=0.15, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'][0]:
            if crit > 1:
                if random.randint(wielder.strength // 4, wielder.strength) \
                        > random.randint(target.con // 2, target.con):
                    duration = max(1, wielder.strength // 10)
                    target.status_effects['Stun'][0] = True
                    target.status_effects['Stun'][1] = duration
                    print("{} is stunned.".format(target.name, duration))


class DevilBlade(NaturalWeapon):
    """

    """

    def __init__(self):
        super().__init__(name='attacks', damage=50, crit=0.33, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        w_chance = wielder.check_mod('luck', luck_factor=10)
        t_chance = target.check_mod('luck', luck_factor=20)
        if crit > 1:
            if random.randint(0, w_chance) > random.randint(0, t_chance):
                effects = ['Stun', 'Doom', 'Blind', 'Disarm', 'Sleep', 'Poison', 'DOT', 'Bleed']
                effect = random.choice(effects)
                target.status_effects[effect][0] = True
                target.status_effects[effect][1] = max(random.randint(1, 5), target.status_effects[effect][0])
                if effect in ['Poison', 'DOT', 'Bleed']:
                    target.status_effects[effect][2] += damage  # damage builds over time
                print("The attack inflicts {} on {}.".format(effect.lower(), target.name))


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


class StoneArmor2(StoneArmor):
    """

    """

    def __init__(self):
        super().__init__()
        self.armor = 9


class SnakeScales(NaturalArmor):
    """

    """

    def __init__(self):
        super().__init__(name="Snake Scales", armor=3, description="")


class SnakeScales2(SnakeScales):
    """

    """

    def __init__(self):
        super().__init__()
        self.armor = 6


class DemonArmor(NaturalArmor):
    """

    """

    def __init__(self):
        super().__init__(name='Demon Armor', armor=4, description="")


class DemonArmor2(DemonArmor):
    """
    Deals additional shadow damage to attacker
    """

    def __init__(self):
        super().__init__()
        self.armor = 10
        self.special = True
        self.shadow_damage = 100

    def special_effect(self, wearer, attacker):
        resist = attacker.check_mod('resist', 'Shadow')
        damage = int(random.randint(self.shadow_damage // 2, self.shadow_damage) * (1 - resist))
        attacker.health -= damage
        if damage > 0:
            print("An aura of shadow emanates from {}, dealing {} damage to {}.".format(
                wearer.name, damage, attacker.name))
        elif damage < 0:
            print("{} absorbs the shadow damage emanating from {} and is healed for {} hit points.".format(
                attacker.name, wearer.name, abs(damage)))
        else:
            print("The shadow aura is ineffective, dealing {} damage.".format(damage))


class MetalPlating(NaturalArmor):

    def __init__(self):
        super().__init__(name='Metal Plating', armor=5, description="")


class DragonScale(NaturalArmor):

    def __init__(self):
        super().__init__(name='Dragon Scales', armor=6, description="")


class CerberusHide(NaturalArmor):
    """
    deals additional fire damage to attacker
    """

    def __init__(self):
        super().__init__(name='Cerberus Hide', armor=18, description="")
        self.special = True
        self.fire_damage = 50

    def special_effect(self, wearer, attacker):
        resist = attacker.check_mod('resist', 'Fire')
        damage = int(random.randint(self.fire_damage // 2, self.fire_damage) * (1 - resist))
        attacker.health -= damage
        if damage > 0:
            print("An aura of fire emanates from {}, dealing {} damage to {}.".format(
                wearer.name, damage, attacker.name))
        elif damage < 0:
            print("{} absorbs the fire damage emanating from {} and is healed for {} hit points.".format(
                attacker.name, wearer.name, abs(damage)))
        else:
            print("The fire is ineffective, dealing {} damage.".format(damage))


class DevilSkin(NaturalArmor):
    """
    deals additional non-elemental damage to attacker
    """

    def __init__(self):
        super().__init__(name='Devil Skin', armor=40, description="")
        self.special = True
        self.damage = 100

    def special_effect(self, wearer, attacker):
        a_chance = attacker.check_mod('luck', luck_factor=10)
        damage = random.randint(self.damage // (1 + a_chance), self.damage)
        attacker.health -= damage
        if damage > 0:
            print("An aura emanates from {}, dealing {} damage to {}.".format(
                wearer.name, damage, attacker.name))
        else:
            print("The aura is ineffective, dealing {} damage.".format(damage))


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
        super().__init__(name="Test", health=1, mana=999, strength=20, intel=0, wisdom=0, con=10, charisma=99, dex=25,
                         exp=5000)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {},
                          "Skills": {'Aqualung': spells.Aqualung}}
        self.pro_level = 99  # test for enemies running away


class Mimic(Aberration):
    """
    z: location level plus 1 if Locked plus 1 if ChestRoom2
    health: 10-40 * z
    mana: 20-35 * z
    strength: 12-42
    intel: 6-24
    wisdom: 11-41
    con: 13-43
    charisma: 8-32
    dex: 12-36
    exp: 25-50 * z
    gold: 50-100 * z
    """

    def __init__(self, z):
        super().__init__(name='Mimic', health=20 + (random.randint(10, 40) * z), mana=10 + (random.randint(20, 35) * z),
                         strength=(15 + (5 * (z - 1))), intel=(6 + (3 * (z - 1))), wisdom=(11 + (5 * (z - 1))),
                         con=(13 + (5 * (z - 1))), charisma=(8 + (4 * (z - 1))), dex=(12 + (4 * (z - 1))),
                         exp=25 + (random.randint(25, 50) * z))
        self.gold = 50 + (random.randint(50, 100) * z)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {},
                          "Skills": {'Lick': spells.Lick,
                                     'Gold Toss': spells.GoldToss}}
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Poison'] = 1.
        self.pro_level = z


# Starting enemies
class GreenSlime(Slime):
    """

    """

    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(7, 14), mana=20, strength=6, intel=15, wisdom=15,
                         con=8, charisma=1, dex=4, exp=random.randint(1, 20))
        self.gold = random.randint(1, 8)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory['Key'] = [items.Key, 1]
        self.spellbook = {"Spells": {'Enfeeble': spells.Enfeeble},
                          "Skills": {'Acid Spit': spells.AcidSpit}}
        self.pro_level = 0


class GiantRat(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=0, strength=4, intel=3, wisdom=3, con=6,
                         charisma=6, dex=15, exp=random.randint(7, 14))
        self.equipment = dict(Weapon=Bite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(1, 5)
        self.inventory['Rat Tail'] = [items.RatTail, 1]
        self.pro_level = 0


class Goblin(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(3, 7), mana=0, strength=7, intel=5, wisdom=2, con=8,
                         charisma=12, dex=8, exp=random.randint(7, 16))
        self.equipment = dict(Weapon=items.Rapier, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(10, 20)
        self.spellbook = {"Spells": {},
                          "Skills": {"Goblin Punch": spells.GoblinPunch}}
        self.pro_level = 0


class Goblin2(Goblin):
    """
    Buffed version of a regular goblin; Barghest boss can transform into one
    """

    def __init__(self):
        super().__init__()
        self.strength = 22
        self.intel = 16
        self.wisdom = 10
        self.con = 17
        self.charisma = 19
        self.dex = 14
        self.equipment = dict(Weapon=items.Talwar, Armor=items.Cuirboulli, OffHand=items.Kris,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook['Skills']['Gold Toss'] = spells.GoldToss


class Bandit(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=16, strength=8, intel=8, wisdom=5, con=8,
                         charisma=10, dex=10, exp=random.randint(8, 18))
        self.equipment = dict(Weapon=items.Dirk, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(15, 25)
        self.spellbook = {"Spells": {},
                          "Skills": {'Steal': spells.Steal,
                                     'Disarm': spells.Disarm}}
        self.pro_level = 0


class Skeleton(Undead):
    """

    """

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=0, strength=8, intel=4, wisdom=8, con=12,
                         charisma=5, dex=6, exp=random.randint(11, 20))
        self.equipment = dict(Weapon=items.Dirk, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(10, 20)
        self.inventory['Health Potion'] = [items.HealthPotion, 1]
        self.resistance['Fire'] = 0.
        self.pro_level = 0


class Scarecrow(Construct):
    """

    """

    def __init__(self):
        super().__init__(name='Scarecrow', health=random.randint(5, 7), mana=0, strength=10, intel=1, wisdom=6, con=10,
                         charisma=8, dex=11, exp=random.randint(13, 21))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(8, 16)
        self.spellbook = {"Spells": {},
                          "Skills": {'Sleeping Powder': spells.SleepingPowder}}
        self.resistance['Fire'] = -1.
        self.resistance['Physical'] = 0.
        self.pro_level = 0


# Level 1
class GiantCentipede(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Giant Centipede', health=random.randint(8, 13), mana=0, strength=10, intel=4, wisdom=6,
                         con=8, charisma=8, dex=12, exp=random.randint(13, 24))
        self.equipment = dict(Weapon=Pincers, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(10, 18)
        self.resistance['Physical'] = 0.25
        self.pro_level = 1


class GiantHornet(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=0, strength=6, intel=4, wisdom=6,
                         con=6, charisma=8, dex=18, exp=random.randint(13, 24))
        self.equipment = dict(Weapon=Stinger, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(6, 15)
        self.flying = True
        self.pro_level = 1


class ElectricBat(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Electric Bat', health=random.randint(5, 9), mana=15, strength=6, intel=11, wisdom=7,
                         con=5, charisma=12, dex=22, exp=random.randint(17, 31))
        self.equipment = dict(Weapon=Bite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(8, 21)
        self.spellbook = {"Spells": {'Shock': spells.Shock,
                                     'Silence': spells.Silence},
                          "Skills": {}}
        self.flying = True
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = -0.25
        self.pro_level = 1


class Zombie(Undead):
    """

    """

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(11, 14), mana=20, strength=15, intel=1, wisdom=5, con=8,
                         charisma=8, dex=8, exp=random.randint(11, 22))
        self.equipment = dict(Weapon=Bite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(15, 30)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike}}
        self.pro_level = 1


class Imp(Fiend):
    """

    """

    def __init__(self):
        super().__init__(name='Imp', health=random.randint(9, 14), mana=25, strength=6, intel=12, wisdom=10,
                         con=8, charisma=12, dex=12, exp=random.randint(15, 24))
        self.equipment = dict(Weapon=DemonClaw, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(15, 30)
        self.spellbook = {"Spells": {'Corruption': spells.Corruption,
                                     'Silence': spells.Silence},
                          "Skills": {}}
        self.pro_level = 1


class GiantSpider(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=10, strength=9, intel=10, wisdom=10,
                         con=8, charisma=10, dex=12, exp=random.randint(15, 24))
        self.equipment = dict(Weapon=Stinger, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(15, 30)
        self.spellbook = {'Spells': {},
                          'Skills': {'Web': spells.Web}}
        self.resistance['Poison'] = 0.25
        self.pro_level = 1


class Quasit(Fiend):
    """
    Can shapeshift between Electric Bat, Giant Centipede, Battle Toad, and natural forms
    """

    def __init__(self):
        super().__init__(name='Quasit', health=random.randint(13, 17), mana=15, strength=8, intel=8, wisdom=10,
                         con=11, charisma=14, dex=16, exp=random.randint(25, 44))
        self.equipment = dict(Weapon=DemonClaw, Armor=DemonArmor, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(25, 40)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike,
                                     'Shapeshift': spells.Shapeshift}}
        self.resistance['Poison'] = 1
        self.transform = [Quasit, ElectricBat, GiantCentipede, BattleToad]
        self.pro_level = 1


class Panther(Animal):
    """
    Transform Level 1 creature
    """

    def __init__(self):
        super().__init__(name='Panther', health=random.randint(10, 14), mana=25, strength=10, intel=8, wisdom=8,
                         con=10, charisma=10, dex=13, exp=random.randint(19, 28))
        self.equipment = dict(Weapon=Claw, Armor=AnimalHide, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(10, 20)
        self.inventory['Leather'] = [items.Leather, 1]
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': spells.Backstab,
                                     'Kidney Punch': spells.KidneyPunch,
                                     'Disarm': spells.Disarm}}
        self.resistance['Physical'] = 0.25
        self.pro_level = 1


class TwistedDwarf(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Twisted Dwarf', health=random.randint(15, 19), mana=10, strength=12, intel=8, wisdom=10,
                         con=12, charisma=8, dex=10, exp=random.randint(25, 44))
        self.equipment = dict(Weapon=items.Mattock, Armor=items.HideArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(10, 20)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}
        self.pro_level = 1


class BattleToad(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Battle Toad', health=random.randint(15, 19), mana=20, strength=10, intel=9, wisdom=10,
                         con=10, charisma=8, dex=15, exp=random.randint(30, 48))
        self.equipment = dict(Weapon=items.BrassKnuckles, Armor=items.NoArmor, OffHand=items.BrassKnuckles,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(31, 47)
        self.spellbook = {"Spells": {},
                          "Skills": {'Jump': spells.Jump}}
        self.pro_level = 1


class Satyr(Fey):
    """

    """

    def __init__(self):
        super().__init__(name='Satyr', health=random.randint(17, 22), mana=25, strength=11, intel=12, wisdom=10, con=11,
                         charisma=12, dex=12, exp=random.randint(28, 44))
        self.equipment = dict(Weapon=items.Rapier, Armor=items.LeatherArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(29, 42)
        self.spellbook = {"Spells": {},
                          "Skills": {'Stomp': spells.Stomp}}
        self.resistance['Fire'] = 0.1
        self.resistance['Ice'] = 0.1
        self.resistance['Electric'] = 0.1
        self.resistance['Water'] = 0.1
        self.resistance['Earth'] = 0.1
        self.resistance['Wind'] = 0.1
        self.resistance['Death'] = 0.1
        self.resistance['Stone'] = 0.1
        self.resistance['Poison'] = 0.1
        self.resistance['Physical'] = 0.1
        self.pro_level = 1


class Minotaur(Monster):
    """
    Level 1 Boss
    """

    def __init__(self):
        super().__init__(name='Minotaur', health=86, mana=30, strength=18, intel=8, wisdom=10, con=14, charisma=14,
                         dex=12, exp=250)
        self.equipment = dict(Weapon=items.DoubleAxe, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 200
        self.inventory['Weapon'] = [items.random_item(2, typ='Weapon'), 1]
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': spells.MortalStrike,
                                     'Charge': spells.Charge,
                                     'Disarm': spells.Disarm,
                                     'Parry': spells.Parry}}
        self.resistance['Death'] = 1
        self.pro_level = 1


class Barghest(Fiend):
    """
    Level 1 Extra Boss - guards first of six relics (TRIANGULUS) required to beat the final boss
    Can shapeshift between 3 forms: Direwolf, Goblin, and Hybrid (natural) forms
    """

    def __init__(self):
        super().__init__(name='Barghest', health=145, mana=80, strength=25, intel=15, wisdom=14,
                         con=18, charisma=14, dex=16, exp=500)
        self.gold = 600
        self.equipment = dict(Weapon=Claw2, Armor=AnimalHide, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory['Old Key'] = [items.OldKey, 1]
        self.spellbook = {"Spells": {'Doom': spells.Doom},
                          "Skills": {'Shapeshift': spells.Shapeshift,
                                     'Trip': spells.Trip}}
        self.resistance['Death'] = 1
        self.resistance['Physical'] = 0.25
        self.transform = [Barghest, Goblin2, Direwolf2]
        self.pro_level = 2


# Level 2
class Gnoll(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Gnoll', health=random.randint(16, 24), mana=20, strength=13, intel=10, wisdom=5, con=8,
                         charisma=12, dex=16, exp=random.randint(45, 85))
        self.equipment = dict(Weapon=items.Partisan, Armor=items.PaddedArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(10, 20)
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': spells.Disarm}}
        self.pro_level = 2


class GiantSnake(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Giant Snake', health=random.randint(18, 26), mana=0, strength=15, intel=5, wisdom=6,
                         con=14, charisma=10, dex=16, exp=random.randint(60, 100))
        self.equipment = dict(Weapon=SnakeFang, Armor=SnakeScales, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(35, 75)
        self.inventory['Snake Skin'] = [items.SnakeSkin, 1]
        self.resistance['Poison'] = 0.25
        self.pro_level = 2


class Orc(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(17, 28), mana=14, strength=12, intel=6, wisdom=5, con=10,
                         charisma=8, dex=14, exp=random.randint(45, 80))
        self.equipment = dict(Weapon=items.Jian, Armor=items.LeatherArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(20, 65)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}
        self.pro_level = 2


class GiantOwl(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Giant Owl', health=random.randint(12, 17), mana=0, strength=13, intel=12, wisdom=10,
                         con=10, charisma=1, dex=15, exp=random.randint(45, 80))
        self.equipment = dict(Weapon=Claw2, Armor=items.NoArmor, OffHand=Claw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(20, 65)
        self.inventory['Feather'] = [items.Feather, 1]
        self.flying = True
        self.pro_level = 2


class Vampire(Undead):
    """

    """

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(20, 28), mana=30, strength=20, intel=14, wisdom=12,
                         con=15, charisma=14, dex=14, exp=random.randint(50, 90))
        self.equipment = dict(Weapon=VampireBite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 90)
        self.spellbook = {"Spells": {'Silence': spells.Silence},
                          "Skills": {'Shapeshift': spells.Shapeshift}}
        self.transform = [Vampire, VampireBat]
        self.pro_level = 2


class VampireBat(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Vampire Bat', health=random.randint(20, 28), mana=30, strength=12, intel=16, wisdom=15,
                         con=10, charisma=14, dex=18, exp=random.randint(50, 90))
        self.equipment = dict(Weapon=Bite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 90)
        self.spellbook = {"Spells": {},
                          "Skills": {'Health Drain': spells.HealthDrain,
                                     'Shapeshift': spells.Shapeshift}}
        self.transform = [Vampire, VampireBat]
        self.flying = True
        self.pro_level = 2


class Direwolf(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Direwolf', health=random.randint(16, 20), mana=0, strength=17, intel=7, wisdom=6, con=14,
                         charisma=10, dex=16, exp=random.randint(60, 100))
        self.equipment = dict(Weapon=Claw2, Armor=AnimalHide, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(35, 75)
        self.inventory['Leather'] = [items.Leather, 1]
        self.spellbook = {"Spells": {},
                          "Skills": {'Howl': spells.Howl,
                                     'Trip': spells.Trip}}
        self.resistance['Physical'] = 0.25
        self.pro_level = 2


class Direwolf2(Direwolf):
    """
    Buffed version of Direwolf; Barghest will transform into
    """

    def __init__(self):
        super().__init__()
        self.strength = 28
        self.intel = 10
        self.wisdom = 9
        self.con = 20
        self.charisma = 12
        self.dex = 20
        self.equipment = dict(Weapon=Claw3, Armor=AnimalHide2, OffHand=Claw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook['Skills']['Jump'] = spells.Jump


class Wererat(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(14, 17), mana=0, strength=14, intel=6, wisdom=12, con=11,
                         charisma=8, dex=18, exp=random.randint(57, 94))
        self.equipment = dict(Weapon=Bite, Armor=AnimalHide, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 65)
        self.pro_level = 2


class RedSlime(Slime):
    """

    """

    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(18, 32), mana=30, strength=10, intel=20, wisdom=20,
                         con=12, charisma=10, dex=5, exp=random.randint(43, 150))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 65)
        self.inventory['Super Health Potion'] = [items.ManaPotion, 1]
        self.spellbook = {'Spells': {'Firebolt': spells.Firebolt,
                                     'Enfeeble': spells.Enfeeble},
                          'Skills': {}}
        self.pro_level = 2


class GiantScorpion(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Giant Scorpion', health=random.randint(13, 18), mana=0, strength=14, intel=5, wisdom=10,
                         con=12, charisma=10, dex=9, exp=random.randint(65, 105))
        self.equipment = dict(Weapon=Stinger, Armor=Carapace, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 65)
        self.resistance['Poison'] = 0.25
        self.resistance['Physical'] = 0.25
        self.pro_level = 2


class Warrior(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(22, 31), mana=25, strength=14, intel=10, wisdom=8,
                         con=12, charisma=10, dex=10, exp=random.randint(65, 110))
        self.equipment = dict(Weapon=items.Jian, Armor=items.ChainMail, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(25, 100)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': spells.PiercingStrike,
                                     'Disarm': spells.Disarm,
                                     'Parry': spells.Parry}}
        self.pro_level = 2


class Harpy(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=0, strength=18, intel=13, wisdom=13,
                         con=14, charisma=14, dex=23, exp=random.randint(65, 115))
        self.equipment = dict(Weapon=Claw2, Armor=items.NoArmor, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(50, 75)
        self.flying = True
        self.spellbook = {'Spells': {},
                          'Skills': {'Screech': spells.Screech}}
        self.pro_level = 2


class Naga(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=0, strength=15, intel=13, wisdom=15,
                         con=15, charisma=12, dex=17, exp=random.randint(67, 118))
        self.equipment = dict(Weapon=items.Partisan, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(55, 75)
        self.spellbook = {"Spells": {'Silence': spells.Silence},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Electric'] = -0.5
        self.resistance['Water'] = 0.75
        self.pro_level = 2


class Clannfear(Fiend):
    """

    """

    def __init__(self):
        super().__init__(name='Clannfear', health=random.randint(22, 28), mana=40, strength=17, intel=8, wisdom=11,
                         con=14, charisma=12, dex=15, exp=random.randint(77, 130))
        self.equipment = dict(Weapon=DemonClaw, Armor=AnimalHide, OffHand=DemonClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(65, 92)
        self.spellbook = {'Spells': {},
                          'Skills': {'Trip': spells.Trip,
                                     'Charge': spells.Charge}}
        self.resistance['Fire'] = 0.75
        self.resistance['Electric'] = -0.5
        self.pro_level = 2


class Xorn(Elemental):
    """
    Earth elemental
    """

    def __init__(self):
        super().__init__(name='Xorn', health=random.randint(27, 33), mana=40, strength=16, intel=11, wisdom=12,
                         con=17, charisma=10, dex=12, exp=random.randint(74, 121))
        self.equipment = dict(Weapon=Claw, Armor=items.NoArmor, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(61, 99)
        self.spellbook = {'Spells': {'Tremor': spells.Tremor},
                          'Skills': {'ConsumeItem': spells.ConsumeItem}}
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.5
        self.resistance['Earth'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Poison'] = 1.
        self.pro_level = 2


class SteelPredator(Construct):
    """

    """

    def __init__(self):
        super().__init__(name='Steel Predator', health=random.randint(27, 33), mana=40, strength=17, intel=9,
                         wisdom=12, con=14, charisma=12, dex=19, exp=random.randint(85, 129))
        self.equipment = dict(Weapon=Claw2, Armor=MetalPlating, OffHand=Claw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(65, 110)
        self.status_effects['Blind'] = [True, -1]
        self.inventory['Scrap Metal'] = [items.ScrapMetal, 1]
        self.spellbook = {'Spells': {'Silence': spells.Silence},
                          'Skills': {'Charge': spells.Charge,
                                     'Destroy Metal': spells.DestroyMetal}}
        self.resistance['Fire'] = 0.5
        self.resistance['Ice'] = 0.5
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.75
        self.resistance['Earth'] = 0.
        self.pro_level = 2


class Pseudodragon(Dragon):
    """
    Level 2 Boss
    """

    def __init__(self):
        super().__init__(name='Pseudodragon', health=250, mana=100, strength=28, intel=26, wisdom=24, con=20,
                         charisma=20, dex=18, exp=500)
        self.gold = 1500
        self.equipment = dict(Weapon=DragonClaw, Armor=DragonScale, OffHand=DragonClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory['Item'] = [items.random_item(random.randint(2, 3)), 1]
        self.inventory['Old Key'] = [items.OldKey, 1]
        self.spellbook = {'Spells': {'Fireball': spells.Fireball,
                                     'Blinding Fog': spells.BlindingFog,
                                     'Dispel': spells.Dispel},
                          'Skills': {'Gold Toss': spells.GoldToss}}
        self.resistance['Death'] = 1
        self.pro_level = 2


class Nightmare(Fiend):
    """
    Level 2 Extra Boss - guards second of six relics (QUADRATA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Nightmare', health=410, mana=100, strength=30, intel=17, wisdom=15, con=22, charisma=16,
                         dex=15, exp=800)
        self.equipment = dict(Weapon=NightmareHoof, Armor=AnimalHide2, OffHand=NightmareHoof,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 2500
        self.inventory['Item'] = [items.random_item(random.randint(3, 4)), 1]
        self.inventory['Old Key'] = [items.OldKey, 1]
        self.spellbook = {'Spells': {'Sleep': spells.Sleep,
                                     'Firestorm': spells.Firestorm},
                          'Skills': {'Charge': spells.Charge,
                                     'Stomp': spells.Stomp,
                                     'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Fire'] = 1
        self.resistance['Ice'] = -0.25
        self.resistance['Death'] = 1
        self.resistance['Physical'] = 0.5
        self.flying = True
        self.pro_level = 3


# Level 3
class Direbear(Animal):
    """
    Transform Level 2 creature
    """

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=30, strength=25, intel=6, wisdom=6,
                         con=26, charisma=12, dex=18, exp=random.randint(210, 310))
        self.equipment = dict(Weapon=BearClaw, Armor=AnimalHide, OffHand=BearClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 65)
        self.inventory['Leather'] = [items.Leather, 1]
        self.spellbook = {'Spells': {},
                          'Skills': {'Piercing Strike': spells.PiercingStrike,
                                     'Charge': spells.Charge}}
        self.resistance['Physical'] = 0.25
        self.pro_level = 3


class Ghoul(Undead):
    """

    """

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=50, strength=23, intel=10, wisdom=8, con=24,
                         charisma=11, dex=12, exp=random.randint(210, 290))
        self.equipment = dict(Weapon=Bite, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(35, 45)
        self.spellbook = {"Spells": {'Disease Breath': spells.DiseaseBreath},
                          "Skills": {}}
        self.pro_level = 3


class PitViper(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=30, strength=17, intel=6, wisdom=8,
                         con=16, charisma=10, dex=18, exp=random.randint(215, 290))
        self.equipment = dict(Weapon=SnakeFang2, Armor=SnakeScales, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(50, 85)
        self.inventory['Snake Skin'] = [items.SnakeSkin, 1]
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Poison'] = 0.25
        self.pro_level = 3


class Disciple(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=70, strength=16, intel=17, wisdom=15,
                         con=16, charisma=12, dex=16, exp=random.randint(210, 290))
        self.equipment = dict(Weapon=items.SerpentStaff, Armor=items.SilverCloak, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(55, 95)
        self.inventory['Super Mana Potion'] = [items.GreatManaPotion, 1]
        self.spellbook = {'Spells': {'Firebolt': spells.Firebolt,
                                     'Ice Lance': spells.IceLance,
                                     'Shock': spells.Shock,
                                     'Enfeeble': spells.Enfeeble},
                          'Skills': {}}
        self.pro_level = 3


class BlackSlime(Slime):
    """

    """

    def __init__(self):
        super().__init__(name='Black Slime', health=random.randint(48, 90), mana=80, strength=13, intel=25, wisdom=30,
                         con=15, charisma=12, dex=6, exp=random.randint(185, 360))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(30, 180)
        self.spellbook = {'Spells': {'Shadow Bolt': spells.ShadowBolt,
                                     'Corruption': spells.Corruption,
                                     'Enfeeble': spells.Enfeeble},
                          'Skills': {}}
        self.pro_level = 3


class Ogre(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=40, strength=24, intel=18, wisdom=14, con=20,
                         charisma=10, dex=14, exp=random.randint(215, 295))
        self.equipment = dict(Weapon=items.Maul, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(50, 75)
        self.spellbook = {"Spells": {'Magic Missile': spells.MagicMissile,
                                     'Dispel': spells.Dispel},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}
        self.pro_level = 3


class Alligator(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Alligator', health=random.randint(60, 75), mana=20, strength=26, intel=8, wisdom=7,
                         con=20, charisma=10, dex=15, exp=random.randint(220, 300))
        self.equipment = dict(Weapon=AlligatorTail, Armor=items.NoArmor, OffHand=AlligatorTail,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 50)
        self.spellbook = {"Spells": {},
                          "Skills": {"Trip": spells.Trip}}
        self.pro_level = 3


class Troll(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=20, strength=24, intel=10, wisdom=8, con=24,
                         charisma=12, dex=15, exp=random.randint(225, 310))
        self.equipment = dict(Weapon=items.DoubleAxe, Armor=items.Cuirboulli, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(35, 45)
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': spells.MortalStrike}}
        self.pro_level = 3


class GoldenEagle(Animal):
    """

    """

    def __init__(self):
        super().__init__(name='Golden Eagle', health=random.randint(40, 50), mana=20, strength=19, intel=15, wisdom=15,
                         con=17, charisma=15, dex=25, exp=random.randint(230, 320))
        self.equipment = dict(Weapon=Claw2, Armor=items.NoArmor, OffHand=Claw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(50, 75)
        self.inventory['Feather'] = [items.Feather, 1]
        self.spellbook = {"Spells": {},
                          "Skills": {'Screech': spells.Screech}}
        self.flying = True
        self.pro_level = 3


class EvilCrusader(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=50, strength=21, intel=18, wisdom=17,
                         con=26, charisma=14, dex=14, exp=random.randint(240, 325))
        self.equipment = dict(Weapon=items.Pernach, Armor=items.Splint, OffHand=items.KiteShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(65, 90)
        self.inventory['Scrap Metal'] = [items.ScrapMetal, 1]
        self.spellbook = {"Spells": {'Smite': spells.Smite},
                          "Skills": {'Shield Slam': spells.ShieldSlam,
                                     'Disarm': spells.Disarm,
                                     'Shield Block': spells.ShieldBlock}}
        self.resistance['Shadow'] = 0.5
        self.resistance['Holy'] = -0.5
        self.pro_level = 3


class Werewolf(Monster):
    """
    Transform Level 3 creature
    """

    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(55, 75), mana=85, strength=24, intel=10, wisdom=10,
                         con=20, charisma=14, dex=20, exp=random.randint(220, 300))
        self.equipment = dict(Weapon=Claw3, Armor=AnimalHide, OffHand=Claw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(45, 55)
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike,
                                     'Howl': spells.Howl}}
        self.resistance['Physical'] = 0.1
        self.pro_level = 3


class Antlion(Animal):
    """
    modeled after the boss from FF2 (FFIV)
    """

    def __init__(self):
        super().__init__(name="Antlion", health=random.randint(52, 70), mana=70, strength=22, intel=8, wisdom=12,
                         con=18, charisma=12, dex=18, exp=random.randint(210, 310))
        self.equipment = dict(Weapon=Pincers2, Armor=Carapace, OffHand=Pincers2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 52)
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Physical'] = 0.25
        self.pro_level = 3


class InvisibleStalker(Elemental):
    """
    Invisible
    """

    def __init__(self):
        super().__init__(name="Invisible Stalker", health=random.randint(25, 46), mana=60, strength=19, intel=13,
                         wisdom=16, con=14, charisma=18, dex=35, exp=random.randint(230, 330))
        self.equipment = dict(Weapon=InvisibleBlade, Armor=items.NoArmor, OffHand=InvisibleBlade,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(65, 79)
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': spells.Backstab,
                                     'Poison Strike': spells.PoisonStrike}}
        self.resistance['Poison'] = 1.
        self.invisible = True
        self.pro_level = 3


class NightHag(Fey):
    """

    """

    def __init__(self):
        super().__init__(name="Night Hag", health=random.randint(30, 48), mana=105, strength=16, intel=22, wisdom=26,
                         con=12, charisma=14, dex=19, exp=random.randint(215, 312))
        self.equipment = dict(Weapon=items.Kris, Armor=items.SilverCloak, OffHand=items.Grimoire,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(70, 99)
        self.spellbook = {"Spells": {'Sleep': spells.Sleep,
                                     'Enfeeble': spells.Enfeeble,
                                     'Magic Missile': spells.MagicMissile},
                          "Skills": {'Nightmare Fuel': spells.NightmareFuel}}
        self.resistance['Fire'] = 0.25
        self.resistance['Cold'] = 0.25
        self.resistance['Physical'] = 0.25
        self.pro_level = 3


class Treant(Fey):
    """

    """

    def __init__(self):
        super().__init__(name="Treant", health=random.randint(52, 78), mana=65, strength=26, intel=16, wisdom=21,
                         con=20, charisma=12, dex=16, exp=random.randint(235, 320))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(60, 85)
        self.spellbook = {"Spells": {'Regen': spells.Regen},
                          "Skills": {'Multi-Attack': spells.DoubleStrike,
                                     'Throw Rock': spells.ThrowRock}}
        self.resistance['Fire'] = -1.
        self.resistance['Water'] = 1.5
        self.resistance['Poison'] = 1.
        self.resistance['Physical'] = 0.25
        self.pro_level = 3


class Ankheg(Monster):
    """

    """

    def __init__(self):
        super().__init__(name="Ankheg", health=random.randint(45, 69), mana=65, strength=23, intel=17, wisdom=14,
                         con=19, charisma=6, dex=14, exp=random.randint(240, 330))
        self.equipment = dict(Weapon=Claw3, Armor=Carapace, OffHand=Pincers2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(55, 78)
        self.spellbook = {"Spells": {},
                          "Skills": {'Trip': spells.Trip,
                                     'Acid Spit': spells.AcidSpit}}
        self.resistance['Holy'] = -0.25
        self.resistance['Poison'] = 1.
        self.resistance['Physical'] = 0.1
        self.pro_level = 3


class Cockatrice(Monster):
    """
    Level 3 Boss
    """

    def __init__(self):
        super().__init__(name='Cockatrice', health=580, mana=99, strength=30, intel=16, wisdom=15, con=16, charisma=16,
                         dex=22, exp=2500)
        self.equipment = dict(Weapon=Claw3, Armor=items.NoArmor, OffHand=DragonTail,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 5000
        self.inventory['Pendant'] = [items.random_item(4, typ='Accessory', subtyp='Pendant'), 1]
        self.inventory['Old Key'] = [items.OldKey, 1]
        self.spellbook = {"Spells": {'Petrify': spells.Petrify},
                          "Skills": {'Screech': spells.Screech}}
        self.flying = True
        self.resistance['Death'] = 1
        self.resistance['Stone'] = 0.5
        self.pro_level = 3


class Wendigo(Fey):
    """
    Level 3 Special Boss - guards third of six relics (HEXAGONUM) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Wendigo', health=750, mana=130, strength=32, intel=16, wisdom=19, con=21, charisma=14,
                         dex=22, exp=4500)
        self.equipment = dict(Weapon=Bite2, Armor=items.NoArmor, OffHand=DemonClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 7500
        self.inventory['Item'] = [items.random_item(random.randint(4, 5)), 1]
        self.inventory['Old Key'] = [items.OldKey, 1]
        self.spellbook = {"Spells": {'Regen': spells.Regen2,
                                     'Terrify': spells.Terrify},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.flying = True
        self.resistance['Fire'] = -0.75
        self.resistance['Ice'] = 1
        self.resistance['Death'] = 1
        self.resistance['Poison'] = 1
        self.pro_level = 4


# Level 4
class BrownSlime(Slime):
    """

    """

    def __init__(self):
        super().__init__(name='Brown Slime', health=random.randint(70, 112), mana=85, strength=17, intel=35, wisdom=40,
                         con=15, charisma=10, dex=8, exp=random.randint(390, 660))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(150, 280)
        self.inventory['Vedas'] = [items.Vedas, 1]
        self.spellbook = {'Spells': {'Mudslide': spells.Mudslide,
                                     'Enfeeble': spells.Enfeeble},
                          'Skills': {}}
        self.pro_level = 4


class Gargoyle(Elemental):
    """

    """

    def __init__(self):
        super().__init__(name='Gargoyle', health=random.randint(55, 75), mana=20, strength=26, intel=10, wisdom=12,
                         con=18, charisma=15, dex=21, exp=random.randint(410, 530))
        self.equipment = dict(Weapon=Claw3, Armor=StoneArmor, OffHand=Claw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(75, 125)
        self.spellbook = {"Spells": {'Blinding Fog': spells.BlindingFog},
                          "Skills": {}}
        self.flying = True
        self.resistance['Stone'] = 1
        self.resistance['Poison'] = 1
        self.pro_level = 4


class Conjurer(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(40, 65), mana=150, strength=14, intel=22, wisdom=18,
                         con=14, charisma=12, dex=13, exp=random.randint(415, 540))
        self.equipment = dict(Weapon=items.RuneStaff, Armor=items.GoldCloak, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(40, 65)
        self.inventory['Master Mana Potion'] = [items.MasterManaPotion, 1]
        self.spellbook = {"Spells": {'Fireball': spells.Fireball,
                                     'Icicle': spells.Icicle,
                                     'Lightning': spells.Lightning,
                                     'Aqualung': spells.Aqualung},
                          "Skills": {'Mana Drain': spells.ManaDrain}}
        self.pro_level = 4


class Chimera(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(60, 95), mana=140, strength=26, intel=14, wisdom=16,
                         con=20, charisma=14, dex=14, exp=random.randint(430, 580))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide2, OffHand=LionPaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(100, 250)
        self.spellbook = {"Spells": {'Molten Rock': spells.MoltenRock,
                                     'Dispel': spells.Dispel},
                          "Skills": {}}
        self.resistance['Physical'] = 0.5
        self.pro_level = 4


class Dragonkin(Dragon):
    """

    """

    def __init__(self):
        super().__init__(name='Dragonkin', health=random.randint(80, 115), mana=90, strength=26, intel=10, wisdom=18,
                         con=20, charisma=18, dex=20, exp=random.randint(450, 680))
        self.equipment = dict(Weapon=items.Halberd, Armor=items.Breastplate, OffHand=items.KiteShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(150, 300)
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': spells.Disarm,
                                     'Charge': spells.Charge}}
        self.flying = True
        self.pro_level = 4


class Griffin(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(75, 105), mana=110, strength=26, intel=21, wisdom=18,
                         con=18, charisma=16, dex=25, exp=random.randint(440, 650))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide2, OffHand=Claw3,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(140, 280)
        self.inventory['Elixir'] = [items.Elixir, 1]
        self.spellbook = {"Spells": {'Hurricane': spells.Hurricane},
                          "Skills": {'Screech': spells.Screech}}
        self.flying = True
        self.resistance['Physical'] = 0.5
        self.pro_level = 4


class DrowAssassin(Humanoid):
    """

    """

    def __init__(self):
        super().__init__(name='Drow Assassin', health=random.randint(65, 85), mana=75, strength=24, intel=16, wisdom=15,
                         con=14, charisma=22, dex=28, exp=random.randint(480, 680))
        self.equipment = dict(Weapon=items.Rondel, Armor=items.StuddedLeather, OffHand=items.Rondel,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(160, 250)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': spells.PoisonStrike,
                                     'Backstab': spells.Backstab,
                                     'Kidney Punch': spells.KidneyPunch,
                                     'Mug': spells.Mug,
                                     'Disarm': spells.Disarm,
                                     'Parry': spells.Parry}}
        self.pro_level = 4


class Cyborg(Construct):
    """
    Electric spells heal Cyborg
    """

    def __init__(self):
        super().__init__(name='Cyborg', health=random.randint(90, 120), mana=80, strength=28, intel=13, wisdom=10,
                         con=18, charisma=10, dex=14, exp=random.randint(490, 700))
        self.equipment = dict(Weapon=Laser, Armor=MetalPlating, OffHand=ForceField,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(200, 300)
        self.inventory['Scrap Metal'] = [items.ScrapMetal, 1]
        self.spellbook = {"Spells": {'Shock': spells.Shock},
                          "Skills": {}}
        self.resistance['Electric'] = 1.25
        self.resistance['Water'] = -0.75
        self.pro_level = 4

    def special_effects(self, enemy):
        if self.health < int(self.health * 0.25):
            spells.Detonate().use(self, enemy)


class DarkKnight(Fiend):
    """

    """

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(85, 110), mana=60, strength=28, intel=15, wisdom=12,
                         con=21, charisma=14, dex=17, exp=random.randint(500, 750))
        self.equipment = dict(Weapon=items.Flamberge, Armor=items.PlateMail, OffHand=items.KiteShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(300, 420)
        self.inventory['Flamberge'] = [items.Flamberge, 1]
        self.spellbook = {"Spells": {'Enhance Blade': spells.EnhanceBlade},
                          "Skills": {'Shield Slam': spells.ShieldSlam,
                                     'Disarm': spells.Disarm,
                                     'Shield Block': spells.ShieldBlock}}
        self.pro_level = 4


class Myrmidon(Elemental):
    """

    """

    def __init__(self):
        super().__init__(name='Myrmidon', health=random.randint(75, 125), mana=75, strength=26, intel=18, wisdom=16,
                         con=18, charisma=10, dex=14, exp=random.randint(520, 800))
        self.equipment = dict(Weapon=ElementalBlade, Armor=items.PlateMail, OffHand=items.KiteShield,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(300, 450)
        self.inventory['Elemental Mote'] = [items.ElementalMote, 1]
        self.resistance['Poison'] = 1
        self.pro_level = 4


class FireMyrmidon(Myrmidon):
    """
    Fire elemental; gains fire DOT applied to elemental blade
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Scorch': spells.Scorch},
                          "Skills": {'Shield Slam': spells.ShieldSlam}}
        self.resistance['Fire'] = 1.5
        self.resistance['Ice'] = -0.5


class IceMyrmidon(Myrmidon):
    """
    Ice elemental; gains Mortal Strike
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Ice Lance': spells.IceLance},
                          "Skills": {'Shield Slam': spells.ShieldSlam,
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
                          "Skills": {'Shield Slam': spells.ShieldSlam,
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
                          "Skills": {'Shield Slam': spells.ShieldSlam,
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
                          "Skills": {'Shield Slam': spells.ShieldSlam,
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
                          "Skills": {'Shield Slam': spells.ShieldSlam,
                                     'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Earth'] = -0.5
        self.resistance['Wind'] = 1.5


class DisplacerBeast(Fey):
    """

    """

    def __init__(self):
        super().__init__(name='Displacer Beast', health=random.randint(80, 115), mana=100, strength=27, intel=11,
                         wisdom=14, con=24, charisma=14, dex=26, exp=random.randint(500, 775))
        self.equipment = dict(Weapon=Claw3, Armor=AnimalHide2, OffHand=Tentacle,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(250, 360)
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.invisible = True
        self.pro_level = 4


class Golem(Construct):
    """
    Guardians of chests on Level 5
    """

    def __init__(self):
        super().__init__(name='Golem', health=1200, mana=100, strength=35, intel=25, wisdom=35, con=40, charisma=21,
                         dex=20, exp=8000)
        self.equipment = dict(Weapon=Laser2, Armor=StoneArmor2, OffHand=Laser,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 12000
        self.inventory['Power Core'] = [items.PowerCore, 1]
        self.spellbook = {"Spells": {'Enfeeble': spells.Enfeeble},
                          "Skills": {'Crush': spells.Crush}}
        self.resistance['Fire'] = 0.25
        self.resistance['Ice'] = -0.25
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.25
        self.resistance['Earth'] = 0.5
        self.pro_level = 5


class IronGolem(Golem):
    """
    Level 4 Boss
    """

    def __init__(self):
        super().__init__()
        self.equipment = dict(Weapon=Laser2, Armor=StoneArmor2, OffHand=ForceField2,
                              Ring=items.BarrierRing, Pendant=items.NoPendant)
        self.inventory['Aard of Being'] = [items.AardBeing, 1]
        self.spellbook = {"Spells": {'Enfeeble': spells.Enfeeble},
                          "Skills": {'Multi-Strike': spells.TripleStrike,
                                     'Crush': spells.Crush}}

    def special_effects(self, enemy):
        pass  # TODO


class Jester(Humanoid):
    """
    Level 4 Special Boss - guards fourth of six relics (LUNA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name="Jester", health=random.randint(500, 1500), mana=random.randint(125, 300),
                         strength=random.randint(10, 50), intel=random.randint(10, 50), wisdom=random.randint(10, 50),
                         con=random.randint(10, 60), charisma=99, dex=random.randint(10, 50),
                         exp=random.randint(5000, 15000))
        self.gold = random.randint(5000, 100000)
        self.equipment = dict(Weapon=items.Kukri, Armor=items.StuddedCuirboulli, OffHand=items.Kukri,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.inventory['Item'] = [items.random_item(5), 1]
        self.inventory['Old Key'] = [items.OldKey, 1]
        self.spellbook = {"Spells": {'Silence': spells.Silence},
                          "Skills": {'Gold Toss': spells.GoldToss,
                                     'Slot Machine': spells.SlotMachine}}
        self.resistance = {'Fire': random.uniform(-1, 1),
                           'Ice': random.uniform(-1, 1),
                           'Electric': random.uniform(-1, 1),
                           'Water': random.uniform(-1, 1),
                           'Earth': random.uniform(-1, 1),
                           'Wind': random.uniform(-1, 1),
                           'Shadow': random.uniform(-1, 1),
                           'Death': 1.,
                           'Stone': 1.,
                           'Holy': random.uniform(-1, 1),
                           'Poison': random.uniform(-1, 1),
                           'Physical': random.uniform(-1, 1)}
        self.pro_level = 5

    def special_effects(self, enemy):
        print("Jester: The wheel of time stops for no one! HAHA!")
        time.sleep(0.5)
        print("The Jester's stats and resistances have been randomized.")
        time.sleep(1)
        self.strength = random.randint(10, 50)
        self.intel = random.randint(10, 50)
        self.wisdom = random.randint(10, 50)
        self.con = random.randint(10, 60)
        self.dex = random.randint(10, 50)
        self.resistance = {'Fire': random.uniform(-1, 1),
                           'Ice': random.uniform(-1, 1),
                           'Electric': random.uniform(-1, 1),
                           'Water': random.uniform(-1, 1),
                           'Earth': random.uniform(-1, 1),
                           'Wind': random.uniform(-1, 1),
                           'Shadow': random.uniform(-1, 1),
                           'Death': 1.,
                           'Stone': 1.,
                           'Holy': random.uniform(-1, 1),
                           'Poison': random.uniform(-1, 1),
                           'Physical': random.uniform(-1, 1)}


# Level 5
class ShadowSerpent(Elemental):
    """

    """

    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=100, strength=28, intel=18,
                         wisdom=15, con=22, charisma=16, dex=23, exp=random.randint(780, 1090))
        self.equipment = dict(Weapon=SnakeFang2, Armor=SnakeScales2, OffHand=SnakeFang2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(280, 485)
        self.inventory['Megalixir'] = [items.Megalixir, 1]
        self.spellbook = {"Spells": {'Corruption': spells.Corruption},
                          "Skills": {'Multi-Strike': spells.DoubleStrike}}
        self.resistance['Shadow'] = 0.9
        self.resistance['Holy'] = -0.75
        self.resistance['Poison'] = 0.25
        self.pro_level = 5


class Aboleth(Slime):
    """

    """

    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(210, 500), mana=120, strength=25, intel=50, wisdom=50,
                         con=25, charisma=12, dex=10, exp=random.randint(650, 1230))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(130, 750)
        self.inventory['Aard of Being'] = [items.AardBeing, 1]
        self.spellbook = {"Spells": {'Disease Breath': spells.DiseaseBreath,
                                     'Enfeeble': spells.Enfeeble},
                          "Skills": {'Acid Spit': spells.AcidSpit}}
        self.resistance['Poison'] = 1.5
        self.pro_level = 5


class Beholder(Aberration):
    """

    """

    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=100, strength=25, intel=40, wisdom=35,
                         con=28, charisma=20, dex=20, exp=random.randint(800, 1200))
        self.equipment = dict(Weapon=Gaze, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(300, 500)
        self.inventory['Medusa Shield'] = [items.MedusaShield, 1]
        self.spellbook = {"Spells": {'Magic Missile': spells.MagicMissile2,
                                     'Terrify': spells.Terrify,
                                     'Dispel': spells.Dispel,
                                     'Disintegrate': spells.Disintegrate},
                          "Skills": {'Mana Drain': spells.ManaDrain}}
        self.flying = True
        self.resistance['Death'] = 1
        self.pro_level = 5


class Behemoth(Aberration):
    """

    """

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=100, strength=38, intel=25, wisdom=20,
                         con=30, charisma=18, dex=25, exp=random.randint(920, 1250))
        self.equipment = dict(Weapon=LionPaw, Armor=AnimalHide2, OffHand=LionPaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(400, 550)
        self.spellbook = {"Spells": {'Holy': spells.Holy3,
                                     'Regen': spells.Regen3},
                          "Skills": {'Multi-Strike': spells.DoubleStrike,
                                     'Counterspell': spells.Counterspell}}
        self.resistance['Fire'] = 1.
        self.resistance['Electric'] = 0.75
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Holy'] = 0.75
        self.resistance['Poison'] = 0.75
        self.resistance['Physical'] = 0.5
        self.pro_level = 5

    def special_effects(self, enemy):
        if not self.is_alive():
            spells.FinalAttack().use(self, enemy)


class Lich(Undead):
    """

    """

    def __init__(self):
        super().__init__(name='Lich', health=random.randint(210, 300), mana=120, strength=25, intel=35, wisdom=40,
                         con=20, charisma=36, dex=22, exp=random.randint(880, 1220))
        self.equipment = dict(Weapon=LichHand, Armor=items.WizardRobe, OffHand=items.Necronomicon,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(400, 530)
        self.inventory['Necronomicon'] = [items.Necronomicon, 1]
        self.spellbook = {"Spells": {'Ice Blizzard': spells.IceBlizzard,
                                     'Desoul': spells.Desoul,
                                     'Terrify': spells.Terrify,
                                     'Disintegrate': spells.Disintegrate},
                          "Skills": {'Health/Mana Drain': spells.HealthManaDrain}}
        self.resistance['Ice'] = 0.9
        self.pro_level = 5


class Basilisk(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(220, 325), mana=120, strength=29, intel=26, wisdom=30,
                         con=27, charisma=17, dex=20, exp=random.randint(930, 1200))
        self.equipment = dict(Weapon=SnakeFang2, Armor=SnakeScales2, OffHand=SnakeFang2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(380, 520)
        self.spellbook = {"Spells": {'Petrify': spells.Petrify,
                                     'Poison Breath': spells.PoisonBreath},
                          "Skills": {'Mortal Strike': spells.MortalStrike2}}
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 0.5
        self.resistance['Poison'] = 0.75
        self.pro_level = 5


class MindFlayer(Aberration):
    """

    """

    def __init__(self):
        super().__init__(name='Mind Flayer', health=random.randint(190, 285), mana=150, strength=28, intel=40,
                         wisdom=35, con=25, charisma=22, dex=18, exp=random.randint(890, 1150))
        self.equipment = dict(Weapon=items.MithrilshodStaff, Armor=items.WizardRobe, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(450, 600)
        self.inventory['Wizard Robe'] = [items.WizardRobe, 1]
        self.spellbook = {"Spells": {'Doom': spells.Doom,
                                     'Terrify': spells.Terrify,
                                     'Corruption': spells.Corruption},
                          "Skills": {'Mana Drain': spells.ManaDrain}}
        self.resistance['Shadow'] = 0.5
        self.resistance['Death'] = 1
        self.resistance['Holy'] = -0.25
        self.pro_level = 5


class Sandworm(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Sandworm', health=random.randint(230, 300), mana=190, strength=34, intel=21, wisdom=22,
                         con=30, charisma=20, dex=18, exp=random.randint(910, 1200))
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(380, 490)
        self.spellbook = {"Spells": {'Earthquake': spells.Earthquake,
                                     'Sandstorm': spells.Sandstorm},
                          "Skills": {'Consume Item': spells.ConsumeItem}}
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.25
        self.resistance['Earth'] = 1
        self.resistance['Stone'] = 1
        self.resistance['Poison'] = 1
        self.resistance['Physical'] = 0.75
        self.pro_level = 5


class Warforged(Construct):
    """

    """

    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=120, strength=40, intel=20, wisdom=16,
                         con=33, charisma=12, dex=10, exp=random.randint(880, 1180))
        self.equipment = dict(Weapon=Cannon, Armor=StoneArmor2, OffHand=ForceField3,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(380, 490)
        self.inventory['Scrap Metal'] = [items.ScrapMetal, 1]
        self.spellbook = {"Spells": {'Silence': spells.Silence},
                          "Skills": {'Turtle': spells.Turtle}}
        self.pro_level = 5

    def special_effects(self, enemy):
        if not any([self.status_effects['Silence'][0],
                    self.status_effects['Stun'][0],
                    self.status_effects['Sleep'][0]]):
            if self.health < int(self.health_max * 0.25) and not self.turtle:
                self.turtle = True
            if self.health > int(self.health_max * 0.75) and self.turtle:
                self.turtle = False
            if self.turtle:
                heal = int(self.health_max * 0.25)
                if heal + self.health > self.health_max:
                    heal = self.health_max - self.health
                self.health += heal
                print("{} heals for {}.".format(self.name, heal))


class Wyrm(Dragon):
    """

    """

    def __init__(self):
        super().__init__(name='Wyrm', health=random.randint(320, 400), mana=150, strength=38, intel=28, wisdom=30,
                         con=28, charisma=22, dex=23, exp=random.randint(920, 1180))
        self.equipment = dict(Weapon=DragonTail2, Armor=DragonScale, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(650, 830)
        self.spellbook = {'Spells': {'Volcano': spells.Volcano},
                          'Skills': {'Multi-Strike': spells.TripleStrike}}
        self.pro_level = 5


class Hydra(Monster):
    """

    """

    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(260, 375), mana=150, strength=37, intel=30, wisdom=26,
                         con=28, charisma=24, dex=22, exp=random.randint(900, 1150))
        self.equipment = dict(Weapon=Bite2, Armor=DragonScale, OffHand=DragonTail,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(400, 550)
        self.spellbook = {'Spells': {'Tsunami': spells.Tsunami},
                          'Skills': {'Multi-Strike': spells.TripleStrike}}
        self.resistance['Electric'] = -1
        self.resistance['Water'] = 1.5
        self.resistance['Death'] = 1
        self.resistance['Stone'] = 0.5
        self.resistance['Poison'] = 0.75
        self.resistance['Physical'] = 0.25
        self.pro_level = 5


class Wyvern(Dragon):
    """

    """

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(320, 410), mana=150, strength=35, intel=33, wisdom=24,
                         con=30, charisma=25, dex=40, exp=random.randint(950, 1200))
        self.equipment = dict(Weapon=DragonClaw2, Armor=DragonScale, OffHand=DragonClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(420, 570)
        self.spellbook = {"Spells": {'Tornado': spells.Tornado},
                          "Skills": {'Piercing Strike': spells.PiercingStrike}}
        self.flying = True
        self.pro_level = 5


class Archvile(Fiend):
    """

    """

    def __init__(self):
        super().__init__(name='Archvile', health=random.randint(360, 460), mana=200, strength=32, intel=31, wisdom=35,
                         con=38, charisma=28, dex=32, exp=random.randint(1010, 1280))
        self.equipment = dict(Weapon=items.BattleGauntlet, Armor=DemonArmor2, OffHand=items.BattleGauntlet,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(375, 555)
        self.spellbook = {"Spells": {'Sleep': spells.Sleep,
                                     'Corruption': spells.Corruption,
                                     'Terrify': spells.Terrify,
                                     'Regen': spells.Regen2,
                                     'Firestorm': spells.Firestorm},
                          "Skills": {'Parry': spells.Parry}}
        self.resistance['Fire'] = 1.
        self.resistance['Ice'] = 0.5
        self.resistance['Electric'] = 0.5
        self.resistance['Poison'] = 1.
        self.pro_level = 5


class BrainGorger(Aberration):
    """

    """

    def __init__(self):
        super().__init__(name='Brain Gorger', health=random.randint(310, 420), mana=250, strength=27, intel=40,
                         wisdom=35, con=31, charisma=25, dex=36, exp=random.randint(1050, 1310))
        self.status_effects['Blind'] = [True, -1]
        self.equipment = dict(Weapon=Tentacle2, Armor=items.NoArmor, OffHand=Tentacle2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = random.randint(320, 515)
        self.inventory['Intelligence Potion'] = items.IntelPotion
        self.spellbook = {"Spells": {'Terrify': spells.Terrify,
                                     'Weaken Mind': spells.WeakenMind},
                          "Skills": {'Brain Gorge': spells.BrainGorge}}
        self.resistance['Fire'] = 0.25
        self.resistance['Ice'] = 0.25
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = 0.25
        self.resistance['Earth'] = 0.25
        self.resistance['Wind'] = 0.25
        self.resistance['Poison'] = 1.
        self.pro_level = 5


class Domingo(Aberration):
    """
    Level 5 Special Boss - guards fifth of six relics (LUNA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Domingo', health=1500, mana=999, strength=0, intel=50, wisdom=40, con=45, charisma=60,
                         dex=50, exp=30000)
        self.equipment = dict(Weapon=items.NoWeapon, Armor=items.NoArmor, OffHand=items.NoOffHand,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 25000
        self.spellbook = {"Spells": {'Ultima': spells.Ultima},
                          "Skills": {'Multi-Cast': spells.DoubleCast}}
        self.flying = True
        self.resistance = {'Fire': 0.25,
                           'Ice': 0.25,
                           'Electric': 0.25,
                           'Water': 0.25,
                           'Earth': 1.,
                           'Wind': -0.25,
                           'Shadow': 0.25,
                           'Death': 1.,
                           'Stone': 1.,
                           'Holy': 0.25,
                           'Poison': 0.25,
                           'Physical': 0}
        self.pro_level = 5


class RedDragon(Dragon):
    """
    Level 5 Boss
    Transform Level 5 creature
    Highly resistant to spells and will heal from fire spells
    """

    def __init__(self):
        super().__init__(name='Red Dragon', health=2000, mana=500, strength=50, intel=38, wisdom=45, con=55,
                         charisma=40, dex=35, exp=50000)
        self.equipment = dict(Weapon=DragonTail2, Armor=DragonScale, OffHand=DragonClaw2,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 50000
        self.inventory['Item'] = [items.random_item(random.randint(5, 6)), 1]
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
                           'Stone': 1.,
                           'Holy': 0.5,
                           'Poison': 0.75,
                           'Physical': 0.25}
        self.pro_level = 5


# Final Boss Guard
class Cerberus(Fiend):
    """
    Level 6 Special Boss - guards sixth and final of six relics (INFINITAS) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Cerberus', health=2500, mana=500, strength=65, intel=28, wisdom=45, con=60, charisma=40,
                         dex=38, exp=100000)
        self.equipment = dict(Weapon=CerberusBite, Armor=CerberusHide, OffHand=CerberusClaw,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.gold = 100000
        self.inventory['Item'] = [items.random_item(6), 1]
        self.spellbook = {"Spells": {},
                          "Skills": {'Multi-Strike': spells.TripleStrike,
                                     'Trip': spells.Trip}}
        self.resistance['Fire'] = 1
        self.resistance['Ice'] = -0.25
        self.resistance['Electric'] = 0.5
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Holy'] = 0.25
        self.resistance['Physical'] = 0.5
        self.pro_level = 6


# Final Boss
class Devil(Fiend):
    """
    Final Boss; highly resistant to spells; immune to weapon damage except ultimate weapons
    Choose Fate ability:
     if Attack is chosen, damage mod is increased (increases attack damage and armor)
     if Hellfire is chosen, spell mod is increased (increase magic, healing, and magic defense)
     if Crush is chosen, both damage and spell mod decrease
    """

    def __init__(self):
        super().__init__(name='The Devil', health=5000, mana=1000, strength=75, intel=55, wisdom=70, con=85,
                         charisma=80, dex=45, exp=0)
        self.equipment = dict(Weapon=DevilBlade, Armor=DevilSkin, OffHand=DevilBlade,
                              Ring=items.NoRing, Pendant=items.NoPendant)
        self.spellbook = {"Spells": {'Hellfire': spells.Hellfire,
                                     'Terrify': spells.Terrify,
                                     'Regen': spells.Regen3},
                          "Skills": {'Choose Fate': spells.ChooseFate,
                                     'Crush': spells.Crush}}
        self.resistance = {'Fire': 0.5,
                           'Ice': 0.5,
                           'Electric': 0.5,
                           'Water': 0.5,
                           'Earth': 0.5,
                           'Wind': 0.5,
                           'Shadow': 0.5,
                           'Death': 1.,
                           'Stone': 1.,
                           'Holy': -0.25,
                           'Poison': 1.,
                           'Physical': 1.}
        self.damage_mod = 0
        self.spell_mod = 0
        self.pro_level = 99

    def check_mod(self, mod, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = self.equipment['Weapon']().damage
            class_mod += self.damage_mod + self.strength
            if self.status_effects['Attack'][0]:
                weapon_mod += self.status_effects['Attack'][2]
            return weapon_mod + class_mod
        elif mod == 'offhand':
            class_mod += self.damage_mod + self.strength
            off_mod = self.equipment['OffHand']().damage
            if self.status_effects['Attack'][0]:
                off_mod += self.status_effects['Attack'][2]
            return int((off_mod + class_mod) * 0.75)
        elif mod == 'armor':
            class_mod += self.damage_mod
            armor_mod = self.equipment['Armor']().armor
            if self.status_effects['Defense'][0]:
                armor_mod += self.status_effects['Defense'][2]
            return armor_mod + class_mod
        elif mod == 'magic':
            magic_mod = self.intel
            class_mod += self.spell_mod
            if self.status_effects['Magic'][0]:
                magic_mod += self.status_effects['Magic'][2]
            return magic_mod + class_mod
        elif mod == 'magic def':
            m_def_mod = self.wisdom
            class_mod += self.spell_mod
            if self.status_effects['Magic Defense'][0]:
                m_def_mod += self.status_effects['Magic Defense'][2]
            return m_def_mod + class_mod
        elif mod == 'heal':
            class_mod += self.spell_mod
            heal_mod = self.wisdom * self.pro_level
            if self.status_effects['Magic'][0]:
                heal_mod += self.status_effects['Magic'][2]
            return heal_mod + class_mod
        elif mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return -0.25
            res_mod = self.resistance[typ]
            return res_mod
        elif mod == 'luck':
            luck_mod = self.charisma // luck_factor
            return luck_mod
