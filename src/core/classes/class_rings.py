"""Quest-awakened Class Ring helpers for legacy second-promotion classes."""

from __future__ import annotations

import copy
import random
from typing import Any


LEGACY_CLASS_NAMES = (
    "Berserker",
    "Crusader",
    "Dragoon",
    "Stalwart Defender",
    "Wizard",
    "Shadowcaster",
    "Knight Enchanter",
    "Grand Summoner",
    "Rogue",
    "Seeker",
    "Ninja",
    "Arcane Trickster",
    "Templar",
    "Hierophant",
    "Master Monk",
    "Archbishop",
    "Troubadour",
    "Lycan",
    "Astromancer",
    "Soulcatcher",
    "Beast Master",
)

CONSTELLATIONS = ("Ember", "Tide", "Gale", "Stone")

CLASS_RING_SPECS: dict[str, dict[str, str]] = {
    "Berserker": {
        "activation": "No Healing Duel",
        "mod": "Bloodied Crits",
        "description": (
            "below 50% HP gains +10% crit; below 25% HP gains +15% crit "
            "and +15% weapon damage"
        ),
    },
    "Crusader": {
        "activation": "Vow Trial",
        "mod": "Vow Affirmation",
        "description": (
            "improves the chosen Paladin vow aura and softens its mark drawback"
        ),
    },
    "Dragoon": {
        "activation": "Guard The Fall",
        "mod": "Aerial Supremacy",
        "description": (
            "enhances post-Jump Aerial Tempo follow-through and grants landing protection"
        ),
    },
    "Stalwart Defender": {
        "activation": "Siege Trial",
        "mod": "Guard Meter",
        "description": (
            "builds a guard meter through defensive pressure and spends it to "
            "reduce major incoming hits"
        ),
    },
    "Wizard": {
        "activation": "Four Formulae",
        "mod": "School Streak",
        "description": (
            "failed riders for the same school add +15% rider chance; four "
            "stacks guarantee the next eligible rider"
        ),
    },
    "Shadowcaster": {
        "activation": "Debt Cap Trial",
        "mod": "Umbral Debt",
        "description": (
            "shadow damage stores a reserve that can auto-heal at low HP, with "
            "backlash when overcapped"
        ),
    },
    "Knight Enchanter": {
        "activation": "Arcane Duel",
        "mod": "Arcane Tempo",
        "description": "builds Tempo from consumed blade charges and bursts at three stacks",
    },
    "Grand Summoner": {
        "activation": "Conduit Ritual",
        "mod": "+30% Summons",
        "description": (
            "permanently sacrifices 5% max HP so all current and future summons "
            "gain +30% HP and damage"
        ),
    },
    "Rogue": {
        "activation": "Loaded Game",
        "mod": "Loaded Dice",
        "description": "failed luck checks have a 15% chance to become successes",
    },
    "Seeker": {
        "activation": "Cartographer's Proof",
        "mod": "Hidden Cache",
        "description": (
            "revealed dungeon levels can contain one depth-weighted hidden cache"
        ),
    },
    "Ninja": {
        "activation": "No-Trace Contract",
        "mod": "No-Trace Opener",
        "description": (
            "with initiative, the first standard attack keeps double damage and "
            "interacts with Death Mark"
        ),
    },
    "Arcane Trickster": {
        "activation": "Impossible Theft",
        "mod": "Arcane Larceny",
        "description": (
            "after a successful spell steal, gain +20% Magic damage and +10% "
            "dodge for 3 turns, and smooth Stolen Charge payoffs"
        ),
    },
    "Templar": {
        "activation": "Relic Defense",
        "mod": "Ordered Blessings",
        "description": (
            "rotating Regen, Defense, and Holy damage blessings trigger through "
            "relevant actions"
        ),
    },
    "Hierophant": {
        "activation": "Consecration Rite",
        "mod": "Sacred Conduit",
        "description": (
            "once per combat after a clean Consecrated Conduit payoff, preserves "
            "1 Devotion and slightly improves staff-conduit holy damage"
        ),
    },
    "Master Monk": {
        "activation": "Purity Rite",
        "mod": "Martial Master",
        "description": "+50% damage and armor while unarmed and unarmored",
    },
    "Archbishop": {
        "activation": "Miracle Vigil",
        "mod": "Divine Intervention",
        "description": (
            "once per combat, the first drop below 50% HP has a 35% chance to "
            "heal 25% max HP"
        ),
    },
    "Troubadour": {
        "activation": "Lost Ballad",
        "mod": "Encore",
        "description": "songs trigger one final weaker effect when they expire",
    },
    "Lycan": {
        "activation": "Control Rite",
        "mod": "Controlled Frenzy",
        "description": (
            "lock-in still happens, but penalties are reduced and healing improves"
        ),
    },
    "Astromancer": {
        "activation": "Star Chart",
        "mod": "Constellation Cycle",
        "description": (
            "casting advances the active constellation; active-sign runes bend "
            "spell fate more strongly"
        ),
    },
    "Soulcatcher": {
        "activation": "Ancestral Totem Rite",
        "mod": "Aspect Evolution",
        "description": (
            "Soul Aspect improves slightly based on distinct enemy types harvested"
        ),
    },
    "Beast Master": {
        "activation": "Pack Trial",
        "mod": "Shared Recovery",
        "description": (
            "when hero or companion receives healing, the other receives a smaller "
            "echo heal"
        ),
    },
}


