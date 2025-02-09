###########################################
""" companion manager """

import random

import abilities
import items
from character import Character, Combat, Resource, Stats


# familiars
class Familiar(Character):
    """
    Base Familiar class
    """

    def __init__(self, name: str, health: Resource, mana: Resource, stats: Stats, combat: Combat):
        super().__init__(name=name, health=health, mana=mana, stats=stats, combat=combat)

    def inspect(self):
        raise NotImplementedError


class Homunculus(Familiar):
    """
    Familiar - cast helpful defensive abilities; abilities upgrade when the familiar upgrades
    Level 1: Can use Disarm, Pocket Sand, and Stupefy
    Level 2: Gains Cover and Goad and bonus to defense
    Level 3: Gains Resurrection
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.race = 'Homunculus'
        self.spellbook = {"Spells": {'Stupefy': abilities.Stupefy()},
                          "Skills": {"Disarm": abilities.Disarm(),
                                     'Pocket Sand': abilities.PocketSand()}}
        self.spec = "Defense"
        self.cls = 'Familiar'

    def inspect(self):
        return (f"A tiny construct that serves and protects its master from anything that challenges them, regardless"
                f" of the enemy's size or toughness. The {self.race} specializes in defensive abilities, either to "
                f"prevent direct damage or to limit the enemy's ability to deal damage. Choose this familiar if you "
                f"are a tad bit squishy, or your favorite movie is The Bodyguard.")

    def level_up(self):
        fam_level_str = f"{self.name} has leveled up!\n"
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            skill_list = [abilities.Cover(), abilities.Goad()]
            for skill in skill_list:
                self.spellbook['Skills'][skill.name] = skill
                fam_level_str += f"{self.name} has gain the ability {skill.name}.\n"
            fam_level_str += f"{self.name} also increases your defense.\n"
        else:
            self.level.pro_level = 3
            self.spellbook['Spells']['Resurrection'] = abilities.Resurrection()
            fam_level_str += f"{self.name} has gain the ability Resurrection.\n"
        return fam_level_str


class Fairy(Familiar):
    """
    Familiar - cast helpful support abilities; abilities upgrade when the familiar upgrades
    Level 1: Can cast Heal, Regen, and Bless
    Level 2: Gains Reflect and will randomly restore percentage of mana
    Level 3: Gains Cleanse
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.race = 'Fairy'
        self.spellbook = {"Spells": {'Heal': abilities.Heal(),
                                     "Regen": abilities.Regen(),
                                     'Bless': abilities.Bless()},
                          "Skills": {}}
        self.spec = 'Support'
        self.cls = 'Familiar'

    def inspect(self):
        return (f"These small, flying creatures hail from a parallel plane of existence and are typically associated"
                f" with a connection to nature. While the {self.race} is not known for its constitution, they more than"
                f" make up for it with support magics. If you hate having to stock up on potions, this familiar is the "
                f"one for you!")

    def level_up(self):
        fam_level_str = f"{self.name} has leveled up!\n"
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            spell_list = [abilities.Reflect(), abilities.Heal2(), abilities.Regen2()]
            for spell in spell_list:
                self.spellbook['Spells'][spell.name] = spell
                fam_level_str += f"{self.name} has gained the ability {spell.name}.\n"
        else:
            self.level.pro_level = 3
            spell_list = [abilities.Cleanse(), abilities.Heal3(), abilities.Regen3()]
            for spell in spell_list:
                self.spellbook['Spells'][spell.name] = spell
                fam_level_str += f"{self.name} has gained the ability {spell.name}.\n"
        return fam_level_str


