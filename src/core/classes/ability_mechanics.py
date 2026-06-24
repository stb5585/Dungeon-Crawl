"""Shared helpers for class ability mechanics."""

from __future__ import annotations

from copy import deepcopy
import random
from typing import Any


ELEMENTS = ("Fire", "Ice", "Electric", "Water", "Earth", "Wind")


def _skills(character: Any) -> dict[str, Any]:
    return getattr(character, "spellbook", {}).get("Skills", {}) or {}


def has_skill(character: Any, skill_name: str) -> bool:
    return skill_name in _skills(character)


def _is_two_handed_polearm(item: Any) -> bool:
    return getattr(item, "subtyp", None) == "Polearm" and getattr(item, "handed", 1) == 2


def can_keep_polearm_shield(character: Any, weapon: Any, offhand: Any) -> bool:
    """Return whether a class skill lets a polearm stay paired with a shield."""
    if not _is_two_handed_polearm(weapon) or getattr(offhand, "subtyp", None) != "Shield":
        return False
    skills = _skills(character)
    return any(
        skill_name in skills
        for skill_name in ("Polearm Proficiency", "Polearm Excellence", "Polearm Mastery")
    )


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
    return {"active": False, "enemy_class": None, "name": None, "level": 1}


def normalize_tamed_companion(state: Any) -> dict[str, Any]:
    normalized = default_tamed_companion()
    if isinstance(state, dict):
        normalized["active"] = bool(state.get("active", False))
        normalized["enemy_class"] = state.get("enemy_class") if state.get("enemy_class") else None
        normalized["name"] = state.get("name") if state.get("name") else normalized["enemy_class"]
        try:
            normalized["level"] = max(1, int(state.get("level", 1) or 1))
        except (TypeError, ValueError):
            normalized["level"] = 1
    return normalized


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
    kill_dict = getattr(character, "kill_dict", {}) or {}
    best_type = None
    best_count = 0
    for enemy_type, enemies in kill_dict.items():
        if not isinstance(enemies, dict):
            continue
        total = sum(int(value or 0) for value in enemies.values())
        if total > best_count:
            best_type = enemy_type
            best_count = total
    return best_type


def favored_enemy_bonus(character: Any, enemy: Any | None) -> int:
    if enemy is None:
        return 0
    if "Favored Enemy" not in getattr(character, "spellbook", {}).get("Skills", {}):
        return 0
    enemy_type = getattr(enemy, "enemy_typ", None)
    if not enemy_type or enemy_type != favorite_enemy_type(character):
        return 0
    total = sum(int(value or 0) for value in (getattr(character, "kill_dict", {}) or {}).get(enemy_type, {}).values())
    return max(1, total // 10)


def attempt_tame(character: Any, target: Any, *, rng: Any = random) -> str:
    if target is None:
        return "There is no beast to tame.\n"
    if getattr(target, "enemy_typ", None) != "Animal":
        return f"{getattr(target, 'name', 'The target')} cannot be tamed.\n"
    if getattr(target, "boss", False) or getattr(target, "boss_type", None) or getattr(target, "class_ring_trial_enemy", False):
        return f"{target.name} resists all attempts at taming.\n"
    hp_max = max(1, int(getattr(getattr(target, "health", None), "max", 1) or 1))
    hp_ratio = max(0.0, min(1.0, getattr(target.health, "current", hp_max) / hp_max))
    low_hp_bonus = 0.35 if hp_ratio <= 0.35 else 0.0
    chance = min(0.85, 0.15 + low_hp_bonus + (character.stats.charisma * 0.015))
    if rng.random() > chance:
        return f"{target.name} refuses to be tamed.\n"

    state = {
        "active": True,
        "enemy_class": target.__class__.__name__,
        "name": target.name,
        "level": max(1, int(getattr(getattr(target, "level", None), "level", 1) or 1)),
    }
    character.tamed_companion = normalize_tamed_companion(state)
    try:
        from .. import companions

        character.familiar = companions.tamed_companion_from_state(character.tamed_companion)
    except Exception:
        pass
    target.health.current = 0
    return f"{character.name} tames {target.name}.\n"


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
