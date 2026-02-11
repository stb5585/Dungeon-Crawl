"""
GUI Combat View for Pygame-based first-person combat.
Integrates with BattleManager or EnhancedBattleManager for combat logic.
"""
from __future__ import annotations

import math
import os

import pygame


class SpriteAnimator:
    """Handles sprite animations (idle, bob, damage, death)."""
    
    def __init__(self):
        self.frame = 0
        self.animation_time = 0
        self.animation_type = None  # 'idle', 'damage', 'death', None
        self.bob_offset = 0
        self.sway_offset = 0
        self.damage_flash = 0  # 0-1, fades over time
        self.is_dead = False
        self.death_progress = 0  # 0-1, for scale/dissolve animation
    
    def update(self, dt=1):
        """Update animation state. dt is frame time."""
        self.animation_time += dt
        
        # Idle idle animation (2-frame breathe/sway)
        if self.animation_type != 'death':
            # Cycle between 0 and 1 every 60 frames (about 1 second at 60fps)
            self.frame = int((self.animation_time // 30) % 2)
        
        # Vertical bob (sine wave, continuous)
        bob_cycle = self.animation_time / 20  # Complete cycle every 20 frames
        self.bob_offset = math.sin(bob_cycle * math.pi * 2) * 8  # ±8 pixel bob

        # Horizontal sway (subtle idle motion for grounded enemies)
        sway_cycle = self.animation_time / 40  # Slower than bob
        self.sway_offset = math.sin(sway_cycle * math.pi * 2) * 3  # ±3 pixel sway
        
        # Damage flash decay
        if self.damage_flash > 0:
            self.damage_flash = max(0, self.damage_flash - 0.1)  # Fade over ~10 frames
        
        # Death animation progress
        if self.animation_type == 'death':
            self.death_progress = min(1.0, self.animation_time / 60)  # 1 second to complete
            if self.death_progress >= 1.0:
                self.is_dead = True
    
    def trigger_damage(self):
        """Trigger damage flash animation."""
        self.damage_flash = 1.0
        self.animation_type = None
    
    def trigger_death(self):
        """Trigger death animation."""
        self.animation_type = 'death'
        self.animation_time = 0
        self.death_progress = 0
        self.damage_flash = 0  # Clear damage flash for clean death animation
    
    def apply_tint(self, surface, tint_color, strength):
        """Apply a tint overlay to a surface while preserving alpha channel."""
        if strength <= 0:
            return surface
        
        tinted = surface.copy()
        # Create RGB-only overlay (no alpha in fill)
        overlay = pygame.Surface(surface.get_size())
        overlay.fill(tint_color)
        overlay.set_alpha(int(strength * 128))
        # Use BLEND_RGB_ADD to affect only RGB channels, preserving original alpha
        tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return tinted


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

        # Status icon colors
        self.status_colors = {
            "positive": (70, 170, 90),
            "negative": (190, 70, 70),
        }
        
        # Sprite cache
        self.sprite_cache = {}
        self.sprite_dir = 'src/ui_pygame/assets/sprites'
        
        # Sprite animators (per enemy instance)
        self.sprite_animators = {}  # Key by enemy id()

    def _get_sprite_animator(self, enemy):
        """Get or create animator for this enemy instance."""
        enemy_id = id(enemy)
        if enemy_id not in self.sprite_animators:
            self.sprite_animators[enemy_id] = SpriteAnimator()
        return self.sprite_animators[enemy_id]
    
    def update_animations(self):
        """Update all active sprite animations."""
        for animator in self.sprite_animators.values():
            animator.update()
    
    def enemy_take_damage(self, enemy):
        """Trigger damage flash when enemy takes damage."""
        animator = self._get_sprite_animator(enemy)
        animator.trigger_damage()
    
    def enemy_dies(self, enemy):
        """Trigger death animation when enemy dies."""
        animator = self._get_sprite_animator(enemy)
        animator.trigger_death()
        
    def add_combat_message(self, message):
        """Add a message to the combat log."""
        cleaned_lines = self._filter_status_message(str(message))
        if not cleaned_lines:
            return
        for line in cleaned_lines:
            self.combat_log.append(line)
        while len(self.combat_log) > self.max_log_lines:
            self.combat_log.pop(0)

    def _filter_status_message(self, message):
        """Remove status-effect log lines to keep the log focused on actions."""
        kept_lines = []
        suppress_terms = (
            "fails to",
            "resists the spell",
            "is immune to",
        )
        suppress_already = (
            "stunned",
            "asleep",
            "prone",
            "blind",
            "disarmed",
            "silenced",
        )
        for line in message.split("\n"):
            line_lower = line.lower()
            if "is affected by" in line_lower:
                continue
            if any(term in line_lower for term in suppress_terms):
                continue
            if "already" in line_lower and any(term in line_lower for term in suppress_already):
                continue
            if line.strip():
                kept_lines.append(line.strip())
        return kept_lines

    def _effect_label(self, effect_name):
        labels = {
            "Berserk": "BRK",
            "Blind": "BLD",
            "Doom": "DOM",
            "Poison": "PSN",
            "Silence": "SIL",
            "Sleep": "SLP",
            "Stun": "STN",
            "Defend": "DEF",
            "Steal Success": "STE",
            "Bleed": "BLD",
            "Disarm": "DSA",
            "Prone": "PRN",
            "Attack": "ATK",
            "Defense": "DEF",
            "Magic": "MAG",
            "Magic Defense": "MDF",
            "Speed": "SPD",
            "DOT": "DOT",
            "Duplicates": "DUP",
            "Ice Block": "ICE",
            "Mana Shield": "MSH",
            "Reflect": "RFL",
            "Regen": "REG",
            "Resist Fire": "RF",
            "Resist Ice": "RI",
            "Resist Electric": "RE",
            "Resist Water": "RW",
            "Resist Earth": "RTH",
            "Resist Wind": "RWI",
            "Jump": "JMP",
            "Power Up": "PWR",
        }
        return labels.get(effect_name, effect_name[:3].upper())

    def _collect_status_icons(self, character):
        icons = []
        skip_effects = {
            "DOT",
            "Duplicates",
            "Jump",
            "Power Up",
            "Shapeshifted",
            "Steal Success",
        }
        positive_status = {"Defend", "Steal Success"}
        positive_magic = {
            "Duplicates",
            "Ice Block",
            "Mana Shield",
            "Reflect",
            "Regen",
            "Resist Fire",
            "Resist Ice",
            "Resist Electric",
            "Resist Water",
            "Resist Earth",
            "Resist Wind",
        }

        for name, effect in character.status_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_status))
        for name, effect in character.physical_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), False))
        for name, effect in character.stat_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), effect.extra >= 0))
        for name, effect in character.magic_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_magic))
        for name, effect in character.class_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), True))

        return icons

    def _render_status_icons(self, icons, x, y, max_width):
        if not icons:
            return

        font = pygame.font.Font(None, 16)
        icon_w = 38
        icon_h = 18
        padding = 6
        per_row = max(1, max_width // (icon_w + padding))

        for idx, (label, is_positive) in enumerate(icons):
            row = idx // per_row
            col = idx % per_row
            icon_x = x + col * (icon_w + padding)
            icon_y = y + row * (icon_h + padding)
            color = self.status_colors["positive" if is_positive else "negative"]

            rect = pygame.Rect(icon_x, icon_y, icon_w, icon_h)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            pygame.draw.rect(self.screen, (20, 20, 20), rect, 1, border_radius=4)

            text_surf = font.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
    
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
                # Always use convert_alpha to preserve transparency
                sprite = sprite.convert_alpha()
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
        if player_char.equipment['Pendant'].mod == "Vision":
            return True
        
        # Check sight attribute (set by Reveal spell or other effects)
        if hasattr(player_char, 'sight') and player_char.sight:
            return True
        
        return False
    
    def _colorize_sprite(self, sprite, enemy):
        """Prepare sprite for rendering.
        
        With the new colored sprite system (ascii_to_sprite_colored.py), sprites
        are generated with full color palettes that preserve detail and outlines.
        This method now skips blanket colorization which was destroying detail.
        
        Sprites generated from ASCII art now include:
        - Base color for the enemy type
        - Shadow colors for depth
        - Highlight colors for detail
        - Accent colors for clothing, equipment, and eyes
        
        No additional colorization is needed.
        """
        # Return sprite as-is - it's already colored from generation
        return sprite
    
    def render_combat(self, player_char, enemy, actions, selected_action=0):
        """Render the complete combat view."""
        # Update animations
        self.update_animations()
        
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
        """Render the enemy sprite/representation with animations."""
        center_x = self.combat_width // 2
        center_y = self.combat_height // 3

        is_flying = getattr(enemy, "flying", False)
        
        # Get animator for this enemy
        animator = self._get_sprite_animator(enemy)
        
        # Try to load enemy sprite
        sprite = self._get_enemy_sprite(enemy)
        
        if sprite:
            # Scale sprite up to 256x256 for better visibility
            scaled_sprite = pygame.transform.scale(sprite, (256, 256))
            
            # Apply animations
            display_sprite = scaled_sprite
            
            # Apply damage flash tint
            if animator.damage_flash > 0:
                display_sprite = animator.apply_tint(display_sprite, (255, 100, 100), animator.damage_flash)
            
            # Apply death animation (scale down and fade)
            if animator.animation_type == 'death':
                # Scale from 1.0 to 0.3 as death progresses
                scale = 1.0 - (animator.death_progress * 0.7)
                death_size = int(256 * scale)
                display_sprite = pygame.transform.scale(display_sprite, (death_size, death_size))
                
                # Fade out by modulating per-pixel alpha (preserves sprite shape)
                fade_alpha = int(255 * (1.0 - animator.death_progress))
                alpha_surf = pygame.Surface(display_sprite.get_size(), pygame.SRCALPHA)
                alpha_surf.fill((255, 255, 255, fade_alpha))
                display_sprite = display_sprite.copy()
                display_sprite.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Calculate Y position with bob animation
            bob_y = center_y + animator.bob_offset if is_flying else center_y
            bob_x = center_x if is_flying else center_x + animator.sway_offset
            
            sprite_rect = display_sprite.get_rect(center=(bob_x, bob_y))
            self.screen.blit(display_sprite, sprite_rect)
            enemy_size = 128  # Use half the scaled size for positioning other elements
        else:
            # Fallback to simple representation
            enemy_size = 120
            fallback_x = center_x if is_flying else center_x + animator.sway_offset
            fallback_y = center_y + animator.bob_offset if is_flying else center_y
            pygame.draw.circle(self.screen, self.colors['enemy'], 
                             (int(fallback_x), int(fallback_y)), enemy_size)
            
            # Add eyes
            eye_offset = enemy_size // 3
            eye_size = enemy_size // 6
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (int(fallback_x - eye_offset), int(fallback_y - eye_offset)), eye_size)
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (int(fallback_x + eye_offset), int(fallback_y - eye_offset)), eye_size)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (int(fallback_x - eye_offset), int(fallback_y - eye_offset)), eye_size // 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (int(fallback_x + eye_offset), int(fallback_y - eye_offset)), eye_size // 2)
        
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
        small_font = pygame.font.Font(None, 18)
        
        # HP
        hp_text = f"HP: {player_char.health.current}/{player_char.health.max}"
        hp_surf = font.render(hp_text, True, self.colors['hp_bar'])
        self.screen.blit(hp_surf, (x, y))
        
        # MP
        mp_text = f"MP: {player_char.mana.current}/{player_char.mana.max}"
        mp_surf = font.render(mp_text, True, self.colors['mp_bar'])
        self.screen.blit(mp_surf, (x, y + 30))

        # Status icons
        icons = self._collect_status_icons(player_char)
        if icons:
            self._render_status_icons(icons, x, y + 60, max_width=260)

        # Encumbered warning
        if getattr(player_char, 'encumbered', False):
            y += 60
            # Warning icon/text
            warning_text = "⚠ ENCUMBERED"
            warning_surf = font.render(warning_text, True, (255, 165, 0))  # Orange
            self.screen.blit(warning_surf, (x, y))

            # Penalties list
            penalty_lines = [
                "• Always lose initiative",
                "• -25% hit chance",
                "• -50% dodge chance"
            ]
            y += 25
            for line in penalty_lines:
                penalty_surf = small_font.render(line, True, (255, 100, 100))  # Light red
                self.screen.blit(penalty_surf, (x + 5, y))
                y += 18
    
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
        # Update animations
        self.update_animations()
        
        # Enemy appears in the center-front of the dungeon view (foreground layer)
        # Position at bottom-center of the dungeon view area (left 65% of screen)
        view_width = int(self.screen_width * 0.65)
        center_x = view_width // 2
        
        # Position enemy at bottom third (standing on the floor ahead)
        center_y = int(self.screen_height * 0.65)

        is_flying = getattr(enemy, "flying", False)
        
        # Get animator for this enemy
        animator = self._get_sprite_animator(enemy)
        
        # Check if player has sight
        has_sight = self._has_sight(player_char)
        
        # Try to load enemy sprite
        sprite = self._get_enemy_sprite(enemy)
        
        if sprite:
            # Colorize the sprite based on enemy type
            colorized_sprite = self._colorize_sprite(sprite, enemy)
            
            # Scale sprite to appear as foreground object (larger)
            scaled_sprite = pygame.transform.scale(colorized_sprite, (320, 320))
            
            # Apply animations
            display_sprite = scaled_sprite
            
            # Apply damage flash tint
            if animator.damage_flash > 0:
                display_sprite = animator.apply_tint(display_sprite, (255, 100, 100), animator.damage_flash)
            
            # Apply death animation
            if animator.animation_type == 'death':
                scale = 1.0 - (animator.death_progress * 0.7)
                death_size = int(320 * scale)
                display_sprite = pygame.transform.scale(display_sprite, (death_size, death_size))
                
                # Fade out by modulating per-pixel alpha (preserves sprite shape)
                fade_alpha = int(255 * (1.0 - animator.death_progress))
                alpha_surf = pygame.Surface(display_sprite.get_size(), pygame.SRCALPHA)
                alpha_surf.fill((255, 255, 255, fade_alpha))
                display_sprite = display_sprite.copy()
                display_sprite.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Calculate Y position with bob animation
            bob_y = center_y + animator.bob_offset if is_flying else center_y
            bob_x = center_x if is_flying else center_x + animator.sway_offset
            
            sprite_rect = display_sprite.get_rect(center=(bob_x, bob_y))
            self.screen.blit(display_sprite, sprite_rect)
            enemy_size = 160  # Use half the scaled size for positioning other elements
        else:
            # Fallback to simple representation
            enemy_size = 150
            fallback_x = center_x if is_flying else center_x + animator.sway_offset
            fallback_y = center_y + animator.bob_offset if is_flying else center_y
            pygame.draw.circle(self.screen, self.colors['enemy'], 
                             (int(fallback_x), int(fallback_y)), enemy_size)
            
            # Add eyes
            eye_offset = enemy_size // 3
            eye_size = enemy_size // 6
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (int(fallback_x - eye_offset), int(fallback_y - eye_offset)), eye_size)
            pygame.draw.circle(self.screen, (255, 255, 255),
                             (int(fallback_x + eye_offset), int(fallback_y - eye_offset)), eye_size)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (int(fallback_x - eye_offset), int(fallback_y - eye_offset)), eye_size // 2)
            pygame.draw.circle(self.screen, (0, 0, 0),
                             (int(fallback_x + eye_offset), int(fallback_y - eye_offset)), eye_size // 2)

        # Status icons under the enemy sprite
        icons = self._collect_status_icons(enemy)
        if icons:
            icon_y = int(center_y + enemy_size + 20)
            icon_x = int(center_x - 150)
            self._render_status_icons(icons, icon_x, icon_y, max_width=300)
        
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

            # Status icons under the HP bar
            icons = self._collect_status_icons(enemy)
            if icons:
                self._render_status_icons(icons, bar_x, bar_y + bar_height + 8, max_width=bar_width)

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
