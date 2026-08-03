"""Overlay behavior for the combat view package."""

from __future__ import annotations

import pygame

import src.ui_pygame.gui.combat_view as combat_view


class CombatOverlayMixin:
    @staticmethod
    def _approximate_health_label(enemy) -> str:
        """Return a coarse health band for hidden-information cards."""
        maximum = max(1, int(getattr(enemy.health, "max", 1) or 1))
        ratio = max(0.0, float(enemy.health.current) / maximum)
        if ratio > (2 / 3):
            return "Healthy"
        if ratio >= (1 / 3):
            return "Wounded"
        return "Critical"

    def render_encounter_in_dungeon(
        self,
        player_char,
        encounter,
        *,
        focus_target_id: str,
        details_by_id: dict[str, bool],
    ) -> None:
        """Render a two-member encounter as compact independent target cards."""
        if len(encounter.members) == 1:
            enemy = encounter.primary_enemy
            self._enemy_card_rects = {}
            self._enemy_target_rects = {}
            self.render_enemy_in_dungeon(
                player_char,
                enemy,
                show_enemy_details=details_by_id.get(
                    encounter.primary_member.combatant_id,
                    False,
                ),
            )
            return

        self.update_animations()
        view_width = int(self.screen_width * 0.65)
        gap = 18
        margin = 18
        top = 178
        bottom = self.screen_height - 158
        card_height = max(250, bottom - top)
        card_width = max(230, (view_width - (margin * 2) - gap) // 2)
        self._enemy_card_rects = {}
        self._enemy_target_rects = {}

        for index, member in enumerate(encounter.members):
            enemy = member.enemy
            card = pygame.Rect(
                margin + index * (card_width + gap),
                top,
                card_width,
                card_height,
            )
            self._enemy_card_rects[member.combatant_id] = card
            focused = member.combatant_id == focus_target_id
            living = member.is_living_hostile
            fill = (22, 22, 28, 225 if living else 170)
            panel = pygame.Surface(card.size, pygame.SRCALPHA)
            panel.fill(fill)
            self.screen.blit(panel, card.topleft)
            border = self.colors["panel_accent"] if focused else (92, 92, 104)
            pygame.draw.rect(
                self.screen,
                border,
                card,
                4 if focused else 2,
                border_radius=8,
            )

            title_font = pygame.font.Font(None, 28)
            body_font = pygame.font.Font(None, 20)
            label = self._truncate_text(
                title_font,
                member.display_label,
                card.width - 24,
            )
            title = title_font.render(label, True, self.colors["text"])
            self.screen.blit(
                title,
                title.get_rect(center=(card.centerx, card.top + 24)),
            )
            if focused:
                marker = body_font.render("TARGET", True, self.colors["panel_accent"])
                self.screen.blit(
                    marker,
                    marker.get_rect(center=(card.centerx, card.top + 48)),
                )

            has_sight = bool(details_by_id.get(member.combatant_id, False))
            sprite_area = pygame.Rect(
                card.left + 14,
                card.top + 58,
                card.width - 28,
                max(110, card.height - 142),
            )
            animator = self._get_sprite_animator(enemy)
            sprite = None
            if has_sight:
                try:
                    sprite = self.enemy_combat_sprite_manager.get_scaled_sprite(
                        enemy,
                        sprite_area.size,
                    )
                except Exception:
                    sprite = None
            if sprite is not None:
                if animator.damage_flash > 0:
                    sprite = animator.apply_tint(
                        sprite,
                        (255, 100, 100),
                        animator.damage_flash,
                    )
                if not living:
                    sprite = sprite.copy()
                    sprite.set_alpha(85)
                sprite_rect = sprite.get_rect(center=sprite_area.center)
                self.screen.blit(sprite, sprite_rect)
                self._enemy_target_rects[member.combatant_id] = sprite_rect
            else:
                silhouette = pygame.Rect(
                    sprite_area.centerx - 42,
                    sprite_area.centery - 62,
                    84,
                    124,
                )
                pygame.draw.ellipse(
                    self.screen,
                    (42, 42, 50) if living else (30, 30, 34),
                    silhouette,
                )
                self._enemy_target_rects[member.combatant_id] = silhouette

            info_y = card.bottom - 68
            if member.resolution is not None:
                resolution_labels = {
                    "defeated": "Defeated",
                    "mercy": "Spared",
                    "tamed": "Tamed",
                    "ejected": "Ejected",
                    "escaped": "Escaped",
                }
                text = resolution_labels.get(
                    member.resolution.value,
                    member.resolution.value.title(),
                )
            elif has_sight:
                text = f"HP {enemy.health.current}/{enemy.health.max}"
            else:
                text = self._approximate_health_label(enemy)
            info = body_font.render(text, True, self.colors["text"])
            self.screen.blit(
                info,
                info.get_rect(center=(card.centerx, info_y)),
            )
            if has_sight and living:
                icons = self._collect_status_icons(enemy)
                if icons:
                    self._render_status_icons(
                        icons,
                        card.left + 12,
                        card.bottom - 38,
                        max_width=card.width - 24,
                        max_rows=1,
                    )

        self._last_enemy_target_rect = self._enemy_target_rects.get(
            focus_target_id,
            self._last_enemy_target_rect,
        ).copy()
        self._render_active_impact_effects()
        self._render_floating_texts()

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
        elif self._enemy_hidden_by_invisibility(enemy, has_sight):
            enemy_size = 0
            self._last_enemy_target_rect = pygame.Rect(center_x, center_y, 1, 1)
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

    def render_combat_overlay(
        self,
        player_char,
        enemy,
        actions,
        selected_action,
        current_turn=None,
        show_enemy_details=None,
        current_actor=None,
    ):
        """Render combat UI overlay (action menu and combat log) over the dungeon view."""
        self._set_combat_log_actors(player_char, enemy)
        self._last_player_target_rect = pygame.Rect(
            26,
            self.screen_height - 312,
            max(180, int(self.screen_width * 0.24)),
            130,
        )
        self._render_player_danger_vignette(player_char)
        self._render_turn_indicator(
            player_char,
            enemy,
            current_turn=current_turn,
            overlay=True,
            current_actor=current_actor,
        )
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

    def _render_turn_indicator(self, player_char, enemy, current_turn=None, overlay=False, current_actor=None):
        """Render a compact banner showing whose turn is active."""
        if current_turn not in {"player", "enemy"}:
            return
        turn_actor = current_actor if current_actor is not None else (player_char if current_turn == "player" else enemy)
        incapacitated = getattr(turn_actor, "incapacitated", None)
        if callable(incapacitated) and incapacitated():
            return

        view_width = int(self.screen_width * 0.65) if overlay else self.combat_width
        token_size = 46
        text_left = token_size + 26
        min_height = 64
        label = "Your Turn" if current_turn == "player" else "Enemy Turn"
        sublabel = getattr(turn_actor, "name", "Player" if current_turn == "player" else "Enemy")
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
                if turn_actor is player_char:
                    token = self.player_token_manager.get_scaled_token(player_char, (token_size, token_size))
                else:
                    token = combat_view.get_companion_art_manager().get_scaled_sprite(turn_actor, (token_size, token_size))
            except Exception as exc:  # pragma: no cover - defensive runtime fallback for external art failures
                print(f"Failed to render player-side token for {getattr(turn_actor, 'name', turn_actor)}: {exc}")
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
        if current_turn == "player" and turn_actor is not player_char:
            icons = self._collect_status_icons(turn_actor)
            if icons:
                self._render_status_icons(icons, rect.left + text_left, rect.bottom + 4, max_width=width - text_left - 10, max_rows=1)

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
