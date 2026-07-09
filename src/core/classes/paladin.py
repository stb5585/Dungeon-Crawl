"""Paladin class definition."""

from __future__ import annotations

import copy
import random
from typing import Any

from .base import Job


class Paladin(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can cast healing spells; additional wisdom and charisma gain
    Cons: Cannot equip 2-handed weapons except hammers and cannot equip light armor; no dex
        and lower strength gain
    Special Mechanic: Oathbringer - choose a path of devotion that grants unique abilities
        and buffs  TODO
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
            restrictions={
                "Weapon": ["Sword", "Club", "Longsword", "Hammer"],
                "OffHand": ["Shield"],
                "Armor": ["Medium", "Heavy"],
            },
            pro_level=2,
        )


PATHS = ("Redemption", "Conquest", "Protection", "Retribution")

SKILL_NAMES = {
    "Redemption": "Redeem",
    "Conquest": "Challenge",
    "Protection": "Interpose",
    "Retribution": "Judgment Riposte",
}

SKILL_CLASS_NAMES = {
    "Redemption": "Redeem",
    "Conquest": "Challenge",
    "Protection": "Interpose",
    "Retribution": "JudgmentRiposte",
}

DESCRIPTIONS = {
    "Redemption": (
        "Redeem offers wounded foes a chance to yield. Mercy can still be "
        "rewarding, especially when your oath is burning bright, but it turns "
        "away from trophies and bloody renown."
    ),
    "Conquest": (
        "Challenge names a foe and presses the fight toward a decisive end. "
        "Victories against chosen or hunted enemies feed your commanding aura."
    ),
    "Protection": (
        "Interpose commits you to a guarded stand. Timely blocks turn defense "
        "into protective momentum for the battles ahead."
    ),
    "Retribution": (
        "Judgment Riposte waits for enemy aggression and answers it with holy "
        "reprisal. Clean vengeance can leave your aura burning brighter."
    ),
}

AURA_NAMES = {
    "Redemption": "Redemption Aura",
    "Conquest": "Conquest Aura",
    "Protection": "Protection Aura",
    "Retribution": "Retribution Aura",
}

MARK_NAMES = {
    "Redemption": "Mark of Perdition",
    "Conquest": "Mark of the Craven",
    "Protection": "Mark of Vulnerability",
    "Retribution": "Mark of Mercy",
}


def default_state() -> dict[str, Any]:
    return {
        "path": None,
        "aura": {
            "name": None,
            "turns": 0,
            "encounters": 0,
            "stacks": 0,
            "doubled": False,
        },
        "mark": {
            "name": None,
            "turns": 0,
            "encounters": 0,
            "active": False,
            "data": {},
        },
        "challenge": {"target_id": None, "turns": 0},
        "interpose": {"turns": 0, "spent": False},
        "riposte": {"turns": 0, "spent": False},
    }


def normalize_path(vow_path: Any) -> str | None:
    if isinstance(vow_path, dict):
        vow_path = vow_path.get("path")
    if vow_path is None:
        return None
    text = str(vow_path).strip().lower()
    for candidate in PATHS:
        if text == candidate.lower():
            return candidate
    return None


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if isinstance(state, str):
        normalized["path"] = normalize_path(state)
        return normalized
    if not isinstance(state, dict):
        return normalized

    normalized["path"] = normalize_path(state.get("path"))
    for key in ("aura", "mark", "challenge", "interpose", "riposte"):
        incoming = state.get(key, {})
        if isinstance(incoming, dict):
            normalized[key].update(copy.deepcopy(incoming))

    aura = normalized["aura"]
    aura["name"] = str(aura["name"]) if aura.get("name") else None
    aura["turns"] = max(0, int(aura.get("turns", 0) or 0))
    aura["encounters"] = max(0, int(aura.get("encounters", 0) or 0))
    aura["stacks"] = max(0, int(aura.get("stacks", 0) or 0))
    aura["doubled"] = bool(aura.get("doubled", False))

    mark = normalized["mark"]
    mark["name"] = str(mark["name"]) if mark.get("name") else None
    mark["turns"] = max(0, int(mark.get("turns", 0) or 0))
    mark["encounters"] = max(0, int(mark.get("encounters", 0) or 0))
    mark["active"] = bool(mark.get("active", False))
    mark["data"] = mark.get("data") if isinstance(mark.get("data"), dict) else {}

    for key in ("challenge", "interpose", "riposte"):
        data = normalized[key]
        data["turns"] = max(0, int(data.get("turns", 0) or 0))
    normalized["interpose"]["spent"] = bool(normalized["interpose"].get("spent", False))
    normalized["riposte"]["spent"] = bool(normalized["riposte"].get("spent", False))
    return normalized


