"""Persistent Druid and Lycan form state and overlay handling."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

FORM_NODE_IDS = {
    "Druid": {
        "Panther": "druid.ability.transform",
        "Direbear": "druid.ability.transform2",
    },
    "Lycan": {"Werewolf": "lycan.ability.transform3"},
}

FORM_COMPATIBLE_SKILLS = {
    "Druid": frozenset({"Mortal Strike"}),
    "Lycan": frozenset({"Charge", "Battle Cry", "Mortal Strike", "Winged Pounce"}),
}

STAT_NAMES = ("strength", "intel", "wisdom", "con", "charisma", "dex")
FORM_EQUIPMENT_SLOTS = ("Weapon", "Armor", "OffHand")


def permanent_class_name(character: Any) -> str:
    """Return the character's progression class even while shifted."""
    snapshot = getattr(character, "_normal_form_snapshot", None)
    if isinstance(snapshot, dict):
        return str(getattr(snapshot.get("cls"), "name", "") or "")
    return str(
        getattr(character, "_normal_class_name", "")
        or getattr(getattr(character, "cls", None), "name", "")
    )


def is_transformed(character: Any) -> bool:
    """Return whether a persistent form overlay is active."""
    return bool(getattr(character, "_transformed", False))


def available_forms(character: Any) -> tuple[str, ...]:
    """Return forms unlocked by purchased progression nodes."""
    class_name = permanent_class_name(character)
    purchased = set(getattr(getattr(character, "progression", None), "purchased_node_ids", ()))
    return tuple(
        form_name
        for form_name, node_id in FORM_NODE_IDS.get(class_name, {}).items()
        if node_id in purchased
    )


def _form_creature(form_name: str) -> Any:
    from .. import enemies

    constructors = {
        "Panther": enemies.Panther,
        "Direbear": enemies.Direbear,
        "Werewolf": enemies.Werewolf,
    }
    try:
        return constructors[form_name]()
    except KeyError as exc:
        raise ValueError(f"Unknown transformation form: {form_name}") from exc


def _normal_snapshot(character: Any) -> dict[str, Any]:
    return {
        "cls": character.cls,
        "health": character.health,
        "mana": character.mana,
        "stats": character.stats,
        "equipment": character.equipment,
        "spellbook": character.spellbook,
        "resistance": character.resistance,
    }


def build_overlay(form_name: str) -> dict[str, Any]:
    """Generate the exact additive/replacement overlay for a form."""
    creature = _form_creature(form_name)
    return {
        "health_bonus": int(creature.health.max),
        "mana_bonus": int(creature.mana.max),
        "stats": {name: int(getattr(creature.stats, name)) for name in STAT_NAMES},
        "equipment": {slot: deepcopy(creature.equipment[slot]) for slot in FORM_EQUIPMENT_SLOTS},
        "spellbook": deepcopy(creature.spellbook),
        "resistance": deepcopy(creature.resistance),
    }


