"""Shared Mage specialization, enhancement, and transient-conjuration rules."""

from __future__ import annotations

import random
from typing import Any


ELEMENTAL_SCHOOLS = ("Fire", "Ice", "Electric", "Wind", "Water", "Earth")
ENHANCEMENT_BY_SCHOOL = {
    "Fire": "Fire Inside",
    "Ice": "Frozen Armor",
    "Electric": "Electrified",
    "Wind": "Wind Currents",
    "Water": "Refreshment",
    "Earth": "Terra Firma",
}
TRANSIENT_SUMMON_STEPS = 50
TORCHLIGHT_STEPS = 50
TORCHLIGHT_ENCOUNTER_MULTIPLIER = 0.50
ENHANCEMENT_PROC_CHANCE = 0.20

CALLING_ENEMY_TYPE_PREFERENCES = {
    "Animal": ("Animal",),
    "Humanoid": ("Humanoid",),
    "Monster": ("Monster",),
    "Spirit": ("Elemental", "Undead"),
    "Fiend": ("Fiend", "Fey"),
    "Celestial": ("Celestial", "Fey", "Humanoid"),
    "Dragon": ("Dragon",),
}


def has_skill(character: Any, name: str) -> bool:
    """Return whether the character learned a named Mage passive."""
    return name in getattr(character, "spellbook", {}).get("Skills", {})


def has_talent(character: Any, key: str) -> bool:
    """Return whether a named progression talent is owned."""
    try:
        from ..progression import has_talent as progression_has_talent

        return progression_has_talent(character, key)
    except Exception:
        return False


def enhance_blade_bonus(character: Any) -> int:
    """Return Tome-warrior bonus damage from current mana percentage."""
    if not has_skill(character, "Enhance Blade"):
        return 0
    weapon = getattr(character, "equipment", {}).get("Weapon")
    base_damage = max(0, int(getattr(weapon, "damage", 0) or 0))
    mana = getattr(character, "mana", None)
    maximum = max(1, int(getattr(mana, "max", 1) or 1))
    current = max(0, min(maximum, int(getattr(mana, "current", 0) or 0)))
    return int(base_damage * (current / maximum))


def enhance_armor_bonus(character: Any) -> int:
    """Return bonus physical armor from the character's missing mana."""
    if not has_skill(character, "Enhance Armor"):
        return 0
    armor = getattr(character, "equipment", {}).get("Armor")
    base_armor = max(0, int(getattr(armor, "armor", 0) or 0))
    mana = getattr(character, "mana", None)
    maximum = max(1, int(getattr(mana, "max", 1) or 1))
    current = max(0, min(maximum, int(getattr(mana, "current", 0) or 0)))
    return int(base_armor * (1.0 - (current / maximum)))


def specialization(character: Any) -> str | None:
    """Return the selected Sorcerer specialization, if any."""
    if has_skill(character, "Classical Force"):
        return "Elemental"
    if has_skill(character, "Arcane Tradition"):
        return "Arcane"
    return None


def school_from_ability(ability: Any) -> str | None:
    """Resolve elemental and Arcane schools without changing resistance types."""
    for candidate in (
        getattr(ability, "subtyp", None),
        getattr(ability, "school", None),
        getattr(ability, "damage_type", None),
    ):
        if str(candidate) in ELEMENTAL_SCHOOLS:
            return str(candidate)
        if str(candidate) == "Arcane":
            return "Arcane"
    if getattr(ability, "name", "") in {
        "Magic Missile",
        "Magic Missile 2",
        "Magic Missile 3",
        "Polymorph",
        "Mana Shield",
        "Imbue Weapon",
    }:
        return "Arcane"
    return None


def spell_potency_multiplier(character: Any, ability: Any) -> float:
    """Apply the mutually exclusive specialization's severe off-school nerf."""
    chosen = specialization(character)
    school = school_from_ability(ability)
    if chosen == "Elemental" and school == "Arcane":
        return 0.50
    if chosen == "Arcane" and school in ELEMENTAL_SCHOOLS:
        return 0.50
    return 1.0


def arcane_potency_multiplier(character: Any) -> float:
    """Return Arcane barrier/enhancement potency after specialization."""
    return 0.50 if specialization(character) == "Elemental" else 1.0


def spell_damage_multiplier(character: Any, ability: Any) -> float:
    """Return authored Mage-talent damage scaling for a spell."""
    if (
        str(getattr(ability, "name", "")).startswith("Shadow Bolt")
        and has_talent(character, "mage.forbidden-studies")
    ):
        return 1.20
    return 1.0


def arcane_critical_multiplier(character: Any, multiplier: float) -> float:
    """Increase only the bonus portion of Arcane critical damage by 10%."""
    try:
        from ..progression import has_talent

        if multiplier > 1 and has_talent(character, "mage.arcane-fundamentals"):
            return 1 + ((multiplier - 1) * 1.10)
    except Exception:
        pass
    return multiplier


def _combat_state(character: Any) -> dict[str, Any]:
    state = getattr(character, "mage_enhancement_state", None)
    if not isinstance(state, dict):
        state = {}
        setattr(character, "mage_enhancement_state", state)
    return state


