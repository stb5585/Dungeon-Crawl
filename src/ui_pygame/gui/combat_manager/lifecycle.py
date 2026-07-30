"""Lifecycle behavior for the combat manager package."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pygame

from src.core import enemies
from src.core.character import Character
from src.core.classes import ability_mechanics
from src.core.player import Player
import src.ui_pygame.gui.combat_manager as combat_manager
from ..input_guards import release_guard_allows_input
from ..mouse_helpers import hit_index, is_left_click, mouse_position
from .constants import (
    _DISPLAY_TO_ENGINE,
    COMBAT_START_TRANSITION_FRAMES,
    POST_TURN_DELAY_FRAMES,
    VESPERION_FALSE_FINAL_ENEMY_TURNS,
)


if TYPE_CHECKING:
    from src.core.map_tiles import MapTile


class CombatLifecycleMixin:
    def start_combat(self, player_char: Player, enemy: Character, tile: MapTile) -> bool:
        """
        Initiate combat between player and enemy.

        Args:
            player_char: The player character
            enemy: The enemy to fight
            tile: The map tile where combat is occurring

        Returns:
            bool: True if player won, False if player fled/died
        """
        # Store tile for loot drops
        self.current_tile = tile

        # Ensure dungeon background has a valid world dict for rendering
        if not self.player_world_dict and hasattr(player_char, "world_dict"):
            self.player_world_dict = player_char.world_dict

        # Create the core engine (handles initiative, actions, bookkeeping)
        self.engine = combat_manager.BattleEngine(
            player=player_char,
            enemy=enemy,
            tile=tile,
            game=self.game,
            logger=self.logger,
        )

        # Build display-friendly action list from the engine's available actions
        self.available_actions = self._build_display_actions()

        # Initialize combat state
        self.running = True
        self.combat_view.reset_combat_log()
        self.combat_view.add_combat_message(f"Combat started with {enemy.name}!")
        self._combat_background = self._capture_background()
        self._prepare_enemy_combat_assets(enemy)

        # Show initial combat screen with brief transition delay (with animation updates)
        init_clock = pygame.time.Clock()
        for _ in range(COMBAT_START_TRANSITION_FRAMES):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._render_combat_frame(self._selection_frame_player(player_char), enemy, [], -1)
            pygame.display.flip()
            init_clock.tick(60)

        # Determine who goes first (engine handles initiative)
        first, _ = self.engine.start_battle()
        if player_char.encumbered:
            self.combat_view.add_combat_message("You are ENCUMBERED! Enemy strikes first!")

        if first == player_char:
            self.combat_view.add_combat_message(f"{player_char.name} has the initiative!")
        else:
            self.combat_view.add_combat_message(f"{enemy.name} has the initiative!")

        clock = pygame.time.Clock()
        fled = False
        vesperion_false_final = self._is_vesperion_false_final_combat(player_char, enemy)
        vesperion_enemy_turns = 0

        # Main combat loop
        while self.running and self.engine.battle_continues() and not player_char.in_town():
            if self.engine.is_player_turn():
                action_result = self._player_turn(player_char, enemy)
                if action_result == "flee":
                    fled = True
                    break
                elif not action_result:  # Closed combat
                    fled = True
                    break

                # Check if enemy died from special effects (e.g., self-healing that prevents death)
                if not enemy.is_alive():
                    if vesperion_false_final:
                        return self._handle_vesperion_false_final(player_char, enemy)
                    if not getattr(enemy, "tamed_by_player", False):
                        self.combat_view.enemy_dies(enemy)
                    break

                if vesperion_false_final and self._vesperion_false_final_hp_threshold_met(enemy):
                    return self._handle_vesperion_false_final(player_char, enemy)

                # Check for Mad Waitress form change (below 10% health)
                self._check_enemy_form_change(player_char, enemy)
            else:
                # Double-check enemy is still alive before their turn
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break

                enemy_result = self._enemy_turn(player_char, enemy)
                if enemy_result == "flee":
                    fled = True
                    break

                if vesperion_false_final:
                    vesperion_enemy_turns += 1
                    if (
                        not player_char.is_alive()
                        or vesperion_enemy_turns >= VESPERION_FALSE_FINAL_ENEMY_TURNS
                        or self._vesperion_false_final_hp_threshold_met(enemy)
                    ):
                        return self._handle_vesperion_false_final(player_char, enemy)

                # Check if player died
                if not player_char.is_alive():
                    break

                # Prevent Mad Waitress from dying before her forced transition
                self._preserve_waitress_for_transition(enemy)
                self._check_enemy_form_change(player_char, enemy)

                # Check if enemy died (e.g., from self-damaging skills like Widow's Wail)
                if not enemy.is_alive():
                    if vesperion_false_final:
                        return self._handle_vesperion_false_final(player_char, enemy)
                    self.combat_view.enemy_dies(enemy)
                    break

            # Advance turn: post-turn processing + swap
            self._post_turn_processing(player_char, enemy)
            if vesperion_false_final and (
                not player_char.is_alive()
                or not enemy.is_alive()
                or self._vesperion_false_final_hp_threshold_met(enemy)
            ):
                return self._handle_vesperion_false_final(player_char, enemy)
            self.engine.swap_turns()
            self._refresh_combat_background(player_char, enemy)

            # Refresh available actions for next turn
            self.available_actions = self._build_display_actions()

            # Small delay between turns (with animation updates)
            for _ in range(POST_TURN_DELAY_FRAMES):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    self._handle_combat_log_scroll_event(event)
                self._render_combat_frame(player_char, enemy, [], -1)
                pygame.display.flip()
                clock.tick(60)

        # Combat ended - show result
        return self._handle_combat_end(player_char, enemy, fled)

    def _prepare_enemy_combat_assets(self, enemy: Character) -> None:
        """Warm the current enemy's combat sprites before the first combat frame."""
        prepare = getattr(self.combat_view, "prepare_enemy_assets", None)
        if callable(prepare):
            try:
                prepare(enemy)
            except Exception:
                pass

    def _build_display_actions(self) -> list[str]:
        """Build the pygame display-friendly action list from the engine's available actions."""
        raw_actions = self.engine.available_actions
        action_names = []
        for action in raw_actions:
            if isinstance(action, dict):
                action_name = action.get('name', str(action))
            else:
                action_name = str(action)
            # Rename for display
            action_name = action_name.replace("Cast Spell", "Spells") \
                                    .replace("Use Skill", "Skills") \
                                    .replace("Use Item", "Items")
            action_names.append(action_name)

        # Deduplicate while preserving order
        deduped = []
        seen = set()
        for name in action_names:
            normalized = name.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(normalized)

        # Add Defend if not already present
        if "Defend" not in deduped and "Attack" in deduped:
            deduped.insert(1, "Defend")

        actor = getattr(self.engine, "attacker", None) or getattr(self.engine, "player", None)

        target = getattr(self.engine, "defender", None)
        if actor is not None and "Skills" in deduped:
            has_resolve = bool(self._available_skill_names(actor, target, resolve=True))
            has_standard_skills = bool(self._available_skill_names(actor, target, resolve=False))
            if has_resolve and "Resolve" not in deduped:
                skill_index = deduped.index("Skills")
                deduped.insert(skill_index, "Resolve")
            if has_resolve and not has_standard_skills and "Skills" in deduped:
                deduped.remove("Skills")

        # Add Pickup Weapon if the active actor is disarmed
        is_disarmed = getattr(actor, "is_disarmed", None)
        if actor is not None and callable(is_disarmed) and is_disarmed() and "Pickup Weapon" not in deduped:
            idx = 2 if "Defend" in deduped else 1
            deduped.insert(idx, "Pickup Weapon")

        if self._debug_mode_enabled() and "Auto Kill" not in deduped:
            deduped.append("Auto Kill")

        return deduped

    def _refresh_display_actions(self) -> None:
        """Refresh the visible combat action list when turn-start effects change availability."""
        try:
            self.available_actions = self._build_display_actions()
        except AttributeError:
            return

    def _post_turn_processing(self, player_char: Player, enemy: Character) -> None:
        """Handle engine post-turn + display any messages."""
        visual_before = (getattr(enemy, "name", None), getattr(enemy, "picture", None))
        post = self.engine.post_turn()
        visual_after = (getattr(enemy, "name", None), getattr(enemy, "picture", None))
        added_message = False
        for msg in post.messages:
            if msg:
                for line in msg.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
                        added_message = True
        if added_message:
            self._flush_result_frame(player_char, enemy)
        if visual_after != visual_before:
            self._play_enemy_visual_transition(player_char, enemy, visual_before, visual_after)

    def _flush_result_frame(self, player_char, enemy) -> None:
        """Draw result log text before any impact animation or turn transition starts."""
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        try:
            pygame.event.pump()
        except pygame.error:
            pass
        pygame.time.Clock().tick(60)

    def _play_enemy_visual_transition(
        self,
        player_char: Player,
        enemy: Character,
        visual_before: tuple[object, object],
        visual_after: tuple[object, object],
    ) -> None:
        """Briefly alternate old/new enemy visuals when a form changes."""
        before_picture = visual_before[1]
        after_picture = visual_after[1]
        if not before_picture or not after_picture or before_picture == after_picture:
            self.combat_view.reload_enemy_sprite(enemy)
            return

        original_offset = getattr(self.combat_view, "enemy_visual_offset", (0, 0))
        frames = [
            (before_picture, -8),
            (after_picture, 8),
            (before_picture, -6),
            (after_picture, 6),
            (before_picture, -3),
            (after_picture, 0),
        ]
        clock = pygame.time.Clock()
        try:
            for picture, offset_x in frames:
                enemy.picture = picture
                self.combat_view.reload_enemy_sprite(enemy)
                self.combat_view.enemy_visual_offset = (offset_x, 0)
                for _ in range(5):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit(0)
                        self._handle_combat_log_scroll_event(event)
                    self._render_combat_frame(player_char, enemy, [], -1)
                    pygame.display.flip()
                    clock.tick(60)
        finally:
            enemy.picture = after_picture
            self.combat_view.enemy_visual_offset = original_offset
            self.combat_view.reload_enemy_sprite(enemy)

    def _player_turn(self, player_char, enemy):
        """
        Handle player's turn with action selection.

        Returns:
            str/bool: "flee" if fled, False if cancelled, True if action taken
        """
        # Pre-turn: process status effects and check if player can act
        pre = self.engine.pre_turn()
        if pre.effects_text:
            for line in pre.effects_text.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)
            self._flush_result_frame(player_char, enemy)

        # If the player died from effects (poison, DOT, bleed), end turn immediately
        if pre.died_from_effects:
            return True

        if not pre.can_act:
            self.combat_view.add_combat_message(pre.inactive_reason.strip())
            self._flush_result_frame(player_char, enemy)
            return True  # Turn skipped

        self._refresh_display_actions()

        # Check for forced actions (berserk, charging, jump)
        forced = self.engine.get_forced_action()
        if forced:
            if forced.action == "Cancelled":
                for line in forced.cancel_message.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
                self._flush_result_frame(player_char, enemy)
                return True

            if forced.action == "Attack":
                actor_name = getattr(getattr(self.engine, "attacker", None), "name", player_char.name)
                self.combat_view.add_combat_message(f"{actor_name} is BERSERKED and attacks wildly!")

            # Execute the forced action via engine
            enemy_hp_before = enemy.health.current
            result = self.engine.execute_action(forced.action, choice=forced.choice)

            for line in result.message.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)

            self._flush_result_frame(player_char, enemy)

            # Damage flash for attack/skill hits
            damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
            if damage_to_enemy > 0:
                self.combat_view.enemy_take_damage(enemy)
                self._show_combat_damage_effect("enemy", forced.action, forced.choice, result.message, damage_to_enemy)
                self._flush_result_frame(player_char, enemy)

            self._preserve_waitress_for_transition(enemy)

            if result.fled:
                return "flee"
            return True

        # Get available actions
        actions = self.available_actions
        selected_action = 0
        input_armed = self._clear_pending_input()

        action_taken = False

        while not action_taken:
            # Render combat scene
            self._render_combat_frame(player_char, enemy, actions, selected_action)

            # Handle input
            input_armed = release_guard_allows_input(True, input_armed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                input_armed = self._arm_guarded_input(event, input_armed)
                if event.type == pygame.KEYDOWN and not input_armed:
                    continue

                if self._handle_combat_log_scroll_event(event):
                    continue

                elif event.type == pygame.KEYDOWN:
                    # Grid navigation: 3 actions per row
                    actions_per_row = 3
                    current_row = selected_action // actions_per_row
                    current_col = selected_action % actions_per_row
                    num_rows = (len(actions) + actions_per_row - 1) // actions_per_row

                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        # Move up one row
                        if current_row > 0:
                            selected_action -= actions_per_row
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        # Move down one row
                        new_action = selected_action + actions_per_row
                        if new_action < len(actions):
                            selected_action = new_action
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        # Move left one column
                        if current_col > 0:
                            selected_action -= 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        # Move right one column
                        if current_col < actions_per_row - 1 and selected_action + 1 < len(actions):
                            selected_action += 1
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Execute selected action
                        action_result = self._execute_action(
                            actions[selected_action],
                            player_char,
                            enemy
                        )
                        if action_result == "flee":
                            return "flee"
                        elif action_result == "continue_turn":
                            self._refresh_display_actions()
                            actions = self.available_actions
                            selected_action = 0
                            input_armed = self._clear_pending_input()
                            break
                        elif action_result is not None:
                            action_taken = True
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                        # Number keys for quick selection
                        num = event.key - pygame.K_1
                        if num < len(actions):
                            action_result = self._execute_action(
                                actions[num],
                                player_char,
                                enemy
                            )
                            if action_result == "flee":
                                return "flee"
                            elif action_result == "continue_turn":
                                self._refresh_display_actions()
                                actions = self.available_actions
                                selected_action = 0
                                input_armed = self._clear_pending_input()
                                break
                            elif action_result is not None:
                                action_taken = True
                elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                    hovered = hit_index(self._combat_action_rects(actions), mouse_position(event))
                    if hovered is None:
                        continue
                    selected_action = hovered
                    if not is_left_click(event) or not input_armed:
                        continue
                    action_result = self._execute_action(
                        actions[selected_action],
                        player_char,
                        enemy,
                    )
                    if action_result == "flee":
                        return "flee"
                    elif action_result == "continue_turn":
                        self._refresh_display_actions()
                        actions = self.available_actions
                        selected_action = 0
                        input_armed = self._clear_pending_input()
                        break
                    elif action_result is not None:
                        action_taken = True

            pygame.display.flip()

        # Companion / familiar turn
        companion_msg = self.engine.companion_turn()
        if companion_msg:
            for line in companion_msg.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)

        return True

    def _check_enemy_form_change(self, player_char, enemy):
        """
        Check if Mad Waitress should change form/state when health drops below 10%.
        When the transition happens, she becomes sane, changes sprite back to waitress.png,
        and attacks herself once before dying.
        """
        # Only applies to Mad Waitress (NightHag2)
        if not isinstance(enemy, enemies.NightHag2):
            return

        # Check if already transitioned
        if getattr(enemy, '_form_changed', False):
            return

        # Check health threshold (below 10%)
        health_pct = enemy.health.current / enemy.health.max
        if health_pct >= 0.1:
            return

        # Perform transition
        enemy._form_changed = True

        # Collect transition messages to display in popup
        transition_messages = [
            "The Mad Waitress momentarily comes to her senses...",
            "This visible form change reveals the waitress beneath the hag's shape.",
            "Her eyes clear. She sees what she has become.",
            "",
            "Recognizing the horror of her actions,",
            "she takes her own life, finally finding peace with Joffrey..."
        ]

        # Change name and sprite back to normal Waitress
        enemy.name = "Waitress"
        self.combat_view.reload_enemy_sprite(enemy)

        # Waitress takes her own life - deal lethal damage
        damage = enemy.health.current
        enemy.health.current = 0

        # Show popup with the wail/transition narrative
        from ..confirmation_popup import ConfirmationPopup
        popup_text = "\n".join(transition_messages)
        popup = ConfirmationPopup(self.presenter, popup_text, show_buttons=False)
        popup.show(flush_events=True, require_key_release=True)

        # Show combat log messages for the self-attack
        self.combat_view.add_combat_message(
            "The Mad Waitress visibly changes form without changing her true identity."
        )
        self.combat_view.add_combat_message(
            f"{enemy.name} turns her weapon on herself in despair!"
        )
        self.combat_view.add_combat_message(
            f"{enemy.name} takes {damage} damage from the attack!"
        )

        # Enemy is now dead
        self.combat_view.enemy_dies(enemy)

    def _preserve_waitress_for_transition(self, enemy) -> None:
        """Prevent killing the Mad Waitress before her transition triggers."""
        if not isinstance(enemy, enemies.NightHag2):
            return
        if getattr(enemy, '_form_changed', False):
            return
        if enemy.health.current <= 0:
            enemy.health.current = 1

    def _execute_action(self, action, player_char, enemy):
        """Execute a player action by delegating to the engine."""
        actor = getattr(self.engine, "attacker", None) or player_char
        if action == "Auto Kill":
            if not self._debug_mode_enabled():
                self.combat_view.add_combat_message("Auto Kill is only available in debug mode.")
                return None
            enemy_hp_before = enemy.health.current
            enemy.health.current = 0
            damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
            self.combat_view.add_combat_message(f"Debug: {enemy.name} defeated.")
            self.combat_view.enemy_take_damage(enemy)
            self._show_combat_damage_effect("enemy", "Attack", None, "", damage_to_enemy)
            return "action_taken"

        # Map display name back to engine name
        engine_action = _DISPLAY_TO_ENGINE.get(action, action)
        support_mode = action == "Support"

        # Sub-menu actions need a selection UI first
        choice = None

        if support_mode:
            support = self._select_summoner_support_action(player_char, enemy)
            if not support:
                return None
            action, engine_action, choice = support
            actor = player_char

        if action == "Items":
            selected_item = self._select_item(actor, enemy, support_only=support_mode)
            if not selected_item:
                return None  # Cancelled
            choice = selected_item.name

        elif action == "Spells":
            if actor.abilities_suppressed():
                reason = "the anti-magic field" if getattr(actor, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{actor.name} cannot cast spells because of {reason}!"
                )
                return None
            selected_spell = self._select_spell(actor, enemy)
            if not selected_spell:
                return None
            choice = selected_spell

        elif action == "Runic Boost":
            if player_char.abilities_suppressed():
                reason = "the anti-magic field" if getattr(player_char, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{player_char.name} cannot cast spells because of {reason}!"
                )
                return None
            selected_spell = self._select_runic_boost_spell(player_char, enemy)
            if not selected_spell:
                return None
            choice = selected_spell

        elif action == "Steal As Well":
            selected_spell = self._select_steal_as_well_spell(player_char, enemy)
            if not selected_spell:
                return None
            choice = selected_spell

        elif action == "Companion":
            if player_char.abilities_suppressed():
                reason = "the anti-magic field" if getattr(player_char, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{player_char.name} cannot command their companion because of {reason}!"
                )
                return None
            selected_command = self._select_companion_command(player_char, enemy)
            if not selected_command:
                return None
            choice = selected_command

        elif action == "Skills":
            if actor.abilities_suppressed():
                reason = "the anti-magic field" if getattr(actor, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{actor.name} cannot use skills because of {reason}!"
                )
                return None
            allowed_skill_names = None
            if support_mode and self.engine is not None:
                allowed_skill_names = self.engine.summoner_support_skill_names()
            if allowed_skill_names is None:
                selected_skill = self._select_skill(actor, enemy)
            else:
                selected_skill = self._select_skill(actor, enemy, allowed_names=allowed_skill_names)
            if not selected_skill:
                return None
            choice = selected_skill
            if selected_skill == "Call Contract":
                intent = self._select_contract_intent(player_char, enemy)
                if not intent:
                    return None
                skill_obj = actor.spellbook.get('Skills', {}).get("Call Contract")
                if skill_obj:
                    skill_obj.pending_intent = intent

        elif action == "Resolve":
            selected_skill = self._select_resolve_ability(actor, enemy)
            if not selected_skill:
                return None
            choice = selected_skill

        elif action == "Summon":
            if player_char.abilities_suppressed():
                reason = "the anti-magic field" if getattr(player_char, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{player_char.name} cannot summon because of {reason}!"
                )
                return None
            selected_summon = self._select_summon(player_char, enemy)
            if not selected_summon:
                return None
            choice = selected_summon

        elif action == "Pickup Weapon":
            is_disarmed = getattr(actor, "is_disarmed", None)
            if not callable(is_disarmed) or not is_disarmed():
                self.combat_view.add_combat_message("Not disarmed!")
                return None

        if choice is not None:
            self._render_combat_frame(self._selection_frame_player(player_char), enemy, [], -1)
            pygame.display.flip()

        # Record HP before execution for damage flash
        enemy_hp_before = enemy.health.current
        player_hp_before = player_char.health.current
        actor_hp_before = getattr(getattr(actor, "health", None), "current", 0)
        enemy_name_before = enemy.name

        # Delegate to engine (handles attack rolls, spell casts, skill use, etc.)
        slot_cb = None
        if action in {"Skills", "Resolve"} and choice:
            skill_obj = actor.spellbook.get('Skills', {}).get(choice)
            if skill_obj and skill_obj.name == "Slot Machine":
                slot_cb = lambda _u, _t: self._show_slot_machine_reveal(actor, enemy)

        if support_mode:
            result = self.engine.execute_summoner_support_action(engine_action, choice=choice, slot_machine_callback=slot_cb)
        else:
            result = self.engine.execute_action(engine_action, choice=choice, slot_machine_callback=slot_cb)

        damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
        favored_msg = ability_mechanics.consume_favored_enemy_bonus_message(player_char)
        if damage_to_enemy > 0:
            for line in favored_msg.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)

        # Display result messages
        for line in result.message.strip().split('\n'):
            if line.strip():
                self.combat_view.add_combat_message(line)

        action_fled = result.fled or bool(getattr(self.engine, "flee", False))
        if engine_action == "Use Skill" and choice == "Smoke Screen" and action_fled:
            self._play_smoke_screen_visual(player_char, enemy, "player")
        else:
            self._flush_result_frame(player_char, enemy)

        # Show damage flash for enemy damage
        showed_damage_effect = False
        tamed_result = bool(getattr(enemy, "tamed_by_player", False))
        if damage_to_enemy > 0 and not tamed_result:
            self.combat_view.enemy_take_damage(enemy)
            self._show_combat_damage_effect("enemy", action, choice, result.message, damage_to_enemy)
            showed_damage_effect = True
        else:
            if not tamed_result:
                self._show_combat_heal_text("enemy", max(0, enemy.health.current - enemy_hp_before))

        # Show damage flash for player damage (from reflected/self-damage skills)
        active_hp_after = getattr(getattr(actor, "health", None), "current", actor_hp_before)
        damage_to_player = max(0, player_hp_before - player_char.health.current)
        if actor is not player_char:
            damage_to_player = max(0, actor_hp_before - active_hp_after)
        if damage_to_player > 0:
            self._show_combat_damage_effect("player", action, choice, result.message, damage_to_player)
            showed_damage_effect = True
        else:
            heal_amount = max(0, player_char.health.current - player_hp_before)
            if actor is not player_char:
                heal_amount = max(0, active_hp_after - actor_hp_before)
            self._show_combat_heal_text("player", heal_amount)

        if showed_damage_effect:
            self._flush_result_frame(player_char, enemy)

        # Check if enemy shapeshifted (name changed)
        if enemy.name != enemy_name_before:
            self.combat_view.reload_enemy_sprite(enemy)

        self._preserve_waitress_for_transition(enemy)

        if action_fled:
            return "flee"
        if getattr(result, "summon_started", False):
            self._refresh_display_actions()
            return "continue_turn"
        return "action_taken"