class Mephit(Familiar):
    """
    Familiar - cast helpful arcane abilities
    Level 1: Can cast the 3 arcane elementals Firebolt, Ice Lance, and Shock and Magic Missile
    Level 2: Gains Boost and sometimes provides elemental resistance
    Level 3: Gains Ultima
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.race = 'Mephit'
        self.spellbook = {"Spells": {'Firebolt': abilities.Firebolt(),
                                     'Ice Lance': abilities.IceLance(),
                                     'Shock': abilities.Shock(),
                                     'Magic Missile': abilities.MagicMissile()},
                          "Skills": {}}
        self.spec = 'Arcane'
        self.cls = 'Familiar'

    def inspect(self):
        return (f"A {self.race} is similar to an imp, except this little guy can blast arcane spells. Typically "
                f"mephits embody a single elemental school but these are more Jack-of-all-trades than specialist, "
                f"even gaining the ability to boost its master's magic and magic defense. Who wouldn't want a their "
                f"very own pocket caster?")

    def level_up(self):
        fam_level_str = f"{self.name} has leveled up!\n"
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            spell_list = [abilities.Fireball(),
                          abilities.Icicle(),
                          abilities.Lightning(),
                          abilities.MagicMissile2(),
                          abilities.Boost()]
            for spell in spell_list:
                self.spellbook['Spells'][spell.name] = spell
                fam_level_str += f"{self.name} has gained the ability {spell.name}.\n"
            fam_level_str += f"{self.name} also increases your magic defense.\n"
        else:
            self.level.pro_level = 3
            spell_list = [abilities.Firestorm(),
                          abilities.IceBlizzard(),
                          abilities.Electrocution(),
                          abilities.MagicMissile3(),
                          abilities.Ultima()]
            for spell in spell_list:
                self.spellbook['Spells'][spell.name] = spell
                fam_level_str += f"{self.name} has gained the ability {spell.name}.\n"
        return fam_level_str


class Jinkin(Familiar):
    """
    Familiar - cast (mostly) helpful luck abilities
    Level 1: Can cast Corruption and use Gold Toss (uses player_char gold) and Steal (items go to player_char inventory)
    Level 2: Gains Enfeeble and will unlock Treasure chests
    Level 3: Gains Slot Machine and will randomly find items at the end of combat
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.race = 'Jinkin'
        self.spellbook = {"Spells": {'Corruption': abilities.Corruption()},
                          "Skills": {'Gold Toss': abilities.GoldToss(),
                                     'Steal': abilities.Steal()}}
        self.spec = 'Luck'
        self.cls = 'Familiar'

    def inspect(self):
        return (f"{self.race}s are vindictive little tricksters. While they mostly rely on (their very good) luck, "
                f"Jinkins also enjoy the occasional curse to really add a thorn to your enemy's paw. You may not always"
                f" like what you get but you also may just love it! (low charisma characters should probably avoid this"
                f" familiar)...")

    def level_up(self):
        fam_level_str = f"{self.name} has leveled up!\n"
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            self.spellbook['Spells']['Enfeeble'] = abilities.Enfeeble()
            fam_level_str += f"{self.name} has gained the ability Enfeeble.\n"
            self.spellbook['Skills']['Lockpick'] = abilities.Lockpick()
            fam_level_str += f"{self.name} has gained the ability Lockpick.\n"
        else:
            self.level.pro_level = 3
            self.spellbook['Skills']['Slot Machine'] = abilities.SlotMachine()
            fam_level_str += f"{self.name} has gained the ability Slot Machine.\n"
        return fam_level_str


