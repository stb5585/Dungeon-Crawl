###########################################
""" companion manager """

# Imports
import abilities
from character import Character, Resource, Stats


class Homunculus(Character):
    """
    Familiar - cast helpful defensive abilities; abilities upgrade when the familiar upgrades
    Level 1: Can use Disarm, Pocket Sand, and Stupefy
    Level 2: Gains Cover and Goad and bonus to defense
    Level 3: Gains Resurrection
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats())
        self.race = 'Homunculus'
        self.spellbook = {"Spells": {'Stupefy': abilities.Stupefy()},
                          "Skills": {'Disarm': abilities.Disarm(),
                                     'Pocket Sand': abilities.PocketSand()}}
        self.spec = 'Defense'
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


class Fairy(Character):
    """
    Familiar - cast helpful support abilities; abilities upgrade when the familiar upgrades
    Level 1: Can cast Heal, Regen, and Bless
    Level 2: Gains Reflect and will randomly restore percentage of mana
    Level 3: Gains Cleanse
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats())
        self.race = 'Fairy'
        self.spellbook = {"Spells": {'Heal': abilities.Heal(),
                                     'Regen': abilities.Regen(),
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


class Mephit(Character):
    """
    Familiar - cast helpful arcane abilities
    Level 1: Can cast the 3 arcane elementals Firebolt, Ice Lance, and Shock and Magic Missile
    Level 2: Gains Boost and sometimes provides elemental resistance
    Level 3: Gains Ultima
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats())
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


class Jinkin(Character):
    """
    Familiar - cast (mostly) helpful luck abilities
    Level 1: Can cast Corruption and use Gold Toss (uses player_char gold) and Steal (items go to player_char inventory)
    Level 2: Gains Enfeeble and will unlock Treasure chests
    Level 3: Gains Slot Machine and will randomly find items at the end of combat
    """

    def __init__(self):
        super().__init__(name="", health=Resource(), mana=Resource(), stats=Stats())
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
