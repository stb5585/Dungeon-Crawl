"""
Promotion selection screen with the updated town aesthetic.
Shows detailed class previews, stat changes, equipment, and restrictions.
"""

import textwrap

import pygame

from .confirmation_popup import ConfirmationPopup
from .town_base import TownScreenBase


class PromotionScreen(TownScreenBase):
    """Promotion selection UI styled like the other town menus."""

    def __init__(self, presenter, player_char, options, option_map, current_class, pro_level):
        super().__init__(presenter)
        self.player_char = player_char
        self.options = list(options) + ["Go Back"]
        self.option_map = option_map
        self.current_class = current_class
        self.pro_level = pro_level
        self.current_selection = 0

        self.container_rect = self._build_container_rect()
        self.options_width = 240

    def _build_container_rect(self):
        width = int(self.width * 0.92)
        height = int(self.height * 0.76)
        x = (self.width - width) // 2
        y = int(self.height * 0.14)
        return pygame.Rect(x, y, width, height)

    def _wrap_lines(self, text, width):
        lines = []
        for paragraph in text.splitlines():
            if not paragraph.strip():
                lines.append("")
                continue
            lines.extend(textwrap.wrap(paragraph, width, break_on_hyphens=False))
        return lines

    def _format_offhand(self, item):
        if not item:
            return "None"
        subtype = getattr(item, "subtyp", "")
        if subtype == "Shield":
            return f"{item.name} ({int(getattr(item, 'mod', 0) * 100)}%)"
        if subtype in ["Tome", "Rod"]:
            return f"{item.name} (+{int(getattr(item, 'mod', 0))})"
        return item.name

    def _stat_pairs(self, cls_instance):
        pc = self.player_char
        return [
            (("Strength", pc.stats.strength + cls_instance.str_plus, cls_instance.str_plus),
             ("Health", pc.health.max + (cls_instance.con_plus * 2), cls_instance.con_plus * 2)),
            (("Intelligence", pc.stats.intel + cls_instance.int_plus, cls_instance.int_plus),
             ("Mana", pc.mana.max + (cls_instance.int_plus * 2), cls_instance.int_plus * 2)),
            (("Wisdom", pc.stats.wisdom + cls_instance.wis_plus, cls_instance.wis_plus),
             ("Attack", pc.combat.attack + cls_instance.att_plus, cls_instance.att_plus)),
            (("Constitution", pc.stats.con + cls_instance.con_plus, cls_instance.con_plus),
             ("Defense", pc.combat.defense + cls_instance.def_plus, cls_instance.def_plus)),
            (("Charisma", pc.stats.charisma + cls_instance.cha_plus, cls_instance.cha_plus),
             ("Magic", pc.combat.magic + cls_instance.magic_plus, cls_instance.magic_plus)),
            (("Dexterity", pc.stats.dex + cls_instance.dex_plus, cls_instance.dex_plus),
             ("Magic Defense", pc.combat.magic_def + cls_instance.magic_def_plus, cls_instance.magic_def_plus)),
        ]

    def _draw_header(self):
        top_rect = pygame.Rect(0, 0, self.width, self.height // 12)
        self.draw_semi_transparent_panel(top_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, top_rect, 2)

        title = self.normal_font.render("Church of Elysia - Promotion", True, self.colors.GOLD)
        title_rect = title.get_rect(center=(self.width // 2, top_rect.centery - 12))
        self.screen.blit(title, title_rect)

        tier_label = {1: "First Promotion", 2: "Second Promotion"}.get(self.pro_level, "Final Promotion")
        subtext = self.small_font.render(f"Current Class: {self.current_class}  •  {tier_label}", True, self.colors.WHITE)
        sub_rect = subtext.get_rect(center=(self.width // 2, top_rect.centery + 12))
        self.screen.blit(subtext, sub_rect)

    def _draw_options_panel(self):
        options_rect = pygame.Rect(
            self.container_rect.right - self.options_width - 20,
            self.container_rect.top + 20,
            self.options_width,
            self.container_rect.height - 40,
        )
        self.draw_semi_transparent_panel(options_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, options_rect, 2)

        header = self.normal_font.render("Choose your path", True, self.colors.GOLD)
        header_rect = header.get_rect(centerx=options_rect.centerx, top=options_rect.top + 20)
        self.screen.blit(header, header_rect)

        line_height = self.normal_font.get_height() + 12
        start_y = options_rect.centery - (line_height * len(self.options) // 2)

        for idx, option in enumerate(self.options):
            y = start_y + idx * line_height
            highlight_rect = pygame.Rect(
                options_rect.left + 12,
                y - 6,
                options_rect.width - 24,
                line_height,
            )
            if idx == self.current_selection:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, highlight_rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, highlight_rect, 2)
                color = self.colors.GOLD
            else:
                color = self.colors.WHITE

            text = self.normal_font.render(option, True, color)
            text_rect = text.get_rect(centerx=options_rect.centerx, centery=y + (line_height // 2) - 6)
            self.screen.blit(text, text_rect)

    def _draw_detail_panel(self, cls_ctor):
        cls_instance = cls_ctor()
        left_rect = pygame.Rect(
            self.container_rect.left + 20,
            self.container_rect.top + 20,
            self.container_rect.width - self.options_width - 60,
            self.container_rect.height - 40,
        )
        self.draw_semi_transparent_panel(left_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, left_rect, 2)

        y = left_rect.top + 14

        name_text = self.large_font.render(cls_instance.name, True, self.colors.GOLD)
        name_rect = name_text.get_rect(centerx=left_rect.centerx, top=y)
        self.screen.blit(name_text, name_rect)
        y = name_rect.bottom + 8

        desc_lines = self._wrap_lines(cls_instance.description, 88)
        max_desc_lines = 7
        line_height = self.normal_font.get_height() + 4
        desc_start_y = y
        for line in desc_lines[:max_desc_lines]:
            text = self.normal_font.render(line, True, self.colors.WHITE)
            self.screen.blit(text, (left_rect.left + 18, y))
            y += line_height

        # Reserve a fixed block for descriptions so lower sections stay aligned
        y = desc_start_y + (line_height * max_desc_lines) + 8

        stats_header = self.normal_font.render("Promotion Stats", True, self.colors.GOLD)
        self.screen.blit(stats_header, (left_rect.left + 18, y))
        y = stats_header.get_height() + y + 6

        stat_pairs = self._stat_pairs(cls_instance)
        line_height = self.small_font.get_height() + 6
        col1_x = left_rect.left + 24
        col2_x = left_rect.left + (left_rect.width // 2) + 10
        for left, right in stat_pairs:
            l_label, l_val, l_bonus = left
            r_label, r_val, r_bonus = right
            left_line = f"{l_label}: {l_val} (+{l_bonus})"
            right_line = f"{r_label}: {r_val} (+{r_bonus})"
            l_text = self.small_font.render(left_line, True, self.colors.WHITE)
            r_text = self.small_font.render(right_line, True, self.colors.WHITE)
            self.screen.blit(l_text, (col1_x, y))
            self.screen.blit(r_text, (col2_x, y))
            y += line_height

        y += 15
        equip_header = self.normal_font.render("New Equipment", True, self.colors.GOLD)
        self.screen.blit(equip_header, (left_rect.left + 18, y))
        y = equip_header.get_height() + y + 4

        equipment = cls_instance.equipment
        equip_lines = [
            ("Weapon", equipment.get("Weapon")),
            ("OffHand", equipment.get("OffHand")),
            ("Armor", equipment.get("Armor")),
        ]
        for label_text, item in equip_lines:
            item_display = self._format_offhand(item) if label_text == "OffHand" else (item.name if item else "None")
            line = f"{label_text}: {item_display}"
            text = self.small_font.render(line, True, self.colors.WHITE)
            self.screen.blit(text, (left_rect.left + 28, y))
            y += line_height

        y += 20
        rest_header = self.normal_font.render("Equipment Restrictions", True, self.colors.GOLD)
        self.screen.blit(rest_header, (left_rect.left + 18, y))
        y = rest_header.get_height() + y + 4

        for slot, allowed in cls_instance.restrictions.items():
            if not allowed:
                continue
            line = f"{slot}: {', '.join(allowed)}"
            for wrapped in self._wrap_lines(line, 80):
                text = self.small_font.render(wrapped, True, self.colors.WHITE)
                self.screen.blit(text, (left_rect.left + 28, y))
                y += line_height

    def _draw_instructions(self):
        hint = "UP/DOWN: Select   ENTER: Promote   ESC: Cancel"
        text = self.small_font.render(hint, True, self.colors.GRAY)
        rect = text.get_rect(centerx=self.width // 2, bottom=self.height - 16)
        self.screen.blit(text, rect)

    def draw_all(self):
        self.draw_background()
        self._draw_header()

        if self.options:
            selected_name = self.options[self.current_selection]
            cls_ctor = self.option_map.get(selected_name)
            if cls_ctor:
                self._draw_detail_panel(cls_ctor)

        self._draw_options_panel()
        self._draw_instructions()
        pygame.display.flip()

    def navigate(self):
        if not self.options:
            return None

        while True:
            self.draw_all()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_selection = (self.current_selection - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.current_selection = (self.current_selection + 1) % len(self.options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        selected_name = self.options[self.current_selection]
                        if selected_name == "Go Back":
                            return None
                        popup = ConfirmationPopup(
                            self.presenter,
                            f"Promote to {selected_name}?"
                        )
                        if popup.show():
                            return selected_name
                    elif event.key == pygame.K_ESCAPE:
                        return None
            self.presenter.clock.tick(30)
