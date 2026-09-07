from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .targeting import TargetScope

if TYPE_CHECKING:
    from typing import Any

    from src.core.character import Character


@dataclass
class CombatResult:
    action: str
    actor: Character | None = None
    target: Character | None = None
    hit: bool | None = None
    crit: float | None = None
    dodge: bool | None = None
    block: bool | None = None
    block_amount: int | None = None
    damage: int | None = None
    healing: int | None = None
    effects_applied: dict[str, list[Any]] = field(
        default_factory=lambda: {"Status": [], "Physical": [], "Stat": [], "Magic": [], "Class": []}
    )
    extra: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    actor_id: str | None = None
    target_id: str | None = None

    def __str__(self) -> str:
        """Return the display message, enabling transparent use with str()."""
        return self.message

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action,
            "actor": self.actor.name if self.actor else None,
            "target": self.target.name if self.target else None,
            "hit": self.hit,
            "crit": self.crit,
            "dodge": self.dodge,
            "block": self.block,
            "block_amount": self.block_amount,
            "damage": self.damage,
            "healing": self.healing,
            "effects_applied": deepcopy(self.effects_applied),
            "extra": deepcopy(self.extra),
            "message": self.message,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
        }


@dataclass
class CombatResultGroup:
    action: str = ""
    actor_id: str | None = None
    target_scope: TargetScope = TargetScope.NONE
    target_ids: tuple[str, ...] = ()
    results: list[CombatResult] = field(default_factory=list)
    message: str = ""

    def add(self, result: CombatResult) -> None:
        self.results.append(result)
        self.message += result.message

    def __getitem__(self, index: int) -> CombatResult:
        """Make CombatResultGroup subscriptable for backward compatibility."""
        return self.results[index]

    def __len__(self) -> int:
        """Return the number of results in the group."""
        return len(self.results)

    def summary_dict(self) -> dict[str, object]:
        """Return JSON-friendly group metadata and ordered results."""
        return {
            "action": self.action,
            "actor_id": self.actor_id,
            "target_scope": self.target_scope.value,
            "target_ids": list(self.target_ids),
            "message": self.message,
            "results": [result.to_dict() for result in self.results],
        }

    def to_dict(self) -> list[dict[str, object]]:
        """Preserve the legacy ordered-result serialization."""
        return [result.to_dict() for result in self.results]
