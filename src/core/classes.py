###########################################
"""class manager"""

from textwrap import wrap

from . import abilities, items


# Promotion rules: Define ability/spell/skill transitions during class promotion
# ================================================================================
# When characters promote, some classes trade abilities to reflect their new identity.
# This dict defines those transitions in a clear, maintainable way.
# 
# Keys: Target class name (the class being promoted TO)
# 
# Values: Dictionary with the following structure:
#   - clear_spells (bool): If True, wipes all spells and keeps only what's in keep_spells.
#                         If False, keeps all current spells but can remove specific ones.
#   - keep_spells (list): Spells to retain after promotion (only used if clear_spells=True
#                        or for explicit preservation). If spell not in current spellbook,
#                        it will be created from abilities module.
#   - remove_spells (list): Spells to remove from spellbook (only if clear_spells=False).
#   - remove_skills (list): Skills to remove from spellbook.
#   - description (str): Message displayed to player about ability changes.
#
# PROMOTION EXAMPLES:
#   Mage → Warlock: Trades Arcane spells for Shadow spells, keeps only Enfeeble.
#   Mage → Monk: Completely replaces spells with physical abilities (clear all spells).
#   Footpad → Inquisitor: Loses stealth skills, gains investigative skills.
# ================================================================================

PROMOTION_ABILITY_RULES = {
    "Warlock": {
        "clear_spells": False,  # Don't clear all spells
        "keep_spells": ["Enfeeble"],  # Keep only Enfeeble from Mage spells
        "remove_spells": [],  # Warlock gets own spells at level 1
        "remove_skills": [],
        "description": "You lose all previously learned attack spells."
    },
    "Shadowcaster": {
        "clear_spells": False,
        "keep_spells": [],  # Inherits Enfeeble from Warlock, gains Shadowcaster spells
        "remove_spells": [],
        "remove_skills": [],
        "description": ""
    },
    "Monk": {
        "clear_spells": True,  # Clear all spells - Monks use chi, not magic
        "keep_spells": [],
        "remove_spells": [],
        "remove_skills": [],
        "description": "You lose all previously learned spells."
    },
    "Ranger": {
        "clear_spells": True,  # Clear all spells - Rangers use physical abilities
        "keep_spells": [],
        "remove_spells": [],
        "remove_skills": [],
        "description": "You lose all previously learned spells."
    },
    "Weapon Master": {
        "clear_spells": False,
        "keep_spells": [],
        "remove_spells": [],
        "remove_skills": ["Shield Slam"],  # Weapon Masters don't use shields
        "description": "You lose the skill Shield Slam."
    },
    "Inquisitor": {
        "clear_spells": False,
        "keep_spells": [],
        "remove_spells": [],
        "remove_skills": ["Backstab", "Smoke Screen", "Pocket Sand", "Kidney Punch", "Steal", "Sleeping Powder"],
        "description": "You lose all stealth skills."
    },
}


def apply_promotion_ability_rules(promoted_player, new_class_name):
    """Apply ability transition rules for a promotion.
    
    Args:
        promoted_player: Character object being promoted
        new_class_name: Name of the new class
    
    Returns:
        str: Message describing ability changes, or empty string if none
    """
    rules = PROMOTION_ABILITY_RULES.get(new_class_name, {})
    message = ""
    
    if not rules:
        return message
    
    # Handle spell transitions
    if rules.get("clear_spells"):
        promoted_player.spellbook["Spells"] = {}
        if rules.get("description"):
            message += rules["description"] + "\n"
    else:
        # Keep only specified spells
        keep_spells = rules.get("keep_spells", [])
        if keep_spells:
            new_spells = {}
            for spell_name in keep_spells:
                if spell_name in promoted_player.spellbook["Spells"]:
                    new_spells[spell_name] = promoted_player.spellbook["Spells"][spell_name]
                else:
                    # Spell not in current spellbook, create it if it's in the keep list
                    spell_class = getattr(abilities, spell_name, None)
                    if spell_class:
                        new_spells[spell_name] = spell_class()
            promoted_player.spellbook["Spells"] = new_spells
            if rules.get("description"):
                message += rules["description"] + "\n"
        
        # Remove specific spells
        remove_spells = rules.get("remove_spells", [])
        for spell_name in remove_spells:
            if spell_name in promoted_player.spellbook["Spells"]:
                del promoted_player.spellbook["Spells"][spell_name]
    
    # Handle skill transitions
    remove_skills = rules.get("remove_skills", [])
    for skill_name in remove_skills:
        if skill_name in promoted_player.spellbook["Skills"]:
            del promoted_player.spellbook["Skills"][skill_name]
    
    return message