def ensure_state(character: Any) -> dict[str, Any]:
    state = normalize_state(getattr(character, "paladin_vow", None))
    setattr(character, "paladin_vow", state)
    return state


def path(character: Any) -> str | None:
    return ensure_state(character).get("path")


def is_paladin_lineage(character: Any) -> bool:
    return getattr(getattr(character, "cls", None), "name", None) in {"Paladin", "Crusader"}


def choose_vow(character: Any, vow_path: Any) -> tuple[bool, str]:
    state = ensure_state(character)
    selected = normalize_path(vow_path)
    if not selected:
        return False, "That vow path is not recognized.\n"
    existing = normalize_path(state.get("path"))
    if existing and existing != selected:
        return False, f"The Vow of {existing} is already sworn.\n"

    state["path"] = selected
    grant_signature_skill(character, selected)
    return True, f"You swear the Vow of {selected} and learn {SKILL_NAMES[selected]}.\n"


def grant_signature_skill(character: Any, vow_path: Any | None = None) -> bool:
    selected = normalize_path(vow_path) or path(character)
    if not selected:
        return False
    try:
        from src.core import abilities

        cls = getattr(abilities, SKILL_CLASS_NAMES[selected])
        skill = cls()
        character.spellbook.setdefault("Skills", {})[skill.name] = skill
        return True
    except Exception:
        return False


def has_affirmation(character: Any) -> bool:
    try:
        from . import class_rings

        return (
            class_rings.is_awakened(character, "Crusader")
            and class_rings.has_equipped_class_ring(character)
        )
    except Exception:
        return False


def aura_multiplier(character: Any) -> float:
    return 1.5 if has_affirmation(character) else 1.0


def mark_multiplier(character: Any) -> float:
    return 0.5 if has_affirmation(character) else 1.0


def adjusted_mark_duration(character: Any, base: int) -> int:
    return max(1, int(round(base * mark_multiplier(character))))


def clear_aura(character: Any) -> None:
    state = ensure_state(character)
    state["aura"] = default_state()["aura"]


def clear_mark(character: Any) -> None:
    state = ensure_state(character)
    state["mark"] = default_state()["mark"]


def trigger_aura(character: Any, vow_path: Any | None = None, doubled: bool = False) -> str:
    selected = normalize_path(vow_path) or path(character)
    if not selected:
        return ""
    state = ensure_state(character)
    aura = state["aura"]
    aura["name"] = AURA_NAMES[selected]
    aura["doubled"] = bool(doubled)
    if selected == "Protection":
        aura["turns"] = 2
        aura["encounters"] = 0
        aura["stacks"] = min(5, max(1, int(aura.get("stacks", 0) or 0) + 1))
    elif selected == "Conquest":
        aura["turns"] = 0
        aura["encounters"] = 3
        aura["stacks"] = min(3, max(1, int(aura.get("stacks", 0) or 0) + 1))
    elif selected == "Retribution":
        aura["turns"] = 0
        aura["encounters"] = 6 if doubled else 3
        aura["stacks"] = 1
    else:
        aura["turns"] = 0
        aura["encounters"] = 3
        aura["stacks"] = 1
    return f"{AURA_NAMES[selected]} answers your vow.\n"


