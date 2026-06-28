"""
Dungeon HUD (Heads-Up Display)
Displays character stats, minimap, inventory quick-access, and other UI elements.
"""

import pygame

from src.core import map_tiles
from src.core.player import LIMINAL_GAP_LEVEL, REALM_OF_CAMBION_LEVEL
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


class DungeonHUD:
    """
    Manages the HUD overlay for dungeon exploration.
    Shows character stats, minimap, compass, inventory, etc.
    """
    
    def __init__(self, presenter):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height
        
        # HUD takes up right side (35% of screen)
        self.hud_width = int(self.width * 0.35)
        self.hud_x = self.width - self.hud_width
        self.hud_rect = pygame.Rect(self.hud_x, 0, self.hud_width, self.height)
        
        # Font sizes
        self.title_font = pygame.font.Font(None, 32)
        self.stat_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
        # Colors
        self.bg_color = (25, 25, 30)
        self.border_color = (100, 100, 110)
        self.text_color = (220, 220, 220)
        self.hp_color = (200, 50, 50)
        self.mp_color = (50, 100, 200)
        self.exp_color = (100, 200, 100)
        self.status_colors = STATUS_ICON_COLORS
        self.last_minimap_rect: pygame.Rect | None = None
        
    def render_hud(self, player_char, combat_mode=False, enemy=None):
        """Render the complete HUD.
        
        Args:
            player_char: The player character
            combat_mode: Whether we're in combat (shows combat indicator)
            enemy: The enemy being fought (if in combat)
        """
        # Background
        pygame.draw.rect(self.screen, self.bg_color, self.hud_rect)
        pygame.draw.line(self.screen, self.border_color, 
                        (self.hud_x, 0), (self.hud_x, self.height), 3)
        
        y_offset = 20
        
        # Combat mode indicator (if in combat)
        if combat_mode:
            y_offset = self._render_combat_indicator(enemy, y_offset)
            y_offset += 15
        
        # Character name and level
        y_offset = self._render_character_info(player_char, y_offset)
        y_offset += 20

        if not combat_mode:
            y_offset = self._render_location_label(player_char, y_offset)
            y_offset += 12
        
        # Health and Mana bars
        y_offset = self._render_resource_bars(player_char, y_offset)
        y_offset += 20

        # Status icons (combat only)
        if combat_mode:
            y_offset = self._render_status_icons(player_char, y_offset)
            y_offset += 15

        if combat_mode:
            feature_height = self._combat_feature_height()
            feature_y = self._combat_feature_title_y(feature_height)
            self._render_combat_features(player_char, enemy, feature_y, feature_height=feature_height)
            return

        # Compass - hide during combat and keep it above the anchored minimap.
        if not combat_mode:
            y_offset = self._render_compass(player_char, y_offset)
            y_offset += 20

        # Minimap stays pinned low in the HUD during exploration.
        minimap_size = self._minimap_size(combat_mode=False)
        minimap_y = self._minimap_title_y(minimap_size)
        self._render_minimap(player_char, minimap_y, minimap_size=minimap_size)

    @staticmethod
    def location_label(player_char) -> str:
        """Return the player-facing label for the current world location."""
        try:
            location_z = int(getattr(player_char, "location_z", 0) or 0)
        except (TypeError, ValueError):
            location_z = 0
        if location_z == 0:
            return "Town"
        if location_z == REALM_OF_CAMBION_LEVEL:
            return "Realm of Cambion"
        if location_z == LIMINAL_GAP_LEVEL:
            return "Liminal Gap"
        return f"Dungeon Level {location_z}"

    def _render_location_label(self, player_char, y_offset):
        """Render a compact location label in exploration HUD mode."""
        x_margin = self.hud_x + 20
        label = self.location_label(player_char)
        label_surface = self.small_font.render(label, True, (220, 205, 145))
        label_rect = pygame.Rect(x_margin, y_offset, self.hud_width - 40, label_surface.get_height() + 10)
        pygame.draw.rect(self.screen, (35, 31, 25), label_rect)
        pygame.draw.rect(self.screen, (150, 130, 80), label_rect, 1)
        text_x = label_rect.left + max(8, (label_rect.width - label_surface.get_width()) // 2)
        self.screen.blit(label_surface, (text_x, label_rect.top + 5))
        return label_rect.bottom

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
            "Bleed": "RND",
            "Disarm": "DSA",
            "Prone": "PRN",
            "Attack": "ATK",
            "Defense": "DEF",
            "Magic": "MAG",
            "Magic Defense": "MDF",
            "Speed": "SPD",
            "DOT": "DOT",
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
        positive_status = set()
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
                icons.append((self._effect_label(name), False))
        for name, effect in character.stat_effects.items():
            if name not in skip_effects:
                icon = stat_effect_status_icon(self._effect_label(name), effect)
                if icon is not None:
                    icons.append(icon)
        for name, effect in character.magic_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_magic))
        for name, effect in character.class_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), True))

        # Maelstrom Weapon passive stack indicator (display current consecutive hit stacks)
        try:
            maelstrom_hits = int(getattr(character, "maelstrom_hits", 0))
            skills = getattr(character, "spellbook", {}).get("Skills", {})
            has_maelstrom = "Maelstrom Weapon" in skills
            if has_maelstrom and maelstrom_hits > 0:
                icons.append((f"MW{maelstrom_hits}", True))
        except (AttributeError, TypeError, ValueError):
            pass

        return prioritize_status_icons(combine_duplicate_status_icons(icons))

    def _render_status_icons(self, player_char, y_offset, max_rows=2):
        x_margin = self.hud_x + 20
        icons = self._collect_status_icons(player_char)
        if not icons:
            return y_offset

        icon_w = 42
        icon_h = 26
        padding = 6
        max_width = self.hud_width - 40
        per_row = max(1, max_width // (icon_w + padding))
        visible_icons = compact_status_icons(icons, per_row, max_rows)
        font = pygame.font.Font(None, 16)

        for idx, (label, is_positive) in enumerate(visible_icons):
            row = idx // per_row
            col = idx % per_row
            icon_x = x_margin + col * (icon_w + padding)
            icon_y = y_offset + row * (icon_h + padding)
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

        rows = (len(visible_icons) + per_row - 1) // per_row
        return y_offset + rows * (icon_h + padding)
    
    def _render_character_info(self, player_char, y_offset):
        """Render character name, race, class, and level."""
        x_margin = self.hud_x + 20
        
        # Name
        name_text = self.title_font.render(player_char.name, True, (255, 215, 0))
        self.screen.blit(name_text, (x_margin, y_offset))
        y_offset += 35
        
        # Race and Class
        race_name = player_char.race.name if getattr(player_char, "race", None) else "Unknown"
        class_name = player_char.cls.name if getattr(player_char, "cls", None) else "Unknown"
        info_text = f"{race_name} {class_name}"
        info_surface = self.stat_font.render(info_text, True, self.text_color)
        self.screen.blit(info_surface, (x_margin, y_offset))
        y_offset += 30
        
        # Level and XP
        level_text = f"Level {player_char.level.level}"
        level_surface = self.stat_font.render(level_text, True, self.exp_color)
        self.screen.blit(level_surface, (x_margin, y_offset))
        y_offset += 25
        
        # XP Bar
        xp_width = self.hud_width - 40
        
        # Check if player is at max level
        if isinstance(player_char.level.exp_to_gain, str):
            # Max level - show full XP bar
            xp_percent = 1.0
            xp_text = "MAX LEVEL"
        else:
            # Calculate XP progress for current level
            # level_exp() returns total XP needed for current level
            # exp_to_gain counts down from level_exp() to 0
            # So progress = level_exp() - exp_to_gain
            total_xp_for_level = player_char.level_exp()
            current_progress = total_xp_for_level - player_char.level.exp_to_gain
            xp_percent = min(1.0, max(0.0, current_progress / max(1, total_xp_for_level)))
            xp_text = f"{current_progress}/{total_xp_for_level} XP"
        
        # XP bar background
        pygame.draw.rect(self.screen, (40, 40, 45), 
                        pygame.Rect(x_margin, y_offset, xp_width, 15))
        # XP bar fill
        pygame.draw.rect(self.screen, self.exp_color,
                        pygame.Rect(x_margin, y_offset, int(xp_width * xp_percent), 15))
        # XP bar border
        pygame.draw.rect(self.screen, self.border_color,
                        pygame.Rect(x_margin, y_offset, xp_width, 15), 1)
        
        # XP text - show progress toward next level
        xp_surface = self.small_font.render(xp_text, True, self.text_color)
        text_x = x_margin + (xp_width - xp_surface.get_width()) // 2
        self.screen.blit(xp_surface, (text_x, y_offset - 1))
        y_offset += 20
        
        return y_offset
    
    def _render_resource_bars(self, player_char, y_offset):
        """Render HP and MP bars."""
        x_margin = self.hud_x + 20
        bar_width = self.hud_width - 40
        bar_height = 25
        
        # HP Bar
        hp_percent = player_char.health.current / max(1, player_char.health.max)
        hp_text = f"HP: {player_char.health.current}/{player_char.health.max}"
        
        # HP background
        pygame.draw.rect(self.screen, (40, 40, 45),
                        pygame.Rect(x_margin, y_offset, bar_width, bar_height))
        # HP fill
        pygame.draw.rect(self.screen, self.hp_color,
                        pygame.Rect(x_margin, y_offset, int(bar_width * hp_percent), bar_height))
        # HP border
        pygame.draw.rect(self.screen, self.border_color,
                        pygame.Rect(x_margin, y_offset, bar_width, bar_height), 2)
        
        # HP text
        hp_surface = self.stat_font.render(hp_text, True, (255, 255, 255))
        text_x = x_margin + (bar_width - hp_surface.get_width()) // 2
        self.screen.blit(hp_surface, (text_x, y_offset + 2))
        y_offset += bar_height + 10
        
        # MP Bar
        mp_percent = player_char.mana.current / max(1, player_char.mana.max)
        mp_text = f"MP: {player_char.mana.current}/{player_char.mana.max}"
        
        # MP background
        pygame.draw.rect(self.screen, (40, 40, 45),
                        pygame.Rect(x_margin, y_offset, bar_width, bar_height))
        # MP fill
        pygame.draw.rect(self.screen, self.mp_color,
                        pygame.Rect(x_margin, y_offset, int(bar_width * mp_percent), bar_height))
        # MP border
        pygame.draw.rect(self.screen, self.border_color,
                        pygame.Rect(x_margin, y_offset, bar_width, bar_height), 2)
        
        # MP text
        mp_surface = self.stat_font.render(mp_text, True, (255, 255, 255))
        text_x = x_margin + (bar_width - mp_surface.get_width()) // 2
        self.screen.blit(mp_surface, (text_x, y_offset + 2))
        y_offset += bar_height + 5
        
        return y_offset
    
    def _render_stats(self, player_char, y_offset):
        """Render character statistics."""
        x_margin = self.hud_x + 20
        
        # Title
        stats_title = self.stat_font.render("Stats", True, (200, 200, 50))
        self.screen.blit(stats_title, (x_margin, y_offset))
        y_offset += 28
        
        # Stats
        stats = [
            ("STR", player_char.stats.strength),
            ("INT", player_char.stats.intel),
            ("WIS", player_char.stats.wisdom),
            ("CON", player_char.stats.con),
            ("DEX", player_char.stats.dex),
            ("CHA", player_char.stats.charisma),
        ]
        
        # Render in two columns
        col_width = (self.hud_width - 40) // 2
        for i, (stat_name, stat_value) in enumerate(stats):
            col = i % 2
            row = i // 2
            x = x_margin + (col * col_width)
            y = y_offset + (row * 22)
            
            stat_text = f"{stat_name}: {stat_value}"
            stat_surface = self.small_font.render(stat_text, True, self.text_color)
            self.screen.blit(stat_surface, (x, y))
        
        y_offset += (len(stats) // 2 + 1) * 22
        return y_offset
    
    def _minimap_size(self, combat_mode: bool = False) -> int:
        max_size = max(80, self.hud_width - 40)
        if combat_mode:
            return min(max_size, max(220, self.height - 420))
        return min(max_size, max(220, self.height - 450))

    def _minimap_title_y(self, minimap_size: int) -> int:
        return max(20, self.height - minimap_size - 52)

    def _combat_feature_height(self) -> int:
        return min(max(190, self.height - 420), 260)

    def _combat_feature_title_y(self, feature_height: int) -> int:
        return max(20, self.height - feature_height - 52)

    @staticmethod
    def _truncate_text(font, text: str, max_width: int) -> str:
        text = str(text)
        def width(value: str) -> int:
            size = getattr(font, "size", None)
            if callable(size):
                return size(value)[0]
            return font.render(value, True, (255, 255, 255)).get_width()

        if width(text) <= max_width:
            return text
        ellipsis = "..."
        while text and width(text + ellipsis) > max_width:
            text = text[:-1]
        return text + ellipsis if text else ellipsis

    @staticmethod
    def _level_value(entity) -> int | None:
        level = getattr(entity, "level", None)
        for attr in ("level", "pro_level"):
            value = getattr(level, attr, None)
            if value is not None:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return None
        return None

    @staticmethod
    def _totem_effect(player_char):
        try:
            effect = player_char.magic_effects.get("Totem")
        except AttributeError:
            return None
        return effect if effect and getattr(effect, "active", False) else None

    @staticmethod
    def _totem_summary(effect) -> tuple[str, str]:
        extra = getattr(effect, "extra", None)
        if not isinstance(extra, dict):
            return "Totem", "Active"
        aspect = str(extra.get("aspect") or "Totem")
        secondary_labels = {
            "reflect": "Reflect",
            "healing": "Healing",
            "elemental": "Elemental",
            "speed": "Speed",
            "crit_damage": "Crit Dmg",
        }
        benefits = []
        try:
            attack_bonus = float(extra.get("attack_bonus", 0) or 0)
            defense_bonus = float(extra.get("defense_bonus", 0) or 0)
        except (TypeError, ValueError):
            attack_bonus = defense_bonus = 0
        if attack_bonus > 0:
            benefits.append(f"+{int(attack_bonus * 100)}% ATK")
        if defense_bonus > 0:
            benefits.append(f"+{int(defense_bonus * 100)}% DEF")
        secondary = secondary_labels.get(extra.get("secondary"))
        if secondary:
            benefits.append(secondary)
        return f"{aspect} Totem", ", ".join(benefits) or "Active"

    def _combat_feature_lines(self, player_char, enemy=None) -> list[tuple[str, str, tuple[int, int, int]]]:
        lines: list[tuple[str, str, tuple[int, int, int]]] = []
        cls_name = getattr(getattr(player_char, "cls", None), "name", "Adventurer")
        lines.append(("Class", cls_name, self.text_color))

        familiar = getattr(player_char, "familiar", None)
        if familiar:
            familiar_name = getattr(familiar, "name", "Familiar")
            spec = getattr(familiar, "spec", "")
            level = self._level_value(familiar)
            suffix = f"{spec} Lv {level}" if spec and level is not None else spec or (f"Lv {level}" if level is not None else "Ready")
            lines.append(("Familiar", familiar_name, (170, 210, 255)))
            lines.append(("Bond", suffix, self.text_color))

        summons = getattr(player_char, "summons", {}) or {}
        active_summons = []
        for summon in summons.values():
            is_alive = getattr(summon, "is_alive", None)
            if callable(is_alive) and not is_alive():
                continue
            active_summons.append(getattr(summon, "name", str(summon)))
        if active_summons:
            summary = ", ".join(active_summons[:2])
            if len(active_summons) > 2:
                summary += f" +{len(active_summons) - 2}"
            lines.append(("Summons", summary, (170, 210, 255)))

        totem = self._totem_effect(player_char)
        if totem:
            label, benefits = self._totem_summary(totem)
            lines.append(("Totem", label, (230, 205, 120)))
            lines.append(("Benefit", benefits, self.text_color))
            lines.append(("Turns", getattr(totem, "duration", 0), self.text_color))

        class_effects = getattr(player_char, "class_effects", {}) or {}
        for name, effect in class_effects.items():
            if getattr(effect, "active", False):
                lines.append((name, f"{getattr(effect, 'duration', 0)} turns", (200, 190, 255)))

        if len(lines) == 1:
            enemy_name = getattr(enemy, "name", "Enemy")
            lines.append(("Target", enemy_name, self.text_color))
            lines.append(("Focus", "No class feature active", self.GRAY if hasattr(self, "GRAY") else (145, 145, 155)))
        return lines

    def _render_totem_focus_glyph(self, rect: pygame.Rect, effect) -> None:
        extra = getattr(effect, "extra", None)
        aspect = extra.get("aspect", "Earth") if isinstance(extra, dict) else "Earth"
        colors = {
            "Earth": (142, 104, 62),
            "Water": (78, 156, 212),
            "Fire": (220, 92, 48),
            "Wind": (150, 204, 166),
            "Soul": (180, 122, 220),
        }
        color = colors.get(aspect, (160, 136, 86))
        center_x = rect.right - 44
        base_y = rect.bottom - 30
        pygame.draw.ellipse(self.screen, (18, 16, 18), pygame.Rect(center_x - 34, base_y + 12, 68, 16))
        pygame.draw.ellipse(self.screen, color, pygame.Rect(center_x - 42, base_y + 4, 84, 28), 2)
        shaft = pygame.Rect(center_x - 6, base_y - 34, 12, 50)
        pygame.draw.rect(self.screen, color, shaft, border_radius=3)
        pygame.draw.rect(self.screen, (35, 28, 24), shaft, 2, border_radius=3)
        head = pygame.Rect(center_x - 18, base_y - 52, 36, 24)
        pygame.draw.rect(self.screen, tuple(min(255, c + 38) for c in color), head, border_radius=4)
        pygame.draw.rect(self.screen, (35, 28, 24), head, 2, border_radius=4)
        pygame.draw.circle(self.screen, (248, 226, 142), head.center, 4)

    def _render_combat_features(self, player_char, enemy, y_offset, feature_height=None):
        """Render combat-relevant class systems in place of the exploration minimap."""
        x_margin = self.hud_x + 20
        panel_width = self.hud_width - 40
        feature_height = feature_height or self._combat_feature_height()
        title = self.stat_font.render("Combat Focus", True, (150, 150, 255))
        self.screen.blit(title, (x_margin, y_offset))
        panel_rect = pygame.Rect(x_margin, y_offset + 30, panel_width, feature_height - 30)
        pygame.draw.rect(self.screen, (15, 15, 20), panel_rect)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 2)

        lines = self._combat_feature_lines(player_char, enemy)
        y = panel_rect.top + 12
        label_w = 78
        max_value_w = max(60, panel_rect.width - label_w - 26)
        for label, value, color in lines[:7]:
            if y + 20 > panel_rect.bottom - 12:
                break
            label_surf = self.small_font.render(f"{label}:", True, (170, 170, 180))
            self.screen.blit(label_surf, (panel_rect.left + 12, y))
            value_text = self._truncate_text(self.small_font, str(value), max_value_w)
            value_surf = self.small_font.render(value_text, True, color)
            self.screen.blit(value_surf, (panel_rect.left + 12 + label_w, y))
            y += 22

        totem = self._totem_effect(player_char)
        if totem:
            self._render_totem_focus_glyph(panel_rect, totem)

        return panel_rect.bottom + 5

    def _render_minimap(
        self,
        player_char,
        y_offset,
        minimap_size=None,
        *,
        x_margin: int | None = None,
        title: str = "Map",
        full_level: bool = False,
    ):
        """Render minimap showing nearby explored areas."""
        x_margin = self.hud_x + 20 if x_margin is None else x_margin
        minimap_size = minimap_size or min(200, self.hud_width - 40)
        visible_adjacent = self._get_visible_adjacent_positions(player_char)
        
        # Title
        if title:
            map_title = self.stat_font.render(title, True, (150, 150, 255))
            self.screen.blit(map_title, (x_margin, y_offset))
            y_offset += 28
        
        # Minimap background
        minimap_rect = pygame.Rect(x_margin, y_offset, minimap_size, minimap_size)
        self.last_minimap_rect = minimap_rect
        pygame.draw.rect(self.screen, (15, 15, 20), minimap_rect)
        pygame.draw.rect(self.screen, self.border_color, minimap_rect, 2)
        
        player_x, player_y = player_char.location_x, player_char.location_y

        if full_level:
            positions = self._revealed_level_minimap_positions(player_char, visible_adjacent)
            if not positions:
                positions = [(player_x, player_y)]
            min_x = min(x for x, _y in positions)
            max_x = max(x for x, _y in positions)
            min_y = min(y for _x, y in positions)
            max_y = max(y for _x, y in positions)
            grid_width = max(1, max_x - min_x + 1)
            grid_height = max(1, max_y - min_y + 1)
            tile_size = max(3, min(minimap_size // grid_width, minimap_size // grid_height))
            map_width = grid_width * tile_size
            map_height = grid_height * tile_size
            origin_x = x_margin + (minimap_size - map_width) // 2
            origin_y = y_offset + (minimap_size - map_height) // 2
            x_values = range(min_x, max_x + 1)
            y_values = range(min_y, max_y + 1)
        else:
            tile_size = minimap_size // 11  # Show 11x11 grid
            origin_x = x_margin
            origin_y = y_offset
            x_values = range(player_x - 5, player_x + 6)
            y_values = range(player_y - 5, player_y + 6)

        for tile_y in y_values:
            for tile_x in x_values:
                tile = player_char.world_dict.get((tile_x, tile_y, player_char.location_z))

                if full_level:
                    screen_x = origin_x + (tile_x - min_x) * tile_size
                    screen_y = origin_y + (tile_y - min_y) * tile_size
                else:
                    screen_x = origin_x + (tile_x - (player_x - 5)) * tile_size
                    screen_y = origin_y + (tile_y - (player_y - 5)) * tile_size
                tile_rect = pygame.Rect(screen_x, screen_y, tile_size - 1, tile_size - 1)
                
                if tile:
                    tile_type = type(tile).__name__
                    is_funhouse_wall = tile_type in ('FunhouseWall', 'MirrorWall')
                    is_directly_visible = (tile_x, tile_y) in visible_adjacent
                    is_discovered_explorable = bool(
                        getattr(tile, 'near', False)
                        and getattr(tile, 'enter', True)
                        and tile_type not in ('FakeWall', 'FunhouseWall', 'MirrorWall')
                    )
                    is_discovered_special = bool(
                        getattr(tile, 'near', False) and (
                            any(
                                marker in tile_type
                                for marker in (
                                    'Chest',
                                    'Stairs',
                                    'Ladder',
                                    'Door',
                                    'WarpPoint',
                                    'UndergroundSpring',
                                    'SecretShop',
                                    'Relic',
                                )
                            ) or (
                                'GoldenChaliceRoom' in tile_type
                                and map_tiles.chalice_altar_visible(player_char)
                            )
                        )
                    )
                    
                    if tile_x == player_x and tile_y == player_y:
                        # Player position - draw base tile first, then player marker with arrow
                        if getattr(tile, 'visited', False):
                            if is_funhouse_wall or not getattr(tile, 'enter', True):
                                pygame.draw.rect(self.screen, (80, 80, 90), tile_rect)
                            else:
                                pygame.draw.rect(self.screen, (120, 120, 130), tile_rect)
                        self._render_minimap_player_marker(tile_rect, player_char.facing, tile_size)
                        
                    elif getattr(tile, 'visited', False) or is_directly_visible or is_discovered_explorable or is_discovered_special:
                        # Explored tile (visited) or directly visible adjacent tile
                        is_visited = getattr(tile, 'visited', False)
                        is_near = getattr(tile, 'near', False)
                        is_fire_path = tile_type in ('FirePath', 'FirePathSpecial')
                        if tile_type == 'FakeWall':
                            # Keep FakeWall hidden unless actually visited
                            if is_visited:
                                pygame.draw.rect(self.screen, (150, 100, 150), tile_rect)
                            else:
                                pygame.draw.rect(self.screen, (80, 80, 90), tile_rect)
                        elif is_funhouse_wall:
                            wall_color = (130, 90, 145) if is_visited else (85, 70, 95)
                            pygame.draw.rect(self.screen, wall_color, tile_rect)
                        elif is_fire_path and is_visited:
                            # Discovered FirePath tiles render as red heat zones on the minimap
                            pygame.draw.rect(self.screen, (175, 55, 55), tile_rect)
                        elif is_discovered_special and not is_visited:
                            # Persist discovered special tiles without re-enabling broad near-tile shading
                            pygame.draw.rect(self.screen, (100, 100, 110), tile_rect)
                        elif not getattr(tile, 'enter', True):
                            # Wall
                            wall_color = (80, 80, 90) if is_visited else (70, 70, 80)
                            pygame.draw.rect(self.screen, wall_color, tile_rect)
                        else:
                            # Corridor
                            if is_visited:
                                corridor_color = (120, 120, 130)
                            elif is_near:
                                corridor_color = (105, 105, 115)
                            else:
                                corridor_color = (95, 95, 105)
                            pygame.draw.rect(self.screen, corridor_color, tile_rect)

                        if self._is_minimap_special_tile(tile_type, tile, player_char):
                            self._render_minimap_special_outline(tile_rect, tile_size)
                        
                        # Draw icons for special features on visible/discovered tiles
                        if 'Chest' in tile_type:
                            self._render_minimap_chest_icon(tile, screen_x, screen_y, tile_size)

                        if 'Door' in tile_type:
                            self._render_minimap_door_icon(tile, screen_x, screen_y, tile_size)
                        
                        if 'Relic' in tile_type and not getattr(tile, 'read', False):
                            # Relic (uncollected) - cyan/bright blue diamond
                            icon_size = tile_size // 3
                            center_x = screen_x + tile_size // 2
                            center_y = screen_y + tile_size // 2
                            points = [(center_x, center_y - icon_size // 2),
                                     (center_x + icon_size // 2, center_y),
                                     (center_x, center_y + icon_size // 2),
                                     (center_x - icon_size // 2, center_y)]
                            pygame.draw.polygon(self.screen, (0, 255, 255), points)

                        if 'RelicRoom' in tile_type and getattr(tile, 'read', False):
                            # Relic altar (collected) - gold diamond
                            icon_size = tile_size // 3
                            center_x = screen_x + tile_size // 2
                            center_y = screen_y + tile_size // 2
                            points = [(center_x, center_y - icon_size // 2),
                                     (center_x + icon_size // 2, center_y),
                                     (center_x, center_y + icon_size // 2),
                                     (center_x - icon_size // 2, center_y)]
                            pygame.draw.polygon(self.screen, (255, 215, 0), points)

                        if 'GoldenChaliceRoom' in tile_type and map_tiles.chalice_altar_visible(player_char):
                            # Chalice altar - warm gold cup marker
                            icon_width = max(2, tile_size // 2)
                            icon_height = max(2, tile_size // 3)
                            icon_x = screen_x + (tile_size - icon_width) // 2
                            icon_y = screen_y + (tile_size - icon_height) // 2
                            chalice_color = (196, 160, 70) if getattr(tile, 'read', False) else (255, 215, 0)
                            pygame.draw.rect(
                                self.screen,
                                chalice_color,
                                pygame.Rect(icon_x, icon_y + icon_height // 3, icon_width, max(2, icon_height // 2)),
                            )
                            stem_width = max(1, icon_width // 4)
                            stem_height = max(2, icon_height // 3)
                            stem_x = screen_x + (tile_size - stem_width) // 2
                            stem_y = icon_y + icon_height // 3
                            pygame.draw.rect(
                                self.screen,
                                chalice_color,
                                pygame.Rect(stem_x, stem_y, stem_width, stem_height),
                            )

                        if 'UndergroundSpring' in tile_type:
                            # Spring marker - cyan circle
                            icon_radius = max(2, tile_size // 4)
                            center = (screen_x + tile_size // 2, screen_y + tile_size // 2)
                            pygame.draw.circle(self.screen, (0, 200, 255), center, icon_radius)

                        if 'SecretShop' in tile_type:
                            # Secret shop marker - magenta square
                            icon_size = max(2, tile_size // 3)
                            icon_x = screen_x + (tile_size - icon_size) // 2
                            icon_y = screen_y + (tile_size - icon_size) // 2
                            pygame.draw.rect(self.screen, (200, 80, 200),
                                             pygame.Rect(icon_x, icon_y, icon_size, icon_size))
                        
                        if 'WarpPoint' in tile_type:
                            # Warp point / teleporter - green star
                            icon_size = tile_size // 3
                            center_x = screen_x + tile_size // 2
                            center_y = screen_y + tile_size // 2
                            # Draw 5-pointed star
                            import math
                            star_points = []
                            for i in range(5):
                                angle = math.radians(i * 72 - 90)  # Start from top
                                x = center_x + int(icon_size * math.cos(angle))
                                y = center_y + int(icon_size * math.sin(angle))
                                star_points.append((x, y))
                            # Draw star by connecting every other point
                            star_order = [0, 2, 4, 1, 3, 0]
                            star_lines = [star_points[star_order[i]] for i in range(len(star_order))]
                            pygame.draw.polygon(self.screen, (50, 255, 50), star_lines)
                        
                        if 'StairsDown' in tile_type or 'LadderDown' in tile_type:
                            # Stairs/Ladder down - red downward arrow
                            icon_size = tile_size // 3
                            center_x = screen_x + tile_size // 2
                            center_y = screen_y + tile_size // 2
                            points = [(center_x, center_y + icon_size // 2),
                                     (center_x - icon_size // 2, center_y - icon_size // 3),
                                     (center_x + icon_size // 2, center_y - icon_size // 3)]
                            pygame.draw.polygon(self.screen, (255, 50, 50), points)
                        
                        if 'StairsUp' in tile_type or 'LadderUp' in tile_type:
                            # Stairs/Ladder up - green upward arrow
                            icon_size = tile_size // 3
                            center_x = screen_x + tile_size // 2
                            center_y = screen_y + tile_size // 2
                            points = [(center_x, center_y - icon_size // 2),
                                     (center_x - icon_size // 2, center_y + icon_size // 3),
                                     (center_x + icon_size // 2, center_y + icon_size // 3)]
                            pygame.draw.polygon(self.screen, (50, 255, 50), points)
                    
        y_offset += minimap_size + 5
        return y_offset

    @staticmethod
    def _is_minimap_special_tile(tile_type: str, tile, player_char) -> bool:
        if any(
            marker in tile_type
            for marker in (
                'Chest',
                'Stairs',
                'Ladder',
                'Door',
                'WarpPoint',
                'UndergroundSpring',
                'SecretShop',
                'Relic',
            )
        ):
            return True
        return 'GoldenChaliceRoom' in tile_type and map_tiles.chalice_altar_visible(player_char)

    def _render_minimap_special_outline(self, tile_rect: pygame.Rect, tile_size: int) -> None:
        width = max(1, tile_size // 8)
        pygame.draw.rect(self.screen, (220, 180, 80), tile_rect, width)

    @staticmethod
    def _minimap_blink_on() -> bool:
        return (pygame.time.get_ticks() // 350) % 2 == 0

    def _render_minimap_player_marker(self, tile_rect: pygame.Rect, facing: str, tile_size: int) -> None:
        blink_on = self._minimap_blink_on()
        fill = (255, 255, 110) if blink_on else (245, 185, 35)
        outline = (255, 255, 255) if blink_on else (150, 110, 20)
        pygame.draw.rect(self.screen, fill, tile_rect)
        pygame.draw.rect(self.screen, outline, tile_rect, max(1, tile_size // 6))

        center_x = tile_rect.x + tile_size // 2
        center_y = tile_rect.y + tile_size // 2
        arrow_size = max(3, tile_size // 3)

        if facing == 'north':
            points = [(center_x, center_y - arrow_size),
                     (center_x - arrow_size//2, center_y + arrow_size//2),
                     (center_x + arrow_size//2, center_y + arrow_size//2)]
        elif facing == 'south':
            points = [(center_x, center_y + arrow_size),
                     (center_x - arrow_size//2, center_y - arrow_size//2),
                     (center_x + arrow_size//2, center_y - arrow_size//2)]
        elif facing == 'east':
            points = [(center_x + arrow_size, center_y),
                     (center_x - arrow_size//2, center_y - arrow_size//2),
                     (center_x - arrow_size//2, center_y + arrow_size//2)]
        else:  # west
            points = [(center_x - arrow_size, center_y),
                     (center_x + arrow_size//2, center_y - arrow_size//2),
                     (center_x + arrow_size//2, center_y + arrow_size//2)]

        pygame.draw.polygon(self.screen, (0, 0, 0), points)

    def _revealed_level_minimap_positions(self, player_char, visible_adjacent: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Return current-level positions visible enough for the enlarged map."""
        positions: set[tuple[int, int]] = {(player_char.location_x, player_char.location_y)}
        current_z = player_char.location_z
        for (tile_x, tile_y, tile_z), tile in getattr(player_char, "world_dict", {}).items():
            if tile_z != current_z or tile is None:
                continue
            if self._minimap_tile_is_revealed(player_char, tile_x, tile_y, tile, visible_adjacent):
                positions.add((tile_x, tile_y))
        return positions

    @staticmethod
    def _minimap_tile_is_revealed(player_char, tile_x: int, tile_y: int, tile, visible_adjacent: set[tuple[int, int]]) -> bool:
        tile_type = type(tile).__name__
        if getattr(tile, 'visited', False) or (tile_x, tile_y) in visible_adjacent:
            return True
        if (
            getattr(tile, 'near', False)
            and getattr(tile, 'enter', True)
            and tile_type not in ('FakeWall', 'FunhouseWall', 'MirrorWall')
        ):
            return True
        if not getattr(tile, 'near', False):
            return False
        special_markers = (
            'Chest',
            'Stairs',
            'Ladder',
            'Door',
            'WarpPoint',
            'UndergroundSpring',
            'SecretShop',
            'Relic',
        )
        if any(marker in tile_type for marker in special_markers):
            return True
        return 'GoldenChaliceRoom' in tile_type and map_tiles.chalice_altar_visible(player_char)

    def enlarged_map_rect(self) -> pygame.Rect:
        """Return the modal panel rectangle for the enlarged minimap."""
        panel_width = min(int(self.width * 0.78), 720)
        panel_height = min(int(self.height * 0.82), 680)
        return pygame.Rect(
            (self.width - panel_width) // 2,
            (self.height - panel_height) // 2,
            panel_width,
            panel_height,
        )

    def render_enlarged_minimap_modal(self, player_char) -> pygame.Rect:
        """Render the enlarged minimap modal and return its panel rect."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))

        panel_rect = self.enlarged_map_rect()
        pygame.draw.rect(self.screen, (18, 18, 24), panel_rect)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 3)

        title = f"{self.location_label(player_char)} Map"
        title_surface = self.stat_font.render(title, True, (220, 205, 145))
        self.screen.blit(title_surface, (panel_rect.left + 24, panel_rect.top + 18))

        close_surface = self.small_font.render("M/Esc: Close", True, self.text_color)
        close_rect = close_surface.get_rect(right=panel_rect.right - 24, top=panel_rect.top + 24)
        self.screen.blit(close_surface, close_rect)

        map_size = min(panel_rect.width - 64, panel_rect.height - 96)
        map_x = panel_rect.centerx - map_size // 2
        map_y = panel_rect.top + 56
        self._render_minimap(
            player_char,
            map_y,
            minimap_size=map_size,
            x_margin=map_x,
            title="",
            full_level=True,
        )
        return panel_rect

    @staticmethod
    def _tile_is_open(tile) -> bool:
        return bool(getattr(tile, 'open', False) or getattr(tile, 'opened', False))

    def _render_minimap_chest_icon(self, tile, screen_x: int, screen_y: int, tile_size: int) -> None:
        icon_size = max(3, tile_size // 3)
        icon_x = screen_x + (tile_size - icon_size) // 2
        icon_y = screen_y + (tile_size - icon_size) // 2
        icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)

        if self._tile_is_open(tile):
            pygame.draw.rect(self.screen, (130, 130, 120), icon_rect, 1)
            return

        pygame.draw.rect(self.screen, (255, 215, 0), icon_rect)

    def _render_minimap_door_icon(self, tile, screen_x: int, screen_y: int, tile_size: int) -> None:
        icon_width = max(4, tile_size // 2)
        icon_height = max(3, tile_size // 3)
        icon_x = screen_x + (tile_size - icon_width) // 2
        icon_y = screen_y + (tile_size - icon_height) // 2
        icon_rect = pygame.Rect(icon_x, icon_y, icon_width, icon_height)

        if self._tile_is_open(tile):
            pygame.draw.rect(self.screen, (95, 170, 120), icon_rect, 1)
            return

        pygame.draw.rect(self.screen, (139, 69, 19), icon_rect)

    def _get_visible_adjacent_positions(self, player_char):
        """Return adjacent N/S/E/W positions visible from the player's current tile."""
        visible = set()
        player_x, player_y, player_z = player_char.location_x, player_char.location_y, player_char.location_z
        current_tile = player_char.world_dict.get((player_x, player_y, player_z))

        directions = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
        }

        for direction, (dx, dy) in directions.items():
            tile_x = player_x + dx
            tile_y = player_y + dy
            adjacent_tile = player_char.world_dict.get((tile_x, tile_y, player_z))
            if adjacent_tile is None:
                continue
            if not self._is_direction_visible_from_tile(current_tile, direction, adjacent_tile):
                continue
            if player_char.world_dict.get((tile_x, tile_y, player_z)) is not None:
                visible.add((tile_x, tile_y))

        return visible

    def _is_direction_visible_from_tile(self, current_tile, direction, adjacent_tile=None):
        """Return whether a cardinal direction is visible from the current tile."""
        if not current_tile:
            return True

        opposite = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
        }

        # Closed doors block line of sight
        if 'Door' in type(current_tile).__name__ and not getattr(current_tile, 'open', False):
            return False
        if adjacent_tile and 'Door' in type(adjacent_tile).__name__ and not getattr(adjacent_tile, 'open', False):
            return False

        blocked = getattr(current_tile, 'blocked', None)
        if blocked and blocked.lower() == direction:
            if hasattr(current_tile, 'open') and getattr(current_tile, 'open', False):
                return True
            return False

        if adjacent_tile:
            adjacent_blocked = getattr(adjacent_tile, 'blocked', None)
            opposite_direction = opposite.get(direction)
            if adjacent_blocked and opposite_direction and adjacent_blocked.lower() == opposite_direction:
                if hasattr(adjacent_tile, 'open') and getattr(adjacent_tile, 'open', False):
                    return True
                return False

        return True
    
    def _render_compass(self, player_char, y_offset):
        """Render compass showing current facing direction."""
        x_margin = self.hud_x + 20
        compass_size = 60
        compass_center_x = x_margin + compass_size
        compass_center_y = y_offset + compass_size
        
        # Compass circle
        pygame.draw.circle(self.screen, (30, 30, 35), 
                          (compass_center_x, compass_center_y), compass_size)
        pygame.draw.circle(self.screen, self.border_color,
                          (compass_center_x, compass_center_y), compass_size, 2)
        
        # Cardinal directions
        directions = {
            'N': (0, -compass_size + 15),
            'E': (compass_size - 15, 0),
            'S': (0, compass_size - 15),
            'W': (-compass_size + 15, 0),
        }
        
        for direction, (dx, dy) in directions.items():
            text_surface = self.small_font.render(direction, True, self.text_color)
            text_rect = text_surface.get_rect(center=(compass_center_x + dx, compass_center_y + dy))
            self.screen.blit(text_surface, text_rect)
        
        # Facing indicator (arrow)
        facing_map = {
            'north': 0,
            'east': 90,
            'south': 180,
            'west': 270,
        }
        
        angle = facing_map.get(player_char.facing, 0)
        import math
        rad = math.radians(angle - 90)  # -90 to point upward at 0 degrees
        arrow_length = compass_size - 20
        
        end_x = compass_center_x + int(arrow_length * math.cos(rad))
        end_y = compass_center_y + int(arrow_length * math.sin(rad))
        
        pygame.draw.line(self.screen, (255, 50, 50),
                        (compass_center_x, compass_center_y), (end_x, end_y), 3)
        pygame.draw.circle(self.screen, (255, 50, 50), (end_x, end_y), 5)
        
        y_offset += compass_size * 2 + 10
        return y_offset
    
    def _render_quick_info(self, player_char, y_offset):
        """Render quick info like gold, depth, etc."""
        x_margin = self.hud_x + 20
        
        # Calculate depth - z=0 is town, z=1-6 are dungeon levels 1-6
        if player_char.location_z == 0:
            depth_str = "Town"
        else:
            depth_str = f"Level {player_char.location_z}"
        
        info_items = [
            f"Gold: {player_char.gold}",
            f"Depth: {depth_str}",
            f"Position: ({player_char.location_x}, {player_char.location_y})",
        ]
        
        for info in info_items:
            info_surface = self.small_font.render(info, True, self.text_color)
            self.screen.blit(info_surface, (x_margin, y_offset))
            y_offset += 20
        
        return y_offset

    def _render_combat_indicator(self, enemy, y_offset):
        """Render combat mode indicator at top of HUD."""
        x_margin = self.hud_x + 20
        
        # Combat banner background
        banner_width = self.hud_width - 40
        banner_height = 50
        banner_rect = pygame.Rect(x_margin - 10, y_offset - 5, banner_width + 20, banner_height)
        
        # Pulsing effect for combat indicator
        pulse = abs((pygame.time.get_ticks() % 1000) / 1000.0 - 0.5) * 2  # 0 to 1 and back
        alpha = int(150 + pulse * 80)  # 150-230
        
        # Draw semi-transparent red background
        combat_bg = pygame.Surface((banner_rect.width, banner_rect.height))
        combat_bg.set_alpha(alpha)
        combat_bg.fill((180, 30, 30))
        self.screen.blit(combat_bg, (banner_rect.x, banner_rect.y))
        
        # Border
        pygame.draw.rect(self.screen, (220, 50, 50), banner_rect, 3)
        
        # "COMBAT" text
        combat_font = pygame.font.Font(None, 32)
        combat_text = combat_font.render("** COMBAT **", True, (255, 255, 255))
        text_rect = combat_text.get_rect(center=(self.hud_x + self.hud_width // 2, y_offset + 10))
        self.screen.blit(combat_text, text_rect)
        
        # Enemy name below
        if enemy:
            enemy_font = pygame.font.Font(None, 24)
            enemy_text = enemy_font.render(f"vs. {enemy.name}", True, (255, 200, 200))
            enemy_rect = enemy_text.get_rect(center=(self.hud_x + self.hud_width // 2, y_offset + 32))
            self.screen.blit(enemy_text, enemy_rect)
        
        y_offset += banner_height + 5
        return y_offset
