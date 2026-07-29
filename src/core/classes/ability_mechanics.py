"""Shared helpers for class ability mechanics."""

from __future__ import annotations

from copy import deepcopy
import random
from typing import Any


ELEMENTS = ("Fire", "Ice", "Electric", "Water", "Earth", "Wind")
TAMED_COMPANION_START_BOND = 5
TAMED_COMPANION_ROSTER_LIMIT = 6
TAMED_COMPANION_EVOLUTIONS = (
    (100, "Apex Form"),
    (75, "Pack Form"),
    (50, "Battle Form"),
    (25, "Trusted Form"),
    (0, "Wild Form"),
)
TAMED_COMPANION_SPECIALS = {
    "Pounce": "Leaps into attacks for small bonus damage once bonded.",
    "Guard Hide": "Keeps close and softens the next blow once bonded.",
    "Wingbeat": "Buffets prey with wind pressure once bonded.",
    "Primal Spark": "Adds a small elemental spark once bonded.",
    "Keen Scent": "Sniffs out openings once bonded.",
}
BEAST_COMPANION_COMMANDS = ("Pack Strike", "Guard Partner", "Harry Prey", "Mend Wounds")
TAMED_COMPANION_CLASS_ALIASES = {
    "Panther2": "Panther",
    "Direwolf2": "Direwolf",
    "Direbear2": "Direbear",
}
TAMED_COMPANION_SPECIES = {
    "GiantRat": {
        "species": "Rat",
        "special_ability": "Pounce",
        "evolutions": ("Skittish Rat", "Tunnel Rat", "Razor Rat", "Pack Rat", "Dread Rat"),
    },
    "GiantCentipede": {
        "species": "Centipede",
        "special_ability": "Keen Scent",
        "evolutions": ("Skitterling", "Hooked Centipede", "Ironback Centipede", "Burrow Centipede", "Elder Centipede"),
    },
    "GiantHornet": {
        "species": "Hornet",
        "special_ability": "Wingbeat",
        "evolutions": ("Stingwing", "Amber Hornet", "War Hornet", "Hiveguard Hornet", "Storm Hornet"),
    },
    "ElectricBat": {
        "species": "Electric Bat",
        "special_ability": "Primal Spark",
        "evolutions": ("Spark Bat", "Stormwing Bat", "Thunder Bat", "Tempest Bat", "Volt Sovereign"),
    },
    "GiantSpider": {
        "species": "Spider",
        "special_ability": "Keen Scent",
        "evolutions": ("Webling", "Silk Spider", "Trap Spider", "Widow Spider", "Web Matriarch"),
    },
    "Panther": {
        "species": "Panther",
        "special_ability": "Pounce",
        "evolutions": ("Shadow Kit", "Stalker Panther", "Night Panther", "Huntmaster Panther", "Apex Panther"),
    },
    "BattleToad": {
        "species": "Battle Toad",
        "special_ability": "Guard Hide",
        "evolutions": ("Puddle Toad", "Brace Toad", "War Toad", "Bulwark Toad", "Elder Battle Toad"),
    },
    "GiantSnake": {
        "species": "Snake",
        "special_ability": "Keen Scent",
        "evolutions": ("Grass Snake", "Coil Snake", "Fang Snake", "Pit Snake", "Ancient Serpent"),
    },
    "GiantOwl": {
        "species": "Owl",
        "special_ability": "Wingbeat",
        "evolutions": ("Moon Owl", "Watch Owl", "Gale Owl", "Great Owl", "Star-Eyed Owl"),
    },
    "VampireBat": {
        "species": "Vampire Bat",
        "special_ability": "Keen Scent",
        "evolutions": ("Duskwick Bat", "Redfang Bat", "Nightdrinker Bat", "Bloodmoon Bat", "Nocturne Bat"),
    },
    "Direwolf": {
        "species": "Direwolf",
        "special_ability": "Pounce",
        "evolutions": ("Wolf Pup", "Trail Wolf", "Direwolf", "Pack Alpha", "Moonfang Alpha"),
    },
    "GiantScorpion": {
        "species": "Scorpion",
        "special_ability": "Guard Hide",
        "evolutions": ("Dust Scorpion", "Barbed Scorpion", "Iron Scorpion", "Venom Scorpion", "Dune Tyrant"),
    },
    "Direbear": {
        "species": "Direbear",
        "special_ability": "Guard Hide",
        "evolutions": ("Bear Cub", "Cave Bear", "Direbear", "Elder Bear", "Mountain King"),
    },
    "PitViper": {
        "species": "Pit Viper",
        "special_ability": "Keen Scent",
        "evolutions": ("Needle Viper", "Coil Viper", "Pit Viper", "Venom Viper", "Emerald Fang"),
    },
    "Alligator": {
        "species": "Alligator",
        "special_ability": "Guard Hide",
        "evolutions": ("Mud Snapper", "Marsh Gator", "Ironjaw Gator", "Bayou Gator", "Ancient Alligator"),
    },
    "GoldenEagle": {
        "species": "Golden Eagle",
        "special_ability": "Wingbeat",
        "evolutions": ("Eaglet", "Golden Eagle", "Sunwing Eagle", "Highwind Eagle", "Sky Crown Eagle"),
    },
    "Antlion": {
        "species": "Antlion",
        "special_ability": "Guard Hide",
        "evolutions": ("Sand Larva", "Pit Antlion", "Ambush Antlion", "Burrow Antlion", "Dune Maw"),
    },
}


def _skills(character: Any) -> dict[str, Any]:
    return getattr(character, "spellbook", {}).get("Skills", {}) or {}


def has_skill(character: Any, skill_name: str) -> bool:
    return skill_name in _skills(character)


def _is_two_handed_polearm(item: Any) -> bool:
    return getattr(item, "subtyp", None) == "Polearm" and getattr(item, "handed", 1) == 2


def _is_two_handed_staff(item: Any) -> bool:
    return getattr(item, "subtyp", None) == "Staff" and getattr(item, "handed", 1) == 2


def can_keep_polearm_shield(character: Any, weapon: Any, offhand: Any) -> bool:
    """Return whether a class skill lets a polearm stay paired with a shield."""
    if not _is_two_handed_polearm(weapon) or getattr(offhand, "subtyp", None) != "Shield":
        return False
    skills = _skills(character)
    return any(
        skill_name in skills
        for skill_name in ("Polearm Proficiency", "Polearm Excellence", "Polearm Mastery")
    )