def apply_mark(character: Any, vow_path: Any | None = None) -> str:
    selected = normalize_path(vow_path) or path(character)
    if not selected:
        return ""
    state = ensure_state(character)
    mark = state["mark"]
    mark["name"] = MARK_NAMES[selected]
    mark["active"] = True
    mark["data"] = {}
    if selected == "Redemption":
        mark["encounters"] = adjusted_mark_duration(character, 3)
        mark["turns"] = 0
    elif selected == "Protection":
        mark["encounters"] = 0
        mark["turns"] = 1
    else:
        mark["encounters"] = 0
        mark["turns"] = 0
    return f"{MARK_NAMES[selected]} settles on you.\n"


def tick_turn(character: Any) -> None:
    state = ensure_state(character)
    for key in ("challenge", "interpose", "riposte"):
        state[key]["turns"] = max(0, int(state[key].get("turns", 0) or 0) - 1)
        if not state[key]["turns"] and key in {"interpose", "riposte"}:
            state[key]["spent"] = False
    aura = state["aura"]
    if aura.get("turns"):
        aura["turns"] = max(0, int(aura.get("turns", 0) or 0) - 1)
        if aura["turns"] <= 0:
            clear_aura(character)
    mark = state["mark"]
    if mark.get("turns"):
        mark["turns"] = max(0, int(mark.get("turns", 0) or 0) - 1)
        if mark["turns"] <= 0:
            clear_mark(character)


def advance_encounter(character: Any) -> None:
    state = ensure_state(character)
    aura = state["aura"]
    if aura.get("encounters"):
        aura["encounters"] = max(0, int(aura.get("encounters", 0) or 0) - 1)
        if aura["encounters"] <= 0:
            clear_aura(character)
    mark = state["mark"]
    if mark.get("encounters"):
        mark["encounters"] = max(0, int(mark.get("encounters", 0) or 0) - 1)
        if mark["encounters"] <= 0:
            clear_mark(character)


def aura_active(character: Any, aura_name: str) -> bool:
    aura = ensure_state(character)["aura"]
    if aura.get("name") != aura_name:
        return False
    return bool(aura.get("stacks", 0) or aura.get("turns", 0) or aura.get("encounters", 0))


def mark_active(character: Any, mark_name: str) -> bool:
    mark = ensure_state(character)["mark"]
    return bool(mark.get("active") and mark.get("name") == mark_name)


def redemption_reward_multiplier(character: Any) -> float:
    multiplier = 1.0
    if aura_active(character, "Redemption Aura"):
        multiplier += 0.20 * aura_multiplier(character)
    if mark_active(character, "Mark of Perdition"):
        multiplier -= 0.20 * mark_multiplier(character)
    return max(0.0, multiplier)


def encounter_rate_multiplier(character: Any) -> float:
    multiplier = 1.0
    if aura_active(character, "Redemption Aura"):
        multiplier -= 0.25 * aura_multiplier(character)
    if mark_active(character, "Mark of Perdition"):
        multiplier += 0.25 * mark_multiplier(character)
    return max(0.05, multiplier)


def conquest_damage_multiplier(character: Any, target: Any | None = None) -> float:
    state = ensure_state(character)
    multiplier = 1.0
    if aura_active(character, "Conquest Aura"):
        stacks = max(1, int(state["aura"].get("stacks", 1) or 1))
        multiplier += (0.05 * stacks) * aura_multiplier(character)
    if mark_active(character, "Mark of the Craven"):
        multiplier -= 0.10 * mark_multiplier(character)
    if target is not None and challenge_matches(character, target):
        multiplier += 0.15 * aura_multiplier(character)
    return max(0.0, multiplier)