def default_state() -> dict[str, Any]:
    return {
        "awakened": {class_name: False for class_name in LEGACY_CLASS_NAMES},
        "data": {
            "Berserker": {
                "no_healing_duel_complete": False,
                "battle_scars": 0,
                "battle_scar_hp_bonus": 0,
            },
            "Crusader": {"vow": None},
            "Dragoon": {"meteor_guard_shield": 0, "meteor_guard_turns": 0},
            "Stalwart Defender": {"guard_meter": 0, "resolve_mastery": 0},
            "Wizard": {"school_streak": {}},
            "Shadowcaster": {
                "debt": 0,
                "backlash": 0,
                "eclipse_turns": 0,
                "familiar_echo_used": False,
            },
            "Knight Enchanter": {"mana_tap_used": False},
            "Grand Summoner": {"hp_sacrificed": 0},
            "Rogue": {},
            "Seeker": {"claimed_caches": []},
            "Ninja": {"first_strike_spent": False},
            "Arcane Trickster": {"buff_turns": 0},
            "Templar": {"blessing_index": 0},
            "Hierophant": {},
            "Master Monk": {},
            "Archbishop": {"intervention_used": False},
            "Troubadour": {},
            "Lycan": {},
            "Astromancer": {"constellation_index": 0},
            "Soulcatcher": {"harvested_types": []},
            "Beast Master": {},
        },
    }


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if not isinstance(state, dict):
        return normalized

    awakened = state.get("awakened", {})
    if isinstance(awakened, dict):
        for class_name in LEGACY_CLASS_NAMES:
            normalized["awakened"][class_name] = bool(awakened.get(class_name, False))

    data = state.get("data", {})
    if isinstance(data, dict):
        for class_name, defaults in normalized["data"].items():
            incoming = data.get(class_name, {})
            if isinstance(incoming, dict):
                defaults.update(copy.deepcopy(incoming))

    _normalize_lists(normalized)
    return normalized


