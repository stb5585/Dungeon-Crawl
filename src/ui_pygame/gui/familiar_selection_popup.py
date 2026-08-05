"""Artwork-backed familiar selection for Warlock promotion."""

import pygame

from src.ui_pygame.assets.companion_art_manager import (
    get_companion_art_manager,
)

from .popup_menus.base import BasePopupMenu


class FamiliarSelectionPopup(BasePopupMenu):
    """Choose a familiar while showing its artwork, role, and abilities."""

    def __init__(self, presenter, parent_screen, familiar_types):
        super().__init__(presenter, parent_screen, title="Choose a Familiar")
        self.familiar_types = tuple(familiar_types)
        self.companion_art_manager = get_companion_art_manager()

    def build_items(self, player_char):
        del player_char
        self.items = [familiar_type() for familiar_type in self.familiar_types]

    def item_display_text(self, item):
        return str(getattr(item, "race", "Familiar"))

    def draw_details(self, player_char):
        del player_char
        familiar = self.items[self.selected_index] if self.items else None
        if familiar is None:
            return
        x = self.details_rect.left + 16
        y = self.details_rect.top + 12
        art_rect = pygame.Rect(0, 0, 150, 150)
        art_rect.midtop = (self.details_rect.centerx, y)
        sprite = self.companion_art_manager.get_scaled_sprite(
            familiar,
            art_rect.size,
        )
        self.screen.blit(sprite, art_rect)
        y = art_rect.bottom + 10

        race = str(getattr(familiar, "race", "Familiar"))
        spec = str(getattr(familiar, "spec", "General"))
        self.screen.blit(self.large_font.render(race, True, self.GOLD), (x, y))
        y += self.large_font.get_height() + 4
        self.screen.blit(
            self.normal_font.render(f"{spec} specialist", True, self.LIGHT_GRAY),
            (x, y),
        )
        y += self.line_height + 4
        abilities = [
            *getattr(familiar, "spellbook", {}).get("Skills", {}),
            *getattr(familiar, "spellbook", {}).get("Spells", {}),
        ]
        y = self._draw_wrapped_lines(
            f"Abilities: {', '.join(abilities) or 'None'}",
            x,
            y,
            self.details_rect.width - 32,
        )
        self._draw_wrapped_lines(
            familiar.inspect(),
            x,
            y + 4,
            self.details_rect.width - 32,
            color=self.LIGHT_GRAY,
        )

    def on_select(self, player_char, item):
        del player_char
        return item