def initiative_multiplier(character: Any) -> float:
    state = ensure_state(character)
    multiplier = 1.0
    if aura_active(character, "Conquest Aura"):
        stacks = max(1, int(state["aura"].get("stacks", 1) or 1))
        multiplier += (0.05 * stacks) * aura_multiplier(character)
    if mark_active(character, "Mark of the Craven"):
        multiplier -= 0.10 * mark_multiplier(character)
    return max(0.0, multiplier)


def protection_block_bonus(character: Any) -> float:
    state = ensure_state(character)
    bonus = 0.0
    if aura_active(character, "Protection Aura"):
        bonus += 0.03 * int(state["aura"].get("stacks", 1) or 1) * aura_multiplier(character)
    if state["interpose"].get("turns") and not state["interpose"].get("spent"):
        bonus += 0.35
    return bonus


def protection_mitigation_bonus(character: Any) -> float:
    state = ensure_state(character)
    bonus = 0.0
    if aura_active(character, "Protection Aura"):
        bonus += 0.05 * int(state["aura"].get("stacks", 1) or 1) * aura_multiplier(character)
    if state["interpose"].get("turns") and not state["interpose"].get("spent"):
        bonus += 0.35
    return bonus


def incoming_damage_multiplier(character: Any, damage_type: str = "Physical") -> float:
    if damage_type in {"Physical", "Melee"} and mark_active(character, "Mark of Vulnerability"):
        return 1.0 + (0.20 * mark_multiplier(character))
    return 1.0


def retribution_dodge_bonus(character: Any) -> float:
    if aura_active(character, "Retribution Aura"):
        return 0.10 * aura_multiplier(character)
    return 0.0


def retribution_crit_damage_multiplier(character: Any) -> float:
    if aura_active(character, "Retribution Aura"):
        return 1.0 + (0.15 * aura_multiplier(character))
    return 1.0


def mercy_lethal_threshold(character: Any) -> float:
    return 0.05 if has_affirmation(character) else 0.10


def challenge_matches(character: Any, target: Any) -> bool:
    state = ensure_state(character)
    return (
        int(state["challenge"].get("turns", 0) or 0) > 0
        and state["challenge"].get("target_id") == id(target)
    )


def start_challenge(character: Any, target: Any) -> str:
    if path(character) != "Conquest":
        return "Only the Vow of Conquest can issue Challenge.\n"
    state = ensure_state(character)
    state["challenge"] = {"target_id": id(target), "turns": 3}
    return f"{target.name} is named your Challenged Foe for 3 turns.\n"


def start_interpose(character: Any) -> str:
    if path(character) != "Protection":
        return "Only the Vow of Protection can Interpose.\n"
    state = ensure_state(character)
    state["interpose"] = {"turns": 2, "spent": False}
    return f"{character.name} enters a guarded stance for 2 turns.\n"


def start_riposte(character: Any) -> str:
    if path(character) != "Retribution":
        return "Only the Vow of Retribution can prepare Judgment Riposte.\n"
    if weapon_missing(character):
        return apply_mark(character, "Retribution")
    state = ensure_state(character)
    state["riposte"] = {"turns": 2, "spent": False}
    return f"{character.name} prepares a retaliatory judgment for 2 turns.\n"


def weapon_missing(character: Any) -> bool:
    weapon = getattr(character, "equipment", {}).get("Weapon")
    return weapon is None or getattr(weapon, "subtyp", "None") == "None" or getattr(character, "is_disarmed", lambda: False)()


def block_succeeded(character: Any) -> str:
    state = ensure_state(character)
    if state["interpose"].get("turns") and not state["interpose"].get("spent"):
        state["interpose"]["spent"] = True
    if path(character) == "Protection":
        return trigger_aura(character, "Protection")
    return ""


