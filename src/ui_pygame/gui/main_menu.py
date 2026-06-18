"""
Main menu screen for Pygame GUI - matches curses terminal layout.
"""

from pathlib import Path

import pygame

from .input_guards import prepare_guarded_input, release_guard_allows_input, update_input_armed_from_event


class MainMenuScreen:
    """
    Main menu that matches the curses terminal style.
    """

    BACKGROUND_PATH = Path(__file__).resolve().parents[1] / "assets" / "backgrounds" / "main_menu.png"
    
    def __init__(self, presenter):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        
        # Fonts
        self.title_font = presenter.title_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        self.background = self._load_background()
        
        self.current_option = 0
        self.options = []

    def _load_background(self):
        """Load the main menu title background if it is available."""
        try:
            return pygame.image.load(str(self.BACKGROUND_PATH))
        except (FileNotFoundError, pygame.error, OSError):
            return None

    def _scale_background(self, image):
        source_width, source_height = image.get_size()
        if source_width <= 0 or source_height <= 0:
            return image, (0, 0)

        scale = max(self.width / source_width, self.height / source_height)
        scaled_size = (int(source_width * scale), int(source_height * scale))
        scaled = pygame.transform.smoothscale(image, scaled_size)
        offset = ((self.width - scaled_size[0]) // 2, (self.height - scaled_size[1]) // 2)
        return scaled, offset

    def draw_background(self):
        """Draw the title background, falling back to a flat fill."""
        if self.background is None:
            self.screen.fill(self.BLACK)
            return

        scaled, offset = self._scale_background(self.background)
        self.screen.blit(scaled, offset)
    
    def draw_title(self):
        """Draw a text title only when the title background is unavailable."""
        if self.background is not None:
            return

        title = self.title_font.render("The Forsaken Tenet", True, self.GOLD)
        subtitle = self.normal_font.render("A tale of choice, memory, and the Seventh Principle", True, self.WHITE)
        title_rect = title.get_rect(centerx=self.width // 2, top=max(40, self.height // 5))
        subtitle_rect = subtitle.get_rect(centerx=self.width // 2, top=title_rect.bottom + 16)
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
    
    def draw_menu(self):
        """Draw the menu options."""
        menu_width = min(360, self.width - 80)
        line_height = 40
        menu_height = max(1, len(self.options)) * line_height + 28
        menu_x = self.width // 2 - menu_width // 2
        menu_y = self.height - menu_height - 54

        panel = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))
        self.screen.blit(panel, (menu_x, menu_y))
        pygame.draw.rect(self.screen, (190, 160, 82), (menu_x, menu_y, menu_width, menu_height), 1)
        
        for i, option in enumerate(self.options):
            y = menu_y + 14 + i * line_height
            
            # Highlight selected option
            if i == self.current_option:
                # Draw highlight box around selected option
                text = self.normal_font.render(option, True, self.BLACK)
                text_width = text.get_width()
                text_height = text.get_height()
                
                # White box background
                box_rect = pygame.Rect(
                    self.width // 2 - text_width // 2 - 10,
                    y - 5,
                    text_width + 20,
                    text_height + 10
                )
                pygame.draw.rect(self.screen, self.WHITE, box_rect)
                
                # Black text on white background
                text_rect = text.get_rect(centerx=self.width // 2, top=y)
                self.screen.blit(text, text_rect)
            else:
                # Normal option - white text
                text = self.normal_font.render(option, True, self.WHITE)
                text_rect = text.get_rect(centerx=self.width // 2, top=y)
                self.screen.blit(text, text_rect)
    
    def draw(self):
        """Draw the entire main menu."""
        self.draw_background()
        self.draw_title()
        self.draw_menu()
        pygame.display.flip()
    
    def navigate(
        self,
        options,
        flush_events: bool = False,
        require_key_release: bool = False,
    ):
        """
        Navigate the main menu and return selected option index.
        
        Args:
            options: List of menu option strings
            
        Returns:
            int: Index of selected option, or None if cancelled
        """
        self.options = options

        input_armed = prepare_guarded_input(
            flush_events=flush_events,
            require_key_release=require_key_release,
        )
        
        while True:
            self.draw()
            
            input_armed = release_guard_allows_input(require_key_release, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                input_armed = update_input_armed_from_event(event, require_key_release, input_armed)
                if event.type == pygame.KEYDOWN:
                    if not input_armed:
                        continue
                    if event.key == pygame.K_UP:
                        self.current_option = (self.current_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.current_option = (self.current_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.current_option
                    elif event.key == pygame.K_ESCAPE:
                        return None
            
            self.presenter.clock.tick(30)
