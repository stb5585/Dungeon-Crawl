"""Standard character menu implementation for the Pygame UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pygame

from src.ui_pygame.assets.companion_art_manager import get_companion_art_manager
from src.ui_pygame.assets.item_render_manager import get_item_render_manager
from src.ui_pygame.assets.portrait_manager import PortraitManager

from .confirmation_popup import ConfirmationPopup
from .input_guards import prepare_guarded_input, release_guard_allows_input, update_input_armed_from_event
from .mouse_helpers import hit_index, is_left_click, mouse_position
from .popup_menus import BestiaryPopupMenu, EquipmentPopupMenu, InventoryPopupMenu, JumpModsPopupMenu, SimpleListPopupMenu, TotemAspectsPopupMenu
from .town_base import TownScreenBase


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
    CharacterTab("equipment", "Equipment"),
)

EQUIPMENT_SLOT_ORDER = ("Weapon", "Armor", "Helmet", "OffHand", "Ring", "Pendant")
TWO_HANDED_WEAPON_SUBTYPES = frozenset({"Longsword", "Battle Axe", "Hammer"})
RESISTANCE_ORDER = ("Fire", "Electric", "Earth", "Shadow", "Poison", "Ice", "Water", "Wind", "Holy", "Physical")
RESISTANCE_SLOT_COUNT = len(RESISTANCE_ORDER)
PORTRAIT_DIR = Path(__file__).resolve().parents[1] / "assets" / "portraits"


class ModernCharacterScreen(TownScreenBase):
    """RPG-style character menu used by the standard pygame character flow."""

    def __init__(self, presenter, tabs: tuple[CharacterTab, ...] = DEFAULT_CHARACTER_TABS):
        self.tabs = tabs
        self.active_tab_index = 0
        self.portrait_manager = PortraitManager()
        self.item_render_manager = get_item_render_manager()
        self.companion_art_manager = get_companion_art_manager()
        self.selected_equipment_slot_index = 0
        self.equipment_selector_active = False
        self.current_selection = 0
        self.menu_options: list[str] = []
        super().__init__(presenter)
        self.calculate_rects()

    def calculate_rects(self):
        """Calculate responsive panel rectangles for the modern layout."""
        margin = 18
        gap = 12
        tab_height = max(44, self.height // 16)
        action_height = max(92, self.height // 8)
        content_top = margin + tab_height + gap
        content_height = self.height - content_top - action_height - (gap * 2) - margin
        content_height = max(320, content_height)

        self.tab_rect = pygame.Rect(margin, margin, self.width - (margin * 2), tab_height)
        self.content_rect = pygame.Rect(margin, content_top, self.width - (margin * 2), content_height)
        self.actions_rect = pygame.Rect(margin, self.content_rect.bottom + gap, self.width - (margin * 2), action_height)

        available_panel_width = self.content_rect.width - gap
        character_width = (available_panel_width * 3) // 5
        self.character_panel_rect = pygame.Rect(self.content_rect.left, self.content_rect.top, character_width, self.content_rect.height)
        self.combat_panel_rect = pygame.Rect(self.character_panel_rect.right + gap, self.content_rect.top, self.content_rect.right - self.character_panel_rect.right - gap, self.content_rect.height)
        self.details_rect = pygame.Rect(self.content_rect.left, self.content_rect.top, self.content_rect.width, self.content_rect.height)
        self.equipment_panel_rect = self.details_rect

        self.menu_rect = self.actions_rect
        self.info_rect = self.character_panel_rect
        self.exp_rect = self.character_panel_rect
        self.stats_rect = self.content_rect
        self.menu_options = self._base_menu_options()

    @property
    def active_tab(self) -> CharacterTab:
        return self.tabs[self.active_tab_index]

    def select_tab(self, key: str) -> None:
        for index, tab in enumerate(self.tabs):
            if tab.key == key:
                self.active_tab_index = index
                if key != "equipment":
                    self.equipment_selector_active = False
                return
        raise ValueError(f"Unknown character tab: {key}")

    def move_tab(self, delta: int) -> None:
        self.active_tab_index = (self.active_tab_index + delta) % len(self.tabs)
        if self.active_tab.key != "equipment":
            self.equipment_selector_active = False

    @staticmethod
    def _attr_name(value: Any, default: str = "Unknown") -> str:
        return str(getattr(value, "name", default) or default)

    @staticmethod
    def portrait_filename(player_char) -> str:
        race = ModernCharacterScreen._attr_name(getattr(player_char, "race", None), "Human")
        sex = str(getattr(player_char, "sex", "Male") or "Male")
        race_key = PortraitManager.normalize_key(race, "human")
        sex_key = PortraitManager.normalize_key(sex, "male")
        if sex_key not in {"male", "female"}:
            sex_key = "male"
        return f"{race_key}_{sex_key}.png"

    def portrait_path(self, player_char) -> Path:
        return PORTRAIT_DIR / self.portrait_filename(player_char)

    def load_portrait(self, player_char):
        race = getattr(player_char, "race", "Human")
        gender = getattr(player_char, "gender", getattr(player_char, "sex", "Male"))
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        first_promotion = getattr(player_char, "first_promotion", None)
        second_promotion = getattr(player_char, "second_promotion", None)
        effects = getattr(player_char, "active_visual_effects", ())
        variant = getattr(player_char, "portrait_variant", 0)
        return self.portrait_manager.get_portrait(
            race=race,
            gender=gender,
            class_name=class_name,
            first_promotion=first_promotion,
            second_promotion=second_promotion,
            effects=effects,
            variant=variant,
        )

    def _draw_fitted_surface(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        source_width, source_height = surface.get_size()
        if source_width <= 0 or source_height <= 0:
            return
        scale = min(rect.width / source_width, rect.height / source_height)
        target_size = (max(1, int(source_width * scale)), max(1, int(source_height * scale)))
        fitted = pygame.transform.smoothscale(surface, target_size)
        target_rect = fitted.get_rect(center=rect.center)
        self.screen.blit(fitted, target_rect)

    def portrait_frame_rect(self, y: int, surface: pygame.Surface | None = None) -> pygame.Rect:
        source_width, source_height = (225, 400)
        if surface is not None:
            surface_width, surface_height = surface.get_size()
            if surface_width > 0 and surface_height > 0:
                source_width, source_height = surface_width, surface_height

        max_width = min(source_width, max(150, self.character_panel_rect.width // 2 - 12))
        max_height = min(source_height, max(220, self.character_panel_rect.height - (y - self.character_panel_rect.top) - 32))
        scale = min(max_width / source_width, max_height / source_height, 1.0)
        portrait_width = max(1, int(source_width * scale))
        portrait_height = max(1, int(source_height * scale))
        return pygame.Rect(self.character_panel_rect.left + 16, y, portrait_width, portrait_height)

    @staticmethod
    def _call_or_attr(player_char, name: str, default: int = 0) -> int:
        value = getattr(player_char, name, default)
        if callable(value):
            try:
                value = value()
            except (TypeError, ValueError):
                value = default
        try:
            return int(value)
        except (TypeError, ValueError):
            return int(default)

    def _get_jump_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Jump" in skills:
            return skills["Jump"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Jump":
                return skill
        return None

    def _has_jump_mods(self, player_char) -> bool:
        jump_skill = self._get_jump_skill(player_char)
        return bool(jump_skill and hasattr(jump_skill, "modifications"))

    def _get_totem_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            return skills["Totem"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Totem":
                return skill
        return None

    def _has_totem_aspects(self, player_char) -> bool:
        totem_skill = self._get_totem_skill(player_char)
        return bool(totem_skill and hasattr(totem_skill, "get_unlocked_aspects"))

    @staticmethod
    def _is_living_companion(entity: Any) -> bool:
        is_alive = getattr(entity, "is_alive", None)
        return bool(is_alive()) if callable(is_alive) else True

    def active_companion_for_display(self, player_char) -> tuple[str, Any] | None:
        """Return the companion that should be visually highlighted."""
        familiar = getattr(player_char, "familiar", None)
        if familiar is not None and self._is_living_companion(familiar):
            return "Familiar", familiar

        summons = getattr(player_char, "summons", {}) or {}
        for summon in summons.values():
            if self._is_living_companion(summon):
                return "Summon", summon
        return None

    def companion_summary_rows(self, kind: str, companion: Any) -> list[tuple[str, str]]:
        """Return compact Character Menu rows for the selected companion."""
        name = str(getattr(companion, "name", "") or kind)
        identity = (
            getattr(companion, "race", None)
            or getattr(companion, "spec", None)
            or getattr(companion, "cls", None)
            or kind
        )
        rows = [("Companion", name), ("Type", str(identity))]
        level = getattr(companion, "level", None)
        for attr in ("level", "pro_level"):
            value = getattr(level, attr, None)
            if value is not None:
                rows.append(("Level", str(value)))
                break
        return rows

    def _get_key_items_list(self, player_char):
        special_inv = getattr(player_char, "special_inventory", {})
        if not special_inv:
            return ["No key items"]

        key_items = []
        for item_name, item_list in special_inv.items():
            if not item_list:
                continue
            item_obj = item_list[0]
            quantity = len(item_list)
            if quantity > 1:
                key_items.append(
                    {
                        "text": f"{item_name} ({quantity})",
                        "value": item_obj,
                        "is_header": False,
                    }
                )
            else:
                key_items.append(item_obj)
        return key_items if key_items else ["No key items"]

    def _get_specials_list(self, player_char):
        result = []

        race = getattr(player_char, "race", None)
        virtue = getattr(race, "virtue", None) if race else None
        sin = getattr(race, "sin", None) if race else None
        if virtue and getattr(virtue, "name", ""):
            result.append("--- RACIAL TRAITS ---")
            result.append(virtue)
            if sin and getattr(sin, "name", ""):
                result.append(sin)

        spellbook = getattr(player_char, "spellbook", None)
        if spellbook and isinstance(spellbook, dict):
            spells = spellbook.get("Spells", {}) or {}
            skills = spellbook.get("Skills", {}) or {}
            if spells:
                result.append("--- SPELLS ---")
                result.extend(spells.values())
            if skills:
                result.append("--- SKILLS ---")
                result.extend(skills.values())

        return result if result else ["No special abilities"]

    @staticmethod
    def _check_mod(player_char, mod: str, default: int = 0) -> int:
        try:
            return int(player_char.check_mod(mod))
        except (AttributeError, KeyError, TypeError, ValueError):
            combat = getattr(player_char, "combat", None)
            fallback = {
                "weapon": getattr(combat, "attack", default),
                "armor": getattr(combat, "defense", default),
                "magic": getattr(combat, "magic", default),
                "magic def": getattr(combat, "magic_def", default),
                "shield": default,
                "speed": getattr(getattr(player_char, "stats", None), "dex", default),
            }
            return int(fallback.get(mod, default) or default)

    @staticmethod
    def _non_negative_int(value: Any, default: int = 0) -> int:
        try:
            return max(0, int(value or default))
        except (TypeError, ValueError):
            return max(0, int(default))

    @staticmethod
    def xp_progress(player_char) -> float:
        level = getattr(player_char, "level", None)
        raw_to_next = getattr(level, "exp_to_gain", 0)
        if isinstance(raw_to_next, str) and raw_to_next.upper() == "MAX":
            return 1.0
        to_next = ModernCharacterScreen._non_negative_int(raw_to_next)
        total = ModernCharacterScreen.xp_required_for_current_level(player_char)
        if total <= 0:
            return 0.0
        current = max(0, total - to_next)
        return max(0.0, min(1.0, current / total))

    @staticmethod
    def xp_label(player_char) -> str:
        level = getattr(player_char, "level", None)
        raw_to_next = getattr(level, "exp_to_gain", 0)
        if isinstance(raw_to_next, str) and raw_to_next.upper() == "MAX":
            exp = ModernCharacterScreen._non_negative_int(getattr(level, "exp", 0))
            return f"{exp} XP / MAX level"
        to_next = ModernCharacterScreen._non_negative_int(raw_to_next)
        total = ModernCharacterScreen.xp_required_for_current_level(player_char)
        current = max(0, total - to_next)
        return f"{current}/{total} XP ({to_next} next)"

    @staticmethod
    def xp_required_for_current_level(player_char) -> int:
        try:
            return ModernCharacterScreen._non_negative_int(player_char.level_exp())
        except (AttributeError, TypeError, ValueError):
            level = getattr(player_char, "level", None)
            exp = ModernCharacterScreen._non_negative_int(getattr(level, "exp", 0))
            to_next = ModernCharacterScreen._non_negative_int(getattr(level, "exp_to_gain", 0))
            return exp + to_next

    def build_character_summary(self, player_char) -> list[tuple[str, str]]:
        race = self._attr_name(getattr(player_char, "race", None), "")
        cls = self._attr_name(getattr(player_char, "cls", None), "")
        level = getattr(getattr(player_char, "level", None), "level", 1)
        return [
            ("Name", str(getattr(player_char, "name", "Adventurer"))),
            ("Race", race or "Unknown"),
            ("Class", cls or "Unknown"),
            ("Level", str(level)),
        ]

    def location_label(self, player_char) -> str:
        location_z = getattr(player_char, "location_z", 0)
        try:
            location_z = int(location_z)
        except (TypeError, ValueError):
            location_z = 0
        if location_z == 0:
            return "Town"
        return f"Dungeon Level {location_z}"

    def build_portrait_details(self, player_char) -> list[tuple[str, str]]:
        gold = self._non_negative_int(getattr(player_char, "gold", 0))
        return [
            ("Gold", f"{gold}G"),
            ("Location", self.location_label(player_char)),
        ]

    def _draw_portrait_details(self, rows: list[tuple[str, str]], rect: pygame.Rect, y: int) -> int:
        font = self.normal_font
        line_gap = 6
        label_width = max(62, rect.width // 3)
        value_width = max(1, rect.width - label_width - 12)
        for label, value in rows:
            self._draw_text(label, font, self.colors.GRAY, rect.left + 4, y, label_width)
            value_text = self._fit_text(value, font, value_width)
            value_x = rect.right - 4 - font.size(value_text)[0]
            self._draw_text(value_text, font, self.colors.WHITE, value_x, y, value_width)
            y += font.get_height() + line_gap
            if y > rect.bottom:
                break
        return y

    def build_core_attributes(self, player_char) -> list[tuple[str, str]]:
        stats = getattr(player_char, "stats", None)
        return [
            ("Strength", str(getattr(stats, "strength", 0))),
            ("Intelligence", str(getattr(stats, "intel", 0))),
            ("Wisdom", str(getattr(stats, "wisdom", 0))),
            ("Constitution", str(getattr(stats, "con", 0))),
            ("Charisma", str(getattr(stats, "charisma", 0))),
            ("Dexterity", str(getattr(stats, "dex", 0))),
        ]

    def attack_display(self, player_char) -> str:
        main_attack = self._check_mod(player_char, "weapon")
        equipment = getattr(player_char, "equipment", {}) or {}
        offhand = equipment.get("OffHand") if isinstance(equipment, dict) else None
        if getattr(offhand, "typ", None) == "Weapon":
            return f"{main_attack}/{self._check_mod(player_char, 'offhand')}"
        return str(main_attack)

    def build_combat_stats(self, player_char) -> list[tuple[str, str]]:
        health = getattr(player_char, "health", None)
        mana = getattr(player_char, "mana", None)
        try:
            crit = float(player_char.critical_chance("Weapon")) * 100
        except (AttributeError, TypeError, ValueError):
            crit = 0.0
        weight = self._call_or_attr(player_char, "current_weight")
        max_weight = self._call_or_attr(player_char, "max_weight")
        return [
            ("HP", f"{getattr(health, 'current', 0)}/{getattr(health, 'max', 0)}"),
            ("MP", f"{getattr(mana, 'current', 0)}/{getattr(mana, 'max', 0)}"),
            ("Attack", self.attack_display(player_char)),
            ("Defense", str(self._check_mod(player_char, "armor"))),
            ("Magic Attack", str(self._check_mod(player_char, "magic"))),
            ("Magic Defense", str(self._check_mod(player_char, "magic def"))),
            ("Critical", f"{crit:.1f}%"),
            ("Block", f"{self._check_mod(player_char, 'shield')}%"),
            ("Speed", str(self._check_mod(player_char, "speed"))),
            ("Weight", f"{weight}/{max_weight}"),
        ]

    def build_equipment_slots(self, player_char) -> list[EquipmentSlotSummary]:
        equipment = getattr(player_char, "equipment", {}) or {}
        slots: list[EquipmentSlotSummary] = []
        weapon = equipment.get("Weapon") if isinstance(equipment, dict) else None
        for slot in EQUIPMENT_SLOT_ORDER:
            item = equipment.get(slot) if isinstance(equipment, dict) else None
            if slot == "OffHand" and self.should_show_two_handed_occupancy(player_char, weapon, item):
                item = weapon
                description = "Off-hand occupied by two-handed weapon."
                detail_rows = self.equipment_slot_detail_rows("Weapon", item)
                details = tuple(f"{label}: {value}" for label, value in detail_rows)
                slots.append(
                    EquipmentSlotSummary(
                        slot,
                        self._equipment_display_name(item),
                        description,
                        ", ".join(details),
                        details,
                        detail_rows,
                        (),
                        item,
                    )
                )
                continue
            if self.is_empty_equipment(item):
                slots.append(EquipmentSlotSummary(slot, "(empty)", "No item equipped.", ""))
                continue
            description = str(getattr(item, "description", "") or getattr(item, "desc", "") or "")
            detail_rows = self.equipment_slot_detail_rows(slot, item)
            details = tuple(f"{label}: {value}" for label, value in detail_rows)
            buffs = self.equipment_slot_buffs(item)
            slots.append(
                EquipmentSlotSummary(
                    slot,
                    self._equipment_display_name(item),
                    description,
                    ", ".join(details),
                    details,
                    detail_rows,
                    buffs,
                    item,
                )
            )
        return slots

    def selectable_equipment_slots(self, player_char) -> list[str]:
        return [slot.slot for slot in self.build_equipment_slots(player_char) if slot.implemented]

    def selected_equipment_slot(self, player_char) -> str:
        slots = self.selectable_equipment_slots(player_char)
        if not slots:
            return "Weapon"
        self.selected_equipment_slot_index = max(0, min(self.selected_equipment_slot_index, len(slots) - 1))
        return slots[self.selected_equipment_slot_index]

    def set_selected_equipment_slot(self, player_char, slot_name: str) -> None:
        slots = self.selectable_equipment_slots(player_char)
        if slot_name in slots:
            self.selected_equipment_slot_index = slots.index(slot_name)

    def move_equipment_selector(self, player_char, direction: str) -> None:
        current = self.selected_equipment_slot(player_char)
        nav = {
            "Helmet": {"down": "Armor", "left": "Weapon", "right": "OffHand"},
            "Weapon": {"up": "Helmet", "right": "Armor", "down": "Ring"},
            "Armor": {"up": "Helmet", "left": "Weapon", "right": "OffHand", "down": "Ring"},
            "OffHand": {"up": "Helmet", "left": "Armor", "down": "Pendant"},
            "Ring": {"up": "Weapon", "right": "Pendant"},
            "Pendant": {"up": "OffHand", "left": "Ring"},
        }
        target = nav.get(current, {}).get(direction, current)
        self.set_selected_equipment_slot(player_char, target)

    @staticmethod
    def is_empty_equipment(item: Any) -> bool:
        if item is None:
            return True
        return str(getattr(item, "subtyp", "") or "") == "None"

    def should_show_two_handed_occupancy(self, player_char, weapon: Any, offhand: Any) -> bool:
        if self.is_empty_equipment(weapon) or not self.is_empty_equipment(offhand):
            return False
        try:
            handed = int(getattr(weapon, "handed", 1) or 1)
        except (TypeError, ValueError):
            handed = 1
        if handed != 2:
            return False
        if self.can_use_two_hander_without_blocking_offhand(player_char, weapon):
            return False
        return True

    def can_use_two_hander_without_blocking_offhand(self, player_char, weapon: Any) -> bool:
        cls = getattr(player_char, "cls", None)
        cls_name = self._attr_name(cls, "")
        if cls_name in {"Lancer", "Dragoon"} and str(getattr(weapon, "subtyp", "") or "") == "Polearm":
            return True
        try:
            return bool(cls.equip_check(weapon, "OffHand"))
        except (AttributeError, KeyError, TypeError, ValueError):
            return False

    @staticmethod
    def _display_number(value: Any) -> str:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return str(value)
        if numeric.is_integer():
            return str(int(numeric))
        return f"{numeric:.2f}".rstrip("0").rstrip(".")

    @staticmethod
    def _display_percent(value: Any) -> str:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return str(value)
        return f"{numeric * 100:.1f}%".replace(".0%", "%")

    @staticmethod
    def _weapon_handedness(item) -> str:
        handed = getattr(item, "handed", None)
        try:
            if int(handed) >= 2:
                return "Two-handed"
            if int(handed) == 1:
                return "One-handed"
        except (TypeError, ValueError):
            pass

        subtyp = str(getattr(item, "subtyp", "") or "")
        return "Two-handed" if subtyp in TWO_HANDED_WEAPON_SUBTYPES else "One-handed"

    @classmethod
    def _equipment_display_name(cls, item) -> str:
        name = cls._attr_name(item)
        typ = str(getattr(item, "typ", "") or "")
        if typ == "Weapon":
            handedness = cls._weapon_handedness(item)
            if handedness == "Two-handed":
                return f"{name} (2H)"
            if handedness == "One-handed":
                return f"{name} (1H)"
        return name

    def equipment_slot_detail_rows(self, slot: str, item) -> tuple[tuple[str, str], ...]:
        details: list[tuple[str, str]] = []
        typ = str(getattr(item, "typ", "") or "")
        subtyp = str(getattr(item, "subtyp", "") or "")
        if subtyp and subtyp != "None" and slot in {"Weapon", "Armor", "OffHand", "Helmet"}:
            details.append(("Type", subtyp))

        if slot in {"Weapon", "OffHand"} and (typ == "Weapon" or getattr(item, "damage", None) not in (None, 0, "")):
            details.append(("Base Damage", self._display_number(getattr(item, "damage", 0))))
            details.append(("Crit", self._display_percent(getattr(item, "crit_chance", getattr(item, "crit", 0)))))
        elif slot in {"Armor", "Helmet"} or typ in {"Armor", "Helmet"} or getattr(item, "armor", None) not in (None, 0, ""):
            details.append(("Base Armor", self._display_number(getattr(item, "armor", 0))))
        elif slot == "OffHand" or typ == "OffHand":
            mod = getattr(item, "mod", None)
            if subtyp == "Shield" and mod not in (None, "", 0):
                details.append(("Block", self._display_percent(mod)))
            elif mod not in (None, "", 0):
                details.append(("Spell Mod", self._display_number(mod)))

        element = getattr(item, "element", None)
        if element:
            details.append(("Element", str(element)))
        return tuple(details)

    def equipment_slot_details(self, slot: str, item) -> tuple[str, ...]:
        return tuple(f"{label}: {value}" for label, value in self.equipment_slot_detail_rows(slot, item))

    def equipment_slot_buffs(self, item) -> tuple[str, ...]:
        buffs: list[str] = []
        if self._attr_name(item) == "Svalinn":
            buffs.append("+25% Fire Resistance")

        resist_mod = getattr(item, "resist_mod", None)
        element = getattr(item, "element", None)
        if resist_mod is not None and element:
            try:
                percent = int(float(resist_mod) * 100)
            except (TypeError, ValueError):
                percent = 0
            if percent:
                buffs.append(f"+{percent}% {element} Resistance")

        resistances = getattr(item, "resistances", None)
        if isinstance(resistances, dict):
            for name, value in resistances.items():
                try:
                    percent = int(float(value) * 100)
                except (TypeError, ValueError):
                    percent = 0
                if percent:
                    buffs.append(f"{percent:+d}% {name} Resistance")

        subtyp = str(getattr(item, "subtyp", "") or "")
        mod = str(getattr(item, "mod", "") or "")
        if mod and mod not in {"0", "No Mod", "None"} and not (subtyp == "Shield" and self._is_number(mod)):
            if mod.startswith("Resist-"):
                buffs.append(f"+50% {mod.removeprefix('Resist-')} Resistance")
            elif mod.startswith("Immune-"):
                buffs.append(f"Immune to {mod.removeprefix('Immune-')}")
            else:
                buffs.append(mod)
        return tuple(buffs)

    @staticmethod
    def _is_number(value: Any) -> bool:
        try:
            float(value)
        except (TypeError, ValueError):
            return False
        return True

    def group_resistances(self, player_char) -> dict[str, list[ResistanceSummary]]:
        resistance = getattr(player_char, "resistance", {}) or {}
        weaknesses: list[ResistanceSummary] = []
        resistances: list[ResistanceSummary] = []
        for name in RESISTANCE_ORDER:
            try:
                value = float(player_char.check_mod("resist", typ=name) or 0.0)
            except (AttributeError, TypeError, ValueError):
                value = float(resistance.get(name, 0.0) or 0.0)
            summary = ResistanceSummary(name, value)
            if value < 0:
                weaknesses.append(summary)
            elif value > 0:
                resistances.append(summary)
        return {"weaknesses": weaknesses, "resistances": resistances}

    def collect_equipment_buffs(self, player_char) -> list[EquipmentBuffSummary]:
        equipment = getattr(player_char, "equipment", {}) or {}
        buffs: list[EquipmentBuffSummary] = []
        seen: set[str] = set()

        def add(name: str, source: str) -> None:
            if not name or name in seen:
                return
            buffs.append(EquipmentBuffSummary(name, source))
            seen.add(name)

        for slot in ("Weapon", "Armor", "OffHand", "Ring", "Pendant"):
            item = equipment.get(slot)
            mod = str(getattr(item, "mod", "") or "")
            if not mod:
                continue
            if mod in {"Vision", "Flying", "Invisible", "Accuracy", "Dodge", "Block"} or mod.startswith("Status-"):
                add(mod, f"{slot}: {self._attr_name(item)}")

        if getattr(player_char, "sight", False):
            add("Vision", "Character state")
        if getattr(player_char, "flying", False):
            add("Flying", "Character state")
        if getattr(player_char, "invisible", False):
            add("Invisible", "Character state")
        return buffs

    def _fit_text(self, text: str, font, max_width: int) -> str:
        if font.size(text)[0] <= max_width:
            return text
        ellipsis = "..."
        trimmed = text
        while trimmed and font.size(trimmed + ellipsis)[0] > max_width:
            trimmed = trimmed[:-1]
        return (trimmed + ellipsis) if trimmed else ellipsis

    def _draw_text(self, text: str, font, color, x: int, y: int, max_width: int | None = None) -> int:
        display_text = self._fit_text(str(text), font, max_width) if max_width is not None else str(text)
        surface = font.render(display_text, True, color)
        self.screen.blit(surface, (x, y))
        return surface.get_height()

    def _draw_wrapped_text(self, text: str, font, color, x: int, y: int, max_width: int, max_lines: int = 2) -> int:
        words = str(text).split()
        if not words:
            return y

        lines: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
        if current and len(lines) < max_lines:
            lines.append(current)

        for index, line in enumerate(lines[:max_lines]):
            if index == max_lines - 1 and len(lines) == max_lines and words and " ".join(words) != " ".join(lines):
                line = self._fit_text(line, font, max_width)
            self._draw_text(line, font, color, x, y, max_width)
            y += font.get_height() + 4
        return y

    def _draw_panel(self, rect: pygame.Rect, title: str | None = None) -> int:
        self.draw_semi_transparent_panel(rect, alpha=205)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, rect, 2)
        y = rect.top + 14
        if title:
            self._draw_text(title, self.large_font, self.colors.GOLD, rect.left + 16, y, rect.width - 32)
            y += self.large_font.get_height() + 10
        return y

    def _draw_divider(self, rect: pygame.Rect, y: int) -> None:
        pygame.draw.line(
            self.screen,
            self.colors.BORDER_COLOR,
            (rect.left + 16, y),
            (rect.right - 16, y),
            1,
        )

    def draw_tabs(self):
        self._draw_panel(self.tab_rect)
        for index, tab in enumerate(self.tabs):
            rect = self.tab_button_rects()[index]
            active = index == self.active_tab_index
            if active:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, rect, 2)
            self._draw_text(tab.label, self.normal_font, self.colors.GOLD if active else self.colors.WHITE, rect.left + 12, rect.centery - self.normal_font.get_height() // 2, rect.width - 24)

    def tab_button_rects(self) -> list[pygame.Rect]:
        """Return clickable rectangles for character tabs."""
        x = self.tab_rect.left + 12
        tab_width = max(120, min(190, (self.tab_rect.width - 24) // max(1, len(self.tabs))))
        return [
            pygame.Rect(x + (index * tab_width), self.tab_rect.top + 8, tab_width - 8, self.tab_rect.height - 16)
            for index, _tab in enumerate(self.tabs)
        ]

    def draw_character_panel(self, player_char):
        y = self._draw_panel(self.character_panel_rect, "Character")
        portrait_surface = self.load_portrait(player_char)
        portrait = self.portrait_frame_rect(y, portrait_surface)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, portrait)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, portrait, 2)
        if portrait_surface is not None:
            self._draw_fitted_surface(portrait_surface, portrait)
            pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, portrait, 2)
        else:
            self._draw_text("Portrait", self.small_font, self.colors.GRAY, portrait.left + 10, portrait.centery - self.small_font.get_height() // 2, portrait.width - 20)

        detail_y = portrait.bottom + 12
        detail_rect = pygame.Rect(portrait.left, detail_y, portrait.width, self.character_panel_rect.bottom - detail_y - 16)
        self._draw_portrait_details(self.build_portrait_details(player_char), detail_rect, detail_y)

        info_x = portrait.right + 16
        info_y = y
        info_width = self.character_panel_rect.right - info_x - 16
        identity_label_font = self.normal_font
        identity_value_font = self.large_font
        for label, value in self.build_character_summary(player_char):
            label_text = label.upper()
            label_width = identity_label_font.size(label_text)[0]
            self._draw_text(label_text, identity_label_font, self.colors.GRAY, info_x + max(0, info_width - label_width), info_y, info_width)
            info_y += identity_label_font.get_height()
            value_text = self._fit_text(value, identity_value_font, info_width)
            value_width = identity_value_font.size(value_text)[0]
            self._draw_text(value_text, identity_value_font, self.colors.WHITE, info_x + max(0, info_width - value_width), info_y, info_width)
            info_y += identity_value_font.get_height() + 8

        bar_width = max(140, info_width * 3 // 4)
        bar_rect = pygame.Rect(self.character_panel_rect.right - 16 - bar_width, info_y + 2, bar_width, 18)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, bar_rect)
        fill_rect = pygame.Rect(bar_rect.left, bar_rect.top, int(bar_rect.width * self.xp_progress(player_char)), bar_rect.height)
        pygame.draw.rect(self.screen, self.colors.GREEN, fill_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, bar_rect, 1)
        xp_label = self.xp_label(player_char)
        xp_label_width = self.small_font.size(xp_label)[0]
        xp_label_x = self.character_panel_rect.right - 16 - min(info_width, xp_label_width)
        self._draw_text(xp_label, self.small_font, self.colors.GRAY, xp_label_x, bar_rect.bottom + 6, info_width)

        attribute_rows = self.build_core_attributes(player_char)
        y = bar_rect.bottom + self.small_font.get_height() + 22
        attribute_rect = pygame.Rect(info_x - 16, y, self.character_panel_rect.right - info_x + 16, self.character_panel_rect.bottom - y - 16)
        attribute_font = self.large_font
        attribute_gap = 8
        available_attribute_height = self.character_panel_rect.bottom - y - self.large_font.get_height() - 16
        large_attribute_height = len(attribute_rows) * (self.large_font.get_height() + attribute_gap)
        normal_attribute_height = len(attribute_rows) * (self.normal_font.get_height() + 2)
        if large_attribute_height > available_attribute_height:
            attribute_font = self.normal_font
            attribute_gap = 2
        if normal_attribute_height > available_attribute_height:
            attribute_font = self.small_font
            attribute_gap = 2
        self._draw_divider(attribute_rect, y - 10)
        self._draw_text("Core Attributes", self.large_font, self.colors.GOLD, info_x, y, info_width)
        y += self.large_font.get_height() + 8
        y = self._draw_key_values(
            attribute_rows,
            attribute_rect,
            y,
            font=attribute_font,
            label_padding=36,
            right_align_values=True,
            row_gap=attribute_gap,
            bottom_limit=self.character_panel_rect.bottom - 16,
        )

    def draw_combat_panel(self, player_char):
        y = self._draw_panel(self.combat_panel_rect, "Combat Stats")
        combat_rows = self.build_combat_stats(player_char)
        groups = self.group_resistances(player_char)
        companion_entry = self.active_companion_for_display(player_char)
        companion_height = 112 if companion_entry else 0
        resistance_font = self.small_font
        resistance_row_gap = 3
        resistance_row_height = resistance_font.get_height() + resistance_row_gap
        resistance_height = self.large_font.get_height() + 6 + (RESISTANCE_SLOT_COUNT * resistance_row_height)
        resistance_top = self.combat_panel_rect.bottom - resistance_height - 16
        companion_top = resistance_top
        if companion_entry:
            companion_top = max(y + 84, resistance_top - companion_height - 12)
        available_stat_height = companion_top - y - 12
        if available_stat_height >= len(combat_rows) * (self.large_font.get_height() + 4):
            stat_font = self.large_font
            stat_gap = 4
        elif available_stat_height >= len(combat_rows) * (self.normal_font.get_height() + 3):
            stat_font = self.normal_font
            stat_gap = 3
        else:
            stat_font = self.small_font
            stat_gap = 1
        y = self._draw_key_values(
            combat_rows,
            self.combat_panel_rect,
            y,
            font=stat_font,
            row_gap=stat_gap,
            right_align_values=True,
            bottom_limit=companion_top - 12,
        )
        if companion_entry:
            companion_rect = pygame.Rect(
                self.combat_panel_rect.left + 16,
                companion_top,
                self.combat_panel_rect.width - 32,
                min(companion_height, max(76, resistance_top - companion_top - 12)),
            )
            self._draw_companion_art_block(companion_entry[0], companion_entry[1], companion_rect)

        y = max(y + 12, resistance_top)
        self._draw_divider(self.combat_panel_rect, y - 10)
        column_gap = 12
        column_width = (self.combat_panel_rect.width - 32 - column_gap) // 2
        weakness_rect = pygame.Rect(self.combat_panel_rect.left + 16, y, column_width, self.combat_panel_rect.bottom - y - 16)
        resistance_rect = pygame.Rect(weakness_rect.right + column_gap, y, column_width, weakness_rect.height)
        self._draw_text("Weaknesses", self.large_font, self.colors.RED, weakness_rect.left, y, weakness_rect.width)
        self._draw_text("Resistances", self.large_font, self.colors.GREEN, resistance_rect.left, y, resistance_rect.width)
        group_y = y + self.large_font.get_height() + 6
        self._draw_resistance_group(groups["weaknesses"], weakness_rect, group_y, self.colors.RED, font=resistance_font, row_gap=resistance_row_gap)
        self._draw_resistance_group(groups["resistances"], resistance_rect, group_y, self.colors.GREEN, font=resistance_font, row_gap=resistance_row_gap)

    def _draw_companion_art_block(self, kind: str, companion: Any, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, (14, 14, 19), rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, rect, 1)
        art_size = max(54, min(84, rect.height - 20, rect.width // 4))
        art_rect = pygame.Rect(rect.left + 10, rect.top + (rect.height - art_size) // 2, art_size, art_size)
        self._draw_item_art_backdrop(art_rect)
        sprite = self.companion_art_manager.get_scaled_sprite(companion, art_rect.size)
        self.screen.blit(sprite, art_rect)

        text_x = art_rect.right + 12
        text_width = rect.right - text_x - 10
        y = rect.top + 10
        self._draw_text(kind, self.small_font, self.colors.GOLD, text_x, y, text_width)
        y += self.small_font.get_height() + 4
        for label, value in self.companion_summary_rows(kind, companion)[:3]:
            self._draw_text(label, self.small_font, self.colors.GRAY, text_x, y, max(70, text_width // 3))
            self._draw_text(
                value,
                self.small_font,
                self.colors.WHITE,
                text_x + max(76, text_width // 3),
                y,
                max(40, text_width - max(76, text_width // 3)),
            )
            y += self.small_font.get_height() + 3

    def _draw_key_values(
        self,
        rows: list[tuple[str, str]],
        rect: pygame.Rect,
        y: int,
        font=None,
        *,
        label_padding: int = 10,
        right_align_values: bool = False,
        row_gap: int = 8,
        bottom_limit: int | None = None,
    ) -> int:
        font = font or self.normal_font
        bottom_limit = bottom_limit if bottom_limit is not None else rect.bottom - 24
        label_width = min(220, max((font.size(label)[0] for label, _ in rows), default=80) + label_padding)
        x = rect.left + 16
        value_x = x + label_width
        max_value_width = rect.right - value_x - 16
        for label, value in rows:
            self._draw_text(label, font, self.colors.GRAY, x, y, label_width - label_padding)
            value_text = self._fit_text(value, font, max_value_width)
            draw_x = value_x
            if right_align_values:
                value_width = font.size(value_text)[0]
                draw_x = value_x + max(0, max_value_width - value_width)
            self._draw_text(value_text, font, self.colors.WHITE, draw_x, y, max_value_width)
            y += font.get_height() + row_gap
            if y > bottom_limit:
                break
        return y

    def _draw_resistance_group(self, entries: list[ResistanceSummary], rect: pygame.Rect, y: int, color, *, font=None, row_gap: int = 6) -> int:
        font = font or self.normal_font
        if not entries:
            self._draw_text("None", font, self.colors.GRAY, rect.left, y, rect.width)
            return y + font.get_height() + row_gap
        row_height = font.get_height() + row_gap
        for entry in entries:
            text = f"{entry.name} ({entry.value * 100:+.0f}%)"
            self._draw_text(text, font, color, rect.left, y, rect.width)
            y += row_height
        return y

    def _draw_equipment_slot_box(self, slot: EquipmentSlotSummary, rect: pygame.Rect, *, selected: bool = False) -> None:
        bg_color = (18, 16, 15) if slot.item_name != "(empty)" and slot.implemented else self.colors.DARK_GRAY
        border_color = self.colors.GOLD if slot.implemented and slot.item_name != "(empty)" else self.colors.BORDER_COLOR
        text_color = self.colors.WHITE if slot.implemented else self.colors.GRAY
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, border_color, rect, 2)
        if selected:
            overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
            overlay.fill((*self.colors.HIGHLIGHT_BG[:3], 95))
            self.screen.blit(overlay, rect)
            inner = rect.inflate(-6, -6)
            pygame.draw.rect(self.screen, self.colors.GOLD, inner, 4)
            pygame.draw.rect(self.screen, (255, 244, 170), inner.inflate(-8, -8), 1)
            corner_len = min(28, max(14, rect.width // 7))
            for x1, x2 in ((inner.left, inner.left + corner_len), (inner.right - corner_len, inner.right)):
                pygame.draw.line(self.screen, (255, 244, 170), (x1, inner.top), (x2, inner.top), 3)
                pygame.draw.line(self.screen, (255, 244, 170), (x1, inner.bottom), (x2, inner.bottom), 3)
        x = rect.left + 10
        y = rect.top + 8
        width = rect.width - 20
        self._draw_text(slot.slot, self.normal_font, self.colors.GRAY, x, y, width)
        y += self.normal_font.get_height() + 2
        art_width = min(76, max(58, rect.width // 4))
        art_height = max(72, rect.height - (y - rect.top) - 12)
        art_rect = pygame.Rect(x, y, art_width, art_height)
        if slot.icon_item is not None:
            self._draw_item_art_backdrop(art_rect)
            render = self.item_render_manager.get_scaled_render(slot.icon_item, art_rect.size)
            self.screen.blit(render, art_rect)

        text_x = art_rect.right + 8
        text_width = max(40, rect.right - text_x - 10)
        item_name = self._fit_text(slot.item_name, self.normal_font, text_width)
        self._draw_text(item_name, self.normal_font, text_color, text_x, y, text_width)
        y += self.normal_font.get_height() + 4
        value_x = text_x + min(max(112, (text_width * 2) // 3), max(40, text_width - 40))
        value_width = max(32, rect.right - value_x - 10)
        label_width = max(32, value_x - text_x - 8)
        for label, value in slot.detail_rows[:4]:
            self._draw_text(f"{label}:", self.small_font, self.colors.WHITE, text_x, y, label_width)
            value_text = self._fit_text(value, self.small_font, value_width)
            rendered_width = self.small_font.size(value_text)[0]
            value_draw_x = value_x + max(0, value_width - rendered_width)
            self._draw_text(value_text, self.small_font, self.colors.WHITE, value_draw_x, y, value_width)
            y += self.small_font.get_height()
        for buff in slot.buffs[:2]:
            self._draw_text(f"Buff: {buff}", self.small_font, self.colors.GOLD, text_x, y, text_width)
            y += self.small_font.get_height()

    def _draw_item_art_backdrop(self, rect: pygame.Rect) -> None:
        backdrop = pygame.Surface(rect.size, pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 150))
        self.screen.blit(backdrop, rect)
        pygame.draw.rect(self.screen, (124, 99, 62), rect, 1)

    def equipment_slot_rects(self, rect: pygame.Rect | None = None) -> dict[str, pygame.Rect]:
        """Return fixed paper-doll slot rectangles for hit testing and drawing."""
        rect = rect or self.equipment_layout_rect()
        box_width = min(260, max(180, (rect.width - 56) // 3))
        box_height = min(150, max(140, (rect.height - 28) // 3))
        center_x = rect.centerx
        row_gap = max(12, (rect.height - (box_height * 3) - 36) // 2)
        top_y = rect.top + 8
        middle_y = top_y + box_height + row_gap
        bottom_y = middle_y + box_height + row_gap

        return {
            "Helmet": pygame.Rect(center_x - box_width // 2, top_y, box_width, box_height),
            "Weapon": pygame.Rect(rect.left, middle_y, box_width, box_height),
            "Armor": pygame.Rect(center_x - box_width // 2, middle_y, box_width, box_height),
            "OffHand": pygame.Rect(rect.right - box_width, middle_y, box_width, box_height),
            "Ring": pygame.Rect(center_x - box_width - 8, bottom_y, box_width, box_height),
            "Pendant": pygame.Rect(center_x + 8, bottom_y, box_width, box_height),
        }

    def equipment_layout_rect(self) -> pygame.Rect:
        """Return the paper-doll layout rect without drawing the surrounding panel."""
        y = self.details_rect.top + 14 + self.large_font.get_height() + 10
        return pygame.Rect(self.details_rect.left + 28, y, self.details_rect.width - 56, self.details_rect.bottom - y - 20)

    def _draw_equipment_paper_doll(self, slots: list[EquipmentSlotSummary], rect: pygame.Rect, selected_slot: str) -> None:
        slot_by_name = {slot.slot: slot for slot in slots}
        positions = self.equipment_slot_rects(rect)
        for slot_name in EQUIPMENT_SLOT_ORDER:
            slot = slot_by_name.get(slot_name)
            if slot is not None:
                self._draw_equipment_slot_box(slot, positions[slot_name], selected=slot_name == selected_slot and slot.implemented)

    def draw_equipment_tab(self, player_char):
        y = self._draw_panel(self.details_rect, "Equipment")
        helper = (
            "Arrows: Select gear  Enter: Change  E/Esc: Back"
            if self.equipment_selector_active
            else "E: Select gear"
        )
        helper_width = self.small_font.size(helper)[0]
        self._draw_text(
            helper,
            self.small_font,
            self.colors.GRAY,
            self.details_rect.right - 16 - min(helper_width, self.details_rect.width - 32),
            self.details_rect.top + 18,
            self.details_rect.width - 32,
        )
        layout_rect = self.equipment_layout_rect()
        slots = self.build_equipment_slots(player_char)
        selected_slot = self.selected_equipment_slot(player_char) if self.equipment_selector_active else ""
        self._draw_equipment_paper_doll(slots, layout_rect, selected_slot)

    def action_rects(self) -> list[pygame.Rect]:
        """Return clickable rectangles for the bottom action menu."""
        y = self.actions_rect.top + 14 + self.large_font.get_height() + 10
        x = self.actions_rect.left + 16
        option_width = max(130, (self.actions_rect.width - 32) // max(1, len(self.menu_options)))
        return [
            pygame.Rect(x + (index * option_width), y, option_width - 8, self.actions_rect.bottom - y - 12)
            for index, _option in enumerate(self.menu_options)
        ]

    def draw_menu(self):
        y = self._draw_panel(self.actions_rect, "Actions")
        for index, option in enumerate(self.menu_options):
            rect = self.action_rects()[index]
            if index == self.current_selection:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, rect, 1)
            self._draw_text(option, self.small_font, self.colors.GOLD if index == self.current_selection else self.colors.WHITE, rect.left + 8, rect.centery - self.small_font.get_height() // 2, rect.width - 16)

    def draw_all(self, player_char, do_flip=True):
        self.draw_background()
        self.draw_tabs()
        if self.active_tab.key == "character":
            self.draw_character_panel(player_char)
            self.draw_combat_panel(player_char)
        elif self.active_tab.key == "equipment":
            self.draw_equipment_tab(player_char)
        self.draw_menu()
        if do_flip:
            pygame.display.flip()

    def _open_menu_choice(self, chosen: str, player_char) -> str | None:
        if chosen == "Inventory":
            popup = InventoryPopupMenu(self.presenter, self)
            popup.show(player_char, flush_events=True, require_key_release=True)
        elif chosen == "Quests":
            from .popup_menus import QuestPopupMenu
            popup = QuestPopupMenu(self.presenter, self)
            _ = popup.show(player_char, flush_events=True, require_key_release=True)
        elif chosen == "Key Items":
            special_inv = getattr(player_char, "special_inventory", {})
            if not special_inv:
                self.draw_all(player_char, do_flip=False)
                popup = ConfirmationPopup(self.presenter, "You do not have any key items.", show_buttons=False)
                popup.show(flush_events=True, require_key_release=True)
            else:
                popup = SimpleListPopupMenu(self.presenter, self, title="Key Items", source_fn=self._get_key_items_list)
                _ = popup.show(player_char, flush_events=True, require_key_release=True)
        elif chosen == "Bestiary":
            popup = BestiaryPopupMenu(self.presenter, self)
            _ = popup.show(player_char, flush_events=True, require_key_release=True)
        elif chosen == "Specials":
            popup = SimpleListPopupMenu(self.presenter, self, title="Special Abilities", source_fn=self._get_specials_list)
            _ = popup.show(player_char, flush_events=True, require_key_release=True)
        elif chosen == "Jump Mods":
            popup = JumpModsPopupMenu(self.presenter, self, title="Jump Modifications")
            _ = popup.show(player_char, flush_events=True, require_key_release=True)
        elif chosen == "Totem Aspects":
            popup = TotemAspectsPopupMenu(self.presenter, self, title="Totem Aspects")
            _ = popup.show(player_char, flush_events=True, require_key_release=True)
        elif chosen == "Exit Menu":
            return chosen
        return None

    def _base_menu_options(self) -> list[str]:
        return ["Inventory", "Quests", "Key Items", "Bestiary", "Specials", "Exit Menu"]

    def open_selected_equipment_change(self, player_char) -> None:
        slot_name = self.selected_equipment_slot(player_char)
        popup = EquipmentPopupMenu(self.presenter, self)
        popup.build_items(player_char)
        for index, entry in enumerate(popup.items):
            if isinstance(entry, tuple) and entry[0] == slot_name:
                popup.selected_index = index
                popup.on_select(player_char, entry)
                return

    def navigate(self, player_char, flush_events=True, require_key_release=True):
        menu_options = self._base_menu_options()
        if self._has_jump_mods(player_char):
            menu_options.insert(-1, "Jump Mods")
        if self._has_totem_aspects(player_char):
            menu_options.insert(-1, "Totem Aspects")
        self.menu_options = menu_options
        self.current_selection = min(self.current_selection, len(self.menu_options) - 1)

        started_in_town = player_char.in_town()
        try:
            input_armed = prepare_guarded_input(flush_events=flush_events, require_key_release=require_key_release)
        except pygame.error:
            input_armed = not require_key_release

        while True:
            if not started_in_town and player_char.in_town():
                return "Exit Menu"

            self.draw_all(player_char)
            input_armed = release_guard_allows_input(require_key_release, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                input_armed = update_input_armed_from_event(event, True, input_armed)

                if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    pos = mouse_position(event)
                    tab_index = hit_index(self.tab_button_rects(), pos)
                    action_index = hit_index(self.action_rects(), pos)
                    if action_index is not None and event.type == pygame.MOUSEMOTION:
                        self.current_selection = action_index
                    elif tab_index is not None and is_left_click(event):
                        if input_armed:
                            self.active_tab_index = tab_index
                            if self.active_tab.key != "equipment":
                                self.equipment_selector_active = False
                        continue
                    elif action_index is not None and is_left_click(event):
                        if input_armed:
                            self.current_selection = action_index
                            result = self._open_menu_choice(self.menu_options[self.current_selection], player_char)
                            if result:
                                return result
                        continue
                    elif self.active_tab.key == "equipment":
                        slot_rects = self.equipment_slot_rects()
                        slot_names = list(EQUIPMENT_SLOT_ORDER)
                        slot_index = hit_index([slot_rects[name] for name in slot_names], pos)
                        if slot_index is not None:
                            self.equipment_selector_active = True
                            self.set_selected_equipment_slot(player_char, slot_names[slot_index])
                            if is_left_click(event) and input_armed:
                                self.open_selected_equipment_change(player_char)
                            continue

                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                if event.type != pygame.KEYDOWN:
                    continue

                if event.key == pygame.K_ESCAPE and self.equipment_selector_active:
                    self.equipment_selector_active = False
                elif event.key == pygame.K_ESCAPE:
                    return "Exit Menu"
                elif event.key == pygame.K_e and self.active_tab.key == "equipment":
                    self.equipment_selector_active = not self.equipment_selector_active
                elif event.key in (pygame.K_TAB, pygame.K_RIGHT):
                    if self.active_tab.key == "equipment" and self.equipment_selector_active and event.key == pygame.K_RIGHT:
                        self.move_equipment_selector(player_char, "right")
                    else:
                        self.move_tab(1)
                elif event.key == pygame.K_LEFT:
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.move_equipment_selector(player_char, "left")
                    else:
                        self.move_tab(-1)
                elif event.key == pygame.K_1:
                    self.select_tab("character")
                elif event.key == pygame.K_2:
                    self.select_tab("equipment")
                elif event.key == pygame.K_UP:
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.move_equipment_selector(player_char, "up")
                    else:
                        self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.move_equipment_selector(player_char, "down")
                    else:
                        self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.open_selected_equipment_change(player_char)
                    else:
                        result = self._open_menu_choice(self.menu_options[self.current_selection], player_char)
                        if result:
                            return result

            self.presenter.clock.tick(30)