def can_keep_staff_shield(character: Any, weapon: Any, offhand: Any) -> bool:
    """Return whether Staff Conduit lets a two-handed staff stay paired with a shield."""
    if not _is_two_handed_staff(weapon) or getattr(offhand, "subtyp", None) != "Shield":
        return False
    return has_skill(character, "Staff Conduit")


def can_keep_berserker_heavy_offhand(character: Any, weapon: Any, offhand: Any) -> bool:
    """Berserkers can wield two-handed weapons in one hand from promotion."""
    return (
        getattr(getattr(character, "cls", None), "name", None) == "Berserker"
        and getattr(weapon, "handed", 1) == 2
        and getattr(offhand, "typ", None) == "Weapon"
    )


def _one_handed_polearm_active(character: Any, weapon_type: str | None = None) -> bool:
    weapon = getattr(character, "equipment", {}).get("Weapon")
    offhand = getattr(character, "equipment", {}).get("OffHand")
    if weapon_type is not None and weapon_type != "Polearm":
        return False
    return _is_two_handed_polearm(weapon) and getattr(offhand, "subtyp", None) == "Shield"


def polearm_damage_multiplier(character: Any) -> float:
    if not _one_handed_polearm_active(character):
        return 1.0
    skills = _skills(character)
    if "Polearm Mastery" in skills:
        return 1.10
    if "Polearm Excellence" in skills:
        return 1.0
    if "Polearm Proficiency" in skills:
        return 0.85
    return 1.0


def polearm_accuracy_modifier(character: Any, weapon_type: str | None = None) -> float:
    if not _one_handed_polearm_active(character, weapon_type):
        return 0.0
    skills = _skills(character)
    if "Polearm Mastery" in skills:
        return 0.10
    if "Polearm Excellence" in skills:
        return 0.0
    if "Polearm Proficiency" in skills:
        return -0.10
    return 0.0


def _berserker_heavy_dual_wield_active(character: Any) -> bool:
    equipment = getattr(character, "equipment", {})
    return can_keep_berserker_heavy_offhand(
        character,
        equipment.get("Weapon"),
        equipment.get("OffHand"),
    )


def monkey_grip_damage_multiplier(character: Any, slot: str = "Weapon") -> float:
    if not _berserker_heavy_dual_wield_active(character):
        return 1.0
    skills = _skills(character)
    if slot == "Weapon":
        return 1.0 if "Monkey Grip" in skills or "Monkey Grip 2" in skills else 0.85
    if "Monkey Grip 2" in skills:
        return 0.75
    if "Monkey Grip" in skills:
        return 0.60
    return 0.50


def monkey_grip_accuracy_modifier(character: Any, slot: str = "Weapon") -> float:
    if not _berserker_heavy_dual_wield_active(character):
        return 0.0
    skills = _skills(character)
    if slot == "Weapon":
        return 0.0 if "Monkey Grip" in skills or "Monkey Grip 2" in skills else -0.10
    if "Monkey Grip 2" in skills:
        return -0.10
    if "Monkey Grip" in skills:
        return -0.20
    return -0.30


def third_eye_crit_bonus(character: Any) -> float:
    if not has_skill(character, "Third Eye"):
        return 0.0
    return min(0.10, max(0.0, int(getattr(character.stats, "intel", 0)) * 0.002))


def third_eye_dodge_bonus(character: Any) -> float:
    if not has_skill(character, "Third Eye"):
        return 0.0
    return min(0.10, max(0.0, int(getattr(character.stats, "intel", 0)) * 0.002))


def drunken_brawler_damage_bonus(character: Any) -> float:
    if not has_skill(character, "Drunken Brawler"):
        return 0.0
    effect = getattr(character, "class_effects", {}).get("Drunken Brawler")
    return 0.25 if effect is not None and effect.active else 0.0


def drunken_brawler_crit_bonus(character: Any) -> float:
    if not has_skill(character, "Drunken Brawler"):
        return 0.0
    effect = getattr(character, "class_effects", {}).get("Drunken Brawler")
    return 0.10 if effect is not None and effect.active else 0.0


def trigger_drunken_brawler(character: Any) -> str:
    if not has_skill(character, "Drunken Brawler"):
        return ""
    effect = getattr(character, "class_effects", {}).get("Drunken Brawler")
    if effect is None:
        return ""
    effect.active = True
    effect.duration = max(int(effect.duration or 0), 2)
    return f"{character.name}'s Drunken Brawler rhythm sharpens.\n"


