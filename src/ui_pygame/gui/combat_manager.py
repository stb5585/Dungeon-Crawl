"""
Combat Manager for Pygame GUI.
Handles combat flow with GUI rendering (doesn't use curses BattleManager).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import random
import re
import sys

import pygame

from src.core import enemies
from src.core.character import Character
from src.core.combat.battle_logger import BattleLogger
from src.core.player import Player
from .combat_view import CombatView
from .level_up import LevelUpScreen

if TYPE_CHECKING:
    from src.core.map_tiles import MapTile
    from src.ui_pygame.game import PygameGame
    from src.ui_pygame.gui.dungeon_hud import DungeonHUD
    from src.ui_pygame.presentation.pygame_presenter import PygamePresenter


class GUICombatManager:
    """Manages combat with pygame GUI rendering."""
    
    def __init__(self, presenter: PygamePresenter, hud: DungeonHUD, game: PygameGame):
        self.presenter = presenter
        self.screen = presenter.screen
        self.hud = hud
        self.game = game
        self.combat_view = CombatView(self.screen, presenter)
        self.level_up_screen = LevelUpScreen(self.screen, presenter)
        self.logger = BattleLogger()
        self.running = False
        # References to dungeon rendering (set by dungeon_manager)
        self.dungeon_renderer = None
        self.player_world_dict = None
        self._combat_background = None
        self.available_actions = []
        # Track charging abilities across turns
        self.charging_ability = None  # (ability_name, skill_obj) tuple when charging
    
    def _result_to_message(self, result):
        """Convert a combat result (string or CombatResult object) to a message string."""
        if isinstance(result, str):
            return result
        
        # Handle CombatResult object
        from src.core.combat.combat_result import CombatResult
        if isinstance(result, CombatResult):
            # Build a message from the CombatResult
            msg_parts = []
            
            if result.action:
                msg_parts.append(result.action)
            
            if result.damage and result.target:
                msg_parts.append(f"{result.target.name} takes {result.damage} damage!")
            
            if result.healing and result.target:
                msg_parts.append(f"{result.target.name} heals {result.healing} HP!")
            
            if result.dodge:
                msg_parts.append(f"{result.target.name if result.target else 'Target'} dodges!")
            
            if result.block:
                msg_parts.append(f"{result.target.name if result.target else 'Target'} blocks!")
            
            return " ".join(msg_parts) if msg_parts else "Action performed."
        
        # Fallback for unknown types
        return str(result)

    def _capture_background(self):
        if hasattr(self.presenter, "get_background_surface"):
            try:
                surface = self.presenter.get_background_surface()
                if surface is not None:
                    return surface
            except Exception:
                pass
        return self.screen.copy()

    def _handle_combat_log_scroll_event(self, event) -> bool:
        """Handle combat-log scrolling input. Returns True when handled."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                self.combat_view.scroll_log(-1)
                return True
            if event.key == pygame.K_PAGEDOWN:
                self.combat_view.scroll_log(1)
                return True
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.combat_view.scroll_log(-1)
            elif event.y < 0:
                self.combat_view.scroll_log(1)
            return True
        return False

    def _show_slot_machine_reveal(self, user: Character, target: Character) -> str:
        """Animate a Slot Machine spin popup and reveal digits left-to-right."""
        digits = [str(random.randint(0, 9)) for _ in range(3)]
        clock = pygame.time.Clock()

        def draw_overlay(revealed_count: int) -> None:
            self._render_combat_frame(user, target, [], -1)

            overlay = pygame.Surface((self.combat_view.combat_width, self.combat_view.combat_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            self.screen.blit(overlay, (0, 0))

            popup_width = min(420, self.combat_view.combat_width - 40)
            popup_height = 170
            popup_x = (self.combat_view.combat_width - popup_width) // 2
            popup_y = (self.combat_view.combat_height - popup_height) // 2
            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

            pygame.draw.rect(self.screen, (26, 26, 34), popup_rect)
            pygame.draw.rect(self.screen, (200, 200, 220), popup_rect, 2)

            title_font = pygame.font.Font(None, 42)
            value_font = pygame.font.Font(None, 64)
            subtitle_font = pygame.font.Font(None, 26)

            title_text = title_font.render("Slot Machine", True, (235, 215, 80))
            title_rect = title_text.get_rect(center=(popup_rect.centerx, popup_rect.top + 34))
            self.screen.blit(title_text, title_rect)

            slots = [digits[i] if i < revealed_count else "?" for i in range(3)]
            slot_text = value_font.render("  ".join(slots), True, (255, 255, 255))
            slot_rect = slot_text.get_rect(center=(popup_rect.centerx, popup_rect.centery + 8))
            self.screen.blit(slot_text, slot_rect)

            subtitle = subtitle_font.render("Reels spinning...", True, (170, 170, 190))
            subtitle_rect = subtitle.get_rect(center=(popup_rect.centerx, popup_rect.bottom - 26))
            self.screen.blit(subtitle, subtitle_rect)

            pygame.display.flip()

        for reveal_idx in range(1, 4):
            frames = 10
            for _ in range(frames):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                draw_overlay(reveal_idx)
                clock.tick(30)

        final_frames = 12
        for _ in range(final_frames):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
            draw_overlay(3)
            clock.tick(30)

        return "".join(digits)
        
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
        
        # Determine available actions
        if hasattr(tile, 'available_actions'):
            available_actions = tile.available_actions(player_char)
            # Extract action names and update old ones to new ones
            action_names = []
            for action in available_actions:
                # Handle both dict actions and string actions
                if isinstance(action, dict):
                    action_name = action.get('name', str(action))
                else:
                    action_name = str(action)
                # Update old action names to new ones
                action_name = action_name.replace("Cast Spell", "Spells") \
                                        .replace("Use Skill", "Skills") \
                                        .replace("Use Item", "Items")
                action_names.append(action_name)
            available_actions = action_names
        else:
            available_actions = ["Attack", "Flee"]

        # Remove duplicate actions while preserving order.
        deduped_actions = []
        seen_actions = set()
        for action_name in available_actions:
            normalized_action = str(action_name).strip()
            if not normalized_action or normalized_action in seen_actions:
                continue
            seen_actions.add(normalized_action)
            deduped_actions.append(normalized_action)
        available_actions = deduped_actions

        # Add Defend option to combat actions
        if "Defend" not in available_actions and "Attack" in available_actions:
            available_actions.insert(1, "Defend")
        
        # Add Pickup Weapon option if player is disarmed
        if player_char.is_disarmed() and "Pickup Weapon" not in available_actions:
            available_actions.insert(2 if "Defend" in available_actions else 1, "Pickup Weapon")

        self.available_actions = available_actions
        
        # Initialize combat state
        self.running = True
        self.combat_view.reset_combat_log()
        self.combat_view.add_combat_message(f"Combat started with {enemy.name}!")
        
        # Initialize combat state
        self.running = True
        self.combat_view.reset_combat_log()
        self.combat_view.add_combat_message(f"Combat started with {enemy.name}!")
        self._combat_background = self._capture_background()
        
        # Initialize battle logger
        boss = "Boss" in str(tile)
        player_initiative = True
        
        # Show initial combat screen with brief transition delay (with animation updates)
        init_clock = pygame.time.Clock()
        for _ in range(48):  # 800ms at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            init_clock.tick(60)
        
        # Determine who goes first (using speed + luck modifiers)
        # Encumbered player always loses initiative
        if player_char.encumbered:
            first = enemy
            player_initiative = False
            self.combat_view.add_combat_message("You are ENCUMBERED! Enemy strikes first!")
        else:
            p_chance = player_char.check_mod("speed", enemy=enemy) + \
                       player_char.check_mod('luck', enemy=enemy, luck_factor=10)
            e_chance = enemy.check_mod("speed", enemy=player_char) + \
                       enemy.check_mod('luck', enemy=player_char, luck_factor=10)
            
            total_chance = p_chance + e_chance
            if total_chance > 0:
                chance_list = [p_chance / total_chance, e_chance / total_chance]
                import random
                first = random.choices([player_char, enemy], chance_list)[0]
            else:
                # Fallback to simple dex comparison
                first = player_char if player_char.stats.dex >= enemy.stats.dex else enemy
            
            player_initiative = (first == player_char)
        
        # Start logging battle
        self.logger.start_battle(player_char, enemy, player_initiative, boss)
        
        if first == player_char:
            attacker, defender = player_char, enemy
            self.combat_view.add_combat_message(f"{player_char.name} has the initiative!")
        else:
            attacker, defender = enemy, player_char
            self.combat_view.add_combat_message(f"{enemy.name} has the initiative!")
        
        clock = pygame.time.Clock()
        fled = False
        
        # Main combat loop
        while self.running and player_char.is_alive() and enemy.is_alive() and not fled and not player_char.in_town():
            # Player turn
            if attacker == player_char:
                action_result = self._player_turn(player_char, enemy, available_actions)
                if action_result == "flee":
                    fled = True
                    break
                elif not action_result:  # Closed combat
                    fled = True
                    break
                
                # Trigger special effects if enemy health drops below threshold (while still alive)
                self._trigger_enemy_special_effects(player_char, enemy)
                
                # Check if enemy died from special effects (e.g., self-healing that prevents death)
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break
                
                # Check for Mad Waitress form change (below 10% health)
                self._check_enemy_form_change(player_char, enemy)
                
                # Switch to enemy turn
                attacker, defender = enemy, player_char
            
            # Enemy turn
            else:
                # Double-check enemy is still alive before their turn
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break
                    
                enemy_result = self._enemy_turn(player_char, enemy)
                if enemy_result == "flee":
                    fled = True
                    break
                
                # Check if player died
                if not player_char.is_alive():
                    break

                # Prevent Mad Waitress from dying before her forced transition,
                # including self-inflicted lethal damage from Widow's Wail.
                self._preserve_waitress_for_transition(enemy)
                self._check_enemy_form_change(player_char, enemy)
                
                # Check if enemy died (e.g., from self-damaging skills like Widow's Wail)
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break
                
                # Switch to player turn
                attacker, _ = player_char, enemy
            
            # Advance turn counter in logger
            self._refresh_combat_background(player_char, enemy)
            self.logger.next_turn()
            
            # Small delay between turns (with animation updates)
            for _ in range(18):  # 300ms at 60fps
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
    
    def _player_turn(self, player_char, enemy, available_actions):
        """
        Handle player's turn with action selection.
        
        Returns:
            str/bool: "flee" if fled, False if cancelled, True if action taken
        """
        # Check if a charging ability is active (e.g., Charge, Minotaur's Charge)
        if self.charging_ability:
            ability_name, skill_obj = self.charging_ability
            # Continue the charge
            result = skill_obj.use(player_char, target=enemy)
            
            # Display result
            if result:
                for line in result.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
            
            # Check if charging is complete
            if not getattr(skill_obj, 'charging', False):
                self.charging_ability = None
            
            # Log skill usage
            self.logger.log_event(
                event_type="skill",
                actor=player_char,
                target=enemy,
                action=f"Charging {ability_name}",
                outcome="Charging"
            )
            return True
        
        # Check if Jump is active (charging)
        if player_char.class_effects.get("Jump") and player_char.class_effects["Jump"].active:
            # Automatically execute Jump
            jump_skill = None
            for skill_name in player_char.spellbook.get('Skills', {}):
                if "Jump" in skill_name:
                    jump_skill = player_char.spellbook['Skills'][skill_name]
                    break
            
            if jump_skill:
                player_char.class_effects["Jump"].active = False
                result = jump_skill.use(player_char, target=enemy)
                
                # Jump.use() returns a string, add it directly to combat log
                if result:
                    # Split multi-line messages and add each line
                    for line in result.strip().split('\n'):
                        if line.strip():
                            self.combat_view.add_combat_message(line)
                
                # Log skill usage
                self.logger.log_event(
                    event_type="skill",
                    actor=player_char,
                    target=enemy,
                    action=f"Used {jump_skill.name} (execution)",
                    outcome="Success"
                )
                return True
        
        # Check if player is berserked (auto-attack, no choice)
        if player_char.status_effects.get('Berserk') and player_char.status_effects['Berserk'].active:
            self.combat_view.add_combat_message(f"{player_char.name} is BERSERKED and attacks wildly!")
            
            # Force attack action
            action_result = self._execute_action("Attack", player_char, enemy)
            
            # Process status effects after attack
            effect_messages = self._process_status_effects(player_char)
            for msg in effect_messages:
                self.combat_view.add_combat_message(msg)
            
            return True
        
        # Check if player is stunned or asleep
        if player_char.status_effects.get('Stun') and player_char.status_effects['Stun'].active:
            self.combat_view.add_combat_message(f"{player_char.name} is stunned and cannot act!")
            # Process status effects (tick down duration)
            effect_messages = self._process_status_effects(player_char)
            for msg in effect_messages:
                self.combat_view.add_combat_message(msg)
            return True  # Skip turn
        
        if player_char.status_effects.get('Sleep') and player_char.status_effects['Sleep'].active:
            self.combat_view.add_combat_message(f"{player_char.name} is asleep and cannot act!")
            # Process status effects (tick down duration)
            effect_messages = self._process_status_effects(player_char)
            for msg in effect_messages:
                self.combat_view.add_combat_message(msg)
            return True  # Skip turn

        if player_char.physical_effects.get('Prone') and player_char.physical_effects['Prone'].active:
            self.combat_view.add_combat_message(f"{player_char.name} is prone and cannot act!")
            # Process status effects (attempt recovery)
            effect_messages = self._process_status_effects(player_char)
            for msg in effect_messages:
                self.combat_view.add_combat_message(msg)
            return True  # Skip turn
        
        # Get available actions
        actions = available_actions
        selected_action = 0
        
        action_taken = False
        
        while not action_taken:
            # Render combat scene
            self._render_combat_frame(player_char, enemy, actions, selected_action)
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

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
                            elif action_result is not None:
                                action_taken = True
            
            pygame.display.flip()
        
        # Process status effects on player after their turn (tick down durations, apply DOT)
        effect_messages = self._process_status_effects(player_char)
        for msg in effect_messages:
            self.combat_view.add_combat_message(msg)
        
        return True
    
    def _trigger_enemy_special_effects(self, player_char, enemy):
        """
        Trigger enemy special effects if health drops below threshold while alive.
        This must be called DURING combat, not after death.
        """
        if not enemy.is_alive() or not hasattr(enemy, 'special_effects'):
            return
        
        # Trigger special effects (will only activate if conditions are met, e.g., below 10% health)
        result = enemy.special_effects(player_char)
        if result:
            for line in result.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)
    
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
        from .confirmation_popup import ConfirmationPopup
        popup_text = "\n".join(transition_messages)
        popup = ConfirmationPopup(self.presenter, popup_text, show_buttons=False)
        popup.show()

        # Show combat log messages for the self-attack
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
        """Execute a player action."""
        if action == "Attack":
            # Execute attack using weapon_damage method (same as battle.py)
            enemy_hp_before = enemy.health.current
            message, hit, damage = player_char.weapon_damage(enemy)
            damage_dealt = max(0, enemy_hp_before - enemy.health.current)
            
            # Add the combat message (split multi-line output)
            for line in message.strip().split("\n"):
                if line.strip():
                    self.combat_view.add_combat_message(line)
            
            # Log attack event
            flags = []
            if not hit:
                flags.append("miss")
                outcome = "Miss"
            elif damage_dealt == 0:
                # Check if it was blocked completely vs just missed/no damage
                if "blocks" in message.lower() or "absorb" in message.lower():
                    flags.append("blocked")
                    outcome = "Blocked"
                else:
                    flags.append("no_damage")
                    outcome = "No Damage"
            else:
                flags.append("hit")
                # Check if damage was partially blocked
                if "blocks" in message.lower() or "mitigates" in message.lower():
                    flags.append("partial_block")
                    outcome = "Partial Block"
                else:
                    outcome = "Hit"
            
            self.logger.log_event(
                event_type="attack",
                actor=player_char,
                target=enemy,
                action="Attack",
                outcome=outcome,
                damage=damage_dealt,
                flags=flags
            )
            
            # Show damage flash if hit
            if damage_dealt > 0:
                self.combat_view.enemy_take_damage(enemy)
                self.combat_view.show_damage_flash(False, event_handler=self._handle_combat_log_scroll_event)
            
            self._preserve_waitress_for_transition(enemy)
            return "action_taken"
            
        elif action == "Flee":
            success, message = player_char.flee(enemy)
            self.combat_view.add_combat_message(message)
            if success:
                return "flee"
            return "action_taken"  # Failed flee still uses turn
            
        elif action == "Pickup Weapon":
            if player_char.is_disarmed():
                message = f"{player_char.name} picks up their weapon."
                player_char.physical_effects["Disarm"].active = False
                self.combat_view.add_combat_message(message)
                self.logger.log_event(
                    event_type="action",
                    actor=player_char,
                    action="Pickup Weapon",
                    outcome="Success"
                )
                return "action_taken"
            else:
                self.combat_view.add_combat_message("Not disarmed!")
                return None
            
        elif action == "Defend":
            message = player_char.enter_defensive_stance(duration=2, source="Defend")
            self.combat_view.add_combat_message(message.strip())
            self.logger.log_event(
                event_type="defend",
                actor=player_char,
                target=enemy,
                action="Defend",
                outcome="Success"
            )
            return "action_taken"
        
        elif action == "Items":
            # Show item selection menu
            selected_item = self._select_item(player_char, enemy)
            if selected_item:
                # Use the item
                message = selected_item.use(player_char, target=player_char)
                self.combat_view.add_combat_message(message.strip())
                
                # Log item usage
                self.logger.log_event(
                    event_type="item",
                    actor=player_char,
                    action=f"Used {selected_item.name}",
                    outcome="Success"
                )
                return "action_taken"
            return None  # Cancelled, don't count as action
            
        elif action == "Spells":
            # Check for Silence
            if player_char.status_effects["Silence"].active:
                self.combat_view.add_combat_message(f"{player_char.name} is silenced and cannot cast spells!")
                return None
            
            # Show spell selection menu
            selected_spell = self._select_spell(player_char, enemy)
            if selected_spell:
                # Cast the spell
                spell_obj = player_char.spellbook['Spells'][selected_spell]
                if player_char.mana.current >= spell_obj.cost:
                    self.combat_view.add_combat_message(f"{player_char.name} casts {selected_spell}.")
                    result = spell_obj.cast(player_char, target=enemy)
                    message = self._result_to_message(result)
                    self.combat_view.add_combat_message(message)
                    
                    # Log spell cast
                    self.logger.log_event(
                        event_type="spell",
                        actor=player_char,
                        target=enemy,
                        action=f"Cast {selected_spell}",
                        outcome="Success"
                    )
                    self._preserve_waitress_for_transition(enemy)
                    return "action_taken"
                else:
                    self.combat_view.add_combat_message("Not enough mana!")
                    return None
            return None  # Cancelled
            
        elif action == "Skills":
            # Check for Silence
            if player_char.status_effects["Silence"].active:
                self.combat_view.add_combat_message(f"{player_char.name} is silenced and cannot use skills!")
                return None
            
            # Show skill selection menu
            selected_skill = self._select_skill(player_char, enemy)
            if selected_skill:
                # Use the skill
                skill_obj = player_char.spellbook['Skills'][selected_skill]
                if player_char.mana.current >= skill_obj.cost:
                    self.combat_view.add_combat_message(f"{player_char.name} uses {selected_skill}.")
                    # Special handling for Jump
                    if "Jump" in selected_skill:
                        charge_time = skill_obj.get_charge_time() if hasattr(skill_obj, "get_charge_time") else 1
                        if charge_time > 0:
                            player_char.class_effects["Jump"].active = True
                        result = skill_obj.use(player_char, target=enemy)
                        if result:
                            for line in result.strip().split('\n'):
                                if line.strip():
                                    self.combat_view.add_combat_message(line)
                    # Special handling for Charge and other charging abilities
                    elif hasattr(skill_obj, 'get_charge_time') and skill_obj.get_charge_time() > 0:
                        charge_time = skill_obj.get_charge_time()
                        result = skill_obj.use(player_char, target=enemy)
                        if result:
                            for line in result.strip().split('\n'):
                                if line.strip():
                                    self.combat_view.add_combat_message(line)
                        # Track that this ability is charging
                        if getattr(skill_obj, 'charging', False):
                            self.charging_ability = (selected_skill, skill_obj)
                    else:
                        if skill_obj.name == "Slot Machine":
                            result = skill_obj.use(
                                player_char,
                                target=enemy,
                                slot_machine_callback=lambda _u, _t: self._show_slot_machine_reveal(player_char, enemy),
                            )
                        else:
                            result = skill_obj.use(player_char, target=enemy)
                        message = self._result_to_message(result)
                        self.combat_view.add_combat_message(message)
                    
                    # Log skill usage
                    self.logger.log_event(
                        event_type="skill",
                        actor=player_char,
                        target=enemy,
                        action=f"Used {selected_skill}",
                        outcome="Success"
                    )
                    self._preserve_waitress_for_transition(enemy)
                    return "action_taken"
                else:
                    self.combat_view.add_combat_message("Not enough mana!")
                    return None
            return None  # Cancelled
    
    def _select_totem_aspect(self, player_char, enemy, totem_skill):
        """Show Totem aspect selection menu and return aspect name."""
        if not totem_skill or not hasattr(totem_skill, "get_unlocked_aspects"):
            return None

        aspects = totem_skill.get_unlocked_aspects(player_char)
        if not aspects:
            self.combat_view.add_combat_message("No Totem aspects unlocked!")
            self._pause_with_events(500)
            return None

        selected = 0
        active = getattr(totem_skill, "active_aspect", "")
        while True:
            self._render_combat_frame(player_char, enemy, [], -1)
            options = []
            for aspect in aspects:
                suffix = " (Active)" if aspect == active else ""
                options.append(f"{aspect}{suffix}")

            self._render_selection_menu("Select Totem Aspect", options, selected)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(aspects)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(aspects)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return aspects[selected]
    
    def _select_item(self, player_char, enemy):
        """Show item selection menu and return selected item."""
        # Get usable items (Health, Mana, Elixir, Status potions)
        usable_types = ['Health', 'Mana', 'Elixir', 'Status', 'Scroll']
        items = []
        for item_name, item_list in player_char.inventory.items():
            if item_list and item_list[0].subtyp in usable_types:
                items.append((item_name, item_list[0], len(item_list)))
        
        if not items:
            self.combat_view.add_combat_message("No usable items!")
            self._pause_with_events(500)
            return None
        
        # Create selection menu
        selected = 0
        scroll_offset = 0
        while True:
            # Render combat with item menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            self._render_selection_menu(
                "Select Item",
                [f"{name} ({count})" for name, _, count in items],
                selected,
                scroll_offset
            )
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(items)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(items)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(items) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return items[selected][1]  # Return the item object
                    
                    # Update scroll to keep selection visible
                    max_visible = 12  # items per screen
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
    
    def _select_spell(self, player_char, enemy):
        """Show spell selection menu and return selected spell name."""
        # Filter out passive spells
        spells = [name for name, spell in player_char.spellbook['Spells'].items() 
                  if not getattr(spell, 'passive', False)]
        
        if not spells:
            self.combat_view.add_combat_message("No spells learned!")
            self._pause_with_events(500)
            return None
        
        selected = 0
        scroll_offset = 0
        while True:
            # Render combat with spell menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            spell_options = []
            for spell_name in spells:
                spell = player_char.spellbook['Spells'][spell_name]
                cost = spell.cost
                spell_options.append(f"{spell_name} (MP: {cost})")
            
            self._render_selection_menu("Select Spell", spell_options, selected, scroll_offset)
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(spells)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(spells)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(spells) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return spells[selected]  # Return spell name
                    
                    # Update scroll to keep selection visible
                    max_visible = 12  # items per screen
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
    
    def _select_skill(self, player_char, enemy):
        """Show skill selection menu and return selected skill name."""
        # Filter out passive skills
        skills = [name for name, skill in player_char.spellbook['Skills'].items()
                  if not getattr(skill, 'passive', False)]
        
        if not skills:
            self.combat_view.add_combat_message("No skills learned!")
            self._pause_with_events(500)
            return None
        
        selected = 0
        scroll_offset = 0
        while True:
            # Render combat with skill menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            skill_options = []
            for skill_name in skills:
                skill = player_char.spellbook['Skills'][skill_name]
                cost = skill.cost
                skill_options.append(f"{skill_name} (MP: {cost})")
            
            self._render_selection_menu("Select Skill", skill_options, selected, scroll_offset)
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(skills)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(skills)
                    elif event.key == pygame.K_PAGEUP:
                        selected = max(0, selected - 10)
                    elif event.key == pygame.K_PAGEDOWN:
                        selected = min(len(skills) - 1, selected + 10)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return skills[selected]  # Return skill name
                    
                    # Update scroll to keep selection visible
                    max_visible = 12  # items per screen
                    if selected < scroll_offset:
                        scroll_offset = selected
                    elif selected >= scroll_offset + max_visible:
                        scroll_offset = selected - max_visible + 1
    
    def _render_selection_menu(self, title, options, selected, scroll_offset=0):
        """Render a selection menu overlay on combat screen with scrolling support."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.combat_view.combat_width, self.combat_view.combat_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))
        
        # Menu dimensions
        menu_width = 400
        max_visible = 12
        menu_height = min(500, 100 + max_visible * 30)
        menu_x = (self.combat_view.combat_width - menu_width) // 2
        menu_y = (self.combat_view.combat_height - menu_height) // 2
        
        # Menu background
        pygame.draw.rect(self.screen, (40, 40, 50), 
                        pygame.Rect(menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, (100, 100, 120), 
                        pygame.Rect(menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        font_large = pygame.font.Font(None, 32)
        title_surf = font_large.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(menu_x + menu_width // 2, menu_y + 30))
        self.screen.blit(title_surf, title_rect)
        
        # Options - only render visible ones
        font_medium = pygame.font.Font(None, 24)
        option_y = menu_y + 70
        
        # Clamp scroll_offset
        max_scroll = max(0, len(options) - max_visible)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        start_idx = scroll_offset
        end_idx = min(len(options), scroll_offset + max_visible)
        
        for i in range(start_idx, end_idx):
            option = options[i]
            # Highlight selected option
            if i == selected:
                highlight_rect = pygame.Rect(menu_x + 10, option_y - 3, menu_width - 30, 30)
                pygame.draw.rect(self.screen, (80, 80, 100), highlight_rect)
            
            # Truncate text if too long
            if len(option) > 40:
                option = option[:37] + "..."
            
            option_surf = font_medium.render(f"{i+1}. {option}", True, (255, 255, 255))
            self.screen.blit(option_surf, (menu_x + 20, option_y))
            option_y += 30
        
        # Scrollbar (if needed)
        if len(options) > max_visible:
            scrollbar_height = int((menu_height - 120) * max_visible / len(options))
            scrollbar_height = max(20, scrollbar_height)
            scrollbar_y = menu_y + 70 + int((menu_height - 120 - scrollbar_height) * scroll_offset / max_scroll)
            pygame.draw.rect(self.screen, (150, 150, 180), 
                           pygame.Rect(menu_x + menu_width - 16, scrollbar_y, 6, scrollbar_height))
        
        # Instructions
        font_small = pygame.font.Font(None, 18)
        if len(options) > max_visible:
            instructions = "Up/Down or W/S: Navigate | PgUp/PgDn: Scroll | Enter: Select | Esc: Cancel"
        else:
            instructions = "Up/Down or W/S: Navigate | Enter/Space: Select | Esc: Cancel"
        instr_surf = font_small.render(instructions, True, (180, 180, 180))
        instr_rect = instr_surf.get_rect(center=(menu_x + menu_width // 2, menu_y + menu_height - 20))
        self.screen.blit(instr_surf, instr_rect)
    
    def _enemy_turn(self, player_char, enemy):
        """Handle enemy's turn (automated)."""
        # Check if enemy is stunned or asleep
        if enemy.status_effects.get('Stun') and enemy.status_effects['Stun'].active:
            self.combat_view.add_combat_message(f"{enemy.name} is stunned and cannot act!")
            
            # Log stunned turn
            self.logger.log_event(
                event_type="status",
                actor=enemy,
                action="Stunned",
                outcome="Skip turn"
            )
            
            # Process status effects (tick down duration)
            effect_messages = self._process_status_effects(enemy)
            for msg in effect_messages:
                self.combat_view.add_combat_message(msg)
            return  # Skip turn
        
        if enemy.status_effects.get('Sleep') and enemy.status_effects['Sleep'].active:
            self.combat_view.add_combat_message(f"{enemy.name} is asleep and cannot act!")
            
            # Log asleep turn
            self.logger.log_event(
                event_type="status",
                actor=enemy,
                action="Asleep",
                outcome="Skip turn"
            )
            
            # Process status effects (tick down duration)
            effect_messages = self._process_status_effects(enemy)
            for msg in effect_messages:
                self.combat_view.add_combat_message(msg)
            return  # Skip turn

        if enemy.physical_effects.get('Prone') and enemy.physical_effects['Prone'].active:
            self.combat_view.add_combat_message(f"{enemy.name} is prone and cannot act!")

            # Log prone turn
            self.logger.log_event(
                event_type="status",
                actor=enemy,
                action="Prone",
                outcome="Skip turn"
            )

            # Process status effects (attempt recovery)
            effect_messages = self._process_status_effects(enemy)
            for msg in effect_messages:
                self.combat_view.add_combat_message(msg)
            return  # Skip turn

        # Continue already-started charging skills before selecting a new action.
        # This keeps telegraphed enemy abilities (e.g., Crushing Blow/Charge) deterministic
        # and prevents normal attacks from replacing the charged resolution turn.
        charging_skill_name = None
        charging_skill_obj = None
        for skill_name, skill in enemy.spellbook.get('Skills', {}).items():
            if getattr(skill, 'charging', False):
                charging_skill_name = skill_name
                charging_skill_obj = skill
                break

        if charging_skill_obj is not None:
            self.combat_view.add_combat_message(f"{enemy.name} continues {charging_skill_obj.name}.")
            result = charging_skill_obj.use(enemy, target=player_char)
            message = self._result_to_message(result)
            if message:
                for line in str(message).split("\n"):
                    if line.strip():
                        self.combat_view.add_combat_message(line)

            self.logger.log_event(
                event_type="skill",
                actor=enemy,
                target=player_char,
                action=f"Used {charging_skill_name} (charge)",
                outcome="Success"
            )
            return None
        
        # Render current state and pause before enemy acts (with animation updates)
        enemy_clock = pygame.time.Clock()
        for _ in range(30):  # 500ms at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            enemy_clock.tick(60)
        
        # Choose action using enemy AI
        action = "Attack"
        choice = None
        if enemy.class_effects.get("Jump") and enemy.class_effects["Jump"].active:
            try:
                choice = [x for x in enemy.spellbook.get('Skills', {}) if "Jump" in x][0]
                enemy.class_effects["Jump"].active = False
                action = "Use Skill"
            except IndexError:
                action = "Attack"
        else:
            try:
                action, choice = enemy.options(player_char, self.available_actions, self.current_tile)
            except Exception:
                action, choice = "Attack", None

        if action == "Nothing":
            self.combat_view.add_combat_message(f"{enemy.name} does nothing.")
            return None
        if action == "Pickup Weapon":
            enemy.physical_effects["Disarm"].active = False
            self.combat_view.add_combat_message(f"{enemy.name} picks up their weapon.")
            return None
        if action == "Defend":
            message = enemy.enter_defensive_stance(duration=2, source="Defend")
            self.combat_view.add_combat_message(message.strip())
            self.logger.log_event(
                event_type="defend",
                actor=enemy,
                target=player_char,
                action="Defend",
                outcome="Success"
            )
            return None
        if action == "Flee":
            success, message = enemy.flee(player_char)
            self.combat_view.add_combat_message(message)
            if success:
                return "flee"
            return None
        if action == "Cast Spell" and choice:
            spell_obj = enemy.spellbook['Spells'].get(choice)
            if spell_obj and enemy.mana.current >= spell_obj.cost:
                self.combat_view.add_combat_message(f"{enemy.name} casts {choice}.")
                result = spell_obj.cast(enemy, target=player_char)
                message = self._result_to_message(result)
                self.combat_view.add_combat_message(message)
                self.logger.log_event(
                    event_type="spell",
                    actor=enemy,
                    target=player_char,
                    action=f"Cast {choice}",
                    outcome="Success"
                )
                return None
            self.combat_view.add_combat_message("Not enough mana!")
            return None
        if action == "Use Skill" and choice:
            skill_obj = enemy.spellbook['Skills'].get(choice)
            if skill_obj and enemy.mana.current >= skill_obj.cost:
                result = None
                enemy_name_before = enemy.name
                self.combat_view.add_combat_message(f"{enemy.name} uses {choice}.")
                if skill_obj.name == 'Smoke Screen':
                    result = skill_obj.use(enemy, target=player_char)
                    _, flee_str = enemy.flee(player_char, smoke=True)
                    if flee_str:
                        result = f"{result}\n{flee_str}" if result else flee_str
                elif skill_obj.name == "Slot Machine":
                    result = skill_obj.use(
                        enemy,
                        target=player_char,
                        slot_machine_callback=lambda _u, _t: self._show_slot_machine_reveal(player_char, enemy),
                    )
                elif skill_obj.name in ["Doublecast", "Triplecast"]:
                    result = skill_obj.use(enemy, player_char, game=self.game)
                elif "Jump" in skill_obj.name:
                    charge_time = skill_obj.get_charge_time() if hasattr(skill_obj, "get_charge_time") else 1
                    if charge_time > 0:
                        enemy.class_effects["Jump"].active = True
                    result = skill_obj.use(enemy, target=player_char)
                else:
                    result = skill_obj.use(enemy, target=player_char)

                # Check if enemy shapeshifted (name changed)
                if enemy.name != enemy_name_before:
                    self.combat_view.reload_enemy_sprite(enemy)

                message = self._result_to_message(result)
                if message:
                    for line in str(message).split("\n"):
                        if line.strip():
                            self.combat_view.add_combat_message(line)
                self.logger.log_event(
                    event_type="skill",
                    actor=enemy,
                    target=player_char,
                    action=f"Used {skill_obj.name}",
                    outcome="Success"
                )
                return None
            self.combat_view.add_combat_message("Not enough mana!")
            return None
        if action == "Use Item" and choice:
            item_key = re.split(r"\s{2,}", choice)[0]
            if item_key in enemy.inventory and enemy.inventory[item_key]:
                itm = enemy.inventory[item_key][0]
                target = enemy
                if itm.subtyp == "Scroll" and itm.spell.subtyp != "Support":
                    target = player_char
                message = itm.use(enemy, target=target)
                if message:
                    self.combat_view.add_combat_message(message.strip())
                self.logger.log_event(
                    event_type="item",
                    actor=enemy,
                    target=target,
                    action=f"Used {itm.name}",
                    outcome="Success"
                )
                return None

        # Enemy attacks using weapon_damage method (same as battle.py)
        player_hp_before = player_char.health.current
        if not random.randint(0, 9 - enemy.check_mod("luck", luck_factor=20)):
            try:
                message = enemy.special_attack(target=player_char)
                hit = True
            except NotImplementedError:
                message, hit, _ = enemy.weapon_damage(player_char)
        else:
            message, hit, _ = enemy.weapon_damage(player_char)
        damage_dealt = max(0, player_hp_before - player_char.health.current)
        
        # Add the combat message (split multi-line output)
        for line in message.strip().split("\n"):
            if line.strip():
                self.combat_view.add_combat_message(line)
        
        # Log enemy attack
        flags = []
        if not hit:
            flags.append("miss")
            outcome = "Miss"
        elif damage_dealt == 0:
            # Check if it was blocked completely vs just missed/no damage
            if "blocks" in message.lower() or "absorb" in message.lower():
                flags.append("blocked")
                outcome = "Blocked"
            else:
                flags.append("no_damage")
                outcome = "No Damage"
        else:
            flags.append("hit")
            # Check if damage was partially blocked
            if "blocks" in message.lower() or "mitigates" in message.lower():
                flags.append("partial_block")
                outcome = "Partial Block"
            else:
                outcome = "Hit"
        
        self.logger.log_event(
            event_type="attack",
            actor=enemy,
            target=player_char,
            action="Attack",
            outcome=outcome,
            damage=damage_dealt,
            flags=flags
        )
        
        # Show damage flash if hit
        if damage_dealt > 0:
            self.combat_view.show_damage_flash(True, event_handler=self._handle_combat_log_scroll_event)
        
        # Render updated state and show result (with animation updates)
        result_clock = pygame.time.Clock()
        for _ in range(48):  # 800ms at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            result_clock.tick(60)
        
        # Process status effects on enemy after their turn (tick down durations, apply DOT)
        effect_messages = self._process_status_effects(enemy)
        for msg in effect_messages:
            self.combat_view.add_combat_message(msg)
    
    def _render_combat_frame(self, player_char, enemy, actions, selected_action):
        """Render a single frame of combat."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render the dungeon view as background (same as exploration)
        # This is passed from dungeon_manager
        if self.dungeon_renderer and self.player_world_dict:
            try:
                self.dungeon_renderer.render_dungeon_view(player_char, self.player_world_dict)
            except Exception as e:
                # Fallback to black screen if dungeon rendering fails
                self.screen.fill((0, 0, 0))
        
        # Render enemy in the dungeon (in front of player)
        self.combat_view.render_enemy_in_dungeon(player_char, enemy)
        
        # Render combat HUD overlay (action menu and combat log)
        self.combat_view.render_combat_overlay(player_char, enemy, actions, selected_action)
        
        # Render HUD (right 1/3) with combat mode indicator
        self.hud.render_hud(player_char, combat_mode=True, enemy=enemy)

    def _refresh_combat_background(self, player_char, enemy):
        """Render and cache the latest combat frame for popups/overlays."""
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        self._combat_background = self.screen.copy()
    
    def _handle_combat_end(self, player_char, enemy, fled):
        """Handle end of combat and show results."""
        end_messages = []

        def _show_end_popup(message_text: str) -> None:
            self._refresh_combat_background(player_char, enemy)
            background = self._combat_background if self._combat_background is not None else self._capture_background()
            draw_background = lambda: self.screen.blit(background, (0, 0))
            from .confirmation_popup import ConfirmationPopup
            popup = ConfirmationPopup(self.presenter, message_text, show_buttons=False)
            popup.show(background_draw_func=draw_background)

        # Clear status effects at end of combat
        player_char.effects(end=True)
        if player_char.in_town():
            # Sanctuary or similar movement effect ended combat by relocating the player.
            self.logger.end_battle(result="Escaped", winner=None, boss=False)
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        if not player_char.is_alive():
            end_messages.append("You have been defeated!")

            # Reset enemy status effects and restore health/mana (only matters for boss fights)
            enemy.effects(end=True)
            enemy.health.current = enemy.health.max
            enemy.mana.current = enemy.mana.max

            # Log battle end
            self.logger.end_battle(result="Defeat", winner=enemy.name, boss="Boss" in str(self.current_tile))

            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()

            self._pause_with_events(900)

            # Show defeat message in popup over current post-combat frame
            _show_end_popup("\n".join(end_messages))
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False
        
        elif not enemy.is_alive():
            end_messages.append(f"Victory! {enemy.name} defeated!")
            
            # Log victory
            self.logger.end_battle(result="Victory", winner=player_char.name, boss="Boss" in str(self.current_tile))
            
            # Handle loot drops (gold, exp, and items)
            tile = getattr(self, 'current_tile', None)

            # Record kill in player kill_dict (for defeat quests)
            try:
                if enemy.enemy_typ not in player_char.kill_dict:
                    player_char.kill_dict[enemy.enemy_typ] = {}
                if enemy.name not in player_char.kill_dict[enemy.enemy_typ]:
                    player_char.kill_dict[enemy.enemy_typ][enemy.name] = 0
                player_char.kill_dict[enemy.enemy_typ][enemy.name] += 1
            except Exception:
                pass

            # Mark boss tiles defeated so quests can be completed after the fact
            if tile is not None and hasattr(tile, 'defeated'):
                tile.defeated = True
            
            # Award experience
            exp_gained = enemy.experience
            player_char.level.exp += exp_gained
            end_messages.append(f"Gained {exp_gained} exp!")
            
            # Handle gold and item drops
            loot_msg = player_char.loot(enemy, tile)
            if loot_msg:
                for line in loot_msg.strip().split('\n'):
                    if line:
                        end_messages.append(line)
            
            # Check for quest completion
            quest_msg = player_char.quests(enemy=enemy)
            if quest_msg:
                for line in quest_msg.strip().split('\n'):
                    if line:
                        end_messages.append(line)
            
            # Check for level up
            level_up = False
            if not player_char.max_level():
                player_char.level.exp_to_gain -= exp_gained
                if player_char.level.exp_to_gain <= 0:
                    level_up = True
                    end_messages.append("\nLEVEL UP!")
            
            # Render final combat state and let death animation complete (~60 frames)
            clock = pygame.time.Clock()
            for _ in range(70):  # Let death dissolve animation play out
                self._render_combat_frame(player_char, enemy, [], -1)
                pygame.display.flip()
                clock.tick(60)  # 60 FPS
                
                # Handle events to prevent window freeze
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    self._handle_combat_log_scroll_event(event)

            self._pause_with_events(900)
            
            # Show all end messages in popup over current post-combat frame
            _show_end_popup("\n".join(end_messages))
            
            # Handle level up screen if needed
            if level_up:
                self.level_up_screen.show_level_up(player_char, self.game)
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return True
        
        elif fled:
            end_messages.append("You fled from combat!")
            
            # Log fled battle (cannot flee boss fights)
            self.logger.end_battle(result="Fled", winner=None, boss=False)
            
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()

            self._pause_with_events(700)
            
            # Show flee message in popup over current post-combat frame
            _show_end_popup("\n".join(end_messages))
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        self.combat_view.reset_combat_log()
        self._combat_background = None
        return True

    def _pause_with_events(self, duration_ms: int) -> None:
        """Pause briefly while pumping events to avoid unresponsive window."""
        pause_clock = pygame.time.Clock()
        elapsed = 0
        while elapsed < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                self._handle_combat_log_scroll_event(event)
            pause_clock.tick(60)
            elapsed += pause_clock.get_time()

    def _process_status_effects(self, character: Character) -> list[str]:
        """
        Process and tick down status effects for a character.
        Returns list of messages about status effects that are active.
        """
        messages = []
        silent_effects = {"Shapeshifted"}
        
        # Process all status effect dictionaries
        effect_dicts = [
            (character.status_effects, "Status"),
            (character.physical_effects, "Physical"),
            (character.stat_effects, "Stat"),
            (character.magic_effects, "Magic")
        ]
        
        for effect_dict, category_name in effect_dicts:
            for effect_name, effect_obj in effect_dict.items():
                if effect_obj.active:
                    if effect_name == "Prone":
                        if effect_obj.duration <= 0:
                            effect_obj.active = False
                            messages.append(f"{character.name} is no longer prone.")
                        elif (not random.randint(0, effect_obj.duration)
                              or random.randint(0, character.check_mod("luck", luck_factor=10))):
                            effect_obj.active = False
                            effect_obj.duration = 0
                            messages.append(f"{character.name} is no longer prone.")
                        else:
                            effect_obj.duration -= 1
                            messages.append(f"{character.name} is still prone.")
                        continue

                if effect_obj.active and effect_obj.duration > 0:
                    # Add message about active effect
                    if effect_name not in silent_effects:
                        messages.append(f"{character.name} is affected by {effect_name}!")
                    
                    # Apply damage/healing for damage-over-time effects
                    if effect_name == "DOT" and hasattr(effect_obj, 'extra') and effect_obj.extra > 0:
                        damage = effect_obj.extra
                        character.health.current -= damage
                        messages.append(f"{character.name} takes {damage} DOT damage!")
                    elif effect_name == "Poison" and hasattr(effect_obj, 'extra') and effect_obj.extra > 0:
                        damage = effect_obj.extra
                        character.health.current -= damage
                        messages.append(f"{character.name} takes {damage} poison damage!")
                    elif effect_name == "Bleed" and hasattr(effect_obj, 'extra') and effect_obj.extra > 0:
                        damage = effect_obj.extra
                        character.health.current -= damage
                        messages.append(f"{character.name} bleeds for {damage} damage!")
                    elif effect_name == "Regen" and hasattr(effect_obj, 'extra') and effect_obj.extra > 0:
                        healing = effect_obj.extra
                        character.health.current = min(character.health.current + healing, character.health.max)
                        messages.append(f"{character.name} regenerates {healing} HP!")
                    
                    # Tick down duration
                    effect_obj.duration -= 1
                    
                    # Deactivate if duration expired
                    if effect_obj.duration <= 0:
                        effect_obj.active = False
                        if effect_name not in silent_effects:
                            messages.append(f"{character.name}'s {effect_name} wears off.")
        
        return messages