def _normalize_lists(state: dict[str, Any]) -> None:
    seeker = state["data"]["Seeker"]
    seeker["claimed_caches"] = [
        int(level) for level in seeker.get("claimed_caches", []) if str(level).lstrip("-").isdigit()
    ]
    soulcatcher = state["data"]["Soulcatcher"]
    soulcatcher["harvested_types"] = sorted(
        {str(enemy_type) for enemy_type in soulcatcher.get("harvested_types", []) if enemy_type}
    )
    wizard = state["data"]["Wizard"]
    streak = wizard.get("school_streak", {})
    wizard["school_streak"] = {
        str(school): max(0, min(4, int(stacks or 0)))
        for school, stacks in streak.items()
    } if isinstance(streak, dict) else {}
    berserker = state["data"]["Berserker"]
    berserker["battle_scars"] = max(0, min(20, int(berserker.get("battle_scars", 0) or 0)))
    berserker["battle_scar_hp_bonus"] = max(0, int(berserker.get("battle_scar_hp_bonus", 0) or 0))
    shadow = state["data"]["Shadowcaster"]
    shadow["debt"] = max(0, int(shadow.get("debt", 0) or 0))
    shadow["backlash"] = max(0, int(shadow.get("backlash", 0) or 0))
    shadow["eclipse_turns"] = max(0, int(shadow.get("eclipse_turns", 0) or 0))
    shadow["familiar_echo_used"] = bool(shadow.get("familiar_echo_used", False))
    stalwart = state["data"]["Stalwart Defender"]
    stalwart["guard_meter"] = max(0, int(stalwart.get("guard_meter", 0) or 0))
    stalwart["resolve_mastery"] = max(0, int(stalwart.get("resolve_mastery", 0) or 0))


def ensure_state(character: Any) -> dict[str, Any]:
    state = normalize_state(getattr(character, "class_ring_awakening", None))
    setattr(character, "class_ring_awakening", state)
    return state


def copy_state(character: Any) -> dict[str, Any]:
    return copy.deepcopy(ensure_state(character))


def class_name(character: Any) -> str:
    return getattr(getattr(character, "cls", None), "name", "")


def has_equipped_class_ring(character: Any) -> bool:
    equipment = getattr(character, "equipment", {})
    ring = equipment.get("Ring") if isinstance(equipment, dict) else None
    return getattr(ring, "name", None) == "Class Ring"


def has_stored_class_ring(character: Any) -> bool:
    storage = getattr(character, "storage", {})
    if not isinstance(storage, dict):
        return False
    return any(getattr(item, "name", None) == "Class Ring" for item in storage.get("Class Ring", []))


def has_inventory_class_ring(character: Any) -> bool:
    inventory = getattr(character, "inventory", {})
    if not isinstance(inventory, dict):
        return False
    return any(getattr(item, "name", None) == "Class Ring" for item in inventory.get("Class Ring", []))


def class_ring_item(character: Any) -> Any | None:
    equipment = getattr(character, "equipment", {})
    if isinstance(equipment, dict):
        ring = equipment.get("Ring")
        if getattr(ring, "name", None) == "Class Ring":
            return ring
    for source_name in ("storage", "inventory"):
        source = getattr(character, source_name, {})
        if not isinstance(source, dict):
            continue
        for item in source.get("Class Ring", []):
            if getattr(item, "name", None) == "Class Ring":
                return item
    return None


def has_visible_class_ring(character: Any) -> bool:
    return has_equipped_class_ring(character) or has_stored_class_ring(character)


def is_legacy_class(class_name_value: str) -> bool:
    return class_name_value in LEGACY_CLASS_NAMES


def is_awakened(character: Any, class_name_value: str | None = None) -> bool:
    target = class_name_value or class_name(character)
    if target not in LEGACY_CLASS_NAMES:
        return False
    return bool(ensure_state(character)["awakened"][target])


def activation_name(class_name_value: str) -> str:
    return CLASS_RING_SPECS.get(class_name_value, {}).get("activation", "Quest Awakening")


def ring_mod(character: Any) -> str:
    current = class_name(character)
    if current not in CLASS_RING_SPECS:
        return "Special"
    if not is_awakened(character, current):
        return f"Dormant {CLASS_RING_SPECS[current]['mod']}"
    return CLASS_RING_SPECS[current]["mod"]