def process_cast(
    character: Any,
    ability: Any,
    target: Any | None = None,
    *,
    rng: Any = random,
) -> str:
    """Attempt the learned matching Enhancement after a successful spell cast."""
    from . import promotion_kits

    message = promotion_kits.record_spell_signature(character, ability)
    school = school_from_ability(ability)
    passive = ENHANCEMENT_BY_SCHOOL.get(str(school))
    if passive is None or not has_skill(character, passive):
        return message
    chance = ENHANCEMENT_PROC_CHANCE
    if specialization(character) == "Arcane":
        chance *= 0.50
    if rng.random() >= chance:
        return message

    state = _combat_state(character)
    if school == "Fire":
        state["fire_inside"] = 3
        return message + f"{character.name}'s Fire Inside primes the next attack.\n"
    if school == "Ice":
        state["frozen_armor"] = 1
        character.stat_effects["Defense"].active = True
        character.stat_effects["Defense"].duration = max(
            character.stat_effects["Defense"].duration, 1
        )
        character.stat_effects["Defense"].extra = max(
            character.stat_effects["Defense"].extra, 10
        )
        return message + f"Frozen Armor protects {character.name} for one turn.\n"
    if school == "Electric":
        state["electrified"] = 3
        return message + f"{character.name} becomes Electrified for three turns.\n"
    if school == "Wind":
        state["wind_currents"] = 3
        character.stat_effects["Speed"].active = True
        character.stat_effects["Speed"].duration = max(
            character.stat_effects["Speed"].duration, 3
        )
        character.stat_effects["Speed"].extra = max(
            character.stat_effects["Speed"].extra, 3
        )
        return message + f"Wind Currents quicken {character.name} for three turns.\n"
    if school == "Water":
        hp = max(1, int(character.health.max * 0.05))
        mp = max(1, int(character.mana.max * 0.05))
        hp = min(hp, character.health.max - character.health.current)
        mp = min(mp, character.mana.max - character.mana.current)
        character.health.current += max(0, hp)
        character.mana.current += max(0, mp)
        return message + f"Refreshment restores {hp} HP and {mp} MP to {character.name}.\n"
    if school == "Earth":
        state["terra_firma"] = 3
        return message + f"Terra Firma empowers {character.name}'s melee attacks.\n"
    return message


def tick_combat_state(character: Any, *, end: bool = False) -> None:
    """Advance or clear temporary Mage enhancement state."""
    state = _combat_state(character)
    if end:
        state.clear()
        return
    for key in tuple(state):
        state[key] = max(0, int(state[key] or 0) - 1)
        if state[key] <= 0:
            del state[key]


def melee_accuracy_bonus(character: Any) -> float:
    return 0.10 if _combat_state(character).get("wind_currents", 0) else 0.0


def melee_damage_multiplier(character: Any) -> float:
    return 1.50 if _combat_state(character).get("terra_firma", 0) else 1.0


def fire_inside_critical_bonus(character: Any) -> float:
    return 0.25 if _combat_state(character).get("fire_inside", 0) else 0.0


def consume_fire_inside(character: Any) -> None:
    _combat_state(character).pop("fire_inside", None)


def ice_resistance_bonus(character: Any, damage_type: str | None) -> float:
    if damage_type == "Ice" and _combat_state(character).get("frozen_armor", 0):
        return 0.25
    return 0.0


def electrified_retaliation(attacker: Any, defender: Any, damage: int) -> str:
    """Return one INT-scaled jolt after a successful incoming melee hit."""
    if damage <= 0 or not _combat_state(defender).get("electrified", 0):
        return ""
    jolt = max(1, int(getattr(defender.stats, "intel", 1) * 0.50))
    attacker.health.current -= jolt
    return f"{defender.name}'s Electrified ward jolts {attacker.name} for {jolt} damage.\n"


