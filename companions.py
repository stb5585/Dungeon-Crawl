###########################################
""" companion manager """

# Imports
import time

import abilities
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
        self.spellbook = {"Spells": {'Stupefy': abilities.Stupefy},
                          "Skills": {'Disarm': abilities.Disarm,
                                     'Pocket Sand': abilities.PocketSand}}
        self.spec = 'Defense'
        self.cls = 'Familiar'

    def inspect(self):
        return f"""
        Familiar; A tiny construct that serves and protects its master from anything that challenges them, regardless of
        the enemy's size or toughness. The {self.race} specializes in defensive abilities, either to prevent direct 
        damage or to limit the enemy's ability to deal damage. Choose this familiar if you are a tad bit squishy, or 
        your favorite movie is The Bodyguard.
        """

    def level_up(self):
        print(f"{self.name} has leveled up!")
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            time.sleep(0.5)
            self.spellbook['Skills']['Cover'] = abilities.Cover
            print("Specials: Cover")
            time.sleep(0.5)
            print(f"{self.name} also increases your defense.")
        else:
            self.level.pro_level = 3
            time.sleep(0.5)
            self.spellbook['Spells']['Resurrection'] = abilities.Resurrection
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
        self.spellbook = {"Spells": {'Heal': abilities.Heal,
                                     'Regen': abilities.Regen,
                                     'Bless': abilities.Bless},
                          "Skills": {}}
        self.spec = 'Support'
        self.cls = 'Familiar'

    def inspect(self):
        return f"""
        Familiar; These small, flying creatures hail from a parallel plane of existence and are typically associated 
        with a connection to nature. While the {self.race} is not known for its constitution, they more than make up 
        for it with support magics. If you hate having to stock up on potions, this familiar is the one for you!
        """

    def level_up(self):
        print(f"{self.name} has leveled up!")
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            spell_list = [abilities.Reflect, abilities.Heal2, abilities.Regen2]
            print_list = []
            for spell in spell_list:
                time.sleep(0.5)
                print_list.append(spell().name)
                self.spellbook['Spells'][spell().name] = spell
            print("Specials: " + ", ".join(print_list))
        else:
            self.level.pro_level = 3
            spell_list = [abilities.Cleanse, abilities.Heal3, abilities.Regen3]
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
        self.spellbook = {"Spells": {'Firebolt': abilities.Firebolt,
                                     'Ice Lance': abilities.IceLance,
                                     'Shock': abilities.Shock,
                                     'Magic Missile': abilities.MagicMissile},
                          "Skills": {}}
        self.spec = 'Arcane'
        self.cls = 'Familiar'

    def inspect(self):
        return f"""
        Familiar; A {self.race} is similar to an imp, except this little guy can blast arcane spells. Typically mephits
        embody a single elemental school but these are more Jack-of-all-trades than specialist, even gaining the ability
        to boost its master's magic and magic defense. Who wouldn't want a their very own pocket caster?
        """

    def level_up(self):
        print(f"{self.name} has leveled up!")
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            spell_list = [abilities.Fireball, abilities.Icicle, abilities.Lightning, abilities.MagicMissile2, abilities.Boost]
            print_list = []
            for spell in spell_list:
                time.sleep(0.5)
                print_list.append(spell().name)
                self.spellbook['Spells'][spell().name] = spell
            print("Specials: " + ", ".join(print_list))
        else:
            self.level.pro_level = 3
            spell_list = [abilities.Firestorm, abilities.IceBlizzard, abilities.Electrocution,
                          abilities.MagicMissile3, abilities.Ultima]
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
        self.spellbook = {"Spells": {'Corruption': abilities.Corruption},
                          "Skills": {'Gold Toss': abilities.GoldToss,
                                     'Steal': abilities.Steal}}
        self.spec = 'Luck'
        self.cls = 'Familiar'

    def inspect(self):
        return f"""
        Familiar; {self.race}s are vindictive little tricksters. While they mostly rely on (their very good) luck, 
        Jinkins also enjoy the occasional curse to really add a thorn to your enemy's paw. You may not always like what
         you get but you also may just love it! (low charisma characters should probably avoid this familiar)...
        """

    def level_up(self):
        print(f"{self.name} has leveled up!")
        time.sleep(0.5)
        if self.level.pro_level == 1:
            self.level.pro_level = 2
            skill_list = [abilities.Enfeeble, abilities.Lockpick]
            print_list = []
            for skill in skill_list:
                time.sleep(0.5)
                print_list.append(skill().name)
                self.spellbook['Spells'][skill().name] = skill
            time.sleep(0.5)
            print("Specials: " + ", ".join(print_list))
        else:
            self.level.pro_level = 3
            print("Specials: " + abilities.SlotMachine().name)
            self.spellbook['Skills']['Slot Machine'] = abilities.SlotMachine
