###########################################
""" enemy manager """

import random
import time
from textwrap import wrap

import abilities
import items
from character import Character, Combat, Resource, Stats, StatusEffect


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

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, Resource(health+con, health+con), Resource(mana+intel, mana+intel),
                         Stats(strength, intel, wisdom, con, charisma, dex),
                         Combat(attack, defense, magic, magic_def))
        self.name = name
        self.cls = self
        self.experience = exp
        self.enemy_typ = ""
        self.action_stack = []
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
                "Fire:", f"{self.resistance['Fire']}", "Ice:", f"{self.resistance['Ice']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Electric:", f"{self.resistance['Electric']}", "Water:", f"{self.resistance['Water']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Earth:", f"{self.resistance['Earth']}", "Wind:", f"{self.resistance['Wind']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Shadow:", f"{self.resistance['Shadow']}", "Holy:", f"{self.resistance['Holy']}"),
            "{:12}{:>6}  {:12}{:>6}".format(
                "Poison:", f"{self.resistance['Poison']}", "Physical:", f"{self.resistance['Physical']}")
                        ]
        resist_str = "\n".join(resist_str)
        immunity_str = ", ".join(self.status_immunity) if self.status_immunity else "None"
        specials = list(self.spellbook['Spells'].keys()) + list(self.spellbook['Skills'].keys())
        specials = ", ".join(specials)
        specials = "\n".join(wrap(f"Specials: {specials}", 50, break_on_hyphens=False))
        text = (
            f"\nName: {self.name} Type: {self.enemy_typ}\n\n"
            f"Stats:\n"
            f"{stats_str}\n\n"
            f"Resistances:\n"
            f"{resist_str}\n\n"
            f"Immunities: {immunity_str}\n\n"
            f"{specials}"
        )
        return text

    def options(self, target, action_list):
        if self.status_effects["Berserk"].active:
            return "Attack"
        if self.turtle or self.magic_effects["Ice Block"].active:
            return "Nothing"
        if self.name != 'Test' and not self.tunnel:
            action_list = ["Attack"]
        else:
            action_list = []
        if not self.status_effects["Silence"].active:
            for spell_name, spell in self.spellbook['Spells'].items():
                if self.spellbook['Spells'][spell_name].passive:
                    continue
                if self.tunnel:
                    if spell.subtyp not in ["Heal", "Support"]:
                        continue
                if self.spellbook['Spells'][spell_name].cost <= self.mana.current:
                    action_list.append(spell)
        for skill_name, skill in self.spellbook['Skills'].items():
            if any([self.spellbook['Skills'][skill_name].passive,
                    self.spellbook['Skills'][skill_name].name == "Backstab" and not target.incapacitated(),
                    self.spellbook["Skills"][skill_name].weapon and self.physical_effects["Disarm"].active,
                    self.spellbook["Skills"][skill_name].name == "Smoke Screen" and
                        self.health.current > self.health.max * 0.25,
                    self.tunnel]):
                continue
            if self.spellbook['Skills'][skill_name].cost <= self.mana.current:
                action_list.append(skill)
        if self.physical_effects["Disarm"].active:
            action_list.append("Pickup Weapon")
        if self.tunnel:
            action_list.extend(["Surface", "Nothing"])
        action = random.choice(action_list)
        if self.action_stack:
            pass  # TODO make responses dictionary for status effects and such
        return action

    def combat_turn(self, game, target, action, in_combat):
        combat_text = ""
        valid_entry = True
        cover = False
        flee = False
        fail_flee = False
        tile = game.player_char.world_dict[
            (game.player_char.location_x, game.player_char.location_y, game.player_char.location_z)]
        if self.incapacitated():
            in_combat = True
        elif action == "Nothing":
            combat_text += f"{self.name} does nothing.\n"
        elif action == "Surface":
            self.tunnel = False
            combat_text += f"{self.name} resurfaces.\n"
        else:
            if target.cls.name in ['Warlock', 'Shadowcaster']:
                if 'Cover' in target.familiar.spellbook['Skills'] and not random.randint(0, 3):
                    cover = True
            if (target.level.pro_level * target.level.level) >= 10 and target.level.pro_level > self.level.pro_level and \
                    random.randint(0, target.level.pro_level - self.level.pro_level) and 'Boss' not in str(tile) and \
                    self.name != 'Mimic':
                if not random.randint(0, 1):
                    if random.randint(0, self.check_mod("speed", enemy=target)) > \
                        random.randint(0, target.check_mod("speed", enemy=self)):
                        in_combat = False
                        flee = True
                        combat_text += f"{self.name} runs away!\n"
                    else:
                        combat_text += f"{self.name} tries to run away...but fails.\n"
                        fail_flee = True
            if not flee and not fail_flee:
                if action == "Attack":
                    special_str = ""
                    if not random.randint(0, 9 - self.check_mod("luck", luck_factor=20)):
                        special_str = self.special_attack(target=target)
                    if not special_str:
                        wd_str, _, _ = self.weapon_damage(target, cover=cover)
                        combat_text += wd_str
                    else:
                        combat_text += special_str
                elif action == "Pickup Weapon":
                    combat_text += f"{self.name} picks up their weapon.\n"
                    self.physical_effects["Disarm"].active = False
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
        combat_text += self.special_effects(target=target)
        if combat_text:
            import utils
            battlebox = utils.TextBox(game)
            battlebox.print_text_in_rectangle(combat_text)
            time.sleep(0.1)
            game.stdscr.getch()
            battlebox.clear_rectangle()
        if not self.is_alive():
            in_combat = False
        return valid_entry, in_combat, flee


class Misc(Enemy):
    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Misc'


class Slime(Enemy):
    """
    Slime type; resistance against all attack magic types; weak against physical damage
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
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

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Animal'
        self.inventory['Mystery Meat'] = [items.MysteryMeat]


class Humanoid(Enemy):
    """
    Humanoid type; no special features
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Humanoid'


class Fey(Enemy):
    """
    Fey type; resistance against shadow damage
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Fey'
        self.resistance['Shadow'] = 0.25


class Fiend(Enemy):
    """
    Fiend type; resistance against shadow damage and weak against holy; immune to death
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Fiend'
        self.resistance['Shadow'] = 0.25
        self.resistance['Holy'] = -0.25
        self.status_immunity = ["Death"]


class Undead(Enemy):
    """
    Undead type; resistance against shadow and poison and weak against fire; very weak against holy and immune to death
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Undead'
        self.resistance['Fire'] = -0.25
        self.resistance['Shadow'] = 0.5
        self.resistance['Holy'] = -0.75
        self.resistance["Poison"] = 0.5
        self.status_immunity = ["Death"]


class Elemental(Enemy):
    """
    Elemental type; high resistance against physical damage
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Elemental'
        self.resistance['Physical'] = 0.25


class Dragon(Enemy):
    """
    Dragon type; resistance against elemental and immune to death magic types; mild resistance against physical
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Dragon'
        self.resistance['Fire'] = 0.25
        self.resistance['Ice'] = 0.25
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = 0.25
        self.resistance['Earth'] = 0.25
        self.resistance['Wind'] = 0.25
        self.resistance['Physical'] = 0.1
        self.status_immunity = ["Death", "Stone"]


class Monster(Enemy):
    """
    Monster type; no special resistances
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Monster'


