"""
Enhanced Battle Manager with Action Queue Integration

This module provides an enhanced version of BattleManager that uses the action queue system
while maintaining backward compatibility with the existing combat flow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Import BattleManager from battle.py (renamed to avoid package conflict)
from battle import BattleManager as BaseBattleManager

# Import from the combat/ package
from combat.action_queue import ActionQueue, ActionType, ActionPriority, ScheduledAction

if TYPE_CHECKING:
    from character import Character
    from game import Game


class EnhancedBattleManager(BaseBattleManager):
    """
    Enhanced BattleManager that uses ActionQueue for sophisticated turn resolution.
    
    Key improvements:
    - Priority-based action execution
    - Speed-based turn order within rounds
    - Support for delayed/charging actions
    - Enemy AI action stacks
    - Telegraph system for Seeker/Inquisitor classes
    """
    
    def __init__(self, game: Game, enemy: Character, logger=None, use_queue: bool = True):
        """
        Args:
            game: The game instance
            enemy: The enemy character
            logger: Optional battle logger
            use_queue: If True, use action queue system. If False, use traditional turn-based
        """
        super().__init__(game, enemy, logger)
        self.use_queue = use_queue
        
        if self.use_queue:
            self.action_queue = ActionQueue()
            self.pending_actions: dict[Character, ScheduledAction] = {}
            self.charging_actions: dict[Character, tuple[str, int]] = {}  # char -> (action_name, turns_left)
    
    def process_turn(self) -> None:
        """
        Enhanced turn processing with action queue support.
        Falls back to traditional behavior if use_queue=False.
        """
        if not self.use_queue:
            # Use traditional turn-based logic
            super().process_turn()
            return
        
        # Action queue logic
        self.before_turn()
        
        # Check for charging actions
        self._update_charging_actions()
        
        # Get actions for this round
        if not self.action_queue.has_ready_actions():
            # Schedule new actions
            self._schedule_player_action()
            self._schedule_enemy_action()
            if self.summon_active and self.summon.is_alive():
                self._schedule_summon_action()
        
        # Resolve actions in priority/speed order
        while self.action_queue.has_ready_actions():
            action = self.action_queue.get_next_action()
            if action:
                self._execute_scheduled_action(action)
                
                # Check if battle ended
                if not self.player_char.is_alive() or not self.enemy.is_alive() or self.flee:
                    break
        
        self.after_turn()
        self.action_queue.next_round()
    
    def _update_charging_actions(self) -> None:
        """Update status of charging/delayed actions and show telegraphs."""
        completed = []
        
        for char, (action_name, turns_left) in self.charging_actions.items():
            if turns_left <= 1:
                # Action ready to execute next
                completed.append(char)
            else:
                # Still charging
                self.charging_actions[char] = (action_name, turns_left - 1)
                
                # Show telegraph message
                if char == self.enemy:
                    telegraph_msg = self._get_telegraph_message(action_name)
                    self.print_text(telegraph_msg)
        
        # Remove completed charges
        for char in completed:
            del self.charging_actions[char]
    
    def _get_telegraph_message(self, action_name: str) -> str:
        """
        Get telegraph message for enemy charging action.
        
        Seeker/Inquisitor classes see specific action, others see generic message.
        """
        # Check if player has sight/knowledge ability
        has_foresight = self.player_char.cls.name in ["Seeker", "Inquisitor"]
        
        if has_foresight:
            return f"{self.enemy.name} is preparing {action_name}!"
        else:
            return f"{self.enemy.name} is preparing something..."
    
    def _schedule_player_action(self) -> None:
        """Schedule the player's chosen action."""
        # Show charging status if applicable
        if self.player_char in self.charging_actions:
            action_name, turns_left = self.charging_actions[self.player_char]
            self.print_text(f"Continuing to charge {action_name}... ({turns_left} turns remaining)")
            return
        
        # Process status effects
        effects_text = self.player_char.effects()
        if effects_text:
            self.print_text(effects_text)
        
        # Check if player can act
        active, text = self.player_char.check_active()
        if not active:
            self.print_text(text)
            # Schedule a "do nothing" action
            self.action_queue.schedule(
                actor=self.player_char,
                action_type=ActionType.SPECIAL,
                callback=lambda **kwargs: None,
                priority=ActionPriority.NORMAL
            )
            return
        
        # Get player's choice
        choice = None
        action = None
        
        if self.player_char.status_effects["Berserk"].active:
            action = "Attack"
        elif self.player_char.class_effects["Jump"].active:
            action = "Use Skill"
            choice = [x for x in self.player_char.spellbook['Skills'] if "Jump" in x][0]
            self.player_char.class_effects["Jump"].active = False
        else:
            while True:
                choice = False
                action = self.battle_ui.navigate_menu()
                if action in ["Cast Spell", "Use Skill", "Use Item"]:
                    self.battle_popup.update_options(action, tile=self.tile)
                    choice = self.battle_popup.navigate_popup().split('  ')[0]
                elif action == "Summon":
                    self.battle_popup.update_options("Summon", options=list(self.player_char.summons))
                    choice = self.battle_popup.navigate_popup()
                elif action == "Untransform":
                    self.print_text(self.player_char.transform(back=True))
                elif action == "Transform":
                    self.print_text(self.player_char.transform())
                if action == "Attack" or (choice and choice != "Go Back"):
                    break
                self.render_screen()
        
        # Determine action properties
        priority, delay, action_type = self._get_action_properties(action, choice)
        
        # Schedule the action
        self.action_queue.schedule(
            actor=self.player_char,
            action_type=action_type,
            callback=self._create_action_callback(action, choice),
            target=self.enemy,
            priority=priority,
            delay=delay,
            action=action,
            choice=choice
        )
        
        # Track charging actions
        if delay > 0:
            ability_name = choice if choice else action
            self.charging_actions[self.player_char] = (ability_name, delay)
            self.print_text(f"{self.player_char.name} begins charging {ability_name}...")
    
    def _schedule_enemy_action(self) -> None:
        """Schedule the enemy's action using their AI."""
        # Check for charging
        if self.enemy in self.charging_actions:
            return
        
        # Process status effects
        effects_text = self.enemy.effects()
        if effects_text:
            self.print_text(effects_text)
        
        # Check if enemy can act
        active, text = self.enemy.check_active()
        if not active:
            self.print_text(text)
            self.action_queue.schedule(
                actor=self.enemy,
                action_type=ActionType.SPECIAL,
                callback=lambda **kwargs: None,
                priority=ActionPriority.NORMAL
            )
            return
        
        # Get enemy's chosen action
        action, choice = self.enemy.options(self.player_char, self.available_actions, self.tile)
        
        # Determine action properties
        priority, delay, action_type = self._get_action_properties(action, choice)
        
        # Schedule the action
        self.action_queue.schedule(
            actor=self.enemy,
            action_type=action_type,
            callback=self._create_action_callback(action, choice),
            target=self.player_char,
            priority=priority,
            delay=delay,
            action=action,
            choice=choice
        )
        
        # Track charging actions
        if delay > 0:
            ability_name = choice if choice else action
            self.charging_actions[self.enemy] = (ability_name, delay)
    
    def _schedule_summon_action(self) -> None:
        """Schedule summon/companion action."""
        if not self.summon or not self.summon.is_alive():
            return
        
        # Summons act with NORMAL priority
        # Simple AI: always attack
        self.action_queue.schedule(
            actor=self.summon,
            action_type=ActionType.ATTACK,
            callback=self._create_action_callback("Attack", None),
            target=self.enemy,
            priority=ActionPriority.NORMAL
        )
    
    def _get_action_properties(self, action: str, choice: str | None) -> tuple:
        """
        Determine priority, delay, and type for an action.
        
        Returns:
            (priority, delay, action_type)
        """
        action_type = ActionType.SPECIAL
        priority = ActionPriority.NORMAL
        delay = 0
        
        if action == "Attack":
            action_type = ActionType.ATTACK
            priority = ActionPriority.NORMAL
        elif action == "Cast Spell":
            action_type = ActionType.SPELL
            priority = ActionPriority.NORMAL
            # Check if spell requires charging
            if choice and choice in self.player_char.spellbook.get('Spells', {}):
                spell = self.player_char.spellbook['Spells'][choice]
                # High-cost spells might charge
                if hasattr(spell, 'cost') and spell.cost > 20:
                    delay = 1  # 1-turn charge for expensive spells
        elif action == "Use Skill":
            action_type = ActionType.SKILL
            # Quick skills get HIGH priority
            if choice and "Quick" in str(choice):
                priority = ActionPriority.HIGH
            else:
                priority = ActionPriority.NORMAL
        elif action == "Use Item":
            action_type = ActionType.ITEM
            priority = ActionPriority.NORMAL
        elif action == "Flee":
            action_type = ActionType.FLEE
            priority = ActionPriority.HIGH  # Fleeing is fast
        elif action == "Defend":
            action_type = ActionType.DEFEND
            priority = ActionPriority.HIGH  # Defending is reactive
        
        return priority, delay, action_type
    
    def _create_action_callback(self, action: str, choice: str | None):
        """Create a callback function for executing an action."""
        def callback(**kwargs):
            # Execute the action using existing execute_action logic
            self.attacker = kwargs.get('actor')
            self.defender = kwargs.get('target')
            self.execute_action(action, choice=choice)
        
        return callback
    
    def _execute_scheduled_action(self, scheduled_action: ScheduledAction) -> None:
        """Execute a scheduled action from the queue."""
        # Set attacker/defender for compatibility with existing methods
        self.attacker = scheduled_action.actor
        
        # Determine target (might be in params or default to opposite side)
        if scheduled_action.target:
            self.defender = scheduled_action.target
        else:
            if self.attacker == self.player_char or self.attacker == self.summon:
                self.defender = self.enemy
            else:
                self.defender = self.player_char
        
        # Execute the callback
        scheduled_action.callback(
            actor=self.attacker,
            target=self.defender,
            **scheduled_action.params
        )
