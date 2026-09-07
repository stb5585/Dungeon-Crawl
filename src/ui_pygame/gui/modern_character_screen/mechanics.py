"""Mechanics behavior for the modern character screen package."""

from __future__ import annotations

import math
from typing import Any

import pygame

from src.core.classes import (
    archdruid,
    astromancer,
    bard,
    demonologist,
    grandmaster,
    lycan,
    nature_totems,
    paladin,
    promotion_kits,
    wizard,
)
from src.ui_pygame.assets.ability_icon_manager import get_ability_icon_manager
import src.ui_pygame.gui.modern_character_screen as character_screen

SCHOOL_AFFINITY_ICON_KEYS = {
    "Fire": "spell_fire",
    "Ice": "spell_ice",
    "Water": "spell_water",
    "Electric": "spell_lightning",
    "Earth": "spell_earth",
    "Wind": "spell_wind",
    "Arcane": "spell_arcane",
}


class CharacterMechanicsMixin:
    def jump_mod_summary_rows(self, player_char) -> list[tuple[str, str]]:
        jump_skill = self._get_jump_skill(player_char)
        if not jump_skill or not hasattr(jump_skill, "modifications"):
            return [("Jump Mods", "Jump not learned")]
        active_count = (
            jump_skill.get_active_count()
            if hasattr(jump_skill, "get_active_count")
            else sum(bool(v) for v in jump_skill.modifications.values())
        )
        max_count = (
            jump_skill.get_max_active_modifications(player_char)
            if hasattr(jump_skill, "get_max_active_modifications")
            else len(jump_skill.modifications)
        )
        unlocked = (
            jump_skill.get_unlocked_modifications()
            if hasattr(jump_skill, "get_unlocked_modifications")
            else list(jump_skill.modifications.keys())
        )
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
        active_count = (
            jump_skill.get_active_count()
            if hasattr(jump_skill, "get_active_count")
            else sum(bool(v) for v in jump_skill.modifications.values())
        )
        max_count = (
            jump_skill.get_max_active_modifications(player_char)
            if hasattr(jump_skill, "get_max_active_modifications")
            else len(jump_skill.modifications)
        )
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
            "Crit": "Increases critical factor but reduces weapon damage.",
            "Thrust": "After landing, thrust with reduced weapon damage if the target survives.",
            "Defend": "Increased damage reduction while preparing to Jump.",
            "Rend": "Chance to apply Bleed, dealing damage over time.",
            "Quake": "Chance to stun the enemy upon landing.",
            "Acrobat": "Gain an evasion bonus while preparing to Jump.",
            "Dragon's Fury": "Deals additional random elemental damage.",
            "Soaring Strike": "Takes two turns to charge, but deals increased damage.",
            "Quick Dive": "Removes charge time but reduces weapon damage.",
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

        jump_skill = self._get_jump_skill(player_char)
        entries = self.jump_mod_entries(player_char)
        self.selected_jump_mod_index = max(
            0,
            min(self.selected_jump_mod_index, max(0, len(entries) - 1)),
        )
        active_count, max_count = self._jump_mod_counts(player_char)

        tempo = promotion_kits.current_aerial_tempo(player_char)
        tempo_cap = promotion_kits.cap_for(player_char, "aerial_tempo")
        summary_rect = pygame.Rect(content.left, content.top, content.width, 76)
        pygame.draw.rect(self.screen, (14, 14, 19), summary_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, summary_rect, 1)
        self._draw_text(
            f"Aerial Tempo: {tempo}/{tempo_cap}",
            self.normal_font,
            self.colors.GOLD,
            summary_rect.left + 12,
            summary_rect.top + 8,
            summary_rect.width - 24,
        )
        self._draw_wrapped_text(
            "Build with clean Jump landings. Your next Sword or Polearm attack "
            "spends all stacks for accuracy and follow-through damage.",
            self.small_font,
            self.colors.WHITE,
            summary_rect.left + 12,
            summary_rect.top + 40,
            summary_rect.width - 24,
            max_lines=2,
        )

        section_top = summary_rect.bottom + 12
        list_width = max(560, (content.width * 2) // 3)
        list_rect = pygame.Rect(
            content.left,
            section_top,
            list_width,
            content.bottom - section_top,
        )
        detail_rect = pygame.Rect(
            list_rect.right + 16,
            section_top + 44,
            content.right - list_rect.right - 16,
            190,
        )

        header = (
            f"Jump Modifications ({active_count}/{max_count} active)"
            if jump_skill
            else "Jump not learned"
        )
        self._draw_text(
            header,
            self.normal_font,
            self.colors.GOLD,
            list_rect.left,
            list_rect.top,
            list_rect.width,
        )
        helper = "UP/DOWN: Select  ENTER: Toggle"
        helper_width = self.small_font.size(helper)[0]
        self._draw_text(
            helper,
            self.small_font,
            self.colors.GRAY,
            list_rect.right - min(helper_width, list_rect.width),
            list_rect.top + self.normal_font.get_height() + 2,
            list_rect.width,
        )

        y_cursor = list_rect.top + self.normal_font.get_height() + self.small_font.get_height() + 10
        columns = 2
        column_gap = 10
        row_gap = 5
        row_width = (list_rect.width - column_gap) // columns
        rows_per_column = max(1, math.ceil(len(entries) / columns))
        available_height = list_rect.bottom - y_cursor
        row_height = min(
            36,
            max(
                26,
                (available_height - (rows_per_column - 1) * row_gap) // rows_per_column,
            ),
        )
        self._jump_mod_row_rects = []
        for index, mod_name in enumerate(entries):
            row = index % rows_per_column
            column = index // rows_per_column
            row_rect = pygame.Rect(
                list_rect.left + column * (row_width + column_gap),
                y_cursor + row * (row_height + row_gap),
                row_width,
                row_height,
            )
            self._jump_mod_row_rects.append(row_rect)
            selected = index == self.selected_jump_mod_index
            active = bool(getattr(jump_skill, "modifications", {}).get(mod_name, False))
            pygame.draw.rect(
                self.screen,
                self.colors.HIGHLIGHT_BG if selected else (14, 14, 19),
                row_rect,
            )
            pygame.draw.rect(
                self.screen,
                self.colors.GOLD if selected else self.colors.BORDER_COLOR,
                row_rect,
                2 if selected else 1,
            )
            marker = "[X]" if active else "[ ]"
            self._draw_text(
                marker,
                self.small_font,
                self.colors.GOLD if active else self.colors.GRAY,
                row_rect.left + 10,
                row_rect.top + 8,
                34,
            )
            self._draw_text(
                mod_name,
                self.small_font,
                self.colors.WHITE,
                row_rect.left + 48,
                row_rect.top + 8,
                row_rect.width - 58,
            )

        pygame.draw.rect(self.screen, (14, 14, 19), detail_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, detail_rect, 1)
        if entries and jump_skill:
            mod_name = entries[self.selected_jump_mod_index]
            active = bool(jump_skill.modifications.get(mod_name, False))
            detail_y = detail_rect.top + 16
            self._draw_text(
                mod_name,
                self.normal_font,
                self.colors.GOLD,
                detail_rect.left + 12,
                detail_y,
                detail_rect.width - 24,
            )
            detail_y += self.normal_font.get_height() + 8
            self._draw_text(
                f"Status: {'Active' if active else 'Inactive'}",
                self.small_font,
                self.colors.WHITE,
                detail_rect.left + 12,
                detail_y,
                detail_rect.width - 24,
            )
            detail_y += self.small_font.get_height() + 6
            self._draw_text(
                self._jump_mod_unlock_text(jump_skill, mod_name),
                self.small_font,
                self.colors.GRAY,
                detail_rect.left + 12,
                detail_y,
                detail_rect.width - 24,
            )
            detail_y += self.small_font.get_height() + 10
            self._draw_wrapped_text(
                self._jump_mod_description(mod_name),
                self.small_font,
                self.colors.WHITE,
                detail_rect.left + 12,
                detail_y,
                detail_rect.width - 24,
                max_lines=4,
            )
        else:
            self._draw_text(
                "Jump has not been learned.",
                self.normal_font,
                self.colors.GRAY,
                detail_rect.left + 12,
                detail_rect.top + 12,
                detail_rect.width - 24,
            )

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

    def _draw_resolve_ability_box(
        self, entry: dict[str, Any], rect: pygame.Rect, *, surge: bool = False
    ) -> None:
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
        if surge:
            learned = bool(entry.get("learned"))
            if learned and not unlocked:
                description = "Discovered through defensive mastery; available after promotion"
            elif not learned:
                title = "Unknown Burst"
                role = "Unrevealed"
                description = "Defensive mastery may reveal a new technique."
        elif not unlocked:
            description = "Locked"
        cost = (
            "Full bar"
            if surge and unlocked
            else (
                "Discovered"
                if surge and bool(entry.get("learned"))
                else "Locked" if surge else f"{int(entry.get('cost', 0) or 0)} Resolve"
            )
        )

        self._draw_text(
            title, self.normal_font, title_color, rect.left + 10, rect.top + 8, rect.width - 20
        )
        self._draw_text(
            f"{role} - {cost}",
            self.small_font,
            text_color,
            rect.left + 10,
            rect.top + 34,
            rect.width - 20,
        )
        self._draw_wrapped_text(
            description,
            self.small_font,
            text_color,
            rect.left + 10,
            rect.top + 56,
            rect.width - 20,
            max_lines=2,
        )

    def _draw_resolve_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        resolve, cap = self._resolve_value_and_cap(player_char)
        content = self.details_rect.inflate(-32, -64)
        content.top = y
        meter_width = min(700, max(360, (content.width * 3) // 4))
        bar_rect = pygame.Rect(content.centerx - meter_width // 2, y + 16, meter_width, 28)
        self._draw_meter_bar(bar_rect, resolve, cap, color=self.colors.RED)
        value_text = f"{resolve}/{cap}"
        value_surface = self.normal_font.render(value_text, True, self.colors.WHITE)
        self.screen.blit(value_surface, value_surface.get_rect(center=bar_rect.center))

        section_y = bar_rect.bottom + 36
        self._draw_text(
            "Resolve Spends",
            self.normal_font,
            self.colors.GOLD,
            content.left,
            section_y,
            content.width,
        )
        box_top = section_y + self.normal_font.get_height() + 14
        columns = 4
        gap = 12
        box_width = (content.width - gap * (columns - 1)) // columns
        box_height = 88
        for index, entry in enumerate(self.resolve_spend_rows(player_char)):
            col = index % columns
            row = index // columns
            rect = pygame.Rect(
                content.left + col * (box_width + gap),
                box_top + row * (box_height + gap),
                box_width,
                box_height,
            )
            self._draw_resolve_ability_box(entry, rect)

        class_name = self._attr_name(getattr(player_char, "cls", None), "")
        if class_name in {"Sentinel", "Stalwart Defender"}:
            surge_y = box_top + 2 * (box_height + gap) + 22
            surge_rows = [
                entry
                for entry in promotion_kits.resolve_surge_rows(player_char)
                if entry.get("learned")
            ]
            heading = "Resolve Bursts" if class_name == "Stalwart Defender" else "Defensive Mastery"
            self._draw_text(
                heading,
                self.normal_font,
                self.colors.GOLD,
                content.left,
                surge_y,
                content.width,
            )
            if not surge_rows:
                self._draw_wrapped_text(
                    "Continued defensive practice may reveal new techniques.",
                    self.small_font,
                    self.colors.GRAY,
                    content.left,
                    surge_y + self.normal_font.get_height() + 14,
                    content.width,
                    max_lines=2,
                )
            for index, entry in enumerate(surge_rows):
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
        right_rect = pygame.Rect(
            left_rect.right + 18, content.top, content.right - left_rect.right - 18, content.height
        )

        self._draw_text(
            f"Conviction {conviction}/{cap}",
            self.large_font,
            self.colors.WHITE,
            left_rect.left,
            y,
            left_rect.width,
        )
        bar_rect = pygame.Rect(
            left_rect.left, y + self.large_font.get_height() + 8, left_rect.width, 16
        )
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
        self._draw_key_values(
            rows, left_rect, bar_rect.bottom + 18, font=self.normal_font, row_gap=8
        )

        detail_y = right_rect.top
        self._draw_text(
            "Oath Rhythm",
            self.normal_font,
            self.colors.GOLD,
            right_rect.left,
            detail_y,
            right_rect.width,
        )
        detail_y += self.normal_font.get_height() + 12
        for title, body in (
            (
                "Build",
                "Use your sworn vow skill and complete its clean payoff to build Conviction.",
            ),
            (
                "Spend",
                "Oath's Judgment and Oath's Shelter consume all stored "
                "Conviction for vow-specific offense or defense.",
            ),
            (
                "Risk",
                "Aura and mark pressure still matter; Conviction reinforces the oath without erasing its drawback.",
            ),
        ):
            if detail_y + 80 > right_rect.bottom:
                break
            detail_y = self._draw_mechanic_note_card(right_rect, title, body, detail_y)

    def _split_mechanic_content(self, y: int) -> tuple[pygame.Rect, pygame.Rect]:
        content = self.details_rect.inflate(-32, -64)
        content.top = y
        left_width = max(320, (content.width * 2) // 5)
        left_rect = pygame.Rect(content.left, content.top, left_width, content.height)
        right_rect = pygame.Rect(
            left_rect.right + 18, content.top, content.right - left_rect.right - 18, content.height
        )
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
        self._draw_text(
            value_text,
            self.small_font,
            self.colors.GRAY,
            rect.left,
            y + self.normal_font.get_height() + 2,
            rect.width,
        )
        bar_rect = pygame.Rect(
            rect.left,
            y + self.normal_font.get_height() + self.small_font.get_height() + 8,
            rect.width,
            12,
        )
        self._draw_meter_bar(bar_rect, int(value), int(cap), color=color or self.colors.GOLD)
        return bar_rect.bottom + 12

    def _ring_state_text(self, player_char, class_name: str) -> str:
        try:
            from src.core.classes import class_rings

            if class_rings.is_awakened(player_char, class_name):
                return (
                    "Awakened, equipped"
                    if class_rings.has_equipped_class_ring(player_char)
                    else "Awakened, unequipped"
                )
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
        from src.core.classes import mage_mechanics

        specialization = mage_mechanics.specialization(player_char)
        schools = (
            ("Arcane",)
            if specialization == "Arcane"
            else ("Fire", "Water", "Earth", "Ice", "Electric", "Wind")
        )

        spells = getattr(player_char, "spellbook", {}).get("Spells", {})
        if schools == ("Arcane",):
            school = "Arcane"
            chain = wizard.SPELL_UPGRADES.get(school, ())
            known = next(
                (name for name in reversed(chain) if name in spells),
                chain[0] if chain else "None",
            )
            icon = get_ability_icon_manager().get_icon(
                SCHOOL_AFFINITY_ICON_KEYS[school],
            )
            self.screen.blit(
                icon,
                icon.get_rect(left=left_rect.left, top=y + 2),
            )
            row_rect = pygame.Rect(
                left_rect.left + 42,
                left_rect.top,
                left_rect.width - 42,
                left_rect.height,
            )
            self._draw_progress_row(
                row_rect,
                school,
                affinity.get(school, 0),
                cap,
                y,
                detail=known,
            )
        else:
            elemental_schools = tuple(schools)
            chart_rect = pygame.Rect(
                self.details_rect.left + 36,
                y + 8,
                self.details_rect.width - 72,
                self.details_rect.bottom - y - 32,
            )
            center = (
                chart_rect.centerx,
                chart_rect.centery,
            )
            radius = min(
                210,
                max(120, (chart_rect.height - 118) // 2),
                max(120, (chart_rect.width - 260) // 2),
            )
            angles = [
                (-math.pi / 2) + (index * math.tau / len(elemental_schools))
                for index in range(len(elemental_schools))
            ]

            def chart_points(scale: float) -> list[tuple[int, int]]:
                return [
                    (
                        round(center[0] + math.cos(angle) * radius * scale),
                        round(center[1] + math.sin(angle) * radius * scale),
                    )
                    for angle in angles
                ]

            for scale in (0.25, 0.50, 0.75, 1.0):
                points = chart_points(scale)
                for index, start in enumerate(points):
                    pygame.draw.line(
                        self.screen,
                        self.colors.GRAY,
                        start,
                        points[(index + 1) % len(points)],
                        1,
                    )
            for endpoint in chart_points(1.0):
                pygame.draw.line(
                    self.screen,
                    self.colors.GRAY,
                    center,
                    endpoint,
                    1,
                )

            affinity_points = []
            for school, angle in zip(elemental_schools, angles):
                scale = max(0.0, min(1.0, float(affinity.get(school, 0)) / cap))
                affinity_points.append(
                    (
                        round(center[0] + math.cos(angle) * radius * scale),
                        round(center[1] + math.sin(angle) * radius * scale),
                    )
                )
            overlay = pygame.Surface(
                (chart_rect.width, chart_rect.height),
                pygame.SRCALPHA,
            )
            local_points = [
                (point[0] - chart_rect.left, point[1] - chart_rect.top) for point in affinity_points
            ]
            pygame.draw.polygon(overlay, (*self.colors.GOLD[:3], 70), local_points)
            pygame.draw.polygon(overlay, self.colors.GOLD, local_points, 2)
            self.screen.blit(overlay, chart_rect.topleft)

            for school, angle in zip(elemental_schools, angles):
                label_radius = radius + (30 if abs(math.sin(angle)) > 0.8 else 48)
                anchor_x = round(center[0] + math.cos(angle) * label_radius)
                anchor_y = round(center[1] + math.sin(angle) * label_radius)
                icon = get_ability_icon_manager().get_icon(
                    SCHOOL_AFFINITY_ICON_KEYS[school],
                )
                icon_rect = icon.get_rect(center=(anchor_x, anchor_y - 12))
                self.screen.blit(icon, icon_rect)
                label_width = 150
                label_x = max(
                    chart_rect.left,
                    min(
                        chart_rect.right - label_width,
                        anchor_x - label_width // 2,
                    ),
                )
                self._draw_text(
                    f"{affinity.get(school, 0):g}/{cap:g}",
                    self.small_font,
                    self.colors.GRAY,
                    label_x,
                    anchor_y + 8,
                    label_width,
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

        row_y = self._draw_progress_row(
            left_rect,
            "Bargain Taint",
            corruption,
            100,
            y,
            detail=f"Tier {demonologist.corruption_tier(player_char)}",
            color=self.colors.RED,
        )
        rows = [
            ("Crypt", "Unlocked" if state.get("crypt_unlocked") else "Hidden"),
            ("Active Patron", patron),
            ("Patron Mood", str(mood)),
            ("Unlocked", ", ".join(unlocked) if unlocked else "None"),
            ("Echo", str(echo.get("name") or echo.get("spec") or "None")),
            (
                "Ring",
                (
                    "Awakened"
                    if state.get("ring_awakened")
                    else self._ring_state_text(player_char, "Demonologist")
                ),
            ),
        ]
        self._draw_key_values(rows, left_rect, row_y, font=self.normal_font, row_gap=8)

        self._draw_text(
            "Recent Contracts",
            self.normal_font,
            self.colors.GOLD,
            right_rect.left,
            y,
            right_rect.width,
        )
        history_y = y + self.normal_font.get_height() + 12
        history = list(state.get("contract_history", []))[-5:]
        if not history:
            self._draw_text(
                "No contract history",
                self.normal_font,
                self.colors.GRAY,
                right_rect.left,
                history_y,
                right_rect.width,
            )
            return
        for entry in reversed(history):
            patron_text = str(entry.get("patron") or "?")
            intent_text = str(entry.get("intent") or "?")
            self._draw_text(
                f"{patron_text} - {intent_text}",
                self.normal_font,
                self.colors.WHITE,
                right_rect.left,
                history_y,
                right_rect.width,
            )
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
        active = (
            astromancer.active_constellation(player_char) if class_name == "Astromancer" else ""
        )

        row_y = y
        if active:
            self._draw_text(
                f"Active Constellation: {active}",
                self.normal_font,
                self.colors.GOLD,
                left_rect.left,
                y,
                left_rect.width,
            )
            row_y += self.normal_font.get_height() + 14
        for sign in astromancer.CONSTELLATIONS:
            count = int(state["runes"].get(sign, 0) or 0)
            element = astromancer.SIGN_TO_ELEMENT.get(sign, "")
            detail = f"{element}"
            if sign == active and astromancer.is_astromancer(player_char):
                detail += " active"
            row_y = self._draw_progress_row(
                left_rect, sign, count, astromancer.RUNE_CAP, row_y, detail=detail
            )

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
        popup = character_screen.TotemAspectsPopupMenu(self.presenter, self, title="Totem Aspects")
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
        active = (
            nature_totems.active_totem_aspect(player_char)
            or getattr(totem_skill, "active_aspect", "")
            or "None"
        )
        if active == "Soul" and class_name != "Soulcatcher":
            active = "None"
        resonance = promotion_kits.totem_resonance(player_char)
        cap = promotion_kits.cap_for(player_char, "totem_resonance")

        row_y = self._draw_progress_row(
            left_rect,
            "Totem Resonance",
            resonance,
            cap,
            y,
            detail="Pulse strength",
            color=self.colors.GREEN,
        )
        rows = [
            ("Active Aspect", str(active)),
            ("Unlocked Aspects", ", ".join(unlocked) if unlocked else "None"),
            ("Spirit Animal", str(getattr(player_char, "spirit_animal", "Not chosen"))),
            (
                "Staff Bond",
                "Aligned" if nature_totems.has_staff_equipped(player_char) else "Unfocused",
            ),
            ("Select", "C/Enter: Totem Aspects"),
        ]
        self._draw_key_values(rows, left_rect, row_y, font=self.normal_font, row_gap=8)

        self._draw_text(
            "Communions", self.normal_font, self.colors.GOLD, right_rect.left, y, right_rect.width
        )
        list_y = y + self.normal_font.get_height() + 12
        aspects = list(nature_totems.ELEMENTAL_ASPECTS)
        if class_name == "Soulcatcher" and "Soul" in unlocked:
            aspects.append("Soul")
        for aspect in aspects:
            spell_name = (
                nature_totems.highest_unlocked_spell_name(player_char, aspect)
                or nature_totems.communion_spell_name(aspect)
                or "None"
            )
            status = (
                "Unlocked"
                if aspect in unlocked
                or spell_name in getattr(player_char, "spellbook", {}).get("Spells", {})
                else "Locked"
            )
            self._draw_text(
                aspect, self.normal_font, self.colors.WHITE, right_rect.left, list_y, 110
            )
            self._draw_text(
                f"{status} - {spell_name}",
                self.small_font,
                self.colors.GRAY,
                right_rect.left + 118,
                list_y + 2,
                right_rect.width - 118,
            )
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
        best_type, best_progress = max(
            journal.items(), key=lambda item: (int(item[1]), item[0]), default=("None", 0)
        )

        rows = [
            ("Best Case", best_type),
            ("Best Rank", promotion_kits.case_rank(best_progress)),
            ("Revelation", "Target-specific in combat"),
        ]
        if class_name == "Seeker":
            rows.extend(
                [
                    ("Wayfinding", "Contextual"),
                    ("Hidden Cache", self._ring_state_text(player_char, "Seeker")),
                ]
            )
        self._draw_key_values(rows, left_rect, y, font=self.normal_font, row_gap=10)

        self._draw_text(
            "Studied Enemy Types",
            self.normal_font,
            self.colors.GOLD,
            right_rect.left,
            y,
            right_rect.width,
        )
        list_y = y + self.normal_font.get_height() + 12
        entries = sorted(journal.items(), key=lambda item: (-int(item[1]), item[0]))
        if not entries:
            self._draw_text(
                "No cases recorded",
                self.normal_font,
                self.colors.GRAY,
                right_rect.left,
                list_y,
                right_rect.width,
            )
            return
        for enemy_type, progress in entries[:8]:
            detail = promotion_kits.case_rank(progress)
            self._draw_text(
                str(enemy_type), self.normal_font, self.colors.WHITE, right_rect.left, list_y, 150
            )
            self._draw_text(
                detail,
                self.small_font,
                self.colors.GRAY,
                right_rect.left + 158,
                list_y + 2,
                right_rect.width - 158,
            )
            list_y += self.normal_font.get_height() + 12
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

        row_y = self._draw_progress_row(
            left_rect,
            "Crescendo",
            crescendo,
            promotion_kits.cap_for(player_char, "crescendo"),
            y,
            detail="Coda",
            color=self.colors.GOLD,
        )
        rows = [
            ("Combat Song", str(song_state.get("active") or "None")),
            ("Song Turns", str(song_state.get("turns", 0))),
            ("Exploration Song", str(exploration.get("active") or "None")),
            ("Exploration Steps", str(exploration.get("steps", 0))),
            ("Route Coda", str(exploration.get("route_effect") or "None")),
        ]
        if class_name == "Troubadour":
            rows.extend(
                [
                    (
                        "Encore",
                        str(
                            song_state.get("encore")
                            or self._ring_state_text(player_char, "Troubadour")
                        ),
                    ),
                    ("Mastered", f"{mastered}/{len(repertoire)}"),
                ]
            )
        self._draw_key_values(rows, left_rect, row_y, font=self.normal_font, row_gap=8)

        available = bard.available_compositions(player_char)
        equipped_song = next(iter(available), "None")
        if class_name != "Troubadour":
            self._draw_text(
                "Composition",
                self.normal_font,
                self.colors.GOLD,
                right_rect.left,
                y,
                right_rect.width,
            )
            self._draw_key_values(
                [
                    ("Instrument Match", equipped_song),
                    ("Compose", "C/Enter: choose song"),
                ],
                right_rect,
                y + self.normal_font.get_height() + 12,
                font=self.normal_font,
                row_gap=10,
            )
            return

        self._draw_text(
            "Advanced Repertoire",
            self.normal_font,
            self.colors.GOLD,
            right_rect.left,
            y,
            right_rect.width,
        )
        list_y = y + self.normal_font.get_height() + 12
        self._draw_text(
            f"Compose: C/Enter ({equipped_song})",
            self.small_font,
            self.colors.GRAY,
            right_rect.left,
            list_y,
            right_rect.width,
        )
        list_y += self.small_font.get_height() + 8
        for song, entry in repertoire.items():
            known = "Mastered" if entry.get("known") else "Practice"
            xp = int(entry.get("practice_xp", 0) or 0)
            finishes = int(entry.get("clean_finishes", 0) or 0)
            self._draw_text(
                song, self.normal_font, self.colors.WHITE, right_rect.left, list_y, right_rect.width
            )
            if known == "Mastered":
                practice = "Complete"
            else:
                practice = f"{xp}/18 XP, {finishes}/3 finishes"
            self._draw_text(
                f"{known} - {practice}",
                self.small_font,
                self.colors.GRAY,
                right_rect.left,
                list_y + self.normal_font.get_height() + 2,
                right_rect.width,
            )
            list_y += self.normal_font.get_height() + self.small_font.get_height() + 12
            if list_y > right_rect.bottom - 24:
                break

    def _open_composition_popup(self, player_char) -> None:
        popup = character_screen.CompositionPopupMenu(
            self.presenter,
            self,
            title="Compose Song",
        )
        popup.show(player_char=player_char, flush_events=True)

    def _draw_forms_tab(self, player_char, y: int) -> None:
        self.class_companion_selector_active = False
        self.weapon_discipline_selector_active = False
        self._jump_mod_row_rects = []
        left_rect, right_rect = self._split_mechanic_content(y)
        from src.core.classes import transformation

        class_name = transformation.permanent_class_name(player_char)
        shifted = transformation.is_transformed(player_char)
        transform_state = getattr(player_char, "transformation_state", {}) or {}
        active_form = str(transform_state.get("active_form") or "None")
        available = getattr(player_char, "available_transform_forms", None)
        forms = tuple(
            available() if callable(available) else transformation.available_forms(player_char)
        )
        rows = [
            ("Current Form", active_form if shifted else "Humanoid"),
            ("Stored Form", class_name or "Unknown"),
            ("Unlocked Forms", ", ".join(forms) if forms else "None"),
            ("Transform", "Available" if forms and not shifted else "Unavailable"),
            ("Dismiss", "Available" if shifted else "Unavailable"),
        ]
        if class_name == "Lycan":
            rows.append(("Ring", self._ring_state_text(player_char, "Lycan")))
        self._draw_key_values(rows, left_rect, y, font=self.normal_font, row_gap=10)

        self._form_action_rects = []
        labels = ("Dismiss Form",) if shifted else forms
        button_y = left_rect.bottom - 48
        button_width = max(
            120,
            (left_rect.width - 12 * max(0, len(labels) - 1)) // max(1, len(labels)),
        )
        for index, label in enumerate(labels):
            rect = pygame.Rect(
                left_rect.left + index * (button_width + 12),
                button_y,
                button_width,
                38,
            )
            pygame.draw.rect(self.screen, self.colors.GOLD, rect, border_radius=6)
            pygame.draw.rect(self.screen, self.colors.WHITE, rect, width=2, border_radius=6)
            text = self.small_font.render(label, True, self.colors.BLACK)
            self.screen.blit(text, text.get_rect(center=rect.center))
            self._form_action_rects.append((label, rect))

        if class_name == "Lycan":
            lycan_state = lycan.ensure_state(player_char)
            control = promotion_kits.lycan_control_state(player_char)
            list_y = self._draw_progress_row(
                right_rect,
                "Moon Cycle",
                lycan_state.get("moon_steps", 0),
                lycan.STEPS_PER_PHASE,
                y,
                detail=str(lycan_state.get("moon_phase", "New")),
                color=self.colors.GOLD,
            )
            rows = [
                ("Frenzy Lock", f"{int(lycan_state.get('frenzy_turns', 0) or 0)} turn(s)"),
                ("Control Rank", str(control.get("rank", "Feral"))),
                ("Stress Records", str(control.get("stress_events", 0))),
                (
                    "Dragon Essence",
                    (
                        "Yes"
                        if control.get("dragon_essence") or lycan_state.get("dragon_essence")
                        else "No"
                    ),
                ),
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
            row_y = self._draw_progress_row(
                left_rect,
                affinity,
                attunement,
                archdruid.MASTERY_THRESHOLD,
                row_y,
                detail=status,
                color=self.colors.GREEN,
            )
            if row_y > left_rect.bottom - 40:
                break

        harmony_text = ", ".join(sorted(harmony)) if harmony else "None"
        rows = [
            ("Grove", "Unlocked" if state.get("grove_unlocked") else "Hidden"),
            ("Aspect Harmony", harmony_text),
            ("Fourfold Surge", "Ready" if len(harmony) >= 2 else "Building"),
            (
                "Ring",
                (
                    "Awakened"
                    if state.get("ring_awakened")
                    else self._ring_state_text(player_char, "Archdruid")
                ),
            ),
        ]
        self._draw_key_values(rows, right_rect, y, font=self.normal_font, row_gap=8)
        detail_y = y + self.normal_font.get_height() * 6 + 64
        self._draw_text(
            "Catalyst Progress",
            self.normal_font,
            self.colors.GOLD,
            right_rect.left,
            detail_y,
            right_rect.width,
        )
        detail_y += self.normal_font.get_height() + 10
        for affinity in archdruid.AFFINITIES:
            progress = state["progress"].get(affinity, {})
            text = (
                "Stirring" if any(int(value or 0) > 0 for value in progress.values()) else "Quiet"
            )
            self._draw_text(
                affinity, self.small_font, self.colors.GRAY, right_rect.left, detail_y, 90
            )
            self._draw_text(
                text,
                self.small_font,
                self.colors.WHITE,
                right_rect.left + 96,
                detail_y,
                right_rect.width - 96,
            )
            detail_y += self.small_font.get_height() + 8
            if detail_y > right_rect.bottom - 12:
                break

    def draw_class_tab(self, player_char):
        mechanic_tab = self.class_mechanic_tab(player_char)
        panel_title = mechanic_tab.label if mechanic_tab is not None else "Class"
        if mechanic_tab is not None and mechanic_tab.label == "Resolve":
            panel_title = None
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
            overview_y = self._draw_favored_enemy_progress_panel(
                player_char, overview_rect, overview_y
            )

        entries = self.class_companion_entries(player_char)
        if not entries:
            self.class_companion_selector_active = False
            self._class_roster_rect = roster_rect
            if class_name in {"Ranger", "Beast Master"}:
                self._draw_text(
                    "Companion",
                    self.normal_font,
                    self.colors.GOLD,
                    roster_rect.left,
                    y,
                    roster_rect.width,
                )
                self._draw_empty_companion_slot()
            return

        self.selected_class_companion_index = max(
            0,
            min(self.selected_class_companion_index, max(0, len(entries) - 1)),
        )
        self._class_roster_rect = roster_rect
        heading = (
            "Companion"
            if class_name in {"Ranger", "Beast Master"}
            else mechanic_tab.label if mechanic_tab is not None else "Companions"
        )
        self._draw_text(
            heading, self.normal_font, self.colors.GOLD, roster_rect.left, y, roster_rect.width
        )
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
            if has_tamed_roster and class_name in {"Ranger", "Beast Master"}:
                helper = "Enter: Inspect  R: Release  C/Esc: Back"
            elif has_tamed_roster:
                helper = "Arrows: Select  Enter: Inspect  S: Lead  R: Release  C/Esc: Back"
            else:
                helper = "Arrows: Select  Enter: Inspect  C/Esc: Back"
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
