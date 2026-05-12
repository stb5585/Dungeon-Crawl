"""
This module handles combat between the player and enemies. It includes functions for determining initiative, handling
turns, and executing actions. The BattleManager class manages the flow of combat, while the BattleLogger class records
combat events for later analysis.
"""
from __future__ import annotations

import datetime
import json
from collections import Counter
from dataclasses import asdict, is_dataclass
from pathlib import Path
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

    @staticmethod
    def _serialize_value(value):
        """Convert logger metadata into JSON-friendly primitives."""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, dict):
            return {
                str(key): BattleLogger._serialize_value(val)
                for key, val in value.items()
            }
        if isinstance(value, (list, tuple, set)):
            return [BattleLogger._serialize_value(val) for val in value]
        if hasattr(value, "__dict__"):
            return {
                key: BattleLogger._serialize_value(val)
                for key, val in vars(value).items()
                if not key.startswith("_")
            }
        return str(value)

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
                "attributes": self._serialize_value(player.stats),
                "combat stats": self._serialize_value(player.combat),
                "hp": player.health.current,
                "mp": player.mana.current,
                "resistances": self._serialize_value(player.resistance),
                "dungeon level": player.location_z,
                "initiative": initiative,
            },
            "enemy": {
                "name": enemy.name,
                "type": enemy.enemy_typ,
                "level": self._serialize_value(enemy.level),
                "attributes": self._serialize_value(enemy.stats),
                "combat stats": self._serialize_value(enemy.combat),
                "hp": enemy.health.current,
                "mp": enemy.mana.current,
                "resistances": self._serialize_value(enemy.resistance),
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

    def get_event_type_counts(self) -> dict[str, int]:
        """Return compact event-type counts for logged battle events."""
        return dict(Counter(event["event_type"] for event in self.events))

    def get_flag_counts(self) -> dict[str, int]:
        """Return compact flag counts for logged battle events."""
        flags = Counter()
        for event in self.events:
            flags.update(str(flag) for flag in event.get("flags", ()))
        return dict(flags)

    def get_actor_counts(self) -> dict[str, int]:
        """Return compact event counts by acting character."""
        return dict(Counter(event["actor"] for event in self.events if event.get("actor")))

    def get_target_counts(self) -> dict[str, int]:
        """Return compact event counts by target character."""
        return dict(Counter(event["target"] for event in self.events if event.get("target")))

    def build_summary(self) -> dict:
        """Create a compact battle summary for debugging and analysis."""
        damage_events = [event for event in self.events if isinstance(event.get("damage"), int)]
        total_damage = sum(max(0, event["damage"]) for event in damage_events)

        return {
            "turns": self.turn_counter,
            "event_count": len(self.events),
            "event_types": self.get_event_type_counts(),
            "flag_counts": self.get_flag_counts(),
            "actor_counts": self.get_actor_counts(),
            "target_counts": self.get_target_counts(),
            "total_damage_logged": total_damage,
            "max_damage_logged": max((event["damage"] for event in damage_events), default=0),
            "result": self.metadata.get("result"),
            "winner": self.metadata.get("winner"),
        }

    def export_payload(self) -> dict:
        """Export a structured combat record with metadata, events, and summary."""
        return {
            "metadata": self._serialize_value(self.metadata),
            "events": self._serialize_value(self.events),
            "summary": self.build_summary(),
        }

    def summary_payload(self) -> dict:
        """Export compact combat metadata and summary without raw per-event logs."""
        metadata = self._serialize_value(self.metadata)
        return {
            "metadata": {
                "player": metadata.get("player"),
                "enemy": metadata.get("enemy"),
                "boss": metadata.get("boss"),
                "result": metadata.get("result"),
                "winner": metadata.get("winner"),
            },
            "summary": self.build_summary(),
        }

    def export_json(self, *, indent: int = 2) -> str:
        """Export the structured combat record as JSON text."""
        return json.dumps(self.export_payload(), indent=indent, sort_keys=True)

    def export_json_file(self, path: str | Path, *, indent: int = 2) -> Path:
        """Write the structured combat record as UTF-8 JSON and return its path."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.export_json(indent=indent), encoding="utf-8")
        return output_path

    def export(self) -> list:
        """
        Exports the logged events for analysis or storage.
        Returns:
            list: A list of dictionaries containing the logged events.
        """
        return list(self.events)
