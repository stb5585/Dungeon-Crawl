"""
Pygame-based presenter for Dungeon Crawl combat.

This presenter implements the GamePresenter interface using Pygame for graphical combat display.
It subscribes to the event system for animations and real-time updates.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable
import sys

import pygame

from src.core.events import get_event_bus, EventType
from .interface import GamePresenter

# TODO: Re-enable sprite manager when available
# Import sprite manager
# try:
#     from src.ui_pygame.assets.sprite_manager import get_sprite_manager
#     SPRITES_AVAILABLE = True
# except ImportError:
SPRITES_AVAILABLE = False
# print("Warning: Sprite manager not available")

if TYPE_CHECKING:
    from src.core.character import Character

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
GOLD = (218, 165, 32)
PURPLE = (147, 112, 219)
ORANGE = (255, 140, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Damage type colors
DAMAGE_COLORS = {
    'Physical': WHITE,
    'Fire': (255, 69, 0),
    'Ice': (135, 206, 250),
    'Lightning': (255, 255, 0),
    'Poison': (50, 205, 50),
    'Holy': (255, 215, 0),
    'Shadow': (138, 43, 226),
    'Arcane': (138, 43, 226),
    'Drain': (139, 0, 0),
}


class FloatingText:
    """Floating damage/healing text that animates upward."""
    
    def __init__(self, text: str, x: int, y: int, color: tuple[int, int, int], font: pygame.font.Font):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.font = font
        self.alpha = 255
        self.lifetime = 60  # frames
        self.age = 0
        
    def update(self) -> bool:
        """Update floating text. Returns True if still alive."""
        self.age += 1
        self.y -= 2  # Float upward
        self.alpha = max(0, 255 - (self.age * 4))
        return self.age < self.lifetime
    
    def draw(self, surface: pygame.Surface):
        """Draw the floating text."""
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        surface.blit(text_surface, (self.x, self.y))


class PygamePresenter(GamePresenter):
    """Pygame-based graphical presenter for combat."""
    
    def __init__(self, width: int = 1024, height: int = 768):
        """Initialize Pygame presenter."""
        pygame.init()
        pygame.font.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dungeon Crawl - Combat")  # TODO: what is this?
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.large_font = pygame.font.Font(None, 36)
        self.normal_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 60

        self._background_provider: Callable[[], pygame.Surface] | None = None
        
        # Combat state
        self.player: Character | None = None
        self.enemy: Character | None = None
        self.turn_number: int = 0
        self.telegraph_message: str | None = None
        
        # Animations
        self.floating_texts: list[FloatingText] = []
        self.shake_intensity = 0
        self.shake_duration = 0
        
        # Sprite manager
        self.sprite_manager = None  # Temporarily disable sprite manager usage
        
        # Event system
        self.event_bus = get_event_bus()
        self._subscribe_to_events()
        
        # Combat log with scrolling
        self.combat_log: list[str] = []
        self.max_log_lines = 100  # Store more messages for scrolling
        self.log_scroll_offset = 0
        
        # Debug mode
        self.debug_mode = False  # Default debug mode, can be overridden by game launcher
        
    def _subscribe_to_events(self):
        """Subscribe to combat events for animations."""
        self.event_bus.subscribe(EventType.COMBAT_START, self._on_combat_start)
        self.event_bus.subscribe(EventType.COMBAT_END, self._on_combat_end)
        self.event_bus.subscribe(EventType.TURN_START, self._on_turn_start)
        self.event_bus.subscribe(EventType.DAMAGE_DEALT, self._on_damage_dealt)
        self.event_bus.subscribe(EventType.HEALING_DONE, self._on_healing_done)
        self.event_bus.subscribe(EventType.CRITICAL_HIT, self._on_critical_hit)
        self.event_bus.subscribe(EventType.STATUS_APPLIED, self._on_status_applied)
        
    def _on_combat_start(self, event):
        """Handle combat start event."""
        self.player = event.data.get('actor')
        self.enemy = event.data.get('target')
        self.turn_number = 0
        self.combat_log.clear()
        self._add_log(f"Combat begins: {self.player.name} vs {self.enemy.name}!")
        
    def _on_combat_end(self, event):
        """Handle combat end event."""
        if event.data.get('fled'):
            self._add_log(f"{self.player.name} fled from combat!")
        elif event.data.get('player_alive'):
            self._add_log(f"{self.player.name} is victorious!")
        else:
            self._add_log(f"{self.player.name} was defeated...")
            
    def _on_turn_start(self, event):
        """Handle turn start event."""
        self.turn_number = event.data.get('turn_number', self.turn_number + 1)
        
    def _on_damage_dealt(self, event):
        """Handle damage dealt event - create floating text."""
        damage = event.data.get('damage', 0)
        damage_type = event.data.get('damage_type', 'Physical')
        is_critical = event.data.get('is_critical', False)
        target = event.data.get('target')
        
        if target:
            # Determine position (enemy is on right, player on left)
            x = self.width * 0.75 if target == self.enemy else self.width * 0.25
            y = self.height * 0.3
            
            # Format text
            text = f"-{damage}"
            if is_critical:
                text = f"CRIT! {text}"
                
            # Get color
            color = DAMAGE_COLORS.get(damage_type, WHITE)
            
            # Create floating text
            self.floating_texts.append(
                FloatingText(text, int(x), int(y), color, self.large_font)
            )
            
            # Add screen shake for big hits
            if damage > 30 or is_critical:
                self.shake_intensity = 10 if is_critical else 5
                self.shake_duration = 15
                
    def _on_healing_done(self, event):
        """Handle healing event - create green floating text."""
        amount = event.data.get('amount', 0)
        target = event.data.get('actor')
        
        if target:
            x = self.width * 0.75 if target == self.enemy else self.width * 0.25
            y = self.height * 0.3
            
            self.floating_texts.append(
                FloatingText(f"+{amount} HP", int(x), int(y), GREEN, self.large_font)
            )
            
    def _on_critical_hit(self, event):
        """Handle critical hit - extra visual feedback."""
        self.shake_intensity = 15
        self.shake_duration = 20
        
    def _on_status_applied(self, event):
        """Handle status effect application."""
        status_name = event.data.get('status_name', 'Unknown')

        # Prefer the CombatEvent.target object when available; fall back to data payload
        target_obj = getattr(event, 'target', None)
        target_data = event.data.get('target')

        if target_obj and hasattr(target_obj, 'name'):
            target_name = target_obj.name
        elif hasattr(target_data, 'name'):
            target_name = target_data.name  # pragma: no cover
        elif target_data:
            target_name = str(target_data)
        else:
            target_name = None

        if target_name:
            self._add_log(f"{target_name} is {status_name}!")
            
    def _add_log(self, message: str):
        """Add message to combat log."""
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log_lines:
            self.combat_log.pop(0)
            
    def _draw_character(self, character: Character, x: int, y: int, is_player: bool = True):
        """Draw a character sprite with health/mana bars."""
        # Get character sprite
        sprite = None
        if self.sprite_manager:
            sprite = self.sprite_manager.get_character_sprite(character)
            
        if sprite:
            # Draw actual sprite
            sprite_rect = sprite.get_rect(center=(x, y - 20))
            self.screen.blit(sprite, sprite_rect)
        else:
            # Fallback: Draw placeholder rectangle
            char_rect = pygame.Rect(x - 50, y - 50, 100, 100)
            color = BLUE if is_player else RED
            pygame.draw.rect(self.screen, color, char_rect, 2)
        
        # Name
        name_text = self.normal_font.render(character.name, True, WHITE)
        name_rect = name_text.get_rect(centerx=x, top=y - 80)
        self.screen.blit(name_text, name_rect)
        
        # Health bar
        bar_width = 120
        bar_height = 20
        health_percent = character.health.current / character.health.max
        
        # Background
        health_bg = pygame.Rect(x - bar_width // 2, y + 60, bar_width, bar_height)
        pygame.draw.rect(self.screen, DARK_GRAY, health_bg)
        
        # Foreground
        health_fg = pygame.Rect(x - bar_width // 2, y + 60, int(bar_width * health_percent), bar_height)
        health_color = GREEN if health_percent > 0.5 else (ORANGE if health_percent > 0.25 else RED)
        pygame.draw.rect(self.screen, health_color, health_fg)
        
        # Border
        pygame.draw.rect(self.screen, WHITE, health_bg, 2)
        
        # HP text
        hp_text = self.small_font.render(
            f"HP: {character.health.current}/{character.health.max}", True, WHITE
        )
        hp_rect = hp_text.get_rect(centerx=x, centery=y + 70)
        self.screen.blit(hp_text, hp_rect)
        
        # Mana bar
        if character.mana.max > 0:
            mana_percent = character.mana.current / character.mana.max
            
            mana_bg = pygame.Rect(x - bar_width // 2, y + 90, bar_width, bar_height)
            pygame.draw.rect(self.screen, DARK_GRAY, mana_bg)
            
            mana_fg = pygame.Rect(x - bar_width // 2, y + 90, int(bar_width * mana_percent), bar_height)
            pygame.draw.rect(self.screen, BLUE, mana_fg)
            
            pygame.draw.rect(self.screen, WHITE, mana_bg, 2)
            
            mp_text = self.small_font.render(
                f"MP: {character.mana.current}/{character.mana.max}", True, WHITE
            )
            mp_rect = mp_text.get_rect(centerx=x, centery=y + 100)
            self.screen.blit(mp_text, mp_rect)
            
        # Status effects with icons
        status_y = y + 120
        active_statuses = [name for name, effect in character.status_effects.items() if effect.active]
        if active_statuses and self.sprite_manager:
            # Draw status icons
            icon_x = x - (len(active_statuses) * 18)
            for status_name in active_statuses[:4]:  # Show up to 4 icons
                icon = self.sprite_manager.get_status_icon(status_name)
                if icon:
                    icon_rect = icon.get_rect(center=(icon_x, status_y + 10))
                    self.screen.blit(icon, icon_rect)
                    icon_x += 36
        elif active_statuses:
            # Fallback: Text display
            status_text = self.small_font.render(", ".join(active_statuses[:3]), True, GOLD)
            status_rect = status_text.get_rect(centerx=x, top=status_y)
            self.screen.blit(status_text, status_rect)
            
    def _draw_combat_log(self):
        """Draw the combat log at the bottom of the screen with scrolling support."""
        log_y = self.height - 200
        
        # Background
        log_bg = pygame.Rect(10, log_y, self.width - 20, 190)
        pygame.draw.rect(self.screen, (20, 20, 20), log_bg)
        pygame.draw.rect(self.screen, WHITE, log_bg, 2)
        
        # Title
        title = self.normal_font.render("Combat Log", True, GOLD)
        self.screen.blit(title, (20, log_y + 5))
        
        # Calculate how many lines can fit
        lines_per_page = 8
        max_scroll = max(0, len(self.combat_log) - lines_per_page)
        self.log_scroll_offset = min(self.log_scroll_offset, max_scroll)
        
        # Log messages with scrolling
        y = log_y + 35
        visible_messages = self.combat_log[self.log_scroll_offset:self.log_scroll_offset + lines_per_page]
        for message in visible_messages:
            text = self.small_font.render(message, True, LIGHT_GRAY)
            self.screen.blit(text, (20, y))
            y += 20
        
        # Scroll indicators
        if len(self.combat_log) > lines_per_page:
            if self.log_scroll_offset > 0:
                up_text = self.small_font.render("▲", True, GRAY)
                self.screen.blit(up_text, (self.width - 40, log_y + 35))
            if self.log_scroll_offset < max_scroll:
                down_text = self.small_font.render("▼", True, GRAY)
                self.screen.blit(down_text, (self.width - 40, log_y + 160))
            
    def _draw_telegraph(self):
        """Draw telegraph message if active."""
        if self.telegraph_message:
            text = self.normal_font.render(f"⚠ {self.telegraph_message}", True, ORANGE)
            rect = text.get_rect(centerx=self.width // 2, top=50)
            
            # Background box
            bg_rect = rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (40, 20, 0), bg_rect)
            pygame.draw.rect(self.screen, ORANGE, bg_rect, 2)
            
            self.screen.blit(text, rect)
            
    def _apply_screen_shake(self) -> tuple[int, int]:
        """Calculate screen shake offset."""
        if self.shake_duration > 0:
            self.shake_duration -= 1
            import random
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            return offset_x, offset_y
        return 0, 0
        
    def render_combat(self, player: Character, enemy: Character, **kwargs):
        """Render the combat screen."""
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                # Handle log scrolling
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.log_scroll_offset = max(0, self.log_scroll_offset - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    max_scroll = max(0, len(self.combat_log) - 8)
                    self.log_scroll_offset = min(max_scroll, self.log_scroll_offset + 1)
                
        # Update animations
        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]
        
        # Clear screen
        self.screen.fill(BLACK)
        
        # Apply screen shake
        shake_x, shake_y = self._apply_screen_shake()
        
        # Create a temporary surface for shake effect
        temp_surface = pygame.Surface((self.width, self.height))
        temp_surface.fill(BLACK)
        
        # Draw to temporary surface
        old_screen = self.screen
        self.screen = temp_surface
        
        # Turn number
        turn_text = self.large_font.render(f"Turn {self.turn_number}", True, GOLD)
        self.screen.blit(turn_text, (self.width // 2 - 60, 10))
        
        # Telegraph message
        self._draw_telegraph()
        
        # Characters
        self._draw_character(player, int(self.width * 0.25), int(self.height * 0.35), is_player=True)
        self._draw_character(enemy, int(self.width * 0.75), int(self.height * 0.35), is_player=False)
        
        # VS text
        vs_text = self.title_font.render("VS", True, GOLD)
        vs_rect = vs_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(vs_text, vs_rect)
        
        # Floating texts
        for floating_text in self.floating_texts:
            floating_text.draw(self.screen)
            
        # Combat log
        self._draw_combat_log()
        
        # Restore screen and apply shake
        self.screen = old_screen
        self.screen.blit(temp_surface, (shake_x, shake_y))
        
        # Update display
        pygame.display.flip()
        self.clock.tick(self.fps)
        
    def render_menu(
        self,
        title: str,
        options: list[str],
        selected_index: int = 0,
        use_grid: bool = False,
        max_visible: int | None = None,
    ) -> int:
        """Render a menu and return selected option index.
        
        Args:
            title: Menu title
            options: list of menu options
            selected_index: Initially selected option
            use_grid: If True, render options in a 2-column grid layout
        """
        selected = selected_index
        scroll_offset = 0
        
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if use_grid:
                        # Grid navigation: up/down/left/right
                        cols = 2
                        rows = (len(options) + cols - 1) // cols
                        current_row = selected // cols
                        current_col = selected % cols
                        
                        if event.key == pygame.K_UP:
                            current_row = (current_row - 1) % rows
                            selected = current_row * cols + current_col
                            if selected >= len(options):
                                selected = len(options) - 1
                        elif event.key == pygame.K_DOWN:
                            current_row = (current_row + 1) % rows
                            selected = min(current_row * cols + current_col, len(options) - 1)
                        elif event.key == pygame.K_LEFT:
                            if current_col > 0:
                                selected -= 1
                            else:
                                # Wrap to previous row, last column
                                selected = max(0, selected - 1)
                        elif event.key == pygame.K_RIGHT:
                            if current_col < cols - 1 and selected + 1 < len(options):
                                selected += 1
                            else:
                                # Wrap to next row, first column
                                selected = min(len(options) - 1, selected + 1)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            return selected
                        elif event.key == pygame.K_ESCAPE:
                            return None  # Cancel
                    else:
                        # list navigation: up/down only (supports optional scrolling window)
                        if event.key == pygame.K_UP:
                            selected = (selected - 1) % len(options)
                        elif event.key == pygame.K_DOWN:
                            selected = (selected + 1) % len(options)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            return selected
                        elif event.key == pygame.K_ESCAPE:
                            return None  # Cancel

                        # Maintain scroll window if max_visible provided
                        if not use_grid and max_visible and max_visible > 0:
                            if selected < scroll_offset:
                                scroll_offset = selected
                            elif selected >= scroll_offset + max_visible:
                                scroll_offset = selected - max_visible + 1
            
            # Render menu
            self.screen.fill(BLACK)
            
            # Title - handle multiline titles
            title_lines = title.split('\n')
            title_y = 80
            for line in title_lines:
                if line:  # Only render non-empty lines
                    title_text = self.title_font.render(line, True, GOLD)
                    title_rect = title_text.get_rect(centerx=self.width // 2, top=title_y)
                    self.screen.blit(title_text, title_rect)
                title_y += 40  # Move down for next line (or blank space)
            
            # Calculate menu start position based on title height
            menu_start_y = max(250, title_y + 30)
            
            if use_grid:
                # Grid layout - 2 columns
                cols = 2
                col_width = self.width // 3
                start_x = self.width // 2 - col_width
                start_y = menu_start_y
                row_height = 70
                
                for i, option in enumerate(options):
                    row = i // cols
                    col = i % cols
                    
                    x = start_x + col * col_width
                    y = start_y + row * row_height
                    
                    color = GOLD if i == selected else WHITE
                    option_text = self.large_font.render(option, True, color)
                    
                    # Draw selection box if selected
                    if i == selected:
                        box_rect = pygame.Rect(x - 10, y - 5, col_width - 20, 50)
                        pygame.draw.rect(self.screen, DARK_GRAY, box_rect, 2)
                    
                    option_rect = option_text.get_rect(left=x, centery=y + 20)
                    self.screen.blit(option_text, option_rect)
            else:
                # list layout with optional vertical scrolling
                y = menu_start_y
                visible_start = scroll_offset if (max_visible and max_visible > 0) else 0
                visible_end = visible_start + max_visible if (max_visible and max_visible > 0) else len(options)
                for i in range(visible_start, min(visible_end, len(options))):
                    option = options[i]
                    color = GOLD if i == selected else WHITE
                    option_text = self.large_font.render(option, True, color)
                    option_rect = option_text.get_rect(centerx=self.width // 2, top=y)
                    self.screen.blit(option_text, option_rect)
                    y += 60

                # Scroll indicators
                if max_visible and len(options) > max_visible:
                    if scroll_offset > 0:
                        up_text = self.small_font.render("▲", True, GRAY)
                        up_rect = up_text.get_rect(centerx=self.width // 2, top=210)
                        self.screen.blit(up_text, up_rect)
                    if scroll_offset + max_visible < len(options):
                        down_text = self.small_font.render("▼", True, GRAY)
                        down_rect = down_text.get_rect(centerx=self.width // 2, top=y)
                        self.screen.blit(down_text, down_rect)
            
            # Instructions
            if use_grid:
                help_text = self.small_font.render("Arrow Keys: Navigate  ENTER: Select  ESC: Cancel", True, GRAY)
            else:
                nav_hint = "UP/DOWN" if not max_visible else "UP/DOWN (scroll)"
                help_text = self.small_font.render(f"{nav_hint}: Navigate  ENTER: Select  ESC: Cancel", True, GRAY)
            help_rect = help_text.get_rect(centerx=self.width // 2, bottom=self.height - 20)
            self.screen.blit(help_text, help_rect)
                
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS for menus
        
    def show_message(self, message: str, title: str = ""):
        """Display a message box and wait for keypress."""
        self.screen.fill(BLACK)
        
        if title:
            title_text = self.title_font.render(title, True, GOLD)
            title_rect = title_text.get_rect(centerx=self.width // 2, top=200)
            self.screen.blit(title_text, title_rect)
            y = 300
        else:
            y = 250
            
        # Handle explicit newlines first, then word wrap each paragraph
        lines = []
        for paragraph in message.split('\n'):
            if not paragraph.strip():
                # Empty line - preserve spacing
                lines.append("")
                continue
                
            # Wrap this paragraph
            words = paragraph.split()
            current_line = []
            for word in words:
                current_line.append(word)
                test_line = " ".join(current_line)
                if self.normal_font.size(test_line)[0] > self.width - 100:
                    current_line.pop()
                    if current_line:  # Avoid empty lines from long words
                        lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))
            
        for line in lines:
            if line:  # Only render non-empty lines
                text = self.normal_font.render(line, True, WHITE)
                text_rect = text.get_rect(centerx=self.width // 2, top=y)
                self.screen.blit(text, text_rect)
            y += 40
        
        # Instructions
        help_text = self.small_font.render("Press any key to continue...", True, GRAY)
        help_rect = help_text.get_rect(centerx=self.width // 2, bottom=self.height - 20)
        self.screen.blit(help_text, help_rect)
            
        pygame.display.flip()
        
        # Wait for keypress
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            self.clock.tick(30)

    def show_progress_popup(self, header: str = "Load Game", message: str = "Loading game file...",
                             steps: int = 20, total_time: float = 3.0):
        """Show a centered popup with a progress bar, similar to curses version.

        Args:
            header: Title shown at the top of the popup
            message: Message shown above the progress bar
            steps: Number of increments to animate
            total_time: Total time in seconds to animate the bar
        """
        import time

        # Popup dimensions and position
        popup_width = max(420, self.width // 2 - 100)
        popup_height = 180
        popup_x = (self.width - popup_width) // 2
        popup_y = (self.height - popup_height) // 2

        # Progress bar geometry
        bar_margin = 20
        bar_rect = pygame.Rect(
            popup_x + bar_margin,
            popup_y + popup_height - 60,
            popup_width - 2 * bar_margin,
            24,
        )

        # Calculate delay per step
        delay = total_time / max(1, steps)

        # Animate progress
        for i in range(steps + 1):
            # Handle window events to keep UI responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

            # Dim background
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            # Popup background
            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
            pygame.draw.rect(self.screen, (20, 20, 20), popup_rect)
            pygame.draw.rect(self.screen, WHITE, popup_rect, 2)

            # Header
            header_text = self.normal_font.render(header, True, GOLD)
            header_rect = header_text.get_rect(centerx=popup_rect.centerx, top=popup_y + 12)
            self.screen.blit(header_text, header_rect)

            # Message
            msg_text = self.small_font.render(message, True, WHITE)
            msg_rect = msg_text.get_rect(centerx=popup_rect.centerx, top=popup_y + 60)
            self.screen.blit(msg_text, msg_rect)

            # Progress bar background and border
            pygame.draw.rect(self.screen, DARK_GRAY, bar_rect)
            pygame.draw.rect(self.screen, WHITE, bar_rect, 2)

            # Filled portion
            filled_width = int((bar_rect.width - 4) * (i / max(1, steps)))
            if filled_width > 0:
                filled_rect = pygame.Rect(bar_rect.left + 2, bar_rect.top + 2, filled_width, bar_rect.height - 4)
                pygame.draw.rect(self.screen, GRAY, filled_rect)

            pygame.display.flip()
            if not self.debug_mode:
                time.sleep(delay)
        
    def cleanup(self):
        """Clean up Pygame resources."""
        pygame.quit()
        
    # Abstract method implementations
    def initialize(self):
        """Initialize the presenter."""
        pass  # Already initialized in __init__
        
    def clear(self):
        """Clear the screen."""
        self.screen.fill(BLACK)
        
    def update(self):
        """Update the display."""
        pygame.display.flip()
        self.clock.tick(self.fps)

    def set_background_provider(self, provider: Callable[[], pygame.Surface] | None) -> None:
        """Set a callable that returns the most recent scene background."""
        self._background_provider = provider

    def get_background_surface(self) -> pygame.Surface:
        """Return the latest cached background surface for popup overlays."""
        if self._background_provider is None:
            return self.screen.copy()

        try:
            surface = self._background_provider()
        except Exception:
            return self.screen.copy()

        if surface is None or surface is self.screen:
            return self.screen.copy()

        return surface
        
    def get_player_action(self, prompt: str, options: list[str]) -> str:
        """Get player action through menu."""
        selected = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return options[selected]
                        
            self.render_menu(prompt, options, selected)
            
    def get_text_input(self, prompt: str, default: str = "", default_text: str = None) -> str:
        """Get text input from player."""
        # Support both 'default' and 'default_text' for compatibility
        if default_text is not None:
            default = default_text
        text = default
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return text if text else default
                    elif event.key == pygame.K_ESCAPE:
                        return default
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        if len(text) < 20:  # Max length
                            text += event.unicode
            
            # Render
            self.screen.fill(BLACK)
            
            # Prompt
            prompt_text = self.large_font.render(prompt, True, WHITE)
            prompt_rect = prompt_text.get_rect(centerx=self.width // 2, top=200)
            self.screen.blit(prompt_text, prompt_rect)
            
            # Input box
            input_text = self.normal_font.render(text + "_", True, GOLD)
            input_rect = input_text.get_rect(centerx=self.width // 2, top=300)
            self.screen.blit(input_text, input_rect)
            
            # Instructions
            help_text = self.small_font.render("ENTER: Confirm  ESC: Cancel", True, GRAY)
            help_rect = help_text.get_rect(centerx=self.width // 2, bottom=self.height - 20)
            self.screen.blit(help_text, help_rect)
            
            pygame.display.flip()
            self.clock.tick(30)
        
    def confirm(self, message: str) -> bool:
        """Show confirmation dialog."""
        return self.get_player_action(message, ["Yes", "No"]) == "Yes"
        
    def show_dialogue(self, speaker: str, text: str):
        """Show dialogue box."""
        self.show_message(text, speaker)
        # Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    waiting = False
            self.clock.tick(30)
            
    def render_map(self, game_map: Any, player_position: tuple[int, int]):
        """Render the game map."""
        # Placeholder - would need tile graphics
        self.screen.fill(BLACK)
        text = self.large_font.render("Map View (Not Implemented)", True, WHITE)
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        
    def render_character_sheet(self, character: Character):
        """Render character sheet/stats."""
        self.screen.fill(BLACK)
        
        # Title
        title = self.title_font.render(character.name, True, GOLD)
        self.screen.blit(title, (50, 50))
        
        y = 150
        # Stats
        stats_info = [
            f"Level: {character.level.level}",
            f"HP: {character.health.current}/{character.health.max}",
            f"MP: {character.mana.current}/{character.mana.max}",
            f"STR: {character.stats.strength}",
            f"INT: {character.stats.intel}",
            f"WIS: {character.stats.wisdom}",
            f"CON: {character.stats.con}",
            f"DEX: {character.stats.dex}",
            f"CHA: {character.stats.charisma}",
        ]
        
        for info in stats_info:
            text = self.normal_font.render(info, True, WHITE)
            self.screen.blit(text, (50, y))
            y += 35
            
        pygame.display.flip()


if __name__ == "__main__":
    # Quick test
    presenter = PygamePresenter()
    
    # Create mock characters for testing
    from src.core.character import Character, Stats, Combat, Resource
    
    stats = Stats(strength=15, intel=10, wisdom=10, con=15, charisma=10, dex=12)
    combat_stats = Combat(attack=10, defense=8, magic=5, magic_def=5)
    health = Resource(current=80, max=100)
    mana = Resource(current=30, max=50)
    
    player = Character("Hero", health, mana, stats, combat_stats)
    player.status_effects = {'Stun': type('SE', (), {'active': False})()}
    
    enemy_health = Resource(current=60, max=80)
    enemy_mana = Resource(current=0, max=0)
    enemy = Character("Goblin", enemy_health, enemy_mana, stats, combat_stats)
    enemy.status_effects = {'Stun': type('SE', (), {'active': False})()}
    
    # Test render for a few frames
    presenter.player = player
    presenter.enemy = enemy
    presenter.turn_number = 1
    presenter._add_log("Combat begins!")
    presenter._add_log("Hero attacks Goblin for 15 damage!")
    
    import time
    for _ in range(180):  # 3 seconds at 60 FPS
        presenter.render_combat(player, enemy)
        time.sleep(1/60)
        
    presenter.cleanup()