def presentation_state(
    character: Any,
    *,
    awakened: bool | None = None,
    effect_requires_equipped: bool = True,
) -> dict[str, Any]:
    """Return compact Class Ring presentation facts without changing mechanics."""
    equipped = has_equipped_class_ring(character)
    stored = has_stored_class_ring(character)
    inventory = has_inventory_class_ring(character)
    if equipped:
        location = "equipped"
    elif stored:
        location = "stored"
    elif inventory:
        location = "inventory only"
    else:
        location = "not present"
    if awakened is None:
        current = class_name(character)
        awakened = is_awakened(character, current) if current else False
    effect_active = bool(awakened and (equipped or not effect_requires_equipped))
    return {
        "location": location,
        "equipped": equipped,
        "stored": stored,
        "inventory": inventory,
        "visible": equipped or stored,
        "town_visible": equipped or stored,
        "awakened": bool(awakened),
        "state": "awakened" if awakened else "dormant",
        "effect_active": effect_active,
    }


def presentation_summary(
    character: Any,
    *,
    awakened: bool | None = None,
    effect_requires_equipped: bool = True,
) -> str:
    state = presentation_state(
        character,
        awakened=awakened,
        effect_requires_equipped=effect_requires_equipped,
    )
    town = "yes" if state["town_visible"] else "no"
    return (
        f"Ring location: {state['location']}. "
        f"Town-visible: {town}. "
        f"State: {state['state']}."
    )


def active_effect_summary(character: Any, *, awakened: bool | None = None) -> str:
    state = presentation_state(character, awakened=awakened)
    if state["effect_active"]:
        return "Active effect: active while equipped."
    if state["awakened"]:
        return "Active effect: equip the ring to use it."
    return "Active effect: inactive until awakened."


def _special_system_awakened(character: Any, current: str) -> bool | None:
    if current == "Grandmaster of Arms":
        from . import grandmaster

        state = grandmaster.normalize_state(getattr(character, "grandmaster_discipline", None))
        return bool(state["activated"])
    if current == "Demonologist":
        from . import demonologist

        state = demonologist.normalize_state(getattr(character, "demonologist_contracts", None))
        return bool(state["ring_awakened"])
    if current == "Archdruid":
        from . import archdruid

        state = archdruid.normalize_state(getattr(character, "archdruid_attunement", None))
        return bool(state["ring_awakened"])
    return None


def description(character: Any) -> str:
    current = class_name(character)
    spec = CLASS_RING_SPECS.get(current)
    if not spec:
        return "A ring that changes depending on the wearer's specialty."
    state_word = "awakened" if is_awakened(character, current) else "dormant"
    extra = _description_extra(character, current)
    return (
        f"A {state_word} Class Ring for a {current}. "
        f"{presentation_summary(character)} "
        f"Activation: {spec['activation']}. "
        f"Awakened effect: {spec['description']}."
        f" {active_effect_summary(character)}"
        f"{extra}"
    )


def class_voluntas_identity(character: Any) -> dict[str, Any]:
    """Return the current Class Ring identity summary for Voluntas story beats."""
    current = class_name(character)
    special_awakened = _special_system_awakened(character, current) if current else None
    presentation = presentation_state(character, awakened=special_awakened)
    visible = presentation["visible"]
    awakened = presentation["awakened"]
    ring = class_ring_item(character)
    ring_description = (
        ring.get_description(character)
        if ring is not None and hasattr(ring, "get_description")
        else description(character)
    )
    return {
        "class_name": current,
        "visible": visible,
        "town_visible": presentation["town_visible"],
        "equipped": presentation["equipped"],
        "location": presentation["location"],
        "effect_active": presentation["effect_active"],
        "awakened": awakened,
        "activation": activation_name(current) if current else "Quest Awakening",
        "mod": ring_mod(character) if current else "Special",
        "description": ring_description,
    }