# summons
class Summons(Character):
    """
    Base class for summon creature
    Odd number levels result in ability gain (except 10); even levels gain stat(s)
    """

    def __init__(self, name: str, health: Resource, mana: Resource, stats: Stats, combat: Combat):
        super().__init__(name=name, health=health, mana=mana, stats=stats, combat=combat)
        self.start_stats = [0, 0, 0, 0, 0, 0, 0, 0]  # health, mana, str, intel, wis, con, cha, dex
        self.start_combat = [0, 0, 0, 0]  # attack, defense, magic, magic_def
        self.cls = self
        self.exp_scale = 2500
        self.description = ""

    def initialize_stats(self, player_char):
        self.level.exp_to_gain = self.level.pro_level * self.exp_scale
        stat_scale = 25 - self.level.pro_level
        stat_adj = 1 + (((player_char.stats.intel - random.randint(10, 20)) + 
                         (player_char.stats.charisma - random.randint(10, 20))) / stat_scale)
        stats = [int(x * stat_adj) for x in self.start_stats]
        self.health = Resource(stats[0], stats[0])
        self.mana = Resource(stats[1], stats[1])
        self.stats = Stats(*stats[2:])
        combat_stats = [int(x * stat_adj) for x in self.start_combat]
        self.combat = Combat(*combat_stats)

    def level_up(self, player_char):
        self.level.level += 1
        self.level.exp_to_gain += self.level.pro_level * self.exp_scale * self.level.level
        level_str = f"{self.name} gains a level and its power increases.\n"
        total_level = self.level.pro_level * (player_char.level.pro_level - 1)
        stat_scale = (100 - random.randint(0, 10)) // total_level
        stat_adj = 1 + (((player_char.stats.intel + player_char.stats.charisma) / stat_scale))
        self.health.max = int(self.health.max * stat_adj)
        self.mana.max = int(self.mana.max * stat_adj)
        new_combat = [x * stat_adj for x in list(self.combat.__dict__.values())]
        self.combat = Combat(*new_combat)
        for typ in summon_abilities[self.name]:
            if str(self.level.level) in summon_abilities[self.name][typ]:
                ability = summon_abilities[self.name][typ][str(self.level.level)]()
                self.spellbook[typ][ability.name] = ability
                level_str += f"{self.name} gains the ability {ability.name}.\n"
        if self.level.level % 2 == 0:
            chances = [x / sum(self.start_stats[2:]) for x in self.start_stats[2:]]
            new_stats = list(self.stats.__dict__.values())
            for _ in range(total_level):
                ind = random.choices([0, 1, 2, 3, 4, 5], chances)[0]
                new_stats[ind] += 1
            self.stats = Stats(*new_stats)
        return level_str

    def options(self):
        action_list = ["Attack"]
        if not self.status_effects["Silence"].active:
            if self.spellbook["Skills"]:
                action_list.append("Use Skill")
            if self.spellbook["Spells"]:
                action_list.append("Cast Spell")
        action_list.append("Recall")
        return action_list

    def inspect(self):
        inspect_str = f"{self.name} - Level {self.level.level}\n\n"
        inspect_str += self.description
        inspect_str += (f"{'Hit Points:':13}{' ':1}{self.health.current:3}/{self.health.max:>3}\n"
                        f"{'Mana Points:':13}{' ':1}{self.mana.current:3}/{self.mana.max:>3}\n"
                        f"{'Attack:':13}{' ':1}{self.combat.attack:>7}\n"
                        f"{'Defense:':13}{' ':1}{self.combat.defense:>7}\n"
                        f"{'Magic:':13}{' ':1}{self.combat.magic:>7}\n"
                        f"{'Magic Defense:':13}{' ':1}{self.combat.magic_def:>7}\n")
        return inspect_str


