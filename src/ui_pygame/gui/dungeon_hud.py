"""
Dungeon HUD (Heads-Up Display)
Displays character stats, minimap, inventory quick-access, and other UI elements.
"""

import pygame


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
        
        # Health and Mana bars
        y_offset = self._render_resource_bars(player_char, y_offset)
        y_offset += 20

        # Status icons (combat only)
        if combat_mode:
            y_offset = self._render_status_icons(player_char, y_offset)
            y_offset += 15
        
        # # Stats
        # y_offset = self._render_stats(player_char, y_offset)
        # y_offset += 20
        
        # Minimap
        y_offset = self._render_minimap(player_char, y_offset)
        y_offset += 40
        
        # Compass - hide during combat
        if not combat_mode:
            y_offset = self._render_compass(player_char, y_offset)
            y_offset += 20
        
        # Quick info
        # y_offset = self._render_quick_info(player_char, y_offset)

    def _effect_label(self, effect_name):
        labels = {
            "Berserk": "BRK",
            "Blind": "BLD",
            "Doom": "DOM",
            "Poison": "PSN",
            "Silence": "SIL",
            "Sleep": "SLP",
            "Stun": "STN",
            "Bleed": "BLD",
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
        }
        positive_status = set()
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

    def _render_status_icons(self, player_char, y_offset):
        x_margin = self.hud_x + 20
        icons = self._collect_status_icons(player_char)
        if not icons:
            return y_offset

        icon_w = 36
        icon_h = 18
        padding = 6
        max_width = self.hud_width - 40
        per_row = max(1, max_width // (icon_w + padding))
        font = pygame.font.Font(None, 16)

        for idx, (label, is_positive) in enumerate(icons):
            row = idx // per_row
            col = idx % per_row
            icon_x = x_margin + col * (icon_w + padding)
            icon_y = y_offset + row * (icon_h + padding)
            color = (70, 170, 90) if is_positive else (190, 70, 70)

            rect = pygame.Rect(icon_x, icon_y, icon_w, icon_h)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            pygame.draw.rect(self.screen, (20, 20, 20), rect, 1, border_radius=4)

            text_surf = font.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

        rows = (len(icons) + per_row - 1) // per_row
        return y_offset + rows * (icon_h + padding)
    
    def _render_character_info(self, player_char, y_offset):
        """Render character name, race, class, and level."""
        x_margin = self.hud_x + 20
        
        # Name
        name_text = self.title_font.render(player_char.name, True, (255, 215, 0))
        self.screen.blit(name_text, (x_margin, y_offset))
        y_offset += 35
        
        # Race and Class
        info_text = f"{player_char.race.name} {player_char.cls.name}"
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
    
    def _render_minimap(self, player_char, y_offset):
        """Render minimap showing nearby explored areas."""
        x_margin = self.hud_x + 20
        minimap_size = min(200, self.hud_width - 40)
        visible_adjacent = self._get_visible_adjacent_positions(player_char)
        
        # Title
        map_title = self.stat_font.render("Map", True, (150, 150, 255))
        self.screen.blit(map_title, (x_margin, y_offset))
        y_offset += 28
        
        # Minimap background
        minimap_rect = pygame.Rect(x_margin, y_offset, minimap_size, minimap_size)
        pygame.draw.rect(self.screen, (15, 15, 20), minimap_rect)
        pygame.draw.rect(self.screen, self.border_color, minimap_rect, 2)
        
        # Render nearby tiles
        tile_size = minimap_size // 11  # Show 11x11 grid
        player_x, player_y = player_char.location_x, player_char.location_y
        
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                tile_x = player_x + dx
                tile_y = player_y + dy
                tile = player_char.world_dict.get((tile_x, tile_y, player_char.location_z))
                
                screen_x = x_margin + (dx + 5) * tile_size
                screen_y = y_offset + (dy + 5) * tile_size
                tile_rect = pygame.Rect(screen_x, screen_y, tile_size - 1, tile_size - 1)
                
                if tile:
                    tile_type = type(tile).__name__
                    is_directly_visible = (tile_x, tile_y) in visible_adjacent
                    
                    if dx == 0 and dy == 0:
                        # Player position - draw base tile first, then player marker with arrow
                        if getattr(tile, 'visited', False):
                            if not getattr(tile, 'enter', True):
                                pygame.draw.rect(self.screen, (80, 80, 90), tile_rect)
                            else:
                                pygame.draw.rect(self.screen, (120, 120, 130), tile_rect)
                        
                        # Player marker (yellow)
                        pygame.draw.rect(self.screen, (255, 255, 0), tile_rect)
                        
                        # Draw directional arrow on player position
                        center_x = screen_x + tile_size // 2
                        center_y = screen_y + tile_size // 2
                        arrow_size = tile_size // 3
                        
                        # Determine arrow direction based on facing
                        if player_char.facing == 'north':
                            points = [(center_x, center_y - arrow_size), 
                                     (center_x - arrow_size//2, center_y + arrow_size//2),
                                     (center_x + arrow_size//2, center_y + arrow_size//2)]
                        elif player_char.facing == 'south':
                            points = [(center_x, center_y + arrow_size),
                                     (center_x - arrow_size//2, center_y - arrow_size//2),
                                     (center_x + arrow_size//2, center_y - arrow_size//2)]
                        elif player_char.facing == 'east':
                            points = [(center_x + arrow_size, center_y),
                                     (center_x - arrow_size//2, center_y - arrow_size//2),
                                     (center_x - arrow_size//2, center_y + arrow_size//2)]
                        else:  # west
                            points = [(center_x - arrow_size, center_y),
                                     (center_x + arrow_size//2, center_y - arrow_size//2),
                                     (center_x + arrow_size//2, center_y + arrow_size//2)]
                        
                        pygame.draw.polygon(self.screen, (0, 0, 0), points)
                        
                    elif getattr(tile, 'visited', False) or getattr(tile, 'near', False) or is_directly_visible:
                        # Explored tile (visited/near) or directly visible adjacent tile
                        is_visited = getattr(tile, 'visited', False)
                        is_near = getattr(tile, 'near', False)
                        if tile_type == 'FakeWall':
                            # Keep FakeWall hidden unless actually visited
                            if is_visited:
                                pygame.draw.rect(self.screen, (150, 100, 150), tile_rect)
                            else:
                                pygame.draw.rect(self.screen, (80, 80, 90), tile_rect)
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
                        
                        # Draw icons for special features on visited tiles
                        if 'Chest' in tile_type and not getattr(tile, 'opened', False):
                            # Chest (unopened) - yellow/gold square
                            icon_size = tile_size // 3
                            icon_x = screen_x + (tile_size - icon_size) // 2
                            icon_y = screen_y + (tile_size - icon_size) // 2
                            pygame.draw.rect(self.screen, (255, 215, 0), 
                                           pygame.Rect(icon_x, icon_y, icon_size, icon_size))
                        
                        if 'LockedDoor' in tile_type and not getattr(tile, 'opened', False):
                            # Door (locked) - brown rectangle
                            icon_width = tile_size // 2
                            icon_height = tile_size // 3
                            icon_x = screen_x + (tile_size - icon_width) // 2
                            icon_y = screen_y + (tile_size - icon_height) // 2
                            pygame.draw.rect(self.screen, (139, 69, 19),
                                           pygame.Rect(icon_x, icon_y, icon_width, icon_height))
                        
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
                    
                    elif getattr(tile, 'near', False):
                        pygame.draw.rect(self.screen, (50, 50, 60), tile_rect)
        
        y_offset += minimap_size + 5
        return y_offset

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
            if not self._is_direction_visible_from_tile(current_tile, direction):
                continue

            tile_x = player_x + dx
            tile_y = player_y + dy
            if player_char.world_dict.get((tile_x, tile_y, player_z)) is not None:
                visible.add((tile_x, tile_y))

        return visible

    def _is_direction_visible_from_tile(self, current_tile, direction):
        """Return whether a cardinal direction is visible from the current tile."""
        if not current_tile:
            return True

        blocked = getattr(current_tile, 'blocked', None)
        if blocked and blocked.lower() == direction:
            if hasattr(current_tile, 'open') and getattr(current_tile, 'open', False):
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