def _description_extra(character: Any, current: str) -> str:
    state = ensure_state(character)
    data = state["data"].get(current, {})
    if current == "Crusader" and not data.get("vow"):
        return " A Paladin vow must exist before this ring can be fully affirmed."
    if current == "Dragoon" and is_awakened(character, current):
        shield = int(data.get("meteor_guard_shield", 0) or 0)
        return f" Landing Shield: {shield}."
    if current == "Berserker":
        scars = int(data.get("battle_scars", 0) or 0)
        return f" Battle Scars: {scars}/20."
    if current == "Stalwart Defender" and is_awakened(character, current):
        return f" Guard Meter: {int(data.get('guard_meter', 0) or 0)}/100."
    if current == "Wizard":
        affinity = getattr(character, "wizard_affinity", {}) or {}
        if affinity:
            values = ", ".join(
                f"{school} {float(affinity.get(school, 0) or 0):.1f}/100"
                for school in ("Fire", "Ice", "Water", "Electric", "Earth", "Wind")
            )
            return f" Affinity: {values}."
    if current == "Shadowcaster" and is_awakened(character, current):
        return f" Umbral Debt: {int(data.get('debt', 0) or 0)}."
    if current == "Troubadour":
        song = getattr(character, "bard_song", {}) or {}
        if song.get("active"):
            return f" Active song: {song.get('active')} ({int(song.get('turns', 0) or 0)} turns)."
    if current == "Lycan":
        state = getattr(character, "lycan_state", {}) or {}
        if state:
            return f" Moon: {state.get('moon_phase', 'New')}; Frenzy Lock: {int(state.get('frenzy_turns', 0) or 0)} turns."
    if current == "Astromancer" and is_awakened(character, current):
        return f" Current constellation: {active_constellation(character)}."
    if current == "Soulcatcher" and is_awakened(character, current):
        count = len(data.get("harvested_types", []))
        return f" Distinct harvested enemy types: {count}."
    return ""


def activate(character: Any, class_name_value: str | None = None, **kwargs: Any) -> tuple[bool, str]:
    target = class_name_value or class_name(character)
    if target not in LEGACY_CLASS_NAMES:
        return False, "This Class Ring has no legacy awakening path.\n"
    if class_name(character) != target:
        return False, f"The {target} awakening can only be completed by a {target}.\n"
    if not has_visible_class_ring(character):
        return False, "The Class Ring must be equipped or placed in Barracks storage.\n"

    state = ensure_state(character)
    if state["awakened"][target]:
        return False, f"The {target} Class Ring is already awakened.\n"

    if target == "Crusader":
        from . import paladin

        vow = paladin.normalize_path(kwargs.get("vow")) or paladin.path(character)
        if not vow:
            return False, "The Vow Trial requires a sworn Paladin vow.\n"
        state["data"]["Crusader"]["vow"] = vow

    if target == "Grand Summoner":
        max_hp = max(1, int(getattr(getattr(character, "health", None), "max", 1) or 1))
        sacrifice = max(1, int(max_hp * 0.05))
        character.health.max = max(1, character.health.max - sacrifice)
        character.health.current = min(character.health.current, character.health.max)
        state["data"]["Grand Summoner"]["hp_sacrificed"] = (
            int(state["data"]["Grand Summoner"].get("hp_sacrificed", 0) or 0) + sacrifice
        )

    state["awakened"][target] = True
    setattr(character, "class_ring_awakening", state)
    return True, f"The Class Ring awakens through {activation_name(target)}.\n"


def bloodied_crit_bonus(character: Any) -> float:
    if not (is_awakened(character, "Berserker") and has_equipped_class_ring(character)):
        return 0.0
    hp_max = max(1, int(getattr(character.health, "max", 1) or 1))
    ratio = character.health.current / hp_max
    if ratio < 0.25:
        return 0.15
    if ratio < 0.50:
        return 0.10
    return 0.0


def weapon_damage_multiplier(character: Any) -> float:
    from . import berserker

    multiplier = 1.0
    if is_awakened(character, "Berserker") and has_equipped_class_ring(character):
        hp_max = max(1, int(getattr(character.health, "max", 1) or 1))
        if character.health.current / hp_max < 0.25:
            multiplier += 0.15
    multiplier += berserker.bloodied_weapon_bonus(character)
    if martial_master_active(character):
        multiplier += 0.50
    return multiplier


