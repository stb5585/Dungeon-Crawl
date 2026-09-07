"""Ranger abilities built around quarry knowledge and crossbow ammunition."""

from __future__ import annotations

from typing import Any

from ..combat.combat_result import CombatResult, CombatResultGroup
from ..combat.targeting import TargetLossPolicy, TargetScope
from .base import Class, Skill


class WildSense(Class):
    """Read a favored enemy's traits using accumulated tracking mastery."""

    def __init__(self) -> None:
        super().__init__(
            "Wild Sense",
            "Inspect a favored enemy. Higher Tracking Mastery reveals more combat details.",
        )
        self.cost = 0

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        from ..classes import pathfinder

        return target is not None and pathfinder.is_favored_enemy(user, target)

    def use(self, user: Any, target: Any | None = None, **kwargs: Any) -> CombatResult:
        from ..classes import pathfinder

        del kwargs
        result = super().use(user, target)
        result.message = pathfinder.wild_sense_report(user, target)
        result.hit = bool(target is not None and pathfinder.is_favored_enemy(user, target))
        return result


class UncannyVolley(Skill):
    """Fire one selected crossbow bolt at every living enemy."""

    def __init__(self) -> None:
        super().__init__(
            "Uncanny Volley",
            "Fire one crossbow bolt at every enemy. Bolts deal 25% more damage to "
            "unnatural enemies.",
        )
        self.cost = 14
        self.subtyp = "Offensive"
        self.target_scope = TargetScope.ALL_ENEMIES
        self.target_loss_policy = TargetLossPolicy.SNAPSHOT_ROSTER

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        from ..classes import crossbow

        del target
        return (
            crossbow.equipped_crossbow(user) is not None
            and crossbow.selected_bolts(user) is not None
        )

    def use_group(
        self,
        user: Any,
        targets: list[tuple[str, Any]],
        *,
        battle_engine: Any,
        rng: Any | None = None,
    ) -> CombatResultGroup:
        from ..classes import crossbow, pathfinder

        group = CombatResultGroup(
            action=self.name,
            actor_id=battle_engine.current_actor_id,
            target_scope=TargetScope.ALL_ENEMIES,
            target_ids=tuple(target_id for target_id, _target in targets),
        )
        if not self.is_available(user):
            group.message = "Uncanny Volley requires an equipped crossbow and bolts.\n"
            return group
        user.mana.current -= self.cost
        for target_id, target in targets:
            multiplier = 1.25 if pathfinder.is_unnatural_enemy(target) else 1.0
            message, hit, damages = crossbow.fire_crossbow(
                user,
                target,
                encounter=None,
                rng=rng,
                shot_limit=1,
                damage_multiplier=multiplier,
                napalm_splash=False,
            )
            result = CombatResult(
                action=self.name,
                actor=user,
                target=target,
                hit=hit,
                damage=sum(damages),
                message=message,
                actor_id=battle_engine.current_actor_id,
                target_id=target_id,
            )
            group.add(result)
        return group


class QuarryCleave(Skill):
    """Commit a two-handed strike that bears down harder on the quarry."""

    def __init__(self) -> None:
        super().__init__(
            "Quarry Cleave",
            "Make a heavy two-handed attack for 25% more damage, increased to "
            "50% against your favored enemy type.",
            weapon=True,
        )
        self.cost = 10
        self.subtyp = "Offensive"

    @staticmethod
    def _has_two_handed_weapon(user: Any) -> bool:
        weapon = getattr(user, "equipment", {}).get("Weapon")
        return (
            getattr(weapon, "typ", None) == "Weapon" and int(getattr(weapon, "handed", 1) or 1) == 2
        )

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        return target is not None and self._has_two_handed_weapon(user)

    def use(self, user: Any, target: Any | None = None, **kwargs: Any) -> CombatResult:
        from ..classes import pathfinder

        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Quarry Cleave needs a target.\n"
            return result
        if not self._has_two_handed_weapon(user):
            result.message = "Quarry Cleave requires a two-handed main-hand weapon.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        before = int(target.health.current)
        favored = pathfinder.is_favored_enemy(user, target)
        message, hit, critical = user.weapon_damage(
            target,
            dmg_mod=1.50 if favored else 1.25,
            use_offhand=False,
            attack_slots=("Weapon",),
        )
        result.hit = hit
        result.crit = critical if critical > 1 else None
        result.damage = max(0, before - int(target.health.current))
        if favored and hit:
            message += "Quarry Cleave follows the marked trail through the target's guard.\n"
        result.message = message
        return result


class HuntersSnare(Skill):
    """Slow an enemy, using Tracking Mastery to bind the current quarry."""

    def __init__(self) -> None:
        super().__init__(
            "Hunter's Snare",
            "Reduce an enemy's Speed. Against your favored enemy, Tracking "
            "Mastery strengthens the penalty and extends its duration.",
        )
        self.cost = 8
        self.subtyp = "Control"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any) -> CombatResult:
        from ..classes import ability_mechanics, pathfinder

        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Hunter's Snare needs a target.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        favored = pathfinder.is_favored_enemy(user, target)
        tracking = ability_mechanics.favored_enemy_practice_bonus(user) if favored else 0
        penalty = max(2, 2 + tracking)
        effect = target.stat_effects["Speed"]
        effect.active = True
        effect.duration = max(int(effect.duration or 0), 4 if favored else 2)
        effect.extra = min(int(effect.extra or 0), -penalty)
        effect.source = self.name
        result.hit = True
        result.effects_applied["Stat"].append("Speed Debuff")
        mastery_text = " Tracking Mastery tightens it." if favored else ""
        result.message = (
            f"{user.name} snares {target.name}, reducing Speed by {penalty}." f"{mastery_text}\n"
        )
        return result
