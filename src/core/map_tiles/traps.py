"""Sparse one-use traps for ordinary dungeon path tiles."""

from __future__ import annotations

import random
from types import SimpleNamespace
from typing import Any

from .. import enemies
from ..classes import footpad
from ..constants import ARMOR_SCALING_FACTOR
from .rules import _queue_cambion_message, quest_biased_random_enemy


TRAP_CHANCE = 0.06
DEATHCAP_CHANCE = 0.015
TRAP_TYPES = ("Tripwire", "Magic Ward", "Alert", "Red Alert")
ELIGIBLE_PATH_TYPES = frozenset({"EmptyCavePath", "CavePath0", "CavePath1", "CavePath2"})
STANDARD_DUNGEON_DEPTHS = frozenset(range(0, 7))
MAGIC_WARD_SPELLS = (
    (0, "Firebolt", "Fire"),
    (0, "Tremor", "Earth"),
    (1, "Water Jet", "Water"),
    (1, "Gust", "Wind"),
    (2, "Ice", "Ice"),
    (2, "Lightning", "Electric"),
    (3, "Shadow Bolt", "Shadow"),
)


def assign_dungeon_traps(world_dict: dict, *, rng: Any | None = None) -> int:
    """Randomly arm a stable, sparse set of ordinary cave-path tiles."""
    rng = rng or random.Random(0xD06E0)
    assigned = 0
    for tile in world_dict.values():
        if (
            type(tile).__name__ not in ELIGIBLE_PATH_TYPES
            or int(getattr(tile, "z", -1)) not in STANDARD_DUNGEON_DEPTHS
        ):
            continue
        tile.trap_type = None
        tile.trap_triggered = False
        tile.deathcap_available = rng.random() < DEATHCAP_CHANCE
        tile.deathcap_gathered = False
        if rng.random() >= TRAP_CHANCE:
            continue
        tile.trap_type = rng.choices(
            TRAP_TYPES,
            weights=(0.35, 0.30, 0.25, 0.10),
            k=1,
        )[0]
        assigned += 1
    return assigned


def _avoidance_severity(player: Any, *, rng: Any) -> tuple[float, str]:
    """Return the fraction of a trap effect remaining after Avoid Traps."""
    return footpad.trap_severity_multiplier(player, rng=rng)


def _tripwire(tile: Any, player: Any, severity: float, *, rng: Any) -> str:
    depth = max(0, int(tile.z))
    raw_damage = rng.randint(8 + (depth * 6), 14 + (depth * 8))
    armor = max(0, int(player.check_mod("armor")))
    damage = int(raw_damage * (1 - (armor / (armor + ARMOR_SCALING_FACTOR))))
    damage = max(1, int(damage * severity)) if severity else 0
    if damage:
        damage = min(damage, max(0, int(player.health.current) - 1))
        player.health.current -= damage
        return f"A hidden tripwire launches an arrow, dealing {damage} Physical damage."
    return "A hidden tripwire snaps, but its arrow misses harmlessly."


def _magic_ward(tile: Any, player: Any, severity: float, *, rng: Any) -> str:
    depth = max(0, int(tile.z))
    available = [entry for entry in MAGIC_WARD_SPELLS if entry[0] <= depth]
    _minimum_depth, spell_name, damage_type = rng.choice(available)
    raw_damage = rng.randint(10 + (depth * 7), 16 + (depth * 10))
    raw_damage = max(0, int(raw_damage * severity))
    source = SimpleNamespace(name="Magic Ward")
    _hit, reduction_message, damage = player.damage_reduction(
        raw_damage,
        source,
        typ=damage_type,
    )
    damage = min(max(0, int(damage)), max(0, int(player.health.current) - 1))
    player.health.current -= damage
    message = f"A Magic Ward casts {spell_name}, dealing {damage} {damage_type} damage."
    if reduction_message:
        message += f" {reduction_message.strip()}"
    return message


def _alert(tile: Any, player: Any, severity: float, *, red: bool, rng: Any) -> str:
    if severity <= 0:
        return "The alarm mechanism clicks, but you disable it before it sounds."
    local_depth = max(0, int(tile.z))
    encounter_depth = local_depth + int(red and severity >= 1.0)
    if red:
        tile.enemy = enemies.random_enemy(str(encounter_depth), rng=rng)
    else:
        tile.enemy = quest_biased_random_enemy(player, str(encounter_depth), rng=rng)
    player.state = "fight"
    tile.trap_forced_initiative = bool(red or severity >= 1.0)
    if red and severity < 1.0:
        return "You partially disable a Red Alert; it summons a local enemy, but still gives it initiative."
    label = "Red Alert" if red else "Alert"
    difficulty = "a stronger enemy" if red else "a local enemy"
    return f"A hidden {label} sounds, drawing {difficulty}; it has the initiative."


def trigger_tile_trap(tile: Any, player: Any, *, rng: Any = random) -> str:
    """Trigger and disarm a tile's trap, returning its exploration message."""
    trap_type = getattr(tile, "trap_type", None)
    if trap_type not in TRAP_TYPES or getattr(tile, "trap_triggered", False):
        return ""
    tile.trap_triggered = True
    severity, avoidance_message = _avoidance_severity(player, rng=rng)
    if trap_type == "Tripwire":
        message = _tripwire(tile, player, severity, rng=rng)
    elif trap_type == "Magic Ward":
        message = _magic_ward(tile, player, severity, rng=rng)
    elif trap_type == "Alert":
        message = _alert(tile, player, severity, red=False, rng=rng)
    else:
        message = _alert(tile, player, severity, red=True, rng=rng)
    if avoidance_message:
        message = f"{avoidance_message} {message}"
    _queue_cambion_message(player, message)
    return message