def armor_multiplier(character: Any) -> float:
    return 1.50 if martial_master_active(character) else 1.0


def martial_master_active(character: Any) -> bool:
    if not (is_awakened(character, "Master Monk") and has_equipped_class_ring(character)):
        return False
    weapon = getattr(character, "equipment", {}).get("Weapon")
    armor = getattr(character, "equipment", {}).get("Armor")
    weapon_empty = weapon is None or getattr(weapon, "subtyp", "None") in {"None", "Fist"}
    armor_empty = armor is None or getattr(armor, "subtyp", "None") == "None" or getattr(armor, "armor", 0) == 0
    return bool(weapon_empty and armor_empty)


def record_shadow_damage(character: Any, amount: int) -> None:
    if not (amount and amount > 0 and class_name(character) == "Shadowcaster"):
        return
    try:
        from . import promotion_kits

        promotion_kits.record_shadow_damage(character, amount)
    except Exception:
        pass


def trigger_umbral_debt(character: Any) -> int:
    if not (is_awakened(character, "Shadowcaster") and has_equipped_class_ring(character)):
        return 0
    state = ensure_state(character)
    data = state["data"]["Shadowcaster"]
    hp_max = max(1, int(character.health.max or 1))
    if character.health.current / hp_max >= 0.35:
        return 0
    debt = int(data.get("debt", 0) or 0)
    heal = min(debt, hp_max - character.health.current)
    if heal <= 0:
        return 0
    character.health.current += heal
    data["debt"] = debt - heal
    return heal


def record_damage_dealt(character: Any, amount: int, damage_type: str = "Physical") -> None:
    if damage_type in {"Shadow", "Dark"}:
        record_shadow_damage(character, amount)


