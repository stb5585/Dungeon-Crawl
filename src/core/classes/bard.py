"""Bard class definition and active song helpers."""

from __future__ import annotations

from typing import Any

from .base import Job
from .. import items

SONGS = {
    "Valor": {
        "description": "Raises weapon and magic damage for 3 turns.",
        "damage_bonus": 0.10,
    },
    "Shelter": {
        "description": "Reduces incoming damage for 3 turns.",
        "damage_reduction": 0.10,
    },
    "Renewal": {
        "description": "Restores a small amount of HP and MP each turn for 3 turns.",
        "recovery": 0.05,
    },
    "Battle Hymn": {
        "description": "All combat participants become berserk for 3 turns.",
        "berserk_all": True,
    },
    "Ode to the Ramparts": {
        "description": "Increases defense and magic defense for 5 turns.",
        "defense_bonus": 0.20,
        "duration": 5,
    },
    "Symphony of Disfunction": {
        "description": "Lowers enemy attack and magic attack while active.",
        "exploration_effect": "enemy_attack_down",
    },
    "Low-defense-ian Rhapsody": {
        "description": "Lowers enemy defense and magic defense while active.",
        "exploration_effect": "enemy_defense_down",
    },
    "Slow Ride": {
        "description": "Lowers enemy speed-related modifiers while active.",
        "exploration_effect": "enemy_speed_down",
    },
    "Bones, Thugs, and Harmony": {
        "description": "Shifts enemy encounter rate while active.",
        "exploration_effect": "encounter_rate_shift",
    },
    "Scores and Scores Score": {
        "description": "Shifts enemy difficulty while active.",
        "exploration_effect": "enemy_difficulty_shift",
    },
    "Gold Trigger": {
        "description": "Increases enemy loot drop rate while active.",
        "exploration_effect": "loot_rate_up",
    },
    "Chorus Time": {
        "description": "Enemies may become dumbfounded and lose their turn.",
        "dumbfound": True,
    },
}
SONG_DURATION = 3
EXPLORATION_SONG_STEPS = 80
COMPOSITIONS = {
    "Battle Hymn": ("Lute", "BattleHymnSheet"),
    "Ode to the Ramparts": ("Mbira", "RampartsOdeSheet"),
    "Slow Ride": ("Lyre", "SlowRideSheet"),
    "Symphony of Disfunction": ("Tambourine", "DysfunctionSymphonySheet"),
    "Low-defense-ian Rhapsody": ("Accordina", "LowDefenseRhapsodySheet"),
    "Bones, Thugs, and Harmony": ("Didgeridoo", "BonesThugsHarmonySheet"),
    "Scores and Scores Score": ("Sitar", "ScoresAndScoresScoreSheet"),
    "Gold Trigger": ("Bagpipes", "GoldTriggerSheet"),
    "Chorus Time": ("GrandPiano", "ChorusTimeSheet"),
}


