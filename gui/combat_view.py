"""
GUI Combat View for Pygame-based first-person combat.
Integrates with BattleManager or EnhancedBattleManager for combat logic.
"""
from __future__ import annotations
import pygame
import os


class CombatView:
    """Renders first-person combat view with enemy sprite and action menu."""
    
    def __init__(self, screen, presenter):
        self.screen = screen
        self.presenter = presenter
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Define combat view area (left 2/3 for combat, right 1/3 for HUD)
        self.combat_width = int(self.screen_width * 2 / 3)
        self.combat_height = self.screen_height
        
        # Colors
        self.colors = {
            'background': (20, 20, 25),
            'enemy': (200, 50, 50),
            'player': (50, 150, 250),
            'hp_bar': (200, 50, 50),
            'mp_bar': (50, 100, 200),
            'text': (255, 255, 255),
            'action_bg': (40, 40, 45),
            'action_selected': (80, 80, 90),
            'message_bg': (30, 30, 35),
        }
        
        # Combat log
        self.combat_log = []
        self.max_log_lines = 5
        
        # Sprite cache
        self.sprite_cache = {}
        self.sprite_dir = 'assets/sprites'
        
        
    def add_combat_message(self, message):
        """Add a message to the combat log."""
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log_lines:
            self.combat_log.pop(0)
    
    def _get_enemy_sprite(self, enemy):
        """
        Load enemy sprite from file based on enemy type.
        
        Args:
            enemy: Enemy character object
        
        Returns:
            pygame.Surface or None if sprite not found
        """
        # Try to get sprite name from picture attribute first
        sprite_name = None
        
        if hasattr(enemy, 'picture') and enemy.picture:
            # Remove .txt extension from picture filename
            sprite_name = enemy.picture.replace('.txt', '')
        elif hasattr(enemy, 'enemy_typ'):
            # Fallback to enemy_typ (won't work for specific enemies, but better than nothing)
            sprite_name = enemy.enemy_typ.lower()
        
        if not sprite_name:
            return None
        
        # Create cache key
        cache_key = f"{sprite_name}"
        
        # Check cache first
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]
        
        # Build sprite filename
        sprite_filename = f"{sprite_name}.png"
        sprite_path = os.path.join(self.sprite_dir, sprite_filename)
        
        # Try to load sprite
        if os.path.exists(sprite_path):
            try:
                sprite = pygame.image.load(sprite_path)
                # Try convert_alpha first, fallback to convert if it fails
                try:
                    sprite = sprite.convert_alpha()
                except:
                    sprite = sprite.convert()
                self.sprite_cache[cache_key] = sprite
                return sprite
            except pygame.error as e:
                print(f"Failed to load sprite {sprite_path}: {e}")
                return None
        
        return None
    
    def _has_sight(self, player_char):
        """Check if player has sight ability.
        
        Sight is granted by:
        - Inquisitor or Seeker class
        - Pendant of Vision equipped
        - Reveal spell effect (sets sight = True)
        """
        # Check class
        if player_char.cls.name in ["Inquisitor", "Seeker"]:
            return True
        
        # Check equipment
        if player_char.equipment['Pendant'].name == "Pendant of Vision":
            return True
        
        # Check sight attribute (set by Reveal spell or other effects)
        if hasattr(player_char, 'sight') and player_char.sight:
            return True
        
        return False
    
    def _colorize_sprite(self, sprite, enemy):
        """Apply color tinting to a grayscale sprite based on enemy type.
        
        Uses multiplicative blending to colorize grayscale sprites while
        preserving shading and detail.
        """
        # Get color from the enemy object, or use default gray
        tint_color = getattr(enemy, 'color', (150, 150, 150))
        
        # Create a colorized copy of the sprite
        colorized = sprite.copy()
        
        # Create a color surface to blend with
        color_surface = pygame.Surface(colorized.get_size())
        color_surface.fill(tint_color)
        
        # Apply multiplicative blend: result = (original * tint) / 255
        # This preserves brightness while applying color
        colorized.blit(color_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return colorized
    
    def render_combat(self, player_char, enemy, actions, selected_action=0):
        """Render the complete combat view."""
        # Fill combat area background
        combat_rect = pygame.Rect(0, 0, self.combat_width, self.combat_height)
        self.screen.fill(self.colors['background'], combat_rect)
        
        # Check if player has sight
        has_sight = self._has_sight(player_char)
        
        # Render enemy in center
        self._render_enemy(enemy, has_sight)
        
        # Render player status at bottom left
        self._render_player_status(player_char)
        
        # Render action menu at bottom
        self._render_action_menu(actions, selected_action)
        
        # Render combat log
        self._render_combat_log()
    
    def _render_enemy(self, enemy, has_sight=True):
        """Render the enemy sprite/representation."""
        center_x = self.combat_width // 2
        center_y = self.combat_height // 3
        
        # Try to load enemy sprite
        sprite = self._get_enemy_sprite(enemy)
        
        if sprite:
            # Scale sprite up to 256x256 for better visibility
            scaled_sprite = pygame.transform.scale(sprite, (256, 256))
            sprite_rect = scaled_sprite.get_rect(center=(center_x, center_y))
            self.screen.blit(scaled_sprite, sprite_rect)
            enemy_size = 128  # Use half the scaled size for positioning other elements
        else:
            # Fallback to simple representation
            enemy_size = 120
            pygame.draw.circle(self.screen, self.colors['enemy'], 
                             (center_x, center_y), enemy_size)
            
            # Add eyes
            eye_offset = enemy_size // 3
            eye_size = enemy_size // 6
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (center_x - eye_offset, center_y - eye_offset), eye_size)
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (center_x + eye_offset, center_y - eye_offset), eye_size)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (center_x - eye_offset, center_y - eye_offset), eye_size // 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (center_x + eye_offset, center_y - eye_offset), eye_size // 2)
        
        # Enemy name (always visible)
        font = pygame.font.Font(None, 32)
        name_surf = font.render(enemy.name, True, self.colors['text'])
        name_rect = name_surf.get_rect(center=(center_x, center_y - enemy_size - 30))
        self.screen.blit(name_surf, name_rect)
        
        # Enemy HP bar (only visible with sight)
        if has_sight:
            bar_width = 200
            bar_height = 20
            bar_x = center_x - bar_width // 2
            bar_y = center_y + enemy_size + 20
            
            # Background
            pygame.draw.rect(self.screen, (100, 100, 100),
                           pygame.Rect(bar_x, bar_y, bar_width, bar_height))
            
            # HP fill
            hp_ratio = enemy.health.current / max(enemy.health.max, 1)
            hp_width = int(bar_width * hp_ratio)
            pygame.draw.rect(self.screen, self.colors['hp_bar'],
                           pygame.Rect(bar_x, bar_y, hp_width, bar_height))
            
            # HP text
            small_font = pygame.font.Font(None, 18)
            hp_text = f"{enemy.health.current}/{enemy.health.max}"
            hp_surf = small_font.render(hp_text, True, self.colors['text'])
            hp_rect = hp_surf.get_rect(center=(center_x, bar_y + bar_height // 2))
            self.screen.blit(hp_surf, hp_rect)
    
    def _render_player_status(self, player_char):
        """Render player HP/MP at bottom left."""
        x = 20
        y = self.combat_height - 120
        
        font = pygame.font.Font(None, 24)
        
        # HP
        hp_text = f"HP: {player_char.health.current}/{player_char.health.max}"
        hp_surf = font.render(hp_text, True, self.colors['hp_bar'])
        self.screen.blit(hp_surf, (x, y))
        
        # MP
        mp_text = f"MP: {player_char.mana.current}/{player_char.mana.max}"
        mp_surf = font.render(mp_text, True, self.colors['mp_bar'])
        self.screen.blit(mp_surf, (x, y + 30))
    
    def _render_action_menu(self, actions, selected_action):
        """Render the action selection menu."""
        menu_height = 150
        menu_y = self.combat_height - menu_height
        
        # Background
        menu_rect = pygame.Rect(0, menu_y, self.combat_width, menu_height)
        pygame.draw.rect(self.screen, self.colors['action_bg'], menu_rect)
        pygame.draw.line(self.screen, self.colors['text'], 
                        (0, menu_y), (self.combat_width, menu_y), 2)
        
        # Title
        font = pygame.font.Font(None, 28)
        title_surf = font.render("Choose Action:", True, self.colors['text'])
        self.screen.blit(title_surf, (20, menu_y + 10))
        
        # Actions in a grid (3 per row)
        action_font = pygame.font.Font(None, 24)
        start_y = menu_y + 45
        actions_per_row = 3
        action_spacing = 180
        
        for i, action in enumerate(actions):
            row = i // actions_per_row
            col = i % actions_per_row
            
            x = 30 + col * action_spacing
            y = start_y + row * 35
            
            # Highlight selected action
            if i == selected_action:
                highlight_rect = pygame.Rect(x - 5, y - 3, action_spacing - 20, 30)
                pygame.draw.rect(self.screen, self.colors['action_selected'], highlight_rect)
            
            # Action text (no numbers)
            action_surf = action_font.render(action, True, self.colors['text'])
            self.screen.blit(action_surf, (x, y))
    
    def _render_combat_log(self):
        """Render recent combat messages."""
        log_height = 120
        log_y = self.combat_height - 270  # Above action menu
        
        # Background
        log_rect = pygame.Rect(0, log_y, self.combat_width, log_height)
        pygame.draw.rect(self.screen, self.colors['message_bg'], log_rect)
        
        # Messages
        font = pygame.font.Font(None, 20)
        y = log_y + 10
        line_height = 22
        max_lines = 5  # Limit to 5 lines total to fit in box
        lines_rendered = 0
        
        # Process messages in reverse to get most recent first
        for message in reversed(self.combat_log):
            if lines_rendered >= max_lines:
                break
                
            # Split message on newlines to handle multi-line messages properly
            message_lines = [line for line in message.split('\n') if line.strip()]
            
            for line in message_lines:
                if lines_rendered >= max_lines:
                    break
                    
                msg_surf = font.render(line, True, self.colors['text'])
                self.screen.blit(msg_surf, (15, y))
                y += line_height
                lines_rendered += 1
    
    def show_damage_flash(self, is_player_hit):
        """Flash the screen to indicate damage."""
        flash_surface = pygame.Surface((self.combat_width, self.combat_height))
        flash_surface.set_alpha(100)
        
        if is_player_hit:
            flash_surface.fill((200, 0, 0))  # Red for player hit
        else:
            flash_surface.fill((255, 255, 0))  # Yellow for enemy hit
        
        self.screen.blit(flash_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(150)  # Brief flash

    def render_enemy_in_dungeon(self, player_char, enemy):
        """Render the enemy as if it's standing in the dungeon ahead of the player."""
        # Enemy appears in the center-front of the dungeon view (foreground layer)
        # Position at bottom-center of the dungeon view area (left 65% of screen)
        view_width = int(self.screen_width * 0.65)
        center_x = view_width // 2
        
        # Position enemy at bottom third (standing on the floor ahead)
        center_y = int(self.screen_height * 0.65)
        
        # Check if player has sight
        has_sight = self._has_sight(player_char)
        
        # Try to load enemy sprite
        sprite = self._get_enemy_sprite(enemy)
        
        if sprite:
            # Colorize the sprite based on enemy type
            colorized_sprite = self._colorize_sprite(sprite, enemy)
            
            # Scale sprite to appear as foreground object (larger)
            scaled_sprite = pygame.transform.scale(colorized_sprite, (320, 320))
            sprite_rect = scaled_sprite.get_rect(center=(center_x, center_y))
            self.screen.blit(scaled_sprite, sprite_rect)
            enemy_size = 160  # Use half the scaled size for positioning other elements
        else:
            # Fallback to simple representation
            enemy_size = 150
            pygame.draw.circle(self.screen, self.colors['enemy'], 
                             (center_x, center_y), enemy_size)
            
            # Add eyes
            eye_offset = enemy_size // 3
            eye_size = enemy_size // 6
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (center_x - eye_offset, center_y - eye_offset), eye_size)
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (center_x + eye_offset, center_y - eye_offset), eye_size)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (center_x - eye_offset, center_y - eye_offset), eye_size // 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (center_x + eye_offset, center_y - eye_offset), eye_size // 2)
        
        # Enemy name label at top of sprite
        font = pygame.font.Font(None, 36)
        name_surf = font.render(enemy.name, True, (255, 255, 255))
        # Add shadow for better readability
        shadow_surf = font.render(enemy.name, True, (0, 0, 0))
        name_rect = name_surf.get_rect(center=(center_x, center_y - enemy_size - 40))
        shadow_rect = shadow_surf.get_rect(center=(center_x + 2, center_y - enemy_size - 38))
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(name_surf, name_rect)
        
        # Enemy HP bar above name (only visible with sight)
        if has_sight:
            bar_width = 250
            bar_height = 25
            bar_x = center_x - bar_width // 2
            bar_y = center_y - enemy_size - 80
            
            # Background
            pygame.draw.rect(self.screen, (40, 40, 40),
                           pygame.Rect(bar_x, bar_y, bar_width, bar_height))
            
            # HP fill
            hp_ratio = enemy.health.current / max(enemy.health.max, 1)
            hp_width = int(bar_width * hp_ratio)
            pygame.draw.rect(self.screen, self.colors['hp_bar'],
                           pygame.Rect(bar_x, bar_y, hp_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, (150, 150, 150),
                           pygame.Rect(bar_x, bar_y, bar_width, bar_height), 2)
            
            # HP text
            hp_font = pygame.font.Font(None, 22)
            hp_text = f"{enemy.health.current}/{enemy.health.max}"
            hp_surf = hp_font.render(hp_text, True, (255, 255, 255))
            hp_rect = hp_surf.get_rect(center=(center_x, bar_y + bar_height // 2))
            self.screen.blit(hp_surf, hp_rect)

    def render_combat_overlay(self, player_char, enemy, actions, selected_action):
        """Render combat UI overlay (action menu and combat log) over the dungeon view."""
        # Render combat log at bottom-left
        self._render_combat_log_overlay()
        
        # Render action menu at bottom
        if actions:  # Only show action menu if there are actions
            self._render_action_menu_overlay(actions, selected_action)

    def _render_combat_log_overlay(self):
        """Render combat log as semi-transparent overlay on dungeon view."""
        view_width = int(self.screen_width * 0.65)
        log_height = 150
        log_y = 10  # Top of screen
        
        # Semi-transparent background
        overlay = pygame.Surface((view_width, log_height))
        overlay.set_alpha(200)
        overlay.fill((15, 15, 20))
        self.screen.blit(overlay, (0, log_y))
        
        # Border
        pygame.draw.rect(self.screen, (80, 80, 90),
                        pygame.Rect(0, log_y, view_width, log_height), 2)
        
        # Messages
        font = pygame.font.Font(None, 22)
        y = log_y + 10
        line_height = 25
        max_lines = 5
        lines_rendered = 0
        
        # Show most recent messages (last 5), oldest to newest from top to bottom
        messages_to_show = self.combat_log[-max_lines:] if len(self.combat_log) > max_lines else self.combat_log
        
        for message in messages_to_show:
            if lines_rendered >= max_lines:
                break
                
            # Split message on newlines to handle multi-line messages properly
            message_lines = [line for line in message.split('\n') if line.strip()]
            
            for line in message_lines:
                if lines_rendered >= max_lines:
                    break
                    
                msg_surf = font.render(line, True, (240, 240, 240))
                self.screen.blit(msg_surf, (15, y))
                y += line_height
                lines_rendered += 1

    def _render_action_menu_overlay(self, actions, selected_action):
        """Render action menu as semi-transparent overlay."""
        view_width = int(self.screen_width * 0.65)
        menu_height = 150
        menu_y = self.screen_height - menu_height
        
        # Semi-transparent background
        overlay = pygame.Surface((view_width, menu_height))
        overlay.set_alpha(220)
        overlay.fill((20, 20, 25))
        self.screen.blit(overlay, (0, menu_y))
        
        # Border
        pygame.draw.rect(self.screen, (100, 100, 110),
                        pygame.Rect(0, menu_y, view_width, menu_height), 3)
        
        # Title
        font = pygame.font.Font(None, 30)
        title_surf = font.render("Choose Action:", True, (220, 220, 220))
        self.screen.blit(title_surf, (20, menu_y + 10))
        
        # Actions in a grid (3 per row)
        action_font = pygame.font.Font(None, 26)
        start_y = menu_y + 50
        actions_per_row = 3
        action_spacing = int(view_width / 3.5)
        
        for i, action in enumerate(actions):
            row = i // actions_per_row
            col = i % actions_per_row
            
            x = 30 + col * action_spacing
            y = start_y + row * 40
            
            # Highlight selected action
            if i == selected_action:
                highlight_rect = pygame.Rect(x - 5, y - 5, action_spacing - 30, 35)
                highlight_overlay = pygame.Surface((highlight_rect.width, highlight_rect.height))
                highlight_overlay.set_alpha(180)
                highlight_overlay.fill((100, 100, 120))
                self.screen.blit(highlight_overlay, (highlight_rect.x, highlight_rect.y))
                pygame.draw.rect(self.screen, (150, 150, 170), highlight_rect, 2)
            
            # Action text
            action_surf = action_font.render(action, True, (240, 240, 240))
            self.screen.blit(action_surf, (x, y))