def build_guard_meter(character: Any, amount: int) -> int:
    if not is_awakened(character, "Stalwart Defender"):
        return 0
    state = ensure_state(character)
    data = state["data"]["Stalwart Defender"]
    gained = max(1, int(amount // 5)) if amount > 0 else 0
    data["guard_meter"] = min(100, int(data.get("guard_meter", 0) or 0) + gained)
    return data["guard_meter"]


def reduce_major_hit(character: Any, amount: int) -> int:
    if not (is_awakened(character, "Stalwart Defender") and has_equipped_class_ring(character)):
        return amount
    state = ensure_state(character)
    data = state["data"]["Stalwart Defender"]
    if amount < max(20, int(character.health.max * 0.20)):
        return amount
    if int(data.get("guard_meter", 0) or 0) < 100:
        return amount
    data["guard_meter"] = 0
    return max(0, int(amount * 0.60))


def wizard_rider_chance_bonus(character: Any, school: str) -> float:
    if not (is_awakened(character, "Wizard") and has_equipped_class_ring(character)):
        return 0.0
    state = ensure_state(character)
    stacks = int(state["data"]["Wizard"]["school_streak"].get(str(school), 0) or 0)
    return 1.0 if stacks >= 4 else stacks * 0.15


def record_wizard_rider(character: Any, school: str, triggered: bool) -> float:
    if not is_awakened(character, "Wizard"):
        return 0.0
    state = ensure_state(character)
    school_key = str(school)
    streak = state["data"]["Wizard"]["school_streak"]
    if triggered:
        streak[school_key] = 0
    else:
        streak[school_key] = min(4, int(streak.get(school_key, 0) or 0) + 1)
    return wizard_rider_chance_bonus(character, school_key)


def summon_multiplier(character: Any) -> float:
    return 1.30 if is_awakened(character, "Grand Summoner") and has_equipped_class_ring(character) else 1.0


def loaded_dice_succeeds(character: Any, rng: Any = random) -> bool:
    return bool(is_awakened(character, "Rogue") and has_equipped_class_ring(character) and rng.random() < 0.15)


def hidden_cache_available(character: Any, dungeon_level: int, reveal_progress: float = 1.0) -> bool:
    if not (is_awakened(character, "Seeker") and has_equipped_class_ring(character)):
        return False
    if reveal_progress < 0.70:
        return False
    state = ensure_state(character)
    return int(dungeon_level) not in state["data"]["Seeker"]["claimed_caches"]


def claim_hidden_cache(character: Any, dungeon_level: int, reveal_progress: float = 1.0) -> tuple[bool, str | None]:
    if not hidden_cache_available(character, dungeon_level, reveal_progress):
        return False, None
    state = ensure_state(character)
    level = int(dungeon_level)
    state["data"]["Seeker"]["claimed_caches"].append(level)
    reward = "Ancient Utility Cache" if level >= 10 else "Hidden Utility Cache"
    return True, reward


def first_strike_multiplier(character: Any, *, has_initiative: bool = True) -> float:
    if not (has_initiative and is_awakened(character, "Ninja") and has_equipped_class_ring(character)):
        return 1.0
    state = ensure_state(character)
    data = state["data"]["Ninja"]
    if data.get("first_strike_spent"):
        return 1.0
    data["first_strike_spent"] = True
    return 2.0


def reset_combat_flags(character: Any) -> None:
    state = ensure_state(character)
    state["data"]["Ninja"]["first_strike_spent"] = False
    state["data"]["Archbishop"]["intervention_used"] = False
    state["data"]["Dragoon"]["meteor_guard_turns"] = 0
    state["data"]["Dragoon"]["meteor_guard_shield"] = 0


def activate_spell_steal_buff(character: Any) -> None:
    if is_awakened(character, "Arcane Trickster"):
        ensure_state(character)["data"]["Arcane Trickster"]["buff_turns"] = 3


def arcane_trickster_magic_bonus(character: Any) -> float:
    if not (is_awakened(character, "Arcane Trickster") and has_equipped_class_ring(character)):
        return 0.0
    turns = int(ensure_state(character)["data"]["Arcane Trickster"].get("buff_turns", 0) or 0)
    return 0.20 if turns > 0 else 0.0


def arcane_trickster_dodge_bonus(character: Any) -> float:
    if not (is_awakened(character, "Arcane Trickster") and has_equipped_class_ring(character)):
        return 0.0
    turns = int(ensure_state(character)["data"]["Arcane Trickster"].get("buff_turns", 0) or 0)
    return 0.10 if turns > 0 else 0.0


def next_ordered_blessing(character: Any) -> str | None:
    if not (is_awakened(character, "Templar") and has_equipped_class_ring(character)):
        return None
    blessings = ("Regen", "Defense", "Holy Damage")
    state = ensure_state(character)
    index = int(state["data"]["Templar"].get("blessing_index", 0) or 0)
    state["data"]["Templar"]["blessing_index"] = (index + 1) % len(blessings)
    return blessings[index % len(blessings)]


def divine_intervention(character: Any, rng: Any = random) -> int:
    if not (is_awakened(character, "Archbishop") and has_equipped_class_ring(character)):
        return 0
    state = ensure_state(character)
    data = state["data"]["Archbishop"]
    if data.get("intervention_used"):
        return 0
    hp_max = max(1, int(character.health.max or 1))
    if character.health.current / hp_max >= 0.50:
        return 0
    data["intervention_used"] = True
    if rng.random() >= 0.35:
        return 0
    heal = max(1, int(hp_max * 0.25))
    character.health.current = min(hp_max, character.health.current + heal)
    return heal


def encore_strength(character: Any) -> float:
    return 0.50 if is_awakened(character, "Troubadour") and has_equipped_class_ring(character) else 0.0


def controlled_frenzy_penalty_multiplier(character: Any) -> float:
    return 0.50 if is_awakened(character, "Lycan") and has_equipped_class_ring(character) else 1.0


def controlled_frenzy_healing_multiplier(character: Any) -> float:
    return 1.25 if is_awakened(character, "Lycan") and has_equipped_class_ring(character) else 1.0


def active_constellation(character: Any) -> str:
    from . import astromancer

    return astromancer.active_constellation(character)


def advance_constellation(character: Any) -> str:
    from . import astromancer

    return astromancer.advance_constellation(character)


def constellation_bonus(character: Any, damage_type: str | None = None) -> float:
    from . import astromancer

    return astromancer.constellation_bonus(character, damage_type)


def record_soul_harvest(character: Any, enemy_type: str | None) -> None:
    if not (enemy_type and is_awakened(character, "Soulcatcher")):
        return
    state = ensure_state(character)
    types = set(state["data"]["Soulcatcher"].get("harvested_types", []))
    types.add(str(enemy_type))
    state["data"]["Soulcatcher"]["harvested_types"] = sorted(types)


def soul_aspect_bonus(character: Any) -> float:
    if not (is_awakened(character, "Soulcatcher") and has_equipped_class_ring(character)):
        return 0.0
    count = len(ensure_state(character)["data"]["Soulcatcher"].get("harvested_types", []))
    return 0.20 + min(0.10, count * 0.01)


def shared_recovery_amount(character: Any, healing: int) -> int:
    if not (is_awakened(character, "Beast Master") and has_equipped_class_ring(character)):
        return 0
    try:
        bond_state = getattr(character, "tamed_companion", {}) or {}
        bond = max(0, min(100, int(bond_state.get("bond", 0) or 0)))
    except Exception:
        bond = 0
    rate = 0.25 + (0.10 * (bond / 100))
    return max(1, int(healing * rate)) if healing > 0 else 0


def apply_aerial_supremacy_shield(character: Any, jump_damage: int) -> int:
    """Create or refresh Aerial Supremacy's two-turn Landing Shield."""
    if not (is_awakened(character, "Dragoon") and has_equipped_class_ring(character)):
        return 0
    shield = max(1, int(jump_damage * 0.15)) if jump_damage > 0 else 0
    if not shield:
        return 0
    state = ensure_state(character)
    data = state["data"]["Dragoon"]
    data["meteor_guard_shield"] = max(
        int(data.get("meteor_guard_shield", 0) or 0),
        shield,
    )
    data["meteor_guard_turns"] = 2
    return int(data["meteor_guard_shield"])


def apply_meteor_guard(character: Any, jump_damage: int) -> int:
    """Compatibility alias for the renamed Aerial Supremacy shield."""
    return apply_aerial_supremacy_shield(character, jump_damage)


def absorb_aerial_supremacy_shield(character: Any, amount: int) -> tuple[int, str]:
    """Absorb incoming damage with an active Landing Shield."""
    amount = max(0, int(amount or 0))
    if amount <= 0:
        return amount, ""
    if not (is_awakened(character, "Dragoon") and has_equipped_class_ring(character)):
        return amount, ""
    data = ensure_state(character)["data"]["Dragoon"]
    shield = max(0, int(data.get("meteor_guard_shield", 0) or 0))
    turns = max(0, int(data.get("meteor_guard_turns", 0) or 0))
    if shield <= 0 or turns <= 0:
        return amount, ""
    absorbed = min(amount, shield)
    remaining = shield - absorbed
    data["meteor_guard_shield"] = remaining
    if remaining <= 0:
        data["meteor_guard_turns"] = 0
    message = f"{character.name}'s Landing Shield absorbs {absorbed} damage.\n"
    if remaining <= 0:
        message += f"{character.name}'s Landing Shield is depleted.\n"
    return amount - absorbed, message


def tick_aerial_supremacy_shield(character: Any) -> str:
    """Advance and expire the combat-only Landing Shield."""
    data = ensure_state(character)["data"]["Dragoon"]
    shield = max(0, int(data.get("meteor_guard_shield", 0) or 0))
    turns = max(0, int(data.get("meteor_guard_turns", 0) or 0))
    if shield <= 0 or turns <= 0:
        return ""
    turns -= 1
    data["meteor_guard_turns"] = turns
    if turns > 0:
        return ""
    data["meteor_guard_shield"] = 0
    return f"{character.name}'s Landing Shield expires.\n"
