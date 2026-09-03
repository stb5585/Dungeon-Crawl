"""Data-driven movement spell implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character
    from src.core.effects.base import Effect


def _get_movement_spell_class():
    from src.core.abilities import MovementSpell
    return MovementSpell


class DataDrivenMovementSpell(_get_movement_spell_class()):
    """
    Data-driven out-of-combat movement spell.

    Movement spells define ``cast_out()`` (not ``cast()``) and operate
    on the game/player world-state rather than in the battle pipeline.
    Two movement_types are supported:

    * ``sanctuary`` — deduct mana, full heal, call ``user.to_town()``.
    * ``teleport``  — present Set / Teleport choice via
      ``selection_callback``, then store or restore coordinates.

    Used by: Sanctuary, Teleport.
    """

    def __init__(
        self,
        name: str,
        description: str,
        cost: int,
        movement_type: str = "sanctuary",
        combat: bool = True,
        effects: list[Effect] | None = None,
        notes: str | None = None,
    ):
        super().__init__(name, description, cost)
        self._movement_type = movement_type
        self.combat = combat
        self._effects: list[Effect] = effects or []
        self._notes = notes

    # ------------------------------------------------------------------
    # cast_out - the primary entry point for movement spells
    # ------------------------------------------------------------------
    def cast_out(
        self,
        user: Character | None = None,
        selection_callback: Any | None = None,
        game: Any | None = None,
    ) -> str:
        """
        Dispatch to the appropriate movement behaviour.

        **Sanctuary** callers pass ``user`` (the Character).
        **Teleport** callers pass ``selection_callback`` and ``game``.
        Legacy callers may pass ``(game)`` as a single positional argument, so
        the compatibility path accepts that flexibly.
        """
        if self._movement_type == "sanctuary":
            return self._cast_sanctuary(user)
        elif self._movement_type == "teleport":
            return self._cast_teleport(selection_callback, game)
        return f"{self.name} has no effect.\n"

    # ------------------------------------------------------------------
    # Sanctuary behaviour
    # ------------------------------------------------------------------
    def _cast_sanctuary(self, user: Character) -> str:
        from src.core.classes import promotion_kits

        cost, route_message = promotion_kits.wayfinding_cost(
            user,
            self.cost,
            mapping_progress=promotion_kits.level_mapping_progress(user),
        )
        user.mana.current -= cost
        user.health.current = user.health.max
        user.mana.current = user.mana.max
        user.to_town()
        return route_message + (
            f"{user.name} casts Sanctuary and is transported back to "
            f"town.\n"
        )

    # ------------------------------------------------------------------
    # Teleport behaviour
    # ------------------------------------------------------------------
    def _cast_teleport(
        self,
        selection_callback: Any | None = None,
        game: Any | None = None,
    ) -> str:
        import random as _random

        teleport_message = (
            "Do you want to set your location or teleport to the "
            "previous location?"
        )
        options = ["Set", "Teleport"]

        if selection_callback is not None:
            option_index = selection_callback(teleport_message, options)
        else:
            option_index = _random.randint(0, len(options) - 1)

        if options[option_index] == "Set":
            cast_message = (
                f"This location has been set for teleport by "
                f"{game.player_char.name}.\n"
            )
            game.player_char.teleport = (
                game.player_char.location_x,
                game.player_char.location_y,
                game.player_char.location_z,
            )
        else:
            if game is None or getattr(game, "player_char", None) is None:
                return "Teleport cannot find a traveler to guide.\n"
            if not getattr(game.player_char, "teleport", None):
                return "Teleport has no previously marked destination.\n"
            cast_message = (
                f"{game.player_char.name} teleports to set location.\n"
            )
            from src.core.classes import promotion_kits

            cost, route_message = promotion_kits.wayfinding_cost(
                game.player_char,
                self.cost,
                mapping_progress=promotion_kits.level_mapping_progress(game.player_char),
            )
            if game.player_char.mana.current < cost:
                return f"{game.player_char.name} does not have enough mana to teleport.\n"
            game.player_char.mana.current -= cost
            (
                game.player_char.location_x,
                game.player_char.location_y,
                game.player_char.location_z,
            ) = game.player_char.teleport

            cast_message = route_message + cast_message

        return cast_message