def _merge_form_compatible_skills(
    character: Any,
    overlay_spellbook: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    spellbook = deepcopy(overlay_spellbook)
    spellbook.setdefault("Spells", {})
    spellbook.setdefault("Skills", {})
    snapshot = getattr(character, "_normal_form_snapshot", {})
    normal_skills = snapshot.get("spellbook", {}).get("Skills", {})
    compatible = FORM_COMPATIBLE_SKILLS.get(permanent_class_name(character), frozenset())
    for name in compatible:
        if name in normal_skills:
            spellbook["Skills"][name] = normal_skills[name]
    return spellbook


def apply_form(
    character: Any,
    form_name: str,
    *,
    overlay: dict[str, Any] | None = None,
    force: bool = False,
) -> str:
    """Apply one persistent form overlay while retaining canonical normal state."""
    if is_transformed(character):
        return "Dismiss the current form before transforming again."
    if not force and form_name not in available_forms(character):
        return f"{form_name} has not been unlocked."
    overlay = deepcopy(overlay) if overlay is not None else build_overlay(form_name)
    character._normal_form_snapshot = _normal_snapshot(character)
    character._normal_class_name = getattr(character.cls, "name", "")
    normal = character._normal_form_snapshot
    health_deficit = max(0, normal["health"].max - normal["health"].current)
    mana_deficit = max(0, normal["mana"].max - normal["mana"].current)

    character.cls = _form_creature(form_name)
    character.transform_type = normal["cls"]
    character.health = deepcopy(normal["health"])
    character.mana = deepcopy(normal["mana"])
    character.stats = deepcopy(normal["stats"])
    character.health.max = normal["health"].max + int(overlay["health_bonus"])
    character.health.current = max(
        1 if normal["health"].current > 0 else 0,
        character.health.max - health_deficit,
    )
    character.mana.max = normal["mana"].max + int(overlay["mana_bonus"])
    character.mana.current = max(0, character.mana.max - mana_deficit)
    for name in STAT_NAMES:
        setattr(
            character.stats,
            name,
            getattr(normal["stats"], name) + int(overlay["stats"].get(name, 0)),
        )
    character.equipment = deepcopy(normal["equipment"])
    for slot in FORM_EQUIPMENT_SLOTS:
        character.equipment[slot] = deepcopy(overlay["equipment"][slot])
    character.spellbook = _merge_form_compatible_skills(character, overlay["spellbook"])
    character.resistance = deepcopy(overlay["resistance"])
    character.transformation_state = {
        "active_form": form_name,
        "overlay": deepcopy(overlay),
    }
    character._transformed = True
    if character.power_up:
        character.class_effects["Power Up"].active = True
        character.class_effects["Power Up"].duration = 1
    return f"{character.name} transforms into a {form_name}."


def dismiss_form(character: Any, *, force: bool = False) -> str:
    """Remove the active overlay while preserving accumulated resource deficits."""
    if not is_transformed(character):
        return ""
    if not force:
        if int(getattr(character.health, "current", 0) or 0) <= 0:
            return "An incapacitated character cannot dismiss their form."
        from . import lycan

        if int(lycan.ensure_state(character).get("frenzy_turns", 0) or 0) > 0:
            return "Frenzy prevents the form from being dismissed."
    snapshot = getattr(character, "_normal_form_snapshot", None)
    if not isinstance(snapshot, dict):
        return "The normal form could not be restored."
    health_deficit = max(0, character.health.max - character.health.current)
    mana_deficit = max(0, character.mana.max - character.mana.current)
    alive = character.health.current > 0
    active_form = str(getattr(character, "transformation_state", {}).get("active_form", "") or "")
    character.cls = snapshot["cls"]
    character.health = snapshot["health"]
    character.health.current = max(1 if alive else 0, character.health.max - health_deficit)
    character.mana = snapshot["mana"]
    character.mana.current = max(0, character.mana.max - mana_deficit)
    character.stats = snapshot["stats"]
    character.equipment = snapshot["equipment"]
    character.spellbook = snapshot["spellbook"]
    character.resistance = snapshot["resistance"]
    character.transform_type = character.cls
    character.transformation_state = {"active_form": None, "overlay": None}
    character._normal_form_snapshot = None
    character._normal_class_name = ""
    character._transformed = False
    message = f"{character.name} transforms back into their normal self."
    if active_form == "Werewolf":
        from . import promotion_kits

        moon_state = getattr(character, "lycan_state", {}) or {}
        if moon_state.pop("stressed_combat_complete", False):
            control = promotion_kits.lycan_control_state(character)
            reason = "safe_dismiss" if control.get("rank") == "Tethered" else "dismiss"
            message += "\n" + promotion_kits.record_lycan_stress(character, reason).rstrip()
    return message


def canonical_view(character: Any) -> dict[str, Any]:
    """Return canonical normal-form objects adjusted for current deficits."""
    snapshot = getattr(character, "_normal_form_snapshot", None)
    if not is_transformed(character) or not isinstance(snapshot, dict):
        return {
            "cls": character.cls,
            "health": character.health,
            "mana": character.mana,
            "stats": character.stats,
            "equipment": character.equipment,
            "spellbook": character.spellbook,
            "resistance": character.resistance,
        }
    view = deepcopy(snapshot)
    health_deficit = max(0, character.health.max - character.health.current)
    mana_deficit = max(0, character.mana.max - character.mana.current)
    view["health"].current = max(
        1 if character.health.current > 0 else 0,
        view["health"].max - health_deficit,
    )
    view["mana"].current = max(0, view["mana"].max - mana_deficit)
    return view


def mirror_learned_skill(character: Any, name: str, ability: Any) -> None:
    """Persist a learned skill and expose it in a compatible active form."""
    snapshot = getattr(character, "_normal_form_snapshot", None)
    if not is_transformed(character) or not isinstance(snapshot, dict):
        return
    snapshot["spellbook"].setdefault("Skills", {})[name] = ability
    if name in FORM_COMPATIBLE_SKILLS.get(permanent_class_name(character), frozenset()):
        character.spellbook.setdefault("Skills", {})[name] = ability
