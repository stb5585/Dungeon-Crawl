"""Dragoon class definition and dragon quest helpers."""

from __future__ import annotations

from typing import Any

from .base import Job


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
            restrictions={
                "Weapon": ["Sword", "Polearm"],
                "OffHand": ["Shield"],
                "Armor": ["Heavy"],
            },
            pro_level=3,
        )


QUEST_FLAGS = (
    "kaelenon_restored",
    "portal_key_obtained",
    "kaelenon_returned_home",
    "draconite_claimed",
    "pendant_crafted",
)

LANCER_LINEAGE = {"Lancer", "Dragoon"}
PORTAL_KEY_NAME = "Kaelenon's Portal Key"
DRACONITE_NAME = "Draconite"
DRACONITE_PENDANT_NAME = "Draconite Pendant"


def default_state() -> dict[str, bool]:
    return {flag: False for flag in QUEST_FLAGS}


def normalize_state(state: Any) -> dict[str, bool]:
    normalized = default_state()
    if isinstance(state, dict):
        for flag in QUEST_FLAGS:
            normalized[flag] = bool(state.get(flag, False))
    return normalized


def ensure_state(character) -> dict[str, bool]:
    state = normalize_state(getattr(character, "dragoon_dragon_quest", None))
    setattr(character, "dragoon_dragon_quest", state)
    return state


def is_lancer_lineage(character) -> bool:
    return getattr(getattr(character, "cls", None), "name", None) in LANCER_LINEAGE


def _has_special_item(character, item_name: str) -> bool:
    return item_name in getattr(character, "special_inventory", {})


def _add_special_item(character, item) -> None:
    if hasattr(character, "modify_inventory"):
        try:
            character.modify_inventory(item, rare=True)
            return
        except TypeError:
            pass
    inventory = getattr(character, "special_inventory", None)
    if isinstance(inventory, dict):
        inventory.setdefault(item.name, []).append(item)


def _remove_special_item(character, item_name: str) -> bool:
    inventory = getattr(character, "special_inventory", {})
    bucket = inventory.get(item_name)
    if not bucket:
        return False
    item = bucket[0] if isinstance(bucket, list) else bucket
    if hasattr(character, "modify_inventory"):
        try:
            character.modify_inventory(item, subtract=True, rare=True)
            return True
        except TypeError:
            pass
    if isinstance(bucket, list):
        bucket.pop(0)
        if not bucket:
            del inventory[item_name]
    else:
        del inventory[item_name]
    return True


def has_draconite_pendant(character) -> bool:
    pendant = getattr(character, "equipment", {}).get("Pendant")
    return getattr(pendant, "name", None) == DRACONITE_PENDANT_NAME


def recover_amounts(character) -> tuple[int, int]:
    """Return Jump Recover HP/MP restoration, including Draconite Pendant bonus."""
    pct = 0.10 if has_draconite_pendant(character) else 0.05
    hp_recover = int(getattr(character.health, "max", 0) * pct)
    mp_recover = int(getattr(character.mana, "max", 0) * pct)
    return hp_recover, mp_recover


def try_restore_kaelenon(
    actor, target, modifications: dict[str, bool], messages: list[str]
) -> bool:
    """Resolve the Lancer/Dragoon Recover Jump alternate Red Dragon victory."""
    if not modifications.get("Recover"):
        return False
    if getattr(target, "name", None) != "Red Dragon":
        return False
    if not is_lancer_lineage(actor):
        return False

    state = ensure_state(actor)
    target.kaelenon_restored = True
    target.health.current = min(0, getattr(target.health, "current", 0))
    if not state["kaelenon_restored"]:
        state["kaelenon_restored"] = True
        messages.append(
            "Recover pours through the Red Dragon's ruined shape. "
            "It does not mend Kaelenon's wounds; it restores the lost "
            "thread that lets them become humanoid again.\n"
        )
        messages.append(
            "Kaelenon collapses out of dragon form, alive and lucid, "
            "and begs for a way home from this realm.\n"
        )
    else:
        messages.append(
            "Recover resonates with Kaelenon's restored essence, ending the dragon's fury.\n"
        )
    return True


def red_dragon_victory_text(enemy) -> str:
    if not getattr(enemy, "kaelenon_restored", False):
        return ""
    return (
        "Kaelenon is restored, no longer trapped in dragon form. "
        "They ask you to seek a portal key in the Realm of Cambion.\n"
    )


def has_pending_terminal_branch(character) -> bool:
    state = ensure_state(character)
    if not state["kaelenon_restored"]:
        return False
    return not state["portal_key_obtained"] or not state["kaelenon_returned_home"]


def resolve_terminal_branch(character) -> str:
    """Advance Kaelenon's Cambion terminal follow-up, if available."""
    state = ensure_state(character)
    if not state["kaelenon_restored"]:
        return ""
    if not state["portal_key_obtained"]:
        state["portal_key_obtained"] = True
        from ..items import KaelenonPortalKey

        if not _has_special_item(character, PORTAL_KEY_NAME):
            _add_special_item(character, KaelenonPortalKey())
        return (
            "The terminal recognizes Kaelenon's restored essence and prints "
            "a glass-dark key from the portal lattice. You obtained "
            "Kaelenon's Portal Key."
        )
    if not state["kaelenon_returned_home"]:
        state["kaelenon_returned_home"] = True
        state["draconite_claimed"] = True
        from ..items import Draconite

        if not _has_special_item(character, DRACONITE_NAME):
            _add_special_item(character, Draconite())
        return (
            "Kaelenon's Portal Key turns in the terminal without touching it. "
            "A doorway of red starlight opens, and Kaelenon returns home. "
            "In thanks, they leave you Draconite."
        )
    return ""


def can_craft_draconite_pendant(character) -> bool:
    state = ensure_state(character)
    return (
        state["draconite_claimed"]
        and not state["pendant_crafted"]
        and _has_special_item(character, DRACONITE_NAME)
    )


def craft_draconite_pendant(character) -> tuple[bool, str]:
    if not can_craft_draconite_pendant(character):
        return False, "The Jeweler needs Draconite before crafting this pendant."

    from ..items import DraconitePendant

    _remove_special_item(character, DRACONITE_NAME)
    _add_special_item(character, DraconitePendant())
    ensure_state(character)["pendant_crafted"] = True
    return (
        True,
        "The Jeweler cuts the Draconite around a quiet red spark. "
        "You received the Draconite Pendant.",
    )
