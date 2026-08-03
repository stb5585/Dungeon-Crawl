"""Runtime encounter roster and enemy-resolution models."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from ..character import Character


class EnemyResolution(str, Enum):
    """Terminal ways an enemy can leave an encounter."""

    DEFEATED = "defeated"
    MERCY = "mercy"
    TAMED = "tamed"
    EJECTED = "ejected"
    ESCAPED = "escaped"


@dataclass(frozen=True)
class EnemyResolutionRecord:
    """Immutable record of one enemy's terminal encounter resolution."""

    combatant_id: str
    resolution: EnemyResolution
    cause: str | None = None


@dataclass
class EncounterEnemy:
    """One enemy in authored encounter order with stable runtime identity."""

    enemy: Character
    combatant_id: str
    slot: int
    canonical_name: str
    display_label: str
    resolution: EnemyResolution | None = None
    resolution_cause: str | None = None

    @property
    def is_living_hostile(self) -> bool:
        """Return whether this unresolved member can still participate."""
        return self.resolution is None and self.enemy.is_alive()

    def summary(self) -> dict[str, object]:
        """Return JSON-friendly lifecycle metadata for this member."""
        return {
            "combatant_id": self.combatant_id,
            "canonical_name": self.canonical_name,
            "display_label": self.display_label,
            "slot": self.slot,
            "resolution": self.resolution.value if self.resolution else None,
            "cause": self.resolution_cause,
        }


class CombatEncounter:
    """Runtime-only ordered hostile roster and resolution ledger."""

    def __init__(
        self,
        members: Sequence[EncounterEnemy],
        *,
        encounter_id: str | None = None,
    ):
        if not members:
            raise ValueError("A combat encounter requires at least one enemy.")

        self.encounter_id = encounter_id or f"enc-{uuid4().hex}"
        self.members = list(members)
        expected_slots = list(range(len(self.members)))
        actual_slots = [member.slot for member in self.members]
        if actual_slots != expected_slots:
            raise ValueError("Encounter enemy slots must be contiguous and in authored order.")

        combatant_ids = [member.combatant_id for member in self.members]
        if len(combatant_ids) != len(set(combatant_ids)):
            raise ValueError("Encounter combatant IDs must be unique.")

        self._resolution_ledger: list[EnemyResolutionRecord] = []
        for member in self.members:
            if member.resolution is not None:
                if not isinstance(member.resolution, EnemyResolution):
                    raise TypeError("Member resolution must be an EnemyResolution value.")
                self._resolution_ledger.append(
                    EnemyResolutionRecord(
                        member.combatant_id,
                        member.resolution,
                        member.resolution_cause,
                    )
                )

    @classmethod
    def from_enemies(
        cls,
        enemies: Sequence[Character],
        *,
        encounter_id: str | None = None,
        combatant_ids: Sequence[str] | None = None,
    ) -> CombatEncounter:
        """Build an encounter from enemies in authored slot order."""
        from ..enemies.identity import defeat_credit_name, remember_defeat_identity

        if not enemies:
            raise ValueError("A combat encounter requires at least one enemy.")
        if combatant_ids is not None and len(combatant_ids) != len(enemies):
            raise ValueError("A combatant ID must be supplied for every encounter enemy.")

        resolved_encounter_id = encounter_id or f"enc-{uuid4().hex}"
        canonical_names = []
        for enemy in enemies:
            remember_defeat_identity(enemy)
            canonical_names.append(defeat_credit_name(enemy) or enemy.__class__.__name__)

        name_counts = Counter(canonical_names)
        name_indexes: Counter[str] = Counter()
        members = []
        for slot, (enemy, canonical_name) in enumerate(zip(enemies, canonical_names)):
            name_indexes[canonical_name] += 1
            display_label = canonical_name
            if name_counts[canonical_name] > 1:
                suffix = cls._alpha_suffix(name_indexes[canonical_name] - 1)
                display_label = f"{canonical_name} {suffix}"
            combatant_id = (
                combatant_ids[slot]
                if combatant_ids is not None
                else f"{resolved_encounter_id}:enemy:{slot}"
            )
            members.append(
                EncounterEnemy(
                    enemy=enemy,
                    combatant_id=combatant_id,
                    slot=slot,
                    canonical_name=canonical_name,
                    display_label=display_label,
                )
            )
        return cls(members, encounter_id=resolved_encounter_id)

    @classmethod
    def singleton(
        cls,
        enemy: Character,
        *,
        encounter_id: str | None = None,
        combatant_id: str | None = None,
    ) -> CombatEncounter:
        """Build a one-enemy encounter for legacy combat callers."""
        ids = [combatant_id] if combatant_id is not None else None
        return cls.from_enemies(
            [enemy],
            encounter_id=encounter_id,
            combatant_ids=ids,
        )

    @staticmethod
    def _alpha_suffix(index: int) -> str:
        """Return a stable spreadsheet-style alphabetic suffix."""
        value = index + 1
        suffix = ""
        while value:
            value, remainder = divmod(value - 1, 26)
            suffix = chr(ord("A") + remainder) + suffix
        return suffix

    @property
    def primary_member(self) -> EncounterEnemy:
        """Return the first authored encounter member."""
        return self.members[0]

    @property
    def primary_enemy(self) -> Character:
        """Return the first authored enemy object."""
        return self.primary_member.enemy

    @property
    def living_members(self) -> list[EncounterEnemy]:
        """Return unresolved living hostiles in authored order."""
        return [member for member in self.members if member.is_living_hostile]

    @property
    def resolution_ledger(self) -> tuple[EnemyResolutionRecord, ...]:
        """Return immutable ordered resolution records."""
        return tuple(self._resolution_ledger)

    @property
    def victory_ready(self) -> bool:
        """Return whether no unresolved living hostile remains."""
        return not self.living_members

    def member_by_id(self, combatant_id: str) -> EncounterEnemy:
        """Return a member by stable combatant ID.

        Raises:
            KeyError: If the combatant ID is not part of this encounter.
        """
        for member in self.members:
            if member.combatant_id == combatant_id:
                return member
        raise KeyError(combatant_id)

    def resolve_enemy(
        self,
        combatant_id: str,
        resolution: EnemyResolution,
        *,
        cause: str | None = None,
    ) -> EnemyResolutionRecord:
        """Resolve one member exactly once and append its ledger record."""
        member = self.member_by_id(combatant_id)
        if member.resolution is not None:
            raise ValueError(f"Combatant {combatant_id!r} has already been resolved.")
        if not isinstance(resolution, EnemyResolution):
            raise TypeError("resolution must be an EnemyResolution value.")

        member.resolution = resolution
        member.resolution_cause = cause
        record = EnemyResolutionRecord(combatant_id, resolution, cause)
        self._resolution_ledger.append(record)
        return record

    def roster_summary(self) -> list[dict[str, object]]:
        """Return authored-order lifecycle summaries for every member."""
        return [member.summary() for member in self.members]

    def clear_resolutions(self) -> None:
        """Discard partial resolution progress after flee or player defeat."""
        self._resolution_ledger.clear()
        for member in self.members:
            member.resolution = None
            member.resolution_cause = None
