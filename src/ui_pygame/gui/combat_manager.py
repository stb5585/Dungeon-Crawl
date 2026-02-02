"""
Combat Manager for Pygame GUI.
Handles combat flow with GUI rendering (doesn't use curses BattleManager).
"""
from __future__ import annotations

import pygame

from src.core.character import Character
from src.core.combat.battle_logger import BattleLogger
from src.core.player import Player
from .combat_view import CombatView
from .level_up import LevelUpScreen


class GUICombatManager:
    """Manages combat with pygame GUI rendering."""
    
    def __init__(self, presenter, hud, game):
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
        
    def start_combat(self, player_char: Player, enemy: Character, tile):
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
        
        # Initialize combat state
        self.running = True
        self.combat_view.combat_log.clear()
        self.combat_view.add_combat_message(f"Combat started with {enemy.name}!")
        
        # Initialize combat state
        self.running = True
        self.combat_view.combat_log.clear()
        self.combat_view.add_combat_message(f"Combat started with {enemy.name}!")
        
        # Initialize battle logger
        boss = "Boss" in str(tile)
        player_initiative = True
        
        # Show initial combat screen with brief transition delay
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        pygame.time.wait(800)  # Brief pause to let player see the transition
        
        # Determine who goes first (using speed + luck modifiers)
        # Encumbered player always loses initiative
        if player_char.encumbered:
            first = enemy
            player_initiative = False
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
        while self.running and player_char.is_alive() and enemy.is_alive() and not fled:
            # Player turn
            if attacker == player_char:
                action_result = self._player_turn(player_char, enemy, available_actions)
                if action_result == "flee":
                    fled = True
                    break
                elif not action_result:  # Closed combat
                    fled = True
                    break
                    
                # Check if enemy died
                if not enemy.is_alive():
                    break
                
                # Switch to enemy turn
                attacker, defender = enemy, player_char
            
            # Enemy turn
            else:
                # Double-check enemy is still alive before their turn
                if not enemy.is_alive():
                    break
                    
                self._enemy_turn(player_char, enemy)
                
                # Check if player died
                if not player_char.is_alive():
                    break
                
                # Switch to player turn
                attacker, defender = player_char, enemy
            
            # Advance turn counter in logger
            self.logger.next_turn()
            
            # Small delay between turns
            pygame.time.wait(300)
            clock.tick(30)
        
        # Combat ended - show result
        return self._handle_combat_end(player_char, enemy, fled)
    
    def _player_turn(self, player_char, enemy, available_actions):
        """
        Handle player's turn with action selection.
        
        Returns:
            str/bool: "flee" if fled, False if cancelled, True if action taken
        """
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
                    self.running = False
                    return False
                
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
    
    def _execute_action(self, action, player_char, enemy):
        """Execute a player action."""
        if action == "Attack":
            # Execute attack using weapon_damage method (same as battle.py)
            message, hit, damage = player_char.weapon_damage(enemy)
            
            # Add the combat message
            self.combat_view.add_combat_message(message.strip())
            
            # Log attack event
            flags = ["hit"] if hit else ["miss"]
            self.logger.log_event(
                event_type="attack",
                actor=player_char,
                target=enemy,
                action="Attack",
                outcome="Hit" if hit else "Miss",
                damage=damage if hit else 0,
                flags=flags
            )
            
            # Show damage flash if hit
            if hit:
                self.combat_view.show_damage_flash(False)
            
        elif action == "Flee":
            success, message = player_char.flee(enemy)
            self.combat_view.add_combat_message(message)
            if success:
                return "flee"
        
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
            # Show spell selection menu
            selected_spell = self._select_spell(player_char, enemy)
            if selected_spell:
                # Cast the spell
                spell_obj = player_char.spellbook['Spells'][selected_spell]
                if player_char.mana.current >= spell_obj.cost:
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
                    return "action_taken"
                else:
                    self.combat_view.add_combat_message("Not enough mana!")
                    return None
            return None  # Cancelled
            
        elif action == "Skills":
            # Show skill selection menu
            selected_skill = self._select_skill(player_char, enemy)
            if selected_skill:
                # Use the skill
                skill_obj = player_char.spellbook['Skills'][selected_skill]
                if player_char.mana.current >= skill_obj.cost:
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
                    return "action_taken"
                else:
                    self.combat_view.add_combat_message("Not enough mana!")
                    return None
            return None  # Cancelled
        
        return "action_taken"
    
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
            pygame.time.wait(1000)
            return None
        
        # Create selection menu
        selected = 0
        while True:
            # Render combat with item menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            self._render_selection_menu(
                "Select Item",
                [f"{name} ({count})" for name, _, count in items],
                selected
            )
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(items)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(items)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return items[selected][1]  # Return the item object
    
    def _select_spell(self, player_char, enemy):
        """Show spell selection menu and return selected spell name."""
        # Filter out passive spells
        spells = [name for name, spell in player_char.spellbook['Spells'].items() 
                  if not getattr(spell, 'passive', False)]
        
        if not spells:
            self.combat_view.add_combat_message("No spells learned!")
            pygame.time.wait(1000)
            return None
        
        selected = 0
        while True:
            # Render combat with spell menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            spell_options = []
            for spell_name in spells:
                spell = player_char.spellbook['Spells'][spell_name]
                cost = spell.cost
                spell_options.append(f"{spell_name} (MP: {cost})")
            
            self._render_selection_menu("Select Spell", spell_options, selected)
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(spells)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(spells)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return spells[selected]  # Return spell name
    
    def _select_skill(self, player_char, enemy):
        """Show skill selection menu and return selected skill name."""
        # Filter out passive skills
        skills = [name for name, skill in player_char.spellbook['Skills'].items()
                  if not getattr(skill, 'passive', False)]
        
        if not skills:
            self.combat_view.add_combat_message("No skills learned!")
            pygame.time.wait(1000)
            return None
        
        selected = 0
        while True:
            # Render combat with skill menu overlay
            self._render_combat_frame(player_char, enemy, [], -1)
            skill_options = []
            for skill_name in skills:
                skill = player_char.spellbook['Skills'][skill_name]
                cost = skill.cost
                skill_options.append(f"{skill_name} (MP: {cost})")
            
            self._render_selection_menu("Select Skill", skill_options, selected)
            pygame.display.flip()
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        return None  # Cancel
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        selected = (selected - 1) % len(skills)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        selected = (selected + 1) % len(skills)
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        return skills[selected]  # Return skill name
    
    def _render_selection_menu(self, title, options, selected):
        """Render a selection menu overlay on combat screen."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.combat_view.combat_width, self.combat_view.combat_height))
        overlay.set_alpha(200)
        overlay.fill((20, 20, 30))
        self.screen.blit(overlay, (0, 0))
        
        # Menu dimensions
        menu_width = 400
        menu_height = min(500, 100 + len(options) * 35)
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
        
        # Options
        font_medium = pygame.font.Font(None, 24)
        option_y = menu_y + 70
        
        for i, option in enumerate(options):
            # Highlight selected option
            if i == selected:
                highlight_rect = pygame.Rect(menu_x + 10, option_y - 3, menu_width - 20, 30)
                pygame.draw.rect(self.screen, (80, 80, 100), highlight_rect)
            
            option_surf = font_medium.render(f"{i+1}. {option}", True, (255, 255, 255))
            self.screen.blit(option_surf, (menu_x + 20, option_y))
            option_y += 35
        
        # Instructions
        font_small = pygame.font.Font(None, 18)
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
        
        # Render current state
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        pygame.time.wait(500)  # Pause before enemy acts
        
        # Enemy attacks using weapon_damage method (same as battle.py)
        message, hit, damage = enemy.weapon_damage(player_char)
        
        # Add the combat message
        self.combat_view.add_combat_message(message.strip())
        
        # Log enemy attack
        flags = ["hit"] if hit else ["miss"]
        self.logger.log_event(
            event_type="attack",
            actor=enemy,
            target=player_char,
            action="Attack",
            outcome="Hit" if hit else "Miss",
            damage=damage if hit else 0,
            flags=flags
        )
        
        # Show damage flash if hit
        if hit:
            self.combat_view.show_damage_flash(True)
        
        # Render updated state
        self._render_combat_frame(player_char, enemy, [], -1)
        pygame.display.flip()
        pygame.time.wait(800)  # Show result
        
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
        if hasattr(self, 'dungeon_renderer') and hasattr(self, 'player_world_dict'):
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
    
    def _handle_combat_end(self, player_char, enemy, fled):
        """Handle end of combat and show results."""
        end_messages = []
        
        if not player_char.is_alive():
            end_messages.append("You have been defeated!")
            
            # Log battle end
            self.logger.end_battle(result="Defeat", winner=enemy.name, boss="Boss" in str(self.current_tile))
            
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            
            # Show defeat message in popup
            from .confirmation_popup import ConfirmationPopup
            popup = ConfirmationPopup(self.presenter, "\n".join(end_messages), show_buttons=False)
            popup.show(background_draw_func=lambda: None)
            return False
        
        elif not enemy.is_alive():
            end_messages.append(f"Victory! {enemy.name} defeated!")
            
            # Log victory
            self.logger.end_battle(result="Victory", winner=player_char.name, boss="Boss" in str(self.current_tile))
            
            # Trigger enemy death special effects (like Behemoth's Meteor)
            if hasattr(enemy, 'special_effects'):
                result = enemy.special_effects(player_char)
                if result:
                    for line in result.strip().split('\n'):
                        if line:
                            end_messages.append(line)
            
            # Handle loot drops (gold, exp, and items)
            tile = getattr(self, 'current_tile', None)
            
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
            
            # Render final combat state
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            
            # Show all end messages in popup
            from .confirmation_popup import ConfirmationPopup
            combat_bg = self.screen.copy()
            popup = ConfirmationPopup(self.presenter, "\n".join(end_messages), show_buttons=False)
            popup.show(background_draw_func=lambda: self.screen.blit(combat_bg, (0, 0)))
            
            # Handle level up screen if needed
            if level_up:
                self.level_up_screen.show_level_up(player_char, self.game)
            
            return True
        
        elif fled:
            end_messages.append("You fled from combat!")
            
            # Log fled battle
            self.logger.end_battle(result="Fled", winner=None, boss="Boss" in str(self.current_tile))
            
            self._render_combat_frame(player_char, enemy, [], -1)
            pygame.display.flip()
            
            # Show flee message in popup
            from .confirmation_popup import ConfirmationPopup
            combat_bg = self.screen.copy()
            popup = ConfirmationPopup(self.presenter, "\n".join(end_messages), show_buttons=False)
            popup.show(background_draw_func=lambda: self.screen.blit(combat_bg, (0, 0)))
            return False
        
        return True

    def _process_status_effects(self, character: Character) -> list[str]:
        """
        Process and tick down status effects for a character.
        Returns list of messages about status effects that are active.
        """
        messages = []
        
        # Process all status effect dictionaries
        effect_dicts = [
            (character.status_effects, "Status"),
            (character.physical_effects, "Physical"),
            (character.stat_effects, "Stat"),
            (character.magic_effects, "Magic")
        ]
        
        for effect_dict, category_name in effect_dicts:
            for effect_name, effect_obj in effect_dict.items():
                if effect_obj.active and effect_obj.duration > 0:
                    # Add message about active effect
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
                        messages.append(f"{character.name}'s {effect_name} wears off.")
        
        return messages