def trigger_zephyrstrike(character: Any) -> str:
    if not has_skill(character, "Zephyrstrike"):
        return ""
    speed = getattr(character, "stat_effects", {}).get("Speed")
    if speed is None:
        return ""
    bonus = max(1, int(getattr(character.stats, "dex", 0)) // 5)
    speed.active = True
    speed.duration = max(int(speed.duration or 0), 2)
    speed.extra = max(int(speed.extra or 0), bonus)
    return f"Zephyrstrike quickens {character.name}.\n"


def power_up_active(character: Any, skill_name: str | None = None, class_name: str | None = None) -> bool:
    if class_name and getattr(getattr(character, "cls", None), "name", None) != class_name:
        return False
    if skill_name and not has_skill(character, skill_name):
        return False
    effect = getattr(character, "class_effects", {}).get("Power Up")
    return bool(getattr(character, "power_up", False) and effect is not None and effect.active)


def passive_power_up_unlocked(character: Any, skill_name: str, class_name: str | None = None) -> bool:
    if class_name and getattr(getattr(character, "cls", None), "name", None) != class_name:
        return False
    return bool(getattr(character, "power_up", False) and has_skill(character, skill_name))


def tricksters_gambit_magic_bonus(character: Any) -> float:
    return 0.20 if power_up_active(character, "Trickster's Gambit", "Arcane Trickster") else 0.0


def tricksters_gambit_crit_bonus(character: Any) -> float:
    return 0.10 if power_up_active(character, "Trickster's Gambit", "Arcane Trickster") else 0.0


def tricksters_gambit_dodge_bonus(character: Any) -> float:
    return 0.10 if power_up_active(character, "Trickster's Gambit", "Arcane Trickster") else 0.0


def primal_ascendance_multiplier(character: Any, aspect: str) -> float:
    if not power_up_active(character, "Primal Ascendance", "Archdruid"):
        return 1.0
    return {
        "Growth": 1.25,
        "Venom": 1.25,
        "Storm": 1.20,
        "Stone": 1.20,
    }.get(aspect, 1.0)


def abyssal_covenant_magic_bonus(character: Any) -> float:
    if not power_up_active(character, "Abyssal Covenant", "Demonologist"):
        return 0.0
    return 0.35


def abyssal_contract_count(character: Any, count: int) -> int:
    return int(count) * 2 if power_up_active(character, "Abyssal Covenant", "Demonologist") else int(count)


def arsenal_mastery_weapon_multiplier(character: Any) -> float:
    if not power_up_active(character, "Arsenal Mastery", "Grandmaster of Arms"):
        return 1.0
    ranks = getattr(character, "grandmaster_discipline", {}).get("disciplines", {})
    mastered = 0
    if isinstance(ranks, dict):
        mastered = sum(1 for entry in ranks.values() if isinstance(entry, dict) and int(entry.get("rank", 0) or 0) >= 10)
    return 1.10 + min(0.20, mastered * 0.03)


def shield_mastery_block_bonus(character: Any) -> int:
    return 25 if passive_power_up_unlocked(character, "Shield Mastery", "Stalwart Defender") else 0


def melody_inspiration_bonus(character: Any) -> float:
    return 0.05 if passive_power_up_unlocked(character, "Melody of Inspiration", "Troubadour") else 0.0


def pack_bond_multiplier(character: Any) -> float:
    familiar = getattr(character, "familiar", None)
    if not (familiar is not None and getattr(familiar, "is_alive", lambda: False)()):
        return 1.0
    if passive_power_up_unlocked(character, "Pack Bond", "Beast Master"):
        return 1.15
    return 1.0


def last_stand_attack_multiplier(character: Any) -> float:
    return 0.75 if has_skill(character, "Last Stand") else 1.0


def last_stand_defense_bonus(character: Any) -> int:
    if not has_skill(character, "Last Stand"):
        return 0
    defense = int(getattr(getattr(character, "combat", None), "defense", 0) or 0)
    return max(1, defense // 2)


def last_stand_block_bonus(character: Any) -> int:
    return 25 if has_skill(character, "Last Stand") else 0


def activate_last_stand(character: Any) -> str:
    if not has_skill(character, "Last Stand"):
        return ""
    effect = getattr(character, "class_effects", {}).get("Last Stand")
    if effect is None or effect.active:
        return ""
    hp = getattr(character, "health", None)
    hp_max = max(1, int(getattr(hp, "max", 1) or 1))
    if getattr(hp, "current", hp_max) / hp_max > 0.35:
        return ""
    effect.active = True
    effect.duration = max(int(effect.duration or 0), 4)
    defense = int(getattr(getattr(character, "combat", None), "defense", 0) or 0)
    effect.extra = max(int(effect.extra or 0), max(1, defense // 2))
    return f"{character.name} makes a Last Stand.\n"


def posturing_parry_bonus(character: Any) -> float:
    if not has_skill(character, "Posturing"):
        return 0.0
    defend = getattr(character, "status_effects", {}).get("Defend")
    return 0.20 if defend is not None and defend.active else 0.0


def retaliate_after_block(defender: Any, attacker: Any, *, rng: Any = random) -> str:
    if not has_skill(defender, "Retaliate"):
        return ""
    chance = min(0.75, 0.20 + (int(getattr(defender.stats, "dex", 0)) * 0.01))
    if rng.random() >= chance:
        return ""
    msg = f"{defender.name} retaliates after the block!\n"
    counter, _hit, _crit = defender.weapon_damage(attacker, dmg_mod=0.75, use_offhand=False)
    return msg + counter


def final_assault_response(defender: Any, attacker: Any, incoming_damage: int) -> tuple[str, bool]:
    if incoming_damage < getattr(defender.health, "current", 0):
        return "", False
    if not has_skill(defender, "Final Assault"):
        return "", False
    if getattr(defender, "_final_assault_used", False) or getattr(defender, "_final_assault_countering", False):
        return "", False
    defender._final_assault_used = True
    defender._final_assault_countering = True
    try:
        msg = f"{defender.name} answers lethal force with a Final Assault!\n"
        counter, _hit, _crit = defender.weapon_damage(attacker, dmg_mod=1.25, use_offhand=True)
        msg += counter
    finally:
        defender._final_assault_countering = False
    if getattr(attacker.health, "current", 0) <= 0:
        defender.health.current = 1
        return msg + f"{defender.name} stabilizes at 1 HP.\n", True
    return msg, False


def nature_shield_orbs(character: Any) -> int:
    effect = getattr(character, "magic_effects", {}).get("Nature Shield")
    if effect is None or not effect.active:
        return 0
    return max(0, int(effect.extra or 0))


def spend_nature_shield_orb(character: Any) -> bool:
    effect = getattr(character, "magic_effects", {}).get("Nature Shield")
    if effect is None or not effect.active:
        return False
    orbs = max(0, int(effect.extra or 0))
    if orbs <= 0:
        effect.active = False
        return False
    effect.extra = orbs - 1
    if effect.extra <= 0:
        effect.active = False
        effect.duration = 0
    return True


def default_tamed_companion() -> dict[str, Any]:
    return {
        "active": False,
        "enemy_class": None,
        "name": None,
        "custom_name": None,
        "level": 1,
        "bond": 0,
        "species": None,
        "evolution": "Wild Form",
        "special_ability": "Keen Scent",
        "pending_command": None,
        "active_index": None,
        "companions": [],
        "base": {},
    }


def _tamed_enemy_class_key(enemy_class: Any) -> str | None:
    if not enemy_class:
        return None
    key = str(enemy_class)
    return TAMED_COMPANION_CLASS_ALIASES.get(key, key)


def _tamed_species_data(enemy_class: Any = None, species: Any = None, name: Any = None) -> dict[str, Any] | None:
    key = _tamed_enemy_class_key(enemy_class)
    if key and key in TAMED_COMPANION_SPECIES:
        return TAMED_COMPANION_SPECIES[key]
    token = str(species or name or "").lower()
    for data in TAMED_COMPANION_SPECIES.values():
        if str(data["species"]).lower() == token:
            return data
    return None


def tamed_companion_species(enemy: Any) -> str:
    data = _tamed_species_data(enemy.__class__.__name__, getattr(enemy, "name", None))
    return str(data["species"]) if data else str(getattr(enemy, "name", "Animal") or "Animal")


def tamed_companion_evolution_for_bond(bond: Any, enemy_class: Any = None, species: Any = None) -> str:
    try:
        value = max(0, min(100, int(bond or 0)))
    except (TypeError, ValueError):
        value = 0
    data = _tamed_species_data(enemy_class, species)
    if data:
        evolutions = data["evolutions"]
        for index, (threshold, _generic) in enumerate(TAMED_COMPANION_EVOLUTIONS):
            if value >= threshold:
                return str(evolutions[len(evolutions) - 1 - index])
    for threshold, generic_evolution in TAMED_COMPANION_EVOLUTIONS:
        if value >= threshold:
            return generic_evolution
    return "Wild Form"


def _infer_tamed_special_from_name(name: str | None) -> str:
    token = str(name or "").lower()
    if any(part in token for part in ("bat", "bird", "hawk", "eagle", "wasp", "bee")):
        return "Wingbeat"
    if any(part in token for part in ("bear", "boar", "turtle", "crab", "beetle")):
        return "Guard Hide"
    if any(part in token for part in ("fox", "wolf", "rat", "cat", "panther", "tiger")):
        return "Pounce"
    return "Keen Scent"


def tamed_special_from_enemy(enemy: Any) -> str:
    data = _tamed_species_data(enemy.__class__.__name__, getattr(enemy, "name", None))
    if data:
        return str(data["special_ability"])
    if getattr(enemy, "flying", False):
        return "Wingbeat"
    combat = getattr(enemy, "combat", None)
    stats = getattr(enemy, "stats", None)
    attack = int(getattr(combat, "attack", 0) or 0)
    defense = int(getattr(combat, "defense", 0) or 0)
    magic = int(getattr(combat, "magic", 0) or 0)
    dex = int(getattr(stats, "dex", 0) or 0)
    con = int(getattr(stats, "con", 0) or 0)
    if magic > max(attack, defense):
        return "Primal Spark"
    if dex >= con + 3 or attack > defense:
        return "Pounce"
    if defense >= attack + 2 or con >= dex + 3:
        return "Guard Hide"
    return _infer_tamed_special_from_name(getattr(enemy, "name", None) or enemy.__class__.__name__)


def _known_tamed_evolutions() -> set[str]:
    known = {name for _threshold, name in TAMED_COMPANION_EVOLUTIONS}
    for data in TAMED_COMPANION_SPECIES.values():
        known.update(str(name) for name in data["evolutions"])
    return known


def tamed_companion_display_name(state: Any) -> str:
    """Return the visible tamed companion name, preserving species identity."""
    entry = state if isinstance(state, dict) else {}
    base_name = str(entry.get("name") or entry.get("species") or entry.get("enemy_class") or "Companion")
    custom_name = str(entry.get("custom_name") or "").strip()
    if custom_name and custom_name != base_name:
        return f"{custom_name} ({base_name})"
    return base_name


def rename_tamed_companion(character: Any, custom_name: Any, roster_index: int | None = None) -> None:
    """Set a tamed companion nickname while keeping the original animal identity."""
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    roster = list(state.get("companions", []))
    if not roster:
        character.tamed_companion = state
        return
    if roster_index is None:
        roster_index = int(state.get("active_index", 0) or 0)
    if roster_index < 0 or roster_index >= len(roster):
        character.tamed_companion = state
        return
    nickname = str(custom_name or "").strip()[:20]
    entry = dict(roster[roster_index])
    entry["custom_name"] = nickname or None
    roster[roster_index] = entry
    character.tamed_companion = _with_active_tamed_companion(roster, int(state.get("active_index", roster_index) or 0))
    try:
        from .. import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass


def _tamed_entry_from_state(state: Any) -> dict[str, Any]:
    normalized = default_tamed_companion()
    if isinstance(state, dict):
        normalized["active"] = bool(state.get("active", False))
        normalized["enemy_class"] = _tamed_enemy_class_key(state.get("enemy_class")) if state.get("enemy_class") else None
        normalized["name"] = state.get("name") if state.get("name") else normalized["enemy_class"]
        custom_name = str(state.get("custom_name") or "").strip()
        normalized["custom_name"] = custom_name or None
        species_data = _tamed_species_data(normalized["enemy_class"], state.get("species"), normalized["name"])
        normalized["species"] = (
            str(species_data["species"])
            if species_data
            else state.get("species") if state.get("species") else normalized["name"]
        )
        try:
            normalized["level"] = max(1, int(state.get("level", 1) or 1))
        except (TypeError, ValueError):
            normalized["level"] = 1
        try:
            normalized["bond"] = max(0, min(100, int(state.get("bond", 0) or 0)))
        except (TypeError, ValueError):
            normalized["bond"] = 0
        special = str(state.get("special_ability") or "")
        if special not in TAMED_COMPANION_SPECIALS:
            special = str(species_data["special_ability"]) if species_data else _infer_tamed_special_from_name(normalized["enemy_class"] or normalized["name"])
        normalized["special_ability"] = special
        evolution = str(state.get("evolution") or "")
        expected_evolution = tamed_companion_evolution_for_bond(
            normalized["bond"], normalized["enemy_class"], normalized["species"]
        )
        normalized["evolution"] = evolution if evolution in _known_tamed_evolutions() and evolution == expected_evolution else expected_evolution
        pending = state.get("pending_command")
        normalized["pending_command"] = str(pending) if pending else None
        base = state.get("base")
        normalized["base"] = base if isinstance(base, dict) else {}
    normalized.pop("companions", None)
    normalized.pop("active_index", None)
    return normalized


def tamed_companion_base_snapshot(enemy: Any) -> dict[str, Any]:
    return {
        "health_max": max(1, int(getattr(enemy.health, "max", 20) * 0.75)),
        "mana_max": max(0, int(getattr(enemy.mana, "max", 0) * 0.5)),
        "stats": {
            "strength": max(1, int(getattr(enemy.stats, "strength", 5) * 0.75)),
            "intel": max(1, int(getattr(enemy.stats, "intel", 5) * 0.5)),
            "wisdom": max(1, int(getattr(enemy.stats, "wisdom", 5) * 0.5)),
            "con": max(1, int(getattr(enemy.stats, "con", 5) * 0.75)),
            "charisma": max(1, int(getattr(enemy.stats, "charisma", 5) * 0.5)),
            "dex": max(1, int(getattr(enemy.stats, "dex", 5) * 0.75)),
        },
        "combat": {
            "attack": max(1, int(getattr(enemy.combat, "attack", 5) * 0.75)),
            "defense": max(1, int(getattr(enemy.combat, "defense", 5) * 0.75)),
            "magic": max(1, int(getattr(enemy.combat, "magic", 5) * 0.5)),
            "magic_def": max(1, int(getattr(enemy.combat, "magic_def", 5) * 0.5)),
        },
    }


def _tamed_roster_key(entry: dict[str, Any]) -> str:
    return str(entry.get("enemy_class") or entry.get("species") or entry.get("name") or "")


def _with_active_tamed_companion(roster: list[dict[str, Any]], active_index: int | None) -> dict[str, Any]:
    normalized = default_tamed_companion()
    normalized["companions"] = roster[:TAMED_COMPANION_ROSTER_LIMIT]
    if active_index is None or active_index < 0 or active_index >= len(normalized["companions"]):
        normalized["active_index"] = None
        return normalized
    active = dict(normalized["companions"][active_index])
    active["active"] = True
    active["pending_command"] = active.get("pending_command")
    normalized.update(active)
    normalized["active_index"] = active_index
    normalized["companions"][active_index] = active
    return normalized


def normalize_tamed_companion(state: Any) -> dict[str, Any]:
    active_entry = _tamed_entry_from_state(state)
    raw_roster = state.get("companions") if isinstance(state, dict) else None
    roster: list[dict[str, Any]] = []
    seen: set[str] = set()
    if isinstance(raw_roster, list):
        for raw_entry in raw_roster:
            entry = _tamed_entry_from_state(raw_entry)
            if not entry.get("enemy_class"):
                continue
            key = _tamed_roster_key(entry)
            if key in seen:
                continue
            seen.add(key)
            roster.append(entry)
            if len(roster) >= TAMED_COMPANION_ROSTER_LIMIT:
                break
    if active_entry.get("active") and active_entry.get("enemy_class") and _tamed_roster_key(active_entry) not in seen:
        roster.insert(0, active_entry)
        roster = roster[:TAMED_COMPANION_ROSTER_LIMIT]

    active_index = None
    if roster:
        try:
            requested_index = int(state.get("active_index")) if isinstance(state, dict) and state.get("active_index") is not None else None
        except (TypeError, ValueError):
            requested_index = None
        if requested_index is not None and 0 <= requested_index < len(roster):
            active_index = requested_index
        elif active_entry.get("active"):
            active_key = _tamed_roster_key(active_entry)
            for index, entry in enumerate(roster):
                if _tamed_roster_key(entry) == active_key:
                    active_index = index
                    break
        if active_index is None:
            active_index = 0
    for index, entry in enumerate(roster):
        entry["active"] = index == active_index
        if index != active_index:
            entry["pending_command"] = None
    normalized = _with_active_tamed_companion(roster, active_index)
    if isinstance(state, dict) and state.get("pending_command") and normalized["active"]:
        normalized["pending_command"] = str(state["pending_command"])
        normalized["companions"][normalized["active_index"]]["pending_command"] = normalized["pending_command"]
    return normalized


def activate_tamed_companion(character: Any, roster_index: int) -> str:
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    roster = list(state.get("companions", []))
    if roster_index < 0 or roster_index >= len(roster):
        return "No tamed companion is waiting there.\n"
    character.tamed_companion = _with_active_tamed_companion(roster, roster_index)
    try:
        from .. import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass
    return f"{character.tamed_companion['name']} takes the lead.\n"


def release_tamed_companion(character: Any, roster_index: int | None = None) -> str:
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    roster = list(state.get("companions", []))
    if not roster:
        return "There is no tamed companion to release.\n"
    if roster_index is None:
        roster_index = state.get("active_index")
    if roster_index is None or roster_index < 0 or roster_index >= len(roster):
        return "No tamed companion is waiting there.\n"
    released = roster.pop(roster_index)
    active_index = None if not roster else min(roster_index, len(roster) - 1)
    character.tamed_companion = _with_active_tamed_companion(roster, active_index)
    try:
        from .. import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass
    return f"{released.get('name', 'The companion')} returns to the wild.\n"


def tamed_special_description(special_ability: str | None) -> str:
    return TAMED_COMPANION_SPECIALS.get(str(special_ability or ""), TAMED_COMPANION_SPECIALS["Keen Scent"])


def apply_tamed_companion_growth(companion: Any, state: dict[str, Any]) -> None:
    bond = max(0, min(100, int(state.get("bond", 0) or 0)))
    multiplier = 1.0 + (0.20 * (bond / 100))
    companion.bond = bond
    companion.species = state.get("species") or getattr(companion, "race", None)
    companion.evolution = tamed_companion_evolution_for_bond(
        bond, state.get("enemy_class"), companion.species
    )
    companion.special_ability = state.get("special_ability") or "Keen Scent"
    for resource_name in ("health", "mana"):
        resource = getattr(companion, resource_name, None)
        if resource is None:
            continue
        resource.max = max(0, int(resource.max * multiplier))
        resource.current = resource.max
    for attr in ("strength", "con", "dex"):
        setattr(companion.stats, attr, max(1, int(getattr(companion.stats, attr, 1) * multiplier)))
    for attr in ("attack", "defense"):
        setattr(companion.combat, attr, max(1, int(getattr(companion.combat, attr, 1) * multiplier)))


def tamed_companion_special_turn(owner: Any, target: Any, *, hit: bool = False, crit: bool = False) -> str:
    companion = getattr(owner, "familiar", None)
    if companion is None or getattr(companion, "spec", "") != "Tamed":
        return ""
    bond = max(0, min(100, int(getattr(companion, "bond", 0) or 0)))
    if bond < 25 or target is None:
        return ""
    special = str(getattr(companion, "special_ability", "") or "Keen Scent")
    if special == "Pounce" and hit:
        damage = max(1, int(getattr(companion.combat, "attack", 1) * (0.12 + (0.08 if crit else 0.0))))
        target.health.current = max(0, target.health.current - damage)
        return f"{companion.name}'s Pounce follows through for {damage} damage.\n"
    if special == "Wingbeat" and hit:
        effect = target.stat_effects["Speed"]
        effect.active = True
        effect.duration = max(effect.duration, 2)
        effect.extra = min(int(effect.extra or 0), -max(1, bond // 25))
        return f"{companion.name}'s Wingbeat throws {target.name} off balance.\n"
    if special == "Guard Hide":
        effect = owner.magic_effects["Nature Shield"]
        effect.active = True
        effect.duration = max(effect.duration, 1)
        effect.extra = max(int(effect.extra or 0), max(4, bond // 5))
        effect.source = "Guard Hide"
        return f"{companion.name}'s Guard Hide braces {owner.name}.\n"
    if special == "Primal Spark" and hit:
        damage = max(1, int(getattr(companion.combat, "magic", 1) * 0.20))
        target.health.current = max(0, target.health.current - damage)
        return f"{companion.name}'s Primal Spark flashes for {damage} damage.\n"
    if special == "Keen Scent" and hit:
        effect = target.stat_effects["Defense"]
        effect.active = True
        effect.duration = max(effect.duration, 2)
        effect.extra = min(int(effect.extra or 0), -max(1, bond // 30))
        return f"{companion.name}'s Keen Scent finds a weak point.\n"
    return ""


def tamed_companion_bond(character: Any) -> int:
    state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    bond = max(0, min(100, int(state.get("bond", 0) or 0)))
    companion = getattr(character, "familiar", None)
    if getattr(companion, "spec", "") == "Tamed":
        try:
            bond = max(bond, max(0, min(100, int(getattr(companion, "bond", 0) or 0))))
        except (TypeError, ValueError):
            pass
    return bond


def has_living_tamed_companion(character: Any) -> bool:
    companion = getattr(character, "familiar", None)
    if companion is None or getattr(companion, "spec", "") != "Tamed":
        return False
    is_alive = getattr(companion, "is_alive", None)
    return bool(is_alive()) if callable(is_alive) else True


def _class_name(character: Any) -> str:
    return str(getattr(getattr(character, "cls", None), "name", "") or "")


def available_beast_companion_commands(character: Any) -> list[str]:
    if _class_name(character) != "Beast Master" or not has_living_tamed_companion(character):
        return []
    skills = getattr(character, "spellbook", {}).get("Skills", {})
    return [name for name in BEAST_COMPANION_COMMANDS if name in skills]


def _companion_command_state(character: Any) -> dict[str, Any]:
    state = getattr(character, "_promotion_kit_combat", None)
    if not isinstance(state, dict):
        state = {}
        setattr(character, "_promotion_kit_combat", state)
    return state


def pending_companion_command(character: Any) -> str | None:
    command = _companion_command_state(character).get("pending_companion_command")
    return str(command) if command else None


def set_pending_companion_command(character: Any, command: str | None) -> None:
    state = _companion_command_state(character)
    if command:
        state["pending_companion_command"] = str(command)
    else:
        state.pop("pending_companion_command", None)


def tamed_auto_action_chance(character: Any) -> float:
    bond = tamed_companion_bond(character)
    return min(0.40, 0.12 + (bond * 0.0028))


def tamed_companion_should_auto_act(character: Any, *, rng: Any = random) -> bool:
    if not has_living_tamed_companion(character) or pending_companion_command(character):
        return False
    class_name = _class_name(character)
    if class_name not in {"Ranger", "Beast Master"}:
        return False
    return rng.random() < tamed_auto_action_chance(character)


def _favored_enemy_pressure(character: Any, target: Any | None) -> bool:
    return bool(target is not None and getattr(target, "enemy_typ", None) == favorite_enemy_type(character))


def resolve_tamed_companion_command(character: Any, target: Any | None) -> str:
    command = pending_companion_command(character)
    if not command:
        return ""
    set_pending_companion_command(character, None)
    companion = getattr(character, "familiar", None)
    if target is None or not has_living_tamed_companion(character):
        return f"{command} fades without a living companion to follow it.\n"

    bond = tamed_companion_bond(character)
    rank = max(0, bond // 25)
    favored = _favored_enemy_pressure(character, target)

    if command == "Pack Strike":
        dmg_mod = 0.55 + (bond / 250.0) + (0.10 if favored else 0.0)
        msg = f"{companion.name} follows Pack Strike.\n"
        attack_str, hit, crit = companion.weapon_damage(target, dmg_mod=dmg_mod)
        msg += attack_str
        msg += tamed_companion_special_turn(character, target, hit=hit, crit=crit)
        return msg

    if command == "Guard Partner":
        effect = character.magic_effects["Nature Shield"]
        amount = 4 + rank * 4 + (bond // 20)
        effect.active = True
        effect.duration = max(effect.duration, 1 + (1 if rank >= 3 else 0))
        effect.extra = max(int(effect.extra or 0), amount)
        effect.source = "Guard Partner"
        return f"{companion.name} guards {character.name}, bracing the next hit.\n"

    if command == "Harry Prey":
        defense = target.stat_effects["Defense"]
        defense.active = True
        defense.duration = max(defense.duration, 1 + min(2, rank))
        defense.extra = min(int(defense.extra or 0), -(1 + rank))
        msg = f"{companion.name} harries {target.name}'s footing.\n"
        if rank >= 2:
            speed = target.stat_effects["Speed"]
            speed.active = True
            speed.duration = max(speed.duration, 2)
            speed.extra = min(int(speed.extra or 0), -max(1, rank))
        return msg

    if command == "Mend Wounds":
        owner_missing = max(0, character.health.max - character.health.current)
        companion_missing = max(0, companion.health.max - companion.health.current)
        heal_target = companion if companion_missing > owner_missing else character
        amount = min(max(owner_missing, companion_missing), 5 + rank * 5 + bond // 10)
        if amount <= 0:
            return f"{companion.name} stays close, ready to mend wounds.\n"
        heal_target.health.current = min(heal_target.health.max, heal_target.health.current + amount)
        return f"{companion.name} mends {heal_target.name}'s wounds for {amount} HP.\n"

    return f"{companion.name} cannot follow {command} yet.\n"


def default_exploration_effects() -> dict[str, int]:
    return {"invisibility": 0, "volitation": 0, "enter_wall": 0}


def normalize_exploration_effects(state: Any) -> dict[str, int]:
    normalized = default_exploration_effects()
    if isinstance(state, dict):
        for key in normalized:
            try:
                normalized[key] = max(0, int(state.get(key, 0) or 0))
            except (TypeError, ValueError):
                normalized[key] = 0
    return normalized


def ensure_exploration_effects(character: Any) -> dict[str, int]:
    state = normalize_exploration_effects(getattr(character, "temporary_exploration_effects", None))
    setattr(character, "temporary_exploration_effects", state)
    sync_exploration_flags(character)
    return state


def sync_exploration_flags(character: Any) -> None:
    state = normalize_exploration_effects(getattr(character, "temporary_exploration_effects", None))
    if state["invisibility"] > 0:
        character.invisible = True
    if state["volitation"] > 0:
        character.flying = True
    if state["enter_wall"] > 0:
        character.enter_wall = True


def apply_exploration_effect(character: Any, key: str, turns: int) -> None:
    state = ensure_exploration_effects(character)
    state[key] = max(state.get(key, 0), int(turns))
    setattr(character, "temporary_exploration_effects", state)
    sync_exploration_flags(character)


def tick_exploration_effects(character: Any, steps: int) -> None:
    state = normalize_exploration_effects(getattr(character, "temporary_exploration_effects", None))
    step_count = max(0, int(steps or 0))
    if step_count <= 0:
        return
    changed = False
    for key in state:
        if state[key] > 0:
            state[key] = max(0, state[key] - step_count)
            changed = True
    if changed:
        character.temporary_exploration_effects = state
        if state["invisibility"] <= 0:
            character.invisible = False
        if state["volitation"] <= 0:
            character.flying = False
        if state["enter_wall"] <= 0:
            character.enter_wall = False


def favorite_enemy_type(character: Any) -> str | None:
    try:
        from . import promotion_kits

        state = promotion_kits.ensure_state(character).get("favored_enemy", {})
        marked = state.get("type") if isinstance(state, dict) else None
        if marked:
            return str(marked)
    except Exception:
        pass
    return None


def favored_enemy_state(character: Any) -> dict[str, Any]:
    try:
        from . import promotion_kits

        state = promotion_kits.ensure_state(character)["favored_enemy"]
        return {
            "type": state.get("type"),
            "practice": max(0, int(state.get("practice", 0) or 0)),
            "switches": max(0, int(state.get("switches", 0) or 0)),
        }
    except Exception:
        return {"type": None, "practice": 0, "switches": 0}


def favored_enemy_rank(practice: Any) -> str:
    try:
        value = max(0, int(practice or 0))
    except (TypeError, ValueError):
        value = 0
    if value >= 30:
        return "Mastered Trail"
    if value >= 15:
        return "Known Trail"
    if value >= 5:
        return "Fresh Trail"
    return "New Trail"


def favored_enemy_practice_bonus(character: Any) -> int:
    state = favored_enemy_state(character)
    practice = max(0, int(state.get("practice", 0) or 0))
    if not state.get("type"):
        return 0
    return min(8, 1 + practice // 5)


def favored_enemy_label(character: Any) -> str:
    state = favored_enemy_state(character)
    marked = state.get("type")
    if marked:
        return str(marked)
    return "None"


def mark_favored_enemy(character: Any, target: Any | None) -> str:
    if target is None:
        return "There is no quarry to mark.\n"
    enemy_type = getattr(target, "enemy_typ", None)
    if not enemy_type:
        return f"{getattr(target, 'name', 'The target')} leaves no usable trail.\n"
    try:
        from . import promotion_kits

        state = promotion_kits.ensure_state(character)["favored_enemy"]
    except Exception:
        return "The trail slips away.\n"

    current = state.get("type")
    before = int(state.get("practice", 0) or 0)
    if current == enemy_type:
        state["practice"] = min(999, before + 2)
        return f"{character.name} studies the {enemy_type} trail more deeply.\n"

    carryover = before // 3 if current else 0
    state["type"] = str(enemy_type)
    state["practice"] = carryover
    state["switches"] = int(state.get("switches", 0) or 0) + int(bool(current))
    if current:
        return f"{character.name} changes quarry from {current} to {enemy_type}.\n"
    return f"{character.name} marks {enemy_type} as their favored enemy.\n"


def gain_favored_enemy_practice(character: Any, enemy: Any | None, amount: int, reason: str) -> str:
    enemy_type = getattr(enemy, "enemy_typ", None)
    state = favored_enemy_state(character)
    if not enemy_type or enemy_type != state.get("type"):
        return ""
    try:
        from . import promotion_kits

        favored = promotion_kits.ensure_state(character)["favored_enemy"]
    except Exception:
        return ""
    before = int(favored.get("practice", 0) or 0)
    favored["practice"] = min(999, before + max(0, int(amount or 0)))
    after = int(favored.get("practice", 0) or 0)
    if after <= before:
        return ""
    return ""


def favored_enemy_bonus(character: Any, enemy: Any | None) -> int:
    if enemy is None:
        return 0
    if "Favored Enemy" not in getattr(character, "spellbook", {}).get("Skills", {}):
        return 0
    enemy_type = getattr(enemy, "enemy_typ", None)
    if not enemy_type or enemy_type != favorite_enemy_type(character):
        return 0
    state = favored_enemy_state(character)
    if state.get("type"):
        bonus = favored_enemy_practice_bonus(character)
    else:
        total = sum(int(value or 0) for value in (getattr(character, "kill_dict", {}) or {}).get(enemy_type, {}).values())
        bonus = max(1, total // 10)
    if bonus > 0:
        try:
            from . import promotion_kits

            combat = promotion_kits.combat_state(character)
            if not combat.get("favored_enemy_bonus_logged"):
                combat["favored_enemy_bonus_logged"] = True
        except Exception:
            pass
    return bonus


def consume_favored_enemy_bonus_message(character: Any) -> str:
    try:
        from . import promotion_kits

        combat = promotion_kits.combat_state(character)
        if combat.pop("favored_enemy_bonus_logged", False):
            return "Favored Enemy pressure guides the strike.\n"
    except Exception:
        pass
    return ""


def attempt_tame(character: Any, target: Any, *, rng: Any = random) -> str:
    if target is None:
        return "There is no beast to tame.\n"
    if getattr(target, "enemy_typ", None) != "Animal":
        return f"{getattr(target, 'name', 'The target')} is not tamable.\n"
    if getattr(target, "boss", False) or getattr(target, "boss_type", None) or getattr(target, "class_ring_trial_enemy", False):
        return f"{target.name} resists all attempts at taming.\n"
    current_state = normalize_tamed_companion(getattr(character, "tamed_companion", None))
    roster = list(current_state.get("companions", []))
    enemy_class = _tamed_enemy_class_key(target.__class__.__name__)
    existing_index = None
    for index, companion_state in enumerate(roster):
        if companion_state.get("enemy_class") == enemy_class:
            existing_index = index
            break
    if existing_index is None and len(roster) >= TAMED_COMPANION_ROSTER_LIMIT:
        return (
            f"{character.name} cannot keep another tamed companion.\n"
            f"Release one from the Companion & Hunt tab before taming {target.name}.\n"
        )
    hp_max = max(1, int(getattr(getattr(target, "health", None), "max", 1) or 1))
    hp_ratio = max(0.0, min(1.0, getattr(target.health, "current", hp_max) / hp_max))
    low_hp_bonus = 0.35 if hp_ratio <= 0.35 else 0.0
    chance = min(0.85, 0.15 + low_hp_bonus + (character.stats.charisma * 0.015))
    if rng.random() > chance:
        return f"{character.name} fails to tame {target.name}; it refuses the signal.\n"

    state = {
        "active": True,
        "enemy_class": enemy_class,
        "name": target.name,
        "custom_name": None,
        "level": max(1, int(getattr(getattr(target, "level", None), "level", 1) or 1)),
        "bond": TAMED_COMPANION_START_BOND,
        "species": tamed_companion_species(target),
        "evolution": tamed_companion_evolution_for_bond(TAMED_COMPANION_START_BOND, enemy_class),
        "special_ability": tamed_special_from_enemy(target),
        "pending_command": None,
        "base": tamed_companion_base_snapshot(target),
    }
    if existing_index is None:
        roster.append(state)
        active_index = len(roster) - 1
        lead = f"{character.name} tames {target.name}.\n"
    else:
        existing = dict(roster[existing_index])
        bond = max(
            int(existing.get("bond", 0) or 0),
            min(100, int(existing.get("bond", 0) or 0) + TAMED_COMPANION_START_BOND),
        )
        existing.update(state)
        existing["bond"] = bond
        existing["evolution"] = tamed_companion_evolution_for_bond(bond, enemy_class, existing["species"])
        roster[existing_index] = existing
        active_index = existing_index
        lead = f"{character.name} strengthens their bond with {target.name}.\n"
    character.tamed_companion = _with_active_tamed_companion(roster, active_index)
    try:
        from .. import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass
    target.tamed_by_player = True
    target.no_victory_rewards = True
    target.health.current = 0
    special = character.tamed_companion["special_ability"]
    roster_count = len(character.tamed_companion.get("companions", []))
    return (
        lead +
        f"{target.name} begins watching for your signals with {special}.\n"
        f"Tamed companions held: {roster_count}/{TAMED_COMPANION_ROSTER_LIMIT}.\n"
    )


def capture_battle_snapshot(engine: Any) -> dict[str, Any]:
    def character_state(character: Any) -> dict[str, Any]:
        return {
            "health": getattr(character.health, "current", 0),
            "mana": getattr(character.mana, "current", 0),
            "status_effects": deepcopy(getattr(character, "status_effects", {})),
            "physical_effects": deepcopy(getattr(character, "physical_effects", {})),
            "stat_effects": deepcopy(getattr(character, "stat_effects", {})),
            "magic_effects": deepcopy(getattr(character, "magic_effects", {})),
            "flying": getattr(character, "flying", False),
            "invisible": getattr(character, "invisible", False),
            "tunnel": getattr(character, "tunnel", False),
        }

    return {
        "player": character_state(engine.player),
        "enemy": character_state(engine.enemy),
        "attacker": "player" if engine.attacker == engine.player else "enemy",
        "defender": "player" if engine.defender == engine.player else "enemy",
        "summon_active": bool(getattr(engine, "summon_active", False)),
    }


def store_rewind_snapshot(engine: Any) -> None:
    if getattr(engine, "attacker", None) == getattr(engine, "player", None):
        engine.player._rewind_snapshot = capture_battle_snapshot(engine)


def restore_battle_snapshot(engine: Any, snapshot: dict[str, Any]) -> str:
    if not snapshot:
        return "No foretelling has been prepared.\n"

    def restore(character: Any, state: dict[str, Any]) -> None:
        character.health.current = state["health"]
        character.mana.current = state["mana"]
        character.status_effects = deepcopy(state["status_effects"])
        character.physical_effects = deepcopy(state["physical_effects"])
        character.stat_effects = deepcopy(state["stat_effects"])
        character.magic_effects = deepcopy(state["magic_effects"])
        character.flying = state["flying"]
        character.invisible = state["invisible"]
        character.tunnel = state["tunnel"]

    restore(engine.player, snapshot["player"])
    restore(engine.enemy, snapshot["enemy"])
    engine.attacker = engine.player if snapshot.get("attacker") == "player" else engine.enemy
    engine.defender = engine.player if snapshot.get("defender") == "player" else engine.enemy
    engine.summon_active = bool(snapshot.get("summon_active", False))
    engine.player._foretell_snapshot = None
    return "Time folds back to the foretold moment.\n"


def restore_rewind_snapshot(engine: Any) -> str:
    snapshot = getattr(engine.player, "_rewind_snapshot", None)
    if not snapshot:
        return "No previous choice point can be rewound.\n"
    message = restore_battle_snapshot(engine, snapshot)
    engine.player._rewind_snapshot = None
    return message.replace("foretold moment", "previous choice point")


def heal_all_summons(character: Any, pct: float = 0.35) -> str:
    summons = getattr(character, "summons", {}) or {}
    if not summons:
        return f"{character.name} has no summons to heal.\n"
    lines = []
    for summon in summons.values():
        hp_max = max(1, int(getattr(summon.health, "max", 1) or 1))
        mp_max = max(1, int(getattr(summon.mana, "max", 1) or 1))
        hp = max(1, int(hp_max * pct))
        mp = max(1, int(mp_max * pct))
        before_hp = summon.health.current
        before_mp = summon.mana.current
        summon.health.current = min(hp_max, summon.health.current + hp)
        summon.mana.current = min(mp_max, summon.mana.current + mp)
        lines.append(
            f"{summon.name} recovers {summon.health.current - before_hp} HP "
            f"and {summon.mana.current - before_mp} MP."
        )
    return "\n".join(lines) + "\n"


def raise_all_summons(character: Any, pct: float = 0.25) -> str:
    summons = getattr(character, "summons", {}) or {}
    if not summons:
        return f"{character.name} has no summons to raise.\n"
    raised = []
    for summon in summons.values():
        if summon.health.current <= 0:
            summon.health.current = max(1, int(summon.health.max * pct))
            raised.append(summon.name)
    if not raised:
        return "No fallen summons answer the call.\n"
    return "Raised summons: " + ", ".join(raised) + ".\n"