# Classes
class Job:
    """
    Base definition for the class.
    *_plus describe the bonus at first level for each class (5 -> 6 -> 7 gain).
    equipment lists the items the player_char starts out with for the selected class.
    restrictions list the allowable item types the class can equip.
    """

    def __init__(
        self,
        name,
        description,
        str_plus,
        int_plus,
        wis_plus,
        con_plus,
        cha_plus,
        dex_plus,
        att_plus,
        def_plus,
        magic_plus,
        magic_def_plus,
        equipment,
        restrictions,
        pro_level,
    ):
        self.name = name
        self.description = "\n".join(wrap(description, 75, break_on_hyphens=False))
        self.str_plus = str_plus
        self.int_plus = int_plus
        self.wis_plus = wis_plus
        self.con_plus = con_plus
        self.cha_plus = cha_plus
        self.dex_plus = dex_plus
        self.att_plus = att_plus
        self.def_plus = def_plus
        self.magic_plus = magic_plus
        self.magic_def_plus = magic_def_plus
        self.equipment = equipment
        self.restrictions = restrictions
        self.pro_level = pro_level

    def equip_check(self, item, equip_slot):
        """
        Checks if the class allows the item type to be equipped
        """

        item = item if type(item) != type else item()
        if equip_slot in ["Ring", "Pendant"]:
            if item.subtyp == equip_slot:
                return True
            return False
        if item.subtyp in self.restrictions[equip_slot]:
            if item.restriction:
                if self.name not in item.restriction:
                    return False
            return True
        return False


