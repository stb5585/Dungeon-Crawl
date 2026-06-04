"""Modern, parallel character menu implementation for the Pygame UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pygame

from .character_screen import CharacterScreen
from .confirmation_popup import ConfirmationPopup
from .input_guards import prepare_guarded_input, release_guard_allows_input, update_input_armed_from_event
from .popup_menus import EquipmentPopupMenu, InventoryPopupMenu, JumpModsPopupMenu, SimpleListPopupMenu, TotemAspectsPopupMenu


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
RESISTANCE_ORDER = ("Fire", "Electric", "Earth", "Shadow", "Poison", "Ice", "Water", "Wind", "Holy", "Physical")


class ModernCharacterScreen(CharacterScreen):
    """Premium RPG-style character menu kept separate from the legacy layout."""

    def __init__(self, presenter, tabs: tuple[CharacterTab, ...] = DEFAULT_CHARACTER_TABS):
        self.tabs = tabs
        self.active_tab_index = 0
        super().__init__(presenter)

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

        character_width = (self.content_rect.width - gap) // 2
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
                return
        raise ValueError(f"Unknown character tab: {key}")

    def move_tab(self, delta: int) -> None:
        self.active_tab_index = (self.active_tab_index + delta) % len(self.tabs)

    @staticmethod
    def _attr_name(value: Any, default: str = "Unknown") -> str:
        return str(getattr(value, "name", default) or default)

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
    def xp_progress(player_char) -> float:
        level = getattr(player_char, "level", None)
        exp = max(0, int(getattr(level, "exp", 0) or 0))
        to_next = max(0, int(getattr(level, "exp_to_gain", 0) or 0))
        total = exp + to_next
        if total <= 0:
            return 0.0
        return max(0.0, min(1.0, exp / total))

    def build_character_summary(self, player_char) -> list[tuple[str, str]]:
        race = self._attr_name(getattr(player_char, "race", None), "")
        cls = self._attr_name(getattr(player_char, "cls", None), "")
        level = getattr(getattr(player_char, "level", None), "level", 1)
        exp = getattr(getattr(player_char, "level", None), "exp", 0)
        to_next = getattr(getattr(player_char, "level", None), "exp_to_gain", 0)
        return [
            ("Name", str(getattr(player_char, "name", "Adventurer"))),
            ("Class", " ".join(part for part in (race, cls) if part) or "Unknown"),
            ("Level", str(level)),
            ("XP Earned", str(exp)),
            ("XP To Next", str(to_next)),
        ]

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
            ("Attack", str(self._check_mod(player_char, "weapon"))),
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
        for slot in EQUIPMENT_SLOT_ORDER:
            if slot == "Helmet" and slot not in equipment:
                slots.append(EquipmentSlotSummary(slot, "(future slot)", "Helmet mechanics are not active yet.", "", False))
                continue
            item = equipment.get(slot)
            if item is None:
                slots.append(EquipmentSlotSummary(slot, "(empty)", "No item equipped.", ""))
                continue
            description = str(getattr(item, "description", "") or getattr(item, "desc", "") or "")
            bonus_parts = []
            for attr in ("damage", "armor", "mod", "weight"):
                value = getattr(item, attr, None)
                if value not in (None, "", 0):
                    bonus_parts.append(f"{attr.title()}: {value}")
            slots.append(EquipmentSlotSummary(slot, self._attr_name(item), description, ", ".join(bonus_parts)))
        return slots

    def group_resistances(self, player_char) -> dict[str, list[ResistanceSummary]]:
        resistance = getattr(player_char, "resistance", {}) or {}
        weaknesses: list[ResistanceSummary] = []
        resistances: list[ResistanceSummary] = []
        for name in RESISTANCE_ORDER:
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

    def draw_tabs(self):
        self._draw_panel(self.tab_rect)
        x = self.tab_rect.left + 12
        tab_width = max(120, min(190, (self.tab_rect.width - 24) // max(1, len(self.tabs))))
        for index, tab in enumerate(self.tabs):
            rect = pygame.Rect(x + (index * tab_width), self.tab_rect.top + 8, tab_width - 8, self.tab_rect.height - 16)
            active = index == self.active_tab_index
            if active:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, rect, 2)
            self._draw_text(tab.label, self.normal_font, self.colors.GOLD if active else self.colors.WHITE, rect.left + 12, rect.centery - self.normal_font.get_height() // 2, rect.width - 24)

    def draw_character_panel(self, player_char):
        y = self._draw_panel(self.character_panel_rect, "Character")
        portrait_size = min(118, max(82, self.character_panel_rect.width // 3))
        portrait = pygame.Rect(self.character_panel_rect.left + 16, y, portrait_size, portrait_size)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, portrait)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, portrait, 2)
        self._draw_text("Portrait", self.small_font, self.colors.GRAY, portrait.left + 10, portrait.centery - self.small_font.get_height() // 2, portrait.width - 20)

        info_x = portrait.right + 16
        info_y = y
        info_width = self.character_panel_rect.right - info_x - 16
        for label, value in self.build_character_summary(player_char):
            self._draw_text(label.upper(), self.small_font, self.colors.GRAY, info_x, info_y, info_width)
            info_y += self.small_font.get_height()
            self._draw_text(value, self.normal_font, self.colors.WHITE, info_x, info_y, info_width)
            info_y += self.normal_font.get_height() + 6

        bar_top = max(portrait.bottom, info_y) + 18
        bar_rect = pygame.Rect(self.character_panel_rect.left + 16, bar_top, self.character_panel_rect.width - 32, 18)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, bar_rect)
        fill_rect = pygame.Rect(bar_rect.left, bar_rect.top, int(bar_rect.width * self.xp_progress(player_char)), bar_rect.height)
        pygame.draw.rect(self.screen, self.colors.GREEN, fill_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, bar_rect, 1)
        level = getattr(player_char, "level", None)
        exp = getattr(level, "exp", 0)
        to_next = getattr(level, "exp_to_gain", 0)
        self._draw_text(f"Level: {exp} earned / {to_next} to next", self.small_font, self.colors.GRAY, bar_rect.left, bar_rect.bottom + 6, bar_rect.width)

        y = bar_rect.bottom + 34
        self._draw_text("Core Attributes", self.normal_font, self.colors.GOLD, self.character_panel_rect.left + 16, y, self.character_panel_rect.width - 32)
        y += self.normal_font.get_height() + 8
        y = self._draw_key_values(self.build_core_attributes(player_char), self.character_panel_rect, y)

        buffs = self.collect_equipment_buffs(player_char)
        if buffs and y < self.character_panel_rect.bottom - 56:
            y += 8
            self._draw_text("Equipment Buffs", self.normal_font, self.colors.GOLD, self.character_panel_rect.left + 16, y, self.character_panel_rect.width - 32)
            y += self.normal_font.get_height() + 6
            for buff in buffs[:3]:
                self._draw_text(buff.name, self.small_font, self.colors.WHITE, self.character_panel_rect.left + 20, y, self.character_panel_rect.width - 40)
                y += self.small_font.get_height() + 4

    def draw_combat_panel(self, player_char):
        y = self._draw_panel(self.combat_panel_rect, "Combat Stats")
        self._draw_key_values(self.build_combat_stats(player_char), self.combat_panel_rect, y)
        groups = self.group_resistances(player_char)
        y = self.combat_panel_rect.bottom - 150
        self._draw_text("Weaknesses", self.normal_font, self.colors.RED, self.combat_panel_rect.left + 16, y, self.combat_panel_rect.width - 32)
        y += self.normal_font.get_height() + 4
        y = self._draw_resistance_group(groups["weaknesses"], self.combat_panel_rect, y, self.colors.RED)
        y += 8
        self._draw_text("Resistances", self.normal_font, self.colors.GREEN, self.combat_panel_rect.left + 16, y, self.combat_panel_rect.width - 32)
        y += self.normal_font.get_height() + 4
        self._draw_resistance_group(groups["resistances"], self.combat_panel_rect, y, self.colors.GREEN)

    def _draw_key_values(self, rows: list[tuple[str, str]], rect: pygame.Rect, y: int) -> int:
        label_width = min(160, max((self.normal_font.size(label)[0] for label, _ in rows), default=80) + 8)
        x = rect.left + 16
        value_x = x + label_width
        max_value_width = rect.right - value_x - 16
        for label, value in rows:
            self._draw_text(label, self.normal_font, self.colors.GRAY, x, y, label_width - 8)
            self._draw_text(value, self.normal_font, self.colors.WHITE, value_x, y, max_value_width)
            y += self.normal_font.get_height() + 8
            if y > rect.bottom - 24:
                break
        return y

    def _draw_resistance_group(self, entries: list[ResistanceSummary], rect: pygame.Rect, y: int, color) -> int:
        if not entries:
            self._draw_text("None", self.small_font, self.colors.GRAY, rect.left + 20, y, rect.width - 40)
            return y + self.small_font.get_height() + 4
        x = rect.left + 20
        for entry in entries[:4]:
            text = f"{entry.name} ({entry.value * 100:+.0f}%)"
            self._draw_text(text, self.small_font, color, x, y, rect.width - 40)
            y += self.small_font.get_height() + 4
        return y

    def draw_equipment_tab(self, player_char):
        y = self._draw_panel(self.details_rect, "Equipment")
        left = pygame.Rect(self.details_rect.left + 16, y, self.details_rect.width // 2 - 24, self.details_rect.bottom - y - 16)
        right = pygame.Rect(left.right + 16, y, self.details_rect.right - left.right - 32, left.height)
        self._draw_text("Equipped Items", self.normal_font, self.colors.GOLD, left.left, left.top, left.width)
        item_y = left.top + self.normal_font.get_height() + 10
        for slot in self.build_equipment_slots(player_char):
            color = self.colors.GRAY if not slot.implemented else self.colors.WHITE
            self._draw_text(slot.slot, self.small_font, self.colors.GRAY, left.left, item_y, left.width)
            self._draw_text(slot.item_name, self.normal_font, color, left.left + 110, item_y - 2, left.width - 110)
            if slot.bonus:
                item_y += self.normal_font.get_height() + 2
                self._draw_text(slot.bonus, self.small_font, self.colors.GRAY, left.left + 110, item_y, left.width - 110)
            item_y += self.small_font.get_height() + 12

        self._draw_text("Item Details", self.normal_font, self.colors.GOLD, right.left, right.top, right.width)
        detail_y = right.top + self.normal_font.get_height() + 10
        for slot in self.build_equipment_slots(player_char):
            if detail_y > right.bottom - 70:
                break
            color = self.colors.GRAY if not slot.implemented or slot.item_name == "(empty)" else self.colors.WHITE
            self._draw_text(f"{slot.slot}: {slot.item_name}", self.normal_font, self.colors.GOLD if slot.implemented else self.colors.GRAY, right.left, detail_y, right.width)
            detail_y += self.normal_font.get_height() + 4
            description = slot.description or ("Slot reserved for future helmet equipment." if not slot.implemented else "No item equipped." if slot.item_name == "(empty)" else "No description available.")
            detail_y = self._draw_wrapped_text(description, self.small_font, color, right.left + 12, detail_y, right.width - 12, max_lines=2)
            if slot.bonus:
                self._draw_text(f"Bonuses: {slot.bonus}", self.small_font, self.colors.BLUE, right.left + 12, detail_y, right.width - 12)
                detail_y += self.small_font.get_height() + 4
            detail_y += 8

        buffs = self.collect_equipment_buffs(player_char)
        if buffs:
            self._draw_text("Equipment Buffs", self.normal_font, self.colors.GOLD, right.left, detail_y, right.width)
            detail_y += self.normal_font.get_height() + 8
            for buff in buffs:
                self._draw_text(f"{buff.name}: {buff.source}", self.small_font, self.colors.WHITE, right.left, detail_y, right.width)
                detail_y += self.small_font.get_height() + 8
                if detail_y > right.bottom - 24:
                    break

    def draw_menu(self):
        y = self._draw_panel(self.actions_rect, "Actions")
        x = self.actions_rect.left + 16
        option_width = max(130, (self.actions_rect.width - 32) // max(1, len(self.menu_options)))
        for index, option in enumerate(self.menu_options):
            rect = pygame.Rect(x + (index * option_width), y, option_width - 8, self.actions_rect.bottom - y - 12)
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
        elif chosen == "Change Equipment":
            popup = EquipmentPopupMenu(self.presenter, self)
            _ = popup.show(player_char, flush_events=True, require_key_release=True)
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
        return ["Inventory", "Change Equipment", "Quests", "Key Items", "Specials", "Exit Menu"]

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
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue
                if event.type != pygame.KEYDOWN:
                    continue

                if event.key == pygame.K_ESCAPE:
                    return "Exit Menu"
                if event.key in (pygame.K_TAB, pygame.K_RIGHT):
                    self.move_tab(1)
                elif event.key == pygame.K_LEFT:
                    self.move_tab(-1)
                elif event.key == pygame.K_1:
                    self.select_tab("character")
                elif event.key == pygame.K_2:
                    self.select_tab("equipment")
                elif event.key == pygame.K_UP:
                    self.current_selection = (self.current_selection - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.current_selection = (self.current_selection + 1) % len(self.menu_options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    result = self._open_menu_choice(self.menu_options[self.current_selection], player_char)
                    if result:
                        return result

            self.presenter.clock.tick(30)
