"""Demonologist contract and Class Ring awakening helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
import random

from .base import Job
from .. import items


PATRONS = ("Imp", "Quasit", "Incubus", "Succubus", "Archvile", "Maelephant", "Balor")
INTENTS = ("Harm", "Curse", "Protect", "Restore", "Desperate Aid")
ECHOES = {
    "Defense": "Homunculus",
    "Support": "Fairy",
    "Arcane": "Mephit",
    "Luck": "Jinkin",
}

BASE_GOLD_COST = {
    "Harm": 160,
    "Curse": 140,
    "Protect": 130,
    "Restore": 150,
    "Desperate Aid": 450,
}

PATRON_POWER = {
    "Imp": 1.00,
    "Quasit": 1.08,
    "Incubus": 1.18,
    "Succubus": 1.20,
    "Archvile": 1.32,
    "Maelephant": 1.42,
    "Balor": 1.55,
}

PATRON_INTENTS = {
    "Imp": {"Harm", "Curse"},
    "Quasit": {"Harm", "Curse", "Desperate Aid"},
    "Incubus": {"Harm", "Curse", "Restore"},
    "Succubus": {"Curse", "Restore", "Desperate Aid"},
    "Archvile": {"Harm", "Curse", "Protect"},
    "Maelephant": {"Harm", "Protect", "Desperate Aid"},
    "Balor": {"Harm", "Curse", "Protect", "Desperate Aid"},
}


class Demonologist(Job):  # TODO
    """
    Promotion: Mage -> Warlock -> Demonologist
    Additional Pros: Increased wisdom and defense
    Additional Cons: Decreased magic gain
    Special Mechanic: can obtain contracts from fiends that grant unique abilities and buffs
        but also have drawbacks  TODO
    """

    def __init__(self):
        super().__init__(
            name="Demonologist",
            description="",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=1,
            cha_plus=2,
            dex_plus=0,
            att_plus=1,
            def_plus=2,
            magic_plus=3,
            magic_def_plus=4,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.DragonRouge(),
                "Armor": items.CloakEnchantment(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )


def default_state() -> dict[str, Any]:
    return {
        "crypt_unlocked": False,
        "unlocked_contracts": [],
        "active_patron": None,
        "ring_awakened": False,
        "imprisoned_familiar": None,
        "contract_history": [],
    }


def normalize_state(state: Any) -> dict[str, Any]:
    normalized = default_state()
    if not isinstance(state, dict):
        return normalized

    normalized["crypt_unlocked"] = bool(state.get("crypt_unlocked", False))
    normalized["ring_awakened"] = bool(state.get("ring_awakened", False))

    unlocked = state.get("unlocked_contracts", [])
    if isinstance(unlocked, (list, tuple, set)):
        normalized["unlocked_contracts"] = [name for name in PATRONS if name in set(unlocked)]

    active = state.get("active_patron")
    normalized["active_patron"] = active if active in normalized["unlocked_contracts"] else None

    familiar = state.get("imprisoned_familiar")
    if isinstance(familiar, dict):
        spec = familiar.get("spec")
        normalized["imprisoned_familiar"] = {
            "name": str(familiar.get("name") or ""),
            "race": str(familiar.get("race") or ECHOES.get(spec, "")),
            "spec": spec if spec in ECHOES else "",
        }

    history = state.get("contract_history", [])
    if isinstance(history, list):
        normalized["contract_history"] = history[-20:]

    return normalized


def ensure_state(character: Any) -> dict[str, Any]:
    state = normalize_state(getattr(character, "demonologist_contracts", None))
    if is_demonologist(character):
        state["crypt_unlocked"] = True
    setattr(character, "demonologist_contracts", state)
    return state


def copy_state(state: Any) -> dict[str, Any]:
    return deepcopy(normalize_state(state))


def is_demonologist(character: Any) -> bool:
    return getattr(getattr(character, "cls", None), "name", None) == "Demonologist"


def has_equipped_class_ring(character: Any) -> bool:
    equipment = getattr(character, "equipment", {})
    ring = equipment.get("Ring") if isinstance(equipment, dict) else None
    return getattr(ring, "name", None) == "Class Ring"


def has_stored_class_ring(character: Any) -> bool:
    storage = getattr(character, "storage", {})
    if not isinstance(storage, dict):
        return False
    return any(getattr(item, "name", None) == "Class Ring" for item in storage.get("Class Ring", []))


def has_visible_class_ring(character: Any) -> bool:
    return has_equipped_class_ring(character) or has_stored_class_ring(character)


def defeated_contract_patrons(character: Any) -> list[str]:
    kill_dict = getattr(character, "kill_dict", {}) or {}
    defeated = set()
    if isinstance(kill_dict, dict):
        for names in kill_dict.values():
            if not isinstance(names, dict):
                continue
            for name, count in names.items():
                try:
                    if int(count) > 0:
                        defeated.add(name)
                except Exception:
                    pass
    return [name for name in PATRONS if name in defeated]


def refresh_unlocked_contracts(character: Any) -> list[str]:
    state = ensure_state(character)
    unlocked = set(state["unlocked_contracts"])
    unlocked.update(defeated_contract_patrons(character))
    state["unlocked_contracts"] = [name for name in PATRONS if name in unlocked]
    if state["active_patron"] not in state["unlocked_contracts"]:
        state["active_patron"] = state["unlocked_contracts"][0] if state["unlocked_contracts"] else None
    setattr(character, "demonologist_contracts", state)
    return state["unlocked_contracts"]


def bind_patron(character: Any, patron: str) -> bool:
    state = ensure_state(character)
    if patron not in state["unlocked_contracts"]:
        return False
    state["active_patron"] = patron
    setattr(character, "demonologist_contracts", state)
    return True


def ring_can_awaken(character: Any) -> bool:
    state = ensure_state(character)
    return bool(
        is_demonologist(character)
        and has_visible_class_ring(character)
        and not state["ring_awakened"]
        and getattr(character, "familiar", None) is not None
    )


def awaken_ring(character: Any) -> tuple[bool, str]:
    if not ring_can_awaken(character):
        return False, "The Class Ring remains cold. It needs both the ring and a familiar bond.\n"

    familiar = getattr(character, "familiar", None)
    state = ensure_state(character)
    state["ring_awakened"] = True
    state["imprisoned_familiar"] = {
        "name": str(getattr(familiar, "name", "") or ""),
        "race": str(getattr(familiar, "race", "") or ""),
        "spec": str(getattr(familiar, "spec", "") or ""),
    }
    setattr(character, "familiar", None)
    setattr(character, "demonologist_contracts", state)
    race = state["imprisoned_familiar"]["race"] or "familiar"
    return True, f"The Class Ring awakens as your {race} is sealed inside it.\n"


def empowered(character: Any) -> bool:
    state = ensure_state(character)
    return bool(state["ring_awakened"])


def echo_spec(character: Any) -> str:
    state = ensure_state(character)
    familiar = state.get("imprisoned_familiar") or {}
    return str(familiar.get("spec") or "")


def available_intents(character: Any, patron: str | None = None) -> list[str]:
    state = ensure_state(character)
    patron = patron or state["active_patron"]
    allowed = PATRON_INTENTS.get(patron or "", set())
    return [intent for intent in INTENTS if intent in allowed]


def quote_contract(character: Any, target: Any, intent: str) -> dict[str, Any]:
    state = ensure_state(character)
    patron = state["active_patron"]
    if not is_demonologist(character):
        return {"ok": False, "reason": "Only a Demonologist can call fiend contracts."}
    if not patron:
        return {"ok": False, "reason": "No active patron is bound in the crypt."}
    if intent not in available_intents(character, patron):
        return {"ok": False, "reason": f"{patron} refuses that kind of bargain."}

    hp_pct = _pct(getattr(character, "health", None))
    mp_pct = _pct(getattr(character, "mana", None))
    urgency = 1.0
    if hp_pct < 0.35:
        urgency += 0.35
    if mp_pct < 0.25 and intent in {"Restore", "Desperate Aid"}:
        urgency += 0.20

    power = PATRON_POWER.get(patron, 1.0)
    ring_mult = 1.45 if empowered(character) else 1.0
    charisma_discount = min(0.30, max(0.0, getattr(character.stats, "charisma", 0) * 0.006))
    gold = int(BASE_GOLD_COST[intent] * power * ring_mult * urgency * (1.0 - charisma_discount))
    gold = max(25, gold)

    costs = {"gold": gold, "item": False, "permanent": None}
    if intent == "Desperate Aid":
        if hp_pct < 0.30:
            costs["permanent"] = {"stat": "health", "amount": 1}
        elif mp_pct < 0.20:
            costs["permanent"] = {"stat": "mana", "amount": 1}
    elif urgency > 1.25:
        costs["item"] = True

    return {
        "ok": True,
        "patron": patron,
        "intent": intent,
        "empowered": empowered(character),
        "echo": echo_spec(character),
        "costs": costs,
        "misbehavior_chance": misbehavior_chance(character, intent),
    }


def can_pay_quote(character: Any, quote: dict[str, Any]) -> bool:
    if not quote.get("ok"):
        return False
    costs = quote.get("costs", {})
    if int(getattr(character, "gold", 0)) < int(costs.get("gold", 0)):
        return False
    permanent = costs.get("permanent")
    if isinstance(permanent, dict):
        stat = permanent.get("stat")
        amount = int(permanent.get("amount", 0) or 0)
        resource = getattr(character, stat, None)
        if resource is not None and getattr(resource, "max", 0) <= amount + 1:
            return False
    if costs.get("item") and _choose_consumable(character) is None:
        return False
    return True


def pay_quote(character: Any, quote: dict[str, Any]) -> str:
    costs = quote.get("costs", {})
    gold = int(costs.get("gold", 0) or 0)
    character.gold = max(0, int(getattr(character, "gold", 0)) - gold)
    msg = f"{quote['patron']} accepts {gold} gold.\n"

    if costs.get("item"):
        item = _choose_consumable(character)
        if item is not None:
            character.modify_inventory(item, subtract=True)
            msg += f"{quote['patron']} takes a {item.name} as a rider to the bargain.\n"

    permanent = costs.get("permanent")
    if isinstance(permanent, dict):
        resource = getattr(character, permanent.get("stat"), None)
        amount = int(permanent.get("amount", 0) or 0)
        if resource is not None and amount > 0:
            resource.max = max(1, resource.max - amount)
            resource.current = min(resource.current, resource.max)
            msg += f"{quote['patron']} brands away {amount} {permanent['stat']}.\n"
    return msg


def resolve_contract(character: Any, target: Any, intent: str, *, rng: Any = random) -> str:
    quote = quote_contract(character, target, intent)
    if not quote.get("ok"):
        return quote.get("reason", "The contract fails.") + "\n"
    if not can_pay_quote(character, quote):
        return "You cannot pay the demanded price.\n"

    msg = pay_quote(character, quote)
    twisted = rng.random() < quote["misbehavior_chance"]
    severity = twist_severity(character)
    strength = contract_strength(character, quote, twisted=twisted)

    msg += apply_intent(character, target, quote["intent"], strength, twisted=twisted, severity=severity)
    _record_history(character, quote, twisted)
    return msg


def contract_strength(character: Any, quote: dict[str, Any], *, twisted: bool = False) -> int:
    patron = quote["patron"]
    power = PATRON_POWER.get(patron, 1.0)
    strength = int(18 * power)
    if quote.get("empowered"):
        strength = int(strength * 1.55)
    if quote.get("intent") == "Desperate Aid":
        strength = int(strength * 1.4)
    if twisted:
        strength = int(strength * 0.65)
    return max(1, strength)


def apply_intent(character: Any, target: Any, intent: str, strength: int, *, twisted: bool, severity: int) -> str:
    patron = ensure_state(character).get("active_patron") or "The fiend"
    prefix = "twists the bargain and " if twisted else ""

    if intent == "Harm":
        damage = max(1, strength + getattr(character.stats, "charisma", 0) // 3)
        target.health.current = max(0, target.health.current - damage)
        return f"{patron} {prefix}lashes {target.name} for {damage} shadow damage.\n"

    if intent == "Curse":
        effect = target.stat_effects["Magic Defense"]
        effect.active = True
        effect.duration = 3
        effect.extra = min(int(effect.extra or 0), -max(3, strength // 4))
        return f"{patron} {prefix}brands {target.name} with a weakening sigil.\n"

    if intent == "Protect":
        effect = character.stat_effects["Defense"]
        effect.active = True
        effect.duration = 3
        effect.extra = max(int(effect.extra or 0), max(3, strength // 4))
        if twisted:
            character.health.current = max(1, character.health.current - severity)
            return f"{patron} raises a harsh ward that cuts into {character.name}.\n"
        return f"{patron} raises a ward around {character.name}.\n"

    if intent == "Restore":
        heal = min(character.health.max - character.health.current, strength)
        character.health.current += max(0, heal)
        if twisted:
            mp_loss = min(character.mana.current, severity)
            character.mana.current -= mp_loss
            return f"{patron} restores {heal} health and siphons {mp_loss} mana.\n"
        return f"{patron} restores {heal} health.\n"

    if intent == "Desperate Aid":
        damage = max(1, int(strength * 1.4))
        target.health.current = max(0, target.health.current - damage)
        heal = min(character.health.max - character.health.current, max(1, strength // 2))
        character.health.current += heal
        if twisted:
            character.mana.current = max(0, character.mana.current - severity)
            return f"{patron} answers imperfectly: {damage} damage, {heal} healing, and {severity} mana lost.\n"
        return f"{patron} intervenes: {damage} damage and {heal} healing.\n"

    return f"{patron} watches in silence.\n"


def misbehavior_chance(character: Any, intent: str) -> float:
    charisma = int(getattr(getattr(character, "stats", None), "charisma", 0) or 0)
    base = 0.30 if intent != "Desperate Aid" else 0.42
    if empowered(character):
        base -= 0.08
    if echo_spec(character) == "Luck":
        base -= 0.05
    return max(0.05, min(0.60, base - charisma * 0.004))


def twist_severity(character: Any) -> int:
    charisma = int(getattr(getattr(character, "stats", None), "charisma", 0) or 0)
    return max(1, 8 - charisma // 5)


def _record_history(character: Any, quote: dict[str, Any], twisted: bool) -> None:
    state = ensure_state(character)
    state["contract_history"].append(
        {
            "patron": quote["patron"],
            "intent": quote["intent"],
            "empowered": quote["empowered"],
            "twisted": bool(twisted),
        }
    )
    state["contract_history"] = state["contract_history"][-20:]
    setattr(character, "demonologist_contracts", state)


def _pct(resource: Any) -> float:
    max_value = float(getattr(resource, "max", 0) or 0)
    if max_value <= 0:
        return 1.0
    return max(0.0, min(1.0, float(getattr(resource, "current", 0) or 0) / max_value))


def _choose_consumable(character: Any) -> Any | None:
    inventory = getattr(character, "inventory", {}) or {}
    for bucket in inventory.values():
        if not bucket:
            continue
        item = bucket[0]
        if isinstance(item, type):
            try:
                item = item()
            except Exception:
                continue
        if getattr(item, "typ", "") == "Potion" or getattr(item, "subtyp", "") == "Scroll":
            return item
    return None
