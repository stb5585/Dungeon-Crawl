"""Equipment compatibility and weapon-style mechanics."""

from __future__ import annotations

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
BEAST_COMPANION_COMMANDS = (
    "Pack Strike",
    "Guard Partner",
    "Harry Prey",
    "Mend Wounds",
    "Unleash Instinct",
    "Rally Partner",
)
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
        "evolutions": (
            "Skitterling",
            "Hooked Centipede",
            "Ironback Centipede",
            "Burrow Centipede",
            "Elder Centipede",
        ),
    },
    "GiantHornet": {
        "species": "Hornet",
        "special_ability": "Wingbeat",
        "evolutions": (
            "Stingwing",
            "Amber Hornet",
            "War Hornet",
            "Hiveguard Hornet",
            "Storm Hornet",
        ),
    },
    "ElectricBat": {
        "species": "Electric Bat",
        "special_ability": "Primal Spark",
        "evolutions": (
            "Spark Bat",
            "Stormwing Bat",
            "Thunder Bat",
            "Tempest Bat",
            "Volt Sovereign",
        ),
    },
    "GiantSpider": {
        "species": "Spider",
        "special_ability": "Keen Scent",
        "evolutions": ("Webling", "Silk Spider", "Trap Spider", "Widow Spider", "Web Matriarch"),
    },
    "Panther": {
        "species": "Panther",
        "special_ability": "Pounce",
        "evolutions": (
            "Shadow Kit",
            "Stalker Panther",
            "Night Panther",
            "Huntmaster Panther",
            "Apex Panther",
        ),
    },
    "BattleToad": {
        "species": "Battle Toad",
        "special_ability": "Guard Hide",
        "evolutions": (
            "Puddle Toad",
            "Brace Toad",
            "War Toad",
            "Bulwark Toad",
            "Elder Battle Toad",
        ),
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
        "evolutions": (
            "Duskwick Bat",
            "Redfang Bat",
            "Nightdrinker Bat",
            "Bloodmoon Bat",
            "Nocturne Bat",
        ),
    },
    "Direwolf": {
        "species": "Direwolf",
        "special_ability": "Pounce",
        "evolutions": ("Wolf Pup", "Trail Wolf", "Direwolf", "Pack Alpha", "Moonfang Alpha"),
    },
    "GiantScorpion": {
        "species": "Scorpion",
        "special_ability": "Guard Hide",
        "evolutions": (
            "Dust Scorpion",
            "Barbed Scorpion",
            "Iron Scorpion",
            "Venom Scorpion",
            "Dune Tyrant",
        ),
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
        "evolutions": (
            "Mud Snapper",
            "Marsh Gator",
            "Ironjaw Gator",
            "Bayou Gator",
            "Ancient Alligator",
        ),
    },
    "GoldenEagle": {
        "species": "Golden Eagle",
        "special_ability": "Wingbeat",
        "evolutions": (
            "Eaglet",
            "Golden Eagle",
            "Sunwing Eagle",
            "Highwind Eagle",
            "Sky Crown Eagle",
        ),
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


def duelist_style_active(character: Any) -> bool:
    """Return whether Duelist's single-weapon stance is currently valid."""
    if not has_skill(character, "Duelist"):
        return False
    weapon = getattr(character, "equipment", {}).get("Weapon")
    offhand = getattr(character, "equipment", {}).get("OffHand")
    offhand_subtype = getattr(offhand, "subtyp", None)
    ranger_crossbow = offhand_subtype == "Crossbow" and getattr(
        getattr(character, "cls", None), "name", None
    ) in {"Ranger", "Beast Master"}
    return bool(
        getattr(weapon, "typ", None) == "Weapon"
        and int(getattr(weapon, "handed", 1) or 1) == 1
        and (offhand_subtype == "None" or ranger_crossbow)
    )


def duelist_accuracy_bonus(character: Any) -> float:
    """Return Duelist's accuracy bonus for a valid stance."""
    return 0.10 if duelist_style_active(character) else 0.0


def duelist_critical_bonus(character: Any) -> float:
    """Return Duelist's critical chance bonus for a valid stance."""
    return 0.10 if duelist_style_active(character) else 0.0


def duelist_damage_multiplier(character: Any) -> float:
    """Return Duelist's melee damage multiplier for a valid stance."""
    return 1.10 if duelist_style_active(character) else 1.0


def cross_block_profile(character: Any) -> tuple[float, float] | None:
    """Return Cross Block chance and mitigation for a valid dual-wield setup."""
    if not has_skill(character, "Cross Block"):
        return None
    equipment = getattr(character, "equipment", {})
    main = equipment.get("Weapon")
    offhand = equipment.get("OffHand")
    if getattr(main, "typ", None) != "Weapon" or getattr(offhand, "typ", None) != "Weapon":
        return None
    strength = max(0, int(getattr(getattr(character, "stats", None), "strength", 0)))
    weapon_strength = sum(max(0, int(getattr(item, "damage", 0) or 0)) for item in (main, offhand))
    chance = min(0.75, 0.10 + ((strength + weapon_strength) / 200))
    mitigation = min(1.0, 0.25 + ((strength + weapon_strength) / 100))
    return chance, mitigation


def can_dual_wield_item(character: Any, item: Any, slot: str) -> bool:
    """Return whether Dual Wield unlocks this off-hand weapon."""
    return (
        slot == "OffHand"
        and getattr(getattr(character, "cls", None), "name", None)
        in {"Weapon Master", "Berserker", "Grandmaster of Arms"}
        and has_skill(character, "Dual Wield")
        and "weapon-master.ability.dual-wield"
        in getattr(
            getattr(character, "progression", None),
            "purchased_node_ids",
            set(),
        )
        and getattr(item, "typ", None) == "Weapon"
        and int(getattr(item, "handed", 1) or 1) == 1
        and getattr(item, "subtyp", None) in {"Fist", "Dagger", "Sword", "Club"}
    )


def dual_wield_accuracy_modifier(character: Any, slot: str) -> float:
    """Return the accuracy penalty for attacks made while dual wielding."""
    equipment = getattr(character, "equipment", {})
    if not has_skill(character, "Dual Wield"):
        return 0.0
    if any(getattr(equipment.get(key), "typ", None) != "Weapon" for key in ("Weapon", "OffHand")):
        return 0.0
    if has_skill(character, "Dual Wield Mastery"):
        return 0.0
    if slot == "Weapon" and has_skill(character, "Dual Wield Excellence"):
        return 0.0
    return -0.15


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
