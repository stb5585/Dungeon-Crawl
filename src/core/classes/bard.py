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
}
SONG_DURATION = 3


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
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.Lute(),
                "Armor": items.Cuirboulli(),
            },
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


def song_strength(character: Any) -> float:
    strength = 1.0
    if getattr(getattr(character, "cls", None), "name", "") == "Troubadour":
        strength *= 1.5
    return strength


def start_song(character: Any, song: str) -> tuple[bool, str]:
    if song not in SONGS:
        return False, f"{song} is not a known song.\n"
    if getattr(getattr(character, "cls", None), "name", "") not in {"Bard", "Troubadour"}:
        return False, f"{character.name} does not know the bardic forms.\n"
    if not has_instrument(character):
        return False, f"{character.name} needs an equipped musical instrument.\n"
    state = ensure_song_state(character)
    state["active"] = song
    state["turns"] = SONG_DURATION
    state["encore"] = None
    pulse = _renewal_pulse(character, strength=song_strength(character)) if song == "Renewal" else ""
    return True, f"{character.name} begins the Song of {song}.\n{pulse}"


def active_song(character: Any) -> str | None:
    state = ensure_song_state(character)
    return state["active"] if state.get("turns", 0) > 0 else None


def damage_bonus(character: Any) -> float:
    state = ensure_song_state(character)
    bonus = 0.0
    if state.get("active") == "Valor" and state.get("turns", 0) > 0:
        bonus += SONGS["Valor"]["damage_bonus"] * song_strength(character)
    if state.get("encore") == "Valor":
        bonus += SONGS["Valor"]["damage_bonus"] * _encore_strength(character)
    return bonus


def damage_reduction(character: Any) -> float:
    state = ensure_song_state(character)
    reduction = 0.0
    if state.get("active") == "Shelter" and state.get("turns", 0) > 0:
        reduction += SONGS["Shelter"]["damage_reduction"] * song_strength(character)
    if state.get("encore") == "Shelter":
        reduction += SONGS["Shelter"]["damage_reduction"] * _encore_strength(character)
    return min(0.75, reduction)


def tick_song(character: Any) -> str:
    state = ensure_song_state(character)
    messages = ""
    if state.get("encore"):
        state["encore"] = None
    song = state.get("active")
    if not song or state.get("turns", 0) <= 0:
        return messages
    if song == "Renewal":
        messages += _renewal_pulse(character, strength=song_strength(character))
    state["turns"] -= 1
    if state["turns"] <= 0:
        from . import class_rings

        encore_strength = class_rings.encore_strength(character)
        messages += f"{character.name}'s Song of {song} ends.\n"
        state["active"] = None
        if encore_strength:
            if song == "Renewal":
                messages += _renewal_pulse(character, strength=song_strength(character) * encore_strength)
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
