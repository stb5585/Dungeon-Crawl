"""Player-facing promotion mechanic guidance."""

from __future__ import annotations

PROMOTION_MECHANIC_GUIDANCE: dict[str, str] = {
    "Weapon Master": (
        "Character Menu tab available: Weapon Discipline. Fight with a weapon "
        "type in worthy battles to build its discipline and reveal weapon arts; "
        "Intelligence helps turn practice into insight."
    ),
    "Berserker": (
        "Character Menu tab available: Weapon Discipline. Your weapon training "
        "continues here, carrying ranks and revealed arts forward. Below half "
        "health, weapon hits and incoming damage build Bloodied Momentum for "
        "heavy weapon arts and Final Assault."
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
        "readiness, inherited shield actions, and full-bar Resolve Bursts."
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
        "backlash, Shade of Ahool readiness, and shadow-form pressure during combat."
    ),
    "Demonologist": (
        "Character Menu tab available: Contracts. Use it to review corruption, "
        "patron mood, contracts, and familiar echo identity."
    ),
    "Spellblade": (
        "Blade Charge is shown in combat HUD/status rows and logs. Alternate "
        "any damaging spells with weapon actions to drive the hybrid flow."
    ),
    "Knight Enchanter": (
        "Blade Charge, Foundation, and Accent are shown in combat HUD/status "
        "rows and logs. Cast across spell categories to shape an Enchanted "
        "Assault, Aegis Weave, or Spellbind release."
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
        "discoveries while Revelation and investigation tools expose enemy openings."
    ),
    "Seeker": (
        "Character Menu tab available: Case Journal. Use it to review enemy-type "
        "discoveries while Wayfinding turns hard-won insight into safer routes."
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
        "Ki is shown in combat HUD/status rows and logs. Authored martial hits, "
        "defensive reactions, and meaningful Chi Heal use build up to 3 Ki; five "
        "martial arts automatically spend one Ki while Master Monk advances toward "
        "full-Ki Dim Mak."
    ),
    "Master Monk": (
        "Build 5 Ki to use the 18-MP Dim Mak finisher. Weapon penalties, ordinary "
        "staff disarm, Ruyi Jingu Bang, and Martial Mastery ring cues appear in combat."
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
        "and coda payoff readiness, or open the inherent Compose selector."
    ),
    "Troubadour": (
        "Character Menu tab available: Crescendo. Use it to review song momentum, "
        "repertoire mastery, Encore, coda payoff readiness, and Compose."
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
        "Character Menu tab available: Forms. Purchased nodes unlock persistent "
        "Panther and Direbear forms; dismiss the active form before switching."
    ),
    "Lycan": (
        "Character Menu tab available: Forms. Review persistent Werewolf form, "
        "moon stress, behavior-earned control, Frenzy, and Dragon Essence."
    ),
    "Archdruid": (
        "Character Menu tab available: Aspects. Use it to review nature aspect "
        "identity, Fourfold Balance progression, combat Harmony charges, and "
        "Fourfold Surge readiness."
    ),
    "Diviner": (
        "Character Menu tab available: Runes. Successfully resolved hostile "
        "spells with explicit rank-1 metadata are learned permanently."
    ),
    "Astromancer": (
        "Character Menu tab available: Runes. Review rank-2 witnessed learning, "
        "rune signs, constellation flow, and action-authored Foresight Threads."
    ),
    "Shaman": (
        "Character Menu tab available: Totems. Use it to review active Totem "
        "aspects, elemental communion, and action-earned Resonance."
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
        guidance = guidance[len(mechanic_tab) :].lstrip()
        guidance = guidance.removeprefix(".").lstrip()
    return guidance


def promotion_mechanic_tab_label(new_class_name: str) -> str:
    """Return the Character Menu mechanic tab unlocked by a promoted class."""
    return PROMOTION_MECHANIC_TABS.get(new_class_name, "")


# Classes
