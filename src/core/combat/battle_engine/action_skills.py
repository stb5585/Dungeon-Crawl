"""Skill actions for the battle engine."""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from ... import items
from ...classes import (
    astromancer,
    footpad,
    promotion_kits,
)
from ...events.event_bus import EventType, create_combat_event
from ..combat_result import CombatResult
from ..encounter import EnemyResolution

if TYPE_CHECKING:
    from collections.abc import Callable


class SkillActionMixin:
    """Resolve active combat skills and their resource costs."""

    def _execute_skill(
        self,
        choice: str | None,
        slot_machine_callback: Callable | None = None,
    ) -> str:
        """Use a skill. Handles silence, Jump, Charge, Smoke Screen, etc."""
        if not choice:
            return f"{self.attacker.name} does nothing.\n"

        # Handle "Remove Shield" alias for Mana Shield
        if choice == "Remove Shield":
            choice = "Mana Shield"

        skills = self.attacker.spellbook.get("Skills", {})
        if choice not in skills:
            return f"{self.attacker.name} does not know {choice}.\n"

        skill = skills[choice]
        if skill.name == "Mortal Strike" and not getattr(self.attacker, "_transformed", False):
            weapon = self.attacker.equipment.get("Weapon")
            if int(getattr(weapon, "handed", 0) or 0) != 2:
                return f"{self.attacker.name} needs a two-handed weapon to use Mortal Strike.\n"
        # Charging skills deduct mana at start, then must be allowed to continue
        # even when the user is at 0 mana or becomes silenced (otherwise the
        # charge can never resolve). Resolve actions spend shield pressure, not
        # voice or spellcasting focus, so silence should not suppress them.
        already_charging = bool(getattr(skill, "charging", False))
        is_resolve_skill = self._skill_uses_resolve(skill)
        is_class_resource_skill = (
            is_resolve_skill or getattr(skill, "resource_type", None) == "Oath Conviction"
        )
        abilities_suppressed = self.attacker.abilities_suppressed()
        anti_magic_active = bool(getattr(self.attacker, "anti_magic_active", False))
        requires_mana = int(getattr(skill, "cost", 0) or 0) > 0 and not is_class_resource_skill
        if (
            abilities_suppressed
            and not already_charging
            and not is_class_resource_skill
            and (anti_magic_active or requires_mana)
        ):
            reason = "the anti-magic field" if anti_magic_active else "silence"
            return f"{self.attacker.name} cannot use skills because of {reason}!\n"

        if (
            not already_charging
            and not is_class_resource_skill
            and self.attacker.mana.current < skill.cost
        ):
            return f"{self.attacker.name} does not have enough mana to use {choice}!\n"
        if (
            skill.name in promotion_kits.KI_SPEND_ABILITIES
            and skill.name != "Chi Heal"
            and self.defender is None
        ):
            return "There is no target.\n"
        martial_weapon_check = getattr(skill, "_has_martial_weapon", None)
        if (
            skill.name in promotion_kits.KI_SPEND_ABILITIES
            and callable(martial_weapon_check)
            and not martial_weapon_check(self.attacker)
        ):
            return f"{self.attacker.name} needs a free hand or fist weapon to use {skill.name}.\n"

        ki_health_before = int(getattr(self.attacker.health, "current", 0) or 0)
        ki_spend_message = promotion_kits.begin_ki_spender(
            self.attacker,
            skill.name,
        )
        stolen_payoff_message = promotion_kits.prepare_stolen_charge_payoff(
            self.attacker,
            "Use Skill",
            skill,
        )

        self._event_bus.emit(
            create_combat_event(
                EventType.SKILL_USE,
                actor=self.attacker,
                target=self.defender,
                skill_name=skill.name,
                ability_name=skill.name,
                source="resolve" if is_resolve_skill else "skill",
            )
        )

        message = (
            f"{self.attacker.name} uses {skill.name}.\n{ki_spend_message}{stolen_payoff_message}"
        )
        bypass_required_item = self.attacker is not self.player

        # ── Special skill handling ───────────────────────────────────
        if skill.name == "Smoke Screen":
            if self.attacker is not self.player:
                message += skill.use(self.attacker, target=self.player)
                escaped, flee_str = self.attacker.flee(self.player, smoke=True)
                if escaped:
                    member = self._member_for_character(self.attacker)
                    if member is not None and member.resolution is None:
                        self.encounter.resolve_enemy(
                            member.combatant_id,
                            EnemyResolution.ESCAPED,
                            cause="smoke_screen",
                        )
                    self.attacker.state = "normal"
                message += flee_str
                return message
            if self.attacker is self.player:
                consumed, smoke_message = items.consume_smoke_bomb(self.attacker)
                if not consumed:
                    return smoke_message
                message += smoke_message
            hostile = self._fastest_living_hostile()
            message += skill.use(self.attacker, target=hostile)
            perceived = any(
                getattr(member.enemy, "sight", False)
                and not member.enemy.status_effects["Blind"].active
                for member in self.encounter.living_members
            )
            attempted, flee_str = self.attacker.flee(hostile, smoke=True)
            from ...classes.thief import has_thief_talent

            if not perceived:
                self.flee = True
                if not attempted:
                    flee_str = f"{self.attacker.name} disappears in a cloud of smoke."
            else:
                self.flee = bool(
                    attempted and has_thief_talent(self.attacker, "thief.clean-getaway")
                )
                if not self.flee:
                    flee_str = f"{hostile.name} sees through the smoke."
            message += flee_str
            if self.flee and footpad.has_skill(self.attacker, "Take It On the Run"):
                from ...abilities.utility import Steal

                stolen = Steal().use(self.attacker, hostile)
                message += getattr(stolen, "message", str(stolen))
                stolen_gold = int(getattr(stolen, "extra", {}).get("stolen_gold", 0) or 0)
                if stolen_gold > 0 and has_thief_talent(self.attacker, "rogue.gone-before-dawn"):
                    bonus = min(stolen_gold, max(0, int(getattr(hostile, "gold", 0) or 0)))
                    hostile.gold -= bonus
                    self.attacker.gold += bonus
                    message += f"Gone Before Dawn steals {bonus} additional gold.\n"
            if self.flee and hasattr(self.player, "record_flee"):
                self.player.record_flee()

        elif skill.name == "Slot Machine":
            if slot_machine_callback:
                message += skill.use(
                    self.attacker,
                    target=self.defender,
                    slot_machine_callback=slot_machine_callback,
                )
            else:
                message += skill.use(self.attacker, target=self.defender)

        elif skill.name in ["Doublecast", "Triplecast"]:
            message += skill.use(self.attacker, self.defender, game=self.game)

        elif skill.name == "Raise Summon":
            message += skill.use(
                self.attacker,
                target=self.defender,
                battle_engine=self,
            )

        elif skill.name in {"Cacophany", "Censure", "Disruption", "Upsurge"}:
            message += skill.use(
                self.attacker,
                target=self.defender,
                battle_engine=self,
            )

        elif "Jump" in skill.name:
            charge_time = skill.get_charge_time() if hasattr(skill, "get_charge_time") else 1
            continuing_charge = already_charging and int(getattr(skill, "charge_turns", 0) or 0) > 1
            if charge_time > 0 and (not already_charging or continuing_charge):
                self.attacker.class_effects["Jump"].active = True
                message = ""
            message += skill.use(self.attacker, target=self.defender)
            self.attacker.class_effects["Jump"].active = bool(getattr(skill, "charging", False))
            if getattr(skill, "charging", False):
                self._register_pending_charge(
                    choice,
                    skill,
                    preserve_start=already_charging,
                )
            else:
                self._clear_pending_charge(self._actor_id_for(self.attacker), skill)

        elif hasattr(skill, "get_charge_time") and skill.get_charge_time() > 0:
            # Charging abilities (Charge, Crushing Blow, etc.)
            message += skill.use(self.attacker, target=self.defender)
            if getattr(skill, "charging", False):
                self.charging_ability = (self.attacker, choice, skill)
                self._register_pending_charge(
                    choice,
                    skill,
                    preserve_start=already_charging,
                )
            else:
                # Charge completed this turn
                self._clear_pending_charge(self._actor_id_for(self.attacker), skill)

        else:
            use_kwargs = {"target": self.defender}
            if bypass_required_item and getattr(skill, "_required_item", None):
                use_kwargs["bypass_required_item"] = True
            message += str(skill.use(self.attacker, **use_kwargs))

        recorded_result = getattr(skill, "result", None)
        if (
            isinstance(recorded_result, CombatResult)
            and recorded_result.actor is self.attacker
            and recorded_result.target is self.defender
        ):
            self._last_combat_result = deepcopy(recorded_result)

        ki_hit = bool(getattr(recorded_result, "hit", False))
        ki_healing = max(
            0,
            int(getattr(self.attacker.health, "current", 0) or 0) - ki_health_before,
        )
        message += promotion_kits.finish_ki_spender(
            self.attacker,
            self.defender,
            skill.name,
            hit=ki_hit,
            healing=ki_healing,
        )
        if self.attacker == self.player:
            message += astromancer.record_thread_action(
                self.player,
                skill.name,
                successful=not any(
                    fragment in message.lower()
                    for fragment in ("no effect", "there is no target", "fails")
                ),
            )

        return message
