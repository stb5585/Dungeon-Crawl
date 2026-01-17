"""
Load Game screen for Pygame GUI - matches the shop layout with character details.
"""

import pygame
from save_system import SaveManager


class LoadGameScreen:
    """
    Load game screen that displays save file information in a two-panel layout.
    Left panel: Character details (name, race, class, level, stats, etc.)
    Right panel: List of save files
    """
    
    def __init__(self, presenter):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.BORDER_COLOR = (200, 200, 200)
        self.HIGHLIGHT_BG = (60, 60, 80)
        
        # Fonts
        self.title_font = presenter.title_font
        self.normal_font = presenter.normal_font
        self.small_font = presenter.small_font
        
        # State
        self.current_selection = 0
        self.save_files = []
        self.save_data = []
        
        # Calculate window positions (left for character info, right for file list)
        self.calculate_window_rects()
    
    def calculate_window_rects(self):
        """Calculate the rectangles for each UI section."""
        # Top header
        header_height = self.height // 12
        self.header_rect = pygame.Rect(0, 0, self.width, header_height)
        
        # Left panel: Character information
        left_width = self.width // 2
        left_height = self.height - header_height
        self.char_info_rect = pygame.Rect(0, header_height, left_width, left_height)
        
        # Right panel: Save file list
        right_width = self.width // 2
        right_height = self.height - header_height
        self.file_list_rect = pygame.Rect(left_width, header_height, right_width, right_height)
    
    def draw_header(self):
        """Draw the header with title."""
        pygame.draw.rect(self.screen, self.BLACK, self.header_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.header_rect, 2)
        
        title = self.normal_font.render("Choose the character to load", True, self.YELLOW)
        title_rect = title.get_rect(centerx=self.width // 2, centery=self.header_rect.centery)
        self.screen.blit(title, title_rect)
    
    def draw_char_info(self):
        """Draw the character information panel."""
        pygame.draw.rect(self.screen, self.BLACK, self.char_info_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.char_info_rect, 2)
        
        if not self.save_data or self.current_selection >= len(self.save_data):
            return
        
        info = self.save_data[self.current_selection]
        
        # Start position for text
        x = self.char_info_rect.left + 20
        y = self.char_info_rect.top + 20
        line_height = 30
        
        # Character name (bold/larger)
        name_text = self.normal_font.render(info['name'], True, self.YELLOW)
        self.screen.blit(name_text, (x, y))
        y += line_height * 1.5
        
        # Character details
        details = [
            f"Level: {info['level']}",
            f"Race: {info['race']}",
            f"Class: {info['class']}",
        ]
        
        if 'experience' in info:
            details.append(f"Experience: {info['experience']:,}")
        
        if 'gold' in info:
            details.append(f"Gold: {info['gold']}")
        
        for detail in details:
            text = self.small_font.render(detail, True, self.WHITE)
            self.screen.blit(text, (x, y))
            y += line_height
        
        # Stats if available
        if 'stats' in info and info['stats']:
            y += 10
            stats_header = self.small_font.render("Stats:", True, self.YELLOW)
            self.screen.blit(stats_header, (x, y))
            y += line_height
            
            for stat_name, stat_value in info['stats'].items():
                stat_text = self.small_font.render(f"{stat_name}: {stat_value}", True, self.WHITE)
                self.screen.blit(stat_text, (x, y))
                y += line_height - 5
    
    def draw_file_list(self):
        """Draw the save file list panel."""
        pygame.draw.rect(self.screen, self.BLACK, self.file_list_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.file_list_rect, 2)
        
        if not self.save_data:
            no_saves = self.normal_font.render("No save files found", True, self.GRAY)
            no_saves_rect = no_saves.get_rect(
                centerx=self.file_list_rect.centerx,
                centery=self.file_list_rect.centery
            )
            self.screen.blit(no_saves, no_saves_rect)
            return
        
        # Draw list header
        x = self.file_list_rect.left + 10
        y = self.file_list_rect.top + 10
        line_height = 40
        
        header = self.small_font.render("Save Files", True, self.YELLOW)
        self.screen.blit(header, (x, y))
        y += line_height
        
        # Draw file list
        max_visible = 10
        for i, data in enumerate(self.save_data[:max_visible]):
            y = self.file_list_rect.top + 50 + i * line_height
            
            # Highlight selected
            if i == self.current_selection:
                highlight_rect = pygame.Rect(
                    self.file_list_rect.left + 5,
                    y - 2,
                    self.file_list_rect.width - 10,
                    line_height - 4
                )
                pygame.draw.rect(self.screen, self.HIGHLIGHT_BG, highlight_rect)
                pygame.draw.rect(self.screen, self.YELLOW, highlight_rect, 1)
                color = self.YELLOW
            else:
                color = self.WHITE
            
            # Display file name with level
            file_text = self.small_font.render(
                f"{data['name']} (Lvl {data['level']})",
                True,
                color
            )
            self.screen.blit(file_text, (x, y))
    
    def draw_all(self):
        """Draw all UI elements."""
        self.screen.fill(self.BLACK)
        self.draw_header()
        self.draw_char_info()
        self.draw_file_list()
        pygame.display.flip()
    
    def load_save_files(self, save_files):
        """
        Load save file data.
        
        Args:
            save_files: List of save file paths
        """
        self.save_files = save_files
        self.save_data = []
        self.current_selection = 0
        
        for save_file in save_files:
            try:
                player_char = SaveManager.load_player(save_file)
                if player_char:
                    # Extract character information
                    char_data = {
                        'name': getattr(player_char, 'name', 'Unknown').title(),
                        'race': getattr(getattr(player_char, 'race', None), 'name', 'Unknown'),
                        'class': getattr(getattr(player_char, 'cls', None), 'name', 'Unknown'),
                        'level': getattr(player_char.level, 'level', 1) if hasattr(player_char, 'level') else 1,
                        'experience': getattr(player_char.level, 'exp', 0) if hasattr(player_char, 'level') else 0,
                        'gold': getattr(player_char, 'gold', 0),
                        'file': save_file
                    }
                    
                    # Try to get stats
                    if hasattr(player_char, 'stats'):
                        stats = getattr(player_char, 'stats', None)
                        if stats:
                            char_data['stats'] = {
                                'STR': getattr(stats, 'strength', 0),
                                'INT': getattr(stats, 'intel', 0),
                                'WIS': getattr(stats, 'wisdom', 0),
                                'CON': getattr(stats, 'con', 0),
                                'CHA': getattr(stats, 'charisma', 0),
                                'DEX': getattr(stats, 'dex', 0),
                            }
                    
                    self.save_data.append(char_data)
                else:
                    # Corrupted save
                    self.save_data.append({
                        'name': 'Corrupted save',
                        'race': '?',
                        'class': '?',
                        'level': '?',
                        'file': save_file
                    })
            except Exception as e:
                # Error loading save
                self.save_data.append({
                    'name': 'Error loading',
                    'race': '?',
                    'class': '?',
                    'level': '?',
                    'file': save_file
                })
    
    def navigate(self, save_files):
        """
        Navigate the load game screen and return selected save file path.
        
        Args:
            save_files: List of save file paths
            
        Returns:
            str: Path to selected save file, or None if cancelled
        """
        self.load_save_files(save_files)
        
        if not self.save_data:
            return None
        
        while True:
            self.draw_all()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_selection = (self.current_selection - 1) % len(self.save_data)
                    elif event.key == pygame.K_DOWN:
                        self.current_selection = (self.current_selection + 1) % len(self.save_data)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return self.save_data[self.current_selection]['file']
                    elif event.key == pygame.K_ESCAPE:
                        return None
            
            self.presenter.clock.tick(30)
