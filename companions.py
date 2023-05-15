# Imports
import time

import spells
from character import Character


class Homunculus(Character):
    """
    Familiar - cast helpful defensive abilities; abilities upgrade when the familiar upgrades
    Level 1: Can use Disarm, Blind, and Stupefy
    Level 2: Gains Cover and bonus to defense
    Level 3: Gains Resurrection
    """

    def __init__(self):
        super().__init__()
        self.race = 'Homunculus'
        self.spellbook = {"Spells": {'Stupefy': spells.Stupefy},
                          "Skills": {'Disarm': spells.Disarm,
                                     'Pocket Sand': spells.PocketSand}}
        self.spec = 'Defense'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; A tiny construct that serves and protects its master from anything that challenges them, regardless of
        the enemy's size or toughness. The {} specializes in defensive abilities, either to prevent direct damage or to
        limit the enemy's ability to deal damage. Choose this familiar if you are a tad bit squishy, or your favorite
        movie is The Bodyguard.
        """.format(self.race)

    def level_up(self):
        print("{} has leveled up!".format(self.name))
        if self.pro_level == 1:
            self.pro_level = 2
            time.sleep(0.5)
            self.spellbook['Skills']['Cover'] = spells.Cover
            print("Specials: Cover")
            time.sleep(0.5)
            print("{} also increases your defense.".format(self.name))
        else:
            self.pro_level = 3
            time.sleep(0.5)
            self.spellbook['Spells']['Resurrection'] = spells.Resurrection
            time.sleep(0.5)
            print("Specials: Resurrection")


class Fairy(Character):
    """
    Familiar - cast helpful support abilities; abilities upgrade when the familiar upgrades
    Level 1: Can cast Heal, Regen, and Bless
    Level 2: Gains Reflect and will randomly restore percentage of mana
    Level 3: Gains Cleanse
    """

    def __init__(self):
        super().__init__()
        self.race = 'Fairy'
        self.spellbook = {"Spells": {'Heal': spells.Heal,
                                     'Regen': spells.Regen,
                                     'Bless': spells.Bless},
                          "Skills": {}}
        self.spec = 'Support'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; These small, flying creatures hail from a parallel plane of existence and are typically associated 
        with a connection to nature. While the {} is not known for its constitution, they more than make up for it 
        with support magics. If you hate having to stock up on potions, this familiar is the one for you!
        """.format(self.race)

    def level_up(self):
        print("{} has leveled up!".format(self.name))
        if self.pro_level == 1:
            self.pro_level = 2
            spell_list = [spells.Reflect, spells.Heal2, spells.Regen2]
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


class Mephit(Character):
    """
    Familiar - cast helpful arcane abilities
    Level 1: Can cast the 3 arcane elementals Firebolt, Ice Lance, and Shock and Magic Missile
    Level 2: Gains Boost and sometimes provides elemental resistance
    Level 3: Gains Ultima
    """

    def __init__(self):
        super().__init__()
        self.race = 'Mephit'
        self.spellbook = {"Spells": {'Firebolt': spells.Firebolt,
                                     'Ice Lance': spells.IceLance,
                                     'Shock': spells.Shock,
                                     'Magic Missile': spells.MagicMissile},
                          "Skills": {}}
        self.spec = 'Arcane'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; A {} is similar to an imp, except this little guy can blast arcane spells. Typically mephits
        embody a single elemental school but these are more Jack-of-all-trades than specialist, even gaining the ability
        to boost its master's magic and magic defense. Who wouldn't want a their very own pocket caster?
        """.format(self.race)

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


class Jinkin(Character):
    """
    Familiar - cast (mostly) helpful luck abilities
    Level 1: Can cast Corruption and use Gold Toss (uses player_char gold) and Steal (items go to player_char inventory)
    Level 2: Gains Enfeeble and will unlock Treasure chests
    Level 3: Gains Slot Machine and will randomly find items at the end of combat
    """

    def __init__(self):
        super().__init__()
        self.race = 'Jinkin'
        self.spellbook = {"Spells": {'Corruption': spells.Corruption},
                          "Skills": {'Gold Toss': spells.GoldToss,
                                     'Steal': spells.Steal}}
        self.spec = 'Luck'
        self.cls = 'Familiar'

    def inspect(self):
        return """
        Familiar; {}s are vindictive little tricksters. While they mostly rely on (their very good) luck, Jinkins 
        also enjoy the occasional curse to really add a thorn to your enemy's paw. You may not always like what you get
        but you also may just love it! (low charisma characters should probably avoid this familiar)...
        """.format(self.race)

    def level_up(self):
        print("{} has leveled up!".format(self.name))
        time.sleep(0.5)
        if self.pro_level == 1:
            self.pro_level = 2
            skill_list = [spells.Enfeeble, spells.Lockpick]
            print_list = []
            for skill in skill_list:
                time.sleep(0.5)
                print_list.append(skill().name)
                self.spellbook['Spells'][skill().name] = skill
            time.sleep(0.5)
            print("Specials: " + ", ".join(print_list))
        else:
            self.pro_level = 3
            print("Specials: " + spells.SlotMachine().name)
            self.spellbook['Skills']['Slot Machine'] = spells.SlotMachine