def set_transient_companion(
    character: Any,
    *,
    name: str,
    kind: str,
    source: str,
    damage: int | None = None,
) -> dict[str, Any]:
    """Replace the single transient companion and start its step duration."""
    level = max(1, int(getattr(getattr(character, "level", None), "level", 1)))
    binding = has_talent(character, "mage.binding-circle")
    base_damage = damage if damage is not None else max(2, level + character.stats.intel // 2)
    duration = TRANSIENT_SUMMON_STEPS
    if kind == "undead" and has_talent(character, "mage.forbidden-studies"):
        duration = int(duration * 1.50)
    state = {
        "name": str(name),
        "kind": str(kind),
        "source": str(source),
        "steps_remaining": duration,
        "damage": max(1, int(base_damage * (1.10 if binding else 1.0))),
    }
    character.transient_companion = state
    return state


def local_enemy_for_calling(
    character: Any,
    category: str,
    *,
    rng: Any = random,
) -> Any | None:
    """Choose a standard enemy of the requested kind nearest the current floor."""
    from .. import enemies
    from ..enemies.catalog import RANDOM_ENEMY_SPECS

    preferred_types = CALLING_ENEMY_TYPE_PREFERENCES.get(str(category), ())
    if not preferred_types:
        return None
    current_floor = max(0, int(getattr(character, "location_z", 0) or 0))
    floor_numbers = sorted(int(floor) for floor in RANDOM_ENEMY_SPECS)
    for enemy_type in preferred_types:
        nearest_distance: int | None = None
        nearest_factories: list[Any] = []
        for floor in floor_numbers:
            distance = abs(floor - current_floor)
            if nearest_distance is not None and distance > nearest_distance:
                continue
            for _name, factory in enemies.random_enemy_candidates(str(floor)):
                candidate = factory()
                if str(getattr(candidate, "enemy_typ", "")) != enemy_type:
                    continue
                if nearest_distance is None or distance < nearest_distance:
                    nearest_distance = distance
                    nearest_factories = [factory]
                elif distance == nearest_distance:
                    nearest_factories.append(factory)
        if nearest_factories:
            return rng.choice(nearest_factories)()
    return None


def conjure_standard_companion(
    character: Any,
    category: str,
    *,
    source: str,
    rng: Any = random,
) -> dict[str, Any] | None:
    """Replace the transient companion with a location-aware ordinary enemy."""
    enemy = local_enemy_for_calling(character, category, rng=rng)
    if enemy is None:
        return None
    damage = max(
        2,
        int(getattr(getattr(enemy, "combat", None), "attack", 0) or 0)
        + int(getattr(getattr(enemy, "stats", None), "strength", 0) or 0) // 2,
    )
    state = set_transient_companion(
        character,
        name=str(getattr(enemy, "name", category)),
        kind=str(category).lower(),
        source=source,
        damage=damage,
    )
    state["enemy_type"] = str(getattr(enemy, "enemy_typ", category))
    return state


def activate_torchlight(character: Any) -> None:
    """Start or refresh Torchlight's encounter-suppression duration."""
    character.torchlight_steps = TORCHLIGHT_STEPS


def torchlight_encounter_multiplier(character: Any) -> float:
    """Return the active Torchlight multiplier for random encounters."""
    if int(getattr(character, "torchlight_steps", 0) or 0) > 0:
        return TORCHLIGHT_ENCOUNTER_MULTIPLIER
    return 1.0


def tick_exploration(character: Any, steps: int) -> None:
    """Advance Mage transient summons, Torchlight, and conjuration cooldowns."""
    step_count = max(0, int(steps or 0))
    companion = getattr(character, "transient_companion", None)
    if isinstance(companion, dict):
        companion["steps_remaining"] = max(
            0, int(companion.get("steps_remaining", 0) or 0) - step_count
        )
        if companion["steps_remaining"] <= 0:
            character.transient_companion = None
    cooldown = max(0, int(getattr(character, "conjure_potion_cooldown", 0) or 0))
    character.conjure_potion_cooldown = max(0, cooldown - step_count)
    elixir_cooldown = max(
        0,
        int(getattr(character, "conjure_elixir_cooldown", 0) or 0),
    )
    character.conjure_elixir_cooldown = max(0, elixir_cooldown - step_count)
    torchlight_steps = max(
        0,
        int(getattr(character, "torchlight_steps", 0) or 0),
    )
    character.torchlight_steps = max(0, torchlight_steps - step_count)


def transient_companion_action(character: Any, enemies: list[Any], *, rng: Any = random) -> str:
    """Resolve the companion's independent random follow-up action."""
    companion = getattr(character, "transient_companion", None)
    living = [enemy for enemy in enemies if getattr(enemy, "is_alive", lambda: False)()]
    if not isinstance(companion, dict) or not living:
        return ""
    target = rng.choice(living)
    spread = rng.uniform(0.80, 1.20)
    damage = max(1, int(int(companion.get("damage", 1) or 1) * spread))
    target.health.current -= damage
    return (
        f"{companion['name']} acts independently and strikes {target.name} "
        f"for {damage} damage.\n"
    )


def permanent_summon_multipliers(character: Any) -> tuple[float, float]:
    """Return health and damage multipliers from Mage/Thaumaturgist mechanics."""
    state = getattr(character, "progression", None)
    purchased = getattr(state, "purchased_node_ids", set()) or set()
    health = 1.10 if has_talent(character, "mage.binding-circle") else 1.0
    damage = 1.10 if has_talent(character, "mage.binding-circle") else 1.0
    conduit_ranks = sum(
        node_id.startswith("summoner.talent.summoner-conduit-mastery")
        for node_id in purchased
    )
    ward_ranks = sum(
        node_id.startswith("summoner.talent.summoner-true-name-ward")
        for node_id in purchased
    )
    return health * (1 + 0.05 * ward_ranks), damage * (1 + 0.05 * conduit_ranks)


def record_last_enemy(character: Any, enemy: Any, *, boss: bool = False) -> None:
    """Remember the most recently defeated non-boss enemy for Enliven Dead."""
    if boss:
        return
    character.last_defeated_enemy = {
        "name": str(getattr(enemy, "name", "Unknown Enemy")),
        "enemy_type": str(getattr(enemy, "enemy_typ", "Monster")),
        "level": max(1, int(getattr(getattr(enemy, "level", None), "level", 1))),
    }