class Bard(Job):
    """
    Promotion: Healer -> Bard -> Troubadour
    Pros: Gain access to musical instruments, can dual wield daggers; gains songs that have affects in and out of
      combat; increased strength and dex gain
    Cons: Lose access to certain priest spells; lower wisdom gain
    Special Mechanic: Plays active songs that bolster damage, shelter the Bard, or renew HP/MP.
    """

    def __init__(self):
        super().__init__(
            name="Bard",
            description="The Bard is a master of performance and inspiration, blending "
            "healing arts with the power of music and storytelling. They can "
            "weave enchanting melodies to bolster their own strength, restore "
            "health, and demoralize enemies. Bards excel at turning the tide of "
            "battle through clever improvisation, crowd control, and "
            "spellcasting.",
            str_plus=1,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=1,
            def_plus=1,
            magic_plus=3,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Sword", "Staff"],
                "OffHand": ["Dagger", "Musical Instrument"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )


def default_song_state() -> dict[str, Any]:
    return {"active": None, "turns": 0, "encore": None}


def normalize_song_state(state: Any) -> dict[str, Any]:
    normalized = default_song_state()
    if isinstance(state, dict):
        active = state.get("active")
        normalized["active"] = active if active in SONGS else None
        try:
            normalized["turns"] = max(0, int(state.get("turns", 0) or 0))
        except (TypeError, ValueError):
            normalized["turns"] = 0
        encore = state.get("encore")
        normalized["encore"] = encore if encore in SONGS else None
    return normalized


def ensure_song_state(character: Any) -> dict[str, Any]:
    state = normalize_song_state(getattr(character, "bard_song", None))
    setattr(character, "bard_song", state)
    return state


def has_instrument(character: Any) -> bool:
    offhand = getattr(character, "equipment", {}).get("OffHand")
    return getattr(offhand, "subtyp", None) == "Musical Instrument"


def equipped_instrument_name(character: Any) -> str:
    offhand = getattr(character, "equipment", {}).get("OffHand")
    return str(getattr(offhand, "name", "") or "")


def available_compositions(character: Any) -> dict[str, str]:
    if getattr(getattr(character, "cls", None), "name", "") not in {"Bard", "Troubadour"}:
        return {}
    instrument_name = equipped_instrument_name(character)
    return {
        song: sheet_cls
        for song, (required_instrument, sheet_cls) in COMPOSITIONS.items()
        if instrument_name == required_instrument
    }


def compose_sheet_music(character: Any, song: str) -> tuple[bool, str]:
    options = available_compositions(character)
    if song not in options:
        required = COMPOSITIONS.get(song, ("a matching instrument", ""))[0]
        return False, f"{character.name} needs {required} to compose {song}.\n"

    sheet = getattr(items, options[song])()
    character.modify_inventory(sheet)
    return True, f"{character.name} composes {sheet.song_name} onto sheet music.\n"


def song_strength(character: Any) -> float:
    strength = 1.0
    if getattr(getattr(character, "cls", None), "name", "") == "Troubadour":
        strength *= 1.5
    return strength


def default_exploration_song_state() -> dict[str, Any]:
    return {"active": None, "steps": 0, "effect": None}


def normalize_exploration_song_state(state: Any) -> dict[str, Any]:
    normalized = default_exploration_song_state()
    if isinstance(state, dict):
        active = state.get("active")
        normalized["active"] = active if active in SONGS else None
        normalized["effect"] = state.get("effect") if normalized["active"] else None
        try:
            normalized["steps"] = max(0, int(state.get("steps", 0) or 0))
        except (TypeError, ValueError):
            normalized["steps"] = 0
    return normalized


def ensure_exploration_song_state(character: Any) -> dict[str, Any]:
    state = normalize_exploration_song_state(getattr(character, "bard_exploration_song", None))
    setattr(character, "bard_exploration_song", state)
    return state


def tick_exploration_song(character: Any, steps: int = 1) -> None:
    state = ensure_exploration_song_state(character)
    if not state.get("active"):
        return
    state["steps"] = max(0, int(state.get("steps", 0) or 0) - max(0, int(steps)))
    if state["steps"] <= 0:
        state.update(default_exploration_song_state())


def active_exploration_effect(character: Any) -> str | None:
    state = ensure_exploration_song_state(character)
    if not state.get("active"):
        return None
    return str(state.get("effect") or "") or None


def loot_drop_multiplier(character: Any) -> float:
    return 2.0 if active_exploration_effect(character) == "loot_rate_up" else 1.0


def encounter_rate_multiplier(character: Any) -> float:
    return 0.75 if active_exploration_effect(character) == "encounter_rate_shift" else 1.0


def enemy_difficulty_shift(character: Any) -> int:
    return -1 if active_exploration_effect(character) == "enemy_difficulty_shift" else 0


def apply_enemy_opening_debuffs(character: Any, enemy: Any) -> str:
    effect = active_exploration_effect(character)
    if not effect:
        return ""
    if effect == "enemy_attack_down":
        for stat_name in ("Attack", "Magic"):
            stat = enemy.stat_effects[stat_name]
            stat.active = True
            stat.duration = max(stat.duration, 3)
            stat.extra = min(int(stat.extra or 0), -max(1, int(getattr(enemy.combat, "attack", 5) * 0.15)))
        return f"{enemy.name}'s offense falters under Symphony of Disfunction.\n"
    if effect == "enemy_defense_down":
        for stat_name in ("Defense", "Magic Defense"):
            stat = enemy.stat_effects[stat_name]
            stat.active = True
            stat.duration = max(stat.duration, 3)
            stat.extra = min(int(stat.extra or 0), -max(1, int(getattr(enemy.combat, "defense", 5) * 0.15)))
        return f"{enemy.name}'s guard falters under Low-defense-ian Rhapsody.\n"
    if effect == "enemy_speed_down":
        stat = enemy.stat_effects["Speed"]
        stat.active = True
        stat.duration = max(stat.duration, 3)
        stat.extra = min(int(stat.extra or 0), -max(1, int(getattr(enemy.stats, "dex", 10) * 0.20)))
        return f"{enemy.name}'s rhythm drags under Slow Ride.\n"
    return ""


def start_song(character: Any, song: str, target: Any | None = None, battle_engine: Any | None = None) -> tuple[bool, str]:
    if song not in SONGS:
        return False, f"{song} is not a known song.\n"
    if getattr(getattr(character, "cls", None), "name", "") not in {"Bard", "Troubadour"}:
        return False, f"{character.name} does not know the bardic forms.\n"
    if not has_instrument(character):
        return False, f"{character.name} needs an equipped musical instrument.\n"
    spec = SONGS[song]
    if spec.get("exploration_effect"):
        state = ensure_exploration_song_state(character)
        state["active"] = song
        state["effect"] = spec["exploration_effect"]
        state["steps"] = EXPLORATION_SONG_STEPS
        return True, f"{character.name} begins {song}; its refrain will carry for {EXPLORATION_SONG_STEPS} steps.\n"

    duration = int(spec.get("duration", SONG_DURATION))
    state = ensure_song_state(character)
    if state.get("active") and state.get("turns", 0) > 0:
        from . import promotion_kits

        messages = promotion_kits.clear_crescendo(character, "song replacement")
    else:
        messages = ""
    state["active"] = song
    state["turns"] = duration
    state["encore"] = None
    messages += f"{character.name} begins the Song of {song}.\n"

    if spec.get("berserk_all"):
        participants = [character]
        if target is not None and target not in participants:
            participants.append(target)
        if battle_engine is not None:
            for participant_name in ("player", "enemy", "summon"):
                participant = getattr(battle_engine, participant_name, None)
                if participant is not None and participant not in participants:
                    participants.append(participant)
        for participant in participants:
            if participant.has_status_protection("Berserk"):
                continue
            berserk = participant.status_effects["Berserk"]
            berserk.active = True
            berserk.duration = max(berserk.duration, 3)
        messages += "Battle Hymn drives the combatants into a battle frenzy.\n"

    if spec.get("defense_bonus"):
        amount = max(1, int((character.check_mod("armor") + character.check_mod("magic def")) * spec["defense_bonus"] / 2))
        for stat_name in ("Defense", "Magic Defense"):
            effect = character.stat_effects[stat_name]
            effect.active = True
            effect.duration = max(effect.duration, duration)
            effect.extra = max(int(effect.extra or 0), amount)
        messages += f"Ode to the Ramparts raises {character.name}'s defenses by {amount}.\n"

    messages += _song_recovery_pulse(character, song, strength=song_strength(character))
    return True, messages


def active_song(character: Any) -> str | None:
    state = ensure_song_state(character)
    return state["active"] if state.get("turns", 0) > 0 else None


def damage_bonus(character: Any) -> float:
    state = ensure_song_state(character)
    bonus = 0.0
    if state.get("active") and state.get("turns", 0) > 0:
        bonus += SONGS.get(state.get("active"), {}).get("damage_bonus", 0.0) * song_strength(character)
    if state.get("encore"):
        bonus += SONGS.get(state.get("encore"), {}).get("damage_bonus", 0.0) * _encore_strength(character)
    return bonus


def damage_reduction(character: Any) -> float:
    state = ensure_song_state(character)
    reduction = 0.0
    if state.get("active") and state.get("turns", 0) > 0:
        reduction += SONGS.get(state.get("active"), {}).get("damage_reduction", 0.0) * song_strength(character)
    if state.get("encore"):
        reduction += SONGS.get(state.get("encore"), {}).get("damage_reduction", 0.0) * _encore_strength(character)
    return min(0.75, reduction)


def tick_song(character: Any) -> str:
    state = ensure_song_state(character)
    messages = ""
    if state.get("encore"):
        state["encore"] = None
    song = state.get("active")
    if not song or state.get("turns", 0) <= 0:
        return messages
    messages += _song_recovery_pulse(character, song, strength=song_strength(character))
    from . import promotion_kits

    messages += promotion_kits.record_song_turn(character, song)
    state["turns"] -= 1
    if state["turns"] <= 0:
        from . import class_rings

        encore_strength = class_rings.encore_strength(character)
        messages += f"{character.name}'s Song of {song} ends.\n"
        messages += promotion_kits.complete_song(character, song)
        state["active"] = None
        if encore_strength:
            if SONGS.get(song, {}).get("recovery"):
                messages += _song_recovery_pulse(character, song, strength=song_strength(character) * encore_strength)
            else:
                state["encore"] = song
                messages += f"Encore carries the Song of {song} for one final beat.\n"
    return messages


def _encore_strength(character: Any) -> float:
    from . import class_rings

    return song_strength(character) * class_rings.encore_strength(character)


def _renewal_pulse(character: Any, *, strength: float) -> str:
    hp_max = max(1, int(getattr(character.health, "max", 1) or 1))
    mp_max = max(1, int(getattr(character.mana, "max", 1) or 1))
    hp = max(1, int(hp_max * SONGS["Renewal"]["recovery"] * strength))
    mp = max(1, int(mp_max * SONGS["Renewal"]["recovery"] * strength))
    before_hp = character.health.current
    before_mp = character.mana.current
    character.health.current = min(hp_max, character.health.current + hp)
    character.mana.current = min(mp_max, character.mana.current + mp)
    gained_hp = character.health.current - before_hp
    gained_mp = character.mana.current - before_mp
    if gained_hp or gained_mp:
        return f"Song of Renewal restores {gained_hp} HP and {gained_mp} MP.\n"
    return ""


def _song_recovery_pulse(character: Any, song: str, *, strength: float) -> str:
    recovery = SONGS.get(song, {}).get("recovery", 0.0)
    if not recovery:
        return ""
    old_recovery = SONGS["Renewal"]["recovery"]
    try:
        SONGS["Renewal"]["recovery"] = recovery
        return _renewal_pulse(character, strength=strength)
    finally:
        SONGS["Renewal"]["recovery"] = old_recovery
