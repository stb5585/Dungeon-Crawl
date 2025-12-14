"""
Pygame-based presenter for Dungeon Crawl combat.

This presenter implements the GamePresenter interface using Pygame for graphical combat display.
It subscribes to the event system for animations and real-time updates.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Tuple
import pygame
from presentation.interface import GamePresenter
from events import get_event_bus, EventType

if TYPE_CHECKING:
    from character import Character
    from items import Item

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
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
    
    def __init__(self, text: str, x: int, y: int, color: Tuple[int, int, int], font: pygame.font.Font):
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
        pygame.display.set_caption("Dungeon Crawl - Combat")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.large_font = pygame.font.Font(None, 36)
        self.normal_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Combat state
        self.player: Optional[Character] = None
        self.enemy: Optional[Character] = None
        self.turn_number: int = 0
        self.telegraph_message: Optional[str] = None
        
        # Animations
        self.floating_texts: List[FloatingText] = []
        self.shake_intensity = 0
        self.shake_duration = 0
        
        # Event system
        self.event_bus = get_event_bus()
        self._subscribe_to_events()
        
        # Combat log
        self.combat_log: List[str] = []
        self.max_log_lines = 10
        
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
        target = event.data.get('target')
        
        if target:
            self._add_log(f"{target.name} is {status_name}!")
            
    def _add_log(self, message: str):
        """Add message to combat log."""
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log_lines:
            self.combat_log.pop(0)
            
    def _draw_character(self, character: Character, x: int, y: int, is_player: bool = True):
        """Draw a character sprite with health/mana bars."""
        # Character placeholder (will be replaced with sprites later)
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
            
        # Status effects (icons placeholder)
        status_y = y + 120
        active_statuses = [name for name, effect in character.status_effects.items() if effect.active]
        if active_statuses:
            status_text = self.small_font.render(", ".join(active_statuses[:3]), True, YELLOW)
            status_rect = status_text.get_rect(centerx=x, top=status_y)
            self.screen.blit(status_text, status_rect)
            
    def _draw_combat_log(self):
        """Draw the combat log at the bottom of the screen."""
        log_y = self.height - 200
        
        # Background
        log_bg = pygame.Rect(10, log_y, self.width - 20, 190)
        pygame.draw.rect(self.screen, (20, 20, 20), log_bg)
        pygame.draw.rect(self.screen, WHITE, log_bg, 2)
        
        # Title
        title = self.normal_font.render("Combat Log", True, YELLOW)
        self.screen.blit(title, (20, log_y + 5))
        
        # Log messages
        y = log_y + 35
        for message in self.combat_log[-8:]:  # Show last 8 messages
            text = self.small_font.render(message, True, LIGHT_GRAY)
            self.screen.blit(text, (20, y))
            y += 20
            
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
            
    def _apply_screen_shake(self) -> Tuple[int, int]:
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
        turn_text = self.large_font.render(f"Turn {self.turn_number}", True, YELLOW)
        self.screen.blit(turn_text, (self.width // 2 - 60, 10))
        
        # Telegraph message
        self._draw_telegraph()
        
        # Characters
        self._draw_character(player, int(self.width * 0.25), int(self.height * 0.35), is_player=True)
        self._draw_character(enemy, int(self.width * 0.75), int(self.height * 0.35), is_player=False)
        
        # VS text
        vs_text = self.title_font.render("VS", True, YELLOW)
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
        
    def render_menu(self, title: str, options: List[str], selected: int = 0) -> int:
        """Render a menu and return selected option."""
        # This is a simplified version - you'll need to add proper input handling
        self.screen.fill(BLACK)
        
        # Title
        title_text = self.title_font.render(title, True, YELLOW)
        title_rect = title_text.get_rect(centerx=self.width // 2, top=100)
        self.screen.blit(title_text, title_rect)
        
        # Options
        y = 250
        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            option_text = self.large_font.render(option, True, color)
            option_rect = option_text.get_rect(centerx=self.width // 2, top=y)
            self.screen.blit(option_text, option_rect)
            y += 60
            
        pygame.display.flip()
        return selected
        
    def show_message(self, message: str, title: str = ""):
        """Display a message box."""
        self.screen.fill(BLACK)
        
        if title:
            title_text = self.title_font.render(title, True, YELLOW)
            title_rect = title_text.get_rect(centerx=self.width // 2, top=200)
            self.screen.blit(title_text, title_rect)
            y = 300
        else:
            y = 250
            
        # Wrap message
        words = message.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            if self.normal_font.size(test_line)[0] > self.width - 100:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
            
        for line in lines:
            text = self.normal_font.render(line, True, WHITE)
            text_rect = text.get_rect(centerx=self.width // 2, top=y)
            self.screen.blit(text, text_rect)
            y += 40
            
        pygame.display.flip()
        
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
        
    def get_player_action(self, prompt: str, options: List[str]) -> str:
        """Get player action through menu."""
        selected = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return options[selected]
                        
            self.render_menu(prompt, options, selected)
            
    def get_text_input(self, prompt: str, default: str = "") -> str:
        """Get text input from player."""
        # Simplified - returns default for now
        # Full implementation would need text input handling
        return default
        
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
            
    def render_map(self, game_map: Any, player_position: Tuple[int, int]):
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
        title = self.title_font.render(character.name, True, YELLOW)
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
    from character import Character, Stats, Combat, Resource
    
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
