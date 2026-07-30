"""Models behavior for the modern character screen package."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core import items


@dataclass(frozen=True)
class CharacterTab:
    """Reusable tab definition for character-style screens."""

    key: str
    label: str


@dataclass(frozen=True)
class EquipmentSlotSummary:
    slot: str
    item_name: str
    description: str
    bonus: str
    details: tuple[str, ...] = ()
    detail_rows: tuple[tuple[str, str], ...] = ()
    buffs: tuple[str, ...] = ()
    icon_item: Any = None
    implemented: bool = True


@dataclass(frozen=True)
class ResistanceSummary:
    name: str
    value: float


@dataclass(frozen=True)
class EquipmentBuffSummary:
    name: str
    source: str


DEFAULT_CHARACTER_TABS = (
    CharacterTab("character", "Character"),
    CharacterTab("class", "Class"),
    CharacterTab("equipment", "Equipment"),
)

EQUIPMENT_SLOT_ORDER = ("Weapon", "Armor", "Helmet", "OffHand", "Ring", "Pendant")
TWO_HANDED_WEAPON_SUBTYPES = frozenset({"Longsword", "Battle Axe", "Hammer"})
RESISTANCE_ORDER = ("Fire", "Electric", "Earth", "Shadow", "Poison", "Ice", "Water", "Wind", "Holy", "Physical")
RESISTANCE_SLOT_COUNT = len(RESISTANCE_ORDER)
PORTRAIT_DIR = Path(__file__).resolve().parents[1] / "assets" / "portraits"
WEAPON_DISCIPLINE_ICON_FACTORIES = {
    "Fist": items.BrassKnuckles,
    "Dagger": items.Dirk,
    "Sword": items.Rapier,
    "Club": items.Mace,
    "Longsword": items.Bastard,
    "Battle Axe": items.Broadaxe,
    "Polearm": items.Framea,
    "Hammer": items.Sledgehammer,
}


def _whole_stat_text(value) -> str:
    """Format combat stats as whole-number values for stable stat surfaces."""
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return str(value)
