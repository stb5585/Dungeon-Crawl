"""Promotion ability transition rules."""

from __future__ import annotations

from typing import Any

PromotionRule = dict[str, Any]


# Archived promotion transition data retained for external compatibility.
# ================================================================================
# Flat progression does not execute these pruning rules.
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
        "Character Menu tab available: School Affinity. Use it to review the "
        "Elemental or Arcane specialization selected on the Mage tree."
    ),
    "Wizard": (
        "Character Menu tab available: School Affinity. Use it to review "
        "specialization-aware mastery, tier-3 upgrades, and ring acceleration."
    ),
    "Warlock": (
        "Character Menu tab available: Familiar. Use it to review your familiar "
        "as it grows beside you."
    ),
    "Shadowcaster": (
        "Umbral Debt is shown in combat HUD/status rows and logs. Watch debt, "
        "backlash, Eclipse readiness, and shadow-form pressure during combat."
    ),
    "Demonologist": (
        "Character Menu tab available: Contracts. Use it to review corruption, "
        "patron mood, contracts, and familiar echo identity."
    ),
    "Spellblade": (
        "Blade Charge is shown in combat HUD/status rows and logs. Alternate "
        "compatible damage spells with weapon actions to drive the hybrid flow."
    ),
    "Knight Enchanter": (
        "Blade Charge and Arcane Tempo are shown in combat HUD/status rows and "
        "logs. Alternate spells and weapon actions to build burst readiness."
    ),
    "Thief": (
        "Fortune and Misfortune are shown in combat HUD/status rows, logs, and "
        "risky-action results. Use theft, luck, and setup actions to create payoffs."
    ),
    "Rogue": (
        "Fortune, Misfortune, Cheat Death, and Loaded Dice readiness are shown "
        "through combat HUD/status rows, logs, and loot/result messages."
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
        "Death Mark is shown in combat HUD/status rows and logs. Use setup "
        "actions to mark targets, then spend marks through finishers."
    ),
    "Ninja": (
        "Death Mark and No-Trace Opener pressure are shown in combat HUD/status "
        "rows and logs. Use setup actions to mark targets, then spend marks "
        "through finishers."
    ),
    "Spell Stealer": (
        "Stolen spell scrolls are cast from the combat Spells menu. "
        "Stolen Charge remains a combat rhythm, not a Character Menu tab."
    ),
    "Arcane Trickster": (
        "Stolen spell scrolls are cast from the combat Spells menu. "
        "Arcane Larceny and Stolen Charge remain combat rhythms, not a "
        "Character Menu tab."
    ),
    "Cleric": (
        "Build Devotion through holy defender actions for passive protection, "
        "then spend it with Sanctuary Ward when you need a larger ward."
    ),
    "Templar": (
        "Build Devotion through holy defender actions for passive protection, "
        "then spend it with Relic Aegis or Ordered Blessings payoffs when the "
        "front line needs a stronger stand."
    ),
    "Hierophant": (
        "Build Devotion through holy battle-caster actions for passive protection, "
        "then spend it with Consecrated Conduit when a staff or holy payoff is ready."
    ),
    "Monk": (
        "Ki is shown in combat HUD/status rows and logs. Build martial focus "
        "through combat actions, then spend it when Dim Mak is ready."
    ),
    "Master Monk": (
        "Ki, Dim Mak readiness, and Martial Mastery cues are shown in combat "
        "HUD/status rows, logs, skill text, and equipment messages."
    ),
    "Priest": (
        "Prayer is shown in combat HUD/status rows and logs. Build divine "
        "support stacks through meaningful support actions, then spend them "
        "with Supplication."
    ),
    "Archbishop": (
        "Prayer, Benediction readiness, and Divine Intervention cues are shown "
        "in combat HUD/status rows, logs, and support skill text."
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
        "Character Menu tab available: Companion & Hunt. Use it to review your "
        "companion and disciplined quarry tracking."
    ),
    "Conjurer": (
        "Transient companions act independently after the player and dissolve "
        "after 50 exploration steps. They do not gain XP, bond, loot, or roster status."
    ),
    "Thaumaturgist": (
        "Character Menu tab available: Xenids. Use it to review called allies "
        "and their conduit growth through the complete permanent invocation, revival, "
        "and conduit system."
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
        "Character Menu tab available: Companion & Hunt. Use it to review your "
        "tamed companion and Favored Enemy hunt identity."
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
    "Demonologist": "Contracts",
    "Inquisitor": "Case Journal",
    "Seeker": "Case Journal",
    "Bard": "Crescendo",
    "Troubadour": "Crescendo",
    "Beast Master": "Companion & Hunt",
    "Thaumaturgist": "Xenids",
    "Druid": "Forms",
    "Lycan": "Forms",
    "Archdruid": "Aspects",
    "Diviner": "Runes",
    "Astromancer": "Runes",
    "Shaman": "Totems",
    "Soulcatcher": "Totems",
    "Ranger": "Companion & Hunt",
}


def apply_promotion_ability_rules(promoted_player: Any, new_class_name: str) -> str:
    """Compatibility no-op; flat progression retains all learned abilities.

    Args:
        promoted_player: Character object being promoted
        new_class_name: Name of the new class

    Returns:
        An empty string. Ability pruning was retired by flat progression.
    """
    del promoted_player, new_class_name
    return ""


def promotion_mechanic_guidance(new_class_name: str) -> str:
    """Return concise player-facing guidance for a promoted class mechanic."""
    guidance = PROMOTION_MECHANIC_GUIDANCE.get(new_class_name, "")
    return f"{guidance}\n" if guidance else ""


def promotion_mechanic_details(new_class_name: str) -> str:
    """Return mechanic guidance without repeating its Character Menu tab label."""
    guidance = PROMOTION_MECHANIC_GUIDANCE.get(new_class_name, "").strip()
    mechanic_tab = PROMOTION_MECHANIC_TABS.get(new_class_name, "")
    if not guidance or not mechanic_tab:
        return guidance

    guidance = guidance.removeprefix("Character Menu tab available: ").strip()
    if guidance.startswith(mechanic_tab):
        guidance = guidance[len(mechanic_tab):].lstrip()
        guidance = guidance.removeprefix(".").lstrip()
    return guidance


def promotion_mechanic_tab_label(new_class_name: str) -> str:
    """Return the Character Menu mechanic tab unlocked by a promoted class."""
    return PROMOTION_MECHANIC_TABS.get(new_class_name, "")


# Classes
