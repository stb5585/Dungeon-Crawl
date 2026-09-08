"""Validated action resolution for the battle engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import (
    ActionIntent,
    ActionResult,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class TurnResolutionMixin:
    """Resolve validated intents and their combat side effects."""

    def execute_intent(
        self,
        intent: ActionIntent,
        *,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """Execute an intent and report terminal resolutions produced by it."""
        mana_before = max(0, int(getattr(self.attacker.mana, "current", 0) or 0))
        result = self._execute_intent(
            intent,
            slot_machine_callback=slot_machine_callback,
        )
        if result.committed:
            barbs = getattr(self.attacker, "mana_barbs", None)
            if isinstance(barbs, dict) and int(barbs.get("turns", 0) or 0) > 0:
                mana_after = max(
                    0,
                    int(getattr(self.attacker.mana, "current", 0) or 0),
                )
                spent = max(0, mana_before - mana_after)
                if spent:
                    self.attacker.health.current -= spent
                    result.message += (
                        f"Mana Barbs deal {spent} damage back to {self.attacker.name}.\n"
                    )
                barbs["turns"] = int(barbs["turns"]) - 1
                if barbs["turns"] <= 0:
                    self.attacker.mana_barbs = None
            result.new_resolutions = self._consume_new_resolution_records()
        return result

    def _tunneled_action_blocked(self, action: str, choice: str | None) -> bool:
        if not getattr(self.attacker, "tunnel", False):
            return False
        if action in {"Recall", "Support", "Nothing", "Cancelled"}:
            return False
        if action == "Use Skill" and choice == "Surface":
            return False
        return action in {"Attack", "Cast Spell", "Use Skill"}

    @staticmethod
    @staticmethod
    def _debuff_state_snapshot(actor, ability_name: str | None, target) -> dict | None:
        rules = getattr(actor, "_DEBUFF_REAPPLY_RULES", None)
        if not ability_name or not isinstance(rules, dict) or target is None:
            return None
        rule = rules.get(ability_name)
        if not rule:
            return None

        snapshot = {"rule": rule}
        status_name = rule.get("status")
        if status_name:
            effect = getattr(target, "status_effects", {}).get(status_name)
            snapshot["status"] = bool(getattr(effect, "active", False))

        physical_name = rule.get("physical")
        if physical_name:
            effect = getattr(target, "physical_effects", {}).get(physical_name)
            snapshot["physical"] = bool(getattr(effect, "active", False))

        stat_all = rule.get("stat_all")
        if stat_all:
            stat_effects = getattr(target, "stat_effects", {})
            snapshot["stats"] = {
                stat_name: bool(getattr(stat_effects.get(stat_name), "active", False))
                for stat_name in stat_all
            }
        return snapshot

    @staticmethod
    @staticmethod
    def _debuff_snapshot_gained_effect(snapshot: dict | None, target) -> bool:
        if not snapshot or target is None:
            return True
        rule = snapshot.get("rule", {})

        status_name = rule.get("status")
        if status_name:
            effect = getattr(target, "status_effects", {}).get(status_name)
            return bool(getattr(effect, "active", False)) and not snapshot.get("status", False)

        physical_name = rule.get("physical")
        if physical_name:
            effect = getattr(target, "physical_effects", {}).get(physical_name)
            return bool(getattr(effect, "active", False)) and not snapshot.get("physical", False)

        stat_all = rule.get("stat_all")
        if stat_all:
            before = snapshot.get("stats", {})
            stat_effects = getattr(target, "stat_effects", {})
            return any(
                bool(getattr(stat_effects.get(stat_name), "active", False))
                and not before.get(stat_name, False)
                for stat_name in stat_all
            )
        return True

    def _record_failed_enemy_debuff(
        self, actor, ability_name: str | None, target, snapshot: dict | None
    ) -> None:
        if snapshot is None or self._member_for_character(actor) is None:
            return
        if self._debuff_snapshot_gained_effect(snapshot, target):
            return
        record_failure = getattr(actor, "record_debuff_failure", None)
        if callable(record_failure):
            record_failure(str(ability_name), turns=2)
