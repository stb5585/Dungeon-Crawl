"""
Combat Manager for Pygame GUI.
Handles combat flow with GUI rendering, delegating core game logic to BattleEngine.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import random
import sys

import pygame

from src.core import enemies
from src.core.combat.battle_engine import BattleEngine
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

# Map display action names (pygame) back to engine action names
_DISPLAY_TO_ENGINE = {
    "Spells": "Cast Spell",
    "Skills": "Use Skill",
    "Items": "Use Item",
}


class GUICombatManager:
    """Manages combat with pygame GUI rendering, delegating logic to BattleEngine."""
    
    def __init__(self, presenter: PygamePresenter, hud: DungeonHUD, game: PygameGame):
        self.presenter = presenter
        self.screen = presenter.screen
        self.hud = hud
        self.game = game
        self.combat_view = CombatView(self.screen, presenter)
        self.level_up_screen = LevelUpScreen(self.screen, presenter)
        self.logger = BattleLogger()
        self.running = False
        self.engine: BattleEngine | None = None
        # References to dungeon rendering (set by dungeon_manager)
        self.dungeon_renderer = None
        self.player_world_dict = None
        self._combat_background = None
        self.available_actions = []
    
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

        # Create the core engine (handles initiative, actions, bookkeeping)
        self.engine = BattleEngine(
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
                    self.combat_view.enemy_dies(enemy)
                    break
                
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
                
                # Check if player died
                if not player_char.is_alive():
                    break

                # Prevent Mad Waitress from dying before her forced transition
                self._preserve_waitress_for_transition(enemy)
                self._check_enemy_form_change(player_char, enemy)
                
                # Check if enemy died (e.g., from self-damaging skills like Widow's Wail)
                if not enemy.is_alive():
                    self.combat_view.enemy_dies(enemy)
                    break
            
            # Advance turn: post-turn processing + swap
            self._post_turn_processing(player_char, enemy)
            self.engine.swap_turns()
            self._refresh_combat_background(player_char, enemy)
            
            # Refresh available actions for next turn
            self.available_actions = self._build_display_actions()
            
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

        # Add Pickup Weapon if disarmed
        if self.engine.player.is_disarmed() and "Pickup Weapon" not in deduped:
            idx = 2 if "Defend" in deduped else 1
            deduped.insert(idx, "Pickup Weapon")

        return deduped

    def _post_turn_processing(self, player_char: Player, enemy: Character) -> None:
        """Handle engine post-turn + display any messages."""
        visual_before = (getattr(enemy, "name", None), getattr(enemy, "picture", None))
        post = self.engine.post_turn()
        visual_after = (getattr(enemy, "name", None), getattr(enemy, "picture", None))
        if visual_after != visual_before:
            self.combat_view.reload_enemy_sprite(enemy)
        for msg in post.messages:
            if msg:
                for line in msg.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
    
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

        # If the player died from effects (poison, DOT, bleed), end turn immediately
        if pre.died_from_effects:
            return True

        if not pre.can_act:
            self.combat_view.add_combat_message(pre.inactive_reason.strip())
            return True  # Turn skipped

        # Check for forced actions (berserk, charging, jump)
        forced = self.engine.get_forced_action()
        if forced:
            if forced.action == "Cancelled":
                for line in forced.cancel_message.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
                return True

            if forced.action == "Attack":
                self.combat_view.add_combat_message(f"{player_char.name} is BERSERKED and attacks wildly!")

            # Execute the forced action via engine
            enemy_hp_before = enemy.health.current
            result = self.engine.execute_action(forced.action, choice=forced.choice)

            for line in result.message.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)

            # Damage flash for attack/skill hits
            damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
            if damage_to_enemy > 0:
                self.combat_view.enemy_take_damage(enemy)
                self.combat_view.show_damage_flash(False, event_handler=self._handle_combat_log_scroll_event)

            self._preserve_waitress_for_transition(enemy)

            if result.fled:
                return "flee"
            return True
        
        # Get available actions
        actions = self.available_actions
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
        popup.show(flush_events=True, require_key_release=True)

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
        """Execute a player action by delegating to the engine."""
        # Map display name back to engine name
        engine_action = _DISPLAY_TO_ENGINE.get(action, action)

        # Sub-menu actions need a selection UI first
        choice = None

        if action == "Items":
            selected_item = self._select_item(player_char, enemy)
            if not selected_item:
                return None  # Cancelled
            choice = selected_item.name

        elif action == "Spells":
            if player_char.abilities_suppressed():
                reason = "the anti-magic field" if getattr(player_char, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{player_char.name} cannot cast spells because of {reason}!"
                )
                return None
            selected_spell = self._select_spell(player_char, enemy)
            if not selected_spell:
                return None
            choice = selected_spell

        elif action == "Skills":
            if player_char.abilities_suppressed():
                reason = "the anti-magic field" if getattr(player_char, "anti_magic_active", False) else "silence"
                self.combat_view.add_combat_message(
                    f"{player_char.name} cannot use skills because of {reason}!"
                )
                return None
            selected_skill = self._select_skill(player_char, enemy)
            if not selected_skill:
                return None
            choice = selected_skill

        elif action == "Pickup Weapon":
            if not player_char.is_disarmed():
                self.combat_view.add_combat_message("Not disarmed!")
                return None

        # Record HP before execution for damage flash
        enemy_hp_before = enemy.health.current
        player_hp_before = player_char.health.current
        enemy_name_before = enemy.name

        # Delegate to engine (handles attack rolls, spell casts, skill use, etc.)
        slot_cb = None
        if action == "Skills" and choice:
            skill_obj = player_char.spellbook.get('Skills', {}).get(choice)
            if skill_obj and skill_obj.name == "Slot Machine":
                slot_cb = lambda _u, _t: self._show_slot_machine_reveal(player_char, enemy)

        result = self.engine.execute_action(engine_action, choice=choice, slot_machine_callback=slot_cb)

        # Display result messages
        for line in result.message.strip().split('\n'):
            if line.strip():
                self.combat_view.add_combat_message(line)

        # Show damage flash for enemy damage
        damage_to_enemy = max(0, enemy_hp_before - enemy.health.current)
        if damage_to_enemy > 0:
            self.combat_view.enemy_take_damage(enemy)
            self.combat_view.show_damage_flash(False, event_handler=self._handle_combat_log_scroll_event)

        # Show damage flash for player damage (from reflected/self-damage skills)
        damage_to_player = max(0, player_hp_before - player_char.health.current)
        if damage_to_player > 0:
            self.combat_view.show_damage_flash(True, event_handler=self._handle_combat_log_scroll_event)

        # Check if enemy shapeshifted (name changed)
        if enemy.name != enemy_name_before:
            self.combat_view.reload_enemy_sprite(enemy)

        self._preserve_waitress_for_transition(enemy)

        if result.fled:
            return "flee"
        return "action_taken"
    
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
        """Handle enemy's turn (automated), delegating logic to the engine."""
        # Pre-turn: process status effects and check activity
        pre = self.engine.pre_turn()
        if pre.effects_text:
            for line in pre.effects_text.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)

        # If the enemy died from its own effects (poison, DOT, bleed), end turn
        if pre.died_from_effects:
            return None

        if not pre.can_act:
            self.combat_view.add_combat_message(pre.inactive_reason.strip())
            return None  # Skip turn
        
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

        # Check for forced actions (charging skills, jump)
        forced = self.engine.get_forced_action()
        if forced:
            if forced.action == "Cancelled":
                for line in forced.cancel_message.strip().split('\n'):
                    if line.strip():
                        self.combat_view.add_combat_message(line)
                return None

            enemy_name_before = enemy.name
            player_hp_before = player_char.health.current

            result = self.engine.execute_action(forced.action, choice=forced.choice)
            for line in result.message.strip().split('\n'):
                if line.strip():
                    self.combat_view.add_combat_message(line)

            # Check if enemy shapeshifted
            if enemy.name != enemy_name_before:
                self.combat_view.reload_enemy_sprite(enemy)

            damage_to_player = max(0, player_hp_before - player_char.health.current)
            if damage_to_player > 0:
                self.combat_view.show_damage_flash(True, event_handler=self._handle_combat_log_scroll_event)

            if result.fled:
                return "flee"
            return None

        # Enemy AI chooses action
        action, choice = self.engine.get_enemy_action()

        if action == "Nothing":
            self.combat_view.add_combat_message(f"{enemy.name} does nothing.")
            return None

        # Record state before execution
        player_hp_before = player_char.health.current
        enemy_name_before = enemy.name

        # Delegate to engine (handles Smoke Screen flee, Slot Machine, Doublecast, Jump, etc.)
        slot_cb = None
        if action == "Use Skill" and choice:
            skill_obj = enemy.spellbook.get('Skills', {}).get(choice)
            if skill_obj and skill_obj.name == "Slot Machine":
                slot_cb = lambda _u, _t: self._show_slot_machine_reveal(player_char, enemy)

        result = self.engine.execute_action(action, choice=choice, slot_machine_callback=slot_cb)

        # Display messages
        for line in result.message.strip().split('\n'):
            if line.strip():
                self.combat_view.add_combat_message(line)

        # Check if enemy shapeshifted (name changed)
        if enemy.name != enemy_name_before:
            self.combat_view.reload_enemy_sprite(enemy)

        # Show damage flash if player took damage
        damage_to_player = max(0, player_hp_before - player_char.health.current)
        if damage_to_player > 0:
            self.combat_view.show_damage_flash(True, event_handler=self._handle_combat_log_scroll_event)

        if result.fled:
            return "flee"

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

        return None
    
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
        current_turn = None
        if self.engine is not None and getattr(self.engine, "attacker", None) is not None:
            current_turn = "player" if self.engine.is_player_turn() else "enemy"
        self.combat_view.render_combat_overlay(
            player_char,
            enemy,
            actions,
            selected_action,
            current_turn=current_turn,
        )
        
        # Render HUD (right 1/3) with combat mode indicator
        self.hud.render_hud(player_char, combat_mode=True, enemy=enemy)

    def _refresh_combat_background(self, player_char, enemy):
        """Render and cache the latest combat frame for popups/overlays."""
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        self._combat_background = self.screen.copy()
    
    def _handle_combat_end(self, player_char, enemy, fled):
        """Handle end of combat using the engine for bookkeeping."""

        def _show_end_popup(message_text: str) -> None:
            self._refresh_combat_background(player_char, enemy)
            background = self._combat_background if self._combat_background is not None else self._capture_background()
            draw_background = lambda: self.screen.blit(background, (0, 0))
            from .confirmation_popup import ConfirmationPopup
            popup = ConfirmationPopup(self.presenter, message_text, show_buttons=False)
            popup.show(
                background_draw_func=draw_background,
                flush_events=True,
                require_key_release=True,
            )

        # Handle Sanctuary (player got teleported to town during combat)
        if player_char.in_town():
            player_char.effects(end=True)
            self.logger.end_battle(result="Escaped", winner=None, boss=False)
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        # Sync engine flee state (in case player fled via UI flow)
        if fled:
            self.engine.flee = True

        # Let the engine handle all bookkeeping (exp, loot, quests, kill tracking, etc.)
        outcome = self.engine.end_battle()

        if outcome.result == "defeat":
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            self._pause_with_events(900)

            _show_end_popup("You have been defeated!")
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        elif outcome.result == "victory":
            # Build end messages from outcome
            end_messages = [f"Victory! {enemy.name} defeated!"]
            # Parse the outcome message for display lines
            for line in outcome.message.strip().split('\n'):
                if line.strip():
                    end_messages.append(line)

            if outcome.level_up:
                end_messages.append("\nLEVEL UP!")

            # Render final combat state and let death animation complete
            clock = pygame.time.Clock()
            for _ in range(70):
                self._render_combat_frame(player_char, enemy, [], -1)
                pygame.display.flip()
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    self._handle_combat_log_scroll_event(event)

            self._pause_with_events(900)
            _show_end_popup("\n".join(end_messages))

            if outcome.level_up:
                self.level_up_screen.show_level_up(player_char, self.game)

            self.combat_view.reset_combat_log()
            self._combat_background = None
            return True

        elif outcome.result == "flee":
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            self._pause_with_events(700)

            _show_end_popup("You fled from combat!")
            self.combat_view.reset_combat_log()
            self._combat_background = None
            return False

        # Fallback
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
