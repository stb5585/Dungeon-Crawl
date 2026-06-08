"""Visual character naming screen for the Pygame creation flow."""

from __future__ import annotations

from pathlib import Path
import sys

import pygame

from src.ui_pygame.assets.portrait_manager import PORTRAIT_ROOT, PortraitManager

from .input_guards import prepare_guarded_input, release_guard_allows_input, update_input_armed_from_event
from .town_base import TownColors


PORTRAIT_DIR = PORTRAIT_ROOT
MAX_NAME_LENGTH = 20


class CharacterNamingScreen:
    """Name-entry screen that previews the selected character identity."""

    def __init__(self, presenter, sex: str, race_name: str, class_name: str):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.sex = sex
        self.race_name = race_name
        self.class_name = class_name
        self.colors = TownColors
        self.title_font = presenter.title_font
        self.large_font = presenter.large_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        self.text = ""
        self.portrait_manager = PortraitManager()
        self.portrait = self.load_portrait()
        self.calculate_rects()

    @staticmethod
    def portrait_filename(race_name: str, sex: str) -> str:
        race_key = PortraitManager.normalize_key(race_name, "human")
        sex_key = PortraitManager.normalize_key(sex, "male")
        if sex_key not in {"male", "female"}:
            sex_key = "male"
        return f"{race_key}_{sex_key}.png"

    @property
    def portrait_path(self) -> Path:
        return PORTRAIT_DIR / self.portrait_filename(self.race_name, self.sex)

    def load_portrait(self) -> pygame.Surface:
        return self.portrait_manager.get_portrait(self.race_name, self.sex)

    def calculate_rects(self) -> None:
        header_height = self.height // 12
        self.header_rect = pygame.Rect(0, 0, self.width, header_height)

        margin = max(24, self.width // 32)
        gap = max(20, self.width // 48)
        content_top = self.header_rect.bottom
        content_height = self.height - content_top
        panel_width = (self.width - margin * 2 - gap) // 2
        panel_height = content_height - margin * 2
        self.preview_rect = pygame.Rect(margin, content_top + margin, panel_width, panel_height)
        self.name_rect = pygame.Rect(self.preview_rect.right + gap, content_top + margin, panel_width, panel_height)

    def draw_header(self) -> None:
        pygame.draw.rect(self.screen, self.colors.BLACK, self.header_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.header_rect, 2)
        title = self.normal_font.render("Name your character", True, self.colors.GOLD)
        title_rect = title.get_rect(centerx=self.width // 2, centery=self.header_rect.centery)
        self.screen.blit(title, title_rect)

    def portrait_preview_rect(self) -> pygame.Rect:
        source_width, source_height = (225, 400)
        if self.portrait is not None:
            source_width, source_height = self.portrait.get_size()

        max_width = min(self.preview_rect.width - 48, 280)
        max_height = min(max(120, self.preview_rect.height - 190), 400)
        scale = min(max_width / source_width, max_height / source_height)
        portrait_width = max(1, int(source_width * scale))
        portrait_height = max(1, int(source_height * scale))
        portrait_rect = pygame.Rect(0, 0, portrait_width, portrait_height)
        portrait_rect.centerx = self.preview_rect.centerx
        portrait_rect.top = self.preview_rect.top + 30
        return portrait_rect

    def draw_preview(self) -> None:
        pygame.draw.rect(self.screen, self.colors.BLACK, self.preview_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.preview_rect, 2)

        portrait_rect = self.portrait_preview_rect()
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, portrait_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, portrait_rect, 2)

        if self.portrait is not None:
            fitted = pygame.transform.smoothscale(self.portrait, portrait_rect.size)
            self.screen.blit(fitted, portrait_rect)
            pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, portrait_rect, 2)
        else:
            placeholder = self.small_font.render("Portrait", True, self.colors.GRAY)
            placeholder_rect = placeholder.get_rect(center=portrait_rect.center)
            self.screen.blit(placeholder, placeholder_rect)

        details = (
            ("Sex", self.sex),
            ("Race", self.race_name),
            ("Class", self.class_name),
        )
        y = portrait_rect.bottom + 28
        label_x = self.preview_rect.left + 48
        value_x = self.preview_rect.right - 48
        for label, value in details:
            label_text = self.normal_font.render(label, True, self.colors.GRAY)
            value_text = self.normal_font.render(value, True, self.colors.WHITE)
            self.screen.blit(label_text, (label_x, y))
            value_rect = value_text.get_rect(right=value_x, top=y)
            self.screen.blit(value_text, value_rect)
            y += self.normal_font.get_height() + 16

    def draw_name_entry(self) -> None:
        pygame.draw.rect(self.screen, self.colors.BLACK, self.name_rect)
        pygame.draw.rect(self.screen, self.colors.BORDER_COLOR, self.name_rect, 2)

        x = self.name_rect.left + 42
        title_y = self.name_rect.top + 52
        title = self.title_font.render("Choose a Name", True, self.colors.GOLD)
        self.screen.blit(title, (x, title_y))

        input_width = self.name_rect.width - 84
        input_height = max(64, self.large_font.get_height() + 28)
        input_rect = pygame.Rect(x, title_y + title.get_height() + 42, input_width, input_height)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, input_rect)
        pygame.draw.rect(self.screen, self.colors.GOLD, input_rect, 2)

        display_text = f"{self.text}_" if self.text else "_"
        available_width = input_rect.width - 36
        entry_font = self.large_font
        if entry_font.render(display_text, True, self.colors.WHITE).get_width() > available_width:
            entry_font = self.normal_font
        if entry_font.render(display_text, True, self.colors.WHITE).get_width() > available_width:
            entry_font = self.small_font
        name_surface = entry_font.render(display_text, True, self.colors.WHITE)
        name_rect = name_surface.get_rect(left=input_rect.left + 18, centery=input_rect.centery)
        self.screen.blit(name_surface, name_rect)

        hint = self.small_font.render("ENTER: Confirm   BACKSPACE: Delete   ESC: Back", True, self.colors.GRAY)
        hint_rect = hint.get_rect(left=x, top=input_rect.bottom + 24)
        self.screen.blit(hint, hint_rect)

        current_name = self.text if self.text else "Hero"
        preview = self.normal_font.render(f"Created as {current_name}", True, self.colors.GOLD)
        preview_rect = preview.get_rect(left=x, bottom=self.name_rect.bottom - 46)
        self.screen.blit(preview, preview_rect)

    def draw(self) -> None:
        self.screen.fill(self.colors.BLACK)
        self.draw_header()
        self.draw_preview()
        self.draw_name_entry()

    def navigate(
        self,
        default: str = "Hero",
        flush_events: bool = False,
        require_key_release: bool = False,
    ) -> str | None:
        input_armed = prepare_guarded_input(
            flush_events=flush_events,
            require_key_release=require_key_release,
        )

        while True:
            self.draw()
            pygame.display.flip()

            input_armed = release_guard_allows_input(require_key_release, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                input_armed = update_input_armed_from_event(event, require_key_release, input_armed)
                if event.type != pygame.KEYDOWN or not input_armed:
                    continue
                if event.key == pygame.K_RETURN:
                    return self.text.strip() or default
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    continue
                text_input = getattr(event, "unicode", "")
                if text_input and text_input.isprintable() and len(self.text) < MAX_NAME_LENGTH:
                    self.text += text_input

            self.presenter.clock.tick(30)
