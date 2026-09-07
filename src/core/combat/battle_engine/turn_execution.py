"""Action targeting and validation for the battle engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..actor_cycle import PLAYER_ACTOR_ID
from ..combat_result import CombatResultGroup
from ..targeting import TargetScope
from .models import (
    ActionIntent,
    ActionResult,
    ActionValidationCode,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class TurnExecutionMixin:
    """Translate actions into validated, explicitly targeted intents."""

    def execute_action(
        self,
        action: str,
        choice: str | None = None,
        slot_machine_callback: Callable | None = None,
    ) -> ActionResult:
        """Compatibility adapter for callers that do not construct intents."""
        scope = self._target_scope_for_action(action, choice)
        target_ids: tuple[str, ...] = ()
        player_side = self.current_actor_id == PLAYER_ACTOR_ID or (
            self.current_actor_id is None and self.is_player_turn()
        )
        if (
            scope == TargetScope.SINGLE_ENEMY
            and player_side
            and len(self.encounter.members) == 1
            and len(self.encounter.living_members) == 1
        ):
            target_ids = (self.encounter.living_members[0].combatant_id,)
        elif scope == TargetScope.SINGLE_ENEMY and player_side:
            pending = self.pending_actions.get(PLAYER_ACTOR_ID)
            if pending:
                target_id = pending.get("target_id")
                try:
                    member = self.encounter.member_by_id(target_id)
                except KeyError:
                    member = None
                policy = pending.get("policy")
                if member is not None and member.is_living_hostile:
                    target_ids = (member.combatant_id,)
                elif getattr(policy, "value", policy) == "retarget_focus":
                    self._refresh_focus()
                    if self.encounter.living_members:
                        member = self.encounter.member_by_id(self._focus_target_id)
                        target_ids = (member.combatant_id,)
                        skill = pending.get("ability")
                        if skill is not None and hasattr(skill, "charge_target"):
                            skill.charge_target = member.enemy
                else:
                    skill = pending.get("ability")
                    if skill is not None:
                        skill.charging = False
                        if hasattr(skill, "charge_turns"):
                            skill.charge_turns = 0
                        if hasattr(skill, "charge_target"):
                            skill.charge_target = None
                    self.pending_actions.pop(PLAYER_ACTOR_ID, None)
                    message = (
                        f"{getattr(skill, 'name', 'The charged action')} fizzles "
                        "because its locked target is gone.\n"
                    )
                    group = CombatResultGroup(
                        action=getattr(skill, "name", action),
                        actor_id=PLAYER_ACTOR_ID,
                        target_scope=TargetScope.SINGLE_ENEMY,
                        message=message,
                    )
                    return ActionResult(message=message, combat_results=group)
            elif self.attacker.status_effects["Berserk"].active:
                self._refresh_focus()
                if self.encounter.living_members:
                    target_ids = (self._focus_target_id,)
        return self.execute_intent(
            ActionIntent(action=action, choice=choice, target_ids=target_ids),
            slot_machine_callback=slot_machine_callback,
        )

    def _ability_for_action(self, action: str, choice: str | None):
        if not choice:
            return None
        if action in {"Cast Spell", "Runic Boost"}:
            return self.attacker.spellbook.get("Spells", {}).get(choice)
        if action in {"Use Skill", "Tame"}:
            return self.attacker.spellbook.get("Skills", {}).get(
                choice if action == "Use Skill" else "Tame"
            )
        return None

    def _target_scope_for_action(
        self,
        action: str,
        choice: str | None,
    ) -> TargetScope:
        """Derive the canonical target scope for a legacy action."""
        if action in {
            "Nothing",
            "Cancelled",
            "Pickup Weapon",
            "Flee",
            "Recall",
            "Companion",
            "Repertoire",
            "Totem",
            "Transform",
            "Untransform",
            "Dismiss Form",
        }:
            return TargetScope.NONE
        if action in {"Defend", "Summon"}:
            return TargetScope.SELF
        if action == "Use Item":
            if choice:
                import re

                item_key = re.split(r"\s{2,}", choice)[0]
                items = self.attacker.inventory.get(item_key, [])
                item = items[0] if items else None
                if isinstance(item, type):
                    item = item()
                spell = getattr(item, "spell", None)
                if (
                    getattr(item, "subtyp", None) == "Scroll"
                    and getattr(spell, "subtyp", None) != "Support"
                ):
                    return TargetScope.SINGLE_ENEMY
            return TargetScope.SELF
        ability = self._ability_for_action(action, choice)
        if ability is not None:
            declared = getattr(ability, "target_scope", TargetScope.SINGLE_ENEMY)
            if (
                declared == TargetScope.ALL_ENEMIES
                and self.attacker != self.player
                and getattr(ability, "name", "")
                in {
                    "Photon Sphere",
                    "Prismatic Cataclysm",
                }
            ):
                # Enemy AI still has a single player-side target. The player
                # version expands across the hostile encounter roster.
                return TargetScope.SINGLE_ENEMY
            raw_data = getattr(ability, "_raw_data", {})
            if isinstance(raw_data, dict) and "target_scope" in raw_data:
                return declared
            if declared in {TargetScope.NONE, TargetScope.ALL_ENEMIES}:
                return declared
            if getattr(ability, "passive", False):
                return TargetScope.NONE
            if getattr(ability, "subtyp", None) in {"Heal", "Support"} or getattr(
                ability, "self_target", False
            ):
                return TargetScope.SELF
            return declared
        return TargetScope.SINGLE_ENEMY

    def target_scope_for_action(
        self,
        action: str,
        choice: str | None = None,
    ) -> TargetScope:
        """Return the canonical target scope for a prospective action."""
        return self._target_scope_for_action(action, choice)

    def _reject_intent(
        self,
        code: ActionValidationCode,
        message: str,
    ) -> ActionResult:
        self._turn_action_committed = False
        return ActionResult(
            message=message,
            committed=False,
            validation_code=code,
            combat_results=CombatResultGroup(message=message),
        )

    def _validated_intent_targets(
        self,
        intent: ActionIntent,
        scope: TargetScope,
    ):
        supplied = intent.target_ids
        if scope in {TargetScope.NONE, TargetScope.SELF, TargetScope.ALL_ENEMIES}:
            if supplied:
                return self._reject_intent(
                    ActionValidationCode.WRONG_TARGET_SCOPE,
                    f"{scope.value} actions do not accept explicit target IDs.\n",
                )
            if scope == TargetScope.ALL_ENEMIES:
                return list(self.encounter.living_members)
            return []

        player_side = self.current_actor_id == PLAYER_ACTOR_ID or (
            self.current_actor_id is None and self.is_player_turn()
        )
        if not player_side:
            if supplied:
                return self._reject_intent(
                    ActionValidationCode.WRONG_TARGET_SCOPE,
                    "Enemy actions target the active player-side combatant.\n",
                )
            return []
        if not supplied:
            return self._reject_intent(
                ActionValidationCode.MISSING_TARGET,
                "Choose one enemy target.\n",
            )
        if len(supplied) != 1:
            return self._reject_intent(
                ActionValidationCode.WRONG_TARGET_COUNT,
                "Single-enemy actions require exactly one target.\n",
            )
        try:
            member = self.encounter.member_by_id(supplied[0])
        except KeyError:
            return self._reject_intent(
                ActionValidationCode.UNKNOWN_TARGET,
                "That target is not part of this encounter.\n",
            )
        if not member.is_living_hostile:
            return self._reject_intent(
                ActionValidationCode.UNAVAILABLE_TARGET,
                "That target is dead or has already left the encounter.\n",
            )
        return [member]
