"""Archdruid class definition and Fourfold Balance helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .base import Job
from .. import items

AFFINITIES = ("Venom", "Stone", "Growth", "Storm")
ENTRY_THRESHOLD = 50
MASTERY_THRESHOLD = 100
PRE_RITUAL_CAP = 99

CATALYSTS = {
    "Venom": ("Serpent Venom Heart", items.SerpentVenomHeart),
    "Stone": ("Heartstone Shard", items.HeartstoneShard),
    "Growth": ("Verdant Seed", items.VerdantSeed),
    "Storm": ("Stormglass Feather", items.StormglassFeather),
}

CATALYST_SOURCES = {
    "Basilisk": "Venom",
    "Shadow Serpent": "Venom",
    "Earth Myrmidon": "Stone",
    "Gargoyle": "Stone",
    "Xorn": "Stone",
    "Treant": "Growth",
    "Storm Myrmidon": "Storm",
    "Wind Myrmidon": "Storm",
}

HARD_CONTROL_EFFECTS = {"Prone", "Stun"}
STORM_TYPES = {"Electric", "Wind"}


class Archdruid(Job):
    """
    Promotion: Pathfinder -> Druid -> Archdruid
    Additional Pros: Much higher intel and wisdom gain
    Additional Cons: Lower strength and charisma gain; lose access to all weapons except staves and daggers;
        lose access to all armor except cloth
    Special Mechanic: Gains access to powerful nature magic; gain attunement with nature
        affinities Venom, Storm, Stone, and Growth
    """

    def __init__(self):
        super().__init__(
            name="Archdruid",
            description="The Archdruid is the ultimate embodiment of nature's power, a "
            "legendary figure who has mastered the ways of the natural world.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=1,
            cha_plus=0,
            dex_plus=1,
            att_plus=1,
            def_plus=2,
            magic_plus=4,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


def default_state() -> dict[str, Any]:
    return {
        "grove_unlocked": False,
        "ring_awakened": False,
        "attunement": {affinity: 0 for affinity in AFFINITIES},
        "aspects": {affinity: False for affinity in AFFINITIES},
        "catalysts": {affinity: False for affinity in AFFINITIES},
        "progress": {
            "Venom": {"poison_damage_taken": 0},
            "Stone": {"physical_damage_survived": 0},
            "Growth": {"healing_done": 0},
            "Storm": {"storm_damage_dealt": 0},
        },
    }


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if not isinstance(state, dict):
        return normalized

    normalized["ring_awakened"] = bool(state.get("ring_awakened", False))
    normalized["grove_unlocked"] = bool(state.get("grove_unlocked", False))

    attunement = state.get("attunement", {})
    if isinstance(attunement, dict):
        for affinity in AFFINITIES:
            normalized["attunement"][affinity] = _clamp_attunement(
                attunement.get(affinity, 0),
                aspect_unlocked=bool((state.get("aspects", {}) or {}).get(affinity, False)),
            )

    aspects = state.get("aspects", {})
    if isinstance(aspects, dict):
        for affinity in AFFINITIES:
            normalized["aspects"][affinity] = bool(aspects.get(affinity, False))

    catalysts = state.get("catalysts", {})
    if isinstance(catalysts, dict):
        for affinity in AFFINITIES:
            normalized["catalysts"][affinity] = bool(catalysts.get(affinity, False))

    progress = state.get("progress", {})
    if isinstance(progress, dict):
        for affinity in AFFINITIES:
            entry = progress.get(affinity, {})
            if not isinstance(entry, dict):
                continue
            for key, value in entry.items():
                try:
                    normalized["progress"][affinity][key] = max(0, int(value or 0))
                except (TypeError, ValueError):
                    normalized["progress"][affinity][key] = 0

    normalized["grove_unlocked"] = normalized[
        "grove_unlocked"
    ] or grove_requirements_met_from_state(normalized)
    if all(normalized["aspects"].values()):
        normalized["ring_awakened"] = bool(normalized["ring_awakened"])
    return normalized


def ensure_state(character: Any) -> dict[str, Any]:
    state = normalize_state(getattr(character, "archdruid_attunement", None))
    if is_archdruid(character) and grove_requirements_met_from_state(state):
        state["grove_unlocked"] = True
    setattr(character, "archdruid_attunement", state)
    apply_mastery_perks(character)
    return state


def copy_state(state: Any) -> dict[str, Any]:
    return deepcopy(normalize_state(state))


def is_archdruid(character: Any) -> bool:
    return getattr(getattr(character, "cls", None), "name", None) == "Archdruid"


def _clamp_attunement(value: Any, *, aspect_unlocked: bool) -> int:
    try:
        value = int(value or 0)
    except (TypeError, ValueError):
        value = 0
    cap = MASTERY_THRESHOLD if aspect_unlocked else PRE_RITUAL_CAP
    return max(0, min(cap, value))


def grove_requirements_met_from_state(state: dict[str, Any]) -> bool:
    attunement = state.get("attunement", {})
    return all(int(attunement.get(affinity, 0) or 0) >= ENTRY_THRESHOLD for affinity in AFFINITIES)


def grove_unlocked(character: Any) -> bool:
    return is_archdruid(character) and bool(ensure_state(character)["grove_unlocked"])


def adjust_attunement(character: Any, affinity: str, amount: int) -> tuple[int, int]:
    if affinity not in AFFINITIES or amount == 0 or not is_archdruid(character):
        return 0, 0
    state = ensure_state(character)
    try:
        from ..progression import has_talent

        memory_talents = {
            "Venom": "archdruid.patient-venom",
            "Stone": "archdruid.granite-memory",
            "Growth": "archdruid.verdant-memory",
            "Storm": "archdruid.storm-memory",
        }
        if amount > 0 and has_talent(character, memory_talents[affinity]):
            amount += 1
    except (AttributeError, KeyError, TypeError):
        pass
    before = int(state["attunement"][affinity])
    state["attunement"][affinity] = _clamp_attunement(
        before + int(amount),
        aspect_unlocked=state["aspects"][affinity],
    )
    if grove_requirements_met_from_state(state):
        state["grove_unlocked"] = True
    setattr(character, "archdruid_attunement", state)
    apply_mastery_perks(character)
    return before, int(state["attunement"][affinity])


def mastery_unlocked(character: Any, affinity: str) -> bool:
    if affinity not in AFFINITIES or not is_archdruid(character):
        return False
    state = ensure_state(character)
    return bool(state["aspects"][affinity] and state["attunement"][affinity] >= MASTERY_THRESHOLD)


def apply_mastery_perks(character: Any) -> None:
    if not is_archdruid(character):
        return
    state = normalize_state(getattr(character, "archdruid_attunement", None))
    immunities = getattr(character, "status_immunity", None)
    if not isinstance(immunities, list):
        return
    if (
        state["aspects"]["Venom"]
        and state["attunement"]["Venom"] >= MASTERY_THRESHOLD
        and "Poison" not in immunities
    ):
        immunities.append("Poison")
    if (
        state["aspects"]["Stone"]
        and state["attunement"]["Stone"] >= MASTERY_THRESHOLD
        and "Stone" not in immunities
    ):
        immunities.append("Stone")
    if state["aspects"]["Growth"] and state["attunement"]["Growth"] >= MASTERY_THRESHOLD:
        try:
            from .. import abilities

            spellbook = getattr(character, "spellbook", {}).setdefault("Spells", {})
            if "Tree of Life" not in spellbook:
                spellbook["Tree of Life"] = abilities.TreeOfLife()
        except Exception:
            pass


def record_status_applied(actor: Any, target: Any, status_name: str) -> None:
    if status_name == "Poison" and is_archdruid(actor):
        adjust_attunement(actor, "Venom", 1)
    if status_name in HARD_CONTROL_EFFECTS and is_archdruid(target):
        adjust_attunement(target, "Stone", -1)
    if status_name in {"Berserk", "Silence"} and is_archdruid(target):
        adjust_attunement(target, "Storm", -1)


def record_damage_dealt(character: Any, amount: int, damage_type: str) -> None:
    if not is_archdruid(character) or amount <= 0:
        return
    if damage_type in STORM_TYPES:
        _accumulate_progress(character, "Storm", "storm_damage_dealt", amount, threshold=100)


def record_damage_taken(character: Any, amount: int, damage_type: str) -> None:
    if not is_archdruid(character) or amount <= 0:
        return
    if damage_type == "Poison":
        _accumulate_progress(
            character, "Venom", "poison_damage_taken", amount, threshold=25, direction=-1
        )
    if damage_type == "Physical" and getattr(getattr(character, "health", None), "current", 0) > 0:
        adjust_attunement(character, "Stone", 1)
    if damage_type in STORM_TYPES and mastery_unlocked(character, "Storm"):
        mana = getattr(character, "mana", None)
        if mana is not None:
            restored = max(1, int(amount * 0.25))
            mana.current = min(mana.max, mana.current + restored)


def record_healing_done(character: Any, amount: int) -> None:
    if not is_archdruid(character) or amount <= 0:
        return
    _accumulate_progress(character, "Growth", "healing_done", amount, threshold=100)


def record_life_drain(character: Any) -> None:
    if is_archdruid(character):
        adjust_attunement(character, "Growth", -1)


def _accumulate_progress(
    character: Any,
    affinity: str,
    key: str,
    amount: int,
    *,
    threshold: int,
    direction: int = 1,
) -> None:
    state = ensure_state(character)
    entry = state["progress"][affinity]
    total = int(entry.get(key, 0) or 0) + max(0, int(amount or 0))
    points = total // threshold
    entry[key] = total % threshold
    setattr(character, "archdruid_attunement", state)
    if points:
        adjust_attunement(character, affinity, points * direction)


def has_equipped_class_ring(character: Any) -> bool:
    equipment = getattr(character, "equipment", {})
    ring = equipment.get("Ring") if isinstance(equipment, dict) else None
    return getattr(ring, "name", None) == "Class Ring"


def has_stored_class_ring(character: Any) -> bool:
    storage = getattr(character, "storage", {})
    if not isinstance(storage, dict):
        return False
    return any(
        getattr(item, "name", None) == "Class Ring" for item in storage.get("Class Ring", [])
    )


def has_visible_class_ring(character: Any) -> bool:
    return has_equipped_class_ring(character) or has_stored_class_ring(character)


def can_awaken_ring(character: Any) -> bool:
    state = ensure_state(character)
    return bool(
        is_archdruid(character)
        and has_visible_class_ring(character)
        and all(state["aspects"].values())
        and not state["ring_awakened"]
    )


def awaken_ring(character: Any) -> tuple[bool, str]:
    if not can_awaken_ring(character):
        return False, "The Class Ring waits for all four Grove aspects and a visible ring.\n"
    state = ensure_state(character)
    state["ring_awakened"] = True
    setattr(character, "archdruid_attunement", state)
    return True, "The Class Ring awakens in fourfold harmony.\n"


def harmony_bonus(character: Any) -> float:
    if not is_archdruid(character):
        return 0.0
    state = ensure_state(character)
    if not (state["ring_awakened"] and has_equipped_class_ring(character)):
        return 0.0
    total = sum(int(state["attunement"][affinity]) for affinity in AFFINITIES)
    bonus = (total // 25) * 0.01
    if all(int(state["attunement"][affinity]) >= 75 for affinity in AFFINITIES):
        bonus *= 2
    return min(0.40, bonus)


def catalyst_for_enemy(character: Any, enemy: Any) -> tuple[str, type[items.Misc]] | None:
    if not grove_unlocked(character):
        return None
    affinity = CATALYST_SOURCES.get(getattr(enemy, "name", ""))
    if affinity is None:
        return None
    state = ensure_state(character)
    if state["catalysts"][affinity] or state["aspects"][affinity]:
        return None
    return CATALYSTS[affinity]


def record_catalyst_obtained(character: Any, item_name: str) -> str | None:
    state = ensure_state(character)
    for affinity, (name, _item_cls) in CATALYSTS.items():
        if item_name == name:
            state["catalysts"][affinity] = True
            setattr(character, "archdruid_attunement", state)
            return affinity
    return None


def perform_ritual(character: Any, affinity: str) -> tuple[bool, str]:
    if affinity not in AFFINITIES:
        return False, "The Grove does not answer that ritual.\n"
    state = ensure_state(character)
    if not state["grove_unlocked"]:
        return False, "The Ancient Grove remains hidden until the four affinities reach balance.\n"
    if state["aspects"][affinity]:
        return True, f"The {affinity} aspect is already awake.\n"
    catalyst_name, catalyst_cls = CATALYSTS[affinity]
    inventory = getattr(character, "special_inventory", {})
    if catalyst_name not in inventory:
        return False, f"The {affinity} ritual requires {catalyst_name}.\n"

    state["aspects"][affinity] = True
    state["catalysts"][affinity] = True
    setattr(character, "archdruid_attunement", state)
    character.modify_inventory(catalyst_cls(), subtract=True, rare=True)
    message = _ritual_message(affinity)
    success, awaken_message = awaken_ring(character)
    if success:
        message += awaken_message
    return True, message


def _ritual_message(affinity: str) -> str:
    if affinity == "Venom":
        return "The venom trial is endured, cleansed, and turned back into living medicine.\n"
    if affinity == "Stone":
        return "The stone trial breaks around you, but you remain standing.\n"
    if affinity == "Growth":
        return "The wounded Grove drinks your restoration and blooms again.\n"
    if affinity == "Storm":
        return "The storm trial arcs through the ring and bends to your will.\n"
    return "The Grove accepts the ritual.\n"


def aspect_summary(character: Any) -> str:
    state = ensure_state(character)
    return ", ".join(
        f"{affinity} {'awake' if state['aspects'][affinity] else 'sealed'}"
        for affinity in AFFINITIES
    )
