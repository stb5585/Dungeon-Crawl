"""Fixed-order encounter actor scheduling."""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..character import Character
    from .encounter import CombatEncounter


PLAYER_ACTOR_ID = "player"


def initiative_rating(actor: Character, opponent: Character) -> float:
    """Return the existing speed-plus-luck initiative weight."""
    try:
        from ..classes import pathfinder

        chronology = pathfinder.chronology_initiative_bonus(actor)
    except Exception:
        chronology = 0
    return max(
        0.0,
        float(actor.check_mod("speed", enemy=opponent))
        + float(actor.check_mod("luck", enemy=opponent, luck_factor=10))
        + chronology,
    )


def build_actor_order(
    player: Character,
    encounter: CombatEncounter,
    *,
    rng: Any = random,
) -> tuple[str, ...]:
    """Roll a tiered weighted actor order once for the encounter."""
    living = encounter.living_members
    if not living:
        return (PLAYER_ACTOR_ID,)

    enemy_by_id = {member.combatant_id: member for member in living}
    tiers: dict[int, list[str]] = {}
    forced_last = bool(
        getattr(player, "dwarf_hangover_steps", 0) > 0
        or getattr(player, "encumbered", False)
    )
    player_surprise = bool(
        not forced_last
        and getattr(player, "invisible", False)
        and not any(getattr(member.enemy, "sight", False) for member in living)
    )
    if (
        player_surprise
        and getattr(getattr(player, "cls", None), "name", None) == "Shadowcaster"
        and getattr(player, "power_up", False)
    ):
        player.class_effects["Power Up"].active = True
        player.class_effects["Power Up"].duration = 1
    if forced_last:
        player_tier = 2
    elif player_surprise:
        player_tier = 0
    else:
        player_tier = 2
    tiers.setdefault(player_tier, []).append(PLAYER_ACTOR_ID)

    for member in living:
        unseen = bool(
            getattr(member.enemy, "invisible", False)
            and not getattr(player, "sight", False)
        )
        enemy_tier = 1 if unseen else 2
        if forced_last:
            enemy_tier = 0 if unseen else 1
        tiers.setdefault(enemy_tier, []).append(member.combatant_id)

    order: list[str] = []
    for tier in sorted(tiers):
        remaining = list(tiers[tier])
        while remaining:
            weights = []
            for actor_id in remaining:
                if actor_id == PLAYER_ACTOR_ID:
                    opponent = living[0].enemy
                    weights.append(initiative_rating(player, opponent))
                else:
                    enemy = enemy_by_id[actor_id].enemy
                    weights.append(initiative_rating(enemy, player))
            if sum(weights) <= 0:
                selected = remaining[0]
            else:
                selected = rng.choices(remaining, weights=weights, k=1)[0]
            order.append(selected)
            remaining.remove(selected)
    return tuple(order)


@dataclass
class ActorCycle:
    """Mutable cursor over a fixed encounter actor order."""

    order: tuple[str, ...]
    cursor: int = 0
    round_number: int = 1
    total_started_actor_turns: int = 0

    @property
    def current_actor_id(self) -> str:
        """Return the scheduled actor at the cursor."""
        return self.order[self.cursor]

    def start_current_turn(self) -> int:
        """Count and return the newly started actor-turn ID."""
        self.total_started_actor_turns += 1
        return self.total_started_actor_turns

    def add_actor(self, actor_id: str) -> None:
        """Append a reinforcement to the current round's fixed actor cycle."""
        if actor_id not in self.order:
            self.order = (*self.order, actor_id)

    def advance(self, valid_actor_ids: set[str]) -> tuple[bool, str]:
        """Advance to the next valid actor, returning round transition state."""
        if not self.order:
            raise RuntimeError("Actor cycle has no scheduled actors.")
        wrapped = False
        for _ in range(len(self.order)):
            self.cursor += 1
            if self.cursor >= len(self.order):
                self.cursor = 0
                self.round_number += 1
                wrapped = True
            actor_id = self.current_actor_id
            if actor_id in valid_actor_ids:
                return wrapped, actor_id
        return wrapped, self.current_actor_id
