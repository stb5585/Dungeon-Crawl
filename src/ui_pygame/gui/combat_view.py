"""
GUI Combat View for Pygame-based first-person combat.
Integrates with BattleManager or EnhancedBattleManager for combat logic.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

import pygame

from src.core.classes import astromancer
from src.ui_pygame.assets.enemy_combat_sprite_manager import (
    EnemyCombatSpriteManager,
    get_enemy_combat_sprite_manager,
)
from src.ui_pygame.assets.enemy_token_manager import get_enemy_token_manager
from src.ui_pygame.assets.player_token_manager import get_player_token_manager

from .status_icons import (
    STATUS_ICON_COLORS,
    combine_duplicate_status_icons,
    compact_status_icons,
    fit_status_icon_label,
    load_status_icon_surface,
    prioritize_status_icons,
    stat_effect_status_icon,
    status_icon_color,
    status_icon_stack_count,
    totem_status_icons,
)

ASSETS_BASE_DIR = Path(__file__).resolve().parents[1] / "assets"


@dataclass
class CombatImpactEffect:
    """Brief procedural combat polish drawn over the current battlefield."""

    target: str
    kind: str
    color: tuple[int, int, int]
    start_ms: int
    duration_ms: int = 420
    critical: bool = False


@dataclass
class FloatingCombatText:
    """Small transient combat result text anchored near a target."""

    target: str
    text: str
    color: tuple[int, int, int]
    start_ms: int
    duration_ms: int = 760


@dataclass(frozen=True)
class CombatLogLine:
    """A render-ready combat log fragment with source-message styling."""

    text: str
    color: tuple[int, int, int]
    marker_color: tuple[int, int, int]
    continuation: bool = False


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
            'action_border': (118, 116, 126),
            'panel_accent': (166, 132, 74),
            'message_bg': (30, 30, 35),
            'turn_player': (70, 130, 210),
            'turn_enemy': (180, 80, 70),
            'telegraph': (255, 205, 110),
            'log_damage': (235, 120, 105),
            'log_heal': (120, 210, 135),
            'log_muted': (175, 175, 180),
            'log_player': (50, 150, 250),
            'log_enemy': (200, 50, 50),
        }
        
        # Combat log
        self.combat_log = []
        self.max_log_lines = 200
        self.log_lines_per_page = 5
        self.log_scroll_offset = 0
        self._active_telegraph_line: str | None = None
        self._suppress_logged_telegraph_banner = False
        self._combat_log_player_name: str | None = None
        self._combat_log_enemy_name: str | None = None
        self._combat_log_revision = 0
        self._combat_log_wrap_cache: dict[tuple[int, int, bool, int], list[CombatLogLine]] = {}

        # Status icon colors
        self.status_colors = STATUS_ICON_COLORS
        
        # Sprite animators (per enemy instance)
        self.sprite_animators = {}  # Key by enemy id()
        self.enemy_visual_offset = (0, 0)
        self._active_impact_effects: list[CombatImpactEffect] = []
        self._active_float_texts: list[FloatingCombatText] = []
        self._transient_smoke_visuals: dict[str, int] = {}
        self._enemy_recoil_until_ms = 0
        self._last_enemy_target_rect = pygame.Rect(
            self.combat_width // 2 - 120,
            self.combat_height // 3 - 120,
            240,
            240,
        )
        self._last_player_target_rect = pygame.Rect(
            28,
            self.screen_height - 270,
            220,
            110,
        )
        self._hide_enemy_for_flee = False
        self.enemy_combat_sprite_manager = get_enemy_combat_sprite_manager()
        self.enemy_token_manager = get_enemy_token_manager()
        self.player_token_manager = get_player_token_manager()

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
        self._prune_impact_effects()
        self._prune_float_texts()
    
    def enemy_take_damage(self, enemy):
        """Trigger damage flash when enemy takes damage."""
        animator = self._get_sprite_animator(enemy)
        animator.trigger_damage()
        self._enemy_recoil_until_ms = max(self._enemy_recoil_until_ms, pygame.time.get_ticks() + 220)

    def trigger_impact_effect(
        self,
        target: str,
        kind: str = "weapon",
        element: str | None = None,
        critical: bool = False,
    ) -> None:
        """Start a short hit/spell effect at the last known target location."""
        self._active_impact_effects.append(
            CombatImpactEffect(
                target=target,
                kind=kind,
                color=self._impact_color(kind, element),
                start_ms=pygame.time.get_ticks(),
                duration_ms=520 if critical else 420,
                critical=critical,
            )
        )

    def trigger_floating_text(
        self,
        target: str,
        text: str,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        """Start a brief floating combat result label."""
        if not text:
            return
        self._active_float_texts.append(
            FloatingCombatText(
                target=target,
                text=str(text),
                color=color or self.colors["text"],
                start_ms=pygame.time.get_ticks(),
            )
        )

    def trigger_smoke_screen_visual(self, target: str, duration_ms: int = 900) -> None:
        """Show the smoke cloud briefly for instant Smoke Screen escapes."""
        if target not in {"enemy", "player"}:
            return
        self._transient_smoke_visuals[target] = pygame.time.get_ticks() + max(1, int(duration_ms))

    def hide_enemy_for_flee(self) -> None:
        """Keep the enemy hidden after a smoke-screen escape until combat cleanup."""
        self._hide_enemy_for_flee = True

    def _transient_smoke_active(self, target: str) -> bool:
        until_ms = self._transient_smoke_visuals.get(target, 0)
        if until_ms <= 0:
            return False
        if pygame.time.get_ticks() <= until_ms:
            return True
        self._transient_smoke_visuals.pop(target, None)
        return False
    
    def enemy_dies(self, enemy):
        """Trigger death animation when enemy dies."""
        animator = self._get_sprite_animator(enemy)
        animator.trigger_death()
        
    def add_combat_message(self, message):
        """Add a message to the combat log."""
        cleaned_lines = self._filter_status_message(str(message))
        if not cleaned_lines:
            return
        has_telegraph_line = any(self._is_telegraph_message(line) for line in cleaned_lines)
        if not has_telegraph_line:
            self._active_telegraph_line = None
            self._suppress_logged_telegraph_banner = True
        was_at_bottom = self.log_scroll_offset >= self._max_log_scroll()
        for line in cleaned_lines:
            if self._is_telegraph_message(line):
                line = self._short_telegraph_message(line)
                self._active_telegraph_line = line
                self._suppress_logged_telegraph_banner = False
            self.combat_log.append(line)
        while len(self.combat_log) > self.max_log_lines:
            self.combat_log.pop(0)
        self._invalidate_combat_log_wrap_cache()
        if was_at_bottom:
            self.log_scroll_offset = self._max_log_scroll()
        else:
            self.log_scroll_offset = min(self.log_scroll_offset, self._max_log_scroll())

    def _max_log_scroll(self):
        display_lines = self._wrapped_combat_log_lines(self.combat_width - 30)
        return max(0, len(display_lines) - self.log_lines_per_page)

    def scroll_log(self, delta: int):
        """Scroll combat log by delta lines (negative=older, positive=newer)."""
        self.log_scroll_offset = max(0, min(self._max_log_scroll(), self.log_scroll_offset + delta))

    def reset_combat_log(self):
        """Clear combat log history and reset scrolling."""
        self.combat_log.clear()
        self.log_scroll_offset = 0
        self._active_telegraph_line = None
        self._suppress_logged_telegraph_banner = False
        self._hide_enemy_for_flee = False
        self._invalidate_combat_log_wrap_cache()

    def _prune_impact_effects(self) -> None:
        if not self._active_impact_effects:
            return
        now = pygame.time.get_ticks()
        self._active_impact_effects = [
            effect
            for effect in self._active_impact_effects
            if now - effect.start_ms < effect.duration_ms
        ]

    def _prune_float_texts(self) -> None:
        if not self._active_float_texts:
            return
        now = pygame.time.get_ticks()
        self._active_float_texts = [
            text
            for text in self._active_float_texts
            if now - text.start_ms < text.duration_ms
        ]

    def _enemy_recoil_offset(self) -> int:
        remaining = max(0, self._enemy_recoil_until_ms - pygame.time.get_ticks())
        if remaining <= 0:
            return 0
        phase = remaining / 220
        return int(math.sin(phase * math.pi * 5) * 8 * phase)

    @staticmethod
    def _impact_color(kind: str, element: str | None = None) -> tuple[int, int, int]:
        element_colors = {
            "Fire": (226, 92, 42),
            "Ice": (150, 206, 230),
            "Electric": (236, 210, 88),
            "Water": (82, 150, 192),
            "Earth": (150, 112, 70),
            "Wind": (178, 205, 182),
            "Poison": (118, 168, 86),
            "Holy": (232, 218, 162),
            "Dark": (142, 104, 174),
            "Death": (156, 144, 128),
        }
        if element in element_colors:
            return element_colors[element]
        if kind == "spell":
            return (178, 142, 222)
        if kind == "skill":
            return (210, 148, 82)
        return (218, 185, 128)

    def _target_rect_for_effect(self, target: str) -> pygame.Rect:
        if target == "player":
            return self._last_player_target_rect.copy()
        return self._last_enemy_target_rect.copy()

    def _render_active_impact_effects(self) -> None:
        if not self._active_impact_effects:
            return
        now = pygame.time.get_ticks()
        for effect in list(self._active_impact_effects):
            progress = (now - effect.start_ms) / max(1, effect.duration_ms)
            if progress >= 1:
                continue
            rect = self._target_rect_for_effect(effect.target)
            if effect.kind == "spell":
                self._draw_spell_impact(rect, effect, progress)
            elif effect.kind == "skill":
                self._draw_skill_impact(rect, effect, progress)
            elif effect.kind == "reflect":
                self._draw_reflect_impact(rect, effect, progress)
            elif effect.kind == "status":
                self._draw_status_impact(rect, effect, progress)
            elif effect.kind == "elemental_strike":
                self._draw_elemental_strike_impact(rect, effect, progress)
            else:
                self._draw_weapon_impact(rect, effect, progress)
        self._prune_impact_effects()

    def _render_floating_texts(self) -> None:
        if not self._active_float_texts:
            return
        now = pygame.time.get_ticks()
        font = pygame.font.Font(None, 28)
        for text in list(self._active_float_texts):
            progress = (now - text.start_ms) / max(1, text.duration_ms)
            if progress >= 1:
                continue
            alpha = int(230 * (1.0 - progress))
            if alpha <= 0:
                continue
            rect = self._target_rect_for_effect(text.target)
            surf = font.render(text.text, True, text.color)
            surf.set_alpha(alpha)
            shadow = font.render(text.text, True, (0, 0, 0))
            shadow.set_alpha(max(0, alpha - 50))
            y_offset = int(34 * progress)
            text_rect = surf.get_rect(center=(rect.centerx, rect.top - 18 - y_offset))
            shadow_rect = shadow.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
            self.screen.blit(shadow, shadow_rect)
            self.screen.blit(surf, text_rect)
        self._prune_float_texts()

    def _draw_weapon_impact(self, rect: pygame.Rect, effect: CombatImpactEffect, progress: float) -> None:
        alpha = int(190 * (1.0 - progress))
        if alpha <= 0:
            return
        overlay = pygame.Surface(rect.inflate(80, 80).size, pygame.SRCALPHA)
        color = (*effect.color, alpha)
        width = 5 if effect.critical else 3
        slash_shift = int(progress * 42)
        pygame.draw.line(
            overlay,
            color,
            (overlay.get_width() // 2 - 54 + slash_shift, overlay.get_height() // 2 - 36),
            (overlay.get_width() // 2 + 54 + slash_shift, overlay.get_height() // 2 + 24),
            width,
        )
        pygame.draw.line(
            overlay,
            (*effect.color, max(40, alpha // 2)),
            (overlay.get_width() // 2 - 36, overlay.get_height() // 2 + 28),
            (overlay.get_width() // 2 + 38, overlay.get_height() // 2 - 28),
            2,
        )
        for index in range(5):
            spark_alpha = max(0, alpha - index * 18)
            spark_x = overlay.get_width() // 2 + index * 14 - 30
            spark_y = overlay.get_height() // 2 - int(progress * 36) + ((index % 2) * 14)
            pygame.draw.circle(overlay, (*effect.color, spark_alpha), (spark_x, spark_y), max(2, 5 - index // 2))
        self.screen.blit(overlay, overlay.get_rect(center=rect.center))

    def _draw_skill_impact(self, rect: pygame.Rect, effect: CombatImpactEffect, progress: float) -> None:
        alpha = int(150 * (1.0 - progress))
        if alpha <= 0:
            return
        overlay = pygame.Surface(rect.inflate(100, 70).size, pygame.SRCALPHA)
        center = (overlay.get_width() // 2, overlay.get_height() // 2)
        radius = int(22 + progress * 48)
        pygame.draw.circle(overlay, (*effect.color, max(25, alpha // 2)), center, radius, 2)
        for angle in (0, math.pi / 3, math.pi * 2 / 3):
            dx = int(math.cos(angle) * (radius + 12))
            dy = int(math.sin(angle) * (radius // 2))
            pygame.draw.line(overlay, (*effect.color, alpha), (center[0] - dx, center[1] - dy), (center[0] + dx, center[1] + dy), 2)
        self.screen.blit(overlay, overlay.get_rect(center=rect.center))

    def _draw_spell_impact(self, rect: pygame.Rect, effect: CombatImpactEffect, progress: float) -> None:
        alpha = int(170 * (1.0 - progress))
        if alpha <= 0:
            return
        overlay = pygame.Surface(rect.inflate(120, 120).size, pygame.SRCALPHA)
        center = (overlay.get_width() // 2, overlay.get_height() // 2)
        glow_radius = int(28 + progress * 62)
        pygame.draw.circle(overlay, (*effect.color, max(24, alpha // 3)), center, glow_radius)
        pygame.draw.circle(overlay, (*effect.color, alpha), center, max(8, glow_radius // 3), 2)
        for index in range(8):
            angle = (math.pi * 2 * index / 8) + progress * 1.4
            inner = glow_radius // 3
            outer = glow_radius
            start = (center[0] + int(math.cos(angle) * inner), center[1] + int(math.sin(angle) * inner))
            end = (center[0] + int(math.cos(angle) * outer), center[1] + int(math.sin(angle) * outer))
            pygame.draw.line(overlay, (*effect.color, max(35, alpha // 2)), start, end, 2)
        self.screen.blit(overlay, overlay.get_rect(center=rect.center))

    def _draw_reflect_impact(self, rect: pygame.Rect, effect: CombatImpactEffect, progress: float) -> None:
        alpha = int(180 * (1.0 - progress))
        if alpha <= 0:
            return
        overlay = pygame.Surface(rect.inflate(130, 110).size, pygame.SRCALPHA)
        center = (overlay.get_width() // 2, overlay.get_height() // 2)
        radius_x = int(34 + progress * 48)
        radius_y = int(22 + progress * 32)
        for index in range(3):
            ring_rect = pygame.Rect(0, 0, radius_x * 2 + index * 18, radius_y * 2 + index * 12)
            ring_rect.center = center
            pygame.draw.ellipse(overlay, (*effect.color, max(35, alpha - index * 42)), ring_rect, 2)
        for angle in (-0.65, 0.0, 0.65):
            start = (
                center[0] - int(math.cos(angle) * (radius_x + 18)),
                center[1] - int(math.sin(angle) * (radius_y + 10)),
            )
            end = (
                center[0] + int(math.cos(angle) * (radius_x + 18)),
                center[1] + int(math.sin(angle) * (radius_y + 10)),
            )
            pygame.draw.line(overlay, (*effect.color, max(50, alpha // 2)), start, end, 2)
        self.screen.blit(overlay, overlay.get_rect(center=rect.center))

    def _draw_status_impact(self, rect: pygame.Rect, effect: CombatImpactEffect, progress: float) -> None:
        alpha = int(175 * (1.0 - progress))
        if alpha <= 0:
            return
        overlay = pygame.Surface(rect.inflate(100, 90).size, pygame.SRCALPHA)
        center = (overlay.get_width() // 2, overlay.get_height() // 2)
        radius = int(16 + progress * 34)
        pygame.draw.circle(overlay, (*effect.color, max(40, alpha // 2)), center, radius, 2)
        for index in range(6):
            angle = math.pi * 2 * index / 6
            marker_center = (
                center[0] + int(math.cos(angle) * (radius + 18)),
                center[1] + int(math.sin(angle) * (radius + 8)),
            )
            pygame.draw.circle(overlay, (*effect.color, max(35, alpha - index * 10)), marker_center, 4)
        self.screen.blit(overlay, overlay.get_rect(center=rect.center))

    def _draw_elemental_strike_impact(self, rect: pygame.Rect, effect: CombatImpactEffect, progress: float) -> None:
        self._draw_weapon_impact(rect, effect, progress)
        alpha = int(120 * (1.0 - progress))
        if alpha <= 0:
            return
        overlay = pygame.Surface(rect.inflate(100, 100).size, pygame.SRCALPHA)
        center = (overlay.get_width() // 2, overlay.get_height() // 2)
        radius = int(24 + progress * 58)
        pygame.draw.circle(overlay, (*effect.color, max(25, alpha // 2)), center, radius, 2)
        for index in range(5):
            angle = progress * math.pi * 2 + index * math.pi * 2 / 5
            start = (
                center[0] + int(math.cos(angle) * max(6, radius // 3)),
                center[1] + int(math.sin(angle) * max(6, radius // 3)),
            )
            end = (
                center[0] + int(math.cos(angle) * radius),
                center[1] + int(math.sin(angle) * radius),
            )
            pygame.draw.line(overlay, (*effect.color, max(35, alpha // 2)), start, end, 2)
        self.screen.blit(overlay, overlay.get_rect(center=rect.center))

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
        class_kit_terms = (
            "aerial",
            "arcane larceny",
            "aspect harmony",
            "case journal",
            "crescendo",
            "death mark",
            "devotion",
            "divine intervention",
            "encore",
            "foresight",
            "fortune",
            "harmony bonus",
            "ki",
            "loaded dice",
            "misfortune",
            "no-trace",
            "oath conviction",
            "ordered blessings",
            "prayer",
            "revelation",
            "resolve",
            "stolen charge",
            "threaded cast",
            "totem resonance",
            "umbral",
            "vow affirmation",
        )
        for line in message.split("\n"):
            line_lower = line.lower()
            keep_class_kit_line = any(term in line_lower for term in class_kit_terms)
            if "is affected by" in line_lower:
                continue
            if not keep_class_kit_line and any(term in line_lower for term in suppress_terms):
                continue
            if (
                not keep_class_kit_line
                and "already" in line_lower
                and any(term in line_lower for term in suppress_already)
            ):
                continue
            if line.strip():
                kept_lines.append(line.strip())
        return kept_lines

    def _wrap_log_line(
        self,
        line: str,
        max_width: int | None = None,
        font: pygame.font.Font | None = None,
    ) -> list[str]:
        """Wrap a combat log line to the combat pane width."""
        if not line:
            return []

        max_width = max(160, max_width if max_width is not None else self.combat_width - 30)
        measure_font = font or pygame.font.Font(None, 20)
        wrapped: list[str] = []
        for paragraph in line.split("\n"):
            stripped = paragraph.strip()
            if not stripped:
                continue

            current = ""
            for word in stripped.split():
                candidate = f"{current} {word}".strip() if current else word
                if measure_font.size(candidate)[0] <= max_width:
                    current = candidate
                    continue

                if current:
                    wrapped.append(current)
                    current = ""

                if measure_font.size(word)[0] <= max_width:
                    current = word
                    continue

                chunk = ""
                for char in word:
                    chunk_candidate = f"{chunk}{char}"
                    if chunk and measure_font.size(chunk_candidate)[0] > max_width:
                        wrapped.append(chunk)
                        chunk = char
                    else:
                        chunk = chunk_candidate
                current = chunk

            if current:
                wrapped.append(current)
        return wrapped

    def _wrapped_combat_log_lines(
        self,
        max_width: int,
        font: pygame.font.Font | None = None,
    ) -> list[str]:
        """Return combat log history flattened into render-ready wrapped lines."""
        return [
            line.text
            for line in self._wrapped_combat_log_entries(max_width=max_width, font=font)
        ]

    def _wrapped_combat_log_entries(
        self,
        max_width: int,
        font: pygame.font.Font | None = None,
        overlay: bool = False,
    ) -> list[CombatLogLine]:
        """Return combat log history flattened with source-message styling intact."""
        cache_key = (
            self._combat_log_revision,
            max(160, max_width - 12),
            overlay,
            self._combat_log_font_cache_key(font),
        )
        cached = self._combat_log_wrap_cache.get(cache_key)
        if cached is not None:
            return cached

        entries: list[CombatLogLine] = []
        wrap_width = cache_key[1]
        for message in self.combat_log:
            color = self._combat_log_color(message, overlay=overlay)
            marker_color = self._combat_log_marker_color(message, overlay=overlay)
            wrapped_lines = self._wrap_log_line(message, max_width=wrap_width, font=font)
            for index, wrapped_line in enumerate(wrapped_lines):
                entries.append(
                    CombatLogLine(
                        text=wrapped_line,
                        color=color,
                        marker_color=marker_color,
                        continuation=index > 0,
                    )
                )
        self._combat_log_wrap_cache[cache_key] = entries
        return entries

    def _invalidate_combat_log_wrap_cache(self) -> None:
        self._combat_log_revision += 1
        self._combat_log_wrap_cache.clear()

    @staticmethod
    def _combat_log_font_cache_key(font: pygame.font.Font | None) -> int:
        if font is None:
            return 0
        try:
            return int(font.size("Dungeon Combat Log Probe")[0])
        except Exception:
            return id(font)

    def _draw_panel_surface(
        self,
        rect: pygame.Rect,
        *,
        fill: tuple[int, int, int],
        border: tuple[int, int, int],
        accent: tuple[int, int, int] | None = None,
        alpha: int | None = None,
        border_width: int = 2,
    ) -> None:
        if alpha is None:
            pygame.draw.rect(self.screen, fill, rect)
        else:
            panel = pygame.Surface(rect.size)
            panel.set_alpha(alpha)
            panel.fill(fill)
            self.screen.blit(panel, rect.topleft)
        pygame.draw.rect(self.screen, border, rect, border_width)
        if accent is not None and rect.height >= 10:
            try:
                pygame.draw.line(self.screen, accent, (rect.left + 2, rect.top + 2), (rect.right - 3, rect.top + 2), 1)
                pygame.draw.line(self.screen, (18, 18, 22), (rect.left + 2, rect.bottom - 3), (rect.right - 3, rect.bottom - 3), 1)
            except TypeError:
                return

    def _render_player_danger_vignette(self, player_char) -> None:
        health = getattr(player_char, "health", None)
        current = getattr(health, "current", 0)
        maximum = max(1, getattr(health, "max", 1))
        ratio = current / maximum
        if ratio > 0.25:
            return

        intensity = min(1.0, (0.25 - ratio) / 0.25)
        pulse = (math.sin(pygame.time.get_ticks() / 210.0) + 1.0) / 2.0
        alpha = int(36 + intensity * 58 + pulse * (12 + intensity * 34))
        overlay = pygame.Surface((self.combat_width, self.screen_height), pygame.SRCALPHA)
        center_rect = pygame.Rect(
            -int(self.combat_width * 0.10),
            -int(self.screen_height * 0.18),
            int(self.combat_width * 1.20),
            int(self.screen_height * 1.32),
        )
        for index, width in enumerate((80, 54, 32, 16)):
            ring_alpha = max(18, alpha - index * 22)
            ring_rect = center_rect.inflate(index * 56, index * 42)
            pygame.draw.ellipse(
                overlay,
                (160, 24, 22, ring_alpha),
                ring_rect,
                width=width,
            )
        if intensity > 0.5:
            pulse_alpha = int((intensity - 0.5) * (58 + pulse * 48))
            pygame.draw.rect(
                overlay,
                (110, 18, 18, pulse_alpha),
                pygame.Rect(0, self.screen_height - 312, self.combat_width, 156),
            )
        self.screen.blit(overlay, (0, 0))

    def _effect_label(self, effect_name):
        labels = {
            "Berserk": "BRK",
            "Blind": "BLD",
            "Blind Rage": "BRG",
            "Doom": "DOM",
            "Poison": "PSN",
            "Silence": "SIL",
            "Sleep": "SLP",
            "Stun": "STN",
            "Defend": "DEF",
            "Steal Success": "STE",
            "Bleed": "RND",
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
            "Totem",
        }
        positive_status = {"Defend", "Steal Success"}
        positive_magic = {
            "Astral Shift",
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

        icons.extend(totem_status_icons(character))

        dot_effect = character.magic_effects.get("DOT")
        if dot_effect and dot_effect.active:
            source = getattr(dot_effect, "source", "").lower()
            icons.append(("BRN" if source == "burn" else "DOT", False))

        for name, effect in character.status_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_status))
        for name, effect in character.physical_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_status))
        for name, effect in character.stat_effects.items():
            if name not in skip_effects:
                icon = stat_effect_status_icon(self._effect_label(name), effect)
                if icon is not None:
                    icons.append(icon)
        for name, effect in character.magic_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_magic or name in positive_status))
        for name, effect in character.class_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), True))

        try:
            maelstrom_hits = int(getattr(character, "maelstrom_hits", 0))
            skills = getattr(character, "spellbook", {}).get("Skills", {})
            if "Maelstrom Weapon" in skills and maelstrom_hits > 0:
                icons.append((f"MW{maelstrom_hits}", True))
        except (AttributeError, TypeError, ValueError):
            pass

        try:
            guard_stacks = int(getattr(character, "evasive_guard_stacks", 0) or 0)
            skills = getattr(character, "spellbook", {}).get("Skills", {})
            if "Evasive Guard" in skills and guard_stacks > 0:
                icons.append((f"EG{min(3, guard_stacks)}", True))
        except (AttributeError, TypeError, ValueError):
            pass

        if ("DEF", True) in icons:
            icons = [icon for icon in icons if icon != ("DEF", False)]

        return prioritize_status_icons(combine_duplicate_status_icons(icons))

    @staticmethod
    def _is_telegraph_message(line: str) -> bool:
        lower = line.lower()
        telegraph_terms = (
            " is lowering ",
            " is raising ",
            " is inhaling ",
            " is gathering ",
            " is coiling ",
            " is channeling ",
            " is melding ",
            " is drawing in ",
            " is preparing",
            " is charging",
            " continues charging",
            " begins to charge",
            " while preparing",
        )
        return any(term in lower for term in telegraph_terms)

    @staticmethod
    def _short_telegraph_message(line: str) -> str:
        stripped = str(line).strip()
        if not stripped:
            return "Enemy is charging."
        if " continues charging" in stripped:
            return stripped.split(" continues charging", 1)[0] + " is charging."
        for marker in (
            " is lowering ",
            " is raising ",
            " is inhaling ",
            " is gathering ",
            " is coiling ",
            " is channeling ",
            " is melding ",
            " is drawing in ",
            " is preparing",
        ):
            if marker in stripped:
                return stripped.split(marker, 1)[0] + " is charging."
        if " begins to charge" in stripped:
            return stripped.split(" begins to charge", 1)[0] + " is charging."
        if " while preparing" in stripped:
            return stripped.split(" while preparing", 1)[0] + " is charging."
        return stripped

    def _combat_log_color(self, line: str, overlay: bool = False):
        lower = line.lower()
        if self._is_telegraph_message(line):
            return self.colors["telegraph"]
        if any(
            term in lower
            for term in ("health regenerated", "health has regenerated", "regenerates", "restore", "restores", "recovers", "heals")
        ):
            return self.colors["log_heal"]
        if any(term in lower for term in ("miss", "resist", "immune", "fails")):
            return self.colors["log_muted"]
        if any(
            term in lower
            for term in (
                " damage",
                "damages ",
                "bleeding",
                "bleeds",
                "burns",
                "poison",
                "blind",
                "silence",
                "silenced",
                "scorches",
                "shocks",
                "slain",
                "stun",
                "disarm",
                "falls prone",
                "knocked",
                "takes ",
                "loses ",
            )
        ):
            return self.colors["log_damage"]
        if self._line_starts_with_actor(lower, self._combat_log_player_name):
            return self.colors["log_player"]
        if self._line_starts_with_actor(lower, self._combat_log_enemy_name):
            return self.colors["log_enemy"]
        return (240, 240, 240) if overlay else self.colors["text"]

    @staticmethod
    def _line_starts_with_actor(lower_line: str, actor_name: str | None) -> bool:
        if not actor_name:
            return False
        actor = actor_name.strip().lower()
        return bool(actor) and (lower_line.startswith(actor + " ") or lower_line.startswith(actor + "'"))

    def _set_combat_log_actors(self, player_char, enemy) -> None:
        player_name = str(getattr(player_char, "name", "") or "") or None
        enemy_name = str(getattr(enemy, "name", "") or "") or None
        if player_name != self._combat_log_player_name or enemy_name != self._combat_log_enemy_name:
            self._combat_log_player_name = player_name
            self._combat_log_enemy_name = enemy_name
            self._invalidate_combat_log_wrap_cache()

    def _combat_log_marker_color(self, line: str, overlay: bool = False) -> tuple[int, int, int]:
        if self._is_telegraph_message(line):
            return self.colors["telegraph"]
        color = self._combat_log_color(line, overlay=overlay)
        if color == self.colors["text"] or color == (240, 240, 240):
            return (120, 120, 128)
        return color

    @staticmethod
    def _truncate_text(font: pygame.font.Font, text: str, max_width: int) -> str:
        def measured_width(value: str) -> int:
            if hasattr(font, "size"):
                return font.size(value)[0]
            return len(value) * 8

        if max_width <= 0 or measured_width(text) <= max_width:
            return text

        ellipsis = "..."
        ellipsis_width = measured_width(ellipsis)
        clipped = text
        while clipped and measured_width(clipped) + ellipsis_width > max_width:
            clipped = clipped[:-1]
        return f"{clipped}{ellipsis}" if clipped else ellipsis

    def _render_status_icons(self, icons, x, y, max_width, max_rows=2):
        if not icons:
            return

        font = pygame.font.Font(None, 16)
        icon_w = 38
        icon_h = 26
        padding = 6
        per_row = max(1, max_width // (icon_w + padding))
        visible_icons = compact_status_icons(icons, per_row, max_rows)

        for idx, (label, is_positive) in enumerate(visible_icons):
            row = idx // per_row
            col = idx % per_row
            icon_x = x + col * (icon_w + padding)
            icon_y = y + row * (icon_h + padding)
            color = status_icon_color(is_positive, label)

            rect = pygame.Rect(icon_x, icon_y, icon_w, icon_h)
            icon_surface = load_status_icon_surface(label, (icon_h - 2, icon_h - 2), is_positive)
            if icon_surface is not None:
                icon_rect = icon_surface.get_rect(center=rect.center)
                self.screen.blit(icon_surface, icon_rect)
                stack_count = status_icon_stack_count(label)
                if stack_count > 1:
                    badge_text = str(stack_count)
                    badge_font = pygame.font.Font(None, 15)
                    badge_surf = badge_font.render(badge_text, True, (255, 255, 255))
                    badge_radius = max(7, badge_surf.get_width() // 2 + 4)
                    badge_center = (rect.right - badge_radius + 2, rect.top + badge_radius - 1)
                    pygame.draw.circle(self.screen, (22, 22, 28), badge_center, badge_radius)
                    pygame.draw.circle(self.screen, (240, 210, 92), badge_center, badge_radius, 1)
                    badge_rect = badge_surf.get_rect(center=badge_center)
                    self.screen.blit(badge_surf, badge_rect)
            else:
                pygame.draw.rect(self.screen, color, rect, border_radius=4)
                pygame.draw.rect(self.screen, (20, 20, 20), rect, 1, border_radius=4)
                fitted_label = fit_status_icon_label(font, label, icon_w - 6)
                text_surf = font.render(fitted_label, True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=rect.center)
                self.screen.blit(text_surf, text_rect)

    def reload_enemy_sprite(self, enemy) -> None:
        """Compatibility hook for enemies that change visual form during combat."""
        return None

    def prepare_enemy_assets(self, enemy) -> None:
        """Populate scaled enemy sprite caches before the first combat frame."""
        for size in (
            self._enemy_combat_sprite_size(enemy),
            self._enemy_dungeon_combat_sprite_size(enemy),
        ):
            self._enemy_sprite_surface(enemy, size, has_sight=True)
    
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

    def _enemy_details_visible(self, player_char, enemy, show_enemy_details=None) -> bool:
        """Return whether sight-based enemy details should be displayed."""
        if show_enemy_details is not None:
            return bool(show_enemy_details)
        if self._is_boss_enemy(enemy) or getattr(enemy, "name", "") == "Waitress":
            return False
        return self._has_sight(player_char)
    
    def _colorize_sprite(self, sprite, enemy):
        """Prepare sprite for rendering.
        
        With the new colored sprite system (ascii_to_sprite_colored.py), sprites
        are generated with full color palettes that preserve detail and outlines.
        This method now skips blanket colorization which was destroying detail.
        
        Combat sprites now include:
        - Base color for the enemy type
        - Shadow colors for depth
        - Highlight colors for detail
        - Accent colors for clothing, equipment, and eyes
        
        No additional colorization is needed.
        """
        # Return sprite as-is - it's already colored from generation
        return sprite

    def _enemy_sprite_surface(self, enemy, size: tuple[int, int], has_sight: bool = True):
        """Return the enemy battlefield sprite scaled to a fixed combat box."""
        if has_sight or getattr(enemy, "name", "") != "Invisible Stalker":
            try:
                sprite_key = self.enemy_combat_sprite_manager.get_sprite_key_for_enemy(enemy)
                return self.enemy_combat_sprite_manager.get_scaled_sprite_by_key(sprite_key, size)
            except Exception as exc:  # pragma: no cover - defensive fallback for asset loading failures
                print(f"Failed to render enemy combat sprite for {getattr(enemy, 'name', enemy)}: {exc}")
        return None

    def _is_boss_enemy(self, enemy) -> bool:
        """Return whether an enemy should use boss-scale combat presentation."""
        is_boss = getattr(self.enemy_combat_sprite_manager, "_is_boss", None)
        if callable(is_boss):
            return bool(is_boss(enemy))
        name = str(getattr(enemy, "name", enemy) or "")
        return bool(
            getattr(enemy, "boss", False)
            or getattr(enemy, "is_boss", False)
            or name in EnemyCombatSpriteManager.BOSS_NAMES
        )

    def _enemy_combat_sprite_size(self, enemy) -> tuple[int, int]:
        """Return the combat sprite box size after optional per-enemy scaling."""
        if self._is_boss_enemy(enemy):
            base_edge = max(256, int(min(self.combat_width, self.combat_height)))
        else:
            base_edge = 256
        edge = max(1, int(base_edge * self._enemy_combat_sprite_scale(enemy)))
        return (edge, edge)

    def _enemy_combat_sprite_scale(self, enemy) -> float:
        get_scale = getattr(self.enemy_combat_sprite_manager, "get_combat_scale_for_enemy", None)
        if not callable(get_scale):
            return 1.0
        try:
            return max(0.25, min(2.5, float(get_scale(enemy))))
        except (TypeError, ValueError):
            return 1.0

    def _enemy_dungeon_combat_sprite_size(self, enemy) -> tuple[int, int]:
        """Return the foreground combat sprite size for the dungeon-backed combat view."""
        edge = max(1, int(320 * self._enemy_combat_sprite_scale(enemy)))
        return (edge, edge)

    @staticmethod
    def _magic_effect_active(character, name: str) -> bool:
        try:
            effect = character.magic_effects.get(name)
            return bool(effect and effect.active)
        except AttributeError:
            return False

    def _active_duplicate_count(self, character) -> int:
        """Return visible Mirror Image duplicate count for a character."""
        try:
            effect = character.magic_effects.get("Duplicates")
            if not effect or not effect.active:
                return 0
            duration = int(effect.duration)
            if duration <= 0:
                effect.active = False
                effect.duration = 0
                return 0
            return max(0, min(4, duration))
        except (AttributeError, TypeError, ValueError):
            return 0

    def _draw_mirror_images(self, sprite, center: tuple[int, int], duplicate_count: int) -> None:
        """Draw overlapping translucent duplicates behind the real sprite."""
        if duplicate_count <= 0:
            return

        offsets = [(-18, -6), (18, 6), (-10, 12), (10, -12)]
        shimmer = (pygame.time.get_ticks() // 120) % 2
        for index in range(duplicate_count):
            offset_x, offset_y = offsets[index % len(offsets)]
            if shimmer and index % 2 == 0:
                offset_x = -offset_x
            ghost = sprite.copy()
            ghost.set_alpha(max(55, 118 - index * 14))
            ghost_rect = ghost.get_rect(center=(center[0] + offset_x, center[1] + offset_y))
            self.screen.blit(ghost, ghost_rect)

    def _render_mana_shield_visual(self, rect: pygame.Rect) -> None:
        padding = 30
        shield_rect = rect.inflate(padding, padding)
        surface = pygame.Surface(shield_rect.size, pygame.SRCALPHA)
        pulse = (math.sin(pygame.time.get_ticks() / 180) + 1) / 2
        alpha = int(70 + pulse * 65)
        pygame.draw.ellipse(surface, (80, 170, 255, alpha), surface.get_rect(), 4)
        inner = surface.get_rect().inflate(-14, -14)
        if inner.width > 0 and inner.height > 0:
            pygame.draw.ellipse(surface, (140, 210, 255, max(35, alpha // 2)), inner, 2)
        self.screen.blit(surface, shield_rect.topleft)

    def _render_smoke_screen_visual(self, rect: pygame.Rect) -> None:
        smoke_width = max(120, int(rect.width * 1.35))
        smoke_height = max(120, int(rect.height * 0.95))
        smoke_rect = pygame.Rect(0, 0, smoke_width, smoke_height)
        smoke_rect.midbottom = (rect.centerx, rect.bottom + 12)
        surface = pygame.Surface(smoke_rect.size, pygame.SRCALPHA)
        ticks = pygame.time.get_ticks()

        base_puffs = (
            (0.20, 0.86, 32, 22, 106),
            (0.36, 0.90, 42, 26, 124),
            (0.54, 0.84, 46, 30, 132),
            (0.72, 0.89, 36, 24, 112),
            (0.84, 0.82, 28, 20, 92),
        )
        for index, (x_pct, y_pct, width, height, alpha) in enumerate(base_puffs):
            drift = math.sin((ticks / 180) + index * 0.8) * 6
            puff_rect = pygame.Rect(0, 0, width * 2, height * 2)
            puff_rect.center = (
                int(smoke_rect.width * x_pct + drift),
                int(smoke_rect.height * y_pct),
            )
            pygame.draw.ellipse(surface, (128, 132, 140, alpha), puff_rect)
            pygame.draw.circle(
                surface,
                (178, 180, 188, max(60, alpha - 42)),
                puff_rect.center,
                max(14, min(width, height)),
            )

        for index in range(16):
            phase = ((ticks / 760) + index * 0.137) % 1.0
            y_pct = 0.92 - phase * 0.74
            spread = 0.10 + phase * 0.30
            sway = math.sin((ticks / 230) + index * 1.9) * smoke_rect.width * spread
            x_pct = 0.50 + math.sin(index * 2.35) * (0.10 + phase * 0.12)
            center_x = int(smoke_rect.width * x_pct + sway)
            center_y = int(smoke_rect.height * y_pct)
            radius_x = int(20 + phase * 42 + (index % 3) * 5)
            radius_y = int(16 + phase * 34 + (index % 2) * 4)
            alpha = int(118 - phase * 48)
            wisp_rect = pygame.Rect(0, 0, radius_x * 2, radius_y * 2)
            wisp_rect.center = (center_x, center_y)
            color_shift = int(phase * 28)
            pygame.draw.ellipse(
                surface,
                (148 + color_shift, 150 + color_shift, 160 + color_shift, alpha),
                wisp_rect,
            )

        self.screen.blit(surface, smoke_rect.topleft)

    def _smoke_screen_active_for(self, character, target: str) -> bool:
        return (
            self._transient_smoke_active(target)
            or self._magic_effect_active(character, "Smoke Screen")
            or self._magic_effect_active(character, "SmokeScreen")
        )

    def _fade_sprite_for_smoke_screen(self, sprite, character, target: str):
        if not self._smoke_screen_active_for(character, target):
            return sprite
        pulse = (math.sin(pygame.time.get_ticks() / 140) + 1) / 2
        faded = sprite.copy()
        faded.set_alpha(int(56 + pulse * 42))
        return faded

    def _render_ability_status_visuals(self, character, target: str, *, include_duplicates: bool = True) -> None:
        rect = self._target_rect_for_effect(target)
        if self._magic_effect_active(character, "Mana Shield"):
            self._render_mana_shield_visual(rect)
        if self._smoke_screen_active_for(character, target):
            self._render_smoke_screen_visual(rect)
    
    def render_combat(self, player_char, enemy, actions, selected_action=0, current_turn=None, show_enemy_details=None):
        """Render the complete combat view."""
        self._set_combat_log_actors(player_char, enemy)
        # Update animations
        self.update_animations()
        
        # Fill combat area background
        combat_rect = pygame.Rect(0, 0, self.combat_width, self.combat_height)
        self.screen.fill(self.colors['background'], combat_rect)
        
        # Check if player can see enemy details
        has_sight = self._enemy_details_visible(player_char, enemy, show_enemy_details)
        
        # Render enemy in center
        self._render_enemy(enemy, has_sight)
        self._render_enemy_info_panel(enemy, has_sight, overlay=False)

        # Render current turn indicator
        self._render_turn_indicator(player_char, enemy, current_turn=current_turn)
        self._render_telegraph_banner(enemy=enemy, overlay=False)

        # Render player status at bottom left
        self._render_player_status(player_char)
        
        # Render action menu at bottom
        self._render_action_menu(actions, selected_action)
        
        # Render combat log
        self._render_combat_log()
    
    def _render_enemy(self, enemy, has_sight=True):
        """Render the enemy sprite/representation with animations."""
        if self._hide_enemy_for_flee:
            return

        visual_offset_x, visual_offset_y = self.enemy_visual_offset
        center_x = self.combat_width // 2 + visual_offset_x + self._enemy_recoil_offset()
        boss_enemy = self._is_boss_enemy(enemy)
        center_y = (int(self.combat_height * 0.42) if boss_enemy else self.combat_height // 3) + visual_offset_y

        is_flying = getattr(enemy, "flying", False)
        is_tunneled = getattr(enemy, "tunnel", False)
        if is_flying:
            center_y -= min(48, max(24, int(self.combat_height * 0.05)))
        
        # If enemy is tunneled, show a "burrowed" message instead of sprite
        if is_tunneled:
            font = pygame.font.Font(None, 40)
            text_surf = font.render(f"{enemy.name} is underground", True, (150, 100, 50))
            text_rect = text_surf.get_rect(center=(center_x, center_y))
            self.screen.blit(text_surf, text_rect)
            
            # Show HP bar if visible
            if has_sight:
                bar_width = 200
                bar_height = 20
                bar_x = center_x - bar_width // 2
                bar_y = center_y + 60
                
                # Background
                pygame.draw.rect(self.screen, (50, 50, 50), 
                               (bar_x, bar_y, bar_width, bar_height))
                # HP fill
                hp_pct = max(0, enemy.health.current / enemy.health.max) if enemy.health.max else 0
                filled_width = int(bar_width * hp_pct)
                pygame.draw.rect(self.screen, (0, 200, 0),
                               (bar_x, bar_y, filled_width, bar_height))
                # Border
                pygame.draw.rect(self.screen, (255, 255, 255),
                               (bar_x, bar_y, bar_width, bar_height), 2)
            return
        
        # Get animator for this enemy
        animator = self._get_sprite_animator(enemy)
        
        sprite_size = self._enemy_combat_sprite_size(enemy)
        display_sprite = self._enemy_sprite_surface(enemy, sprite_size, has_sight=has_sight)
        enemy_size = sprite_size[1] // 2

        if display_sprite is not None:
            # Apply damage flash tint
            if animator.damage_flash > 0:
                display_sprite = animator.apply_tint(display_sprite, (255, 100, 100), animator.damage_flash)
            
            # Apply death animation (scale down and fade)
            if animator.animation_type == 'death':
                # Scale from 1.0 to 0.3 as death progresses
                scale = 1.0 - (animator.death_progress * 0.7)
                death_size = (
                    max(1, int(display_sprite.get_width() * scale)),
                    max(1, int(display_sprite.get_height() * scale)),
                )
                display_sprite = pygame.transform.scale(display_sprite, death_size)
                
                # Fade out by modulating per-pixel alpha (preserves sprite shape)
                fade_alpha = int(255 * (1.0 - animator.death_progress))
                alpha_surf = pygame.Surface(display_sprite.get_size(), pygame.SRCALPHA)
                alpha_surf.fill((255, 255, 255, fade_alpha))
                display_sprite = display_sprite.copy()
                display_sprite.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if animator.animation_type != 'death':
                display_sprite = self._fade_sprite_for_smoke_screen(display_sprite, enemy, "enemy")
            
            # Calculate Y position with bob animation
            bob_y = center_y + animator.bob_offset if is_flying else center_y
            bob_x = center_x if is_flying else center_x + animator.sway_offset

            if animator.animation_type != 'death':
                self._draw_mirror_images(
                    display_sprite,
                    (int(bob_x), int(bob_y)),
                    self._active_duplicate_count(enemy),
                )

            sprite_rect = display_sprite.get_rect(center=(bob_x, bob_y))
            self._last_enemy_target_rect = sprite_rect.copy()
            self.screen.blit(display_sprite, sprite_rect)
        else:
            # Fallback to simple representation
            enemy_size = 120
            fallback_x = center_x if is_flying else center_x + animator.sway_offset
            fallback_y = center_y + animator.bob_offset if is_flying else center_y
            pygame.draw.circle(self.screen, self.colors['enemy'], 
                             (int(fallback_x), int(fallback_y)), enemy_size)
            self._last_enemy_target_rect = pygame.Rect(
                int(fallback_x - enemy_size),
                int(fallback_y - enemy_size),
                enemy_size * 2,
                enemy_size * 2,
            )
            
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

        self._render_ability_status_visuals(enemy, "enemy", include_duplicates=False)
        
        # Enemy name (always visible)
        font = pygame.font.Font(None, 32)
        name_surf = font.render(enemy.name, True, self.colors['text'])
        name_rect = name_surf.get_rect(center=(center_x, center_y - enemy_size - 30))
        self.screen.blit(name_surf, name_rect)
        
        # Enemy HP/MP bars (only visible with sight)
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
            hp_text = f"HP {enemy.health.current}/{enemy.health.max}"
            hp_surf = small_font.render(hp_text, True, self.colors['text'])
            hp_rect = hp_surf.get_rect(center=(center_x, bar_y + bar_height // 2))
            self.screen.blit(hp_surf, hp_rect)

            enemy_mana = getattr(enemy, "mana", None)
            if enemy_mana is not None and getattr(enemy_mana, "max", 0) > 0:
                mp_y = bar_y + bar_height + 6
                pygame.draw.rect(self.screen, (100, 100, 100),
                               pygame.Rect(bar_x, mp_y, bar_width, bar_height))
                mp_ratio = enemy_mana.current / max(enemy_mana.max, 1)
                mp_width = int(bar_width * mp_ratio)
                pygame.draw.rect(self.screen, self.colors['mp_bar'],
                               pygame.Rect(bar_x, mp_y, mp_width, bar_height))
                mp_text = f"MP {enemy_mana.current}/{enemy_mana.max}"
                mp_surf = small_font.render(mp_text, True, self.colors['text'])
                mp_rect = mp_surf.get_rect(center=(center_x, mp_y + bar_height // 2))
                self.screen.blit(mp_surf, mp_rect)

        self._render_active_impact_effects()
        self._render_floating_texts()

    def _render_enemy_info_panel(self, enemy, has_sight=True, overlay=True):
        """Render combat artwork and target details without replacing gameplay sprites."""
        if self._hide_enemy_for_flee:
            return

        panel_x = int(self.screen_width * 0.65) + 12 if overlay else self.combat_width + 12
        panel_w = self.screen_width - panel_x - 12
        if panel_w < 170:
            return

        panel_y = 80 if overlay else 86
        panel_h = min(390, self.screen_height - panel_y - 170)
        if panel_h < 210:
            return

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel.fill((16, 16, 22, 232 if overlay else 255))
        self.screen.blit(panel, panel_rect.topleft)
        pygame.draw.rect(self.screen, (106, 82, 48), panel_rect, 2, border_radius=6)

        pad = 12
        title_font = pygame.font.Font(None, 26)
        body_font = pygame.font.Font(None, 18)

        name = self._truncate_text(title_font, getattr(enemy, "name", "Enemy"), panel_w - (pad * 2))
        name_surf = title_font.render(name, True, self.colors["text"])
        self.screen.blit(name_surf, (panel_rect.left + pad, panel_rect.top + pad))

        art_top = panel_rect.top + pad + 30
        art_h = max(110, min(210, panel_h - 150))
        art_rect = pygame.Rect(panel_rect.left + pad, art_top, panel_w - (pad * 2), art_h)
        try:
            artwork = self.enemy_combat_sprite_manager.get_scaled_sprite(enemy, art_rect.size)
        except Exception as exc:  # pragma: no cover - hard runtime fallback for broken external assets
            print(f"Failed to render enemy combat sprite for {getattr(enemy, 'name', enemy)}: {exc}")
            artwork = self.enemy_combat_sprite_manager.fallback_surface()
            artwork = pygame.transform.smoothscale(artwork, art_rect.size)
        self.screen.blit(artwork, art_rect.topleft)
        pygame.draw.rect(self.screen, (58, 48, 38), art_rect, 1)

        y = art_rect.bottom + 10
        if has_sight and hasattr(enemy, "health"):
            hp_text = f"HP {enemy.health.current} / {enemy.health.max}"
            hp_surf = body_font.render(hp_text, True, self.colors["hp_bar"])
            self.screen.blit(hp_surf, (panel_rect.left + pad, y))
            y += 22

        enemy_type = getattr(enemy, "enemy_typ", "")
        if enemy_type:
            type_surf = body_font.render(f"Type {enemy_type}", True, (205, 197, 176))
            self.screen.blit(type_surf, (panel_rect.left + pad, y))
            y += 22

        if has_sight:
            y = self._render_enemy_resistance_summary(enemy, panel_rect, y, body_font)

        icons = self._collect_status_icons(enemy)
        if icons and y + 20 < panel_rect.bottom:
            self._render_status_icons(icons, panel_rect.left + pad, y + 4, max_width=panel_w - (pad * 2), max_rows=2)

    def _render_enemy_resistance_summary(self, enemy, panel_rect, y, font):
        resistance = getattr(enemy, "resistance", {}) or {}
        if not resistance:
            return y

        weaknesses = []
        strengths = []
        for name, value in resistance.items():
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            if numeric < 0:
                weaknesses.append(name)
            elif numeric > 0:
                strengths.append(name)

        max_width = panel_rect.width - 24
        for label, entries, color in (
            ("Weak", weaknesses, (230, 110, 100)),
            ("Resist", strengths, (126, 205, 132)),
        ):
            if not entries or y + 18 >= panel_rect.bottom:
                continue
            text = f"{label} {', '.join(entries[:4])}"
            if len(entries) > 4:
                text += f" +{len(entries) - 4}"
            text = self._truncate_text(font, text, max_width)
            surf = font.render(text, True, color)
            self.screen.blit(surf, (panel_rect.left + 12, y))
            y += 20
        return y
    
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

        if astromancer.has_rune_system(player_char):
            rune_y = y + 56
            if astromancer.is_astromancer(player_char):
                sign_text = f"Sign: {astromancer.active_constellation(player_char)}"
                sign_surf = small_font.render(sign_text, True, self.colors.get("gold", (232, 196, 92)))
                self.screen.blit(sign_surf, (x, rune_y))
                rune_y += 16
            for line in astromancer.rune_grid_lines(player_char):
                rune_surf = small_font.render(line, True, self.colors.get("text", (230, 230, 230)))
                self.screen.blit(rune_surf, (x, rune_y))
                rune_y += 14

        # Status icons
        icons = self._collect_status_icons(player_char)
        if icons:
            icon_y = y + 60
            if astromancer.has_rune_system(player_char):
                icon_y += 66 if astromancer.is_astromancer(player_char) else 50
            self._render_status_icons(icons, x, icon_y, max_width=260)
        self._last_player_target_rect = pygame.Rect(x - 8, y - 10, 248, 104)
        self._render_ability_status_visuals(player_char, "player")

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

    @staticmethod
    def _action_grid_layout(width: int, menu_height: int, action_count: int) -> tuple[int, int, int, int, int]:
        actions_per_row = 3
        row_count = max(1, math.ceil(max(1, action_count) / actions_per_row))
        start_y_offset = 46
        bottom_padding = 14
        available_height = max(24, menu_height - start_y_offset - bottom_padding)
        row_height = max(22, min(34, available_height // row_count))
        cell_width = max(92, (width - 54) // actions_per_row)
        return actions_per_row, row_count, start_y_offset, row_height, cell_width

    def _render_action_grid(
        self,
        actions,
        selected_action,
        *,
        rect: pygame.Rect,
        action_font: pygame.font.Font,
        text_color,
        highlight_color,
        border_color=None,
        translucent_highlight: bool = False,
    ) -> None:
        actions_per_row, _row_count, start_y_offset, row_height, cell_width = self._action_grid_layout(
            rect.width,
            rect.height,
            len(actions),
        )
        cell_padding = 10

        for i, action in enumerate(actions):
            row = i // actions_per_row
            col = i % actions_per_row
            x = rect.left + 28 + col * cell_width
            y = rect.top + start_y_offset + row * row_height
            highlight_rect = pygame.Rect(x - 5, y - 4, max(42, cell_width - 12), max(20, row_height - 3))

            if i == selected_action:
                if translucent_highlight:
                    highlight_overlay = pygame.Surface(highlight_rect.size)
                    highlight_overlay.set_alpha(150)
                    highlight_overlay.fill(highlight_color)
                    self.screen.blit(highlight_overlay, highlight_rect.topleft)
                else:
                    pygame.draw.rect(self.screen, highlight_color, highlight_rect)
                selected_border = border_color or self.colors["panel_accent"]
                pygame.draw.rect(self.screen, selected_border, highlight_rect, 2)
                try:
                    pygame.draw.line(
                        self.screen,
                        (235, 215, 165),
                        (highlight_rect.left + 2, highlight_rect.top + 2),
                        (highlight_rect.right - 3, highlight_rect.top + 2),
                        1,
                    )
                except TypeError:
                    pass

            fitted_action = self._truncate_text(action_font, str(action), max(20, highlight_rect.width - cell_padding))
            action_surf = action_font.render(fitted_action, True, text_color)
            self.screen.blit(action_surf, (x, y))
    
    def _render_action_menu(self, actions, selected_action):
        """Render the action selection menu."""
        menu_height = 150
        menu_y = self.combat_height - menu_height
        
        menu_rect = pygame.Rect(0, menu_y, self.combat_width, menu_height)
        self._draw_panel_surface(
            menu_rect,
            fill=(24, 24, 30),
            border=self.colors["action_border"],
            accent=self.colors["panel_accent"],
            border_width=2,
        )
        
        # Title
        font = pygame.font.Font(None, 28)
        title_surf = font.render("Choose Action:", True, (232, 224, 205))
        self.screen.blit(title_surf, (24, menu_y + 10))
        
        action_font = pygame.font.Font(None, 24)
        self._render_action_grid(
            actions,
            selected_action,
            rect=menu_rect,
            action_font=action_font,
            text_color=self.colors['text'],
            highlight_color=self.colors['action_selected'],
        )
    
    def _render_combat_log(self):
        """Render recent combat messages."""
        log_height = 120
        log_y = self.combat_height - 270  # Above action menu
        
        log_rect = pygame.Rect(0, log_y, self.combat_width, log_height)
        self._draw_panel_surface(
            log_rect,
            fill=self.colors["message_bg"],
            border=(76, 76, 84),
            accent=(105, 90, 58),
            border_width=1,
        )
        
        # Messages
        font = pygame.font.Font(None, 20)
        y = log_y + 10
        line_height = 22
        max_lines = self.log_lines_per_page
        lines_rendered = 0

        display_lines = self._wrapped_combat_log_entries(self.combat_width - 30, font=font)
        max_scroll = max(0, len(display_lines) - max_lines)
        self.log_scroll_offset = min(self.log_scroll_offset, max_scroll)

        for line in display_lines[self.log_scroll_offset:self.log_scroll_offset + max_lines]:
            if lines_rendered >= max_lines:
                break
            marker_color = (90, 90, 98) if line.continuation else line.marker_color
            pygame.draw.rect(self.screen, marker_color, pygame.Rect(11, y + 5, 4, 12))
            msg_surf = font.render(line.text, True, line.color)
            self.screen.blit(msg_surf, (31 if line.continuation else 20, y))
            y += line_height
            lines_rendered += 1
    
    def show_damage_flash(self, is_player_hit, event_handler=None):
        """Flash the screen to indicate damage."""
        base_surface = self.screen.copy()
        flash_color = (160, 28, 20) if is_player_hit else (176, 128, 62)

        # Brief pause while still pumping events to keep the window responsive.
        flash_clock = pygame.time.Clock()
        elapsed = 0
        duration_ms = 180
        while elapsed < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event_handler is not None:
                    event_handler(event)
            self.screen.blit(base_surface, (0, 0))
            flash_surface = pygame.Surface((self.combat_width, self.combat_height), pygame.SRCALPHA)
            flash_surface.fill((*flash_color, int(82 * (1.0 - elapsed / duration_ms))))
            self.screen.blit(flash_surface, (0, 0))
            self._render_active_impact_effects()
            pygame.display.flip()
            flash_clock.tick(60)
            elapsed += flash_clock.get_time()

    def render_enemy_in_dungeon(self, player_char, enemy, show_enemy_details=None):
        """Render the enemy as if it's standing in the dungeon ahead of the player."""
        if self._hide_enemy_for_flee:
            return

        # Update animations
        self.update_animations()
        
        # Enemy appears in the center-front of the dungeon view (foreground layer)
        # Position at bottom-center of the dungeon view area (left 65% of screen)
        visual_offset_x, visual_offset_y = self.enemy_visual_offset
        view_width = int(self.screen_width * 0.65)
        center_x = view_width // 2 + visual_offset_x + self._enemy_recoil_offset()
        
        # Position enemy at bottom third (standing on the floor ahead)
        center_y = int(self.screen_height * 0.65) + visual_offset_y

        is_flying = getattr(enemy, "flying", False)
        if is_flying:
            center_y -= min(56, max(28, int(self.screen_height * 0.05)))
        
        # Get animator for this enemy
        animator = self._get_sprite_animator(enemy)
        
        # Check if player can see enemy details
        has_sight = self._enemy_details_visible(player_char, enemy, show_enemy_details)
        
        sprite_size = self._enemy_dungeon_combat_sprite_size(enemy)
        display_sprite = self._enemy_sprite_surface(enemy, sprite_size, has_sight=has_sight)
        enemy_size = sprite_size[1] // 2

        if display_sprite is not None:
            # Apply damage flash tint
            if animator.damage_flash > 0:
                display_sprite = animator.apply_tint(display_sprite, (255, 100, 100), animator.damage_flash)
            
            # Apply death animation
            if animator.animation_type == 'death':
                scale = 1.0 - (animator.death_progress * 0.7)
                death_size = (
                    max(1, int(display_sprite.get_width() * scale)),
                    max(1, int(display_sprite.get_height() * scale)),
                )
                display_sprite = pygame.transform.scale(display_sprite, death_size)
                
                # Fade out by modulating per-pixel alpha (preserves sprite shape)
                fade_alpha = int(255 * (1.0 - animator.death_progress))
                alpha_surf = pygame.Surface(display_sprite.get_size(), pygame.SRCALPHA)
                alpha_surf.fill((255, 255, 255, fade_alpha))
                display_sprite = display_sprite.copy()
                display_sprite.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if animator.animation_type != 'death':
                display_sprite = self._fade_sprite_for_smoke_screen(display_sprite, enemy, "enemy")
            
            # Calculate Y position with bob animation
            bob_y = center_y + animator.bob_offset if is_flying else center_y
            bob_x = center_x if is_flying else center_x + animator.sway_offset

            if animator.animation_type != 'death':
                self._draw_mirror_images(
                    display_sprite,
                    (int(bob_x), int(bob_y)),
                    self._active_duplicate_count(enemy),
                )

            sprite_rect = display_sprite.get_rect(center=(bob_x, bob_y))
            self._last_enemy_target_rect = sprite_rect.copy()
            self.screen.blit(display_sprite, sprite_rect)
        else:
            # Fallback to simple representation
            enemy_size = 150
            fallback_x = center_x if is_flying else center_x + animator.sway_offset
            fallback_y = center_y + animator.bob_offset if is_flying else center_y
            pygame.draw.circle(self.screen, self.colors['enemy'], 
                             (int(fallback_x), int(fallback_y)), enemy_size)
            self._last_enemy_target_rect = pygame.Rect(
                int(fallback_x - enemy_size),
                int(fallback_y - enemy_size),
                enemy_size * 2,
                enemy_size * 2,
            )
            
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

        self._render_ability_status_visuals(enemy, "enemy", include_duplicates=False)
        
        # Enemy name label at top of sprite
        font = pygame.font.Font(None, 36)
        name_surf = font.render(enemy.name, True, (255, 255, 255))
        # Add shadow for better readability
        shadow_surf = font.render(enemy.name, True, (0, 0, 0))
        name_rect = name_surf.get_rect(center=(center_x, center_y - enemy_size - 40))
        shadow_rect = shadow_surf.get_rect(center=(center_x + 2, center_y - enemy_size - 38))
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(name_surf, name_rect)
        
        # Enemy HP/MP bars above name (only visible with sight)
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
            hp_text = f"HP {enemy.health.current}/{enemy.health.max}"
            hp_surf = hp_font.render(hp_text, True, (255, 255, 255))
            hp_rect = hp_surf.get_rect(center=(center_x, bar_y + bar_height // 2))
            self.screen.blit(hp_surf, hp_rect)

            resource_bottom = bar_y + bar_height
            enemy_mana = getattr(enemy, "mana", None)
            if enemy_mana is not None and getattr(enemy_mana, "max", 0) > 0:
                mp_y = resource_bottom + 6
                pygame.draw.rect(self.screen, (40, 40, 40),
                               pygame.Rect(bar_x, mp_y, bar_width, bar_height))
                mp_ratio = enemy_mana.current / max(enemy_mana.max, 1)
                mp_width = int(bar_width * mp_ratio)
                pygame.draw.rect(self.screen, self.colors['mp_bar'],
                               pygame.Rect(bar_x, mp_y, mp_width, bar_height))
                pygame.draw.rect(self.screen, (150, 150, 150),
                               pygame.Rect(bar_x, mp_y, bar_width, bar_height), 2)
                mp_text = f"MP {enemy_mana.current}/{enemy_mana.max}"
                mp_surf = hp_font.render(mp_text, True, (255, 255, 255))
                mp_rect = mp_surf.get_rect(center=(center_x, mp_y + bar_height // 2))
                self.screen.blit(mp_surf, mp_rect)
                resource_bottom = mp_y + bar_height

            # Status icons under the HP bar
            icons = self._collect_status_icons(enemy)
            if icons:
                self._render_status_icons(icons, bar_x, resource_bottom + 8, max_width=bar_width)

        self._render_active_impact_effects()
        self._render_floating_texts()

    def render_combat_overlay(self, player_char, enemy, actions, selected_action, current_turn=None, show_enemy_details=None):
        """Render combat UI overlay (action menu and combat log) over the dungeon view."""
        self._set_combat_log_actors(player_char, enemy)
        self._last_player_target_rect = pygame.Rect(
            26,
            self.screen_height - 312,
            max(180, int(self.screen_width * 0.24)),
            130,
        )
        self._render_player_danger_vignette(player_char)
        self._render_turn_indicator(player_char, enemy, current_turn=current_turn, overlay=True)
        self._render_telegraph_banner(enemy=enemy, overlay=True)
        has_sight = self._enemy_details_visible(player_char, enemy, show_enemy_details)
        self._render_enemy_info_panel(enemy, has_sight, overlay=True)
        self._render_ability_status_visuals(enemy, "enemy")
        self._render_ability_status_visuals(player_char, "player")

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
        
        log_rect = pygame.Rect(0, log_y, view_width, log_height)
        self._draw_panel_surface(
            log_rect,
            fill=(15, 15, 20),
            border=(80, 80, 90),
            accent=(105, 90, 58),
            alpha=200,
            border_width=2,
        )
        
        # Messages
        font = pygame.font.Font(None, 22)
        y = log_y + 10
        line_height = 25
        max_lines = self.log_lines_per_page
        lines_rendered = 0
        
        display_lines = self._wrapped_combat_log_entries(view_width - 30, font=font, overlay=True)
        max_scroll = max(0, len(display_lines) - max_lines)
        self.log_scroll_offset = min(self.log_scroll_offset, max_scroll)

        for line in display_lines[self.log_scroll_offset:self.log_scroll_offset + max_lines]:
            if lines_rendered >= max_lines:
                break
            marker_color = (90, 90, 98) if line.continuation else line.marker_color
            pygame.draw.rect(self.screen, marker_color, pygame.Rect(11, y + 5, 4, 12))
            msg_surf = font.render(line.text, True, line.color)
            self.screen.blit(msg_surf, (31 if line.continuation else 20, y))
            y += line_height
            lines_rendered += 1

        if len(display_lines) > max_lines:
            indicator_font = pygame.font.Font(None, 18)
            if self.log_scroll_offset > 0:
                up_surf = indicator_font.render("^", True, (210, 210, 210))
                self.screen.blit(up_surf, (view_width - 24, log_y + 8))
            if self.log_scroll_offset < max_scroll:
                down_surf = indicator_font.render("v", True, (210, 210, 210))
                self.screen.blit(down_surf, (view_width - 24, log_y + log_height - 22))

            hint = indicator_font.render("PgUp/PgDn or Mouse Wheel", True, (170, 170, 170))
            self.screen.blit(hint, (view_width - hint.get_width() - 34, log_y + log_height - 22))

    def _render_action_menu_overlay(self, actions, selected_action):
        """Render action menu as semi-transparent overlay."""
        view_width = int(self.screen_width * 0.65)
        menu_height = 150
        menu_y = self.screen_height - menu_height
        
        menu_rect = pygame.Rect(0, menu_y, view_width, menu_height)
        self._draw_panel_surface(
            menu_rect,
            fill=(20, 20, 25),
            border=self.colors["action_border"],
            accent=self.colors["panel_accent"],
            alpha=220,
            border_width=3,
        )
        
        # Title
        font = pygame.font.Font(None, 30)
        title_surf = font.render("Choose Action:", True, (232, 224, 205))
        self.screen.blit(title_surf, (24, menu_y + 10))
        
        action_font = pygame.font.Font(None, 26)
        self._render_action_grid(
            actions,
            selected_action,
            rect=pygame.Rect(0, menu_y, view_width, menu_height),
            action_font=action_font,
            text_color=(240, 240, 240),
            highlight_color=(100, 100, 120),
            border_color=(150, 150, 170),
            translucent_highlight=True,
        )

    def _render_turn_indicator(self, player_char, enemy, current_turn=None, overlay=False):
        """Render a compact banner showing whose turn is active."""
        if current_turn not in {"player", "enemy"}:
            return
        current_actor = player_char if current_turn == "player" else enemy
        incapacitated = getattr(current_actor, "incapacitated", None)
        if callable(incapacitated) and incapacitated():
            return

        view_width = int(self.screen_width * 0.65) if overlay else self.combat_width
        token_size = 46
        text_left = token_size + 26
        min_height = 64
        label = "Your Turn" if current_turn == "player" else "Enemy Turn"
        sublabel = getattr(player_char, "name", "Player") if current_turn == "player" else getattr(enemy, "name", "Enemy")
        color = self.colors["turn_player" if current_turn == "player" else "turn_enemy"]

        font = pygame.font.Font(None, 26)
        small_font = pygame.font.Font(None, 18)
        label_surf = font.render(label, True, (255, 255, 255))

        max_width = max(120, view_width - 30)
        width = min(max(label_surf.get_width() + text_left + 14, small_font.size(sublabel)[0] + text_left + 14, 180), max_width)
        sublabel = self._truncate_text(small_font, sublabel, width - text_left - 14)
        sublabel_surf = small_font.render(sublabel, True, (220, 220, 220))
        rect = pygame.Rect(15, 170 if overlay else 12, width, min_height)

        if overlay:
            panel = pygame.Surface(rect.size)
            panel.set_alpha(210)
            panel.fill((18, 18, 24))
            self.screen.blit(panel, rect.topleft)
        else:
            pygame.draw.rect(self.screen, (18, 18, 24), rect)

        pygame.draw.rect(self.screen, color, rect, 3)
        if current_turn == "player":
            try:
                token = self.player_token_manager.get_scaled_token(player_char, (token_size, token_size))
            except Exception as exc:  # pragma: no cover - defensive runtime fallback for external art failures
                print(f"Failed to render player token for {getattr(player_char, 'name', player_char)}: {exc}")
                token = None
        else:
            try:
                token = self.enemy_token_manager.get_scaled_token(enemy, (token_size, token_size))
            except Exception as exc:  # pragma: no cover - defensive runtime fallback for external art failures
                print(f"Failed to render enemy token for {getattr(enemy, 'name', enemy)}: {exc}")
                token = None
        if token is not None:
            self.screen.blit(token, (rect.left + 8, rect.centery - token_size // 2))
        self.screen.blit(label_surf, (rect.left + text_left, rect.top + 8))
        self.screen.blit(sublabel_surf, (rect.left + text_left, rect.top + 34))

    def _latest_telegraph_line(self, actor=None) -> str | None:
        if self._active_telegraph_line:
            if actor is None or self._message_starts_with_actor(self._active_telegraph_line, actor):
                return self._active_telegraph_line
        if self._suppress_logged_telegraph_banner:
            return None
        for message in reversed(self.combat_log):
            for line in reversed([segment.strip() for segment in message.split("\n") if segment.strip()]):
                if self._is_telegraph_message(line) and (
                    actor is None or self._message_starts_with_actor(line, actor)
                ):
                    return line
        return None

    @staticmethod
    def _message_starts_with_actor(message: str, actor) -> bool:
        actor_name = getattr(actor, "name", "")
        return bool(actor_name and message.startswith(f"{actor_name} "))

    def _render_telegraph_banner(self, enemy=None, overlay: bool = False) -> None:
        line = self._latest_telegraph_line(actor=enemy)
        if not line:
            return

        available_width = self.combat_width - 56
        if available_width <= 0:
            return

        title_font = pygame.font.Font(None, 20)
        body_font = pygame.font.Font(None, 19)
        title_text = "Incoming"
        title_surf = title_font.render(title_text, True, (246, 238, 216))
        body_text = self._truncate_text(body_font, line, max(120, available_width - 128))
        body_surf = body_font.render(body_text, True, self.colors["telegraph"])

        width = min(max(title_surf.get_width() + body_surf.get_width() + 102, 340), available_width)
        height = 46
        x = max(20, (self.combat_width - width) // 2)
        y = 205 if overlay else 74
        rect = pygame.Rect(x, y, width, height)

        self._draw_panel_surface(
            rect,
            fill=(26, 20, 14),
            border=self.colors["telegraph"],
            accent=(176, 96, 58),
            alpha=225,
            border_width=2,
        )
        pygame.draw.rect(self.screen, (132, 58, 42), pygame.Rect(rect.left + 10, rect.top + 9, 7, rect.height - 18))
        pygame.draw.circle(self.screen, self.colors["telegraph"], (rect.left + 30, rect.centery), 5)
        self.screen.blit(title_surf, (rect.left + 44, rect.top + 6))
        self.screen.blit(body_surf, (rect.left + 44, rect.top + 24))
