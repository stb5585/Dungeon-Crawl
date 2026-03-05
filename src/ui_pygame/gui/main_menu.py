"""
Main menu screen for Pygame GUI - matches curses terminal layout.
"""

import pygame


class MainMenuScreen:
    """
    Main menu that matches the curses terminal style.
    """
    
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
        
        # Try to load a monospaced font for ASCII art
        try:
            self.ascii_font = pygame.font.Font(pygame.font.match_font('courier', bold=True), 16)
        except Exception:
            # Fallback to default monospace
            self.ascii_font = pygame.font.SysFont('monospace', 16, bold=True)
        
        # ASCII Art Title (matching curses version)
        self.title_art = [
            " /$$$$$$$  /$$   /$$ /$$   /$$  /$$$$$$  /$$$$$$$$  /$$$$$$  /$$   /$$",
            "| $$__  $$| $$  | $$| $$$ | $$ /$$__  $$| $$_____/ /$$__  $$| $$$ | $$",
            "| $$  \\ $$| $$  | $$| $$$$| $$| $$  \\__/| $$      | $$  \\ $$| $$$$| $$",
            "| $$  | $$| $$  | $$| $$ $$ $$| $$ /$$$$| $$$$$   | $$  | $$| $$ $$ $$",
            "| $$  | $$| $$  | $$| $$  $$$$| $$|_  $$| $$__/   | $$  | $$| $$  $$$$",
            "| $$  | $$| $$  | $$| $$\\  $$$| $$  \\ $$| $$      | $$  | $$| $$\\  $$$",
            "| $$$$$$$/|  $$$$$$/| $$ \\  $$|  $$$$$$/| $$$$$$$$|  $$$$$$/| $$ \\  $$",
            "|_______/  \\______/ |__/  \\__/ \\______/ |________/ \\______/ |__/  \\__/",
            "",
            "            /$$$$$$  /$$$$$$$   /$$$$$$  /$$      /$$ /$$",
            "           /$$__  $$| $$__  $$ /$$__  $$| $$  /$ | $$| $$",
            "          | $$  \\__/| $$  \\ $$| $$  \\ $$| $$ /$$$| $$| $$",
            "          | $$      | $$$$$$$/| $$$$$$$$| $$/$$ $$ $$| $$",
            "          | $$      | $$__  $$| $$__  $$| $$$$_  $$$$| $$",
            "          | $$    $$| $$  \\ $$| $$  | $$| $$$/ \\  $$$| $$",
            "          |  $$$$$$/| $$  | $$| $$  | $$| $$/   \\  $$| $$$$$$$$",
            "           \\______/ |__/  |__/|__/  |__/|__/     \\__/|________/"
        ]
        
        self.current_option = 0
        self.options = []
    
    def draw_title(self):
        """Draw the ASCII art title."""
        # Calculate starting position to center the title
        line_height = 18  # Tight spacing for ASCII art
        title_height = len(self.title_art) * line_height
        start_y = max(20, (self.height // 2) - title_height - 80)
        
        # Find the longest line to center everything relative to it
        max_width = max(self.ascii_font.size(line)[0] for line in self.title_art if line)
        
        # Draw each line of ASCII art using monospaced font
        for i, line in enumerate(self.title_art):
            text = self.ascii_font.render(line, True, self.WHITE)
            # Center based on the longest line width
            text_x = (self.width - max_width) // 2
            self.screen.blit(text, (text_x, start_y + i * line_height))
    
    def draw_menu(self):
        """Draw the menu options."""
        # Calculate menu position - centered below title
        menu_start_y = (self.height // 2) + 50
        line_height = 40
        
        for i, option in enumerate(self.options):
            y = menu_start_y + i * line_height
            
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
        self.screen.fill(self.BLACK)
        self.draw_title()
        self.draw_menu()
        pygame.display.flip()
    
    def navigate(self, options):
        """
        Navigate the main menu and return selected option index.
        
        Args:
            options: List of menu option strings
            
        Returns:
            int: Index of selected option, or None if cancelled
        """
        self.options = options
        
        while True:
            self.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_option = (self.current_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.current_option = (self.current_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.current_option
                    elif event.key == pygame.K_ESCAPE:
                        return None
            
            self.presenter.clock.tick(30)
