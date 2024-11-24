###########################################
""" enemy manager """

# Imports
import random
from textwrap import wrap

from character import Character, Resource, Stats, StatusEffect
import items
import abilities


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
    # random_monster = Test()
    if random_monster.name == "Myrmidon":
        random_monster = random.choice([FireMyrmidon(),
                                        IceMyrmidon(),
                                        ElectricMyrmidon(),
                                        WaterMyrmidon(),
                                        EarthMyrmidon(),
                                        WindMyrmidon()])

    return random_monster


class Enemy(Character):
    """
    Same as player character with notable exceptions
    cls: just the name of the enemy (used for transforming and other class checks)
    experience: number of experience points awarded for defeating the enemy
    enemy_typ: defines the base type template used for enemy
    picture(str): file that contains the ascii art for the enemy 
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, Resource(health+con, health+con), Resource(mana+intel, mana+intel),
                         Stats(strength, intel, wisdom, con, charisma, dex))
        self.name = name
        self.cls = self
        self.experience = exp
        self.gold = 0
        self.enemy_typ = ""
        self.action_stack = []
        self.turtle = False
        self.picture = "test.txt"


    def __str__(self):
        return (f"{self.name} | "
                f"Health: {self.health.current}/{self.health.max} | "
                f"Mana: {self.mana.current}/{self.mana.max}")

    def inspect(self):
        stats_str = [
            "{:15}{:>4}".format("Strength:", f"{self.stats.strength}"),
            "{:15}{:>4}".format("Intelligence:", f"{self.stats.intel}"),
            "{:15}{:>4}".format("Wisdom:", f"{self.stats.wisdom}"),
            "{:15}{:>4}".format("Constitution:", f"{self.stats.con}"),
            "{:15}{:>4}".format("Charisma:", f"{self.stats.charisma}"),
            "{:15}{:>4}".format("Dexterity:", f"{self.stats.dex}")
                    ]
        stats_str = "\n".join(stats_str)
        resist_str = [
            "{:12}{:>6}  {:12}{:>6}".format(
                "Fire:", f"{self.resistance['Fire']}", "Shadow:", f"{self.resistance['Shadow']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Ice:", f"{self.resistance['Ice']}", "Death:", f"{self.resistance['Death']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Electric:", f"{self.resistance['Electric']}", "Stone:", f"{self.resistance['Stone']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Water:", f"{self.resistance['Water']}", "Holy:", f"{self.resistance['Holy']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Earth:", f"{self.resistance['Earth']}", "Poison:", f"{self.resistance['Poison']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Wind:", f"{self.resistance['Wind']}", "Physical:", f"{self.resistance['Physical']}")
                        ]
        resist_str = "\n".join(resist_str)
        specials = list(self.spellbook['Spells'].keys()) + list(self.spellbook['Skills'].keys())
        specials = ", ".join(specials)
        specials = "\n".join(wrap(f"Specials: {specials}", 50))
        text = (
            f"\nName: {self.name} Type: {self.enemy_typ}\n\n"
            f"Stats:\n"
            f"{stats_str}\n\n"
            f"Resistances:\n"
            f"{resist_str}\n\n"
            f"{specials}"
        )
        return text

    def options(self, target, action_list):
        if self.status_effects['Berserk'].active:
            return "Attack"
        if not self.turtle:
            if self.name != 'Test':
                action_list = ['Attack']
            else:
                action_list = []
            if not self.status_effects['Silence'].active:
                for spell_name, spell in self.spellbook['Spells'].items():
                    if self.spellbook['Spells'][spell_name].passive:
                        continue
                    if self.spellbook['Spells'][spell_name].cost <= self.mana.current:
                        action_list.append(spell)
            for skill_name, skill in self.spellbook['Skills'].items():
                if any([self.spellbook['Skills'][skill_name].passive,
                        self.spellbook['Skills'][skill_name].name == "Backstab" and not target.incapacitated(),
                        self.spellbook["Skills"][skill_name].weapon and self.status_effects["Disarm"].active]):
                    continue
                if self.spellbook['Skills'][skill_name].cost <= self.mana.current:
                    action_list.append(skill)
            if self.status_effects['Disarm'].active:
                action_list.append("Pickup Weapon")
            action = random.choice(action_list)
            if self.action_stack:
                pass  # TODO
            return action
        raise NotImplementedError

    def combat_turn(self, game, target, action, in_combat):
        combat_text = ""
        valid_entry = True
        cover = False
        flee = False
        fail_flee = False
        tile = target.world_dict[(target.location_x, target.location_y, target.location_z)]
        if self.incapacitated():
            in_combat = True
        else:
            if target.cls.name in ['Warlock', 'Shadowcaster']:
                if 'Cover' in target.familiar.spellbook['Skills'] and not random.randint(0, 3):
                    cover = True
            if (target.level.pro_level * target.level.level) >= 10 and target.level.pro_level > self.level.pro_level and \
                    random.randint(0, target.level.pro_level - self.level.pro_level) and 'Boss' not in str(tile) and \
                    self.name != 'Mimic':
                if not random.randint(0, 1):
                    if random.randint(0, self.stats.dex) > random.randint(0, target.stats.dex):
                        in_combat = False
                        flee = True
                        combat_text += f"{self.name} runs away!\n"
                    else:
                        combat_text += f"{self.name} tries to run away...but fails.\n"
                        fail_flee = True
            if not flee and not fail_flee:
                if action == "Attack":
                    wd_str, _, _ = self.weapon_damage(target, cover=cover)
                    combat_text += wd_str
                elif action == "Pickup Weapon":
                    combat_text += f"{self.name} picks up their weapon.\n"
                    self.status_effects['Disarm'].active = False
                elif action.typ == "Skill":
                    skill_str = f"{self.name} uses {action.name}.\n"
                    if action.name in ["Slot Machine", "Choose Fate", "Blackjack"]:
                        skill_str += action.use(game, self, target=target)
                    elif action.name == "Smoke Screen":
                        skill_str += action.use(self, target=target)
                        flee, flee_str = self.flee(target, smoke=True)
                        skill_str += flee_str
                        if flee:
                            in_combat = False
                    else:
                        skill_str += action.use(self, target=target, cover=cover)
                    combat_text += skill_str
                    if action.name == "Shapeshift":
                        wd_str, _, _ = self.weapon_damage(defender=target, cover=cover)
                        combat_text += wd_str
                    try:
                        if action.rank == 1:
                            if (target.cls in ["Diviner", "Geomancer"]) and \
                                    action.name not in target.spellbook['Skills']:
                                target.spellbook['Skills'][action.name] = action
                                combat_text += action
                                combat_text += f"You have gained the ability to cast {action.name}.\n"
                        elif action.rank == 2:
                            if target.cls == "Geomancer" and action.name not in target.spellbook['Skills']:
                                target.spellbook['Skills'][action.name] = action
                                combat_text += action
                                combat_text == f"You have gained the ability to cast {action.name}.\n"
                    except AttributeError:
                        pass
                elif action.typ == "Spell":
                    spell_str = f"{self.name} casts {action.name}.\n"
                    spell_str += action.cast(self, target=target, cover=cover)
                    combat_text += spell_str
                    try:
                        if action.rank == 1:
                            if target.cls in ["Diviner", "Geomancer"] and action.name not in target.spellbook['Spells']:
                                target.spellbook['Spells'][action.name] = action
                                combat_text += action
                                combat_text += f"You have gained the ability to cast {action.name}.\n"
                        elif action.rank == 2:
                            if target.cls == "Geomancer" and action.name not in target.spellbook['Spells']:
                                target.spellbook['Spells'][action.name] = action
                                combat_text += action
                                combat_text += f"You have gained the ability to cast {action.name}.\n"
                    except AttributeError:
                        pass
                else:
                    combat_text += f"{self.name} doesn't do anything.\n"
        if combat_text:
            import utils
            battlebox = utils.TextBox(game)
            battlebox.print_text_in_rectangle(combat_text)
            game.stdscr.getch()
            battlebox.clear_rectangle()
        if not self.is_alive():
            in_combat = False
        return valid_entry, in_combat, flee

    def check_mod(self, mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.status_effects["Disarm"].active))
            class_mod += (max(self.stats.strength, self.stats.dex) // 3)
            weapon_mod += self.status_effects['Attack'].extra * self.status_effects['Attack'].active
            return weapon_mod + class_mod
        if mod == 'shield':
            block_mod = 0
            if self.equipment['OffHand'].subtyp == 'Shield':
                block_mod = round(self.equipment['OffHand'].mod * (1 + ('Shield Block' in self.spellbook['Skills'])) * 100)
            if self.equipment['Ring'].mod == "Block":
                block_mod += 25
            return block_mod
        if mod == 'offhand':
            try:
                off_mod = self.equipment['OffHand'].damage + (max(self.stats.strength, self.stats.dex) // 5)
                off_mod += self.status_effects['Attack'].extra * self.status_effects['Attack'].active
                return int((off_mod + class_mod) * 0.75)
            except AttributeError:
                return 0
        if mod == 'armor':
            armor_mod = self.equipment['Armor'].armor
            if self.turtle:
                class_mod += 99
            armor_mod += self.status_effects['Defense'].extra * self.status_effects['Defense'].active
            return armor_mod * int(not ignore) + class_mod
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                magic_mod += self.equipment['OffHand'].mod
            if self.equipment['Weapon'].subtyp == 'Staff':
                magic_mod += int(self.equipment['Weapon'].damage * 1.5)
            magic_mod += self.status_effects['Magic'].extra * self.status_effects['Magic'].active
            return magic_mod + class_mod
        if mod == 'magic def':
            m_def_mod = self.stats.wisdom
            if self.turtle:
                class_mod += 99
            m_def_mod += self.status_effects['Magic Defense'].extra * self.status_effects['Magic Defense'].active
            return m_def_mod + class_mod
        if mod == 'heal':
            heal_mod = self.stats.wisdom * self.level.pro_level
            if self.equipment['OffHand'].subtyp == 'Tome':
                heal_mod += self.equipment['OffHand'].mod
            elif self.equipment['Weapon'].subtyp == 'Staff':
                heal_mod += int(self.equipment['Weapon'].damage * 1.5)
            heal_mod += self.status_effects['Magic'].extra * self.status_effects['Magic'].active
            return heal_mod + class_mod
        if mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return -0.25
            res_mod = self.resistance[typ]
            if self.flying:
                if typ == 'Earth':
                    res_mod = 1
                elif typ == 'Wind':
                    res_mod = -0.25
            return res_mod
        if mod == 'luck':
            luck_mod = self.stats.charisma // luck_factor
            return luck_mod
        return 0


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
        self.picture = "slime.txt"


class Animal(Enemy):
    """
    Animal type; no special features
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex, exp)
        self.enemy_typ = 'Animal'
        self.inventory['Mystery Meat'] = [items.MysteryMeat()]


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

    def __init__(self):
        super().__init__(name="Bite", damage=3, crit=0.05, description="", off=False)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if self.crit > random.random():
            special_str += "The bite is diseased.\n"
            if not random.randint(0, 39 // crit):
                special_str += f"The bite is diseased, crippling {target.name} and lowering their constitution by 1.\n"
                target.stats.con -= 1
            else:
                special_str += f"{target.name} resists the disease.\n"
        return special_str


class Bite2(Bite):

    def __init__(self):
        super().__init__()
        self.damage = 15
        self.crit = 0.2

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if self.crit > random.random():
            special_str += "The bite is diseased.\n"
            if not random.randint(0, 19 // crit):
                special_str += f"The disease cripples {target.name}, lowering their constitution by 1.\n"
                target.stats.con -= 1
            else:
                special_str += f"{target.name} resists the disease.\n"
        return special_str


class VampireBite(Bite):

    def __init__(self):
        super().__init__()
        self.damage = 10
        self.crit = 0.15

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if self.crit > random.random():
            wielder.health.current += damage
            wielder.health.current = min(wielder.health.current, wielder.health.max)
            special_str += f"{wielder.name} drains {target.name} and gains {damage} life.\n"
        return special_str


class Claw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Claw", damage=4, crit=0.2, description="", off=True)
        self.att_name = 'swipes'


class Claw2(Claw):

    def __init__(self):
        super().__init__()
        self.damage = 10
        self.crit = 0.25


class Claw3(Claw):

    def __init__(self):
        super().__init__()
        self.special = True
        self.damage = 18
        self.crit = 0.33

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.stats.dex // 2) * crit, wielder.stats.dex * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Bleed'].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.stats.dex // 10)
                bleed_dmg = int(max(wielder.stats.dex // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'] = StatusEffect(True,
                                                              max(duration, target.status_effects['Bleed'].duration),
                                                              max(bleed_dmg, target.status_effects['Bleed'].extra))
        return special_str


class BearClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Bear Claw", damage=12, crit=0.2, description="", off=True)
        self.special = True
        self.att_name = 'mauls'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.stats.strength // 2) * crit, wielder.stats.strength * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Bleed'].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = int(max(wielder.stats.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'] = StatusEffect(True,
                                                              max(duration, target.status_effects['Bleed'].duration),
                                                              max(bleed_dmg, target.status_effects['Bleed'].extra))
        return special_str


class Stinger(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Stinger", damage=5, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'stings'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Poison')
        if resist < 1:
            if random.randint((wielder.stats.dex * crit) // 2, (wielder.stats.dex * crit)) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Poison'].active:
                    special_str += f"{target.name} is poisoned.\n"
                else:
                    special_str += "The poison persists.\n"
                duration = max(1, wielder.stats.dex // 10)
                damage = int(target.health.max * 0.005)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects['Poison'] = StatusEffect(True,
                                                               max(duration, target.status_effects['Poison'].duration),
                                                               max(pois_dmg, target.status_effects['Poison'].extra))
        return special_str


class Pincers(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Pincers", damage=4, crit=0.15, description="", off=True)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Poison')
        if resist < 1:
            if random.randint(wielder.stats.dex // 2, wielder.stats.dex) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Poison'].active:
                    special_str += f"{target.name} is poisoned.\n"
                else:
                    special_str += "The poison persists.\n"
                duration = max(1, wielder.stats.dex // 10)
                damage = int(target.health.max * 0.005)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects['Poison'] = StatusEffect(True,
                                                               max(duration, target.status_effects['Poison'].duration),
                                                               max(pois_dmg, target.status_effects['Poison'].extra))
                if not target.status_effects['Stun'].active:
                    p_resist = target.check_mod('resist', enemy=wielder, typ='Physical')
                    if crit > 1:
                        if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - p_resist) \
                                > random.randint(target.stats.con // 2, target.stats.con):
                            s_duration = max(1, wielder.stats.strength // 10)
                            target.status_effects['Stun'] = StatusEffect(True, s_duration)
                            special_str += f"{target.name} is stunned.\n"
        return special_str


class Pincers2(Pincers):

    def __init__(self):
        super().__init__()
        self.damage = 10
        self.crit = 0.2


class DemonClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Demon Claw", damage=5, crit=0.25, description="", off=True)
        self.special = True
        self.att_name = 'claws'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        special_str += abilities.Doom().cast(wielder, target=target, special=True)
        return special_str


class DemonClaw2(DemonClaw):

    def __init__(self):
        super().__init__()
        self.damage = 15
        self.crit = 0.33
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        special_str += abilities.Desoul().cast(wielder, target=target, special=True)
        return special_str


class SnakeFang(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Snake Fang", damage=5, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'strikes'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Poison')
        if resist < 1:
            if random.randint((wielder.stats.dex * crit) // 2, (wielder.stats.dex * crit)) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Poison'].active:
                    special_str += f"{target.name} is poisoned.\n"
                else:
                    special_str += "The poison persists.\n"
                duration = max(1, wielder.stats.dex // 10)
                damage = int(target.health.max * 0.005)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects['Poison'] = StatusEffect(True,
                                                               max(duration, target.status_effects['Poison'].duration),
                                                               max(pois_dmg, target.status_effects['Poison'].extra))
        return special_str


class SnakeFang2(SnakeFang):

    def __init__(self):
        super().__init__()
        self.damage = 16
        self.crit = 0.33


class AlligatorTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Alligator Tail", damage=12, crit=0.1, description="", off=False)
        self.special = True
        self.att_name = 'swipes'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.status_effects['Stun'].active:
            resist = target.check_mod('resist', enemy=wielder, typ='Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - resist) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        duration = max(1, wielder.stats.strength // 10)
                        target.status_effects['Stun'] = StatusEffect(True, duration)
                        special_str += f"{target.name} is stunned.\n"
        return special_str


class LionPaw(NaturalWeapon):
    """
    Chance to berserk enemy
    """

    def __init__(self):
        super().__init__(name="Lion Paw", damage=17, crit=0.15, description="", off=True)
        self.att_name = 'swipes'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.status_effects['Berserk'].active:
            if crit > 1:
                if random.randint(0, wielder.stats.strength) > random.randint(target.stats.con // 2, target.stats.con):
                    duration = max(3, wielder.stats.strength // 10)
                    target.status_effects['Berserk'] = StatusEffect(True, duration)
                    special_str += f"{target.name} is enraged.\n"
        return special_str


class Laser(NaturalWeapon):
    """
    ignores armor
    """

    def __init__(self):
        super().__init__(name="Laser", damage=20, crit=0.25, description="", off=True)
        self.ignore = True
        self.att_name = 'zaps'


class Laser2(Laser):
    """
    Chance on crit to permanently damage the enemy, reducing a random stat by 1
    """

    def __init__(self):
        super().__init__()
        self.damage = 35
        self.crit = 0.4
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        t_chance = target.check_mod('luck', enemy=wielder, luck_factor=5) / 100
        if crit > 1:
            if random.random() > 0.95 + t_chance:  # 5% chance minus charisma // 5
                stat_list = ['strength', 'intelligence', 'wisdom', 'constitution', 'charisma', 'dexterity']
                stat_name = random.choice(stat_list)
                if stat_name == 'strength':
                    target.stats.strength -= 1
                if stat_name == 'intelligence':
                    target.stats.intel -= 1
                if stat_name == 'wisdom':
                    target.stats.wisdom -= 1
                if stat_name == 'constitution':
                    target.stats.con -= 1
                if stat_name == 'charisma':
                    target.stats.charisma -= 1
                if stat_name == 'dexterity':
                    target.stats.dex -= 1
                special_str += (f"The attack is devastating, causing {target.name} to lose 1 {stat_name}.\n")
        return special_str


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player_char to stone
    """

    def __init__(self):
        super().__init__(name="Gaze", damage=0, crit=0, description="", off=False)
        self.special = True
        self.att_name = 'leers'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = f"{wielder.name} {self.name} at {target.name}.\n"
        special_str += abilities.Petrify().cast(wielder, target=target, special=True)
        return special_str


class DragonClaw(NaturalWeapon):
    """
    ignores armor
    """

    def __init__(self):
        super().__init__(name="Dragon Claw", damage=14, crit=0.2, description="", off=True)
        self.ignore = True
        self.att_name = 'rakes'


class DragonClaw2(DragonClaw):

    def __init__(self):
        super().__init__()
        self.damage = 35
        self.crit = 0.33
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.stats.strength // 2) * crit, wielder.stats.strength * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Bleed'].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = int(max(wielder.stats.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'] = StatusEffect(True,
                                                              max(duration, target.status_effects['Bleed'].duration),
                                                              max(bleed_dmg, target.status_effects['Bleed'].extra))
        return special_str


class DragonTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Dragon Tail", damage=20, crit=0.15, description="", off=True)
        self.att_name = 'swipes'


class DragonTail2(DragonTail):

    def __init__(self):
        super().__init__()
        self.damage = 45
        self.crit = 0.3
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.status_effects['Stun'].active:
            resist = target.check_mod('resist', enemy=wielder, typ='Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - resist) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        duration = max(1, wielder.stats.strength // 10)
                        target.status_effects['Stun'] = StatusEffect(True, duration)
                        special_str += f"{target.name} is stunned.\n"
        return special_str


class NightmareHoof(NaturalWeapon):
    """
    Natural weapon of Nightmare; additional fire damage
    """

    def __init__(self):
        super().__init__(name="Nightmare Hoof", damage=13, crit=0.25, description="", off=True)
        self.special = True
        self.att_name = 'attacks'
        self.element = "Fire"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ=self.element)
        damage = int(random.randint(wielder.stats.intel // 2, wielder.stats.intel) * (1 - resist))
        target.health.current -= damage
        if damage > 0:
            special_str += f"The fire from {wielder.name}'s attack burns {target.name} for {damage} damage.\n"
        elif damage < 0:
            special_str += f"{target.name} absorbs the fire damage and is healed for {abs(damage)} hit points.\n"
        else:
            special_str += "The fire is ineffective, dealing no damage.\n"
        return special_str


class ElementalBlade(NaturalWeapon):
    """
    Innate weapon possessed by Myrmidons; does elemental damage based on the enemy type
    """

    def __init__(self):
        super().__init__(name="Elemental Blade", damage=15, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        elemental_type = max(wielder.resistance, key=wielder.resistance.get)
        resist = target.check_mod('resist', enemy=wielder, typ=elemental_type)
        damage = int(damage * (1 - resist))
        if damage < 0:
            special_str += f"{target.name} absorbs the {elemental_type.lower()} damage, gaining {abs(damage)} hit points.\n"
        elif damage > 0:
            special_str += f"{wielder.name}'s blade deals {damage} additional {elemental_type.lower()} damage to {target.name}.\n"
        else:
            special_str += f"{elemental_type} damage was not effective against {target.name}.\n"
        target.health.current -= damage
        if damage > 0 and elemental_type == "Fire" and target.is_alive():
            if not target.status_effects['DOT'].active:
                special_str += f"{target.name} is on fire.\n"
            target.status_effects['DOT'] = StatusEffect(True, 3, 
                                                        max(int(damage // 2), target.status_effects['DOT'].extra))
        return special_str


class Tentacle(NaturalWeapon):
    """
    Chance to trip and leave prone
    """

    def __init__(self):
        super().__init__(name="Tentacle", damage=12, crit=0.2, description="A slender, flexible limb or appendage in an "
                                                                          "animal, especially around the mouth of an "
                                                                          "invertebrate, used for grasping or moving "
                                                                          "about, or bearing sense organs.",
                         off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        special_str += abilities.Trip().use(wielder, target, special=True)
        return special_str


class Tentacle2(Tentacle):
    """
    Chance to stun
    """

    def __init__(self):
        super().__init__()
        self.damage = 24
        self.crit = 0.3
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.status_effects['Stun'].active:
            resist = target.check_mod('resist', enemy=wielder, typ='Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - resist) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        duration = max(1, wielder.stats.strength // 10)
                        target.status_effects['Stun'] = StatusEffect(True, duration)
                        special_str += f"{target.name} is stunned.\n"
        return special_str


class InvisibleBlade(NaturalWeapon):
    """
    Shadow element
    Only stuns on crit
    """

    def __init__(self):
        super().__init__(name="Invisible Blade", damage=9, crit=0.25, description="", off=True)
        self.special = True
        self.element = "Shadow"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.status_effects['Stun'].active:
            resist = target.check_mod('resist', enemy=wielder, typ='Physical')
            if resist < 1:
                if crit > 1:
                    if random.randint(0, wielder.stats.dex // 2) * (1 - resist) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        duration = 1
                        target.status_effects['Stun'] = StatusEffect(True, duration)
                        special_str += f"{target.name} is stunned.\n"
        return special_str


class CerberusClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name='claws', damage=20, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.stats.strength // 2) * crit, wielder.stats.strength * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Bleed'].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = int(max(wielder.stats.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.status_effects['Bleed'] = StatusEffect(True,
                                                              max(duration, target.status_effects['Bleed'].duration),
                                                              max(bleed_dmg, target.status_effects['Bleed'].extra))
        return special_str


class CerberusBite(NaturalWeapon):

    def __init__(self):
        super().__init__(name="bites", damage=30, crit=0.25, description="", off=False)
        self.special = True
        self.element = "Fire"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ=self.element)
        damage = int(random.randint(damage // 2, damage) * (1 - resist))
        target.health.current -= damage
        if damage > 0:
            special_str += f"The fire from {wielder.name}'s bite burns {target.name} for {damage} damage.\n"
        elif damage < 0:
            special_str += f"{target.name} absorbs the fire damage and is healed for {abs(damage)} hit points.\n"
        else:
            special_str += f"The fire is ineffective, dealing {damage} damage.\n"
        return special_str


class LichHand(NaturalWeapon):
    """
    Chance to paralyze (stun) enemy
    """

    def __init__(self):
        super().__init__(name="touches", damage=1, crit=0.2, description="", off=True)
        self.special = True
        self.element = "Ice"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.status_effects['Stun'].active:
            if crit > 1:
                if random.randint(wielder.stats.intel // 4, wielder.stats.intel) \
                        > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                    duration = max(1, wielder.stats.intel // 10)
                    target.status_effects['Stun'] = StatusEffect(True, duration)
                    special_str += f"{target.name} is stunned.\n"
        return special_str


class Cannon(NaturalWeapon):
    """
    Chance to stun the target
    """

    def __init__(self):
        super().__init__(name="attacks", damage=40, crit=0.15, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.status_effects['Stun'].active:
            if crit > 1:
                if random.randint(wielder.stats.strength // 4, wielder.stats.strength) \
                        > random.randint(target.stats.con // 2, target.stats.con):
                    duration = max(1, wielder.stats.strength // 10)
                    target.status_effects['Stun'] = StatusEffect(True, duration)
                    special_str += f"{target.name} is stunned.\n"
        return special_str


class DevilBlade(NaturalWeapon):

    def __init__(self):
        super().__init__(name='attacks', damage=50, crit=0.33, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        w_chance = wielder.check_mod('luck', enemy=target, luck_factor=10)
        t_chance = target.check_mod('luck', enemy=wielder, luck_factor=20)
        if crit > 1:
            if random.randint(0, w_chance) > random.randint(0, t_chance):
                effects = ['Stun', 'Doom', 'Blind', 'Disarm', 'Sleep', 'Poison', 'DOT', 'Bleed', 'Berserk']
                effect = random.choice(effects)
                target.status_effects[effect] = StatusEffect(True,
                                                             max(random.randint(1, 5), target.status_effects[effect].duration))
                if effect in ['Poison', 'DOT', 'Bleed']:
                    if effect == "Poison":
                        damage = int(target.health.max * 0.005)
                    target.status_effects[effect].extra += damage  # damage builds over time
                special_str += f"The attack inflicts {effect.lower()} on {target.name}.\n"
        return special_str


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

    def __init__(self):
        super().__init__()
        self.armor = 9


class SnakeScales(NaturalArmor):

    def __init__(self):
        super().__init__(name="Snake Scales", armor=3, description="")


class SnakeScales2(SnakeScales):

    def __init__(self):
        super().__init__()
        self.armor = 6


class DemonArmor(NaturalArmor):

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
        special_str = ""
        resist = attacker.check_mod('resist', enemy=wearer, typ='Shadow')
        damage = int(random.randint(self.shadow_damage // 2, self.shadow_damage) * (1 - resist))
        attacker.health.current -= damage
        if damage > 0:
            special_str += f"An aura of shadow emanates from {wearer.name}, dealing {damage} damage to {attacker.name}.\n"
        elif damage < 0:
            special_str += (
                f"{attacker.name} absorbs the shadow damage emanating from {wearer.name} and is healed for "
                f"{abs(damage)} hit points.\n")
        else:
            special_str += f"The shadow aura is ineffective, dealing {damage} damage.\n"
        return special_str


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
        special_str = ""
        resist = attacker.check_mod('resist', enemy=wearer, typ='Fire')
        damage = int(random.randint(self.fire_damage // 2, self.fire_damage) * (1 - resist))
        attacker.health.current -= damage
        if damage > 0:
            special_str += f"An aura of fire emanates from {wearer.name}, dealing {damage} damage to {attacker.name}.\n"
        elif damage < 0:
            special_str += (
                f"{attacker.name} absorbs the fire damage emanating from {wearer.name} and is healed for {abs(damage)} "
                f"hit points.\n")
        else:
            special_str += f"The fire is ineffective, dealing {damage} damage.\n"
        return special_str


class DevilSkin(NaturalArmor):
    """
    deals additional non-elemental damage to attacker
    """

    def __init__(self):
        super().__init__(name='Devil Skin', armor=40, description="")
        self.special = True
        self.damage = 100

    def special_effect(self, wearer, attacker):
        special_str = ""
        a_chance = attacker.check_mod('luck', enemy=wearer, luck_factor=10)
        damage = random.randint(self.damage // (1 + a_chance), self.damage)
        attacker.health.current -= damage
        if damage > 0:
            special_str += f"An aura emanates from {wearer.name}, dealing {damage} damage to {attacker.name}.\n"
        else:
            special_str += f"The aura is ineffective, dealing {damage} damage.\n"
        return special_str


class NaturalShield(items.OffHand):

    def __init__(self, name, mod, subtyp):
        super().__init__(name=name, mod=mod, subtyp=subtyp, description="", rarity=0, unequip=False, value=0)
        self.name = name
        self.mod = mod
        self.subtyp = subtyp


class ForceField(NaturalShield):

    def __init__(self):
        super().__init__(name="Force Field", mod=0.1, subtyp="Shield")


class ForceField2(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 0.2


class ForceField3(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 0.3


# Enemies
class Test(Misc):
    """
    Used for testing new implementations
    """

    def __init__(self):
        super().__init__(name="Test", health=1, mana=999, strength=20, intel=0, wisdom=0, con=10, charisma=99, dex=25,
                         exp=5000)
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': abilities.Disarm()}}
        self.level.pro_level = 99  # test for enemies running away


class Mimic(Aberration):
    """
    true sight
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
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook = {"Spells": {},
                          "Skills": {'Lick': abilities.Lick(),
                                     'Gold Toss': abilities.GoldToss(),
                                     'Slot Machine': abilities.SlotMachine()}}
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Poison'] = 1.
        self.level.pro_level = z
        self.sight = True
        self.picture = "mimic.txt"


# Starting enemies
class GreenSlime(Slime):

    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(7, 14), mana=20, strength=6, intel=15, wisdom=15,
                         con=8, charisma=1, dex=4, exp=random.randint(1, 20))
        self.gold = random.randint(1, 8)
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.inventory['Key'] = [items.Key()]
        self.spellbook = {"Spells": {'Enfeeble': abilities.Enfeeble()},
                          "Skills": {'Acid Spit': abilities.AcidSpit()}}
        self.level.pro_level = 0


class GiantRat(Animal):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=3, strength=4, intel=3, wisdom=3, con=6,
                         charisma=6, dex=15, exp=random.randint(7, 14))
        self.equipment = {'Weapon': Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(1, 5)
        self.inventory['Rat Tail'] = [items.RatTail()]
        self.level.pro_level = 0
        self.picture = "giantrat.txt"


class Goblin(Humanoid):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(3, 7), mana=5, strength=7, intel=5, wisdom=2, con=8,
                         charisma=12, dex=8, exp=random.randint(7, 16))
        self.equipment = {'Weapon': items.Rapier(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 20)
        self.spellbook = {"Spells": {},
                          "Skills": {"Goblin Punch": abilities.GoblinPunch(),
                                     "Gold Toss": abilities.GoldToss()}}
        self.level.pro_level = 0
        self.picture = "goblin.txt"


class Goblin2(Goblin):
    """
    Buffed version of a regular goblin; Barghest boss can transform into one
    """

    def __init__(self):
        super().__init__()
        self.stats = Stats(22, 16, 10, 17, 19, 14)
        self.equipment = {'Weapon': items.Talwar(), 'Armor': items.Cuirboulli(), 'OffHand': items.Kris(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Mirror Image"] = abilities.MirrorImage()
        self.spellbook['Skills']["Parry"] = abilities.Parry()


class Bandit(Humanoid):

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=16, strength=8, intel=8, wisdom=5, con=8,
                         charisma=10, dex=10, exp=random.randint(8, 18))
        self.equipment = {'Weapon': items.Dirk(), 'Armor': items.PaddedArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 25)
        self.inventory['Feather'] = [items.Feather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Steal': abilities.Steal(),
                                     'Disarm': abilities.Disarm(),
                                     'Smoke Screen': abilities.SmokeScreen()}}
        self.level.pro_level = 0
        self.picture = "fighter.txt"


class Skeleton(Undead):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=2, strength=8, intel=4, wisdom=8, con=12,
                         charisma=5, dex=6, exp=random.randint(11, 20))
        self.equipment = {'Weapon': items.Rapier(), 'Armor': items.NoArmor(), 'OffHand': items.Buckler(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(1, 5)
        self.inventory['Health Potion'] = [items.HealthPotion()]
        self.resistance['Fire'] = 0.
        self.level.pro_level = 0
        self.picture = "skeleton.txt"


class Scarecrow(Construct):

    def __init__(self):
        super().__init__(name='Scarecrow', health=random.randint(5, 7), mana=10, strength=12, intel=3, wisdom=6, con=10,
                         charisma=8, dex=11, exp=random.randint(13, 21))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(8, 16)
        self.spellbook = {"Spells": {},
                          "Skills": {'Sleeping Powder': abilities.SleepingPowder()}}
        self.resistance['Fire'] = -1.
        self.resistance['Physical'] = 0.
        self.level.pro_level = 0
        self.picture = "scarecrow.txt"


# Level 1
class GiantCentipede(Animal):

    def __init__(self):
        super().__init__(name='Giant Centipede', health=random.randint(8, 13), mana=3, strength=10, intel=4, wisdom=6,
                         con=8, charisma=8, dex=12, exp=random.randint(13, 24))
        self.equipment = {'Weapon': Pincers(), 'Armor': Carapace(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 18)
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 1
        self.picture = "centipede.txt"


class GiantHornet(Animal):

    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=25, strength=6, intel=4, wisdom=6,
                         con=6, charisma=8, dex=18, exp=random.randint(13, 24))
        self.equipment = {'Weapon': Stinger(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(6, 15)
        self.spellbook = {"Spells": {'Berserk': abilities.Berserk()},
                          "Skills": {}}
        self.flying = True
        self.level.pro_level = 1
        self.picture = "hornet.txt"


class ElectricBat(Animal):

    def __init__(self):
        super().__init__(name='Electric Bat', health=random.randint(5, 9), mana=15, strength=6, intel=11, wisdom=7,
                         con=5, charisma=12, dex=22, exp=random.randint(17, 31))
        self.equipment = {'Weapon': Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(8, 21)
        self.spellbook = {"Spells": {'Shock': abilities.Shock(),
                                     'Silence': abilities.Silence()},
                          "Skills": {}}
        self.flying = True
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = -0.25
        self.level.pro_level = 1
        self.picture = "bat.txt"


class Zombie(Undead):

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(11, 14), mana=20, strength=15, intel=1, wisdom=5, con=8,
                         charisma=8, dex=8, exp=random.randint(11, 22))
        self.equipment = {'Weapon': Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 30)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': abilities.PoisonStrike()}}
        self.level.pro_level = 1
        self.picture = "zombie.txt"


class Imp(Fiend):

    def __init__(self):
        super().__init__(name='Imp', health=random.randint(9, 14), mana=25, strength=6, intel=12, wisdom=10,
                         con=8, charisma=12, dex=12, exp=random.randint(15, 24))
        self.equipment = {'Weapon': DemonClaw(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 30)
        self.spellbook = {"Spells": {'Corruption': abilities.Corruption(),
                                     'Silence': abilities.Silence()},
                          "Skills": {}}
        self.level.pro_level = 1
        self.picture = "imp.txt"


class GiantSpider(Animal):

    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=10, strength=9, intel=10, wisdom=10,
                         con=8, charisma=10, dex=12, exp=random.randint(15, 24))
        self.equipment = {'Weapon': Stinger(), 'Armor': Carapace(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 30)
        self.spellbook = {'Spells': {},
                          'Skills': {'Web': abilities.Web()}}
        self.resistance['Poison'] = 0.25
        self.level.pro_level = 1
        self.picture = "spider.txt"


class Quasit(Fiend):
    """
    Can shapeshift between Electric Bat, Giant Centipede, Battle Toad, and natural forms
    """

    def __init__(self):
        super().__init__(name='Quasit', health=random.randint(13, 17), mana=15, strength=8, intel=8, wisdom=10,
                         con=11, charisma=14, dex=16, exp=random.randint(25, 44))
        self.equipment = {'Weapon': DemonClaw(), 'Armor': DemonArmor(), 'OffHand': Claw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(25, 40)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': abilities.PoisonStrike(),
                                     'Shapeshift': abilities.Shapeshift()}}
        self.resistance['Poison'] = 1
        self.transform = [Quasit,
                          ElectricBat,
                          GiantCentipede,
                          BattleToad]
        self.level.pro_level = 1
        self.picture = "quasit.txt"


class Panther(Animal):
    """
    Transform Level 1 creature
    """

    def __init__(self):
        super().__init__(name='Panther', health=random.randint(10, 14), mana=25, strength=10, intel=8, wisdom=8,
                         con=10, charisma=10, dex=13, exp=random.randint(19, 28))
        self.equipment = {'Weapon': Claw(), 'Armor': AnimalHide(), 'OffHand': Claw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 20)
        self.inventory['Leather'] = [items.Leather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': abilities.Backstab(),
                                     'Kidney Punch': abilities.KidneyPunch(),
                                     'Disarm': abilities.Disarm()}}
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 1
        self.picture = "panther.txt"


class TwistedDwarf(Humanoid):

    def __init__(self):
        super().__init__(name='Twisted Dwarf', health=random.randint(15, 19), mana=10, strength=12, intel=8, wisdom=10,
                         con=12, charisma=8, dex=10, exp=random.randint(25, 44))
        self.equipment = {'Weapon': items.Mattock(), 'Armor': items.HideArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 20)
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike()}}
        self.level.pro_level = 1
        self.picture = "dwarf.txt"


class BattleToad(Animal):

    def __init__(self):
        super().__init__(name='Battle Toad', health=random.randint(15, 19), mana=20, strength=10, intel=9, wisdom=10,
                         con=10, charisma=8, dex=15, exp=random.randint(30, 48))
        self.equipment = {'Weapon': items.BrassKnuckles(), 'Armor': items.NoArmor(), 'OffHand': items.BrassKnuckles(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(31, 47)
        self.spellbook = {"Spells": {},
                          "Skills": {'Jump': abilities.Jump()}}
        self.resistance["Water"] = 0.75
        self.level.pro_level = 1
        self.picture = "battletoad.txt"


class Satyr(Fey):

    def __init__(self):
        super().__init__(name='Satyr', health=random.randint(17, 22), mana=25, strength=11, intel=12, wisdom=10, con=11,
                         charisma=12, dex=12, exp=random.randint(28, 44))
        self.equipment = {'Weapon': items.Rapier(), 'Armor': items.LeatherArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(29, 42)
        self.inventory['Leather'] = [items.Leather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Stomp': abilities.Stomp()}}
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
        self.level.pro_level = 1
        self.picture = "satyr.txt"


class Minotaur(Monster):
    """
    Level 1 Boss
    """

    def __init__(self):
        super().__init__(name='Minotaur', health=86, mana=60, strength=18, intel=8, wisdom=10, con=14, charisma=14,
                         dex=12, exp=250)
        self.equipment = {'Weapon': items.DoubleAxe(), 'Armor': items.Cuirboulli(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 200
        self.inventory['Weapon'] = [items.random_item(2)]
        self.inventory['Leather'] = [items.Leather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': abilities.MortalStrike(),
                                     'Charge': abilities.Charge(),
                                     'Disarm': abilities.Disarm(),
                                     'Parry': abilities.Parry()}}
        self.resistance['Death'] = 1
        self.level.pro_level = 1
        self.sight = True
        self.picture = "minotaur.txt"


class Barghest(Fiend):
    """
    Level 1 Extra Boss - guards first of six relics (TRIANGULUS) required to beat the final boss
    Can shapeshift between 3 forms: Direwolf, Goblin, and Hybrid (natural) forms
    """

    def __init__(self):
        super().__init__(name='Barghest', health=145, mana=120, strength=25, intel=15, wisdom=14,
                         con=18, charisma=14, dex=16, exp=500)
        self.gold = 600
        self.equipment = {'Weapon': Claw2(), 'Armor': AnimalHide(), 'OffHand': Claw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.inventory['Old Key'] = [items.OldKey()]
        self.spellbook = {"Spells": {"Enfeeble": abilities.Enfeeble()},
                          "Skills": {'Shapeshift': abilities.Shapeshift(),
                                     'Kidney Punch': abilities.KidneyPunch(),
                                     'Backstab': abilities.Backstab()}}
        self.resistance['Death'] = 1
        self.resistance['Physical'] = 0.25
        self.transform = [Barghest, Goblin2, Direwolf2]
        self.level.pro_level = 2
        self.sight = True
        self.picture = "barghest.txt"


# Level 2
class Gnoll(Humanoid):

    def __init__(self):
        super().__init__(name='Gnoll', health=random.randint(16, 24), mana=20, strength=13, intel=10, wisdom=5, con=8,
                         charisma=12, dex=16, exp=random.randint(45, 85))
        self.equipment = {'Weapon': items.Partisan(), 'Armor': items.PaddedArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 20)
        self.inventory['Feather'] = [items.Feather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': abilities.Disarm()}}
        self.level.pro_level = 2
        self.picture = "gnoll.txt"


class GiantSnake(Animal):

    def __init__(self):
        super().__init__(name='Giant Snake', health=random.randint(18, 26), mana=2, strength=15, intel=5, wisdom=6,
                         con=14, charisma=10, dex=16, exp=random.randint(60, 100))
        self.equipment = {'Weapon': SnakeFang(), 'Armor': SnakeScales(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(35, 75)
        self.inventory['Snake Skin'] = [items.SnakeSkin()]
        self.resistance['Poison'] = 0.25
        self.level.pro_level = 2
        self.picture = "snake.txt"


class Orc(Humanoid):

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(17, 28), mana=14, strength=12, intel=6, wisdom=5, con=10,
                         charisma=8, dex=14, exp=random.randint(45, 80))
        self.equipment = {'Weapon': items.Jian(), 'Armor': items.LeatherArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(20, 65)
        self.inventory['Leather'] = [items.Leather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike()}}
        self.level.pro_level = 2
        self.picture = "orc.txt"


class GiantOwl(Animal):

    def __init__(self):
        super().__init__(name='Giant Owl', health=random.randint(12, 17), mana=12, strength=13, intel=12, wisdom=10,
                         con=10, charisma=1, dex=15, exp=random.randint(45, 80))
        self.equipment = {'Weapon': Claw2(), 'Armor': items.NoArmor(), 'OffHand': Claw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(20, 65)
        self.spellbook = {"Spells": {},
                          "Skills": {'Screech': abilities.Screech()}}
        self.inventory['Feather'] = [items.Feather()]
        self.flying = True
        self.level.pro_level = 2
        self.picture = "giantowl.txt"


class Vampire(Undead):

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(20, 28), mana=30, strength=16, intel=14, wisdom=12,
                         con=15, charisma=14, dex=14, exp=random.randint(50, 90))
        self.equipment = {'Weapon': items.IronshodStaff(), 'Armor': items.NoArmor(), 'OffHand': VampireBite(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 90)
        self.spellbook = {"Spells": {'Silence': abilities.Silence(),
                                     'Lightning': abilities.Lightning()},
                          "Skills": {'Health Drain': abilities.HealthDrain(),
                                     'Shapeshift': abilities.Shapeshift()}}
        self.transform = [Vampire, VampireBat]
        self.level.pro_level = 2
        self.picture = "vampire.txt"


class VampireBat(Animal):

    def __init__(self):
        super().__init__(name='Vampire Bat', health=random.randint(20, 28), mana=30, strength=12, intel=16, wisdom=15,
                         con=10, charisma=14, dex=18, exp=random.randint(50, 90))
        self.equipment = {'Weapon': VampireBite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 90)
        self.spellbook = {"Spells": {},
                          "Skills": {'Health Drain': abilities.HealthDrain(),
                                     'Shapeshift': abilities.Shapeshift()}}
        self.transform = [Vampire, VampireBat]
        self.flying = True
        self.level.pro_level = 2
        self.picture = "bat.txt"


class Direwolf(Animal):

    def __init__(self):
        super().__init__(name='Direwolf', health=random.randint(16, 20), mana=8, strength=17, intel=7, wisdom=6, con=14,
                         charisma=10, dex=16, exp=random.randint(60, 100))
        self.equipment = {'Weapon': Claw2(), 'Armor': AnimalHide(), 'OffHand': Claw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(35, 75)
        self.inventory['Leather'] = [items.Leather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Howl': abilities.Howl(),
                                     'Trip': abilities.Trip()}}
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 2
        self.picture = "direwolf.txt"


class Direwolf2(Direwolf):
    """
    Buffed version of Direwolf; Barghest will transform into
    """

    def __init__(self):
        super().__init__()
        self.stats = Stats(28, 10, 9, 20, 12, 20)
        self.equipment = {'Weapon': Claw2(), 'Armor': AnimalHide2(), 'OffHand': Claw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.spellbook['Skills']['Jump'] = abilities.Jump()


class Wererat(Monster):

    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(14, 17), mana=4, strength=14, intel=6, wisdom=12, con=11,
                         charisma=8, dex=18, exp=random.randint(57, 94))
        self.equipment = {'Weapon': Bite(), 'Armor': AnimalHide(), 'OffHand': Claw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.inventory['Leather'] = [items.Leather()]
        self.level.pro_level = 2
        self.picture = "giantrat.txt"


class RedSlime(Slime):

    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(18, 32), mana=30, strength=10, intel=20, wisdom=20,
                         con=12, charisma=10, dex=5, exp=random.randint(43, 150))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.inventory['Mana Potion'] = [items.ManaPotion()]
        self.spellbook = {'Spells': {'Firebolt': abilities.Firebolt(),
                                     'Enfeeble': abilities.Enfeeble()},
                          'Skills': {}}
        self.level.pro_level = 2


class GiantScorpion(Animal):

    def __init__(self):
        super().__init__(name='Giant Scorpion', health=random.randint(13, 18), mana=2, strength=14, intel=5, wisdom=10,
                         con=12, charisma=10, dex=9, exp=random.randint(65, 105))
        self.equipment = {'Weapon': Stinger(), 'Armor': Carapace(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.resistance['Poison'] = 0.25
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 2
        self.picture = "giantscorpion.txt"


class Warrior(Humanoid):

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(22, 31), mana=25, strength=14, intel=10, wisdom=8,
                         con=12, charisma=10, dex=10, exp=random.randint(65, 110))
        self.equipment = {'Weapon': items.Jian(), 'Armor': items.ChainMail(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(25, 100)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike(),
                                     'Disarm': abilities.Disarm(),
                                     'Parry': abilities.Parry()}}
        self.level.pro_level = 2
        self.picture = "fighter.txt"


class Harpy(Monster):

    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=23, strength=18, intel=13, wisdom=13,
                         con=14, charisma=14, dex=23, exp=random.randint(65, 115))
        self.equipment = {'Weapon': items.Mace(), 'Armor': items.NoArmor(), 'OffHand': Claw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(50, 75)
        self.inventory['Feather'] = [items.Feather()]
        self.flying = True
        self.spellbook = {'Spells': {"Berserk": abilities.Berserk()},
                          'Skills': {'Screech': abilities.Screech()}}
        self.level.pro_level = 2
        self.picture = "harpy.txt"


class Naga(Monster):

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=17, strength=15, intel=13, wisdom=15,
                         con=15, charisma=12, dex=17, exp=random.randint(67, 118))
        self.equipment = {'Weapon': items.Partisan(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(55, 75)
        self.spellbook = {"Spells": {'Silence': abilities.Silence()},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Electric'] = -0.5
        self.resistance['Water'] = 0.75
        self.level.pro_level = 2
        self.picture = "naga.txt"


class Clannfear(Fiend):

    def __init__(self):
        super().__init__(name='Clannfear', health=random.randint(22, 28), mana=40, strength=17, intel=8, wisdom=11,
                         con=14, charisma=12, dex=15, exp=random.randint(77, 130))
        self.equipment = {'Weapon': DemonClaw(), 'Armor': AnimalHide(), 'OffHand': DemonClaw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(65, 92)
        self.spellbook = {'Spells': {},
                          'Skills': {'Trip': abilities.Trip(),
                                     'Charge': abilities.Charge()}}
        self.resistance['Fire'] = 0.75
        self.resistance['Electric'] = -0.5
        self.level.pro_level = 2
        self.picture = "clannfear.txt"


class Xorn(Elemental):
    """
    Earth elemental
    """

    def __init__(self):
        super().__init__(name='Xorn', health=random.randint(27, 33), mana=40, strength=16, intel=11, wisdom=12,
                         con=17, charisma=10, dex=12, exp=random.randint(74, 121))
        self.equipment = {'Weapon': Claw(), 'Armor': items.NoArmor(), 'OffHand': Claw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(61, 99)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {'Spells': {'Tremor': abilities.Tremor()},
                          'Skills': {'ConsumeItem': abilities.ConsumeItem()}}
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.5
        self.resistance['Earth'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Poison'] = 1.
        self.level.pro_level = 2
        self.picture = "xorn.txt"


class SteelPredator(Construct):

    def __init__(self):
        super().__init__(name='Steel Predator', health=random.randint(27, 33), mana=40, strength=17, intel=9,
                         wisdom=12, con=14, charisma=12, dex=19, exp=random.randint(85, 129))
        self.equipment = {'Weapon': Claw2(), 'Armor': MetalPlating(), 'OffHand': Claw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(65, 110)
        self.status_effects['Blind'] = StatusEffect(True, -1)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {'Spells': {'Silence': abilities.Silence()},
                          'Skills': {'Charge': abilities.Charge(),
                                     'Destroy Metal': abilities.DestroyMetal()}}
        self.resistance['Fire'] = 0.5
        self.resistance['Ice'] = 0.5
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.75
        self.resistance['Earth'] = 0.
        self.level.pro_level = 2
        self.picture = "steelpredator.txt"


class Pseudodragon(Dragon):
    """
    Level 2 Boss
    """

    def __init__(self):
        super().__init__(name='Pseudodragon', health=250, mana=100, strength=28, intel=26, wisdom=24, con=20,
                         charisma=20, dex=18, exp=800)
        self.gold = 1500
        self.equipment = {'Weapon': DragonClaw(), 'Armor': DragonScale(), 'OffHand': DragonClaw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.inventory['Item'] = [items.random_item(3)]
        self.inventory['Old Key'] = [items.OldKey()]
        self.spellbook = {'Spells': {'Fireball': abilities.Fireball(),
                                     'Blinding Fog': abilities.BlindingFog(),
                                     'Dispel': abilities.Dispel()},
                          'Skills': {'Gold Toss': abilities.GoldToss()}}
        self.resistance['Death'] = 1.
        self.level.pro_level = 2
        self.sight = True
        self.picture = "pseudodragon.txt"


class Nightmare(Fiend):
    """
    Level 2 Extra Boss - guards second of six relics (QUADRATA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Nightmare', health=410, mana=100, strength=30, intel=17, wisdom=15, con=22, charisma=16,
                         dex=15, exp=2000)
        self.equipment = {'Weapon': NightmareHoof(), 'Armor': AnimalHide2(), 'OffHand': NightmareHoof(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = 2500
        self.inventory['Item'] = [items.random_item(4)]
        self.inventory['Old Key'] = [items.OldKey()]
        self.spellbook = {'Spells': {'Sleep': abilities.Sleep(),
                                     'Firestorm': abilities.Firestorm()},
                          'Skills': {'Stomp': abilities.Stomp(),
                                     'True Strike': abilities.TrueStrike()}}
        self.resistance['Fire'] = 1.
        self.resistance['Ice'] = -0.25
        self.resistance['Death'] = 1.
        self.resistance['Physical'] = 0.5
        self.flying = True
        self.level.pro_level = 3
        self.sight = True
        self.picture = "nightmare.txt"


# Level 3
class Direbear(Animal):
    """
    Transform Level 2 creature
    """

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=30, strength=24, intel=6, wisdom=6,
                         con=24, charisma=12, dex=17, exp=random.randint(210, 310))
        self.equipment = {'Weapon': BearClaw(), 'Armor': AnimalHide(), 'OffHand': BearClaw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.inventory['Leather'] = [items.Leather()]
        self.spellbook = {'Spells': {},
                          'Skills': {'Piercing Strike': abilities.PiercingStrike(),
                                     'Charge': abilities.Charge()}}
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 3
        self.picture = "direbear.txt"


class Ghoul(Undead):

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=50, strength=25, intel=10, wisdom=8, con=24,
                         charisma=11, dex=12, exp=random.randint(210, 290))
        self.equipment = {'Weapon': Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(35, 45)
        self.spellbook = {"Spells": {'Disease Breath': abilities.DiseaseBreath()},
                          "Skills": {}}
        self.level.pro_level = 3
        self.picture = "ghoul.txt"


class PitViper(Animal):

    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=30, strength=17, intel=6, wisdom=8,
                         con=16, charisma=10, dex=18, exp=random.randint(215, 290))
        self.equipment = {'Weapon': SnakeFang2(), 'Armor': SnakeScales(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(50, 85)
        self.inventory['Snake Skin'] = [items.SnakeSkin()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Poison'] = 0.25
        self.level.pro_level = 3
        self.picture = "snake.txt"


class Disciple(Humanoid):

    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=70, strength=16, intel=17, wisdom=15,
                         con=16, charisma=12, dex=16, exp=random.randint(210, 290))
        self.equipment = {'Weapon': items.SerpentStaff(), 'Armor': items.SilverCloak(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(55, 95)
        self.spellbook = {'Spells': {'Firebolt': abilities.Firebolt(),
                                     'Ice Lance': abilities.IceLance(),
                                     'Shock': abilities.Shock(),
                                     'Enfeeble': abilities.Enfeeble(),
                                     'Boost': abilities.Boost()},
                          'Skills': {}}
        self.level.pro_level = 3
        self.picture = "disciple.txt"


class BlackSlime(Slime):
    """
    Stupefy - Enemy Skill learnable by Diviner/Geomancer
    """

    def __init__(self):
        super().__init__(name='Black Slime', health=random.randint(48, 90), mana=80, strength=13, intel=25, wisdom=30,
                         con=15, charisma=12, dex=6, exp=random.randint(185, 360))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(30, 180)
        self.spellbook = {'Spells': {'Shadow Bolt': abilities.ShadowBolt(),
                                     'Corruption': abilities.Corruption(),
                                     'Stupefy': abilities.Stupefy()},
                          'Skills': {}}
        self.level.pro_level = 3


class Ogre(Monster):

    def __init__(self):
        super().__init__(name='Ogre', health=random.randint(40, 50), mana=40, strength=24, intel=18, wisdom=14, con=20,
                         charisma=10, dex=14, exp=random.randint(215, 295))
        self.equipment = {'Weapon': items.Maul(), 'Armor': items.Cuirboulli(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(50, 75)
        self.spellbook = {"Spells": {'Magic Missile': abilities.MagicMissile(),
                                     'Dispel': abilities.Dispel()},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike()}}
        self.level.pro_level = 3
        self.picture = "ogre.txt"


class Alligator(Animal):

    def __init__(self):
        super().__init__(name='Alligator', health=random.randint(60, 75), mana=20, strength=26, intel=8, wisdom=7,
                         con=20, charisma=10, dex=15, exp=random.randint(220, 300))
        self.equipment = {'Weapon': AlligatorTail(), 'Armor': items.NoArmor(), 'OffHand': Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 50)
        self.spellbook = {"Spells": {},
                          "Skills": {"Trip": abilities.Trip()}}
        self.level.pro_level = 3
        self.picture = "alligator.txt"


class Troll(Humanoid):

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=20, strength=24, intel=10, wisdom=8, con=24,
                         charisma=12, dex=15, exp=random.randint(225, 310))
        self.equipment = {'Weapon': items.DoubleAxe(), 'Armor': items.Cuirboulli(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(35, 45)
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': abilities.MortalStrike()}}
        self.level.pro_level = 3
        self.picture = "troll.txt"


class GoldenEagle(Animal):

    def __init__(self):
        super().__init__(name='Golden Eagle', health=random.randint(40, 50), mana=20, strength=19, intel=15, wisdom=15,
                         con=17, charisma=15, dex=25, exp=random.randint(230, 320))
        self.equipment = {'Weapon': Claw2(), 'Armor': items.NoArmor(), 'OffHand': Claw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(50, 75)
        self.inventory['Feather'] = [items.Feather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Screech': abilities.Screech()}}
        self.flying = True
        self.level.pro_level = 3
        self.picture = "goldeneagle.txt"


class EvilCrusader(Humanoid):

    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=50, strength=21, intel=18, wisdom=17,
                         con=26, charisma=14, dex=14, exp=random.randint(240, 325))
        self.equipment = {'Weapon': items.Pernach(), 'Armor': items.Splint(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(65, 90)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {"Spells": {'Smite': abilities.Smite(),
                                     'Bless': abilities.Bless()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     'Shield Block': abilities.ShieldBlock(),
                                     "Goad": abilities.Goad()}}
        self.resistance['Shadow'] = 0.5
        self.resistance['Holy'] = -0.5
        self.level.pro_level = 3
        self.picture = "skeleton.txt"


class Werewolf(Monster):
    """
    Transform Level 3 creature
    """

    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(55, 75), mana=85, strength=24, intel=10, wisdom=10,
                         con=20, charisma=14, dex=20, exp=random.randint(220, 300))
        self.equipment = {'Weapon': Claw3(), 'Armor': AnimalHide(), 'OffHand': Claw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(45, 55)
        self.inventory['Leather'] = [items.Leather()]
        self.spellbook = {"Spells": {},
                          "Skills": {'True Strike': abilities.TrueStrike(),
                                     'Howl': abilities.Howl()}}
        self.resistance['Physical'] = 0.1
        self.level.pro_level = 3
        self.picture = "werewolf.txt"


class Antlion(Animal):
    """
    modeled after the boss from FF2 (FFIV)
    """

    def __init__(self):
        super().__init__(name="Antlion", health=random.randint(52, 70), mana=70, strength=22, intel=8, wisdom=12,
                         con=18, charisma=12, dex=18, exp=random.randint(210, 310))
        self.equipment = {'Weapon': Pincers2(), 'Armor': Carapace(), 'OffHand': Pincers2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 52)
        self.spellbook = {"Spells": {},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 3
        self.picture = "antlion.txt"


class InvisibleStalker(Elemental):
    """
    Invisible
    """

    def __init__(self):
        super().__init__(name="Invisible Stalker", health=random.randint(25, 46), mana=60, strength=19, intel=13,
                         wisdom=16, con=14, charisma=18, dex=29, exp=random.randint(230, 330))
        self.equipment = {'Weapon': InvisibleBlade(), 'Armor': items.NoArmor(), 'OffHand': InvisibleBlade(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(65, 79)
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': abilities.Backstab(),
                                     "Kidney Punch": abilities.KidneyPunch(),
                                     'Poison Strike': abilities.PoisonStrike(),
                                     'Smoke Screen': abilities.SmokeScreen(),
                                     "Parry": abilities.Parry()}}
        self.resistance['Poison'] = 1.
        self.invisible = True
        self.sight = True
        self.level.pro_level = 3
        self.picture = "assassin.txt"


class NightHag(Fey):

    def __init__(self):
        super().__init__(name="Night Hag", health=random.randint(30, 48), mana=105, strength=16, intel=22, wisdom=26,
                         con=12, charisma=14, dex=19, exp=random.randint(215, 312))
        self.equipment = {'Weapon': items.Kris(), 'Armor': items.SilverCloak(), 'OffHand': items.Grimoire(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(70, 99)
        self.spellbook = {"Spells": {'Sleep': abilities.Sleep(),
                                     'Enfeeble': abilities.Enfeeble(),
                                     'Magic Missile': abilities.MagicMissile()},
                          "Skills": {'Nightmare Fuel': abilities.NightmareFuel()}}
        self.resistance['Fire'] = 0.25
        self.resistance['Cold'] = 0.25
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 3
        self.picture = "nighthag.txt"


class NightHag2(NightHag):

    def __init__(self):
        super().__init__()
        self.name = "Waitress"
        self.health = Resource(500, 500)
        self.mana = Resource(300, 300)
        self.stats = Stats(18, 24, 30, 15, 15, 20)
        self.experience = 2500
        self.gold = 1000
        self.inventory['Ornate Key'] = [items.OrnateKey()]
        self.spellbook['Skills']["Widow's Wail"] = [abilities.WidowsWail()]
        self.resistance['Stone'] = 1.


class Treant(Fey):

    def __init__(self):
        super().__init__(name="Treant", health=random.randint(52, 78), mana=65, strength=26, intel=16, wisdom=21,
                         con=20, charisma=12, dex=16, exp=random.randint(235, 320))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(60, 85)
        self.inventory['Cursed Hops'] = [items.CursedHops()]
        self.spellbook = {"Spells": {'Regen': abilities.Regen()},
                          "Skills": {'Multi-Attack': abilities.DoubleStrike(),
                                     'Throw Rock': abilities.ThrowRock()}}
        self.resistance['Fire'] = -1.
        self.resistance['Water'] = 1.5
        self.resistance['Poison'] = 1.
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 3
        self.picture = "treant.txt"


class Ankheg(Monster):

    def __init__(self):
        super().__init__(name="Ankheg", health=random.randint(45, 69), mana=65, strength=23, intel=17, wisdom=14,
                         con=19, charisma=6, dex=14, exp=random.randint(240, 330))
        self.equipment = {'Weapon': Claw3(), 'Armor': Carapace(), 'OffHand': Pincers2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(55, 78)
        self.spellbook = {"Spells": {},
                          "Skills": {'Trip': abilities.Trip(),
                                     'Acid Spit': abilities.AcidSpit()}}
        self.resistance['Holy'] = -0.25
        self.resistance['Poison'] = 1.
        self.resistance['Physical'] = 0.1
        self.level.pro_level = 3
        self.picture = "ankheg.txt"


class Cockatrice(Monster):
    """
    Level 3 Boss
    """

    def __init__(self):
        super().__init__(name='Cockatrice', health=580, mana=99, strength=30, intel=16, wisdom=15, con=16, charisma=16,
                         dex=22, exp=3500)
        self.equipment = {'Weapon': Claw3(), 'Armor': items.NoArmor(), 'OffHand': DragonTail(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = 5000
        self.inventory['Pendant'] = [items.random_item(4)]
        self.inventory['Old Key'] = [items.OldKey()]
        self.inventory['Feather'] = [items.Feather()]
        self.spellbook = {"Spells": {'Petrify': abilities.Petrify()},
                          "Skills": {'Screech': abilities.Screech(),
                                     'Double Strike': abilities.DoubleStrike()}}
        self.flying = True
        self.resistance['Death'] = 1
        self.resistance['Stone'] = 0.5
        self.level.pro_level = 3
        self.sight = True
        self.picture = "cockatrice.txt"


class Wendigo(Fey):
    """
    Level 3 Special Boss - guards third of six relics (HEXAGONUM) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Wendigo', health=750, mana=130, strength=32, intel=16, wisdom=19, con=21, charisma=14,
                         dex=22, exp=6000)
        self.equipment = {'Weapon': Bite2(), 'Armor': items.NoArmor(), 'OffHand': DemonClaw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = 7500
        self.inventory['Item'] = [items.random_item(5)]
        self.inventory['Old Key'] = [items.OldKey()]
        self.spellbook = {"Spells": {'Regen': abilities.Regen2(),
                                     'Terrify': abilities.Terrify(),
                                     "Berserk": abilities.Berserk()},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.flying = True
        self.resistance['Fire'] = -0.75
        self.resistance['Ice'] = 1
        self.resistance['Death'] = 1
        self.resistance['Poison'] = 1
        self.level.pro_level = 4
        self.sight = True
        self.picture = "wendigo.txt"


# Level 4
class BrownSlime(Slime):

    def __init__(self):
        super().__init__(name='Brown Slime', health=random.randint(70, 112), mana=85, strength=17, intel=35, wisdom=40,
                         con=15, charisma=10, dex=8, exp=random.randint(390, 660))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(150, 280)
        self.spellbook = {'Spells': {'Mudslide': abilities.Mudslide(),
                                     'Enfeeble': abilities.Enfeeble()},
                          'Skills': {}}
        self.level.pro_level = 4


class Gargoyle(Elemental):

    def __init__(self):
        super().__init__(name='Gargoyle', health=random.randint(55, 75), mana=20, strength=26, intel=10, wisdom=12,
                         con=18, charisma=15, dex=21, exp=random.randint(410, 530))
        self.equipment = {'Weapon': Claw3(), 'Armor': StoneArmor(), 'OffHand': Claw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(75, 125)
        self.spellbook = {"Spells": {'Blinding Fog': abilities.BlindingFog()},
                          "Skills": {"Piercing Strike": abilities.PiercingStrike()}}
        self.flying = True
        self.resistance['Stone'] = 1
        self.resistance['Poison'] = 1
        self.level.pro_level = 4
        self.picture = "gargoyle.txt"


class Conjurer(Humanoid):

    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(40, 65), mana=150, strength=14, intel=22, wisdom=18,
                         con=14, charisma=12, dex=13, exp=random.randint(415, 540))
        self.equipment = {'Weapon': items.RuneStaff(), 'Armor': items.GoldCloak(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.spellbook = {"Spells": {'Fireball': abilities.Fireball(),
                                     'Icicle': abilities.Icicle(),
                                     'Lightning': abilities.Lightning(),
                                     'Aqualung': abilities.Aqualung(),
                                     'Boost': abilities.Boost()},
                          "Skills": {'Mana Drain': abilities.ManaDrain()}}
        self.level.pro_level = 4
        self.picture = "disciple.txt"


class Chimera(Monster):

    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(60, 95), mana=140, strength=26, intel=14, wisdom=16,
                         con=20, charisma=14, dex=14, exp=random.randint(430, 580))
        self.equipment = {'Weapon': LionPaw(), 'Armor': AnimalHide2(), 'OffHand': LionPaw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(100, 250)
        self.spellbook = {"Spells": {'Molten Rock': abilities.MoltenRock(),
                                     'Dispel': abilities.Dispel()},
                          "Skills": {"True Strike": abilities.TrueStrike()}}
        self.resistance['Physical'] = 0.5
        self.level.pro_level = 4
        self.picture = "chimera.txt"


class Dragonkin(Dragon):

    def __init__(self):
        super().__init__(name='Dragonkin', health=random.randint(80, 115), mana=90, strength=26, intel=10, wisdom=18,
                         con=20, charisma=18, dex=19, exp=random.randint(450, 680))
        self.equipment = {'Weapon': items.Halberd(), 'Armor': items.Breastplate(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(150, 300)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {"Spells": {},
                          "Skills": {'Disarm': abilities.Disarm(),
                                     'Charge': abilities.Charge(),
                                     "Goad": abilities.Goad()}}
        self.flying = True
        self.level.pro_level = 4
        self.picture = "dragonkin.txt"


class Griffin(Monster):

    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(75, 105), mana=110, strength=26, intel=21, wisdom=18,
                         con=18, charisma=16, dex=18, exp=random.randint(440, 650))
        self.equipment = {'Weapon': LionPaw(), 'Armor': AnimalHide2(), 'OffHand': Claw3(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(140, 280)
        self.spellbook = {"Spells": {'Hurricane': abilities.Hurricane()},
                          "Skills": {'Screech': abilities.Screech()}}
        self.flying = True
        self.resistance['Physical'] = 0.5
        self.level.pro_level = 4
        self.picture = "griffin.txt"


class DrowAssassin(Humanoid):
    """
    true sight
    """

    def __init__(self):
        super().__init__(name='Drow Assassin', health=random.randint(65, 85), mana=75, strength=22, intel=16, wisdom=15,
                         con=14, charisma=22, dex=28, exp=random.randint(480, 680))
        self.equipment = {'Weapon': items.Rondel(), 'Armor': items.StuddedLeather(), 'OffHand': items.Rondel(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(160, 250)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': abilities.PoisonStrike(),
                                     'Backstab': abilities.Backstab(),
                                     'Kidney Punch': abilities.KidneyPunch(),
                                     'Mug': abilities.Mug(),
                                     'Parry': abilities.Parry(),
                                     'Smoke Screen': abilities.SmokeScreen()}}
        self.level.pro_level = 4
        self.sight = True
        self.picture = "assassin.txt"


class Cyborg(Construct):
    """
    Electric spells heal Cyborg
    """

    def __init__(self):
        super().__init__(name='Cyborg', health=random.randint(90, 120), mana=80, strength=28, intel=13, wisdom=10,
                         con=18, charisma=10, dex=14, exp=random.randint(490, 700))
        self.equipment = {'Weapon': Laser(), 'Armor': MetalPlating(), 'OffHand': ForceField(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(200, 300)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {"Spells": {'Shock': abilities.Shock()},
                          "Skills": {}}
        self.resistance['Electric'] = 1.25
        self.resistance['Water'] = -0.75
        self.level.pro_level = 4
        self.picture = "cyborg.txt"

    def special_effects(self, target):
        special_str = ""
        if self.health.current < int(self.health.current * 0.25):
            special_str += abilities.Detonate.use(self, target=target)
        return special_str


class DarkKnight(Fiend):

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(85, 110), mana=60, strength=28, intel=15, wisdom=12,
                         con=21, charisma=14, dex=17, exp=random.randint(500, 750))
        self.equipment = {'Weapon': items.Flamberge(), 'Armor': items.PlateMail(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(300, 420)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {"Spells": {'Enhance Blade': abilities.EnhanceBlade()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     'Disarm': abilities.Disarm(),
                                     'Shield Block': abilities.ShieldBlock()}}
        self.level.pro_level = 4
        self.picture = "darkknight.txt"


class Myrmidon(Elemental):

    def __init__(self):
        super().__init__(name='Myrmidon', health=random.randint(75, 125), mana=75, strength=26, intel=18, wisdom=16,
                         con=18, charisma=10, dex=14, exp=random.randint(520, 800))
        self.equipment = {'Weapon': ElementalBlade(), 'Armor': items.PlateMail(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(300, 450)
        self.inventory['Elemental Mote'] = [items.ElementalMote()]
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.resistance['Poison'] = 1
        self.level.pro_level = 4
        self.picture = "myrmidon.txt"


class FireMyrmidon(Myrmidon):
    """
    Fire elemental; gains fire DOT applied to elemental blade
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Scorch': abilities.Scorch()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam()}}
        self.resistance['Fire'] = 1.5
        self.resistance['Ice'] = -0.5


class IceMyrmidon(Myrmidon):
    """
    Ice elemental; gains Mortal Strike
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Ice Lance': abilities.IceLance()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     'True Strike': abilities.TrueStrike()}}
        self.resistance['Fire'] = -0.5
        self.resistance['Ice'] = 1.5


class ElectricMyrmidon(Myrmidon):
    """
    Electric elemental; gains Piercing Strike
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Shock': abilities.Shock()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     'Piercing Strike': abilities.PiercingStrike()}}
        self.resistance['Electric'] = 1.5
        self.resistance['Water'] = -0.5


class WaterMyrmidon(Myrmidon):
    """
    Water elemental; gains Parry
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Water Jet': abilities.WaterJet()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     'Parry': abilities.Parry()}}
        self.resistance['Electric'] = -0.5
        self.resistance['Water'] = 1.5


class EarthMyrmidon(Myrmidon):
    """
    Earth elemental; gains Shield Block
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Tremor': abilities.Tremor()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     'Shield Block': abilities.ShieldBlock(),
                                     "Goad": abilities.Goad()}}
        self.resistance['Earth'] = 1.5
        self.resistance['Wind'] = -0.5


class WindMyrmidon(Myrmidon):
    """
    Wind elemental; gains Double Strike
    """

    def __init__(self):
        super().__init__()
        self.spellbook = {"Spells": {'Gust': abilities.Gust()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Earth'] = -0.5
        self.resistance['Wind'] = 1.5


class DisplacerBeast(Fey):

    def __init__(self):
        super().__init__(name='Displacer Beast', health=random.randint(80, 115), mana=100, strength=24, intel=11,
                         wisdom=14, con=24, charisma=14, dex=26, exp=random.randint(500, 775))
        self.equipment = {'Weapon': Claw3(), 'Armor': AnimalHide2(), 'OffHand': Tentacle(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(250, 360)
        self.spellbook = {"Spells": {},
                          "Skills": {'Double Strike': abilities.DoubleStrike(),
                                     'Smoke Screen': abilities.SmokeScreen()}}
        self.invisible = True
        self.level.pro_level = 4
        self.picture = "displacerbeast.txt"


class Golem(Construct):
    """
    Guardians of chests on Level 5
    """

    def __init__(self):
        super().__init__(name='Golem', health=1200, mana=100, strength=32, intel=25, wisdom=30, con=35, charisma=21,
                         dex=20, exp=8000)
        self.equipment = {'Weapon': Laser(), 'Armor': StoneArmor2(), 'OffHand': Laser(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = 12000
        self.inventory['Power Core'] = [items.PowerCore()]
        self.spellbook = {"Spells": {'Enfeeble': abilities.Enfeeble()},
                          "Skills": {'Crush': abilities.Crush(),
                                     "Goad": abilities.Goad()}}
        self.resistance['Fire'] = 0.25
        self.resistance['Ice'] = -0.25
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.25
        self.resistance['Earth'] = 0.5
        self.level.pro_level = 5
        self.sight = True
        self.picture = "golem.txt"


class IronGolem(Golem):
    """
    Level 4 Boss
    """

    def __init__(self):
        super().__init__()
        self.name = "Iron Golem"
        self.health = Resource(1250, 1250)
        self.mana = Resource(250, 250)
        self.stats = Stats(35, 25, 35, 40, 21, 20)
        self.experience = 12000
        self.equipment = {'Weapon': Laser2(), 'Armor': StoneArmor2(), 'OffHand': ForceField2(), 'Ring': items.BarrierRing(),
                          'Pendant': items.NoPendant()}
        self.inventory['Aard of Being'] = [items.AardBeing()]
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook["Skills"]["Triple Strike"] = abilities.TripleStrike()


    def special_effects(self, target):
        special_str = ""
        if not self.incapacitated():
            if self.health.current < int(self.health.max * 0.25) and not self.turtle:
                self.turtle = True
            if self.health.current > int(self.health.max * 0.75) and self.turtle:
                self.turtle = False
            if self.turtle:
                heal = int(self.health.max * 0.25)
                if heal + self.health.current > self.health.max:
                    heal = self.health.max - self.health.current
                self.health.current += heal
                special_str += f"{self.name} heals for {heal}.\n"
        return special_str


class Jester(Humanoid):
    """
    Level 4 Special Boss - guards fourth of six relics (LUNA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name="Jester", health=random.randint(500, 1500), mana=random.randint(125, 300),
                         strength=random.randint(10, 50), intel=random.randint(10, 50), wisdom=random.randint(10, 50),
                         con=random.randint(10, 60), charisma=99, dex=random.randint(10, 50),
                         exp=random.randint(15000, 25000))
        self.gold = random.randint(5000, 100000)
        self.equipment = {'Weapon': items.Kukri(), 'Armor': items.StuddedCuirboulli(), 'OffHand': items.Kukri(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.inventory['Item'] = [items.random_item(6)]
        self.inventory['Joker'] = [items.Joker()]
        self.spellbook = {"Spells": {'Silence': abilities.Silence()},
                          "Skills": {'Gold Toss': abilities.GoldToss(),
                                     'Slot Machine': abilities.SlotMachine(),
                                     'Blackjack': abilities.Blackjack()}}
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
        self.level.pro_level = 5
        self.sight = True
        self.picture = "jester.txt"

    def special_effects(self, target):
        special_str = ""
        special_str += "Jester: The wheel of time stops for no one! HAHA!\n"
        special_str += "The Jester's stats and resistances have been randomized.\n"
        self.stats = Stats(random.randint(10, 50),
                              random.randint(10, 50),
                              random.randint(10, 50),
                              random.randint(10, 60),
                              self.stats.charisma,
                              random.randint(10, 50))
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
        return special_str


# Level 5
class ShadowSerpent(Elemental):

    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=100, strength=28, intel=18,
                         wisdom=15, con=22, charisma=16, dex=23, exp=random.randint(780, 1090))
        self.equipment = {'Weapon': SnakeFang2(), 'Armor': SnakeScales2(), 'OffHand': SnakeFang2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(280, 485)
        self.inventory['Megalixir'] = [items.Megalixir()]
        self.spellbook = {"Spells": {'Corruption': abilities.Corruption()},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Shadow'] = 0.9
        self.resistance['Holy'] = -0.75
        self.resistance['Poison'] = 0.25
        self.invisible = True
        self.level.pro_level = 5
        self.picture = "snake.txt"


class Aboleth(Slime):

    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(210, 500), mana=120, strength=25, intel=50, wisdom=50,
                         con=25, charisma=12, dex=10, exp=random.randint(650, 1230))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(130, 750)
        self.spellbook = {"Spells": {'Disease Breath': abilities.DiseaseBreath(),
                                     'Enfeeble': abilities.Enfeeble(),
                                     'Boost': abilities.Boost()},
                          "Skills": {'Acid Spit': abilities.AcidSpit()}}
        self.resistance['Poison'] = 1.5
        self.level.pro_level = 5


class Beholder(Aberration):

    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=100, strength=25, intel=40, wisdom=35,
                         con=28, charisma=20, dex=20, exp=random.randint(800, 1200))
        self.equipment = {'Weapon': Gaze(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(300, 500)
        self.spellbook = {"Spells": {'Magic Missile': abilities.MagicMissile2(),
                                     'Terrify': abilities.Terrify(),
                                     'Dispel': abilities.Dispel(),
                                     'Disintegrate': abilities.Disintegrate()},
                          "Skills": {'Mana Drain': abilities.ManaDrain()}}
        self.flying = True
        self.resistance['Death'] = 1
        self.level.pro_level = 5
        self.picture = "beholder.txt"


class Behemoth(Aberration):

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=100, strength=38, intel=25, wisdom=20,
                         con=30, charisma=18, dex=25, exp=random.randint(920, 1250))
        self.equipment = {'Weapon': LionPaw(), 'Armor': AnimalHide2(), 'OffHand': LionPaw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(400, 550)
        self.spellbook = {"Spells": {'Holy': abilities.Holy3(),
                                     'Regen': abilities.Regen3(),
                                     "Berserk": abilities.Berserk()},
                          "Skills": {'True Strike': abilities.TrueStrike(),
                                     'Counterspell': abilities.Counterspell()}}
        self.resistance['Fire'] = 1.
        self.resistance['Electric'] = 0.75
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Holy'] = 0.75
        self.resistance['Poison'] = 0.75
        self.resistance['Physical'] = 0.5
        self.level.pro_level = 5
        self.picture = "behemoth.txt"

    def special_effects(self, target):
        special_str = ""
        if not self.is_alive():
            special_str += abilities.FinalAttack.use(self, target=target)
        return special_str


class Lich(Undead):

    def __init__(self):
        super().__init__(name='Lich', health=random.randint(210, 300), mana=120, strength=25, intel=35, wisdom=40,
                         con=20, charisma=36, dex=22, exp=random.randint(880, 1220))
        self.equipment = {'Weapon': LichHand(), 'Armor': items.WizardRobe(), 'OffHand': items.Necronomicon(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(400, 530)
        self.inventory["Phylactery"] = [items.Phylactery()]
        self.spellbook = {"Spells": {'Ice Blizzard': abilities.IceBlizzard(),
                                     'Desoul': abilities.Desoul(),
                                     'Terrify': abilities.Terrify(),
                                     'Disintegrate': abilities.Disintegrate(),
                                     'Boost': abilities.Boost()},
                          "Skills": {'Health/Mana Drain': abilities.HealthManaDrain()}}
        self.resistance['Ice'] = 0.9
        self.level.pro_level = 5
        self.picture = "lich.txt"


class Basilisk(Monster):

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(220, 325), mana=120, strength=29, intel=26, wisdom=30,
                         con=27, charisma=17, dex=20, exp=random.randint(930, 1200))
        self.equipment = {'Weapon': SnakeFang2(), 'Armor': SnakeScales2(), 'OffHand': SnakeFang2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(380, 520)
        self.spellbook = {"Spells": {'Petrify': abilities.Petrify(),
                                     'Poison Breath': abilities.PoisonBreath()},
                          "Skills": {'Mortal Strike': abilities.MortalStrike2()}}
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 0.5
        self.resistance['Poison'] = 0.75
        self.level.pro_level = 5
        self.picture = "snake.txt"


class MindFlayer(Aberration):
    """
    true sight
    """

    def __init__(self):
        super().__init__(name='Mind Flayer', health=random.randint(190, 285), mana=150, strength=28, intel=40,
                         wisdom=35, con=25, charisma=22, dex=18, exp=random.randint(890, 1150))
        self.equipment = {'Weapon': items.MithrilshodStaff(), 'Armor': items.WizardRobe(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(450, 600)
        self.spellbook = {"Spells": {'Doom': abilities.Doom(),
                                     'Terrify': abilities.Terrify(),
                                     'Corruption': abilities.Corruption()},
                          "Skills": {'Mana Drain': abilities.ManaDrain()}}
        self.resistance['Shadow'] = 0.5
        self.resistance['Death'] = 1
        self.resistance['Holy'] = -0.25
        self.level.pro_level = 5
        self.sight = True
        self.picture = "mindflayer.txt"


class Sandworm(Monster):

    def __init__(self):
        super().__init__(name='Sandworm', health=random.randint(230, 300), mana=190, strength=34, intel=21, wisdom=22,
                         con=30, charisma=20, dex=18, exp=random.randint(910, 1200))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(380, 490)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {"Spells": {'Earthquake': abilities.Earthquake(),
                                     'Sandstorm': abilities.Sandstorm()},
                          "Skills": {'Consume Item': abilities.ConsumeItem()}}
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.25
        self.resistance['Earth'] = 1
        self.resistance['Stone'] = 1
        self.resistance['Poison'] = 1
        self.resistance['Physical'] = 0.5
        self.level.pro_level = 5
        self.picture = "naga.txt"


class Warforged(Construct):

    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=120, strength=40, intel=20, wisdom=16,
                         con=33, charisma=12, dex=10, exp=random.randint(880, 1180))
        self.equipment = {'Weapon': Cannon(), 'Armor': StoneArmor2(), 'OffHand': ForceField3(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(380, 490)
        self.inventory['Scrap Metal'] = [items.ScrapMetal()]
        self.spellbook = {"Spells": {'Silence': abilities.Silence()},
                          "Skills": {'Turtle': abilities.Turtle(),
                                     "Crush": abilities.Crush()}}
        self.level.pro_level = 5
        self.picture = "golem.txt"

    def special_effects(self, target):
        special_str = ""
        if not self.incapacitated():
            if self.health.current < int(self.health.max * 0.25) and not self.turtle:
                self.turtle = True
            if self.health.current > int(self.health.max * 0.75) and self.turtle:
                self.turtle = False
            if self.turtle:
                heal = int(self.health.max * 0.25)
                if heal + self.health.current > self.health.max:
                    heal = self.health.max - self.health.current
                self.health.current += heal
                special_str += f"{self.name} heals for {heal}.\n"
        return special_str


class Wyrm(Dragon):

    def __init__(self):
        super().__init__(name='Wyrm', health=random.randint(320, 400), mana=150, strength=38, intel=28, wisdom=30,
                         con=28, charisma=22, dex=23, exp=random.randint(920, 1180))
        self.equipment = {'Weapon': DragonTail2(), 'Armor': DragonScale(), 'OffHand': items.NoOffHand(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(650, 830)
        self.spellbook = {'Spells': {'Volcano': abilities.Volcano()},
                          'Skills': {'Triple Strike': abilities.TripleStrike()}}
        self.level.pro_level = 5
        self.picture = "wyrm.txt"


class Hydra(Monster):

    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(260, 375), mana=150, strength=37, intel=30, wisdom=26,
                         con=28, charisma=24, dex=22, exp=random.randint(900, 1150))
        self.equipment = {'Weapon': Bite2(), 'Armor': DragonScale(), 'OffHand': DragonTail(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(400, 550)
        self.spellbook = {'Spells': {'Tsunami': abilities.Tsunami()},
                          'Skills': {'Triple Strike': abilities.TripleStrike()}}
        self.resistance['Electric'] = -1
        self.resistance['Water'] = 1.5
        self.resistance['Death'] = 1
        self.resistance['Stone'] = 0.5
        self.resistance['Poison'] = 0.75
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 5
        self.picture = "hydra.txt"


class Wyvern(Dragon):

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(320, 410), mana=150, strength=35, intel=33, wisdom=24,
                         con=30, charisma=25, dex=40, exp=random.randint(950, 1200))
        self.equipment = {'Weapon': DragonClaw2(), 'Armor': DragonScale(), 'OffHand': DragonClaw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(420, 570)
        self.spellbook = {"Spells": {'Tornado': abilities.Tornado()},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike()}}
        self.flying = True
        self.level.pro_level = 5
        self.picture = "wyvern.txt"


class Archvile(Fiend):

    def __init__(self):
        super().__init__(name='Archvile', health=random.randint(360, 460), mana=200, strength=32, intel=31, wisdom=35,
                         con=38, charisma=28, dex=32, exp=random.randint(1010, 1280))
        self.equipment = {'Weapon': items.BattleGauntlet(), 'Armor': DemonArmor2(), 'OffHand': items.BattleGauntlet(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(375, 555)
        self.spellbook = {"Spells": {'Sleep': abilities.Sleep(),
                                     'Corruption': abilities.Corruption(),
                                     'Terrify': abilities.Terrify(),
                                     'Regen': abilities.Regen2(),
                                     'Firestorm': abilities.Firestorm()},
                          "Skills": {'Parry': abilities.Parry()}}
        self.resistance['Fire'] = 1.
        self.resistance['Ice'] = 0.5
        self.resistance['Electric'] = 0.5
        self.resistance['Poison'] = 1.
        self.level.pro_level = 5
        self.picture = "archvile.txt"


class BrainGorger(Aberration):

    def __init__(self):
        super().__init__(name='Brain Gorger', health=random.randint(310, 420), mana=250, strength=27, intel=40,
                         wisdom=35, con=31, charisma=25, dex=36, exp=random.randint(1050, 1310))
        self.status_effects['Blind'] = StatusEffect(True, -1)
        self.equipment = {'Weapon': Claw3(), 'Armor': items.NoArmor(), 'OffHand': Claw3(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = random.randint(320, 515)
        self.spellbook = {"Spells": {'Terrify': abilities.Terrify(),
                                     'Weaken Mind': abilities.WeakenMind()},
                          "Skills": {'Brain Gorge': abilities.BrainGorge()}}
        self.resistance['Fire'] = 0.25
        self.resistance['Ice'] = 0.25
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = 0.25
        self.resistance['Earth'] = 0.25
        self.resistance['Wind'] = 0.25
        self.resistance['Poison'] = 1.
        self.level.pro_level = 5
        self.picture = "braingorger.txt"


class Domingo(Aberration):
    """
    Level 5 Special Boss - guards fifth of six relics (LUNA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Domingo', health=1500, mana=999, strength=0, intel=50, wisdom=40, con=45, charisma=60,
                         dex=50, exp=40000)
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 25000
        self.spellbook = {"Spells": {'Ultima': abilities.Ultima(),
                                     'Desoul': abilities.Desoul(),
                                     'Boost': abilities.Boost()},
                          "Skills": {'Multi-Cast': abilities.DoubleCast()}}
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
        self.level.pro_level = 5
        self.sight = True
        self.picture = "domingo.txt"


class RedDragon(Dragon):
    """
    Level 5 Boss
    Transform Level 4 creature
    Highly resistant to spells and will heal from fire spells
    """

    def __init__(self):
        super().__init__(name='Red Dragon', health=2000, mana=500, strength=50, intel=38, wisdom=45, con=55,
                         charisma=40, dex=35, exp=80000)
        self.equipment = {'Weapon': DragonTail2(), 'Armor': DragonScale(), 'OffHand': DragonClaw2(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = 50000
        self.inventory['Item'] = [items.random_item(7)]
        self.spellbook = {"Spells": {'Heal': abilities.Heal3(),
                                     'Volcano': abilities.Volcano(),
                                     'Ultima': abilities.Ultima()},
                          "Skills": {'Mortal Strike': abilities.MortalStrike2(),
                                     'Multi-Cast': abilities.TripleCast()}}
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
        self.level.pro_level = 5
        self.sight = True
        self.picture = "reddragon.txt"


# Final Boss Guard
class Cerberus(Fiend):
    """
    Level 6 Special Boss - guards sixth and final of six relics (INFINITAS) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Cerberus', health=2500, mana=500, strength=65, intel=28, wisdom=45, con=60, charisma=40,
                         dex=38, exp=120000)
        self.equipment = {'Weapon': CerberusBite(), 'Armor': CerberusHide(), 'OffHand': CerberusClaw(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.gold = 100000
        self.inventory['Item'] = [items.random_item(8)]
        self.spellbook = {"Spells": {'Regen': abilities.Regen3(),
                                     'Shell': abilities.Shell()},
                          "Skills": {'Triple Strike': abilities.TripleStrike(),
                                     'Trip': abilities.Trip()}}
        self.resistance['Fire'] = 1
        self.resistance['Ice'] = -0.25
        self.resistance['Electric'] = 0.5
        self.resistance['Death'] = 1.
        self.resistance['Stone'] = 1.
        self.resistance['Holy'] = 0.25
        self.resistance['Physical'] = 0.5
        self.level.pro_level = 6
        self.sight = True
        self.picture = "cerberus.txt"


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
        self.equipment = {'Weapon': DevilBlade(), 'Armor': DevilSkin(), 'OffHand': DevilBlade(), 'Ring': items.NoRing(),
                          'Pendant': items.NoPendant()}
        self.spellbook = {"Spells": {'Hellfire': abilities.Hellfire(),
                                     'Terrify': abilities.Terrify(),
                                     'Regen': abilities.Regen3()},
                          "Skills": {'Choose Fate': abilities.ChooseFate(),
                                     'Crush': abilities.Crush(),
                                     "Parry": abilities.Parry()}}
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
        self.level.pro_level = 99
        self.sight = True
        self.picture = "devil.txt"

    def check_mod(self, mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.status_effects["Disarm"].active))
            class_mod += self.damage_mod + (self.stats.strength // 3)
            weapon_mod += self.status_effects['Attack'].extra * self.status_effects['Attack'].active
            return weapon_mod + class_mod
        if mod == 'offhand':
            off_mod = self.equipment['OffHand'].damage
            class_mod += self.damage_mod + (self.stats.strength // 5)
            off_mod += self.status_effects['Attack'].extra * self.status_effects['Attack'].active
            return int((off_mod + class_mod) * 0.75)
        if mod == 'armor':
            class_mod += self.damage_mod
            armor_mod = self.equipment['Armor'].armor
            armor_mod += self.status_effects['Defense'].extra * self.status_effects['Defense'].active
            return armor_mod + class_mod
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * 10
            class_mod += self.spell_mod
            magic_mod += self.status_effects['Magic'].extra * self.status_effects['Magic'].active
            return magic_mod + class_mod
        if mod == 'magic def':
            m_def_mod = self.stats.wisdom
            class_mod += self.spell_mod
            m_def_mod += self.status_effects['Magic Defense'].extra * self.status_effects['Magic Defense'].active
            return m_def_mod + class_mod
        if mod == 'heal':
            class_mod += self.spell_mod
            heal_mod = self.stats.wisdom * self.level.pro_level
            magic_mod += self.status_effects['Magic'].extra * self.status_effects['Magic'].active
            return heal_mod + class_mod
        if mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return -0.25
            if typ in self.resistance:
                res_mod = self.resistance[typ]
            return res_mod
        if mod == 'luck':
            luck_mod = self.stats.charisma // luck_factor
            return luck_mod
        return 0
