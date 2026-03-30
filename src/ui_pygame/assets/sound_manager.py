"""
Sound Manager - Handles sound effects and music for Dungeon Crawl.

Integrates with the event bus to play sounds based on game events.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pygame.mixer

from src.core.events.event_bus import EventBus, EventType


logger = logging.getLogger(__name__)


class SoundManager:
    """Manages sound effects and background music."""

    def __init__(
        self,
        assets_dir: str = "src/ui_pygame/assets",
        event_bus: EventBus | None = None,
    ):
        """
        Initialize sound manager.

        Args:
            assets_dir: Base directory for assets
            event_bus: Event bus for subscribing to game events
        """
        self.assets_dir = Path(assets_dir)
        self.sounds_dir = self.assets_dir / "sounds"
        self.music_dir = self.assets_dir / "music"
        
        # Sound caches
        self.sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self.current_music: str | None = None
        
        # Volume settings (0.0 to 1.0)
        self.master_volume = 1.0
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        self.enabled = True
        
        # Event bus integration
        self.event_bus = event_bus
        
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512
                )
                logger.info("Pygame mixer initialized")
            except pygame.error as e:
                logger.error(f"Failed to initialize pygame mixer: {e}")
                self.enabled = False
                return
        
        # Set channel count for simultaneous sounds
        pygame.mixer.set_num_channels(16)
        
        if self.event_bus:
            self._subscribe_to_events()
        
        logger.info("SoundManager initialized")

    def _subscribe_to_events(self):
        """Subscribe to combat and game events."""
        if not self.event_bus:
            return
            
        # Combat events
        self.event_bus.subscribe(EventType.COMBAT_START, self._on_combat_start)
        self.event_bus.subscribe(EventType.COMBAT_END, self._on_combat_end)
        self.event_bus.subscribe(EventType.DAMAGE_DEALT, self._on_damage_dealt)
        self.event_bus.subscribe(EventType.HEALING_DONE, self._on_healing)
        self.event_bus.subscribe(EventType.SPELL_CAST, self._on_spell_cast)
        self.event_bus.subscribe(EventType.SKILL_USE, self._on_skill_use)
        self.event_bus.subscribe(EventType.STATUS_APPLIED, self._on_status_applied)
        self.event_bus.subscribe(EventType.CHARACTER_DEATH, self._on_death)
        self.event_bus.subscribe(EventType.LEVEL_UP, self._on_level_up)
        
        logger.info("SoundManager subscribed to events")

    def _on_combat_start(self, event):
        """Handle combat start event."""
        self.play_sfx("combat_start")

    def _on_combat_end(self, event):
        """Handle combat end event."""
        if event.data.get('player_alive'):
            self.play_sfx("victory")
        elif event.data.get('fled'):
            self.play_sfx("flee")
        else:
            self.play_sfx("defeat")

    def _on_damage_dealt(self, event):
        """Handle damage dealt event."""
        is_crit = event.data.get('crit', False)
        damage = event.data.get('damage', 0)
        
        if is_crit:
            self.play_sfx("critical_hit", volume=1.0)
        elif damage > 50:
            self.play_sfx("heavy_hit")
        else:
            self.play_sfx("hit")

    def _on_healing(self, event):
        """Handle healing event."""
        self.play_sfx("heal")

    def _on_spell_cast(self, event):
        """Handle spell cast event."""
        spell_name = event.data.get('spell_name', event.data.get('ability_name', ''))
        
        # Map spells to sound effects
        if 'fire' in spell_name.lower():
            self.play_sfx("spell_fire")
        elif 'ice' in spell_name.lower() or 'frost' in spell_name.lower():
            self.play_sfx("spell_ice")
        elif 'lightning' in spell_name.lower() or 'shock' in spell_name.lower():
            self.play_sfx("spell_lightning")
        elif 'heal' in spell_name.lower():
            self.play_sfx("spell_heal")
        else:
            self.play_sfx("spell_cast")
    
    def _on_skill_use(self, event):
        """Handle skill use event."""
        skill_name = event.data.get('skill_name', event.data.get('ability_name', ''))
        
        # Map skills to sound effects
        if 'fire' in skill_name.lower():
            self.play_sfx("spell_fire")
        elif 'ice' in skill_name.lower() or 'frost' in skill_name.lower():
            self.play_sfx("spell_ice")
        elif 'lightning' in skill_name.lower() or 'shock' in skill_name.lower():
            self.play_sfx("spell_lightning")
        elif 'heal' in skill_name.lower():
            self.play_sfx("spell_heal")
        else:
            self.play_sfx("spell_cast")

    def _on_status_applied(self, event):
        """Handle status effect applied event."""
        status_name = event.data.get('status_name', '').lower()
        
        if 'poison' in status_name or 'bleed' in status_name:
            self.play_sfx("poison")
        elif 'stun' in status_name or 'freeze' in status_name:
            self.play_sfx("stun")
        elif 'burn' in status_name:
            self.play_sfx("burn")

    def _on_death(self, event):
        """Handle death event."""
        is_player = event.data.get('is_player', False)
        
        if is_player:
            self.play_sfx("player_death")
        else:
            self.play_sfx("enemy_death")

    def _on_level_up(self, event):
        """Handle level up event."""
        self.play_sfx("level_up")

    def load_sfx(self, sound_name: str) -> pygame.mixer.Sound | None:
        """
        Load a sound effect from cache or file.

        Args:
            sound_name: Name of the sound file (without extension)

        Returns:
            Pygame Sound object or None if not found
        """
        if not self.enabled:
            return None
            
        # Check cache first
        if sound_name in self.sfx_cache:
            return self.sfx_cache[sound_name]
        
        # Try to load from file
        sound_path = self.sounds_dir / f"{sound_name}.wav"
        if not sound_path.exists():
            sound_path = self.sounds_dir / f"{sound_name}.ogg"
        
        if not sound_path.exists():
            logger.debug(f"Sound file not found: {sound_name}")
            return None
        
        try:
            sound = pygame.mixer.Sound(str(sound_path))
            self.sfx_cache[sound_name] = sound
            logger.debug(f"Loaded sound: {sound_name}")
            return sound
        except pygame.error as e:
            logger.error(f"Failed to load sound {sound_name}: {e}")
            return None

    def play_sfx(self, sound_name: str, volume: float | None = None, loops: int = 0):
        """
        Play a sound effect.

        Args:
            sound_name: Name of the sound to play
            volume: Optional volume override (0.0 to 1.0)
            loops: Number of additional times to play (-1 for infinite)
        """
        if not self.enabled:
            return
            
        sound = self.load_sfx(sound_name)
        if sound is None:
            return
        
        # Calculate final volume
        if volume is None:
            volume = self.sfx_volume
        final_volume = volume * self.master_volume
        
        sound.set_volume(final_volume)
        sound.play(loops=loops)

    def play_music(self, music_name: str, loops: int = -1, fade_ms: int = 1000):
        """
        Play background music.

        Args:
            music_name: Name of the music file (without extension)
            loops: Number of times to loop (-1 for infinite)
            fade_ms: Fade in duration in milliseconds
        """
        if not self.enabled:
            return
            
        music_path = self.music_dir / f"{music_name}.ogg"
        if not music_path.exists():
            music_path = self.music_dir / f"{music_name}.mp3"
        
        if not music_path.exists():
            logger.debug(f"Music file not found: {music_name}")
            return
        
        try:
            # Stop current music with fade out
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms // 2)
            
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            self.current_music = music_name
            logger.info(f"Playing music: {music_name}")
        except pygame.error as e:
            logger.error(f"Failed to play music {music_name}: {e}")

    def stop_music(self, fade_ms: int = 1000):
        """
        Stop background music.

        Args:
            fade_ms: Fade out duration in milliseconds
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
            self.current_music = None

    def pause_music(self):
        """Pause background music."""
        pygame.mixer.music.pause()

    def resume_music(self):
        """Resume background music."""
        pygame.mixer.music.unpause()

    def set_master_volume(self, volume: float):
        """
        Set master volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def set_sfx_volume(self, volume: float):
        """
        Set sound effects volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float):
        """
        Set music volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def enable(self):
        """Enable sound system."""
        self.enabled = True

    def disable(self):
        """Disable sound system."""
        self.enabled = False
        self.stop_music(fade_ms=0)
        pygame.mixer.stop()

    def cleanup(self):
        """Clean up sound resources."""
        self.stop_music(fade_ms=0)
        self.sfx_cache.clear()
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        logger.info("SoundManager cleaned up")


# Singleton instance
_sound_manager: SoundManager | None = None


def get_sound_manager(
    assets_dir: str = "src/ui_pygame/assets",
    event_bus: EventBus | None = None,
) -> SoundManager:
    """Get or create the singleton sound manager instance."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager(assets_dir=assets_dir, event_bus=event_bus)
    return _sound_manager
