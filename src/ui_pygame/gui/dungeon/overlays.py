from __future__ import annotations

import pygame


class OverlayRenderer:
    """Bottom message log and full-screen damage flash overlays."""

    def __init__(self, presenter):
        self.presenter = presenter
        self._damage_flash_active = False
        self._damage_flash_start = 0
        self._damage_flash_duration = 1
        self._damage_flash_alpha = 0
        self._damage_flash_color = (255, 32, 16)

    @property
    def screen(self) -> pygame.Surface:
        return self.presenter.screen

    def _get_viewport_size(self) -> tuple[int, int]:
        width, height = self.screen.get_size()
        return int(width * 0.65), height

    def trigger_damage_flash(self, duration_ms: int = 700, alpha: int = 255, color=(255, 32, 16)) -> None:
        now = pygame.time.get_ticks()
        self._damage_flash_active = True
        self._damage_flash_start = now
        self._damage_flash_duration = max(1, duration_ms)
        self._damage_flash_alpha = max(0, min(255, alpha))
        self._damage_flash_color = color

    def render_damage_flash(self) -> None:
        if not self._damage_flash_active:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self._damage_flash_start
        if elapsed >= self._damage_flash_duration:
            self._damage_flash_active = False
            return

        factor = 1.0 - (elapsed / self._damage_flash_duration)
        alpha = int(self._damage_flash_alpha * max(0.0, min(1.0, factor)))
        if alpha <= 0:
            self._damage_flash_active = False
            return

        width, height = self.screen.get_size()
        flash_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        flash_surface.fill((*self._damage_flash_color, alpha))
        self.screen.blit(flash_surface, (0, 0))

    def render_vignette(self) -> None:
        """Draw a soft edge vignette over the dungeon viewport."""
        width, height = self._get_viewport_size()
        if width <= 0 or height <= 0:
            return

        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        color = (8, 8, 12)
        min_dim = min(width, height)

        vignette.fill((*color, 8))

        band_specs = (
            (0, max(18, min_dim // 8), 52),
            (10, max(12, min_dim // 11), 34),
            (22, max(8, min_dim // 15), 20),
        )
        for inset, band_width, alpha in band_specs:
            inner_width = max(1, width - (inset * 2))
            inner_height = max(1, height - (inset * 2))
            top = pygame.Rect(inset, inset, inner_width, band_width)
            bottom = pygame.Rect(inset, height - inset - band_width, inner_width, band_width)
            left = pygame.Rect(inset, inset, band_width, inner_height)
            right = pygame.Rect(width - inset - band_width, inset, band_width, inner_height)
            for rect in (top, bottom, left, right):
                pygame.draw.rect(vignette, (*color, alpha), rect)

        corner_size = max(18, min_dim // 7)
        corner_alpha = 58
        for rect in (
            pygame.Rect(0, 0, corner_size, corner_size),
            pygame.Rect(width - corner_size, 0, corner_size, corner_size),
            pygame.Rect(0, height - corner_size, corner_size, corner_size),
            pygame.Rect(width - corner_size, height - corner_size, corner_size, corner_size),
        ):
            pygame.draw.ellipse(vignette, (*color, corner_alpha), rect)

        divider = pygame.Surface((6, height), pygame.SRCALPHA)
        for offset, alpha in ((0, 72), (1, 54), (2, 36), (3, 24), (4, 12)):
            pygame.draw.rect(divider, (6, 6, 10, alpha), pygame.Rect(offset, 0, 1, height))
        self.screen.blit(divider, (width - divider.get_width(), 0))

        self.screen.blit(vignette, (0, 0))

    def render_message_area(self, messages, scroll_offset: int = 0, lines_per_page: int = 4) -> None:
        width, height = self._get_viewport_size()
        msg_height = 100

        msg_surface = pygame.Surface((width, msg_height), pygame.SRCALPHA)
        msg_surface.fill((20, 20, 25, 200))
        self.screen.blit(msg_surface, (0, height - msg_height))

        font = pygame.font.Font(None, 24)
        indicator_font = pygame.font.Font(None, 18)

        y_offset = height - msg_height + 10
        max_scroll = max(0, len(messages) - lines_per_page)
        clamped_offset = max(0, min(scroll_offset, max_scroll))
        visible_messages = messages[clamped_offset:clamped_offset + lines_per_page]

        for message in visible_messages:
            text_surface = font.render(message, True, (220, 220, 220))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 22

        if len(messages) > lines_per_page:
            if clamped_offset > 0:
                up = indicator_font.render("^", True, (210, 210, 210))
                self.screen.blit(up, (width - 22, height - msg_height + 8))
            if clamped_offset < max_scroll:
                down = indicator_font.render("v", True, (210, 210, 210))
                self.screen.blit(down, (width - 22, height - 22))

            hint = indicator_font.render("PgUp/PgDn or Mouse Wheel", True, (170, 170, 170))
            self.screen.blit(hint, (width - hint.get_width() - 30, height - 22))
