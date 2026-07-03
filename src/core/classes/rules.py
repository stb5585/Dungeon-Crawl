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
