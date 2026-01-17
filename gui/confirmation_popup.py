"""
Confirmation popup for character creation decisions.
"""

import pygame


class ConfirmationPopup:
    """
    A small Yes/No confirmation popup that appears over the current screen.
    """
    
    def __init__(self, presenter, message):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        self.message = message
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        self.POPUP_BG = (20, 20, 30)
        
        # Fonts
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        
        # State
        self.current_selection = 0  # 0 = Yes, 1 = No
        self.options = ["Yes", "No"]
        
        # Calculate popup position (centered)
        self.popup_width = 400
        self.popup_height = 200
        self.popup_x = (self.width - self.popup_width) // 2
        self.popup_y = (self.height - self.popup_height) // 2
        self.popup_rect = pygame.Rect(self.popup_x, self.popup_y, self.popup_width, self.popup_height)
    
    def draw_popup(self):
        """Draw the confirmation popup over the current screen."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw popup background
        pygame.draw.rect(self.screen, self.POPUP_BG, self.popup_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.popup_rect, 3)
        
        # Draw message
        y = self.popup_y + 30
        message_lines = self._wrap_text(self.message, self.popup_width - 40)
        for line in message_lines:
            text = self.normal_font.render(line, True, self.WHITE)
            text_rect = text.get_rect(centerx=self.popup_x + self.popup_width // 2)
            text_rect.y = y
            self.screen.blit(text, text_rect)
            y += 30
        
        # Draw options (Yes/No)
        y = self.popup_y + self.popup_height - 70
        for i, option in enumerate(self.options):
            x = self.popup_x + (self.popup_width // 4) + i * (self.popup_width // 2)
            
            if i == self.current_selection:
                # Highlight selected option
                option_rect = pygame.Rect(x - 50, y - 5, 100, 35)
                pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, option_rect)
                pygame.draw.rect(self.screen, self.YELLOW, option_rect, 2)
                color = self.YELLOW
            else:
                color = self.WHITE
            
            text = self.normal_font.render(option, True, color)
            text_rect = text.get_rect(centerx=x, centery=y + 10)
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            line = " ".join(current_line)
            line_width = self.normal_font.size(line)[0]
            
            if line_width > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def show(self, background_draw_func=None):
        """
        Show the popup and wait for user response.
        
        Args:
            background_draw_func: Optional function to redraw background screen
            
        Returns:
            bool: True if Yes, False if No
        """
        # Draw background once before entering loop
        if background_draw_func:
            background_draw_func()
        
        while True:
            # Draw popup on top
            self.draw_popup()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.current_selection = 0
                    elif event.key == pygame.K_RIGHT:
                        self.current_selection = 1
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.current_selection == 0  # True for Yes, False for No
                    elif event.key == pygame.K_ESCAPE:
                        return False  # ESC = No
            
            self.presenter.clock.tick(30)


def confirm_yes_no(presenter, message, background_draw_func=None):
    """
    Convenience helper for simple Yes/No confirmations.

    Args:
        presenter: Active presenter with screen/clock/fonts
        message: Prompt to display
        background_draw_func: Optional function to redraw the underlying screen once

    Returns:
        bool: True for Yes, False for No (ESC also returns False)
    """
    popup = ConfirmationPopup(presenter, message)
    return popup.show(background_draw_func=background_draw_func)
