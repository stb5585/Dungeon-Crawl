"""Promotion ability transition rules."""

from __future__ import annotations

from typing import Any

from .. import abilities


PromotionRule = dict[str, Any]


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

PROMOTION_ABILITY_RULES: dict[str, PromotionRule] = {
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


PROMOTION_MECHANIC_GUIDANCE: dict[str, str] = {
    "Weapon Master": (
        "Character Menu tab available: Weapon Discipline. Fight with a weapon "
        "type in worthy battles to build its discipline and reveal weapon arts; "
        "Intelligence helps turn practice into insight."
    ),
    "Berserker": (
        "Character Menu tab available: Weapon Discipline. Your weapon training "
        "continues here, carrying ranks and revealed arts forward."
    ),
    "Grandmaster of Arms": (
        "Character Menu tab available: Weapon Discipline. Your weapon training "
        "continues here, carrying ranks and revealed arts forward."
    ),
    "Paladin": (
        "Character Menu tab available: Oath Conviction. Use it to review your "
        "sworn vow, conviction meter, and vow-aligned combat rhythm."
    ),
    "Crusader": (
        "Character Menu tab available: Oath Conviction. Use it to review your "
        "sworn vow, conviction meter, and vow-aligned combat rhythm."
    ),
    "Lancer": (
        "Character Menu tab available: Aerial Tempo. Use it to review Jump "
        "follow-through readiness and polearm combat flow."
    ),
    "Dragoon": (
        "Character Menu tab available: Aerial Tempo. Use it to review Jump "
        "follow-through readiness, landing shields, and polearm combat flow."
    ),
    "Sentinel": (
        "Character Menu tab available: Resolve. Use it to review shield guard "
        "readiness, Hold the Line pressure, and Resolve-spending shield actions."
    ),
    "Stalwart Defender": (
        "Character Menu tab available: Resolve. Use it to review shield guard "
        "readiness, inherited shield actions, and full-bar Resolve Surges."
    ),
    "Sorcerer": (
        "Character Menu tab available: School Affinity. Use it to review six-school "
        "affinity growth and tier-2 elemental upgrade progress."
    ),
    "Wizard": (
        "Character Menu tab available: School Affinity. Use it to review six-school "
        "affinity mastery, tier-3 upgrades, and Wizard ring acceleration."
    ),
    "Warlock": (
        "Character Menu tab available: Familiar. Use it to review your familiar "
        "as it grows beside you."
    ),
    "Shadowcaster": (
        "Character Menu tab available: Umbral Debt. Use it to review debt, "
        "backlash, Eclipse readiness, and shadow-form pressure."
    ),
    "Demonologist": (
        "Character Menu tab available: Contracts. Use it to review corruption, "
        "patron mood, contracts, and familiar echo identity."
    ),
    "Spellblade": (
        "Character Menu tab available: Blade Charge. Use it to review spell-to-blade "
        "charge readiness and hybrid combat flow."
    ),
    "Knight Enchanter": (
        "Character Menu tab available: Arcane Tempo. Use it to review blade charge, "
        "Arcane Tempo stacks, and burst readiness."
    ),
    "Thief": (
        "Character Menu tab available: Fortune. Use it to review Fortune, "
        "Misfortune, and risky-action payoff readiness."
    ),
    "Rogue": (
        "Character Menu tab available: Fortune. Use it to review Fortune, "
        "Misfortune, Cheat Death, and Loaded Dice payoff readiness."
    ),
    "Inquisitor": (
        "Character Menu tab available: Case Journal. Use it to review enemy-type "
        "evidence, Revelation stacks, and open investigation counterplay."
    ),
    "Seeker": (
        "Character Menu tab available: Case Journal. Use it to review enemy-type "
        "evidence, Revelation stacks, and Wayfinding progress."
    ),
    "Assassin": (
        "Character Menu tab available: Death Mark. Use it to review mark setup "
        "and finisher readiness."
    ),
    "Ninja": (
        "Character Menu tab available: Death Mark. Use it to review mark setup, "
        "finisher readiness, and No-Trace Opener pressure."
    ),
    "Spell Stealer": (
        "Character Menu tab available: Stolen Charge. Use it to review stolen "
        "spell charge and magical theft payoff readiness."
    ),
    "Arcane Trickster": (
        "Character Menu tab available: Stolen Charge. Use it to review stolen "
        "spell charge, Arcane Larceny, and hybrid payoff readiness."
    ),
    "Cleric": (
        "Character Menu tab available: Devotion. Use it to review holy defender "
        "stacks, Sanctuary Ward readiness, and shield-support rhythm."
    ),
    "Templar": (
        "Character Menu tab available: Devotion. Use it to review holy defender "
        "stacks, Relic Aegis readiness, and Ordered Blessings."
    ),
    "Monk": (
        "Character Menu tab available: Ki. Use it to review martial focus, Ki "
        "stacks, and Dim Mak readiness."
    ),
    "Master Monk": (
        "Character Menu tab available: Ki. Use it to review martial focus, Ki "
        "stacks, Dim Mak readiness, and Martial Mastery."
    ),
    "Priest": (
        "Character Menu tab available: Prayer. Use it to review divine support "
        "stacks and Supplication readiness."
    ),
    "Archbishop": (
        "Character Menu tab available: Prayer. Use it to review divine support "
        "stacks, Benediction readiness, and Divine Intervention."
    ),
    "Bard": (
        "Character Menu tab available: Crescendo. Use it to review song momentum "
        "and coda payoff readiness."
    ),
    "Troubadour": (
        "Character Menu tab available: Crescendo. Use it to review song momentum, "
        "repertoire mastery, Encore, and coda payoff readiness."
    ),
    "Beast Master": (
        "Character Menu tab available: Companion. Use it to review your companion "
        "as it grows beside you."
    ),
    "Summoner": (
        "Character Menu tab available: Summons. Use it to review summoned allies "
        "and their bond growth as they fight beside you."
    ),
    "Grand Summoner": (
        "Character Menu tab available: Summons. Use it to review summoned allies "
        "and their bond growth as they fight beside you."
    ),
    "Druid": (
        "Character Menu tab available: Forms. Use it to review stable wild-shape "
        "identity and nature-form progression as it unlocks."
    ),
    "Lycan": (
        "Character Menu tab available: Forms. Use it to review moon form, control, "
        "and transformation pressure."
    ),
    "Archdruid": (
        "Character Menu tab available: Aspects. Use it to review nature aspect "
        "identity and Fourfold Balance progression."
    ),
    "Diviner": (
        "Character Menu tab available: Runes. Use it to review learned-spell "
        "runes and elemental casting identity."
    ),
    "Astromancer": (
        "Character Menu tab available: Runes. Use it to review rune signs, "
        "constellation flow, and Foresight Threads."
    ),
    "Shaman": (
        "Character Menu tab available: Totems. Use it to review active Totem "
        "aspects and elemental communion."
    ),
    "Soulcatcher": (
        "Character Menu tab available: Totems. Use it to review Totem Resonance, "
        "Soul Aspect, and harvest scaling."
    ),
    "Ranger": (
        "Character Menu tab available: Companion. Use it to review your tamed "
        "companion and Favored Enemy hunt identity."
    ),
}


PROMOTION_MECHANIC_TABS: dict[str, str] = {
    "Weapon Master": "Weapon Discipline",
    "Berserker": "Weapon Discipline",
    "Grandmaster of Arms": "Weapon Discipline",
    "Paladin": "Oath Conviction",
    "Crusader": "Oath Conviction",
    "Lancer": "Aerial Tempo",
    "Dragoon": "Aerial Tempo",
    "Sentinel": "Resolve",
    "Stalwart Defender": "Resolve",
    "Sorcerer": "School Affinity",
    "Wizard": "School Affinity",
    "Warlock": "Familiar",
    "Shadowcaster": "Umbral Debt",
    "Demonologist": "Contracts",
    "Spellblade": "Blade Charge",
    "Knight Enchanter": "Arcane Tempo",
    "Thief": "Fortune",
    "Rogue": "Fortune",
    "Inquisitor": "Case Journal",
    "Seeker": "Case Journal",
    "Assassin": "Death Mark",
    "Ninja": "Death Mark",
    "Spell Stealer": "Stolen Charge",
    "Arcane Trickster": "Stolen Charge",
    "Cleric": "Devotion",
    "Templar": "Devotion",
    "Monk": "Ki",
    "Master Monk": "Ki",
    "Priest": "Prayer",
    "Archbishop": "Prayer",
    "Bard": "Crescendo",
    "Troubadour": "Crescendo",
    "Beast Master": "Companion",
    "Summoner": "Summons",
    "Grand Summoner": "Summons",
    "Druid": "Forms",
    "Lycan": "Forms",
    "Archdruid": "Aspects",
    "Diviner": "Runes",
    "Astromancer": "Runes",
    "Shaman": "Totems",
    "Soulcatcher": "Totems",
    "Ranger": "Companion",
}


def apply_promotion_ability_rules(promoted_player: Any, new_class_name: str) -> str:
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


def promotion_mechanic_guidance(new_class_name: str) -> str:
    """Return concise player-facing guidance for a promoted class mechanic."""
    guidance = PROMOTION_MECHANIC_GUIDANCE.get(new_class_name, "")
    return f"{guidance}\n" if guidance else ""


def promotion_mechanic_tab_label(new_class_name: str) -> str:
    """Return the Character Menu mechanic tab unlocked by a promoted class."""
    return PROMOTION_MECHANIC_TABS.get(new_class_name, "")


def grant_summoner_initial_summon(promoted_player: Any) -> str:
    """Grant Patagon, the starting summon for new Summoners."""
    from .. import companions

    summons = getattr(promoted_player, "summons", None)
    if summons is None:
        summons = {}
        promoted_player.summons = summons
    if "Patagon" in summons:
        return ""

    summon = companions.Patagon()
    summon.initialize_stats(promoted_player)
    summons[summon.name] = summon
    return "You have gained the summon Patagon.\n"


# Classes