def redeem_chance(character: Any, target: Any) -> float:
    if target is None or mercy_immune(target):
        return 0.0
    hp_max = max(1, int(getattr(getattr(target, "health", None), "max", 1) or 1))
    missing_ratio = max(0.0, min(1.0, (hp_max - getattr(target.health, "current", hp_max)) / hp_max))
    stats_bonus = (int(getattr(character.stats, "charisma", 0)) + int(getattr(character.stats, "wisdom", 0))) / 300.0
    chance = 0.10 + stats_bonus + (missing_ratio * 0.45)
    if aura_active(character, "Redemption Aura"):
        chance += 0.10 * aura_multiplier(character)
    return max(0.10, min(0.90, chance))


def mercy_immune(target: Any) -> bool:
    if bool(getattr(target, "mercy_immune", False)):
        return True
    if "Boss" in str(getattr(target, "__class__", type(target)).__name__):
        return True
    if bool(getattr(target, "class_ring_trial", False)):
        return True
    return bool(getattr(target, "is_boss", False))


def attempt_redeem(character: Any, target: Any, rng: Any | None = None) -> str:
    if path(character) != "Redemption":
        return "Only the Vow of Redemption can use Redeem.\n"
    if mercy_immune(target):
        return f"{target.name} refuses mercy.\n"
    rng = rng or random
    chance = redeem_chance(character, target)
    if rng.random() <= chance:
        target.health.current = 0
        setattr(target, "paladin_mercy_victory", True)
        return trigger_aura(character, "Redemption") + f"{target.name} yields to mercy.\n"
    return f"{target.name} rejects mercy.\n"


def on_enemy_defeated(character: Any, enemy: Any, bounty_target: bool = False, mercy: bool = False) -> str:
    if mercy:
        return ""
    selected = path(character)
    if selected == "Redemption":
        clear_aura(character)
        return apply_mark(character, "Redemption")
    if selected == "Conquest" and (challenge_matches(character, enemy) or bounty_target):
        ensure_state(character)["challenge"] = {"target_id": None, "turns": 0}
        if bounty_target and mark_active(character, "Mark of the Craven"):
            clear_mark(character)
        return trigger_aura(character, "Conquest")
    return ""


def on_flee(character: Any, success: bool) -> str:
    if success and path(character) == "Conquest":
        return apply_mark(character, "Conquest")
    return ""


def on_incapacitated(character: Any) -> str:
    if path(character) == "Protection":
        return apply_mark(character, "Protection")
    return ""


def clear_transient_marks(character: Any) -> None:
    state = ensure_state(character)
    mark = state["mark"]
    if mark.get("name") == "Mark of Vulnerability" and not getattr(character, "incapacitated", lambda: False)():
        clear_mark(character)
    if mark.get("name") == "Mark of Mercy" and not weapon_missing(character):
        clear_mark(character)


def pending_riposte(character: Any) -> bool:
    state = ensure_state(character)
    return bool(state["riposte"].get("turns") and not state["riposte"].get("spent"))


def resolve_riposte(character: Any, target: Any) -> str:
    state = ensure_state(character)
    if not pending_riposte(character):
        return ""
    state["riposte"]["spent"] = True
    if weapon_missing(character):
        state["riposte"]["turns"] = 0
        return apply_mark(character, "Retribution")
    damage = max(1, int(character.check_mod("weapon", enemy=target) * 0.75))
    damage += max(1, int(character.check_mod("heal", enemy=target) * 0.25))
    target.health.current -= damage
    message = f"{character.name}'s Judgment Riposte strikes {target.name} for {damage} Holy damage.\n"
    if getattr(target.health, "current", 1) <= 0:
        message += trigger_aura(character, "Retribution", doubled=True)
    ensure_state(character)["riposte"] = {"turns": 0, "spent": True}
    return message


def mercy_lethal_message(character: Any, incoming_damage: int) -> str:
    if incoming_damage <= 0 or not mark_active(character, "Mark of Mercy"):
        return ""
    hp_max = max(1, int(getattr(character.health, "max", 1) or 1))
    if character.health.current / hp_max <= mercy_lethal_threshold(character):
        character.health.current = 0
        return f"{MARK_NAMES['Retribution']} turns mercy into a fatal opening.\n"
    return ""
