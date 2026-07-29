"""Standard character menu implementation for the Pygame UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pygame

from src.ui_pygame.assets.companion_art_manager import get_companion_art_manager
from src.ui_pygame.assets.item_render_manager import get_item_render_manager
from src.ui_pygame.assets.portrait_manager import PortraitManager
from src.core import items
from src.core.classes import (
    ability_mechanics,
    archdruid,
    astromancer,
    bard,
    demonologist,
    grandmaster,
    lycan,
    nature_totems,
    paladin,
    promotion_kits,
    promotion_mechanic_tab_label,
    wizard,
)

from .confirmation_popup import ConfirmationPopup, draw_popup_close_button, popup_close_clicked
from .input_guards import prepare_guarded_input, release_guard_allows_input, update_input_armed_from_event
from .mouse_helpers import hit_index, is_left_click, mouse_position
from .popup_menus import BestiaryPopupMenu, EquipmentPopupMenu, InventoryPopupMenu, SimpleListPopupMenu, TotemAspectsPopupMenu
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


class ClassCompanionDetailsPopup:
    """Character-tab-style details modal for familiars, companions, and summons."""

    def __init__(self, presenter, parent_screen: "ModernCharacterScreen", player_char, kind: str, companion: Any):
        self.presenter = presenter
        self.parent_screen = parent_screen
        self.player_char = player_char
        self.kind = kind
        self.companion = companion
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.small_font = presenter.small_font
        self.normal_font = presenter.normal_font
        self.large_font = presenter.large_font
        self.colors = parent_screen.colors

        popup_width = min(self.width - 60, max(760, self.width * 9 // 10))
        popup_height = min(self.height - 56, max(500, self.height * 4 // 5))
        self.popup_rect = pygame.Rect(
            (self.width - popup_width) // 2,
            (self.height - popup_height) // 2,
            popup_width,
            popup_height,
        )

    def _content_rects(self) -> tuple[pygame.Rect, pygame.Rect]:
        gap = 12
        content = self.popup_rect.inflate(-32, -104)
        content.top = self.popup_rect.top + 72
        content.height = self.popup_rect.bottom - content.top - 42
        left_width = (content.width * 3) // 5
        left_rect = pygame.Rect(content.left, content.top, left_width, content.height)
        right_rect = pygame.Rect(left_rect.right + gap, content.top, content.right - left_rect.right - gap, content.height)
        return left_rect, right_rect

    def _draw_overlay(self, background_surface) -> None:
        self.screen.blit(background_surface, (0, 0))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.rect(self.screen, (8, 8, 12), self.popup_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.popup_rect, 2)
        draw_popup_close_button(self.screen, self.popup_rect, self.small_font)

    def _draw_art_and_identity(self, rect: pygame.Rect, y: int) -> int:
        art_width = min(max(170, rect.width // 3), rect.width // 2)
        art_height = min(max(190, (rect.height * 9) // 20), rect.height - 180)
        art_rect = pygame.Rect(rect.left + 16, y, art_width, art_height)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, art_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, art_rect, 2)
        sprite = self.parent_screen.companion_art_manager.get_scaled_sprite(self.companion, art_rect.size)
        self.screen.blit(sprite, art_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, art_rect, 2)

        name = self.parent_screen._attr_name(self.companion, self.kind)
        info_x = art_rect.right + 16
        info_y = y
        info_width = rect.right - info_x - 16
        identity_rows = self.parent_screen.companion_summary_rows(self.kind, self.companion)
        identity_rows = [row for row in identity_rows if row[0] != "Companion"]
        identity_rows.insert(0, ("Name", name))
        if getattr(self.companion, "spec", "") != "Tamed":
            identity_rows.append(("XP", self.parent_screen._companion_xp_label(self.companion)))
        bond = self.parent_screen._summon_bond_label(self.player_char, self.companion)
        if bond is not None:
            identity_rows.append(("Bond", bond))

        for index, (label, value) in enumerate(identity_rows):
            label_text = label.upper()
            label_width = self.normal_font.size(label_text)[0]
            self.parent_screen._draw_text(
                label_text,
                self.normal_font,
                self.colors.GRAY,
                info_x + max(0, info_width - label_width),
                info_y,
                info_width,
            )
            info_y += self.normal_font.get_height()
            value_font = self.large_font if index == 0 else self.normal_font
            value_gap = 8 if index == 0 else 4
            value_text = self.parent_screen._fit_text(str(value), value_font, info_width)
            value_width = value_font.size(value_text)[0]
            self.parent_screen._draw_text(
                value_text,
                value_font,
                self.colors.WHITE,
                info_x + max(0, info_width - value_width),
                info_y,
                info_width,
            )
            info_y += value_font.get_height() + value_gap

        return max(art_rect.bottom, info_y)

    def _core_attribute_rows(self) -> list[tuple[str, str]]:
        stats = getattr(self.companion, "stats", None)
        return [
            ("Strength", str(getattr(stats, "strength", 0))),
            ("Intelligence", str(getattr(stats, "intel", 0))),
            ("Wisdom", str(getattr(stats, "wisdom", 0))),
            ("Constitution", str(getattr(stats, "con", 0))),
            ("Charisma", str(getattr(stats, "charisma", 0))),
            ("Dexterity", str(getattr(stats, "dex", 0))),
        ]

    def _combat_rows(self) -> list[tuple[str, str]]:
        health = getattr(self.companion, "health", None)
        mana = getattr(self.companion, "mana", None)
        combat = getattr(self.companion, "combat", None)
        return [
            ("HP", f"{getattr(health, 'current', 0)}/{getattr(health, 'max', 0)}"),
            ("MP", f"{getattr(mana, 'current', 0)}/{getattr(mana, 'max', 0)}"),
            ("Attack", _whole_stat_text(getattr(combat, "attack", 0))),
            ("Defense", _whole_stat_text(getattr(combat, "defense", 0))),
            ("Magic", _whole_stat_text(getattr(combat, "magic", 0))),
            ("Magic Defense", _whole_stat_text(getattr(combat, "magic_def", 0))),
        ]

    def _ability_names(self) -> list[str]:
        spellbook = getattr(self.companion, "spellbook", {}) or {}
        if not isinstance(spellbook, dict):
            return []
        names: list[str] = []
        for bucket in ("Skills", "Spells"):
            abilities = spellbook.get(bucket, {})
            if isinstance(abilities, dict):
                names.extend(str(name) for name in abilities.keys())
        return names

    def _draw_abilities(self, rect: pygame.Rect, y: int, bottom_limit: int) -> int:
        names = self._ability_names()
        self.parent_screen._draw_divider(rect, y - 10)
        self.parent_screen._draw_text("Abilities", self.large_font, self.colors.GOLD, rect.left + 16, y, rect.width - 32)
        y += self.large_font.get_height() + 8
        if not names:
            self.parent_screen._draw_text("None", self.normal_font, self.colors.GRAY, rect.left + 16, y, rect.width - 32)
            return y + self.normal_font.get_height() + 8

        available_lines = max(1, (bottom_limit - y) // (self.small_font.get_height() + 4))
        return self.parent_screen._draw_wrapped_text(
            ", ".join(names),
            self.small_font,
            self.colors.WHITE,
            rect.left + 16,
            y,
            rect.width - 32,
            max_lines=available_lines,
        )

    def _draw_tamed_companion_flavor(self, rect: pygame.Rect, y: int) -> None:
        self.parent_screen._draw_text("Companion Notes", self.large_font, self.colors.GOLD, rect.left + 16, y, rect.width - 32)
        y += self.large_font.get_height() + 10
        notes = [
            getattr(self.companion, "inspect", lambda: "")(),
            "The animal acts through bond and instinct rather than a visible resource pool.",
            "Evolution reflects growing trust and battlefield temperament; deeper effects are a future tuning pass.",
        ]
        for note in notes:
            if not str(note).strip():
                continue
            y = self.parent_screen._draw_wrapped_text(
                str(note).strip(),
                self.normal_font,
                self.colors.WHITE,
                rect.left + 16,
                y,
                rect.width - 32,
                max_lines=3,
            )
            y += 12

    def _draw_tamed_companion_bond_panel(self, rect: pygame.Rect, y: int) -> None:
        rows = self.parent_screen.companion_summary_rows(self.kind, self.companion)
        rows = [(label, value) for label, value in rows if label not in {"Companion", "Type"}]
        if not rows:
            rows = [("Bond", "New")]
        self.parent_screen._draw_key_values(
            rows,
            rect,
            y,
            font=self.normal_font,
            row_gap=8,
            right_align_values=False,
            bottom_limit=rect.bottom - 16,
        )

    def draw(self, background_surface) -> None:
        self._draw_overlay(background_surface)
        name = self.parent_screen._attr_name(self.companion, self.kind)
        title = f"{name} Details"
        title_text = self.presenter.title_font.render(title, True, self.colors.GOLD)
        self.screen.blit(
            title_text,
            (self.popup_rect.centerx - title_text.get_width() // 2, self.popup_rect.top + 18),
        )

        left_rect, right_rect = self._content_rects()
        y = self.parent_screen._draw_panel(left_rect, self.kind)
        y = self._draw_art_and_identity(left_rect, y)
        y += 16
        if getattr(self.companion, "spec", "") == "Tamed":
            self.parent_screen._draw_divider(left_rect, y - 8)
            self._draw_tamed_companion_flavor(left_rect, y)
            right_y = self.parent_screen._draw_panel(right_rect, "Bond & Form")
            self._draw_tamed_companion_bond_panel(right_rect, right_y)
        else:
            self.parent_screen._draw_divider(left_rect, y - 8)
            self.parent_screen._draw_text("Core Attributes", self.large_font, self.colors.GOLD, left_rect.left + 16, y, left_rect.width - 32)
            y += self.large_font.get_height() + 8
            self.parent_screen._draw_key_values(
                self._core_attribute_rows(),
                left_rect,
                y,
                font=self.small_font,
                label_padding=36,
                right_align_values=True,
                row_gap=2,
                bottom_limit=left_rect.bottom - 16,
            )

            y = self.parent_screen._draw_panel(right_rect, "Combat Stats")
            resistance_height = min(
                190,
                self.large_font.get_height() + 8 + (6 * (self.small_font.get_height() + 2)),
            )
            resistance_top = right_rect.bottom - resistance_height - 16
            y = self.parent_screen._draw_key_values(
                self._combat_rows(),
                right_rect,
                y,
                font=self.small_font,
                row_gap=2,
                right_align_values=True,
                bottom_limit=resistance_top - 14,
            )
            y = self._draw_abilities(right_rect, y + 18, resistance_top - 14)
            groups = self.parent_screen.group_resistances(self.companion)
            y = max(y + 12, resistance_top)
            self.parent_screen._draw_divider(right_rect, y - 10)
            column_gap = 12
            column_width = (right_rect.width - 32 - column_gap) // 2
            weakness_rect = pygame.Rect(right_rect.left + 16, y, column_width, right_rect.bottom - y - 16)
            resistance_rect = pygame.Rect(weakness_rect.right + column_gap, y, column_width, weakness_rect.height)
            self.parent_screen._draw_text("Weaknesses", self.large_font, self.colors.RED, weakness_rect.left, y, weakness_rect.width)
            self.parent_screen._draw_text("Resistances", self.large_font, self.colors.GREEN, resistance_rect.left, y, resistance_rect.width)
            group_y = y + self.large_font.get_height() + 6
            self.parent_screen._draw_resistance_group(groups["weaknesses"], weakness_rect, group_y, self.colors.RED, font=self.small_font, row_gap=2)
            self.parent_screen._draw_resistance_group(groups["resistances"], resistance_rect, group_y, self.colors.GREEN, font=self.small_font, row_gap=2)

        footer = "Esc/Enter: Close"
        footer_text = self.small_font.render(footer, True, self.colors.GRAY)
        self.screen.blit(footer_text, (self.popup_rect.left + 16, self.popup_rect.bottom - footer_text.get_height() - 12))
        pygame.display.flip()

    def show(self, background_draw_func=None, flush_events: bool = False, require_key_release: bool = False) -> None:
        if background_draw_func is None:
            background = self.screen.copy()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))
        background_draw_func()
        background_surface = self.screen.copy()
        input_armed = prepare_guarded_input(flush_events=flush_events, require_key_release=require_key_release)

        while True:
            self.draw(background_surface)
            input_armed = release_guard_allows_input(require_key_release, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys

                    sys.exit()
                input_armed = update_input_armed_from_event(event, require_key_release, input_armed)
                if popup_close_clicked(event, self.popup_rect):
                    if input_armed:
                        background_draw_func()
                        return
                    continue
                if event.type != pygame.KEYDOWN or not input_armed:
                    continue
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    background_draw_func()
                    return
            self.presenter.clock.tick(30)


class ModernCharacterScreen(TownScreenBase):
    """RPG-style character menu used by the standard pygame character flow."""

    def __init__(self, presenter, tabs: tuple[CharacterTab, ...] = DEFAULT_CHARACTER_TABS):
        self.tabs = tabs
        self.active_tab_key = tabs[0].key
        self.active_tab_index = 0
        self.portrait_manager = PortraitManager()
        self.item_render_manager = get_item_render_manager()
        self.companion_art_manager = get_companion_art_manager()
        self.selected_equipment_slot_index = 0
        self.selected_class_companion_index = 0
        self.selected_weapon_discipline_index = 0
        self.equipment_selector_active = False
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self.selected_jump_mod_index = 0
        self._jump_mod_row_rects: list[pygame.Rect] = []
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
        for tab in self.tabs:
            if tab.key == self.active_tab_key:
                return tab
        return self.tabs[0]

    def select_tab(self, key: str) -> None:
        for index, tab in enumerate(self.tabs):
            if tab.key == key:
                self.active_tab_key = key
                self.active_tab_index = index
                if key != "equipment":
                    self.equipment_selector_active = False
                if key != "class":
                    self.class_companion_selector_active = False
                    self.weapon_discipline_selector_active = False
                return
        raise ValueError(f"Unknown character tab: {key}")

    def class_mechanic_tab(self, player_char) -> CharacterTab | None:
        if grandmaster.is_weapon_discipline_class(player_char):
            return CharacterTab("class", "Weapon Discipline")
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        mechanic_label = promotion_mechanic_tab_label(class_name)
        summons = getattr(player_char, "summons", {}) or {}
        familiar = getattr(player_char, "familiar", None)
        if class_name in {"Summoner", "Grand Summoner"} or summons:
            return CharacterTab("class", "Summons")
        if class_name in {"Ranger", "Beast Master"}:
            return CharacterTab("class", "Companion & Hunt")
        if mechanic_label:
            return CharacterTab("class", mechanic_label)
        return None

    def visible_tabs(self, player_char=None) -> tuple[CharacterTab, ...]:
        if player_char is None:
            return self.tabs
        equipment_tab = next((tab for tab in self.tabs if tab.key == "equipment"), self.tabs[-1])
        tabs = [self.tabs[0], equipment_tab]
        mechanic_tab = self.class_mechanic_tab(player_char)
        if mechanic_tab is not None:
            tabs.append(mechanic_tab)
        return tuple(tabs)

    def ensure_active_tab_visible(self, player_char) -> None:
        visible = self.visible_tabs(player_char)
        if self.active_tab_key not in {tab.key for tab in visible}:
            self.select_tab(visible[0].key)

    def select_visible_tab_index(self, index: int, player_char) -> None:
        visible = self.visible_tabs(player_char)
        if 0 <= index < len(visible):
            self.select_tab(visible[index].key)

    def active_mechanic_label(self, player_char) -> str:
        if self.active_tab_key != "class":
            return ""
        mechanic_tab = self.class_mechanic_tab(player_char)
        return mechanic_tab.label if mechanic_tab is not None else ""

    def move_tab(self, delta: int, player_char=None) -> None:
        visible = self.visible_tabs(player_char)
        active_index = next(
            (index for index, tab in enumerate(visible) if tab.key == self.active_tab_key),
            0,
        )
        self.select_tab(visible[(active_index + delta) % len(visible)].key)
        if self.active_tab.key != "equipment":
            self.equipment_selector_active = False
        if self.active_tab.key != "class":
            self.class_companion_selector_active = False

    @staticmethod
    def _attr_name(value: Any, default: str = "Unknown") -> str:
        return str(getattr(value, "name", default) or default)

    @staticmethod
    def portrait_filename(player_char) -> str:
        race = ModernCharacterScreen._attr_name(getattr(player_char, "race", None), "Human")
        race_key = PortraitManager.normalize_key(race, "human")
        return f"{race_key}_base_portraits.png"

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

    def portrait_frame_rect(
        self,
        y: int,
        surface: pygame.Surface | None = None,
        *,
        reserved_bottom: int = 32,
    ) -> pygame.Rect:
        source_width, source_height = (225, 400)
        if surface is not None:
            surface_width, surface_height = surface.get_size()
            if surface_width > 0 and surface_height > 0:
                source_width, source_height = surface_width, surface_height

        max_width = min(source_width, max(150, self.character_panel_rect.width // 2 - 12))
        max_height = min(
            source_height,
            max(120, self.character_panel_rect.height - (y - self.character_panel_rect.top) - reserved_bottom),
        )
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
            kind = "Companion" if getattr(familiar, "spec", "") == "Tamed" else "Familiar"
            return kind, familiar

        summons = getattr(player_char, "summons", {}) or {}
        for summon in summons.values():
            if self._is_living_companion(summon):
                return "Summon", summon
        return None

    def companion_summary_rows(self, kind: str, companion: Any) -> list[tuple[str, str]]:
        """Return compact Character Menu rows for the selected companion."""
        name = str(getattr(companion, "name", "") or kind)
        identity = (
            getattr(companion, "species", None)
            or getattr(companion, "race", None)
            or getattr(companion, "spec", None)
            or getattr(companion, "cls", None)
            or kind
        )
        if not isinstance(identity, str):
            identity = self._attr_name(identity, kind)
        if identity == name:
            identity = kind
        rows = [("Companion", name), ("Type", str(identity))]
        if getattr(companion, "spec", "") == "Tamed":
            evolution = str(getattr(companion, "evolution", "") or "")
            special = str(getattr(companion, "special_ability", "") or "")
            if evolution:
                rows.append(("Form", evolution))
            if special:
                rows.append(("Special", special))
        if getattr(companion, "spec", "") != "Tamed":
            level = getattr(companion, "level", None)
            for attr in ("level", "pro_level"):
                value = getattr(level, attr, None)
                if value is not None:
                    rows.append(("Level", str(value)))
                    break
        return rows

    def companion_detail_rows(self, kind: str, companion: Any) -> list[tuple[str, str]]:
        """Return stat rows for a familiar, companion, or summon."""
        rows = self.companion_summary_rows(kind, companion)
        health = getattr(companion, "health", None)
        mana = getattr(companion, "mana", None)
        combat = getattr(companion, "combat", None)
        if getattr(companion, "spec", "") != "Tamed":
            rows.extend(
                [
                    ("HP", f"{getattr(health, 'current', 0)}/{getattr(health, 'max', 0)}"),
                    ("MP", f"{getattr(mana, 'current', 0)}/{getattr(mana, 'max', 0)}"),
                    ("Attack", _whole_stat_text(getattr(combat, "attack", 0))),
                    ("Defense", _whole_stat_text(getattr(combat, "defense", 0))),
                    ("Magic", _whole_stat_text(getattr(combat, "magic", 0))),
                    ("Magic Defense", _whole_stat_text(getattr(combat, "magic_def", 0))),
                ]
            )
        return rows

    def class_summary_rows(self, player_char) -> list[tuple[str, str]]:
        """Return class-specific summary rows for the Class tab."""
        if grandmaster.is_weapon_discipline_class(player_char):
            return []
        summons = getattr(player_char, "summons", {}) or {}
        familiar = getattr(player_char, "familiar", None)
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        rows = []
        if class_name in {"Ranger", "Beast Master"}:
            try:
                favored = ability_mechanics.favored_enemy_label(player_char)
            except Exception:
                favored = "None"
            rows.append(("Favored Enemy", favored))
            tamed_state = ability_mechanics.normalize_tamed_companion(getattr(player_char, "tamed_companion", None))
            roster = tamed_state.get("companions", [])
            if isinstance(roster, list):
                rows.append(("Held", f"{len(roster)}/{ability_mechanics.TAMED_COMPANION_ROSTER_LIMIT}"))
        if summons:
            rows.append(("Known Summons", str(len(summons))))
        if familiar is not None:
            if getattr(familiar, "spec", "") == "Tamed":
                rows.append(("Companion", self._attr_name(familiar, "Companion")))
                tamed = getattr(player_char, "tamed_companion", {}) or {}
                bond = getattr(familiar, "bond", 0)
                evolution = str(getattr(familiar, "evolution", "") or "")
                special = str(getattr(familiar, "special_ability", "") or "")
                if isinstance(tamed, dict):
                    bond = tamed.get("bond", bond)
                    evolution = str(tamed.get("evolution") or evolution)
                    special = str(tamed.get("special_ability") or special)
                rows.append(("Bond", f"{self._non_negative_int(bond)}/100"))
                if evolution:
                    rows.append(("Form", evolution))
                if special:
                    rows.append(("Special", special))
                roster = tamed.get("companions", []) if isinstance(tamed, dict) else []
                if class_name not in {"Ranger", "Beast Master"} and isinstance(roster, list) and roster:
                    rows.append(("Held", f"{len(roster)}/{ability_mechanics.TAMED_COMPANION_ROSTER_LIMIT}"))
            else:
                rows.append(("Familiar", self._attr_name(familiar, "Familiar")))
        return rows

    def favored_enemy_progress_rows(self, player_char) -> list[tuple[str, int, int, str]]:
        """Return the marked enemy-type practice row for Ranger/Beast Master."""
        try:
            state = ability_mechanics.favored_enemy_state(player_char)
        except Exception:
            state = {"type": None, "practice": 0, "switches": 0}
        marked = state.get("type")
        practice = self._non_negative_int(state.get("practice", 0))
        if not marked:
            return [("No marked quarry", 0, 100, "Use Favored Enemy in combat")]
        return [
            (
                str(marked),
                min(100, practice),
                100,
                f"{ability_mechanics.favored_enemy_rank(practice)} - {practice} practice",
            )
        ]

    def _draw_favored_enemy_progress_panel(self, player_char, rect: pygame.Rect, y: int) -> int:
        """Draw Ranger/Beast Master enemy-type tracking mastery progress."""
        self._draw_text("Tracking Mastery", self.normal_font, self.colors.GOLD, rect.left, y, rect.width)
        y += self.normal_font.get_height() + 10
        for label, value, cap, detail in self.favored_enemy_progress_rows(player_char):
            if y + 54 > rect.bottom:
                break
            y = self._draw_progress_row(rect, label, value, cap, y, detail=detail, color=self.colors.GREEN)
        try:
            switches = ability_mechanics.favored_enemy_state(player_char).get("switches", 0)
        except Exception:
            switches = 0
        if y + self.small_font.get_height() <= rect.bottom:
            self._draw_text(
                f"Quarry changes: {self._non_negative_int(switches)}",
                self.small_font,
                self.colors.GRAY,
                rect.left,
                y,
                rect.width,
            )
            y += self.small_font.get_height() + 10
        return y

    def _weapon_discipline_progress_label(self, xp: float, rank: int) -> str:
        if rank >= grandmaster.MAX_RANK:
            return "MAX"
        next_threshold = grandmaster.XP_THRESHOLDS[rank]
        return f"{grandmaster.format_xp_value(xp)}/{next_threshold} XP"

    def _weapon_discipline_progress_fraction(self, xp: int, rank: int) -> float:
        if rank >= grandmaster.MAX_RANK:
            return 1.0
        previous_threshold = grandmaster.XP_THRESHOLDS[rank - 1] if rank > 0 else 0
        next_threshold = grandmaster.XP_THRESHOLDS[rank]
        span = max(1, next_threshold - previous_threshold)
        return max(0.0, min(1.0, (xp - previous_threshold) / span))

    def weapon_discipline_rows(self, player_char) -> list[tuple[str, str]]:
        """Return per-weapon Weapon Discipline progression rows."""
        state = grandmaster.normalize_state(getattr(player_char, "grandmaster_discipline", None))
        rows: list[tuple[str, str]] = []
        for weapon_type in grandmaster.WEAPON_TYPES:
            entry = state["disciplines"][weapon_type]
            xp = self._non_negative_float(entry.get("xp", 0))
            rank = self._non_negative_int(entry.get("rank", 0))
            progress = self._weapon_discipline_progress_label(xp, rank)
            rows.append((weapon_type, f"Rank {rank} - {progress}"))
        return rows

    def weapon_discipline_detail_text(self, player_char, weapon_type: str) -> str:
        """Return readable progression details for one Weapon Discipline row."""
        state = grandmaster.normalize_state(getattr(player_char, "grandmaster_discipline", None))
        entry = state["disciplines"].get(weapon_type, {"xp": 0, "rank": 0})
        xp = self._non_negative_float(entry.get("xp", 0))
        rank = self._non_negative_int(entry.get("rank", 0))
        progress = self._weapon_discipline_progress_label(xp, rank)
        art_name = grandmaster.WEAPON_ARTS.get(weapon_type, "Weapon Art")
        equipped = weapon_type in {
            grandmaster.get_weapon_type(player_char, "Weapon"),
            grandmaster.get_weapon_type(player_char, "OffHand"),
        }
        unlocked = rank >= 1
        improved = rank >= 5
        mastered = rank >= grandmaster.MAX_RANK
        lines = [
            f"{weapon_type} Discipline",
            f"Rank {rank} - {progress}",
            f"Equipped now: {'Yes' if equipped else 'No'}",
            "",
            f"Weapon Art: {art_name}",
            f"Required weapon: {weapon_type}",
            "",
            "Unlocks:",
            f"Rank 1: {'Unlocked' if unlocked else 'Locked'} - learn {art_name}.",
            f"Rank 5: {'Unlocked' if improved else 'Locked'} - improved art effect.",
            f"Rank {grandmaster.MAX_RANK}: {'Unlocked' if mastered else 'Locked'} - mastered art effect.",
        ]
        if rank < grandmaster.MAX_RANK:
            next_threshold = grandmaster.XP_THRESHOLDS[rank]
            remaining = max(0, next_threshold - int(xp))
            lines.append(f"Next rank: {remaining} XP remaining.")
        return "\n".join(lines)

    def _weapon_discipline_icon_item(self, weapon_type: str):
        if not hasattr(self, "_weapon_discipline_icon_cache"):
            self._weapon_discipline_icon_cache = {}
        cache = self._weapon_discipline_icon_cache
        if weapon_type not in cache:
            factory = WEAPON_DISCIPLINE_ICON_FACTORIES.get(weapon_type, items.NoWeapon)
            try:
                cache[weapon_type] = factory()
            except Exception:
                cache[weapon_type] = items.NoWeapon()
        return cache[weapon_type]

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
    def _non_negative_float(value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, float(value or default))
        except (TypeError, ValueError):
            return max(0.0, float(default))

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
        font = self.small_font
        line_gap = 4
        for label, value in rows:
            if y + font.get_height() > rect.bottom:
                break
            label_width = min(max(62, font.size(label)[0] + 8), max(62, rect.width // 2))
            value_width = max(1, rect.width - label_width - 12)
            self._draw_text(label, font, self.colors.GRAY, rect.left + 4, y, label_width)
            if font.size(str(value))[0] <= value_width:
                value_text = str(value)
                value_x = rect.right - 4 - font.size(value_text)[0]
                self._draw_text(value_text, font, self.colors.WHITE, value_x, y, value_width)
                y += font.get_height() + line_gap
            else:
                y += font.get_height()
                full_width = max(1, rect.width - 8)
                value_text = str(value)
                self._draw_text(value_text, font, self.colors.WHITE, rect.left + 4, y, full_width)
                y += font.get_height() + line_gap
            if y > rect.bottom:
                break
        return y

    def _portrait_details_min_height(self, rows: list[tuple[str, str]], width: int) -> int:
        """Return the height needed for compact portrait metadata rows."""
        font = self.small_font
        line_gap = 4
        height = 0
        for label, value in rows:
            label_width = min(max(62, font.size(label)[0] + 8), max(62, width // 2))
            value_width = max(1, width - label_width - 12)
            row_lines = 1 if font.size(str(value))[0] <= value_width else 2
            height += (font.get_height() * row_lines) + line_gap
        return height

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
        if str(getattr(weapon, "subtyp", "") or "") == "Staff" and ability_mechanics.has_skill(player_char, "Staff Conduit"):
            return True
        equipment = getattr(player_char, "equipment", {}) or {}
        offhand = equipment.get("OffHand")
        if ability_mechanics.can_keep_staff_shield(player_char, weapon, offhand):
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

    def draw_tabs(self, player_char=None):
        self._draw_panel(self.tab_rect)
        visible_tabs = self.visible_tabs(player_char)
        for index, tab in enumerate(visible_tabs):
            rect = self.tab_button_rects(player_char)[index]
            active = tab.key == self.active_tab_key
            if active:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, rect, 2)
            self._draw_text(tab.label, self.normal_font, self.colors.GOLD if active else self.colors.WHITE, rect.left + 12, rect.centery - self.normal_font.get_height() // 2, rect.width - 24)

    def tab_button_rects(self, player_char=None) -> list[pygame.Rect]:
        """Return clickable rectangles for character tabs."""
        visible_tabs = self.visible_tabs(player_char)
        x = self.tab_rect.left + 12
        tab_width = max(120, min(220, (self.tab_rect.width - 24) // max(1, len(visible_tabs))))
        return [
            pygame.Rect(x + (index * tab_width), self.tab_rect.top + 8, tab_width - 8, self.tab_rect.height - 16)
            for index, _tab in enumerate(visible_tabs)
        ]

    def draw_character_panel(self, player_char):
        y = self._draw_panel(self.character_panel_rect, "Character")
        portrait_surface = self.load_portrait(player_char)
        portrait_rows = self.build_portrait_details(player_char)
        initial_portrait = self.portrait_frame_rect(y, portrait_surface)
        detail_gap = 8
        detail_bottom_padding = 8
        detail_height = self._portrait_details_min_height(portrait_rows, initial_portrait.width)
        portrait = self.portrait_frame_rect(
            y,
            portrait_surface,
            reserved_bottom=detail_gap + detail_height + detail_bottom_padding,
        )
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, portrait)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, portrait, 2)
        if portrait_surface is not None:
            self._draw_fitted_surface(portrait_surface, portrait)
            pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, portrait, 2)
        else:
            self._draw_text("Portrait", self.small_font, self.colors.GRAY, portrait.left + 10, portrait.centery - self.small_font.get_height() // 2, portrait.width - 20)

        detail_y = portrait.bottom + detail_gap
        detail_rect = pygame.Rect(portrait.left, detail_y, portrait.width, self.character_panel_rect.bottom - detail_y - detail_bottom_padding)
        self._draw_portrait_details(portrait_rows, detail_rect, detail_y)

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
        resistance_font = self.small_font
        resistance_row_gap = 3
        resistance_row_height = resistance_font.get_height() + resistance_row_gap
        resistance_height = self.large_font.get_height() + 6 + (RESISTANCE_SLOT_COUNT * resistance_row_height)
        resistance_top = self.combat_panel_rect.bottom - resistance_height - 16
        available_stat_height = resistance_top - y - 12
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
            bottom_limit=resistance_top - 12,
        )

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

    def class_companion_entries(self, player_char) -> list[tuple[str, Any]]:
        """Return all companions worth showing on the Class tab."""
        entries: list[tuple[str, Any]] = []
        familiar = getattr(player_char, "familiar", None)
        tamed_state = ability_mechanics.normalize_tamed_companion(getattr(player_char, "tamed_companion", None))
        tamed_roster = tamed_state.get("companions", [])
        if isinstance(tamed_roster, list) and tamed_roster:
            try:
                from src.core import companions

                for index, entry in enumerate(tamed_roster):
                    display_entry = dict(entry)
                    display_entry["active"] = True
                    companion = companions.tamed_companion_from_state(display_entry)
                    if companion is None:
                        continue
                    kind = "Companion" if index == tamed_state.get("active_index") else "Held Companion"
                    entries.append((kind, companion))
            except Exception:
                if familiar is not None:
                    entries.append(("Companion", familiar))
        elif familiar is not None:
            kind = "Companion" if getattr(familiar, "spec", "") == "Tamed" else "Familiar"
            entries.append((kind, familiar))

        summons = getattr(player_char, "summons", {}) or {}
        for summon in summons.values():
            entries.append(("Summon", summon))
        return entries

    def _companion_xp_label(self, companion: Any) -> str:
        level = getattr(companion, "level", None)
        if getattr(level, "level", 1) >= 10:
            return "MAX"
        exp = self._non_negative_int(getattr(level, "exp", 0))
        to_next = self._non_negative_int(getattr(level, "exp_to_gain", 0))
        total = exp + to_next
        if total <= 0:
            return "0/0 XP"
        return f"{exp}/{total} XP"

    def _summon_bond_label(self, player_char, companion: Any) -> str | None:
        name = self._attr_name(companion, "")
        if getattr(companion, "spec", "") == "Tamed":
            return f"{self._non_negative_int(getattr(companion, 'bond', 0))}/100"
        state = getattr(player_char, "promotion_kit_state", {}) or {}
        bonds = state.get("summon_bonds", {}) if isinstance(state, dict) else {}
        if name not in bonds:
            return None
        return f"{self._non_negative_int(bonds.get(name))}/100"

    def _draw_class_companion_card(self, kind: str, companion: Any, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, (14, 14, 19), rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, rect, 1)
        art_size = max(72, min(116, rect.height - 22, rect.width // 5))
        art_rect = pygame.Rect(rect.left + 12, rect.top + (rect.height - art_size) // 2, art_size, art_size)
        self._draw_item_art_backdrop(art_rect)
        sprite = self.companion_art_manager.get_scaled_sprite(companion, art_rect.size)
        self.screen.blit(sprite, art_rect)

        text_x = art_rect.right + 14
        text_width = rect.right - text_x - 12
        y = rect.top + 12
        name = self._attr_name(companion, kind)
        self._draw_text(name, self.normal_font, self.colors.GOLD, text_x, y, text_width)
        y += self.normal_font.get_height() + 4

        row_rect = pygame.Rect(text_x, y, text_width, rect.bottom - y - 10)
        detail_rows = self.companion_detail_rows(kind, companion)
        self._draw_key_values(
            detail_rows,
            row_rect,
            y,
            font=self.small_font,
            label_padding=18,
            row_gap=1,
            bottom_limit=rect.bottom - 10,
        )

    def class_companion_tile_rects(self, entries: list[tuple[str, Any]]) -> list[pygame.Rect]:
        """Return stacked clickable companion row rectangles for the Class tab."""
        if not entries or not hasattr(self, "_class_roster_rect"):
            return []

        roster_rect = self._class_roster_rect
        gap = 6
        tile_width = roster_rect.width
        top = roster_rect.top + self.normal_font.get_height() + 10
        available_height = max(1, roster_rect.bottom - top)
        tile_height = min(64, max(30, (available_height - gap * (len(entries) - 1)) // len(entries)))
        rects = []
        for index, _entry in enumerate(entries):
            rects.append(
                pygame.Rect(
                    roster_rect.left,
                    top + index * (tile_height + gap),
                    tile_width,
                    tile_height,
                )
            )
        return rects

    def weapon_discipline_row_rects(self) -> list[pygame.Rect]:
        """Return clickable Weapon Discipline row rectangles for the Class tab."""
        return list(getattr(self, "_weapon_discipline_row_rects", []))

    def _draw_inline_companion_fields(
        self,
        fields: list[tuple[str, str]],
        rect: pygame.Rect,
        y: int,
        *,
        selected: bool,
    ) -> None:
        x = rect.left + 12
        max_x = rect.right - 10
        label_color = self.colors.GOLD if selected else self.colors.GRAY
        for label, value in fields:
            label_text = str(label)
            label_width = self.small_font.size(label_text)[0]
            value_width = self.small_font.size(str(value))[0]
            if x + label_width + 4 + value_width > max_x:
                break
            self._draw_text(label_text, self.small_font, label_color, x, y, label_width)
            x += label_width + 4
            self._draw_text(str(value), self.small_font, self.colors.WHITE, x, y, max_x - x)
            x += value_width + 14

    def _draw_class_companion_tile(
        self,
        kind: str,
        companion: Any,
        rect: pygame.Rect,
        *,
        selected: bool,
        player_char,
    ) -> None:
        pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG if selected else (14, 14, 19), rect)
        pygame.draw.rect(self.screen, self.colors.GOLD if selected else self.colors.BORDER_COLOR, rect, 2 if selected else 1)

        text_x = rect.left + 12
        text_width = rect.right - text_x - 8
        y = rect.top + 8
        name = self._attr_name(companion, kind)
        name_width = max(90, min(text_width // 2, self.normal_font.size(name)[0] + 8))
        self._draw_text(name, self.normal_font, self.colors.GOLD, text_x, y, name_width)

        fields = [("Type", kind)]
        if getattr(companion, "spec", "") != "Tamed":
            level = getattr(getattr(companion, "level", None), "level", "?")
            fields.append(("Level", str(level)))
        if getattr(companion, "spec", "") == "Tamed":
            evolution = str(getattr(companion, "evolution", "") or "")
            special = str(getattr(companion, "special_ability", "") or "")
            if evolution:
                fields.append(("Form", evolution))
            if special:
                fields.append(("Special", special))
        if getattr(companion, "spec", "") != "Tamed":
            health = getattr(companion, "health", None)
            fields.append(("HP", f"{getattr(health, 'current', 0)}/{getattr(health, 'max', 0)}"))
            fields.append(("XP", self._companion_xp_label(companion)))
        bond = self._summon_bond_label(player_char, companion)
        if bond is not None:
            fields.append(("Bond", bond))

        first_line_fields = fields[:2]
        second_line_fields = fields[2:]
        field_x = text_x + name_width + 8
        self._draw_inline_companion_fields(
            first_line_fields,
            pygame.Rect(field_x, y + 2, rect.right - field_x - 8, self.small_font.get_height()),
            y + 2,
            selected=selected,
        )
        detail_y = min(rect.bottom - self.small_font.get_height() - 4, y + self.normal_font.get_height() + 1)
        self._draw_inline_companion_fields(
            second_line_fields,
            pygame.Rect(text_x, detail_y, text_width, self.small_font.get_height()),
            detail_y,
            selected=selected,
        )

    def _draw_empty_companion_slots(self, rect: pygame.Rect, y: int) -> None:
        """Draw Ranger/Beast Master stable placeholders before any tame exists."""
        self._draw_text("Companion Stable", self.normal_font, self.colors.GOLD, rect.left, y, rect.width)
        prompt = "Tame a wounded Animal to fill a slot."
        prompt_width = self.small_font.size(prompt)[0]
        self._draw_text(
            prompt,
            self.small_font,
            self.colors.GRAY,
            rect.right - min(prompt_width, rect.width),
            self.details_rect.top + 18,
            rect.width,
        )

        slot_count = ability_mechanics.TAMED_COMPANION_ROSTER_LIMIT
        columns = 2
        gap = 8
        top = y + self.normal_font.get_height() + 14
        available_height = max(1, rect.bottom - top)
        rows = max(1, (slot_count + columns - 1) // columns)
        slot_width = max(1, (rect.width - gap * (columns - 1)) // columns)
        slot_height = min(58, max(36, (available_height - gap * (rows - 1)) // rows))
        for index in range(slot_count):
            col = index % columns
            row = index // columns
            slot_rect = pygame.Rect(
                rect.left + col * (slot_width + gap),
                top + row * (slot_height + gap),
                slot_width,
                slot_height,
            )
            if slot_rect.bottom > rect.bottom:
                break
            pygame.draw.rect(self.screen, (14, 14, 19), slot_rect)
            pygame.draw.rect(self.screen, self.colors.DARK_GRAY, slot_rect, 1)
            self._draw_text(
                f"Empty Slot {index + 1}",
                self.normal_font,
                self.colors.GRAY,
                slot_rect.left + 10,
                slot_rect.top + 8,
                slot_rect.width - 20,
            )
            self._draw_text(
                "Available",
                self.small_font,
                self.colors.GRAY,
                slot_rect.left + 10,
                slot_rect.top + 8 + self.normal_font.get_height(),
                slot_rect.width - 20,
            )

    def _open_class_companion_popup(self, player_char) -> None:
        entries = self.class_companion_entries(player_char)
        if not entries:
            return
        self.selected_class_companion_index = max(
            0,
            min(self.selected_class_companion_index, len(entries) - 1),
        )
        kind, companion = entries[self.selected_class_companion_index]
        background = self.screen.copy()
        popup = ClassCompanionDetailsPopup(self.presenter, self, player_char, kind, companion)
        popup.show(
            background_draw_func=lambda: self.screen.blit(background, (0, 0)),
            flush_events=True,
            require_key_release=True,
        )

    def _selected_tamed_roster_index(self, player_char) -> int | None:
        entries = self.class_companion_entries(player_char)
        if not entries:
            return None
        selected_index = max(0, min(self.selected_class_companion_index, len(entries) - 1))
        kind, companion = entries[selected_index]
        if kind not in {"Companion", "Held Companion"} or getattr(companion, "spec", "") != "Tamed":
            return None
        roster_index = 0
        for entry_kind, entry_companion in entries[: selected_index + 1]:
            if entry_kind in {"Companion", "Held Companion"} and getattr(entry_companion, "spec", "") == "Tamed":
                if entry_companion is companion:
                    return roster_index
                roster_index += 1
        return None

    def _activate_selected_tamed_companion(self, player_char) -> None:
        roster_index = self._selected_tamed_roster_index(player_char)
        if roster_index is None:
            return
        ability_mechanics.activate_tamed_companion(player_char, roster_index)
        self.selected_class_companion_index = roster_index

    def _release_selected_tamed_companion(self, player_char) -> None:
        roster_index = self._selected_tamed_roster_index(player_char)
        if roster_index is None:
            return
        entries = self.class_companion_entries(player_char)
        companion_name = "this companion"
        tamed_index = -1
        for kind, companion in entries:
            if kind in {"Companion", "Held Companion"} and getattr(companion, "spec", "") == "Tamed":
                tamed_index += 1
                if tamed_index == roster_index:
                    companion_name = getattr(companion, "name", companion_name)
                    break
        background = self.screen.copy()
        popup = ConfirmationPopup(
            self.presenter,
            f"Release {companion_name}?",
            show_buttons=True,
        )
        if not popup.show(
            background_draw_func=lambda: self.screen.blit(background, (0, 0)),
            flush_events=True,
            require_key_release=True,
        ):
            return
        ability_mechanics.release_tamed_companion(player_char, roster_index)
        entries = self.class_companion_entries(player_char)
        self.selected_class_companion_index = max(
            0,
            min(self.selected_class_companion_index, max(0, len(entries) - 1)),
        )
        self.class_companion_selector_active = bool(entries)

    def _open_weapon_discipline_popup(self, player_char) -> None:
        if not grandmaster.is_weapon_discipline_class(player_char):
            return
        self.selected_weapon_discipline_index = max(
            0,
            min(self.selected_weapon_discipline_index, len(grandmaster.WEAPON_TYPES) - 1),
        )
        weapon_type = grandmaster.WEAPON_TYPES[self.selected_weapon_discipline_index]
        background = self.screen.copy()
        popup = ConfirmationPopup(
            self.presenter,
            self.weapon_discipline_detail_text(player_char, weapon_type),
            show_buttons=False,
        )
        popup.show(
            background_draw_func=lambda: self.screen.blit(background, (0, 0)),
            flush_events=True,
            require_key_release=True,
        )

    def _draw_weapon_discipline_progress_bar(
        self,
        rect: pygame.Rect,
        *,
        xp: int,
        rank: int,
        equipped: bool,
    ) -> None:
        fill_width = int(rect.width * self._weapon_discipline_progress_fraction(xp, rank))
        pygame.draw.rect(self.screen, (24, 24, 28), rect)
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.left, rect.top, fill_width, rect.height)
            pygame.draw.rect(self.screen, self.colors.GOLD if equipped else self.colors.GREEN, fill_rect)
        pygame.draw.rect(self.screen, self.colors.GOLD if equipped else self.colors.BORDER_COLOR, rect, 1)

    def _draw_weapon_discipline_row(
        self,
        weapon_type: str,
        entry: dict[str, Any],
        rect: pygame.Rect,
        *,
        equipped: bool,
        selected: bool,
    ) -> None:
        highlighted = equipped or selected
        border_color = self.colors.GOLD if highlighted else self.colors.BORDER_COLOR
        pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG if highlighted else (14, 14, 19), rect)
        pygame.draw.rect(self.screen, border_color, rect, 2 if highlighted else 1)

        icon_size = min(40, max(28, rect.height - 12))
        icon_rect = pygame.Rect(rect.left + 8, rect.top + (rect.height - icon_size) // 2, icon_size, icon_size)
        self._draw_item_art_backdrop(icon_rect)
        icon_item = self._weapon_discipline_icon_item(weapon_type)
        render = self.item_render_manager.get_scaled_render(icon_item, icon_rect.size)
        self.screen.blit(render, icon_rect)

        xp = self._non_negative_float(entry.get("xp", 0))
        rank = self._non_negative_int(entry.get("rank", 0))
        name_color = self.colors.GOLD if equipped else self.colors.WHITE
        detail_color = self.colors.WHITE if highlighted else self.colors.GRAY
        text_x = icon_rect.right + 10
        name_width = min(150, max(104, rect.width // 3))
        name_y = rect.centery - self.normal_font.get_height() // 2
        self._draw_text(weapon_type, self.normal_font, name_color, text_x, name_y, name_width)
        if equipped:
            equipped_y = min(rect.bottom - self.small_font.get_height() - 4, name_y + self.normal_font.get_height() - 1)
            self._draw_text("Equipped", self.small_font, detail_color, text_x, equipped_y, name_width)

        bar_x = text_x + name_width + 12
        bar_width = max(80, rect.right - bar_x - 12)
        rank_text = f"Rank {rank}"
        xp_text = self._weapon_discipline_progress_label(xp, rank)
        self._draw_text(rank_text, self.small_font, self.colors.WHITE, bar_x, rect.top + 7, bar_width)
        xp_width = self.small_font.size(xp_text)[0]
        self._draw_text(
            xp_text,
            self.small_font,
            detail_color,
            rect.right - 12 - min(xp_width, bar_width),
            rect.top + 7,
            bar_width,
        )
        bar_rect = pygame.Rect(bar_x, rect.top + 30, bar_width, 10)
        self._draw_weapon_discipline_progress_bar(bar_rect, xp=xp, rank=rank, equipped=equipped)

    def _draw_weapon_discipline_panel(self, player_char, rect: pygame.Rect, y: int, *, show_heading: bool = True) -> None:
        if show_heading:
            self._draw_text("Weapon Discipline", self.normal_font, self.colors.GOLD, rect.left, y, rect.width)
            y += self.normal_font.get_height() + 10
        self.selected_weapon_discipline_index = max(
            0,
            min(self.selected_weapon_discipline_index, len(grandmaster.WEAPON_TYPES) - 1),
        )
        helper = "Arrows: Select  Enter: Details"
        helper_width = self.small_font.size(helper)[0]
        self._draw_text(
            helper,
            self.small_font,
            self.colors.GRAY,
            rect.right - min(helper_width, rect.width),
            y,
            rect.width,
        )
        y += self.small_font.get_height() + 6
        state = grandmaster.normalize_state(getattr(player_char, "grandmaster_discipline", None))
        equipped = {
            weapon_type
            for weapon_type in (
                grandmaster.get_weapon_type(player_char, "Weapon"),
                grandmaster.get_weapon_type(player_char, "OffHand"),
            )
            if weapon_type is not None
        }
        row_gap = 6
        available_height = max(1, rect.bottom - y - 4)
        row_height = min(54, max(42, (available_height - row_gap * (len(grandmaster.WEAPON_TYPES) - 1)) // len(grandmaster.WEAPON_TYPES)))
        self._weapon_discipline_row_rects = []
        for index, weapon_type in enumerate(grandmaster.WEAPON_TYPES):
            row_rect = pygame.Rect(rect.left, y + index * (row_height + row_gap), rect.width, row_height)
            if row_rect.bottom > rect.bottom:
                break
            self._weapon_discipline_row_rects.append(row_rect)
            self._draw_weapon_discipline_row(
                weapon_type,
                state["disciplines"][weapon_type],
                row_rect,
                equipped=weapon_type in equipped,
                selected=index == self.selected_weapon_discipline_index,
            )

    def _draw_meter_bar(self, rect: pygame.Rect, value: int, cap: int, *, color=None) -> None:
        cap = max(1, int(cap or 1))
        value = max(0, min(cap, int(value or 0)))
        fill_width = int(rect.width * (value / cap))
        pygame.draw.rect(self.screen, (24, 24, 28), rect)
        if fill_width > 0:
            pygame.draw.rect(self.screen, color or self.colors.GREEN, pygame.Rect(rect.left, rect.top, fill_width, rect.height))
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, rect, 1)

    def _draw_mechanic_note_card(self, rect: pygame.Rect, title: str, body: str, y: int) -> int:
        card = pygame.Rect(rect.left, y, rect.width, max(74, self.small_font.get_height() * 3 + 28))
        pygame.draw.rect(self.screen, (14, 14, 19), card)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, card, 1)
        self._draw_text(title, self.normal_font, self.colors.GOLD, card.left + 12, card.top + 10, card.width - 24)
        return self._draw_wrapped_text(
            body,
            self.small_font,
            self.colors.WHITE,
            card.left + 12,
            card.top + self.normal_font.get_height() + 14,
            card.width - 24,
            max_lines=3,
        ) + 10

    def jump_mod_summary_rows(self, player_char) -> list[tuple[str, str]]:
        jump_skill = self._get_jump_skill(player_char)
        if not jump_skill or not hasattr(jump_skill, "modifications"):
            return [("Jump Mods", "Jump not learned")]
        active_count = jump_skill.get_active_count() if hasattr(jump_skill, "get_active_count") else sum(bool(v) for v in jump_skill.modifications.values())
        max_count = jump_skill.get_max_active_modifications(player_char) if hasattr(jump_skill, "get_max_active_modifications") else len(jump_skill.modifications)
        unlocked = jump_skill.get_unlocked_modifications() if hasattr(jump_skill, "get_unlocked_modifications") else list(jump_skill.modifications.keys())
        active = [name for name in unlocked if jump_skill.modifications.get(name)]
        return [
            ("Active Mods", f"{active_count}/{max_count}"),
            ("Unlocked", str(len(unlocked))),
            ("Equipped", ", ".join(active) if active else "None"),
        ]

    def jump_mod_entries(self, player_char) -> list[str]:
        jump_skill = self._get_jump_skill(player_char)
        if not jump_skill or not hasattr(jump_skill, "modifications"):
            return []
        if hasattr(jump_skill, "get_unlocked_modifications"):
            return list(jump_skill.get_unlocked_modifications())
        return list(jump_skill.modifications.keys())

    def jump_mod_row_rects(self) -> list[pygame.Rect]:
        return list(self._jump_mod_row_rects)

    def _jump_mod_counts(self, player_char) -> tuple[int, int]:
        jump_skill = self._get_jump_skill(player_char)
        if not jump_skill or not hasattr(jump_skill, "modifications"):
            return 0, 0
        active_count = jump_skill.get_active_count() if hasattr(jump_skill, "get_active_count") else sum(bool(v) for v in jump_skill.modifications.values())
        max_count = jump_skill.get_max_active_modifications(player_char) if hasattr(jump_skill, "get_max_active_modifications") else len(jump_skill.modifications)
        return int(active_count), int(max_count)

    def _toggle_selected_jump_mod(self, player_char) -> None:
        entries = self.jump_mod_entries(player_char)
        if not entries:
            return
        self.selected_jump_mod_index = max(0, min(self.selected_jump_mod_index, len(entries) - 1))
        jump_skill = self._get_jump_skill(player_char)
        if not jump_skill or not hasattr(jump_skill, "modifications"):
            return
        mod_name = entries[self.selected_jump_mod_index]
        current = bool(jump_skill.modifications.get(mod_name, False))
        if hasattr(jump_skill, "set_modification"):
            jump_skill.set_modification(mod_name, not current, player_char)
        else:
            jump_skill.modifications[mod_name] = not current

    def _jump_mod_unlock_text(self, jump_skill, mod_name: str) -> str:
        requirements = getattr(jump_skill, "unlock_requirements", {}) or {}
        req = requirements.get(mod_name, {}) if isinstance(requirements, dict) else {}
        req_type = req.get("type", "")
        req_val = req.get("requirement")
        if req_type == "lancer_level":
            return f"Unlocked: Lancer Level {req_val}"
        if req_type == "dragoon_level":
            return f"Unlocked: Dragoon Level {req_val}"
        if req_type == "boss":
            return f"Unlocked by defeating {req_val}"
        if req_type == "item":
            return f"Unlocked by finding {req_val}"
        return "Initial modification"

    def _jump_mod_description(self, mod_name: str) -> str:
        descriptions = {
            "Crit": "Increases critical factor but reduces damage to 1.5x weapon damage.",
            "Thrust": "After landing, thrust for 3/4 weapon damage if the target survives.",
            "Defend": "Increased damage reduction while preparing to Jump.",
            "Rend": "Chance to apply Bleed, dealing damage over time.",
            "Quake": "Chance to stun the enemy upon landing.",
            "Acrobat": "Gain an evasion bonus while preparing to Jump.",
            "Dragon's Fury": "Deals additional random elemental damage.",
            "Soaring Strike": "Takes two turns to charge, but deals increased damage.",
            "Quick Dive": "Removes charge time but reduces damage to 0.75x.",
            "Retribution": "Taking damage while charging boosts the Jump damage.",
            "Unstoppable": "Jump cannot be interrupted once started.",
            "Recover": "Regain a small amount of health and mana upon landing.",
            "Skyfall": "Additional smaller hits fall on the target after landing.",
        }
        return descriptions.get(mod_name, "")

    def _draw_aerial_tempo_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        content = self.details_rect.inflate(-32, -64)
        content.top = y
        left_width = max(300, (content.width * 9) // 20)
        list_rect = pygame.Rect(content.left, content.top, left_width, content.height)
        detail_rect = pygame.Rect(list_rect.right + 18, content.top, content.right - list_rect.right - 18, content.height)

        jump_skill = self._get_jump_skill(player_char)
        entries = self.jump_mod_entries(player_char)
        self.selected_jump_mod_index = max(0, min(self.selected_jump_mod_index, max(0, len(entries) - 1)))
        active_count, max_count = self._jump_mod_counts(player_char)

        header = f"Jump Modifications ({active_count}/{max_count} active)" if jump_skill else "Jump not learned"
        self._draw_text(header, self.normal_font, self.colors.GOLD, list_rect.left, list_rect.top, list_rect.width)
        helper = "UP/DOWN: Select  ENTER: Toggle"
        helper_width = self.small_font.size(helper)[0]
        self._draw_text(helper, self.small_font, self.colors.GRAY, list_rect.right - min(helper_width, list_rect.width), list_rect.top + self.normal_font.get_height() + 2, list_rect.width)

        y_cursor = list_rect.top + self.normal_font.get_height() + self.small_font.get_height() + 14
        row_height = 42
        row_gap = 6
        self._jump_mod_row_rects = []
        for index, mod_name in enumerate(entries):
            row_rect = pygame.Rect(list_rect.left, y_cursor + index * (row_height + row_gap), list_rect.width, row_height)
            if row_rect.bottom > list_rect.bottom:
                break
            self._jump_mod_row_rects.append(row_rect)
            selected = index == self.selected_jump_mod_index
            active = bool(getattr(jump_skill, "modifications", {}).get(mod_name, False))
            pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG if selected else (14, 14, 19), row_rect)
            pygame.draw.rect(self.screen, self.colors.GOLD if selected else self.colors.BORDER_COLOR, row_rect, 2 if selected else 1)
            marker = "[X]" if active else "[ ]"
            self._draw_text(marker, self.normal_font, self.colors.GOLD if active else self.colors.GRAY, row_rect.left + 12, row_rect.top + 10, 40)
            self._draw_text(mod_name, self.normal_font, self.colors.WHITE, row_rect.left + 58, row_rect.top + 10, row_rect.width - 70)

        pygame.draw.rect(self.screen, (14, 14, 19), detail_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, detail_rect, 1)
        if entries and jump_skill:
            mod_name = entries[self.selected_jump_mod_index]
            active = bool(jump_skill.modifications.get(mod_name, False))
            detail_y = detail_rect.top + 16
            self._draw_text(mod_name, self.large_font, self.colors.GOLD, detail_rect.left + 16, detail_y, detail_rect.width - 32)
            detail_y += self.large_font.get_height() + 12
            self._draw_text(f"Status: {'Active' if active else 'Inactive'}", self.normal_font, self.colors.WHITE, detail_rect.left + 16, detail_y, detail_rect.width - 32)
            detail_y += self.normal_font.get_height() + 8
            self._draw_text(self._jump_mod_unlock_text(jump_skill, mod_name), self.small_font, self.colors.GRAY, detail_rect.left + 16, detail_y, detail_rect.width - 32)
            detail_y += self.small_font.get_height() + 14
            self._draw_wrapped_text(
                self._jump_mod_description(mod_name),
                self.normal_font,
                self.colors.WHITE,
                detail_rect.left + 16,
                detail_y,
                detail_rect.width - 32,
                max_lines=5,
            )
        else:
            self._draw_text("Jump has not been learned.", self.normal_font, self.colors.GRAY, detail_rect.left + 16, detail_rect.top + 16, detail_rect.width - 32)

    def _resolve_value_and_cap(self, player_char) -> tuple[int, int]:
        cap = promotion_kits.resolve_cap(player_char)
        try:
            from src.core.classes import class_rings

            data = class_rings.ensure_state(player_char)["data"]["Stalwart Defender"]
            value = int(data.get("guard_meter", 0) or 0)
        except Exception:
            value = 0
        return max(0, min(cap, value)), cap

    def resolve_spend_rows(self, player_char) -> list[dict[str, Any]]:
        return promotion_kits.resolve_spend_rows(player_char)

    def _draw_resolve_ability_box(self, entry: dict[str, Any], rect: pygame.Rect, *, surge: bool = False) -> None:
        unlocked = bool(entry.get("unlocked"))
        bg = (14, 14, 20) if unlocked else (24, 24, 28)
        border = self.colors.GOLD if unlocked else self.colors.DARK_GRAY
        text_color = self.colors.WHITE if unlocked else self.colors.GRAY
        title_color = self.colors.GOLD if unlocked else self.colors.GRAY
        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, border, rect, 1)

        title = str(entry.get("name", ""))
        role = str(entry.get("role", ""))
        description = str(entry.get("description", ""))
        if not unlocked:
            title = "???"
            description = "Locked"
        cost = "Full bar" if surge else f"{int(entry.get('cost', 0) or 0)} Resolve"

        self._draw_text(title, self.normal_font, title_color, rect.left + 10, rect.top + 8, rect.width - 20)
        self._draw_text(f"{role} - {cost}", self.small_font, text_color, rect.left + 10, rect.top + 34, rect.width - 20)
        self._draw_wrapped_text(description, self.small_font, text_color, rect.left + 10, rect.top + 56, rect.width - 20, max_lines=2)

    def _draw_resolve_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        resolve, cap = self._resolve_value_and_cap(player_char)
        content = self.details_rect.inflate(-32, -64)
        content.top = y
        meter_width = min(700, max(360, (content.width * 3) // 4))
        bar_rect = pygame.Rect(content.centerx - meter_width // 2, y + 58, meter_width, 28)
        self._draw_meter_bar(bar_rect, resolve, cap, color=self.colors.RED)
        value_text = f"{resolve}/{cap}"
        value_surface = self.normal_font.render(value_text, True, self.colors.WHITE)
        self.screen.blit(value_surface, value_surface.get_rect(center=bar_rect.center))

        section_y = bar_rect.bottom + 36
        self._draw_text("Resolve Spends", self.normal_font, self.colors.GOLD, content.left, section_y, content.width)
        box_top = section_y + self.normal_font.get_height() + 14
        columns = 3
        gap = 12
        box_width = (content.width - gap * (columns - 1)) // columns
        box_height = 92
        for index, entry in enumerate(self.resolve_spend_rows(player_char)):
            col = index % columns
            row = index // columns
            rect = pygame.Rect(content.left + col * (box_width + gap), box_top + row * (box_height + gap), box_width, box_height)
            self._draw_resolve_ability_box(entry, rect)

        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        if class_name == "Stalwart Defender":
            surge_y = box_top + 2 * (box_height + gap) + 22
            self._draw_text("Resolve Surges", self.normal_font, self.colors.GOLD, content.left, surge_y, content.width)
            for index, entry in enumerate(promotion_kits.resolve_surge_rows(player_char)):
                rect = pygame.Rect(
                    content.left + index * (box_width + gap),
                    surge_y + self.normal_font.get_height() + 14,
                    box_width,
                    box_height,
                )
                self._draw_resolve_ability_box(entry, rect, surge=True)

    def _draw_oath_conviction_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        state = promotion_kits.combat_state(player_char)
        conviction = int(state.get("oath_conviction", 0) or 0)
        cap = max(1, promotion_kits.cap_for(player_char, "oath_conviction"))
        vow = paladin.path(player_char) or "Unsworn"
        content = self.details_rect.inflate(-32, -64)
        content.top = y
        left_width = max(320, (content.width * 2) // 5)
        left_rect = pygame.Rect(content.left, content.top, left_width, content.height)
        right_rect = pygame.Rect(left_rect.right + 18, content.top, content.right - left_rect.right - 18, content.height)

        self._draw_text(f"Conviction {conviction}/{cap}", self.large_font, self.colors.WHITE, left_rect.left, y, left_rect.width)
        bar_rect = pygame.Rect(left_rect.left, y + self.large_font.get_height() + 8, left_rect.width, 16)
        self._draw_meter_bar(bar_rect, conviction, cap, color=self.colors.GOLD)
        rows = [("Vow", vow)]
        if vow in paladin.PATHS:
            rows.extend(
                [
                    ("Signature", paladin.SKILL_NAMES[vow]),
                    ("Aura", paladin.AURA_NAMES[vow]),
                    ("Mark", paladin.MARK_NAMES[vow]),
                ]
            )
        self._draw_key_values(rows, left_rect, bar_rect.bottom + 18, font=self.normal_font, row_gap=8)

        detail_y = right_rect.top
        self._draw_text("Oath Rhythm", self.normal_font, self.colors.GOLD, right_rect.left, detail_y, right_rect.width)
        detail_y += self.normal_font.get_height() + 12
        for title, body in (
            ("Build", "Use your sworn vow skill and complete its clean payoff to build Conviction."),
            ("Spend", "Your next matching vow action spends stored Conviction to strengthen that vow's defining moment."),
            ("Risk", "Aura and mark pressure still matter; Conviction reinforces the oath without erasing its drawback."),
        ):
            if detail_y + 80 > right_rect.bottom:
                break
            detail_y = self._draw_mechanic_note_card(right_rect, title, body, detail_y)

    def _split_mechanic_content(self, y: int) -> tuple[pygame.Rect, pygame.Rect]:
        content = self.details_rect.inflate(-32, -64)
        content.top = y
        left_width = max(320, (content.width * 2) // 5)
        left_rect = pygame.Rect(content.left, content.top, left_width, content.height)
        right_rect = pygame.Rect(left_rect.right + 18, content.top, content.right - left_rect.right - 18, content.height)
        return left_rect, right_rect

    def _draw_progress_row(
        self,
        rect: pygame.Rect,
        label: str,
        value: int | float,
        cap: int | float,
        y: int,
        *,
        detail: str = "",
        color=None,
    ) -> int:
        cap = max(1, float(cap or 1))
        value = max(0.0, min(cap, float(value or 0)))
        self._draw_text(label, self.normal_font, self.colors.WHITE, rect.left, y, rect.width)
        value_text = f"{value:g}/{cap:g}" if detail == "" else f"{value:g}/{cap:g} {detail}"
        self._draw_text(value_text, self.small_font, self.colors.GRAY, rect.left, y + self.normal_font.get_height() + 2, rect.width)
        bar_rect = pygame.Rect(rect.left, y + self.normal_font.get_height() + self.small_font.get_height() + 8, rect.width, 12)
        self._draw_meter_bar(bar_rect, int(value), int(cap), color=color or self.colors.GOLD)
        return bar_rect.bottom + 12

    def _ring_state_text(self, player_char, class_name: str) -> str:
        try:
            from src.core.classes import class_rings

            if class_rings.is_awakened(player_char, class_name):
                return "Awakened, equipped" if class_rings.has_equipped_class_ring(player_char) else "Awakened, unequipped"
            if class_rings.has_visible_class_ring(player_char):
                return "Dormant"
        except Exception:
            pass
        return "Not visible"

    def _draw_school_affinity_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        affinity = wizard.ensure_affinity(player_char)
        cap = wizard.cap_for(player_char)

        row_y = y
        spells = getattr(player_char, "spellbook", {}).get("Spells", {})
        for school in wizard.AFFINITY_SCHOOLS:
            chain = wizard.SPELL_UPGRADES.get(school, ())
            known = next((name for name in reversed(chain) if name in spells), chain[0] if chain else "None")
            detail = f"{known}"
            row_y = self._draw_progress_row(left_rect, school, affinity.get(school, 0), cap, row_y, detail=detail)
            if row_y > left_rect.bottom - 40:
                break

        if class_name == "Wizard":
            self._draw_key_values(
                [("Wizard Ring", self._ring_state_text(player_char, "Wizard"))],
                right_rect,
                y,
                font=self.normal_font,
                row_gap=8,
            )

    def _draw_contracts_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        state = demonologist.ensure_state(player_char)
        patron = state.get("active_patron") or "None"
        mood = int(state.get("patron_moods", {}).get(patron, 0) or 0) if patron != "None" else 0
        corruption = int(state.get("corruption", 0) or 0)
        unlocked = list(state.get("unlocked_contracts", []))
        echo = state.get("imprisoned_familiar") or {}

        row_y = self._draw_progress_row(left_rect, "Corruption", corruption, 100, y, detail=f"Tier {demonologist.corruption_tier(player_char)}", color=self.colors.RED)
        rows = [
            ("Crypt", "Unlocked" if state.get("crypt_unlocked") else "Hidden"),
            ("Active Patron", patron),
            ("Patron Mood", str(mood)),
            ("Unlocked", ", ".join(unlocked) if unlocked else "None"),
            ("Echo", str(echo.get("name") or echo.get("spec") or "None")),
            ("Ring", "Awakened" if state.get("ring_awakened") else self._ring_state_text(player_char, "Demonologist")),
        ]
        self._draw_key_values(rows, left_rect, row_y, font=self.normal_font, row_gap=8)

        self._draw_text("Recent Contracts", self.normal_font, self.colors.GOLD, right_rect.left, y, right_rect.width)
        history_y = y + self.normal_font.get_height() + 12
        history = list(state.get("contract_history", []))[-5:]
        if not history:
            self._draw_text("No contract history", self.normal_font, self.colors.GRAY, right_rect.left, history_y, right_rect.width)
            return
        for entry in reversed(history):
            patron_text = str(entry.get("patron") or "?")
            intent_text = str(entry.get("intent") or "?")
            self._draw_text(f"{patron_text} - {intent_text}", self.normal_font, self.colors.WHITE, right_rect.left, history_y, right_rect.width)
            history_y += self.normal_font.get_height() + self.small_font.get_height() + 12
            if history_y > right_rect.bottom - 24:
                break

    def _draw_runes_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        state = astromancer.ensure_state(player_char)
        active = astromancer.active_constellation(player_char) if class_name == "Astromancer" else ""

        row_y = y
        if active:
            self._draw_text(f"Active Constellation: {active}", self.normal_font, self.colors.GOLD, left_rect.left, y, left_rect.width)
            row_y += self.normal_font.get_height() + 14
        for sign in astromancer.CONSTELLATIONS:
            count = int(state["runes"].get(sign, 0) or 0)
            element = astromancer.SIGN_TO_ELEMENT.get(sign, "")
            detail = f"{element}"
            if sign == active and astromancer.is_astromancer(player_char):
                detail += " active"
            row_y = self._draw_progress_row(left_rect, sign, count, astromancer.RUNE_CAP, row_y, detail=detail)

        boostable = astromancer.boostable_spells(player_char)
        rows = [
            ("Boostable Spells", ", ".join(boostable) if boostable else "None"),
        ]
        if class_name == "Astromancer":
            rows.insert(0, ("Ring", self._ring_state_text(player_char, "Astromancer")))
        self._draw_key_values(rows, right_rect, y, font=self.normal_font, row_gap=10)

    def _get_totem_skill(self, player_char):
        skills = getattr(player_char, "spellbook", {}).get("Skills", {})
        if "Totem" in skills:
            return skills["Totem"]
        for skill in skills.values():
            if getattr(skill, "name", "") == "Totem":
                return skill
        return None

    def _totem_unlocked_aspects(self, player_char, totem_skill) -> list[str]:
        if totem_skill and hasattr(totem_skill, "get_unlocked_aspects"):
            try:
                return list(totem_skill.get_unlocked_aspects(player_char))
            except TypeError:
                return list(totem_skill.get_unlocked_aspects())
        return []

    def _open_totem_aspects_popup(self, player_char) -> None:
        popup = TotemAspectsPopupMenu(self.presenter, self, title="Totem Aspects")
        popup.show(player_char=player_char, flush_events=True)

    def _draw_totems_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        totem_skill = self._get_totem_skill(player_char)
        unlocked = self._totem_unlocked_aspects(player_char, totem_skill)
        if class_name != "Soulcatcher":
            unlocked = [aspect for aspect in unlocked if aspect != "Soul"]
        active = nature_totems.active_totem_aspect(player_char) or getattr(totem_skill, "active_aspect", "") or "None"
        if active == "Soul" and class_name != "Soulcatcher":
            active = "None"
        resonance = promotion_kits.totem_resonance(player_char)
        cap = promotion_kits.cap_for(player_char, "totem_resonance")

        row_y = self._draw_progress_row(left_rect, "Totem Resonance", resonance, cap, y, detail="Pulse strength", color=self.colors.GREEN)
        rows = [
            ("Active Aspect", str(active)),
            ("Unlocked Aspects", ", ".join(unlocked) if unlocked else "None"),
            ("Staff Bond", "Aligned" if nature_totems.has_staff_equipped(player_char) else "Unfocused"),
            ("Select", "C/Enter: Totem Aspects"),
        ]
        self._draw_key_values(rows, left_rect, row_y, font=self.normal_font, row_gap=8)

        self._draw_text("Communions", self.normal_font, self.colors.GOLD, right_rect.left, y, right_rect.width)
        list_y = y + self.normal_font.get_height() + 12
        aspects = list(nature_totems.ELEMENTAL_ASPECTS)
        if class_name == "Soulcatcher" and "Soul" in unlocked:
            aspects.append("Soul")
        for aspect in aspects:
            spell_name = nature_totems.highest_unlocked_spell_name(player_char, aspect) or nature_totems.communion_spell_name(aspect) or "None"
            status = "Unlocked" if aspect in unlocked or spell_name in getattr(player_char, "spellbook", {}).get("Spells", {}) else "Locked"
            self._draw_text(aspect, self.normal_font, self.colors.WHITE, right_rect.left, list_y, 110)
            self._draw_text(f"{status} - {spell_name}", self.small_font, self.colors.GRAY, right_rect.left + 118, list_y + 2, right_rect.width - 118)
            list_y += self.normal_font.get_height() + 12
            if list_y > right_rect.bottom - 24:
                break

    def _draw_case_journal_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        state = promotion_kits.ensure_state(player_char)
        journal = state["case_journal"]
        combat = promotion_kits.combat_state(player_char)
        revelation = combat.get("revelation", {})
        current_revelation = max((int(value or 0) for value in revelation.values()), default=0) if isinstance(revelation, dict) else 0
        best_type, best_progress = max(journal.items(), key=lambda item: (int(item[1]), item[0]), default=("None", 0))

        rows = [
            ("Best Case", f"{best_type} {int(best_progress)}/100"),
            ("Best Rank", promotion_kits.case_rank(best_progress)),
            ("Revelation", f"{current_revelation}/{promotion_kits.cap_for(player_char, 'revelation')}"),
        ]
        if class_name == "Seeker":
            rows.extend(
                [
                    ("Wayfinding", "Aligned" if promotion_kits.wayfinding_discount(player_char) > 0 else "Quiet"),
                    ("Hidden Cache", self._ring_state_text(player_char, "Seeker")),
                ]
            )
        self._draw_key_values(rows, left_rect, y, font=self.normal_font, row_gap=10)

        self._draw_text("Enemy-Type Progress", self.normal_font, self.colors.GOLD, right_rect.left, y, right_rect.width)
        list_y = y + self.normal_font.get_height() + 12
        entries = sorted(journal.items(), key=lambda item: (-int(item[1]), item[0]))
        if not entries:
            self._draw_text("No cases recorded", self.normal_font, self.colors.GRAY, right_rect.left, list_y, right_rect.width)
            return
        for enemy_type, progress in entries[:8]:
            detail = promotion_kits.case_rank(progress)
            list_y = self._draw_progress_row(right_rect, str(enemy_type), int(progress), 100, list_y, detail=detail, color=self.colors.GREEN)
            if list_y > right_rect.bottom - 40:
                break

    def _draw_crescendo_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        song_state = bard.ensure_song_state(player_char)
        exploration = bard.ensure_exploration_song_state(player_char)
        combat = promotion_kits.combat_state(player_char)
        crescendo = int(combat.get("crescendo", 0) or 0)
        repertoire = promotion_kits.ensure_state(player_char)["bard_repertoire"]
        mastered = sum(1 for entry in repertoire.values() if entry.get("known"))

        row_y = self._draw_progress_row(left_rect, "Crescendo", crescendo, 3, y, detail="Coda", color=self.colors.GOLD)
        rows = [
            ("Combat Song", str(song_state.get("active") or "None")),
            ("Song Turns", str(song_state.get("turns", 0))),
            ("Exploration Song", str(exploration.get("active") or "None")),
            ("Exploration Steps", str(exploration.get("steps", 0))),
        ]
        if class_name == "Troubadour":
            rows.extend(
                [
                    ("Encore", str(song_state.get("encore") or self._ring_state_text(player_char, "Troubadour"))),
                    ("Mastered", f"{mastered}/{len(repertoire)}"),
                ]
            )
        self._draw_key_values(rows, left_rect, row_y, font=self.normal_font, row_gap=8)

        if class_name != "Troubadour":
            return

        self._draw_text("Advanced Repertoire", self.normal_font, self.colors.GOLD, right_rect.left, y, right_rect.width)
        list_y = y + self.normal_font.get_height() + 12
        for song, entry in repertoire.items():
            known = "Mastered" if entry.get("known") else "Practice"
            xp = int(entry.get("practice_xp", 0) or 0)
            finishes = int(entry.get("clean_finishes", 0) or 0)
            self._draw_text(song, self.normal_font, self.colors.WHITE, right_rect.left, list_y, right_rect.width)
            practice = "Complete" if known == "Mastered" else "Growing" if xp or finishes else "Unstarted"
            self._draw_text(f"{known} - {practice}", self.small_font, self.colors.GRAY, right_rect.left, list_y + self.normal_font.get_height() + 2, right_rect.width)
            list_y += self.normal_font.get_height() + self.small_font.get_height() + 12
            if list_y > right_rect.bottom - 24:
                break

    def _draw_forms_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        transform_type = getattr(player_char, "transform_type", None)
        base_form = self._attr_name(transform_type, class_name or "Unknown")
        shifted = lycan.is_transformed(player_char) if class_name == "Lycan" or base_form == "Lycan" else bool(transform_type and self._attr_name(transform_type, "") != class_name)
        rows = [
            ("Current Form", "Shifted" if shifted else "Humanoid"),
            ("Stored Form", base_form),
            ("Transform", "Available" if transform_type else "Unavailable"),
            ("Dismiss", "Available" if shifted else "Unavailable"),
        ]
        if class_name == "Lycan" or base_form == "Lycan":
            rows.append(("Ring", self._ring_state_text(player_char, "Lycan")))
        self._draw_key_values(rows, left_rect, y, font=self.normal_font, row_gap=10)

        if class_name == "Lycan" or base_form == "Lycan":
            lycan_state = lycan.ensure_state(player_char)
            control = promotion_kits.lycan_control_state(player_char)
            list_y = self._draw_progress_row(right_rect, "Moon Cycle", lycan_state.get("moon_steps", 0), lycan.STEPS_PER_PHASE, y, detail=str(lycan_state.get("moon_phase", "New")), color=self.colors.GOLD)
            rows = [
                ("Frenzy Lock", f"{int(lycan_state.get('frenzy_turns', 0) or 0)} turn(s)"),
                ("Control Rank", str(control.get("rank", "Feral"))),
                ("Stress Records", str(control.get("stress_events", 0))),
                ("Dragon Essence", "Yes" if control.get("dragon_essence") or lycan_state.get("dragon_essence") else "No"),
            ]
            self._draw_key_values(rows, right_rect, list_y, font=self.normal_font, row_gap=8)
        else:
            return

    def _draw_aspects_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        state = archdruid.ensure_state(player_char)
        combat = promotion_kits.combat_state(player_char)
        harmony = combat.get("aspect_harmony", set())
        if not isinstance(harmony, set):
            harmony = set(harmony)

        row_y = y
        for affinity in archdruid.AFFINITIES:
            attunement = int(state["attunement"].get(affinity, 0) or 0)
            status = "Awake" if state["aspects"].get(affinity) else "Sealed"
            if state["catalysts"].get(affinity):
                status += ", catalyst"
            row_y = self._draw_progress_row(left_rect, affinity, attunement, archdruid.MASTERY_THRESHOLD, row_y, detail=status, color=self.colors.GREEN)
            if row_y > left_rect.bottom - 40:
                break

        harmony_text = ", ".join(sorted(harmony)) if harmony else "None"
        rows = [
            ("Grove", "Unlocked" if state.get("grove_unlocked") else "Hidden"),
            ("Aspect Harmony", harmony_text),
            ("Fourfold Surge", "Ready" if len(harmony) >= 2 else "Building"),
            ("Ring", "Awakened" if state.get("ring_awakened") else self._ring_state_text(player_char, "Archdruid")),
        ]
        self._draw_key_values(rows, right_rect, y, font=self.normal_font, row_gap=8)
        detail_y = y + self.normal_font.get_height() * 6 + 64
        self._draw_text("Catalyst Progress", self.normal_font, self.colors.GOLD, right_rect.left, detail_y, right_rect.width)
        detail_y += self.normal_font.get_height() + 10
        for affinity in archdruid.AFFINITIES:
            progress = state["progress"].get(affinity, {})
            text = "Stirring" if any(int(value or 0) > 0 for value in progress.values()) else "Quiet"
            self._draw_text(affinity, self.small_font, self.colors.GRAY, right_rect.left, detail_y, 90)
            self._draw_text(text, self.small_font, self.colors.WHITE, right_rect.left + 96, detail_y, right_rect.width - 96)
            detail_y += self.small_font.get_height() + 8
            if detail_y > right_rect.bottom - 12:
                break

    def draw_class_tab(self, player_char):
        mechanic_tab = self.class_mechanic_tab(player_char)
        panel_title = mechanic_tab.label if mechanic_tab is not None else "Class"
        y = self._draw_panel(self.details_rect, panel_title)

        if grandmaster.is_weapon_discipline_class(player_char):
            self.class_companion_selector_active = False
            discipline_rect = pygame.Rect(
                self.details_rect.left + 16,
                y,
                self.details_rect.width - 32,
                self.details_rect.bottom - y - 16,
            )
            self._class_roster_rect = discipline_rect
            self._draw_weapon_discipline_panel(player_char, discipline_rect, y, show_heading=False)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Oath Conviction":
            self._draw_oath_conviction_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Aerial Tempo":
            self._draw_aerial_tempo_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Resolve":
            self._draw_resolve_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "School Affinity":
            self._draw_school_affinity_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Contracts":
            self._draw_contracts_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Runes":
            self._draw_runes_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Totems":
            self._draw_totems_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Case Journal":
            self._draw_case_journal_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Crescendo":
            self._draw_crescendo_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Forms":
            self._draw_forms_tab(player_char, y)
            return

        if mechanic_tab is not None and mechanic_tab.label == "Aspects":
            self._draw_aspects_tab(player_char, y)
            return

        self._jump_mod_row_rects = []
        self.weapon_discipline_selector_active = False
        gap = 14
        left_width = max(260, (self.details_rect.width * 2) // 5)
        overview_rect = pygame.Rect(
            self.details_rect.left + 16,
            y,
            left_width - 16,
            self.details_rect.bottom - y - 16,
        )
        roster_rect = pygame.Rect(
            overview_rect.right + gap,
            y,
            self.details_rect.right - overview_rect.right - gap - 16,
            self.details_rect.bottom - y - 16,
        )

        overview_y = y
        overview_y = self._draw_key_values(
            self.class_summary_rows(player_char),
            overview_rect,
            overview_y,
            font=self.normal_font,
            row_gap=8,
            bottom_limit=overview_rect.bottom - 16,
        )
        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        if class_name in {"Ranger", "Beast Master"}:
            overview_y += 8
            overview_y = self._draw_favored_enemy_progress_panel(player_char, overview_rect, overview_y)

        entries = self.class_companion_entries(player_char)
        if not entries:
            self.class_companion_selector_active = False
            self._class_roster_rect = roster_rect
            if class_name in {"Ranger", "Beast Master"}:
                self._draw_empty_companion_slots(roster_rect, y)
            return

        self.selected_class_companion_index = max(
            0,
            min(self.selected_class_companion_index, max(0, len(entries) - 1)),
        )
        self._class_roster_rect = roster_rect
        heading = (
            "Companion Stable"
            if class_name in {"Ranger", "Beast Master"}
            else mechanic_tab.label if mechanic_tab is not None else "Companions"
        )
        self._draw_text(heading, self.normal_font, self.colors.GOLD, roster_rect.left, y, roster_rect.width)
        singular_label = {
            "Familiar": "familiar",
            "Companion": "companion",
            "Companion Stable": "companion",
        }.get(heading, "summon")
        has_tamed_roster = any(
            kind in {"Companion", "Held Companion"} and getattr(companion, "spec", "") == "Tamed"
            for kind, companion in entries
        )
        if self.class_companion_selector_active:
            helper = (
                "Arrows: Select  Enter: Inspect  S: Lead  R: Release  C/Esc: Back"
                if has_tamed_roster
                else "Arrows: Select  Enter: Inspect  C/Esc: Back"
            )
        else:
            helper = f"C: Select {singular_label}"
        helper_width = self.small_font.size(helper)[0]
        self._draw_text(
            helper,
            self.small_font,
            self.colors.GRAY,
            roster_rect.right - min(helper_width, roster_rect.width),
            self.details_rect.top + 18,
            roster_rect.width,
        )

        for index, rect in enumerate(self.class_companion_tile_rects(entries)):
            kind, companion = entries[index]
            self._draw_class_companion_tile(
                kind,
                companion,
                rect,
                selected=index == self.selected_class_companion_index,
                player_char=player_char,
            )

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
        self.ensure_active_tab_visible(player_char)
        self.draw_background()
        self.draw_tabs(player_char)
        if self.active_tab.key == "character":
            self.draw_character_panel(player_char)
            self.draw_combat_panel(player_char)
        elif self.active_tab.key == "class":
            self.draw_class_tab(player_char)
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

            self.ensure_active_tab_visible(player_char)
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
                    tab_index = hit_index(self.tab_button_rects(player_char), pos)
                    action_index = hit_index(self.action_rects(), pos)
                    if action_index is not None and event.type == pygame.MOUSEMOTION:
                        self.current_selection = action_index
                    elif tab_index is not None and is_left_click(event):
                        if input_armed:
                            self.select_visible_tab_index(tab_index, player_char)
                            if self.active_tab.key != "equipment":
                                self.equipment_selector_active = False
                            if self.active_tab.key != "class":
                                self.class_companion_selector_active = False
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
                    elif (
                        self.active_tab.key == "class"
                        and self.active_mechanic_label(player_char) == "Aerial Tempo"
                    ):
                        row_index = hit_index(self.jump_mod_row_rects(), pos)
                        if row_index is not None:
                            self.selected_jump_mod_index = row_index
                            if is_left_click(event) and input_armed:
                                self._toggle_selected_jump_mod(player_char)
                            continue
                    elif self.active_tab.key == "class" and not grandmaster.is_weapon_discipline_class(player_char):
                        entries = self.class_companion_entries(player_char)
                        tile_index = hit_index(self.class_companion_tile_rects(entries), pos)
                        if tile_index is not None:
                            self.class_companion_selector_active = True
                            self.selected_class_companion_index = tile_index
                            if is_left_click(event) and input_armed:
                                self._open_class_companion_popup(player_char)
                            continue
                    elif self.active_tab.key == "class" and grandmaster.is_weapon_discipline_class(player_char):
                        row_index = hit_index(self.weapon_discipline_row_rects(), pos)
                        if row_index is not None:
                            self.selected_weapon_discipline_index = row_index
                            if is_left_click(event) and input_armed:
                                self._open_weapon_discipline_popup(player_char)
                            continue

                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                if event.type != pygame.KEYDOWN:
                    continue

                if event.key == pygame.K_ESCAPE and self.equipment_selector_active:
                    self.equipment_selector_active = False
                elif event.key == pygame.K_ESCAPE and self.class_companion_selector_active:
                    self.class_companion_selector_active = False
                elif event.key == pygame.K_ESCAPE:
                    return "Exit Menu"
                elif event.key == pygame.K_e and self.active_tab.key == "equipment":
                    self.equipment_selector_active = not self.equipment_selector_active
                elif event.key == pygame.K_c and self.active_tab.key == "class":
                    if self.active_mechanic_label(player_char) == "Totems":
                        self._open_totem_aspects_popup(player_char)
                    elif not grandmaster.is_weapon_discipline_class(player_char):
                        entries = self.class_companion_entries(player_char)
                        self.class_companion_selector_active = bool(entries) and not self.class_companion_selector_active
                elif event.key in (pygame.K_TAB, pygame.K_RIGHT):
                    if self.active_tab.key == "equipment" and self.equipment_selector_active and event.key == pygame.K_RIGHT:
                        self.move_equipment_selector(player_char, "right")
                    elif (
                        self.active_tab.key == "class"
                        and self.class_companion_selector_active
                        and event.key == pygame.K_RIGHT
                        and self.class_companion_entries(player_char)
                    ):
                        entries = self.class_companion_entries(player_char)
                        self.selected_class_companion_index = min(len(entries) - 1, self.selected_class_companion_index + 1)
                    else:
                        self.move_tab(1, player_char)
                elif event.key == pygame.K_LEFT:
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.move_equipment_selector(player_char, "left")
                    elif (
                        self.active_tab.key == "class"
                        and self.class_companion_selector_active
                        and self.class_companion_entries(player_char)
                    ):
                        self.selected_class_companion_index = max(0, self.selected_class_companion_index - 1)
                    else:
                        self.move_tab(-1, player_char)
                elif event.key == pygame.K_1:
                    self.select_visible_tab_index(0, player_char)
                elif event.key == pygame.K_2:
                    self.select_visible_tab_index(1, player_char)
                elif event.key == pygame.K_3:
                    self.select_visible_tab_index(2, player_char)
                elif event.key == pygame.K_UP:
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.move_equipment_selector(player_char, "up")
                    elif self.active_tab.key == "class" and self.active_mechanic_label(player_char) == "Aerial Tempo" and self.jump_mod_entries(player_char):
                        self.selected_jump_mod_index = max(0, self.selected_jump_mod_index - 1)
                    elif self.active_tab.key == "class" and self.class_companion_selector_active and self.class_companion_entries(player_char):
                        self.selected_class_companion_index = max(0, self.selected_class_companion_index - 1)
                    elif self.active_tab.key == "class" and grandmaster.is_weapon_discipline_class(player_char):
                        self.selected_weapon_discipline_index = max(0, self.selected_weapon_discipline_index - 1)
                    else:
                        self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.move_equipment_selector(player_char, "down")
                    elif self.active_tab.key == "class" and self.active_mechanic_label(player_char) == "Aerial Tempo" and self.jump_mod_entries(player_char):
                        entries = self.jump_mod_entries(player_char)
                        self.selected_jump_mod_index = min(len(entries) - 1, self.selected_jump_mod_index + 1)
                    elif self.active_tab.key == "class" and self.class_companion_selector_active and self.class_companion_entries(player_char):
                        entries = self.class_companion_entries(player_char)
                        self.selected_class_companion_index = min(len(entries) - 1, self.selected_class_companion_index + 1)
                    elif self.active_tab.key == "class" and grandmaster.is_weapon_discipline_class(player_char):
                        self.selected_weapon_discipline_index = min(
                            len(grandmaster.WEAPON_TYPES) - 1,
                            self.selected_weapon_discipline_index + 1,
                        )
                    else:
                        self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                elif event.key == pygame.K_a and self.active_tab.key == "class" and self.class_companion_selector_active and self.class_companion_entries(player_char):
                    self.selected_class_companion_index = max(0, self.selected_class_companion_index - 1)
                elif event.key == pygame.K_d and self.active_tab.key == "class" and self.class_companion_selector_active and self.class_companion_entries(player_char):
                    entries = self.class_companion_entries(player_char)
                    self.selected_class_companion_index = min(len(entries) - 1, self.selected_class_companion_index + 1)
                elif event.key == pygame.K_s and self.active_tab.key == "class" and self.class_companion_selector_active:
                    self._activate_selected_tamed_companion(player_char)
                elif event.key == pygame.K_r and self.active_tab.key == "class" and self.class_companion_selector_active:
                    self._release_selected_tamed_companion(player_char)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.active_tab.key == "equipment" and self.equipment_selector_active:
                        self.open_selected_equipment_change(player_char)
                    elif (
                        self.active_tab.key == "class"
                        and self.active_mechanic_label(player_char) == "Aerial Tempo"
                        and self._has_jump_mods(player_char)
                    ):
                        self._toggle_selected_jump_mod(player_char)
                    elif self.active_tab.key == "class" and self.active_mechanic_label(player_char) == "Totems":
                        self._open_totem_aspects_popup(player_char)
                    elif self.active_tab.key == "class" and self.class_companion_selector_active and self.class_companion_entries(player_char):
                        self._open_class_companion_popup(player_char)
                    elif self.active_tab.key == "class" and grandmaster.is_weapon_discipline_class(player_char):
                        self._open_weapon_discipline_popup(player_char)
                    else:
                        result = self._open_menu_choice(self.menu_options[self.current_selection], player_char)
                        if result:
                            return result

            self.presenter.clock.tick(30)
