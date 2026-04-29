"""
Stat selection popup for level up screens.
Displays a popup menu for selecting which stat to increase.
"""

import pygame


class StatSelectionPopup:
    """
    A stat selection popup that appears over the current screen.
    Allows player to select which stat to increase during level up.
    """
    
    def __init__(self, presenter, stat_options):
        """
        Initialize the stat selection popup.
        
        Args:
            presenter: The pygame presenter with screen and fonts
            stat_options: List of tuples (stat_name, current_value)
        """
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.stat_options = stat_options
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (218, 165, 32)  # Warm gold
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        self.POPUP_BG = (20, 20, 30)
        self.GAIN_COLOR = (100, 255, 100)
        
        # Fonts
        self.title_font = presenter.title_font if hasattr(presenter, 'title_font') else pygame.font.Font(None, 48)
        self.normal_font = presenter.normal_font if hasattr(presenter, 'normal_font') else pygame.font.Font(None, 32)
        self.small_font = presenter.small_font if hasattr(presenter, 'small_font') else pygame.font.Font(None, 24)
        
        # State
        self.current_selection = 0
        self.result = None
        
        # Calculate popup position and size
        self.popup_width = 500
        self.popup_height = 100 + len(stat_options) * 50
        self.popup_x = (self.width - self.popup_width) // 2
        self.popup_y = (self.height - self.popup_height) // 2
        self.popup_rect = pygame.Rect(self.popup_x, self.popup_y, self.popup_width, self.popup_height)
    
    def show(self, background_draw_func=None, flush_events: bool = False, require_key_release: bool = False):
        """
        Display the stat selection popup and handle user input.
        
        Args:
            background_draw_func: Optional function to draw the background
        
        Returns:
            The name of the selected stat
        """
        if flush_events:
            pygame.event.clear()

        self.result = None
        selecting = True
        input_armed = not require_key_release

        if background_draw_func is None:
            background = self._get_background_surface()
            background_draw_func = lambda: self.screen.blit(background, (0, 0))
        
        while selecting:
            # Draw background if provided
            if background_draw_func:
                background_draw_func()
            
            # Draw popup
            self.draw_popup()
            
            pygame.display.flip()
            
            # Handle input
            if require_key_release and not input_armed:
                if not any(pygame.key.get_pressed()):
                    input_armed = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selecting = False
                elif event.type == pygame.KEYDOWN:
                    if not input_armed:
                        continue
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.current_selection = (self.current_selection - 1) % len(self.stat_options)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.current_selection = (self.current_selection + 1) % len(self.stat_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.result = self.stat_options[self.current_selection][0]
                        selecting = False
            
            self.presenter.clock.tick(30)
        
        return self.result

    def _get_background_surface(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()
    
    def draw_popup(self):
        """Draw the stat selection popup over the current screen."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(self.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(self.screen, self.POPUP_BG, self.popup_rect)
        pygame.draw.rect(self.screen, self.GOLD, self.popup_rect, 3)
        
        # Draw title
        title_text = self.title_font.render("Choose Stat to Increase", True, self.GOLD)
        title_rect = title_text.get_rect(center=(self.popup_rect.centerx, self.popup_rect.top + 25))
        self.screen.blit(title_text, title_rect)
        
        # Draw stat options
        y = self.popup_rect.top + 70
        for i, (stat_name, stat_value) in enumerate(self.stat_options):
            # Draw highlight box for selected option
            if i == self.current_selection:
                highlight_rect = pygame.Rect(
                    self.popup_x + 20,
                    y - 5,
                    self.popup_width - 40,
                    40
                )
                pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, highlight_rect)
                pygame.draw.rect(self.screen, self.GOLD, highlight_rect, 2)
                text_color = self.GOLD
            else:
                text_color = self.WHITE
            
            # Draw stat option
            stat_text = self.normal_font.render(
                f"{stat_name}: {stat_value} -> {stat_value + 1}",
                True, text_color
            )
            stat_rect = stat_text.get_rect(center=(self.popup_rect.centerx, y + 15))
            self.screen.blit(stat_text, stat_rect)
            
            y += 50
        
        # Draw instruction
        instruction_text = self.small_font.render(
            "Up/Down or W/S to select | Enter to confirm",
            True, self.GRAY
        )
        instruction_rect = instruction_text.get_rect(center=(self.popup_rect.centerx, self.popup_rect.bottom - 20))
        self.screen.blit(instruction_text, instruction_rect)