class Patagon(Summons):
    """
    Level 1 Summon creature
    Giant mountain man with a giant club; gained when player is promoted to Summoner

    Abilities:
    Level 1 (start)
    - Throw Rock
    - Charge
    Level 3
    - Piercing Strike
    Level 5
    - Stomp
    Level 7
    - Mortal Strike
    Level 9
    - Crush
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Patagon", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 1
        self.start_stats = [125, 85, 20, 5, 8, 15, 3, 14, 75, 40]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.GiantClub(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Skills"]["Throw Rock"] =  abilities.ThrowRock()
        self.spellbook["Skills"]["Charge"] =  abilities.Charge()
        self.resistance['Holy'] = -0.3
        self.resistance["Poison"] = 0.33
        self.resistance['Physical'] = 0.2
        self.description = "A giant mountain man that wields a giant club.\n\n"


class Dilong(Summons):
    """
    Summon creature
    Sandworm; unlocked by retrieving Chiryu Koma item from Xorn enemy and taking it to 1:I17

    Abilities:
    Level 1 (start)
    - Tremor
    - Tunnel
    Level 3
    - Slam
    Level 5
    - Mudslide
    Level 7
    - Consume Item
    Level 9
    - Earthquake
    Level 10
    - Ultimate attack (Devour) TODO
    """

    def __init__(self):
        super().__init__(name="Dilong", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 2
        self.start_stats = [225, 118, 24, 7, 12, 23, 4, 15, 85, 80]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.EarthMaw(), 'Armor': items.SnakeScales2(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Tremor"] = abilities.Tremor()
        self.spellbook["Skills"]["Tunnel"] = abilities.Tunnel()
        self.resistance["Water"] = -0.5
        self.resistance["Earth"] = 1.0
        self.status_immunity = ["Stone"]
        self.description = "A sandworm that can harness the power of the Earth.\n\n"


class Agloolik(Summons):
    """
    Summon creature
    Ice spirit; unlocked after defeating Wendigo

    Abilities:
    Level 1 (start)
    - Ice Lance
    - Piercing Strike
    Level 3
    - Ice Block
    Level 5
    - Icicle
    Level 7
    - True Piercing Strike
    Level 9
    - Ice Blizzard
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Agloolik", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 2
        self.start_stats = [190, 168, 18, 15, 13, 12, 9, 18, 80, 55]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.IceShard(), 'Armor': items.NoArmor(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Ice Lance"] = abilities.IceLance()
        self.spellbook["Skills"]["Piercing Strike"] = abilities.PiercingStrike()
        self.resistance["Fire"] = -0.5
        self.resistance["Ice"] = 1.25
        self.resistance["Physical"] = -0.2
        self.description = "An ice spirit, said to provide aid to fishermen and hunters in the Inuit culture.\n\n"


class Cacus(Summons):
    """
    Summon creature
    Fire breathing monster; unlocked by retrieving Vulcan's Hammer item from Griswold after obtaining the first 2
      relics and taking it to 2:F13

    Abilities:
    Level 1 (start)
    - Scorch
    - Mortal Strike
    Level 3
    - Vulcanize
    Level 5
    - Molten Rock
    Level 7
    - Mortal Strike 2
    Level 9
    - Volcano
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Cacus", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 2
        self.start_stats = [215, 112, 25, 11, 13, 21, 7, 15, 110, 60]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.VulcansHammer(), 'Armor': items.Splint(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Scorch"] = abilities.Scorch()
        self.spellbook["Skills"]["Mortal Strike"] = abilities.MortalStrike()
        self.resistance["Fire"] = 1.0
        self.resistance["Ice"] = -0.75
        self.resistance["Physical"] = 0.2
        self.description = "A fire-breathing monster and the son of the fire god Vulcan.\n\n"


class Fuath(Summons):
    """
    Summon creature
    Malevolent water spirit; unlocked by defeating it at the UndergroundSpring at 3:E10

    Abilities:
    Level 1 (start)
    - Water Jet
    - Screech
    Level 3
    - Terrify
    Level 5
    - Aqualung
    Level 7
    - Weaken Mind
    Level 9
    - Tsunami
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Fuath", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 2
        self.start_stats = [202, 147, 19, 14, 18, 14, 11, 15, 90, 55]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.Pincers2(), 'Armor': items.NoArmor(), 'OffHand': items.Pincers2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"] = abilities.WaterJet()
        self.spellbook["Skills"] = abilities.Screech()
        self.resistance["Electric"] = -0.75
        self.resistance["Water"] = 1.25
        self.resistance["Shadow"] = 0.25
        self.resistance["Holy"] = -0.25
        self.description = "A malevolent water spirit that can drive its victims mad.\n\n"


class Izulu(Summons):
    """
    Summon creature
    Avian, vampiric lightning spirit

    Abilities:
    Level 1 (start)
    - Shock
    - True Strike
    Level 3
    - Berserk
    Level 5
    - Lightning
    Level 7
    - True Piercing Strike
    Level 9
    - Electrocution
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Izulu", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 2
        self.start_stats = [212, 123, 18, 11, 12, 14, 13, 22, 85, 50]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.VampireBite(), 'Armor': items.NoArmor(), 'OffHand': items.VampireBite(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Shock"] = abilities.Shock()
        self.spellbook["Skills"]["True Strike"] = abilities.TrueStrike()
        self.resistance["Electric"] = 1.0
        self.resistance["Water"] = -0.5
        self.resistance["Wind"] = -0.5
        self.resistance["Shadow"] = 0.5
        self.status_immunity = ["Death"]
        self.flying = True
        self.description = "The lightning bird, a vampiric spirit with an insatiable lust for blood.\n\n"


class Hala(Summons):
    """
    Summon creature
    Wind demon

    Abilities:
    Level 1 (start)
    - Parry
    - Gust
    Level 3
    - Double Strike
    Level 5
    - Hurricane
    Level 7
    - Wind Speed
    Level 9
    - Tornado
    Level 10
    - Ultimate attack TODO (Wind Shrapnel/Bullets)
    """

    def __init__(self):
        super().__init__(name="Hala", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 2
        self.start_stats = [224, 109, 20, 12, 9, 15, 10, 24, 105, 65]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.Claw2(), 'Armor': items.DemonArmor(), 'OffHand': items.DemonClaw(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Skills"]["Parry"] = abilities.Parry()
        self.spellbook["Spells"]["Gust"] = abilities.Gust()
        self.resistance["Wind"] = 1.0
        self.resistance["Shadow"] = 0.5
        self.resistance["Holy"] = -1.0
        self.status_immunity = ["Death"]
        self.flying = True
        self.description = "A female demon that can harness the power of the wind for devious purposes.\n\n"


class Grigori(Summons):
    """
    Summon creature
    A angelic spirit known as the Watcher 

    Abilities:
    Level 1 (start)
    - Smite 2
    - Holy 2
    - Shield Slam
    Level 3
    - Divine Protection
    Level 5
    - Regen 2
    Level 7
    - Holy 3
    Level 9
    - Resurrection
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Grigori", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 3
        self.start_stats = [280, 205, 29, 12, 18, 30, 14, 12, 130, 90]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.Pernach(), 'Armor': items.Breastplate(), 'OffHand': items.KiteShield(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Smite"] = abilities.Smite2()
        self.spellbook["Spells"]["Holy"] = abilities.Holy2()
        self.spellbook["Skills"]["Shield Slam"] = abilities.ShieldSlam()
        self.resistance["Shadow"] = -0.25
        self.resistance["Holy"] = 1.25
        self.status_immunity = ["Death"]
        self.flying = True
        self.description = "An angelic spirit, also known as the Watcher, that serves Elysia without question.\n\n"


class Bardi(Summons):
    """
    Summon creature
    death spirit, perhaps modeled after Anima from FFX

    Abilities:
    Level 1 (start)
    - Battle Cry
    - Double Strike
    - Shadow Bolt 2
    - Blinding Fog
    Level 3
    - Corruption
    Level 5
    - Sleeping Powder
    Level 7
    - Ruin
    Level 9
    - Shadow Bolt 3
    Level 10
    - Ultimate attack (Anguish or Oblivion)  TODO
    """

    def __init__(self):
        super().__init__(name="Bardi", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 4
        self.start_stats = [321, 285, 32, 19, 22, 27, 19, 18, 155, 80]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.Scythe(), 'Armor': items.DemonArmor2(), 'OffHand': items.NoOffHand(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Skills"]["Battle Cry"] = abilities.BattleCry()
        self.spellbook["Skills"]["Double Strike"] = abilities.DoubleStrike()
        self.spellbook["Spells"]["Shadow Bolt"] = abilities.ShadowBolt2()
        self.spellbook["Spells"]["Blinding Fog"] = abilities.BlindingFog()
        self.resistance["Shadow"] = 0.25
        self.resistance["Holy"] = -0.5
        self.status_immunity = ["Death"]
        self.description = "An evil spirit, the bringer of Death and darkness.\n\n"


class Kobalos(Summons):
    """
    Summon creature
    Goblin thief/trickster; unlocked once Jester is defeated and Joker obtained
    Chance to turn on user, will either fight or steal and run

    Abilities:
    Level 1 (start)
    - Steal
    - Backstab
    - Pocket Sand
    - Gold Toss
    Level 3
    - Poison Strike
    Level 5
    - Mug
    Level 7
    - Sneak Attack
    Level 9
    - Slot Machine
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Kobalos", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 4
        self.start_stats = [365, 305, 23, 14, 13, 19, 20, 25, 130, 75]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.KoboldDagger(), 'Armor': items.StuddedCuirboulli(),
                          'OffHand': items.KoboldDagger(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Skills"]["Steal"] = abilities.Steal()
        self.spellbook["Skills"]["Backstab"] = abilities.Backstab()
        self.spellbook["Skills"]["Pocket Sand"] = abilities.PocketSand()
        self.spellbook["Skills"]["Gold Toss"] = abilities.GoldToss()
        self.resistance = {'Fire': 0.1,
                           'Ice': 0.1,
                           'Electric': 0.1,
                           'Water': 0.1,
                           'Earth': 0.1,
                           'Wind': 0.1,
                           'Shadow': 0.1,
                           'Holy': 0.0,
                           "Poison": 1.,
                           'Physical': 0.0}
        self.status_immunity.append("Poison")
        self.invisible = True
        self.description = "A filthy little trickster. Watch your back with this guy around.\n\n"


class Zahhak(Summons):
    """
    Summon creature
    Non-elemental red dragon spirit; obtained by beating the Red Dragon
    Has special attack Breathe Fire

    Abilities:
    Level 1 (start)
    - Magic Missile 2
    - Mirror Image
    - Heal 3
    - Reflect
    Level 3
    - Magic Missile 3
    Level 5
    - Ultima
    Level 7
    - Disintegrate
    Level 9
    - Meteor
    Level 10
    - Ultimate attack TODO
    """

    def __init__(self):
        super().__init__(name="Zahhak", health=Resource(), mana=Resource(), stats=Stats(), combat=Combat())
        self.level.pro_level = 5
        self.start_stats = [455, 402, 32, 29, 31, 35, 23, 26, 190, 100]
        self.start_combat = [0, 0, 0, 0]
        self.equipment = {'Weapon': items.DragonClaw2(), 'Armor': items.DragonScale(), 'OffHand': items.DragonTail2(),
                          'Ring': items.NoRing(), 'Pendant': items.NoPendant()}
        self.spellbook["Spells"]["Magic Missile"] = abilities.MagicMissile2()
        self.spellbook["Spells"]["Mirror Image"] = abilities.MirrorImage()
        self.spellbook["Spells"]["Heal"] = abilities.Heal3()
        self.spellbook["Spells"]["Reflect"] = abilities.Reflect()
        self.resistance = {'Fire': 0.25,
                           'Ice': 0.25,
                           'Electric': 0.25,
                           'Water': 0.25,
                           'Earth': 0.25,
                           'Wind': 0.25,
                           'Shadow': 0.25,
                           'Holy': 0.25,
                           "Poison": 1.,
                           'Physical': 0.25}
        self.status_immunity.append("Poison")
        self.description = ""  # TODO

    def special_attack(self, target):
        return abilities.BreatheFire().use(self, target=target)


summon_abilities = {
    "Patagon": {"Skills": {"3": abilities.PiercingStrike,
                           "5": abilities.Stomp,
                           "7": abilities.MortalStrike,
                           "9": abilities.Crush},
                "Spells": {}},
    "Dilong": {"Skills": {"3": abilities.Slam,
                          "7": abilities.ConsumeItem},
               "Spells": {"5": abilities.Mudslide,
                          "9": abilities.Earthquake}},
    "Agloolik": {"Skills": {"7": abilities.TruePiercingStrike},
                 "Spells": {"3": abilities.IceBlock,
                            "5": abilities.Icicle,
                            "9": abilities.IceBlizzard}},
    "Cacus": {"Skills": {"7": abilities.MortalStrike2},
              "Spells": {"3": abilities.Vulcanize,
                         "5": abilities.MoltenRock,
                         "9": abilities.Volcano}},
    "Fuath": {"Skills": {},
              "Spells": {"3": abilities.Terrify,
                         "5": abilities.Aqualung,
                         "7": abilities.WeakenMind,
                         "9": abilities.Tsunami}},
    "Izulu": {"Skills": {"7": abilities.TruePiercingStrike},
              "Spells": {"3": abilities.Berserk,
                         "5": abilities.Lightning,
                         "9": abilities.Electrocution}},
    "Hala": {"Skills": {"3": abilities.DoubleStrike},
              "Spells": {"5": abilities.Hurricane,
                         "7": abilities.WindSpeed,
                         "9": abilities.Tornado}},
    "Grigori": {"Skills": {},
                "Spells": {"3": abilities.DivineProtection,
                           "5": abilities.Regen2,
                           "7": abilities.Holy3,
                           "9": abilities.Resurrection}},
    "Bardi": {"Skills": {"5": abilities.SleepingPowder},
              "Spells": {"3": abilities.Corruption,
                         "7": abilities.Ruin,
                         "9": abilities.ShadowBolt3}},
    "Kobalos": {"Skills": {"3": abilities.PoisonStrike,
                           "5": abilities.Mug,
                           "7": abilities.SneakAttack,
                           "9": abilities.SlotMachine},
                "Spells": {}},
    "Zahhak": {"Skills": {},
               "Spells": {"3": abilities.MagicMissile3,
                          "5": abilities.Ultima,
                          "7": abilities.Disintegrate,
                          "9": abilities.Meteor}}
}
