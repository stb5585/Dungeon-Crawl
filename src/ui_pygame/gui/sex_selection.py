"""Character creation screen for sex selection."""

from __future__ import annotations

import pygame

from .input_guards import prepare_guarded_input, release_guard_allows_input, update_input_armed_from_event
from .town_base import TownColors


SEX_OPTIONS = ("Male", "Female")


class SexSelectionScreen:
    """Small guarded selection screen for choosing character sex."""

    def __init__(self, presenter):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.colors = TownColors
        self.title_font = presenter.title_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        self.current_selection = 0

    def draw(self, options: tuple[str, ...] = SEX_OPTIONS) -> None:
        self.screen.fill(self.colors.BLACK)

        panel_width = min(520, self.width - 80)
        panel_height = min(360, self.height - 80)
        panel = pygame.Rect(0, 0, panel_width, panel_height)
        panel.center = (self.width // 2, self.height // 2)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, self.colors.GOLD, panel, 3)

        title = self.title_font.render("Select Character Sex", True, self.colors.GOLD)
        title_rect = title.get_rect(centerx=panel.centerx, top=panel.top + 28)
        self.screen.blit(title, title_rect)

        y = panel.top + 120
        line_height = 58
        for index, option in enumerate(options):
            option_rect = pygame.Rect(panel.left + 50, y + index * line_height, panel.width - 100, line_height - 10)
            if index == self.current_selection:
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, option_rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, option_rect, 2)
                color = self.colors.GOLD
            else:
                color = self.colors.WHITE
            text = self.normal_font.render(option, True, color)
            text_rect = text.get_rect(center=option_rect.center)
            self.screen.blit(text, text_rect)

        instructions = self.small_font.render("UP/DOWN: Navigate   ENTER: Select   ESC: Back", True, self.colors.GRAY)
        instructions_rect = instructions.get_rect(centerx=panel.centerx, bottom=panel.bottom - 24)
        self.screen.blit(instructions, instructions_rect)

    def navigate(
        self,
        options: tuple[str, ...] = SEX_OPTIONS,
        flush_events: bool = False,
        require_key_release: bool = False,
    ) -> str | None:
        """Return selected sex label, or None when cancelled."""
        input_armed = prepare_guarded_input(
            flush_events=flush_events,
            require_key_release=require_key_release,
        )

        while True:
            self.draw(options)
            pygame.display.flip()

            input_armed = release_guard_allows_input(require_key_release, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

                input_armed = update_input_armed_from_event(event, require_key_release, input_armed)
                if event.type != pygame.KEYDOWN or not input_armed:
                    continue
                if event.key == pygame.K_UP:
                    self.current_selection = (self.current_selection - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    self.current_selection = (self.current_selection + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return options[self.current_selection]
                elif event.key == pygame.K_ESCAPE:
                    return None

            self.presenter.clock.tick(30)
