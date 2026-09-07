"""Shared Thieves Guild progression rules and state."""

from __future__ import annotations

from typing import Any

UNLOCK_LEVEL = 10
DISCOUNT_MULTIPLIER = 0.75
SIGNET_NAME = "Thieves Guild Signet"
TRIAL_LEVEL = 2
# Player-facing hint tile: an enterable approach beside the false wall.
TRIAL_HINT_POS = (15, 0, TRIAL_LEVEL)
# Internal injected tiles for the hidden trial room.
TRIAL_ENTRY_POS = (15, 0, TRIAL_LEVEL)
TRIAL_FAKE_WALL_POS = (15, 1, TRIAL_LEVEL)
TRIAL_BOSS_POS = (15, 2, TRIAL_LEVEL)

PROMOTED_FOOTPAD_CLASSES = {
    "Thief",
    "Rogue",
    "Inquisitor",
    "Seeker",
    "Assassin",
    "Ninja",
    "Spell Stealer",
    "Arcane Trickster",
}

BRANCH_BY_CLASS = {
    "Thief": "cutpurse",
    "Rogue": "cutpurse",
    "Inquisitor": "inquest",
    "Seeker": "inquest",
    "Assassin": "contract",
    "Ninja": "contract",
    "Spell Stealer": "arcane",
    "Arcane Trickster": "arcane",
}

BRANCH_LABELS = {
    "cutpurse": "Cutpurse Trial",
    "inquest": "Counterfeit Ledger Trial",
    "contract": "Silent Contract Trial",
    "arcane": "Spell-Sealed Coffer Trial",
}


def default_state() -> dict[str, Any]:
    return {
        "member": False,
        "trial_started": False,
        "trial_branch": "",
        "starter_kit_claimed": False,
    }


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if isinstance(state, dict):
        normalized["member"] = bool(state.get("member", False))
        normalized["trial_started"] = bool(state.get("trial_started", False))
        branch = str(state.get("trial_branch", "") or "")
        normalized["trial_branch"] = branch if branch in BRANCH_LABELS else ""
        normalized["starter_kit_claimed"] = bool(state.get("starter_kit_claimed", False))
    return normalized


def ensure_state(character: Any) -> dict[str, Any]:
    character.thieves_guild = normalize_state(getattr(character, "thieves_guild", None))
    return character.thieves_guild


def class_name(character: Any) -> str:
    return str(getattr(getattr(character, "cls", None), "name", "") or "")


def player_level(character: Any) -> int:
    level_fn = getattr(character, "player_level", None)
    if callable(level_fn):
        try:
            return int(level_fn() or 1)
        except (TypeError, ValueError):
            return 1
    level = getattr(character, "level", None)
    try:
        return int(getattr(level, "level", 1) or 1)
    except (TypeError, ValueError):
        return 1


def location_unlocked(character: Any) -> bool:
    return player_level(character) >= UNLOCK_LEVEL


def can_join(character: Any) -> bool:
    return class_name(character) in PROMOTED_FOOTPAD_CLASSES


def member(character: Any) -> bool:
    return bool(ensure_state(character).get("member"))


def branch_for(character: Any) -> str:
    return BRANCH_BY_CLASS.get(class_name(character), "")


def branch_label(branch: str) -> str:
    return BRANCH_LABELS.get(branch, "Initiation Trial")


def trial_hint_text() -> str:
    x, y, z = TRIAL_HINT_POS
    return f"dungeon level {z} near {x},{y},{z}"


def start_trial(character: Any) -> tuple[bool, str]:
    state = ensure_state(character)
    if state["member"]:
        return False, "You already carry the guild's mark."
    if not can_join(character):
        return False, "The backroom only sponsors promoted Footpad-line candidates."
    branch = branch_for(character)
    if not branch:
        return False, "The guild cannot find a trial suited to your path."
    state["trial_started"] = True
    state["trial_branch"] = branch
    return True, branch


def has_signet(character: Any) -> bool:
    inventory = getattr(character, "special_inventory", {}) or {}
    return SIGNET_NAME in inventory


def complete_membership(character: Any) -> tuple[bool, str]:
    state = ensure_state(character)
    if state["member"]:
        return False, "The Gray Broker taps the mark you already carry. You are known here."
    if not can_join(character):
        return (
            False,
            "Mara smiles without opening the ledger. Only promoted Footpad-line candidates join.",
        )
    if not has_signet(character):
        return (
            False,
            "Bring the Thieves Guild Signet from the hidden trial room on dungeon level 2.",
        )
    state["member"] = True
    state["trial_started"] = True
    if not state["trial_branch"]:
        state["trial_branch"] = branch_for(character)
    return True, "The Gray Broker accepts the signet and opens the backroom ledger to your name."
