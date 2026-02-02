"""
This module handles combat between the player and enemies. It includes functions for determining initiative, handling
turns, and executing actions. The BattleManager class manages the flow of combat, while the BattleLogger class records
combat events for later analysis.
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..enemies import Enemy
    from ..character import Character
    from ..player import Player


class BattleLogger:
    def __init__(self):
        self.events = []
        self.metadata = {}
        self.turn_counter = 0

    def start_battle(self, player: Player, enemy: Enemy, initiative: bool, boss: bool) -> None:
        """
        Initializes the battle logger with metadata about the battle.
        Args:
            player: The player character.
            enemy: The enemy character.
        """
        self.metadata = {
            "start_time": datetime.datetime.now().isoformat(),
            "player": {
                "name": player.name,
                "cls": player.cls.name,
                "level": player.level.level,
                "pro level": player.level.pro_level,
                "attributes": player.stats,
                "combat stats": player.combat,
                "hp": player.health.current,
                "mp": player.mana.current,
                "resistances": player.resistance,
                "dungeon level": player.location_z,
                "initiative": initiative,
            },
            "enemy": {
                "name": enemy.name,
                "type": enemy.enemy_typ,
                "level": enemy.level,
                "attributes": enemy.stats,
                "combat stats": enemy.combat,
                "hp": enemy.health.current,
                "mp": enemy.mana.current,
                "resistances": enemy.resistance,
                "boss": boss,
            }
        }

    def log_event(
            self,
            event_type: str,
            actor: Character,
            target: Character=None,
            action: str=None,
            outcome: str=None,
            damage: int=None,
            flags: list=None,
            status_changes: dict=None,
            notes: str=None,
            ) -> None:
        """
        Logs a combat event with details about the action taken.
        Args:
            event_type: The type of event (e.g., "attack", "spell", "item").
            actor: The character performing the action.
            target: The character being targeted (if applicable).
            action: The action taken (e.g., "attack", "spell", "item").
            outcome: The outcome of the action.
            damage: The amount of damage dealt (if applicable).
            flags: Any special flags or conditions associated with the event.
                Example: ["critical", "miss", "dodge"]
            status_changes: Any changes to status effects or conditions.
            notes: Additional notes about the event.
        """
        event = {
            "turn": self.turn_counter,
            "event_type": event_type,
            "actor": actor.name if actor else None,
            "target": target.name if target else None,
            "action": action,
            "outcome": outcome,
            "damage": damage,
            "flags": flags or [],
            "status_changes": status_changes or {},
            "notes": notes,
            "actor_health": actor.health.current / actor.health.max if actor else None,
            "actor_mana": actor.mana.current / actor.mana.max if actor else None,
            "target_health": target.health.current / target.health.max if target else None,
            "target_mana": target.mana.current / target.mana.max if target else None,
        }
        self.events.append(event)

    def next_turn(self) -> None:
        self.turn_counter += 1

    def end_battle(self, result: str, winner: str | None, boss: bool) -> None:
        self.metadata.update({
            "result": result,
            "winner": winner,
            "boss": boss,
            "turns": self.turn_counter,
            "end_time": datetime.datetime.now().isoformat(),
        })

    def export(self) -> list:
        """
        Exports the logged events for analysis or storage.
        Returns:
            list: A list of dictionaries containing the logged events.
        """
        # This could be extended to save to a file or database
        # For now, we just return the events
        # as a list of dictionaries
        # Example: [{"event": "attack", "actor": "Player", "target": "Enemy", "details": "Hit for 10 damage"}]
        # This is a placeholder for actual export logic
        # You could save to a JSON file or a database here
        return self.events
