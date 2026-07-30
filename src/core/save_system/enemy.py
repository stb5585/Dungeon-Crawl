"""Enemy state serialization."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import enemies

if TYPE_CHECKING:
    from typing import Any


class EnemyStateSerializer:
    """Serializes/deserializes enemy state (for bosses and key enemies)."""

    @staticmethod
    def serialize(enemy) -> dict[str, Any]:
        """Convert enemy to data dictionary."""
        if not enemy:
            return None

        # Handle case where enemy is a class instead of an instance
        if isinstance(enemy, type):
            # It's a class, not an instance - just return the class name
            return {
                'name': enemy.__name__,
                'class_type': enemy.__name__,
                'is_class': True,
            }

        # It's an instance
        return {
            'name': getattr(enemy, 'name', 'Unknown'),
            'class_type': enemy.__class__.__name__,
            'is_class': False,
            'health': {
                'max': getattr(enemy.health, 'max', 100) if hasattr(enemy, 'health') else 100,
                'current': getattr(enemy.health, 'current', 100) if hasattr(enemy, 'health') else 100,
            },
            'mana': {
                'max': getattr(enemy.mana, 'max', 0) if hasattr(enemy, 'mana') else 0,
                'current': getattr(enemy.mana, 'current', 0) if hasattr(enemy, 'mana') else 0,
            },
            'alive': enemy.is_alive() if hasattr(enemy, 'is_alive') else True,
        }

    @staticmethod
    def deserialize(enemy_data: dict):
        """Reconstruct enemy from data dictionary."""
        if not enemy_data:
            return None

        enemy_class_name = enemy_data.get('class_type')

        # Get the enemy class from enemies module
        enemy_class = getattr(enemies, enemy_class_name, None)
        if not enemy_class:
            return None

        # If it was stored as a class, return the class
        if enemy_data.get('is_class'):
            return enemy_class

        # Create instance
        enemy = enemy_class()

        # Restore health/mana if present
        if 'health' in enemy_data and hasattr(enemy, 'health'):
            enemy.health.max = enemy_data['health']['max']
            enemy.health.current = enemy_data['health']['current']

        if 'mana' in enemy_data and hasattr(enemy, 'mana'):
            enemy.mana.max = enemy_data['mana']['max']
            enemy.mana.current = enemy_data['mana']['current']

        return enemy