class Aberration(Enemy):
    """
    Aberration type; no special resistances
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Aberration'


class Construct(Enemy):
    """
    Construct type: immune to death, stone, and poison, strong against physical
    """

    def __init__(self, name, health, mana, strength, intel, wisdom, con, charisma, dex,
                 attack, defense, magic, magic_def, exp):
        super().__init__(name, health, mana, strength, intel, wisdom, con, charisma, dex,
                         attack, defense, magic, magic_def, exp)
        self.enemy_typ = 'Construct'
        self.resistance["Poison"] = 1.
        self.resistance['Physical'] = 0.5
        self.status_immunity = ["Poison", "Death", "Stone"]


# Enemies
class Test(Misc):
    """
    Used for testing new implementations
    """

    def __init__(self):
        super().__init__(name="Test", health=1, mana=999, strength=20, intel=0, wisdom=0, con=10, charisma=99, dex=25,
                         attack=0, defense=0, magic=0, magic_def=0,
                         exp=5000)
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook = {"Spells": {'Firebolt': abilities.Firebolt()},
                          "Skills": {'Doublecast': abilities.Doublecast()}}
        self.level.pro_level = 99  # test for enemies running away

    def special_attack(self, target):
        return abilities.BreatheFire().use(self, target=target)


class Mimic(Aberration):
    """
    true sight
    z: location level plus 1 if Locked plus 1 if ChestRoom2
    health: 
    mana: 
    strength: 
    intel: 
    wisdom: 
    con: 
    charisma:
    dex: 
    attack:
    defense:
    magic:
    magic def:
    exp: 
    gold: 
    """

    def __init__(self, z):
        super().__init__(name='Mimic', health=20 + (random.randint(10, 40) * z), mana=10 + (random.randint(20, 35) * z),
                         strength=(15 + (5 * (z - 1))), intel=(6 + (3 * (z - 1))), wisdom=(11 + (5 * (z - 1))),
                         con=(13 + (5 * (z - 1))), charisma=(8 + (4 * (z - 1))), dex=(12 + (4 * (z - 1))),
                         attack=(random.randint(10, 20) * z), defense=(random.randint(6, 15) * z),
                         magic=(random.randint(8, 16) * z), magic_def=(random.randint(4, 12) * z), 
                         exp=25 + (random.randint(25, 50) * z))
        self.gold = 50 + (random.randint(50, 100) * z)
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook = {"Spells": {},
                          "Skills": {'Lick': abilities.Lick(),
                                     'Gold Toss': abilities.GoldToss(),
                                     'Slot Machine': abilities.SlotMachine()}}
        self.resistance["Poison"] = 1.0
        self.status_immunity = ["Poison", "Death", "Stone"]
        self.level.pro_level = z
        self.sight = True
        self.picture = "mimic.txt"


# Starting enemies
class GreenSlime(Slime):

    def __init__(self):
        super().__init__(name='Green Slime', health=random.randint(7, 14), mana=25, strength=6, intel=15, wisdom=15,
                         con=8, charisma=1, dex=6, attack=3, defense=7, magic=8, magic_def=99,
                         exp=random.randint(1, 20))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(1, 8)
        self.inventory['Key'] = [items.Key]
        self.spellbook = {"Spells": {'Enfeeble': abilities.Enfeeble()},
                          "Skills": {'Acid Spit': abilities.AcidSpit()}}
        self.level.pro_level = 0


class GiantRat(Animal):

    def __init__(self):
        super().__init__(name='Giant Rat', health=random.randint(2, 4), mana=3, strength=4, intel=3, wisdom=3, con=6,
                         charisma=6, dex=15, attack=2, defense=5, magic=2, magic_def=6,
                         exp=random.randint(7, 14))
        self.equipment = {'Weapon': items.Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(1, 5)
        self.inventory['Rat Tail'] = [items.RatTail]
        self.level.pro_level = 0
        self.picture = "giantrat.txt"


class Goblin(Humanoid):

    def __init__(self):
        super().__init__(name='Goblin', health=random.randint(3, 7), mana=5, strength=7, intel=5, wisdom=2, con=8,
                         charisma=12, dex=8, attack=2, defense=6, magic=5, magic_def=7,
                         exp=random.randint(7, 16))
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
        self.combat = Combat(35, 18, 12, 22)
        self.equipment = {'Weapon': items.Jian(), 'Armor': items.LeatherArmor(), 'OffHand': items.Baselard(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Mirror Image"] = abilities.MirrorImage()
        self.spellbook['Skills']["Parry"] = abilities.Parry()


class Bandit(Humanoid):

    def __init__(self):
        super().__init__(name='Bandit', health=random.randint(4, 8), mana=16, strength=8, intel=8, wisdom=5, con=8,
                         charisma=10, dex=10, attack=4, defense=5, magic=3, magic_def=5,
                         exp=random.randint(8, 18))
        self.equipment = {'Weapon': items.Dirk(), 'Armor': items.PaddedArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 25)
        self.inventory['Feather'] = [items.Feather]
        self.spellbook = {"Spells": {},
                          "Skills": {'Steal': abilities.Steal(),
                                     "Disarm": abilities.Disarm(),
                                     'Smoke Screen': abilities.SmokeScreen()}}
        self.level.pro_level = 0
        self.picture = "fighter.txt"


class Skeleton(Undead):

    def __init__(self):
        super().__init__(name='Skeleton', health=random.randint(5, 7), mana=2, strength=8, intel=4, wisdom=8, con=12,
                         charisma=5, dex=6, attack=3, defense=8, magic=5, magic_def=6,
                         exp=random.randint(11, 20))
        self.equipment = {'Weapon': items.Rapier(), 'Armor': items.NoArmor(), 'OffHand': items.Buckler(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(1, 5)
        self.inventory['Health Potion'] = [items.HealthPotion]
        self.resistance['Fire'] = 0.0
        self.level.pro_level = 0
        self.picture = "skeleton.txt"


class Scarecrow(Construct):

    def __init__(self):
        super().__init__(name='Scarecrow', health=random.randint(5, 7), mana=10, strength=12, intel=3, wisdom=6, con=10,
                         charisma=8, dex=11, attack=4, defense=5, magic=7, magic_def=5,
                         exp=random.randint(13, 21))
        self.equipment = {'Weapon': items.Claw(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(8, 16)
        self.spellbook = {"Spells": {},
                          "Skills": {'Sleeping Powder': abilities.SleepingPowder()}}
        self.resistance['Fire'] = -1.0
        self.resistance['Physical'] = 0.0
        self.level.pro_level = 0
        self.picture = "scarecrow.txt"


# Level 1
class GiantCentipede(Animal):

    def __init__(self):
        super().__init__(name='Giant Centipede', health=random.randint(8, 13), mana=3, strength=10, intel=4, wisdom=6,
                         con=8, charisma=8, dex=12, attack=10, defense=9, magic=5, magic_def=7,
                         exp=random.randint(13, 24))
        self.equipment = {'Weapon': items.Pincers(), 'Armor': items.Carapace(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 18)
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 1
        self.picture = "centipede.txt"


class GiantHornet(Animal):

    def __init__(self):
        super().__init__(name='Giant Hornet', health=random.randint(6, 10), mana=25, strength=6, intel=4, wisdom=6,
                         con=6, charisma=8, dex=18, attack=9, defense=8, magic=6, magic_def=9,
                         exp=random.randint(13, 24))
        self.equipment = {'Weapon': items.Stinger(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(6, 15)
        self.spellbook = {"Spells": {"Berserk": abilities.Berserk()},
                          "Skills": {}}
        self.flying = True
        self.level.pro_level = 1
        self.picture = "hornet.txt"


class ElectricBat(Animal):

    def __init__(self):
        super().__init__(name='Electric Bat', health=random.randint(5, 9), mana=15, strength=6, intel=11, wisdom=7,
                         con=5, charisma=12, dex=22, attack=10, defense=6, magic=14, magic_def=11,
                         exp=random.randint(17, 31))
        self.equipment = {'Weapon': items.Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(8, 21)
        self.spellbook = {"Spells": {'Shock': abilities.Shock(),
                                     "Silence": abilities.Silence()},
                          "Skills": {}}
        self.flying = True
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = -0.25
        self.level.pro_level = 1
        self.picture = "bat.txt"


class Zombie(Undead):

    def __init__(self):
        super().__init__(name='Zombie', health=random.randint(11, 14), mana=20, strength=15, intel=1, wisdom=5, con=8,
                         charisma=8, dex=8, attack=12, defense=10, magic=4, magic_def=8,
                         exp=random.randint(11, 22))
        self.equipment = {'Weapon': items.Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 30)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': abilities.PoisonStrike()}}
        self.level.pro_level = 1
        self.picture = "zombie.txt"


class Imp(Fiend):

    def __init__(self):
        super().__init__(name='Imp', health=random.randint(9, 14), mana=25, strength=6, intel=12, wisdom=10,
                         con=8, charisma=12, dex=12, attack=7, defense=11, magic=16, magic_def=14,
                         exp=random.randint(15, 24))
        self.equipment = {'Weapon': items.DemonClaw(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 30)
        self.spellbook = {"Spells": {'Corruption': abilities.Corruption(),
                                     "Silence": abilities.Silence()},
                          "Skills": {}}
        self.level.pro_level = 1
        self.picture = "imp.txt"


class GiantSpider(Animal):

    def __init__(self):
        super().__init__(name='Giant Spider', health=random.randint(12, 15), mana=10, strength=9, intel=10, wisdom=10,
                         con=8, charisma=10, dex=12, attack=11, defense=13, magic=8, magic_def=10,
                         exp=random.randint(15, 24))
        self.equipment = {'Weapon': items.Stinger(), 'Armor': items.Carapace(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(15, 30)
        self.spellbook = {'Spells': {},
                          'Skills': {'Web': abilities.Web()}}
        self.resistance["Poison"] = 0.25
        self.level.pro_level = 1
        self.picture = "spider.txt"


class Quasit(Fiend):
    """
    Can shapeshift between Electric Bat, Giant Centipede, Battle Toad, and natural forms
    """

    def __init__(self):
        super().__init__(name='Quasit', health=random.randint(13, 17), mana=15, strength=8, intel=8, wisdom=10,
                         con=11, charisma=14, dex=16, attack=10, defense=11, magic=10, magic_def=13,
                         exp=random.randint(25, 44))
        self.equipment = {'Weapon': items.DemonClaw(), 'Armor': items.DemonArmor(), 'OffHand': items.Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(25, 40)
        self.spellbook = {"Spells": {},
                          "Skills": {'Poison Strike': abilities.PoisonStrike(),
                                     'Shapeshift': abilities.Shapeshift()}}
        self.resistance["Poison"] = 1
        self.status_immunity.append("Poison")
        self.transform = [Quasit,
                          ElectricBat,
                          GiantCentipede,
                          BattleToad]
        self.level.pro_level = 1
        self.picture = "quasit.txt"


class Panther(Animal):

    def __init__(self):
        super().__init__(name='Panther', health=random.randint(10, 14), mana=25, strength=10, intel=8, wisdom=8,
                         con=10, charisma=10, dex=13, attack=13, defense=10, magic=8, magic_def=7,
                         exp=random.randint(19, 28))
        self.equipment = {'Weapon': items.Claw(), 'Armor': items.AnimalHide(), 'OffHand': items.Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 20)
        self.inventory['Leather'] = [items.Leather]
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': abilities.Backstab(),
                                     'Kidney Punch': abilities.KidneyPunch(),
                                     "Disarm": abilities.Disarm()}}
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 1
        self.picture = "panther.txt"


class Panther2(Panther):
    """
    Transform Level 1 creature
    """

    def __init__(self):
        super().__init__()
        self.stats = Stats(0, 0, 0, 0, 0, 0)
        self.combat = Combat(0, 0, 0, 0)


class TwistedDwarf(Humanoid):

    def __init__(self):
        super().__init__(name='Twisted Dwarf', health=random.randint(15, 19), mana=10, strength=12, intel=8, wisdom=10,
                         con=12, charisma=8, dex=10, attack=14, defense=14, magic=11, magic_def=11,
                         exp=random.randint(25, 44))
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
                         con=10, charisma=8, dex=15, attack=11, defense=10, magic=12, magic_def=9,
                         exp=random.randint(30, 48))
        self.equipment = {'Weapon': items.BrassKnuckles(), 'Armor': items.NoArmor(), 'OffHand': items.BrassKnuckles(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(31, 47)
        self.spellbook = {"Spells": {},
                          "Skills": {"Kidney Punch": abilities.KidneyPunch()}}
#                          "Skills": {"Jump": abilities.Jump()}}  TODO nerf Jump by adding delay
        self.resistance["Water"] = 0.75
        self.level.pro_level = 1
        self.picture = "battletoad.txt"


class Satyr(Fey):

    def __init__(self):
        super().__init__(name='Satyr', health=random.randint(17, 22), mana=25, strength=11, intel=12, wisdom=10, con=11,
                         charisma=12, dex=12, attack=13, defense=14, magic=12, magic_def=18,
                         exp=random.randint(28, 44))
        self.equipment = {'Weapon': items.Rapier(), 'Armor': items.PaddedArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(29, 42)
        self.inventory['Leather'] = [items.Leather]
        self.spellbook = {"Spells": {},
                          "Skills": {'Stomp': abilities.Stomp()}}
        self.resistance['Fire'] = 0.1
        self.resistance['Ice'] = 0.1
        self.resistance['Electric'] = 0.1
        self.resistance['Water'] = 0.1
        self.resistance['Earth'] = 0.1
        self.resistance['Wind'] = 0.1
        self.resistance["Poison"] = 0.1
        self.resistance['Physical'] = 0.1
        self.level.pro_level = 1
        self.picture = "satyr.txt"


class Minotaur(Monster):
    """
    Level 1 Boss
    """

    def __init__(self):
        super().__init__(name='Minotaur', health=86, mana=60, strength=18, intel=8, wisdom=10, con=14, charisma=14,
                         dex=12, attack=24, defense=15, magic=12, magic_def=17,
                         exp=250)
        self.equipment = {'Weapon': items.Broadaxe(), 'Armor': items.LeatherArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 200
        self.inventory['Weapon'] = [items.random_item(2)]
        self.inventory['Leather'] = [items.Leather]
        self.spellbook = {"Spells": {},
                          "Skills": {'Mortal Strike': abilities.MortalStrike(),
                                     'Charge': abilities.Charge(),
                                     "Disarm": abilities.Disarm(),
                                     'Parry': abilities.Parry()}}
        self.status_immunity = ["Death"]
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
                         con=18, charisma=14, dex=16, attack=40, defense=35, magic=21, magic_def=32,
                         exp=500)
        self.gold = 600
        self.equipment = {'Weapon': items.Claw2(), 'Armor': items.AnimalHide(), 'OffHand': items.Claw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.inventory['Old Key'] = [items.OldKey]
        self.spellbook = {"Spells": {"Enfeeble": abilities.Enfeeble()},
                          "Skills": {'Shapeshift': abilities.Shapeshift(),
                                     'Kidney Punch': abilities.KidneyPunch(),
                                     'Backstab': abilities.Backstab()}}
        self.resistance['Physical'] = 0.25
        self.transform = [Barghest, Goblin2, Direwolf2]
        self.level.pro_level = 2
        self.sight = True
        self.picture = "barghest.txt"


# Level 2
class Gnoll(Humanoid):

    def __init__(self):
        super().__init__(name='Gnoll', health=random.randint(16, 24), mana=20, strength=13, intel=10, wisdom=5, con=8,
                         charisma=12, dex=16, attack=13, defense=12, magic=12, magic_def=13,
                         exp=random.randint(45, 85))
        self.equipment = {'Weapon': items.Partisan(), 'Armor': items.PaddedArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(10, 20)
        self.inventory['Feather'] = [items.Feather]
        self.spellbook = {"Spells": {},
                          "Skills": {"Disarm": abilities.Disarm()}}
        self.level.pro_level = 2
        self.picture = "gnoll.txt"


class GiantSnake(Animal):

    def __init__(self):
        super().__init__(name='Giant Snake', health=random.randint(18, 26), mana=2, strength=15, intel=5, wisdom=6,
                         con=14, charisma=10, dex=16, attack=16, defense=15, magic=8, magic_def=11,
                         exp=random.randint(60, 100))
        self.equipment = {'Weapon': items.SnakeFang(), 'Armor': items.SnakeScales(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(35, 75)
        self.inventory['Snake Skin'] = [items.SnakeSkin]
        self.spellbook = {"Spells": {},
                          "Skills": {"Slam": abilities.Slam()}}
        self.resistance["Poison"] = 0.25
        self.level.pro_level = 2
        self.picture = "snake.txt"


class Orc(Humanoid):

    def __init__(self):
        super().__init__(name='Orc', health=random.randint(17, 28), mana=14, strength=12, intel=6, wisdom=5, con=10,
                         charisma=8, dex=14, attack=14, defense=13, magic=10, magic_def=10,
                         exp=random.randint(45, 80))
        self.equipment = {'Weapon': items.Jian(), 'Armor': items.LeatherArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(20, 65)
        self.inventory['Leather'] = [items.Leather]
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike()}}
        self.level.pro_level = 2
        self.picture = "orc.txt"


class GiantOwl(Animal):

    def __init__(self):
        super().__init__(name='Giant Owl', health=random.randint(12, 17), mana=12, strength=13, intel=12, wisdom=10,
                         con=10, charisma=1, dex=15, attack=10, defense=12, magic=14, magic_def=16,
                         exp=random.randint(45, 80))
        self.equipment = {'Weapon': items.Claw2(), 'Armor': items.NoArmor(), 'OffHand': items.Claw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(20, 65)
        self.spellbook = {"Spells": {},
                          "Skills": {'Screech': abilities.Screech()}}
        self.inventory['Feather'] = [items.Feather]
        self.flying = True
        self.level.pro_level = 2
        self.picture = "giantowl.txt"


class Vampire(Undead):

    def __init__(self):
        super().__init__(name='Vampire', health=random.randint(20, 28), mana=30, strength=16, intel=14, wisdom=12,
                         con=15, charisma=14, dex=14, attack=13, defense=17, magic=21, magic_def=18,
                         exp=random.randint(50, 90))
        self.equipment = {'Weapon': items.IronshodStaff(), 'Armor': items.NoArmor(), 'OffHand': items.VampireBite(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 90)
        self.spellbook = {"Spells": {"Silence": abilities.Silence(),
                                     'Lightning': abilities.Lightning()},
                          "Skills": {'Health Drain': abilities.HealthDrain(),
                                     'Shapeshift': abilities.Shapeshift()}}
        self.transform = [Vampire, VampireBat]
        self.level.pro_level = 2
        self.picture = "vampire.txt"


class VampireBat(Animal):

    def __init__(self):
        super().__init__(name='Vampire Bat', health=random.randint(20, 28), mana=30, strength=12, intel=16, wisdom=15,
                         con=10, charisma=14, dex=18, attack=10, defense=11, magic=14, magic_def=11,
                         exp=random.randint(50, 90))
        self.equipment = {'Weapon': items.VampireBite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
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
                         charisma=10, dex=16, attack=17, defense=16, magic=9, magic_def=8,
                         exp=random.randint(60, 100))
        self.equipment = {'Weapon': items.Claw2(), 'Armor': items.AnimalHide(), 'OffHand': items.Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(35, 75)
        self.inventory['Leather'] = [items.Leather]
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
        self.combat = Combat(36, 38, 24, 33)
        self.equipment = {'Weapon': items.Claw2(), 'Armor': items.AnimalHide2(), 'OffHand': items.Claw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook['Skills']["Jump"] = abilities.Jump()


class Wererat(Monster):

    def __init__(self):
        super().__init__(name='Wererat', health=random.randint(14, 17), mana=4, strength=14, intel=6, wisdom=12, con=11,
                         charisma=8, dex=18, attack=11, defense=14, magic=7, magic_def=11,
                         exp=random.randint(57, 94))
        self.equipment = {'Weapon': items.Bite(), 'Armor': items.AnimalHide(), 'OffHand': items.Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.inventory["Rat Tail"] = [items.RatTail]
        self.inventory['Leather'] = [items.Leather]
        self.level.pro_level = 2
        self.picture = "giantrat.txt"


class RedSlime(Slime):

    def __init__(self):
        super().__init__(name='Red Slime', health=random.randint(18, 32), mana=30, strength=10, intel=20, wisdom=20,
                         con=12, charisma=10, dex=5, attack=7, defense=13, magic=24, magic_def=150,
                         exp=random.randint(43, 150))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.inventory['Mana Potion'] = [items.ManaPotion]
        self.spellbook = {'Spells': {'Firebolt': abilities.Firebolt(),
                                     'Enfeeble': abilities.Enfeeble()},
                          'Skills': {}}
        self.level.pro_level = 2


class GiantScorpion(Animal):

    def __init__(self):
        super().__init__(name='Giant Scorpion', health=random.randint(13, 18), mana=2, strength=14, intel=5, wisdom=10,
                         con=12, charisma=10, dex=9, attack=16, defense=18, magic=9, magic_def=15,
                         exp=random.randint(65, 105))
        self.equipment = {'Weapon': items.Stinger(), 'Armor': items.Carapace(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.resistance["Poison"] = 0.25
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 2
        self.picture = "giantscorpion.txt"


class Warrior(Humanoid):

    def __init__(self):
        super().__init__(name='Warrior', health=random.randint(22, 31), mana=25, strength=14, intel=10, wisdom=8,
                         con=12, charisma=10, dex=10, attack=14, defense=14, magic=14, magic_def=12,
                         exp=random.randint(65, 110))
        self.equipment = {'Weapon': items.Jian(), 'Armor': items.ChainMail(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(25, 100)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook = {"Spells": {},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike(),
                                     "Disarm": abilities.Disarm(),
                                     'Parry': abilities.Parry()}}
        self.level.pro_level = 2
        self.picture = "fighter.txt"


class Harpy(Monster):

    def __init__(self):
        super().__init__(name='Harpy', health=random.randint(18, 25), mana=23, strength=18, intel=13, wisdom=13,
                         con=14, charisma=14, dex=23, attack=12, defense=15, magic=18, magic_def=14,
                         exp=random.randint(65, 115))
        self.equipment = {'Weapon': items.Mace(), 'Armor': items.NoArmor(), 'OffHand': items.Claw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(50, 75)
        self.inventory['Feather'] = [items.Feather]
        self.flying = True
        self.spellbook = {'Spells': {"Berserk": abilities.Berserk()},
                          'Skills': {'Screech': abilities.Screech()}}
        self.level.pro_level = 2
        self.picture = "harpy.txt"


class Naga(Monster):

    def __init__(self):
        super().__init__(name='Naga', health=random.randint(22, 28), mana=17, strength=15, intel=13, wisdom=15,
                         con=15, charisma=12, dex=17, attack=17, defense=16, magic=13, magic_def=16,
                         exp=random.randint(67, 118))
        self.equipment = {'Weapon': items.Partisan(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(55, 75)
        self.spellbook = {"Spells": {"Silence": abilities.Silence()},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Electric'] = -0.5
        self.resistance['Water'] = 0.75
        self.level.pro_level = 2
        self.picture = "naga.txt"


class Clannfear(Fiend):

    def __init__(self):
        super().__init__(name='Clannfear', health=random.randint(22, 28), mana=40, strength=17, intel=8, wisdom=11,
                         con=14, charisma=12, dex=15, attack=11, defense=19, magic=11, magic_def=12,
                         exp=random.randint(77, 130))
        self.equipment = {'Weapon': items.DemonClaw(), 'Armor': items.AnimalHide(), 'OffHand': items.DemonClaw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
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
    Earth elemental; rare drop to obtain summon Dilong
    """

    def __init__(self):
        super().__init__(name='Xorn', health=random.randint(27, 33), mana=40, strength=16, intel=11, wisdom=12,
                         con=17, charisma=10, dex=12, attack=16, defense=19, magic=17, magic_def=17,
                         exp=random.randint(74, 121))
        self.equipment = {'Weapon': items.Claw(), 'Armor': items.NoArmor(), 'OffHand': items.Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(61, 99)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.inventory["Chiryu Koma"] = [items.ChiryuKoma]
        self.spellbook = {'Spells': {'Tremor': abilities.Tremor()},
                          'Skills': {'ConsumeItem': abilities.ConsumeItem()}}
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.5
        self.resistance['Earth'] = 1.0
        self.resistance["Poison"] = 1.0
        self.status_immunity = ["Poison", "Stone"]
        self.level.pro_level = 2
        self.picture = "xorn.txt"


class SteelPredator(Construct):

    def __init__(self):
        super().__init__(name='Steel Predator', health=random.randint(27, 33), mana=40, strength=17, intel=9,
                         wisdom=12, con=14, charisma=12, dex=19, attack=18, defense=21, magic=11, magic_def=16,
                         exp=random.randint(85, 129))
        self.equipment = {'Weapon': items.Claw2(), 'Armor': items.MetalPlating(), 'OffHand': items.Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(65, 110)
        self.status_effects["Blind"] = StatusEffect(True, -1)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook = {'Spells': {"Silence": abilities.Silence()},
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
                         charisma=20, dex=18, attack=38, defense=30, magic=42, magic_def=40,
                         exp=800)
        self.gold = 1500
        self.equipment = {'Weapon': items.DragonClaw(), 'Armor': items.DragonScale(), 'OffHand': items.DragonClaw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.inventory['Item'] = [items.random_item(3)]
        self.inventory['Old Key'] = [items.OldKey]
        self.spellbook = {'Spells': {'Fireball': abilities.Fireball(),
                                     'Blinding Fog': abilities.BlindingFog(),
                                     'Dispel': abilities.Dispel()},
                          'Skills': {'Gold Toss': abilities.GoldToss()}}
        self.level.pro_level = 2
        self.sight = True
        self.picture = "pseudodragon.txt"

    def special_attack(self, target):
        return abilities.BreatheFire().use(self, target, typ="Fire")


class Nightmare(Fiend):
    """
    Level 2 Extra Boss - guards second of six relics (QUADRATA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Nightmare', health=410, mana=100, strength=30, intel=17, wisdom=15, con=22, charisma=16,
                         dex=15, attack=58, defense=42, magic=46, magic_def=38,
                         exp=2000)
        self.equipment = {'Weapon': items.NightmareHoof(), 'Armor': items.AnimalHide2(), 'OffHand': items.NightmareHoof(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 2500
        self.inventory['Item'] = [items.random_item(4)]
        self.inventory['Old Key'] = [items.OldKey]
        self.spellbook = {'Spells': {"Sleep": abilities.Sleep(),
                                     "Nightmare Fuel": abilities.NightmareFuel()},
                          'Skills': {'Stomp': abilities.Stomp(),
                                     'True Strike': abilities.TrueStrike()}}
        self.resistance['Fire'] = 1.
        self.resistance['Ice'] = -0.25
        self.resistance['Physical'] = 0.5
        self.flying = True
        self.level.pro_level = 3
        self.sight = True
        self.picture = "nightmare.txt"

    def special_attack(self, target):
        return super().special_attack(target)


# Level 3
class Direbear(Animal):

    def __init__(self):
        super().__init__(name='Direbear', health=random.randint(55, 70), mana=30, strength=24, intel=6, wisdom=6,
                         con=24, charisma=12, dex=17, attack=28, defense=28, magic=13, magic_def=15,
                         exp=random.randint(210, 310))
        self.equipment = {'Weapon': items.BearClaw(), 'Armor': items.AnimalHide(), 'OffHand': items.BearClaw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.inventory['Leather'] = [items.Leather]
        self.spellbook = {'Spells': {},
                          'Skills': {'Piercing Strike': abilities.PiercingStrike(),
                                     'Charge': abilities.Charge()}}
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 3
        self.picture = "direbear.txt"


class Direbear2(Direbear):
    """
    Transform Level 2 creature
    """

    def __init__(self):
        super().__init__()
        self.stats = Stats(0, 0, 0, 0, 0, 0)
        self.combat = Combat(0, 0, 0, 0)


class Ghoul(Undead):

    def __init__(self):
        super().__init__(name='Ghoul', health=random.randint(42, 60), mana=50, strength=25, intel=10, wisdom=8, con=24,
                         charisma=11, dex=12, attack=26, defense=28, magic=16, magic_def=17,
                         exp=random.randint(210, 290))
        self.equipment = {'Weapon': items.Bite(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(35, 45)
        self.spellbook = {"Spells": {'Disease Breath': abilities.DiseaseBreath()},
                          "Skills": {}}
        self.level.pro_level = 3
        self.picture = "ghoul.txt"


class PitViper(Animal):

    def __init__(self):
        super().__init__(name='Pit Viper', health=random.randint(38, 50), mana=30, strength=17, intel=6, wisdom=8,
                         con=16, charisma=10, dex=18, attack=25, defense=24, magic=12, magic_def=19,
                         exp=random.randint(215, 290))
        self.equipment = {'Weapon': items.SnakeFang2(), 'Armor': items.SnakeScales(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(50, 85)
        self.inventory['Snake Skin'] = [items.SnakeSkin]
        self.spellbook = {"Spells": {},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.resistance["Poison"] = 0.25
        self.level.pro_level = 3
        self.picture = "snake.txt"


class Disciple(Humanoid):

    def __init__(self):
        super().__init__(name='Disciple', health=random.randint(40, 50), mana=70, strength=16, intel=17, wisdom=15,
                         con=16, charisma=12, dex=16, attack=14, defense=20, magic=38, magic_def=36,
                         exp=random.randint(210, 290))
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
                         con=15, charisma=12, dex=6, attack=12, defense=24, magic=35, magic_def=200,
                         exp=random.randint(185, 360))
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
                         charisma=10, dex=14, attack=28, defense=27, magic=30, magic_def=31,
                         exp=random.randint(215, 295))
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
                         con=20, charisma=10, dex=15, attack=26, defense=27, magic=16, magic_def=23,
                         exp=random.randint(220, 300))
        self.equipment = {'Weapon': items.AlligatorTail(), 'Armor': items.NoArmor(), 'OffHand': items.Claw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 50)
        self.spellbook = {"Spells": {},
                          "Skills": {"Trip": abilities.Trip()}}
        self.level.pro_level = 3
        self.picture = "alligator.txt"


class Troll(Humanoid):

    def __init__(self):
        super().__init__(name='Troll', health=random.randint(50, 65), mana=20, strength=24, intel=10, wisdom=8, con=24,
                         charisma=12, dex=15, attack=25, defense=24, magic=22, magic_def=21,
                         exp=random.randint(225, 310))
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
                         con=17, charisma=15, dex=25, attack=23, defense=22, magic=25, magic_def=26,
                         exp=random.randint(230, 320))
        self.equipment = {'Weapon': items.Claw2(), 'Armor': items.NoArmor(), 'OffHand': items.Claw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(50, 75)
        self.inventory['Feather'] = [items.Feather]
        self.inventory["Bird Fat"] = [items.BirdFat]
        self.spellbook = {"Spells": {},
                          "Skills": {'Screech': abilities.Screech()}}
        self.flying = True
        self.level.pro_level = 3
        self.picture = "goldeneagle.txt"


class EvilCrusader(Humanoid):

    def __init__(self):
        super().__init__(name='Evil Crusader', health=random.randint(45, 60), mana=50, strength=21, intel=18, wisdom=17,
                         con=26, charisma=14, dex=14, attack=24, defense=34, magic=23, magic_def=27,
                         exp=random.randint(240, 325))
        self.equipment = {'Weapon': items.Pernach(), 'Armor': items.Splint(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(65, 90)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
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

    """

    def __init__(self):
        super().__init__(name='Werewolf', health=random.randint(55, 75), mana=85, strength=24, intel=10, wisdom=10,
                         con=20, charisma=14, dex=20, attack=28, defense=31, magic=21, magic_def=20,
                         exp=random.randint(220, 300))
        self.equipment = {'Weapon': items.Claw3(), 'Armor': items.AnimalHide(), 'OffHand': items.Claw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(45, 55)
        self.inventory['Leather'] = [items.Leather]
        self.spellbook = {"Spells": {},
                          "Skills": {'True Strike': abilities.TrueStrike(),
                                     'Howl': abilities.Howl()}}
        self.resistance['Physical'] = 0.1
        self.level.pro_level = 3
        self.picture = "werewolf.txt"


class Werewolf2(Werewolf):
    """
    Transform Level 3 creature
    """

    def __init__(self):
        super().__init__()
        self.stats = Stats(0, 0, 0, 0, 0, 0)
        self.combat = Combat(0, 0, 0, 0)


class Antlion(Animal):
    """
    modeled after the boss from FF2 (FFIV)
    """

    def __init__(self):
        super().__init__(name="Antlion", health=random.randint(52, 70), mana=70, strength=22, intel=8, wisdom=12,
                         con=18, charisma=12, dex=18, attack=26, defense=32, magic=18, magic_def=22,
                         exp=random.randint(210, 310))
        self.equipment = {'Weapon': items.Pincers2(), 'Armor': items.Carapace(), 'OffHand': items.Pincers2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 52)
        self.spellbook = {"Spells": {},
                          "Skills": {'Double Strike': abilities.DoubleStrike(),
                                     "Tunnel": abilities.Tunnel()}}
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 3
        self.picture = "antlion.txt"


class InvisibleStalker(Elemental):
    """
    Invisible
    """

    def __init__(self):
        super().__init__(name="Invisible Stalker", health=random.randint(25, 46), mana=60, strength=19, intel=13,
                         wisdom=16, con=14, charisma=18, dex=29, attack=21, defense=27, magic=22, magic_def=22,
                         exp=random.randint(230, 330))
        self.equipment = {'Weapon': items.InvisibleBlade(), 'Armor': items.NoArmor(), 'OffHand': items.InvisibleBlade(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(65, 79)
        self.spellbook = {"Spells": {},
                          "Skills": {'Backstab': abilities.Backstab(),
                                     "Kidney Punch": abilities.KidneyPunch(),
                                     'Poison Strike': abilities.PoisonStrike(),
                                     'Smoke Screen': abilities.SmokeScreen(),
                                     "Parry": abilities.Parry()}}
        self.resistance["Poison"] = 1.0
        self.status_immunity = ["Poison"]
        self.invisible = True
        self.sight = True
        self.level.pro_level = 3
        self.picture = "assassin.txt"


class NightHag(Fey):

    def __init__(self):
        super().__init__(name="Night Hag", health=random.randint(30, 48), mana=105, strength=16, intel=22, wisdom=26,
                         con=12, charisma=14, dex=19, attack=20, defense=26, magic=41, magic_def=40,
                         exp=random.randint(215, 312))
        self.equipment = {'Weapon': items.Kris(), 'Armor': items.SilverCloak(), 'OffHand': items.InfernalGrimoire(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(70, 99)
        self.spellbook = {"Spells": {"Sleep": abilities.Sleep(),
                                     'Enfeeble': abilities.Enfeeble(),
                                     'Magic Missile': abilities.MagicMissile()},
                          "Skills": {'Nightmare Fuel': abilities.NightmareFuel()}}
        self.resistance['Fire'] = 0.25
        self.resistance['Cold'] = 0.25
        self.resistance['Physical'] = 0.25
        self.level.pro_level = 3
        self.picture = "nighthag.txt"


class NightHag2(NightHag):
    """
    Waitress from tavern after Joffrey is discovered; modeled after Night Hag
    """

    def __init__(self):
        super().__init__()
        self.name = "Waitress"
        self.health = Resource(500, 500)
        self.mana = Resource(300, 300)
        self.stats = Stats(18, 24, 30, 15, 15, 20)
        self.combat = Combat(40, 51, 72, 68)
        self.experience = 2500
        self.gold = 1000
        self.inventory['Brass Key'] = [items.BrassKey]
        self.spellbook['Skills']["Widow's Wail"] = abilities.WidowsWail()
        self.status_immunity = ["Death", "Stone"]


class Treant(Fey):

    def __init__(self):
        super().__init__(name="Treant", health=random.randint(52, 78), mana=65, strength=26, intel=16, wisdom=21,
                         con=20, charisma=12, dex=16, attack=30, defense=35, magic=37, magic_def=43,
                         exp=random.randint(235, 320))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(60, 85)
        self.inventory['Cursed Hops'] = [items.CursedHops]
        self.spellbook = {"Spells": {"Regen": abilities.Regen()},
                          "Skills": {'Double Strike': abilities.DoubleStrike(),
                                     'Throw Rock': abilities.ThrowRock()}}
        self.resistance['Fire'] = -1.
        self.resistance['Water'] = 1.5
        self.resistance["Poison"] = 1.
        self.resistance['Physical'] = 0.25
        self.status_immunity = ["Poison"]
        self.level.pro_level = 3
        self.picture = "treant.txt"


class Ankheg(Monster):

    def __init__(self):
        super().__init__(name="Ankheg", health=random.randint(45, 69), mana=65, strength=23, intel=17, wisdom=14,
                         con=19, charisma=6, dex=14, attack=27, defense=32, magic=21, magic_def=23,
                         exp=random.randint(240, 330))
        self.equipment = {'Weapon': items.Claw3(), 'Armor': items.Carapace(), 'OffHand': items.Pincers2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(55, 78)
        self.spellbook = {"Spells": {},
                          "Skills": {'Trip': abilities.Trip(),
                                     'Acid Spit': abilities.AcidSpit()}}
        self.resistance['Holy'] = -0.25
        self.resistance["Poison"] = 1.
        self.resistance['Physical'] = 0.1
        self.status_immunity = ["Poison"]
        self.level.pro_level = 3
        self.picture = "ankheg.txt"


class Fuath(Monster):
    """
    Summoner Boss; must defeat to obtain Fuath summon
    """

    def __init__(self):
        super().__init__(name="Fuath", health=340, mana=147, strength=19, intel=14, wisdom=18, con=14, charisma=11,
                         dex=15, attack=65, defense=46, magic=75, magic_def=82,
                         exp=3000)
        self.equipment = {'Weapon': items.Pincers2(), 'Armor': items.NoArmor(), 'OffHand': items.Pincers2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook = {"Spells": {"Water Jet": abilities.WaterJet(),
                                     "Sleep": abilities.Sleep()},
                          "Skills": {"Screech": abilities.Screech()}}
        self.resistance["Electric"] = -0.75
        self.resistance["Water"] = 1.25
        self.resistance["Shadow"] = 0.25
        self.resistance["Holy"] = -0.25
        self.level.pro_level = 3
        self.picture = "fuath.txt"


class Cockatrice(Monster):
    """
    Level 3 Boss
    """

    def __init__(self):
        super().__init__(name='Cockatrice', health=580, mana=99, strength=30, intel=16, wisdom=15, con=16, charisma=16,
                         dex=22, attack=80, defense=65, magic=72, magic_def=69,
                         exp=3500)
        self.equipment = {'Weapon': items.Claw3(), 'Armor': items.NoArmor(), 'OffHand': items.DragonTail(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 5000
        self.inventory['Pendant'] = [items.random_item(4)]
        self.inventory['Old Key'] = [items.OldKey]
        self.inventory['Feather'] = [items.Feather]
        self.spellbook = {"Spells": {'Petrify': abilities.Petrify()},
                          "Skills": {'Screech': abilities.Screech(),
                                     'Double Strike': abilities.DoubleStrike()}}
        self.flying = True
        self.status_immunity = ["Death", "Stone"]
        self.level.pro_level = 3
        self.sight = True
        self.picture = "cockatrice.txt"


class Wendigo(Fey):
    """
    Level 3 Special Boss - guards third of six relics (HEXAGONUM) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Wendigo', health=750, mana=130, strength=32, intel=16, wisdom=19, con=21, charisma=14,
                         dex=22, attack=92, defense=84, magic=93, magic_def=95,
                         exp=6000)
        self.equipment = {'Weapon': items.Bite2(), 'Armor': items.NoArmor(), 'OffHand': items.DemonClaw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 7500
        self.inventory['Item'] = [items.random_item(5)]
        self.inventory['Old Key'] = [items.OldKey]
        self.spellbook = {"Spells": {"Regen": abilities.Regen2(),
                                     'Terrify': abilities.Terrify(),
                                     "Berserk": abilities.Berserk()},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.flying = True
        self.resistance['Fire'] = -0.75
        self.resistance['Ice'] = 1
        self.resistance["Poison"] = 1
        self.status_immunity = ["Poison", "Death"]
        self.level.pro_level = 4
        self.sight = True
        self.picture = "wendigo.txt"


# Level 4
class BrownSlime(Slime):

    def __init__(self):
        super().__init__(name='Brown Slime', health=random.randint(70, 112), mana=85, strength=17, intel=35, wisdom=40,
                         con=15, charisma=10, dex=8, attack=22, defense=32, magic=55, magic_def=300,
                         exp=random.randint(390, 660))
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
                         con=18, charisma=15, dex=21, attack=33, defense=36, magic=32, magic_def=37,
                         exp=random.randint(410, 530))
        self.equipment = {'Weapon': items.Claw3(), 'Armor': items.StoneArmor(), 'OffHand': items.Claw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(75, 125)
        self.spellbook = {"Spells": {'Blinding Fog': abilities.BlindingFog()},
                          "Skills": {"Piercing Strike": abilities.PiercingStrike()}}
        self.flying = True
        self.resistance["Poison"] = 1
        self.status_immunity = ["Poison", "Stone"]
        self.level.pro_level = 4
        self.picture = "gargoyle.txt"


class Conjurer(Humanoid):

    def __init__(self):
        super().__init__(name='Conjurer', health=random.randint(40, 65), mana=150, strength=14, intel=22, wisdom=18,
                         con=14, charisma=12, dex=13, attack=26, defense=27, magic=50, magic_def=45,
                         exp=random.randint(415, 540))
        self.equipment = {'Weapon': items.RuneStaff(), 'Armor': items.GoldCloak(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(40, 65)
        self.spellbook = {"Spells": {'Fireball': abilities.Fireball(),
                                     "Ice Block": abilities.IceBlock(),
                                     'Lightning': abilities.Lightning(),
                                     'Aqualung': abilities.Aqualung(),
                                     'Boost': abilities.Boost()},
                          "Skills": {"Mana Shield": abilities.ManaShield()}}
        self.level.pro_level = 4
        self.picture = "disciple.txt"


class Chimera(Monster):

    def __init__(self):
        super().__init__(name='Chimera', health=random.randint(60, 95), mana=140, strength=26, intel=14, wisdom=16,
                         con=20, charisma=14, dex=14, attack=38, defense=36, magic=46, magic_def=47,
                         exp=random.randint(430, 580))
        self.equipment = {'Weapon': items.LionPaw(), 'Armor': items.AnimalHide2(), 'OffHand': items.LionPaw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
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
                         con=20, charisma=18, dex=19, attack=39, defense=34, magic=28, magic_def=42,
                         exp=random.randint(450, 680))
        self.equipment = {'Weapon': items.Halberd(), 'Armor': items.Breastplate(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(150, 300)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook = {"Spells": {},
                          "Skills": {"Disarm": abilities.Disarm(),
                                     'Charge': abilities.Charge(),
                                     "Goad": abilities.Goad()}}
        self.flying = True
        self.level.pro_level = 4
        self.picture = "dragonkin.txt"


class Griffin(Monster):

    def __init__(self):
        super().__init__(name='Griffin', health=random.randint(75, 105), mana=110, strength=26, intel=21, wisdom=18,
                         con=18, charisma=16, dex=18, attack=37, defense=39, magic=41, magic_def=37,
                         exp=random.randint(440, 650))
        self.equipment = {'Weapon': items.LionPaw(), 'Armor': items.AnimalHide2(), 'OffHand': items.Claw3(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
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
                         con=14, charisma=22, dex=28, attack=32, defense=30, magic=33, magic_def=30,
                         exp=random.randint(480, 680))
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
                         con=18, charisma=10, dex=14, attack=45, defense=43, magic=39, magic_def=27,
                         exp=random.randint(490, 700))
        self.equipment = {'Weapon': items.Laser(), 'Armor': items.MetalPlating(), 'OffHand': items.ForceField(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(200, 300)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook = {"Spells": {'Shock': abilities.Shock()},
                          "Skills": {}}
        self.resistance['Electric'] = 1.25
        self.resistance['Water'] = -0.75
        self.level.pro_level = 4
        self.picture = "cyborg.txt"

    def special_effects(self, target):
        special_str = ""
        if self.health.current < int(self.health.current * 0.25):
            special_str += abilities.Detonate().use(self, target=target)
        return special_str


class DarkKnight(Fiend):

    def __init__(self):
        super().__init__(name='Dark Knight', health=random.randint(85, 110), mana=60, strength=28, intel=15, wisdom=12,
                         con=21, charisma=14, dex=17, attack=37, defense=45, magic=30, magic_def=29,
                         exp=random.randint(500, 750))
        self.equipment = {'Weapon': items.Flamberge(), 'Armor': items.PlateMail(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(300, 420)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook = {"Spells": {'Enhance Blade': abilities.EnhanceBlade()},
                          "Skills": {'Shield Slam': abilities.ShieldSlam(),
                                     "Disarm": abilities.Disarm(),
                                     'Shield Block': abilities.ShieldBlock()}}
        self.level.pro_level = 4
        self.picture = "darkknight.txt"


class Myrmidon(Elemental):

    def __init__(self):
        super().__init__(name='Myrmidon', health=random.randint(75, 125), mana=75, strength=26, intel=18, wisdom=16,
                         con=18, charisma=10, dex=14, attack=35, defense=36, magic=38, magic_def=34,
                         exp=random.randint(520, 800))
        self.equipment = {'Weapon': items.ElementalBlade(), 'Armor': items.PlateMail(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(300, 450)
        self.inventory['Elemental Mote'] = [items.ElementalMote]
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.resistance["Poison"] = 1
        self.status_immunity = ["Poison"]
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
                         wisdom=14, con=24, charisma=14, dex=26, attack=32, defense=30, magic=29, magic_def=31,
                         exp=random.randint(500, 775))
        self.equipment = {'Weapon': items.Claw3(), 'Armor': items.AnimalHide2(), 'OffHand': items.Tentacle(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
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
                         dex=20, attack=100, defense=88, magic=68, magic_def=82,
                         exp=8000)
        self.equipment = {'Weapon': items.Laser(), 'Armor': items.StoneArmor2(), 'OffHand': items.Laser(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 12000
        self.inventory['Power Core'] = [items.PowerCore]
        self.spellbook = {"Spells": {'Enfeeble': abilities.Enfeeble()},
                          "Skills": {'Crush': abilities.Crush(),
                                     "Goad": abilities.Goad()}}
        self.resistance['Fire'] = 0.5
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
        self.combat = Combat(115, 108, 89, 99)
        self.experience = 12000
        self.equipment = {'Weapon': items.Laser2(), 'Armor': items.StoneArmor2(), 'OffHand': items.ForceField2(),
                          'Ring': items.BarrierRing(), 'Pendant': items.NoPendant()}
        self.inventory['Aard of Being'] = [items.AardBeing]
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook["Skills"]["Triple Strike"] = abilities.TripleStrike()
        self.resistance['Fire'] = 1.0
        self.resistance['Electric'] = -0.25
        self.resistance['Water'] = -0.5
        self.turtled = False  # signifies if enemy has used turtle or not; limited to once a battle


    def special_effects(self, target):
        special_str = ""
        if not self.incapacitated():
            if self.health.current < int(self.health.max * 0.1) and not self.turtle and not self.turtled:
                self.turtle = True
                self.turtled = True
                special_str += f"{self.name} curls up into a ball for protection.\n"
            if self.health.current > int(self.health.max * 0.5) and self.turtle:
                self.turtle = False
                special_str += f"{self.name} stands up into an offensive stance.\n"
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
                         attack=random.randint(0, 100), defense=random.randint(0, 100),
                         magic=random.randint(0, 100), magic_def=random.randint(0, 100),
                         exp=random.randint(15000, 25000))
        self.gold = random.randint(5000, 100000)
        self.equipment = {'Weapon': items.Kukri(), 'Armor': items.StuddedCuirboulli(), 'OffHand': items.Kukri(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.inventory['Item'] = [items.random_item(6)]
        self.inventory['Joker'] = [items.Joker]
        self.spellbook = {"Spells": {"Silence": abilities.Silence(),
                                     "Mirror Image": abilities.MirrorImage2()},
                          "Skills": {'Gold Toss': abilities.GoldToss(),
                                     'Slot Machine': abilities.SlotMachine()}}
        self.resistance = {'Fire': round(random.uniform(-1, 1), 1),
                           'Ice': round(random.uniform(-1, 1), 1),
                           'Electric': round(random.uniform(-1, 1), 1),
                           'Water': round(random.uniform(-1, 1), 1),
                           'Earth': round(random.uniform(-1, 1), 1),
                           'Wind': round(random.uniform(-1, 1), 1),
                           'Shadow': round(random.uniform(-1, 1), 1),
                           'Holy': round(random.uniform(-1, 1), 1),
                           "Poison": round(random.uniform(-1, 1), 1),
                           'Physical': round(random.uniform(-1, 1), 1)}
        self.status_immunity = ["Death", "Stone"]
        self.level.pro_level = 5
        self.sight = True
        self.picture = "jester.txt"

    def special_effects(self, target):
        special_str = "Jester: The wheel of time stops for no one! HAHA!\n"
        special_str += "The Jester's stats and resistances have been randomized.\n"
        self.stats = Stats(strength=random.randint(10, 50),
                           intel=random.randint(10, 50),
                           wisdom=random.randint(10, 50),
                           con=random.randint(10, 60),
                           charisma=self.stats.charisma,
                           dex=random.randint(10, 50))
        self.combat = Combat(attack=random.randint(0, 100),
                             defense=random.randint(0, 100),
                             magic=random.randint(0, 100),
                             magic_def=random.randint(0, 100))
        self.resistance = {'Fire': round(random.uniform(-1, 1), 2),
                           'Ice': round(random.uniform(-1, 1), 2),
                           'Electric': round(random.uniform(-1, 1), 2),
                           'Water': round(random.uniform(-1, 1), 2),
                           'Earth': round(random.uniform(-1, 1), 2),
                           'Wind': round(random.uniform(-1, 1), 2),
                           'Shadow': round(random.uniform(-1, 1), 2),
                           'Holy': round(random.uniform(-1, 1), 2),
                           "Poison": round(random.uniform(-1, 1), 2),
                           'Physical': round(random.uniform(-1, 1), 2)}
        return special_str


# Level 5
class ShadowSerpent(Elemental):

    def __init__(self):
        super().__init__(name='Shadow Serpent', health=random.randint(130, 180), mana=100, strength=28, intel=18,
                         wisdom=15, con=22, charisma=16, dex=23, attack=46, defense=41, magic=46, magic_def=40,
                         exp=random.randint(780, 1090))
        self.equipment = {'Weapon': items.SnakeFang2(), 'Armor': items.SnakeScales2(), 'OffHand': items.SnakeFang2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(280, 485)
        self.inventory['Megalixir'] = [items.Megalixir]
        self.spellbook = {"Spells": {'Corruption': abilities.Corruption()},
                          "Skills": {'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Shadow'] = 0.9
        self.resistance['Holy'] = -0.75
        self.resistance["Poison"] = 0.25
        self.invisible = True
        self.level.pro_level = 5
        self.picture = "snake.txt"


class Aboleth(Slime):

    def __init__(self):
        super().__init__(name='Aboleth', health=random.randint(210, 500), mana=120, strength=25, intel=50, wisdom=50,
                         con=25, charisma=12, dex=10, attack=32, defense=40, magic=65, magic_def=300,
                         exp=random.randint(650, 1230))
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(130, 750)
        self.spellbook = {"Spells": {'Disease Breath': abilities.DiseaseBreath(),
                                     'Enfeeble': abilities.Enfeeble(),
                                     'Boost': abilities.Boost()},
                          "Skills": {'Acid Spit': abilities.AcidSpit()}}
        self.resistance["Poison"] = 1.5
        self.status_immunity = ["Poison"]
        self.level.pro_level = 5


class Beholder(Aberration):

    def __init__(self):
        super().__init__(name='Beholder', health=random.randint(150, 300), mana=100, strength=25, intel=40, wisdom=35,
                         con=28, charisma=20, dex=20, attack=47, defense=45, magic=60, magic_def=55,
                         exp=random.randint(800, 1200))
        self.equipment = {'Weapon': items.Gaze(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(300, 500)
        self.spellbook = {"Spells": {'Magic Missile': abilities.MagicMissile2(),
                                     'Terrify': abilities.Terrify(),
                                     'Dispel': abilities.Dispel(),
                                     'Disintegrate': abilities.Disintegrate()},
                          "Skills": {'Mana Drain': abilities.ManaDrain()}}
        self.flying = True
        self.status_immunity = ["Death"]
        self.level.pro_level = 5
        self.picture = "beholder.txt"


class Behemoth(Aberration):

    def __init__(self):
        super().__init__(name='Behemoth', health=random.randint(200, 300), mana=100, strength=38, intel=25, wisdom=20,
                         con=30, charisma=18, dex=25, attack=58, defense=51, magic=57, magic_def=53,
                         exp=random.randint(920, 1250))
        self.equipment = {'Weapon': items.LionPaw(), 'Armor': items.AnimalHide2(), 'OffHand': items.LionPaw(), 
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(400, 550)
        self.spellbook = {"Spells": {'Holy': abilities.Holy3(),
                                     "Regen": abilities.Regen3(),
                                     "Berserk": abilities.Berserk()},
                          "Skills": {'True Strike': abilities.TrueStrike(),
                                     'Counterspell': abilities.Counterspell()}}
        self.resistance['Fire'] = 1.
        self.resistance['Electric'] = 0.75
        self.resistance['Holy'] = 0.75
        self.resistance["Poison"] = 0.75
        self.resistance['Physical'] = 0.5
        self.status_immunity = ["Death", "Stone"]
        self.level.pro_level = 5
        self.picture = "behemoth.txt"

    def special_effects(self, target):
        special_str = ""
        if not self.is_alive():
            special_str += f"{self.name} unleashes a powerful attack as it dies.\n"
            special_str += abilities.Meteor().cast(self, target=target, special=True)
        return special_str


class Lich(Undead):

    def __init__(self):
        super().__init__(name='Lich', health=random.randint(210, 300), mana=120, strength=25, intel=35, wisdom=40,
                         con=20, charisma=36, dex=22, attack=44, defense=42, magic=63, magic_def=70,
                         exp=random.randint(880, 1220))
        self.equipment = {'Weapon': items.LichHand(), 'Armor': items.WizardRobe(), 'OffHand': items.Necronomicon(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(400, 530)
        self.inventory["Phylactery"] = [items.Phylactery]
        self.spellbook = {"Spells": {'Ice Blizzard': abilities.IceBlizzard(),
                                     'Desoul': abilities.Desoul(),
                                     'Terrify': abilities.Terrify(),
                                     "Ice Block": abilities.IceBlock(),
                                     'Boost': abilities.Boost()},
                          "Skills": {'Health/Mana Drain': abilities.HealthManaDrain()}}
        self.resistance['Ice'] = 0.9
        self.level.pro_level = 5
        self.picture = "lich.txt"


class Basilisk(Monster):

    def __init__(self):
        super().__init__(name='Basilisk', health=random.randint(220, 325), mana=120, strength=29, intel=26, wisdom=30,
                         con=27, charisma=17, dex=20, attack=49, defense=46, magic=51, magic_def=66,
                         exp=random.randint(930, 1200))
        self.equipment = {'Weapon': items.SnakeFang2(), 'Armor': items.SnakeScales2(), 'OffHand': items.SnakeFang2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(380, 520)
        self.spellbook = {"Spells": {'Petrify': abilities.Petrify(),
                                     'Poison Breath': abilities.PoisonBreath()},
                          "Skills": {'Slam': abilities.Slam()}}
        self.resistance["Poison"] = 0.75
        self.status_immunity = ["Death", "Poison", "Stone"]
        self.level.pro_level = 5
        self.picture = "snake.txt"


class MindFlayer(Aberration):
    """
    true sight
    """

    def __init__(self):
        super().__init__(name='Mind Flayer', health=random.randint(190, 285), mana=150, strength=28, intel=40,
                         wisdom=35, con=25, charisma=22, dex=18, attack=42, defense=38, magic=68, magic_def=81,
                         exp=random.randint(890, 1150))
        self.equipment = {'Weapon': items.MithrilshodStaff(), 'Armor': items.WizardRobe(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(450, 600)
        self.spellbook = {"Spells": {"Doom": abilities.Doom(),
                                     'Terrify': abilities.Terrify(),
                                     'Corruption': abilities.Corruption()},
                          "Skills": {'Mana Drain': abilities.ManaDrain()}}
        self.resistance['Shadow'] = 0.5
        self.resistance['Holy'] = -0.25
        self.status_immunity = ["Death"]
        self.level.pro_level = 5
        self.sight = True
        self.picture = "mindflayer.txt"


class Sandworm(Monster):

    def __init__(self):
        super().__init__(name='Sandworm', health=random.randint(230, 300), mana=190, strength=34, intel=21, wisdom=22,
                         con=30, charisma=20, dex=18, attack=56, defense=49, magic=49, magic_def=54,
                         exp=random.randint(910, 1200))
        self.equipment = {'Weapon': items.EarthMaw(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(380, 490)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook = {"Spells": {'Earthquake': abilities.Earthquake(),
                                     'Sandstorm': abilities.Sandstorm()},
                          "Skills": {'Consume Item': abilities.ConsumeItem(),
                                     "Tunnel": abilities.Tunnel()}}
        self.resistance['Electric'] = 0.5
        self.resistance['Water'] = -0.25
        self.resistance['Earth'] = 1
        self.resistance["Poison"] = 1
        self.resistance['Physical'] = 0.5
        self.status_immunity = ["Stone"]
        self.level.pro_level = 5
        self.picture = "naga.txt"


class Warforged(Construct):

    def __init__(self):
        super().__init__(name='Warforged', health=random.randint(230, 300), mana=120, strength=40, intel=20, wisdom=16,
                         con=33, charisma=12, dex=10, attack=66, defense=62, magic=45, magic_def=39,
                         exp=random.randint(880, 1180))
        self.equipment = {'Weapon': items.Cannon(), 'Armor': items.StoneArmor2(), 'OffHand': items.ForceField3(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(380, 490)
        self.inventory['Scrap Metal'] = [items.ScrapMetal]
        self.spellbook = {"Spells": {"Silence": abilities.Silence()},
                          "Skills": {"Crush": abilities.Crush()}}
        self.level.pro_level = 5
        self.picture = "golem.txt"

    def special_effects(self, target):
        special_str = ""
        if not self.incapacitated():
            if self.health.current < int(self.health.max * 0.1) and not self.turtle:
                self.turtle = True
                special_str += f"{self.name} curls up into a ball for protection.\n"
            if self.health.current > int(self.health.max * 0.5) and self.turtle:
                self.turtle = False
                special_str += f"{self.name} stands up into an offensive stance.\n"
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
                         con=28, charisma=22, dex=23, attack=62, defense=53, magic=55, magic_def=59,
                         exp=random.randint(920, 1180))
        self.equipment = {'Weapon': items.DragonTail2(), 'Armor': items.DragonScale(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(650, 830)
        self.spellbook = {'Spells': {'Volcano': abilities.Volcano()},
                          'Skills': {'Triple Strike': abilities.TripleStrike()}}
        self.level.pro_level = 5
        self.picture = "wyrm.txt"


class Hydra(Monster):

    def __init__(self):
        super().__init__(name='Hydra', health=random.randint(260, 375), mana=150, strength=37, intel=30, wisdom=26,
                         con=28, charisma=24, dex=22, attack=60, defense=51, magic=52, magic_def=53,
                         exp=random.randint(900, 1150))
        self.equipment = {'Weapon': items.Bite2(), 'Armor': items.DragonScale(), 'OffHand': items.DragonTail(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(400, 550)
        self.spellbook = {'Spells': {'Tsunami': abilities.Tsunami()},
                          'Skills': {'Double Strike': abilities.DoubleStrike()}}
        self.resistance['Electric'] = -1
        self.resistance['Water'] = 1.5
        self.resistance["Poison"] = 0.75
        self.resistance['Physical'] = 0.25
        self.status_immunity = ["Death", "Stone"]
        self.level.pro_level = 5
        self.picture = "hydra.txt"


class Wyvern(Dragon):

    def __init__(self):
        super().__init__(name='Wyvern', health=random.randint(320, 410), mana=150, strength=35, intel=33, wisdom=24,
                         con=30, charisma=25, dex=40, attack=66, defense=50, magic=50, magic_def=43,
                         exp=random.randint(950, 1200))
        self.equipment = {'Weapon': items.DragonClaw2(), 'Armor': items.DragonScale(), 'OffHand': items.DragonClaw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(420, 570)
        self.spellbook = {"Spells": {'Tornado': abilities.Tornado()},
                          "Skills": {'Piercing Strike': abilities.PiercingStrike()}}
        self.flying = True
        self.level.pro_level = 5
        self.picture = "wyvern.txt"


    def special_attack(self, target):
        return abilities.BreatheFire().use(self, target, typ="Wind")


class Archvile(Fiend):

    def __init__(self):
        super().__init__(name='Archvile', health=random.randint(360, 460), mana=200, strength=32, intel=31, wisdom=35,
                         con=38, charisma=28, dex=32, attack=72, defense=53, magic=52, magic_def=58,
                         exp=random.randint(1010, 1280))
        self.equipment = {'Weapon': items.BattleGauntlet(), 'Armor': items.DemonArmor2(), 'OffHand': items.BattleGauntlet(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(375, 555)
        self.spellbook = {"Spells": {"Sleep": abilities.Sleep(),
                                     'Corruption': abilities.Corruption(),
                                     'Terrify': abilities.Terrify(),
                                     "Regen": abilities.Regen2(),
                                     'Firestorm': abilities.Firestorm()},
                          "Skills": {'Parry': abilities.Parry()}}
        self.resistance['Fire'] = 1.
        self.resistance['Ice'] = 0.5
        self.resistance['Electric'] = 0.5
        self.resistance["Poison"] = 1.
        self.status_immunity.append("Poison")
        self.level.pro_level = 5
        self.picture = "archvile.txt"


class BrainGorger(Aberration):

    def __init__(self):
        super().__init__(name='Brain Gorger', health=random.randint(310, 420), mana=250, strength=27, intel=40,
                         wisdom=35, con=31, charisma=25, dex=36, attack=62, defense=47, magic=70, magic_def=67,
                         exp=random.randint(1050, 1310))
        self.status_effects["Blind"] = StatusEffect(True, -1)
        self.equipment = {'Weapon': items.Claw3(), 'Armor': items.NoArmor(), 'OffHand': items.Claw3(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = random.randint(320, 515)
        self.spellbook = {"Spells": {'Terrify': abilities.Terrify(),
                                     'Weaken Mind': abilities.WeakenMind()},
                          "Skills": {'Brain Gorge': abilities.BrainGorge(),
                                     "Mana Shield": abilities.ManaShield()}}
        self.resistance['Fire'] = 0.25
        self.resistance['Ice'] = 0.25
        self.resistance['Electric'] = 0.25
        self.resistance['Water'] = 0.25
        self.resistance['Earth'] = 0.25
        self.resistance['Wind'] = 0.25
        self.resistance["Poison"] = 1.
        self.status_immunity = ["Poison"]
        self.level.pro_level = 5
        self.picture = "braingorger.txt"


class Domingo(Aberration):
    """
    Level 5 Special Boss - guards fifth of six relics (LUNA) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Domingo', health=1500, mana=999, strength=20, intel=50, wisdom=40, con=45, charisma=60,
                         dex=50, attack=92, defense=123, magic=135, magic_def=119,
                         exp=40000)
        self.equipment = {'Weapon': items.NoWeapon(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 25000
        self.spellbook = {"Spells": {'Ultima': abilities.Ultima(),
                                     'Desoul': abilities.Desoul(),
                                     'Boost': abilities.Boost(),
                                     "Ice Block": abilities.IceBlock()},
                          "Skills": {'Doublecast': abilities.Doublecast(),
                                     "Mana Shield": abilities.ManaShield2()}}
        self.flying = True
        self.resistance = {'Fire': 0.25,
                           'Ice': 0.25,
                           'Electric': 0.25,
                           'Water': 0.25,
                           'Earth': 1.,
                           'Wind': -0.25,
                           'Shadow': 0.25,
                           'Holy': 0.25,
                           "Poison": 0.25,
                           'Physical': 0}
        self.status_immunity = ["Death", "Stone"]
        self.level.pro_level = 5
        self.sight = True
        self.picture = "domingo.txt"


class RedDragon(Dragon):
    """
    Level 5 Boss
    Highly resistant to spells and will heal from fire spells
    """

    def __init__(self):
        super().__init__(name='Red Dragon', health=2000, mana=500, strength=50, intel=38, wisdom=45, con=55,
                         charisma=40, dex=35, attack=135, defense=138, magic=115, magic_def=161,
                         exp=80000)
        self.equipment = {'Weapon': items.DragonTail2(), 'Armor': items.DragonScale(), 'OffHand': items.DragonClaw2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 50000
        self.inventory['Item'] = [items.random_item(7)]
        self.spellbook = {"Spells": {'Heal': abilities.Regen2(),
                                     'Volcano': abilities.Volcano(),
                                     'Ultima': abilities.Ultima()},
                          "Skills": {'Mortal Strike': abilities.MortalStrike2(),
                                     'Doublecast': abilities.Doublecast()}}
        self.flying = True
        self.resistance = {'Fire': 1.5,
                           'Ice': 0.5,
                           'Electric': 0.5,
                           'Water': 0.5,
                           'Earth': 1.,
                           'Wind': -0.25,
                           'Shadow': 0.5,
                           'Holy': 0.5,
                           "Poison": 0.75,
                           'Physical': 0.25}
        self.status_immunity = ["Death", "Poison", "Stone"]
        self.level.pro_level = 5
        self.sight = True
        self.picture = "reddragon.txt"

    def special_attack(self, target):
        return abilities.BreatheFire().use(self, target)


class RedDragon2(RedDragon):
    """
    Transform Level 4 creature
    """

    def __init__(self):
        super().__init__()
        self.stats = Stats(0, 0, 0, 0, 0, 0)
        self.combat = Combat(0, 0, 0, 0)


class Merzhin(Humanoid):
    """
    Breton name for Merlin; Maid of the Spring gives quest to defeat
    Create additional map for wizard's realm
    Can't die in Realm of Cambion, death will return to UndergroundSpring and reset level
    Special map tiles
    - anti-magic field (can't cast spells and/or skills)
    - 
    """

    def __init__(self):
        super().__init__(name="Merzhin", health=1500, mana=2000, strength=24, intel=61, wisdom=58, con=28, charisma=35,
                         dex=32, attack=103, defense=101, magic=140, magic_def=164,
                         exp=90000)
        self.equipment = {"Weapon": items.Khatvanga(), "Armor": items.MerlinRobe(), "OffHand": items.Vedas(),
                          "Ring": items.NoRing(), "Pendant": items.NoPendant()}
        self.gold = 125000
        self.inventory['Codex of Eternity'] = [items.CodexEternity]
        self.inventory['Master Key'] = [items.MasterKey]
        self.spellbook = {"Spells": {"Mirror Image": abilities.MirrorImage2(),
                                     "Magic Missile": abilities.MagicMissile3(),
                                     "Ultima": abilities.Ultima(),
                                     "Disintegrate": abilities.Disintegrate(),
                                     "Boost": abilities.Boost(),
                                     "Ruin": abilities.Ruin()},
                          "Skills": {"Mana Shield": abilities.ManaShield2()}}
        self.status_immunity = ["Death", "Stone"]
        self.level.pro_level = 6


# Final Boss Guard
class Cerberus(Fiend):
    """
    Level 6 Special Boss - guards sixth and final of six relics (INFINITAS) required to beat the final boss
    """

    def __init__(self):
        super().__init__(name='Cerberus', health=2500, mana=500, strength=65, intel=28, wisdom=45, con=60, charisma=40,
                         dex=38, attack=151, defense=142, magic=108, magic_def=132,
                         exp=120000)
        self.equipment = {'Weapon': items.CerberusBite(), 'Armor': items.CerberusHide(), 'OffHand': items.CerberusClaw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.gold = 100000
        self.inventory['Item'] = [items.random_item(8)]
        self.spellbook = {"Spells": {"Regen": abilities.Regen3(),
                                     'Shell': abilities.Shell()},
                          "Skills": {'Triple Strike': abilities.TripleStrike(),
                                     'Trip': abilities.Trip()}}
        self.resistance['Fire'] = 1
        self.resistance['Ice'] = -0.25
        self.resistance['Electric'] = 0.5
        self.resistance['Holy'] = 0.25
        self.resistance['Physical'] = 0.5
        self.status_immunity = ["Death", "Stone"]
        self.level.pro_level = 6
        self.sight = True
        self.picture = "cerberus.txt"


# Final Boss
class Devil(Fiend):
    """
    Final Boss; highly resistant to spells; immune to weapon damage except ultimate weapons
    Aided in combat by his acolyte  TODO
    Choose Fate ability:
     if Attack is chosen, damage mod is increased (increases attack damage and armor)
     if Hellfire is chosen, spell mod is increased (increase magic, healing, and magic defense)
     if Crush is chosen, both damage and spell mod decrease
    """

    def __init__(self):
        super().__init__(name='The Devil', health=5000, mana=1000, strength=75, intel=55, wisdom=70, con=85,
                         charisma=80, dex=45, attack=208, defense=205, magic=194, magic_def=156,
                         exp=0)
        self.equipment = {'Weapon': items.DevilBlade(), 'Armor': items.DevilSkin(), 'OffHand': items.DevilBlade(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook = {"Spells": {'Hellfire': abilities.Hellfire(),
                                     'Terrify': abilities.Terrify(),
                                     "Regen": abilities.Regen3()},
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
                           'Holy': -0.25,
                           "Poison": 1.,
                           'Physical': 1.}
        self.status_immunity = ["Death", "Poison", "Stone"]
        self.damage_mod = 0
        self.spell_mod = 0
        self.level.pro_level = 99
        self.sight = True
        self.picture = "devil.txt"

    def check_mod(self, mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        class_mod = 0
        berserk_per = int(self.status_effects["Berserk"].active) * 0.1  # berserk increases damage by 10%
        if mod == 'weapon':
            weapon_mod = (self.equipment['Weapon'].damage * int(not self.physical_effects["Disarm"].active))
            weapon_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
            total_mod = weapon_mod + class_mod + self.combat.attack
            return max(0, int(total_mod * (1 + berserk_per)))
        if mod == 'offhand':
            off_mod = self.equipment['OffHand'].damage
            class_mod += self.damage_mod
            off_mod += self.stat_effects["Attack"].extra * self.stat_effects["Attack"].active
            return max(0, int((off_mod + class_mod + self.combat.attack) * (0.75 + berserk_per)))
        if mod == 'armor':
            class_mod += self.damage_mod
            armor_mod = self.equipment['Armor'].armor
            armor_mod += self.stat_effects["Defense"].extra * self.stat_effects["Defense"].active
            return max(0, (armor_mod * (not ignore)) + class_mod + self.combat.defense)
        if mod == 'magic':
            magic_mod = int(self.stats.intel // 4) * 10
            class_mod += self.spell_mod
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, magic_mod + class_mod + self.combat.magic)
        if mod == 'magic def':
            m_def_mod = self.stats.wisdom
            class_mod += self.spell_mod
            m_def_mod += self.stat_effects["Magic Defense"].extra * self.stat_effects["Magic Defense"].active
            return max(0, m_def_mod + class_mod + self.combat.magic_def)
        if mod == 'heal':
            class_mod += self.spell_mod
            heal_mod = self.stats.wisdom * self.level.pro_level
            magic_mod += self.stat_effects["Magic"].extra * self.stat_effects["Magic"].active
            return max(0, heal_mod + class_mod + self.combat.magic)
        if mod == 'resist':
            if ultimate and typ == 'Physical':  # ultimate weapons bypass Physical resistance
                return -0.25
            if typ in self.resistance:
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
        if mod == "speed":
            speed_mod = self.stats.dex
            speed_mod += self.stat_effects["Speed"].extra * self.stat_effects["Speed"].active
            return speed_mod
        return 0