class Warrior(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
                       |
                       -> Paladin       -> Crusader
                       |
                       -> Lancer        -> Dragoon
                       |
                       -> Sentinel      -> Stalwart Defender
    """

    def __init__(self):
        super().__init__(
            name="Warrior",
            description="Warriors are weapon specialists that rely on strength and "
            "defense. While unable to cast spells, they have access to a wide"
            " variety of combat skills that make them deadly in combat. The "
            "most stout of the bass classes, this character is best for "
            "someone who wants to hack and slash their way through the game.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=0,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=1,
            equipment={
                "Weapon": items.Rapier(),
                "OffHand": items.Aspis(),
                "Armor": items.HideArmor(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": [
                    "Dagger",
                    "Sword",
                    "Club",
                    "Longsword",
                    "Battle Axe",
                    "Hammer",
                ],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium", "Heavy"],
            },
            pro_level=1,
        )


class WeaponMaster(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield some one handed weapons; higher dexterity gain
    Cons: Cannot use shields or heavy armor; lower constitution gain
    """

    def __init__(self):
        super().__init__(
            name="Weapon Master",
            description="Weapon Masters focus on the mastery of weapons and their"
            " skill with them. They can equip many weapons and learn "
            "the ability to dual wield one-handed weapons. Since Weapon"
            " Masters really on dexterity, they lose the ability to "
            "wear heavy armor and shields.",
            str_plus=3,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=0,
            dex_plus=2,
            att_plus=4,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=2,
            equipment={
                "Weapon": items.DoubleAxe(),
                "OffHand": items.NoOffHand(),
                "Armor": items.ScaleMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": [
                    "Fist",
                    "Dagger",
                    "Sword",
                    "Club",
                    "Longsword",
                    "Battle Axe",
                    "Hammer",
                ],
                "OffHand": ["Fist", "Dagger", "Sword", "Club"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )


class Berserker(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Additional Pros: Can dual wield 2-handed weapons; additional charisma gain
    Additional Cons: Can only equip light armor
    """

    def __init__(self):
        super().__init__(
            name="Berserker",
            description="Berserkers are combat masters, driven by pure rage and "
            "vengeance. Their strength is so great, they gain the "
            "ability to dual wield two-handed weapons. Their further "
            "reliance on maneuverability limits the type of armor to light "
            "armor.",
            str_plus=3,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=5,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Parashu(),
                "OffHand": items.Changdao(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Longsword", "Battle Axe", "Hammer"],
                "OffHand": ["Longsword", "Battle Axe", "Hammer"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )


class Paladin(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can cast healing spells; additional wisdom and charisma gain
    Cons: Cannot equip 2-handed weapons except hammers and cannot equip light armor; no dex and lower strength gain
    """

    def __init__(self):
        super().__init__(
            name="Paladin",
            description="The Paladin is a holy knight, crusading in the name of good and "
            "order. Gaining some healing and damage spells, paladins become a"
            " more balanced class and are ideal for players who always forget"
            " to restock health potions.",
            str_plus=1,
            int_plus=0,
            wis_plus=2,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.WarHammer(),
                "OffHand": items.Glagwa(),
                "Armor": items.Splint(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Sword", "Club", "Longsword", "Hammer"],
                "OffHand": ["Shield"],
                "Armor": ["Medium", "Heavy"],
            },
            pro_level=2,
        )


class Crusader(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Additional Pros: additional strength gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Crusader",
            description="The Crusader is a holy warrior, who values order and justice "
            "above all else. Crusaders continue the path of the paladin, "
            "fully embracing all aspects that carry over.",
            str_plus=2,
            int_plus=0,
            wis_plus=2,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=3,
            def_plus=3,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Pernach(),
                "OffHand": items.KiteShield(),
                "Armor": items.PlateMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Sword", "Club", "Longsword", "Hammer"],
                "OffHand": ["Shield"],
                "Armor": ["Medium", "Heavy"],
            },
            pro_level=3,
        )


class Lancer(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; charisma gain
    Cons: Cannot equip other 2-handed weapons or dual wield; loses access to light armor
    Special Mechanic: Jump ability takes 2 turns to complete and is guaranteed to hit; during jump, cannot be target of
      melee attacks and gains dodge bonus against magic attacks
    """

    def __init__(self):
        super().__init__(
            name="Lancer",
            description="Lancers are typically more at home on the back of a horse but one"
            " benefit this affords is the skill to wield a two-handed polearm "
            "while also using a shield. They are also adept at leaping high "
            "into the air and driving that polearm into their enemies.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=3,
            magic_plus=0,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Halberd(),
                "OffHand": items.Glagwa(),
                "Armor": items.Splint(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Sword", "Polearm"],
                "OffHand": ["Shield"],
                "Armor": ["Medium", "Heavy"],
            },
            pro_level=2,
        )


class Dragoon(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Additional Pros: additional dex gain
    Additional Cons: Lose access to medium armor
    """

    def __init__(self):
        super().__init__(
            name="Dragoon",
            description="Masters of spears, lances, and polearms and gifted with "
            "supernatural abilities, Dragoons have become legendary for their"
            " grace and power. Their intense training, said to have been "
            "passed down by the dragon riders of old, allows these warriors to"
            " leap unnaturally high into the air and strike their foes with "
            "deadly force from above.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=2,
            att_plus=4,
            def_plus=3,
            magic_plus=0,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Naginata(),
                "OffHand": items.KiteShield(),
                "Armor": items.PlateMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Sword", "Polearm"],
                "OffHand": ["Shield"],
                "Armor": ["Heavy"],
            },
            pro_level=3,
        )


class Sentinel(Job):
    """
    Promotion: Warrior -> Sentinel -> Stalwart Defender
    Pros: increased constitution gain
    Cons: Can only wear heavy armor and cannot equip 2-handed weapons
    """

    def __init__(self):
        super().__init__(
            name="Sentinel",
            description="Masters of defensive tactics, Sentinels excels at enduring "
            "heavy assaults. Equipped with impenetrable shields and an array"
            " of defensive skills, this class specializes in mitigating "
            "damage, taunting enemies, and bolstering the their resilience. "
            "Their unique abilities allow them to a reflect enemy strikes, "
            "and maintain a near-impervious stance against even the fiercest"
            " foes.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=3,
            cha_plus=0,
            dex_plus=1,
            att_plus=1,
            def_plus=4,
            magic_plus=0,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Talwar(),
                "OffHand": items.Glagwa(),
                "Armor": items.Splint(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Heavy"],
            },
            pro_level=2,
        )


class StalwartDefender(Job):
    """
    Promotion: Warrior -> Sentinel -> Stalwart Defender
    Additional Pros: additional constitution gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Stalwart Defender",
            description="The Stalwart Defender embodies unyielding resilience "
            "and unmatched defensive mastery. These protectors are "
            "immovable bastions, capable of absorbing devastating "
            "blows and locking down enemies at will. With "
            "impenetrable defenses and a commanding presence, "
            "they are the epitome of strength and fortitude.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=4,
            cha_plus=0,
            dex_plus=1,
            att_plus=2,
            def_plus=5,
            magic_plus=0,
            magic_def_plus=4,
            equipment={
                "Weapon": items.Shamshir(),
                "OffHand": items.KiteShield(),
                "Armor": items.PlateMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Heavy"],
            },
            pro_level=3,
        )


class Mage(Job):
    """
    Promotion: Mage -> Sorcerer    -> Wizard
                    |
                    -> Warlock     -> Shadowcaster
                    |
                    -> Spellblade  -> Knight Enchanter
                    |
                    -> Summoner    -> Grand Summoner
    """

    def __init__(self):
        super().__init__(
            name="Mage",
            description="Mages possess exceptional aptitude for spell casting, able to "
            "destroy an enemy with the wave of a finger. Weaker and more "
            "vulnerable than any other class, they more than make up for it "
            "with powerful magics.",
            str_plus=0,
            int_plus=3,
            wis_plus=1,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=3,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Quarterstaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.Tunic(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=1,
        )


class Sorcerer(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Earlier access to spells and access to higher level spells
    Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Sorcerer",
            description="A Sorcerer is someone who practices magic derived from "
            "supernatural, occult, or arcane sources. They spend most of "
            "their life reading massive tomes to expand their "
            "knowledge and the rest of the time applying that knowledge at "
            "the expense of anything in their path.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.SerpentStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.GoldCloak(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )


class Wizard(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Additional Pros: Increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Wizard",
            description="The Wizard is a master of arcane magic, unparalleled in their "
            "magical ability. Being able to cast the most powerful spells makes"
            " the wizard an ideal class for anyone who prefers to live fast "
            "and die hard if not properly prepared.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=0,
            cha_plus=1,
            dex_plus=1,
            att_plus=0,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=4,
            equipment={
                "Weapon": items.RuneStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.CloakEnchantment(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


class Warlock(Job):
    """
    Promotion: Mage -> Warlock -> Shadowcaster
    Pros: Higher charisma and constitution gain; access to additional skills; gains access to shadow spells and familiar
    Cons: Lower intelligence gain and limited access to higher level spells; lose access to learned arcane Mage spells
    Special Mechanic: gains familiar that sometimes acts in or out of combat
    """

    def __init__(self):
        super().__init__(
            name="Warlock",
            description="The Warlock specializes in the dark arts, forsaking the arcane "
            "training learned as a Mage. However this focus unlocks powerful "
            "abilities, including the ability to summon a familiar to aid "
            "them.",
            str_plus=0,
            int_plus=2,
            wis_plus=1,
            con_plus=1,
            cha_plus=2,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.ElementalPrimer(),
                "Armor": items.GoldCloak(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )


class Shadowcaster(Job):
    """
    Promotion: Mage -> Warlock -> Shadowcaster
    Additional Pros: Increased wisdom gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Shadowcaster",
            description="The Shadowcaster is highly attuned to the dark arts and can "
            "conjure the most demonic of powers, including the practicing"
            " of forbidden blood magic.",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=1,
            cha_plus=2,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.DragonRouge(),
                "Armor": items.CloakEnchantment(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


class Spellblade(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Pros: Adds melee damage based on mana percentage and level; higher strength and constitution gain; can equip swords
      and light armor
    Cons: Lower intelligence and wisdom gain; cannot equip staves; gains spells at a much slower pace
    """

    def __init__(self):
        super().__init__(
            name="Spellblade",
            description="The Spellblade combines a magical affinity with a higher level"
            " of martial prowess from the other magical classes. While they"
            " no longer gain many of the same arcane spells, the spellblade"
            " has unlocked the ability to channel the learned magical power"
            " through their blade to devastate enemies.",
            str_plus=2,
            int_plus=1,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=3,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Talwar(),
                "OffHand": items.ElementalPrimer(),
                "Armor": items.Cuirboulli(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )


class KnightEnchanter(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Additional Pros: adds armor based on intel and mana percentage; additional dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Knight Enchanter",
            description="The Knight Enchanter uses their arcane powers to imbue"
            " weapons and armor with magical enchantments that can "
            "rival the most powerful fighter.",
            str_plus=2,
            int_plus=1,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=4,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Shamshir(),
                "OffHand": items.DragonRouge(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )


class Summoner(Job):
    """
    Promotion: Mage -> Summoner -> Grand Summoner
    Pros: Increased charisma and dominion over powerful allies
    Cons: No longer gains attack spells and lower intelligence
    Special Mechanic: gains spells from Summon creatures when used enough times  TODO
    """

    def __init__(self):
        super().__init__(
            name="Summoner",
            description="The Summoner has dominion over distant realms, capable of "
            "calling forth powerful creatures to aid them in battle. These "
            "summoned entities range from ferocious beasts to mystical"
            " elementals, each with unique abilities tailored to specific "
            "combat needs. Summoners form bonds with their creatures, "
            "allowing for synergistic strategies and unparalleled "
            "versatility. Highly charismatic individuals will see the "
            "greatest increase in summoning power.",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=0,
            cha_plus=2,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.SerpentStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.GoldCloak(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )


class GrandSummoner(Job):
    """
    Promotion: Mage -> Summoner -> Grand Summoner
    Additional Pros: Summoned creatures have increased power
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Grand Summoner",
            description="The Grand Summoner represents the pinnacle of summoning "
            "mastery, channeling immense magical power to enhance "
            "their summoned creatures. These legendary conjurers can "
            "summon stronger, larger, and more formidable entities "
            "than ever before, each imbued with enhanced abilities and"
            " resilience. The bond between the Grand Summoner and "
            "their creatures is unbreakable, allowing for precise "
            "control and synergy.",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=0,
            cha_plus=3,
            dex_plus=0,
            att_plus=0,
            def_plus=2,
            magic_plus=4,
            magic_def_plus=4,
            equipment={
                "Weapon": items.RuneStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.CloakEnchantment(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


class Footpad(Job):
    """
    Promotion: Footpad -> Thief         -> Rogue
                       |
                       -> Inquisitor    -> Seeker
                       |
                       -> Assassin      -> Ninja
                       |
                       -> Spell Stealer -> Arcane Trickster
    """

    def __init__(self):
        super().__init__(
            name="Footpad",
            description="Footpads are agile and perceptive, with an natural ability of "
            "deftness. While more than capable of holding their own in hand-"
            "to-hand combat, they truly excel at subterfuge. Footpads are the"
            " only base class that can dual wield, albeit the offhand weapon "
            "must be a dagger.",
            str_plus=0,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=2,
            att_plus=2,
            def_plus=1,
            magic_plus=1,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Dirk(),
                "OffHand": items.Dirk(),
                "Armor": items.PaddedArmor(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Sword", "Club"],
                "OffHand": ["Fist", "Dagger"],
                "Armor": ["Light"],
            },
            pro_level=1,
        )


class Thief(Job):
    """
    Promotion: Footpad -> Thief-> Rogue
    Pros: Access to stealth abilities earlier than other classes; gains bonus to damage from dex; increased
        intel gain
    Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Thief",
            description="Thieves prefer stealth over brute force, although a well-placed "
            "backstab is still highly effective. They gain stealth abilities "
            "more quickly than other classes and are typically more well-"
            "balanced.",
            str_plus=0,
            int_plus=1,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=2,
            att_plus=2,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Talwar(),
                "OffHand": items.Kris(),
                "Armor": items.Cuirboulli(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Sword", "Club"],
                "OffHand": ["Fist", "Dagger"],
                "Armor": ["Light"],
            },
            pro_level=2,
        )


class Rogue(Job):
    """
    Promotion: Footpad -> Thief -> Rogue
    Additional Pros: Ability to dual wield swords and maces in offhand; increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Rogue",
            description="Rogues rely on skill, stealth, and their foes' vulnerabilities to "
            "get the upper hand in any situation. They have a knack for finding "
            "the solution to just about any problem, demonstrating a "
            "resourcefulness and versatility that has no rival. They gain the "
            "ability to dual wield swords, maces, and fist weapons.",
            str_plus=0,
            int_plus=1,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=3,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Shamshir(),
                "OffHand": items.Rondel(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Sword", "Club"],
                "OffHand": ["Fist", "Dagger", "Sword", "Club"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )


class Inquisitor(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Pros: Increased strength and constitution gain; ability to perceive enemy status and weaknesses; access to medium
          armor, shields, and some spells; increased resistance to shadow damage
    Cons: Lower dexterity and charisma gain; lose ability to dual wield and stealth skills and access to fist weapons
    """

    def __init__(self):
        super().__init__(
            name="Inquisitor",
            description="Inquisitors exchange the stealth of the shadows for a pure"
            "distain. They excel at rooting out hidden secrets and "
            "unraveling mysteries. They rely on a sharp eye for detail, "
            "but also on a finely honed ability to read the words and "
            "deeds of other creatures to determine their true intent. "
            "They excel at defeating creatures that hide in the shadows "
            " and their mastery of lore and sharp eye make them "
            "well-equipped to expose and end hidden evils.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Talwar(),
                "OffHand": items.Glagwa(),
                "Armor": items.ScaleMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )


class Seeker(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Additional Pros: Additional intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Seeker",
            description="Seekers are very good at moving through the dungeon, being able to"
            " levitate, locate other characters, and teleport. They can't "
            "directly kill monsters with their magical abilities, but a Seeker "
            "does well with a weapon in hand. They are also the best at "
            "mapping the dungeon and detecting any types of 'anomalies' they "
            "may encounter in the depths.",
            str_plus=2,
            int_plus=1,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Shamshir(),
                "OffHand": items.KiteShield(),
                "Armor": items.Breastplate(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=3,
        )


class Assassin(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills; can use fist
      weapons in the offhand slot; gains bonus to damage from dex
    Cons: Lower constitution; can only equip daggers or fist weapons
    """

    def __init__(self):
        super().__init__(
            name="Assassin",
            description="You focus your training on the grim art of death. Those who "
            "adhere to this archetype are diverse: hired killers, spies, "
            "bounty hunters, and even specially anointed priests trained to "
            "exterminate  the enemies of their deity. Stealth, poison, and "
            "disguise help you eliminate your foes with deadly efficiency.",
            str_plus=0,
            int_plus=0,
            wis_plus=1,
            con_plus=0,
            cha_plus=2,
            dex_plus=3,
            att_plus=3,
            def_plus=1,
            magic_plus=1,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.Kris(),
                "Armor": items.Cuirboulli(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger"],
                "OffHand": ["Fist", "Dagger"],
                "Armor": ["Light"],
            },
            pro_level=2,
        )


class Ninja(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Additional Pros: Gains access to class only Ninja Blade weapons
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Ninja",
            description="Since a Ninja desires quickness, they are very specific about the "
            "items they use. Ninjas are not allowed to wear most types of armor "
            "and other items. However, having access to special weapons that "
            "only they can use, Ninjas possess the skills of Critically hitting "
            "and Backstabbing their opponents, along with moderate thieving "
            "skills.",
            str_plus=0,
            int_plus=0,
            wis_plus=2,
            con_plus=0,
            cha_plus=2,
            dex_plus=3,
            att_plus=4,
            def_plus=1,
            magic_plus=1,
            magic_def_plus=4,
            equipment={
                "Weapon": items.Tanto(),
                "OffHand": items.Rondel(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Ninja Blade"],
                "OffHand": ["Fist", "Dagger", "Ninja Blade"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )


class SpellStealer(Job):
    """
    Promotion: Footpad -> Spell Stealer -> Arcane Trickster
    Pros: Intel and wisdom gain; can use Tomes in offhand and can wear cloth armor
    Cons: Lower dex and no constitution gain; lose access to fist and club weapons
    Special Mechanic: can steal magic from enemies  TODO
    """

    def __init__(self):
        super().__init__(
            name="Spell Stealer",
            description="The Spell Stealer is an elite evolution of the Footpad, "
            "blending agility and cunning with mystical talent. Masters"
            " of magical deception, they can cast a variety of spells "
            "while uniquely able to steal magic from enemies. Spells "
            "directed at them may be absorbed or reflected back at "
            "their casters. Their versatility allows them to adapt to "
            "both offensive and defensive situations, disrupting foes' "
            "strategies while empowering themselves with stolen magic.",
            str_plus=0,
            int_plus=2,
            wis_plus=1,
            con_plus=0,
            cha_plus=1,
            dex_plus=2,
            att_plus=1,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.ElementalPrimer(),
                "Armor": items.Cuirboulli(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Dagger", "Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )


class ArcaneTrickster(Job):
    """
    Promotion: Footpad -> Spell Stealer -> Arcane Trickster
    Additional Pros: Increased intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Arcane Trickster",
            description="The Arcane Trickster elevates the Spell Stealer's "
            "cunning and arcane mastery to new heights. Adept at "
            "weaving magic and subterfuge, these versatile "
            "spellcasters manipulate the battlefield with illusions,"
            " stealth, and devastating arcane strikes. Their ability"
            " to enhance their physical attacks with magical force "
            "and cast debilitating spells ensures they are as "
            "dangerous in close quarters as from afar.",
            str_plus=0,
            int_plus=3,
            wis_plus=1,
            con_plus=0,
            cha_plus=1,
            dex_plus=2,
            att_plus=1,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.DragonRouge(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Dagger", "Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )


class Healer(Job):
    """
    Promotion: Healer -> Cleric -> Templar
                      |
                      -> Priest -> Archbishop
                      |
                      -> Monk   -> Master Monk
                      |
                      -> Bard   -> Troubadour

    """

    def __init__(self):
        super().__init__(
            name="Healer",
            description="Healers primary role in battle is to preserve the party with "
            "healing and protective spells. Well, how does that work when "
            "they are alone? Pretty much the same way!",
            str_plus=0,
            int_plus=1,
            wis_plus=2,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Quarterstaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.PaddedArmor(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Shield", "Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=1,
        )


class Cleric(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Pros: Can equip medium armor; gains additional protective abilities including turn undead; increased strength and
        constitution
    Cons: gains fewer healing spells compared to Priest class; no longer gains holy damage spells; lose access to tomes;
        lower intel gain
    """

    def __init__(self):
        super().__init__(
            name="Cleric",
            description="Where the paladin is a warrior that can heal, a cleric is a "
            "healer that can hold their own in combat. The biggest difference"
            " is that the cleric cannot equip heavy armor (yet...) but gain "
            "additional protective abilities that paladins do not.",
            str_plus=1,
            int_plus=0,
            wis_plus=2,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.WarHammer(),
                "OffHand": items.Glagwa(),
                "Armor": items.ScaleMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )


class Templar(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Additional Pros: Can equip heavy armor and hammers; increased strength and dex gain
    Additional Cons: lose access to staff weapons; lower wisdom gain
    """

    def __init__(self):
        super().__init__(
            name="Templar",
            description="A templar exemplifies the best of both worlds, able to heal and"
            " protect while also being able to dish out quite a bit of damage"
            " along the way. While a templar is right at home with a mace and"
            " a shield, they have also trained in the art of the 2-handed "
            "hammer.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Pernach(),
                "OffHand": items.KiteShield(),
                "Armor": items.PlateMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Club", "Hammer"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium", "Heavy"],
            },
            pro_level=3,
        )


class Priest(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Pros: Access to the best healing and holy spells; only class that can equip the holy staff except Archbishop;
        increased intel and wisdom gain
    Cons: Can only equip cloth armor; lose access to shields; lower constitution gain
    """

    def __init__(self):
        super().__init__(
            name="Priest",
            description="A priest channels the holy light through prayer, accessing "
            "powerful regenerative and cleansing spells. While they can only "
            "equip cloth armor, they gain the ability to increase their "
            "defense at the expense of mana.",
            str_plus=0,
            int_plus=2,
            wis_plus=3,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=2,
            magic_plus=3,
            magic_def_plus=3,
            equipment={
                "Weapon": items.SerpentStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.GoldCloak(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )


class Archbishop(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Additional Pros: Only class that can create and equip the Princess Guard; increased intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Archbishop",
            description="An archbishop attunes with the holy light for the most "
            "powerful healing, protective, and holy magics available.",
            str_plus=0,
            int_plus=3,
            wis_plus=3,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=1,
            def_plus=2,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.HolyStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.CloakEnchantment(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


class Monk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Pros: Adds wisdom to damage rolls; gains special skills; increased strength and dex gain
    Cons: Can only wear light armor; loses access to spells; lower intel and wisdom gain
    """

    def __init__(self):
        super().__init__(
            name="Monk",
            description="Monks abandon the cloth to focus the mind into the body, harnessing "
            "the inner power of the chi. Monks specialize in hand-to-hand combat,"
            " adding both strength and wisdom to their melee damage.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Cestus(),
                "OffHand": items.Cestus(),
                "Armor": items.Cuirboulli(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Staff"],
                "OffHand": ["Fist"],
                "Armor": ["Light"],
            },
            pro_level=2,
        )


class MasterMonk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Additional Pros: increased constitution gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Master Monk",
            description="A master monk has fully attuned to the power of the chi, "
            "becoming unparalleled at dealing damage with fists or a "
            "staff.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=4,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=3,
            equipment={
                "Weapon": items.BattleGauntlet(),
                "OffHand": items.BattleGauntlet(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Staff"],
                "OffHand": ["Fist"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )


class Bard(Job):
    """
    Promotion: Healer -> Bard -> Troubadour
    Pros: Gain access to musical instruments, can dual wield daggers; gains songs that have affects in and out of
      combat; increased strength and dex gain
    Cons: Lose access to certain priest spells; lower wisdom gain
    Special Mechanic: Plays songs that boost self, hurt foes, or affects actions out of combat  TODO
    """

    def __init__(self):
        super().__init__(
            name="Bard",
            description="The Bard is a master of performance and inspiration, blending "
            "healing arts with the power of music and storytelling. They can "
            "weave enchanting melodies to bolster their own strength, restore "
            "health, and demoralize enemies. Bards excel at turning the tide of "
            "battle through clever improvisation, crowd control, and "
            "spellcasting.",
            str_plus=1,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=1,
            def_plus=1,
            magic_plus=3,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.Lute(),
                "Armor": items.Cuirboulli(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword", "Staff"],
                "OffHand": ["Dagger", "Musical Instrument"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )


class Troubadour(Job):
    """
    Promotion: Healer -> Bard -> Troubadour
    Additional Pros: Increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Troubadour",
            description="The Troubadour is the pinnacle of the Bard's art, a legendary"
            " performer who wields songs and stories with unmatched "
            "mastery. Their melodies amplify their abilities, granting "
            "powerful buffs and healing over time, while their sharp wit "
            "and magical harmonies sow discord among foes. They are "
            "paragons of charisma, seamlessly blending support, "
            "enchantment, and clever combat tricks to uplift their "
            "companions and ensure victory through the power of "
            "performance.",
            str_plus=1,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=1,
            def_plus=2,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.Lyre(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword", "Staff"],
                "OffHand": ["Dagger", "Musical Instrument"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )


class Pathfinder(Job):
    """
    Promotion: Pathfinder -> Druid   -> Lycan
                          |
                          -> Diviner -> Geomancer
                          |
                          -> Shaman  -> Soulcatcher
                          |
                          -> Ranger  -> Beast Master
    """

    def __init__(self):
        super().__init__(
            name="Pathfinder",
            description="In philosophy, naturalism is the belief that only natural laws"
            " and forces operate in the universe. A pathfinder embraces "
            "this idea by being attuned to one or more of the various "
            "aspects of nature, mainly the 4 classical elements: Earth, "
            "Wind, Water, and Fire.",
            str_plus=0,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=1,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Dirk(),
                "OffHand": items.Buckler(),
                "Armor": items.HideArmor(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Club", "Polearm", "Hammer", "Staff"],
                "OffHand": ["Shield", "Tome"],
                "Armor": ["Cloth", "Light", "Medium"],
            },
            pro_level=1,
        )


class Druid(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Pros: gains animal abilities and statistics when shifted; increased strength and dex gain
    Cons: loses ability to wear medium armor and shields; lower intel gain
    """

    def __init__(self):
        super().__init__(
            name="Druid",
            description="Druids act as an extension of nature to call upon the elemental"
            " forces, embodying nature's wrath and mystique. This attunement "
            "with nature allows druids to emulate creatures of the animal world,"
            " transforming into them and gaining there specs and abilities. They"
            " lose the ability to wear medium armor and shields but gain "
            "natural weapons and armor when transformed.",
            str_plus=1,
            int_plus=0,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.SerpentStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.Cuirboulli(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Club", "Polearm", "Hammer", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )


class Lycan(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Additional Pros: Can learn to transform into Red Dragon; increased constitution gain
    Additional Cons: None
    Special Mechanic: Can shapeshift into alternative forms
    """

    def __init__(self):
        super().__init__(
            name="Lycan",
            description="Unlike the lycans of mythology who have little choice in morphing "
            "into their animal form, these lycans have gained mastery over their"
            " powers to become something truly terrifying.",
            str_plus=1,
            int_plus=0,
            wis_plus=1,
            con_plus=2,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Maul(),
                "OffHand": items.NoOffHand(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Club", "Polearm", "Hammer", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )


class Diviner(Job):
    """
    Promotion: Pathfinder -> Diviner -> Geomancer
    Pros: can learn rank 1 enemy specials when cast against; increased intel and wisdom gain
    Cons: loses access to shields and some weapon choices; lower dex gain
    """

    def __init__(self):
        super().__init__(
            name="Diviner",
            description="A diviner works with nature to balance the four classical "
            "elements of Earth, Wind, Water, and Fire, and can learn certain "
            "spells cast against them within these domains. Diviners are also "
            "hyper aware of their surroundings, limiting the effect of traps "
            "and magic effects.",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.ElementalPrimer(),
                "Armor": items.GoldCloak(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome", "Rod"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )


class Geomancer(Job):
    """
    Promotion: Pathfinder -> Diviner -> Geomancer
    Additional Pros: can learn rank 2 enemy specials when cast against; increased intel gain
    Additional Cons: None
    Special Mechanic: similar to a Blue Mage, gains spells from enemy use
    """

    def __init__(self):
        super().__init__(
            name="Geomancer",
            description="Classified as one of the 7 forbidden arts, geomancers have "
            "mastered natural phenomena, granting them access to some of the"
            " most devastating elemental spells. Their adeptness with "
            "magical effects allow geomancers to manipulate special tiles to"
            " their advantage.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=4,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.DragonRouge(),
                "Armor": items.CloakEnchantment(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome", "Rod"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


class Shaman(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Pros: Can dual wield fist weapons; can imbue weapons with elemental fury; increased strength and dex gain
    Cons: Loses access to cloth armor, tomes, and some weapons; lower intel gain
    """

    def __init__(self):
        super().__init__(
            name="Shaman",
            description="The Shaman is a master of the natural elements, channeling the "
            "raw forces of fire, water, earth, and air to devastate their "
            "enemies. By imbuing weapons with elemental fury, they transform "
            "mundane strikes into catastrophic blows. As warriors of nature, "
            "they bring balance to the battlefield, wielding power both "
            "destructive and enhancing.",
            str_plus=1,
            int_plus=0,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Cestus(),
                "OffHand": items.Cestus(),
                "Armor": items.ScaleMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Club", "Staff"],
                "OffHand": ["Fist", "Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )


class Soulcatcher(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Additional Pros: Chance to gain essence from enemies; increased strength gain
    Additional Cons: None
    Special Mechanic: gains power based on enemies slain
    """

    def __init__(self):
        super().__init__(
            name="Soulcatcher",
            description="The Soulcatcher is a mystic who has mastered the art of "
            "binding spirits and harnessing their power. As a promotion "
            "of the Shaman, they wield unparalleled control over "
            "elemental and spiritual energies, weaving them into "
            "devastating attacks or protective barriers. By capturing the"
            " essence of defeated foes, the Soulcatcher can unleash "
            "soul-charged magic upon enemies. Their deep connection to "
            "the spirit world grants them unique insight and power, "
            "making them both revered and feared on the battlefield.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.BattleGauntlet(),
                "OffHand": items.BattleGauntlet(),
                "Armor": items.Breastplate(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Club", "Staff"],
                "OffHand": ["Fist", "Shields"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=3,
        )


class Ranger(Job):
    """
    Promotion: Pathfinder -> Ranger -> Beast Master
    Pros: Increased strength and dex gain; gain dual wielding with daggers; can use swords and 2-handed axes
    Cons: Lose access to attack spells, some weapons and armor, shields, and tomes
    Special Mechanic: can tame a beast to aid in and out of combat; companion strength affected by charisma
    """

    def __init__(self):
        super().__init__(
            name="Ranger",
            description="Rangers blend their deep wilderness expertise with fierce melee "
            "combat capabilities. Skilled in tracking and survival, they excel"
            " in close-quarters combat using precision and agility. Their true"
            " strength lies in their ability to tame and command powerful "
            "animals, forging bonds with beasts to fight alongside them. "
            "Rangers leverage their primal connection to nature and combat "
            "mastery, creating a formidable duo of human and beast.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Talwar(),
                "OffHand": items.Kris(),
                "Armor": items.ScaleMail(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword", "Longsword", "Battle Axe", "Polearm"],
                "OffHand": ["Dagger"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )


class BeastMaster(Job):
    """
    Promotion: Pathfinder -> Ranger -> Beast Master
    Additional Pros: Increased charisma gain; increased companion strength from charisma
    Additional Cons: Lose access to medium armor
    """

    def __init__(self):
        super().__init__(
            name="Beast Master",
            description="The Beast Master is the pinnacle of the Ranger's journey, "
            "embodying an unbreakable bond with the wild. Beast Masters "
            "thrive in harmony with their companion, fighting as one "
            "unified force. With heightened instincts and the ability "
            "to channel primal energy, they inspire and protect their "
            "allies, making them guardians of the natural world and "
            "champions of untamed strength.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=2,
            att_plus=4,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Shamshir(),
                "OffHand": items.Rondel(),
                "Armor": items.StuddedLeather(),
                "Pendant": items.NoPendant(),
                "Ring": items.NoRing(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword", "Longsword", "Battle Axe", "Polearm"],
                "OffHand": ["Dagger"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )


# dataclass dictionaries
classes_dict = {
    "Warrior": {
        "class": Warrior,
        "pro": {
            "Weapon Master": {
                "class": WeaponMaster,
                "pro": {"Berserker": {"class": Berserker}},
            },
            "Paladin": {"class": Paladin, "pro": {"Crusader": {"class": Crusader}}},
            "Lancer": {"class": Lancer, "pro": {"Dragoon": {"class": Dragoon}}},
            "Sentinel": {
                "class": Sentinel,
                "pro": {"Stalwart Defender": {"class": StalwartDefender}},
            },
        },
    },
    "Mage": {
        "class": Mage,
        "pro": {
            "Sorcerer": {"class": Sorcerer, "pro": {"Wizard": {"class": Wizard}}},
            "Warlock": {
                "class": Warlock,
                "pro": {"Shadowcaster": {"class": Shadowcaster}},
            },
            "Spellblade": {
                "class": Spellblade,
                "pro": {"Knight Enchanter": {"class": KnightEnchanter}},
            },
            "Summoner": {
                "class": Summoner,
                "pro": {"Grand Summoner": {"class": GrandSummoner}},
            },
        },
    },
    "Footpad": {
        "class": Footpad,
        "pro": {
            "Thief": {"class": Thief, "pro": {"Rogue": {"class": Rogue}}},
            "Inquisitor": {"class": Inquisitor, "pro": {"Seeker": {"class": Seeker}}},
            "Assassin": {"class": Assassin, "pro": {"Ninja": {"class": Ninja}}},
            "Spell Stealer": {
                "class": SpellStealer,
                "pro": {"Arcane Trickster": {"class": ArcaneTrickster}},
            },
        },
    },
    "Healer": {
        "class": Healer,
        "pro": {
            "Cleric": {"class": Cleric, "pro": {"Templar": {"class": Templar}}},
            "Monk": {"class": Monk, "pro": {"Master Monk": {"class": MasterMonk}}},
            "Priest": {"class": Priest, "pro": {"Archbishop": {"class": Archbishop}}},
            "Bard": {"class": Bard, "pro": {"Troubadour": {"class": Troubadour}}},
        },
    },
    "Pathfinder": {
        "class": Pathfinder,
        "pro": {
            "Druid": {"class": Druid, "pro": {"Lycan": {"class": Lycan}}},
            "Diviner": {"class": Diviner, "pro": {"Geomancer": {"class": Geomancer}}},
            "Shaman": {"class": Shaman, "pro": {"Soulcatcher": {"class": Soulcatcher}}},
            "Ranger": {
                "class": Ranger,
                "pro": {"Beast Master": {"class": BeastMaster}},
            },
        },
    },
}
