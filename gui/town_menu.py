"""
Town Menu screen for Pygame GUI with background image.
"""

import pygame

from gui.town_base import TownScreenBase


class TownMenuScreen(TownScreenBase):
    """
    Town menu screen that displays the town background and location options.
    """
    
    def __init__(self, presenter):
        super().__init__(presenter)
        # Menu state
        self.current_selection = 0

    def draw_menu_panel(self, options):
        """Draw the semi-transparent menu panel with options."""
        panel_width = 400
        panel_height = self.height
        panel_x = self.width - panel_width
        panel_y = 0
        
        # Create semi-transparent overlay
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.draw_semi_transparent_panel(panel_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, self.colors.GOLD, panel_rect, 3)
        
        # Title
        title_text = self.title_font.render("Town of Silvana", True, self.colors.GOLD)
        title_rect = title_text.get_rect(centerx=panel_x + panel_width // 2, top=40)
        self.screen.blit(title_text, title_rect)
        
        # Options list
        options_start_y = 150
        line_height = 50
        
        for i, option in enumerate(options):
            y = options_start_y + i * line_height
            
            # Highlight selected option
            if i == self.current_selection:
                highlight_rect = pygame.Rect(
                    panel_x + 20,
                    y - 5,
                    panel_width - 40,
                    line_height - 10
                )
                pygame.draw.rect(self.screen, self.colors.HIGHLIGHT_BG, highlight_rect)
                pygame.draw.rect(self.screen, self.colors.GOLD, highlight_rect, 2)
                color = self.colors.GOLD
            else:
                color = self.colors.WHITE
            
            # Option text
            option_text = self.normal_font.render(option, True, color)
            option_rect = option_text.get_rect(left=panel_x + 40, centery=y + 15)
            self.screen.blit(option_text, option_rect)
        
        # Instructions at bottom
        instructions = [
            "UP/DOWN: Navigate",
            "ENTER: Select",
            "ESC: Quit"
        ]
        instructions_y = self.height - 120
        for instruction in instructions:
            instr_text = self.small_font.render(instruction, True, self.colors.GRAY)
            instr_rect = instr_text.get_rect(centerx=panel_x + panel_width // 2, top=instructions_y)
            self.screen.blit(instr_text, instr_rect)
            instructions_y += 25
    
    def navigate(self, options):
        """
        Navigate the town menu and return selected option index.
        
        Args:
            options: List of location names to display
            
        Returns:
            int: Index of selected option, or None if cancelled
        """
        self.current_selection = 0
        
        while True:
            # Draw everything
            self.draw_background()
            self.draw_menu_panel(options)
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_selection = (self.current_selection - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        self.current_selection = (self.current_selection + 1) % len(options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.current_selection
                    elif event.key == pygame.K_ESCAPE:
                        # Return the last option (typically Quit)
                        return len(options) - 1
            
            self.presenter.clock.tick(30)
