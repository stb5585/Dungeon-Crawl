"""Active and passive techniques for Thief and Rogue progression."""

from __future__ import annotations

from typing import Any

from ..combat.targeting import TargetScope
from .base import Class, Skill


def _spend_mana(user: Any, cost: int, action: str) -> str:
    """Spend mana after action validation."""
    if int(user.mana.current) < cost:
        return f"{user.name} does not have enough mana for {action}.\n"
    user.mana.current -= cost
    return ""


def _luck_state(user: Any) -> dict[str, Any]:
    from ..classes import promotion_kits

    return promotion_kits.combat_state(user)


def _has_talent(user: Any, key: str) -> bool:
    from ..classes.thief import has_thief_talent

    return has_thief_talent(user, key)


def _weapon_result(
    result: Any,
    user: Any,
    target: Any,
    *,
    damage_modifier: float,
    accuracy_modifier: float = 0.0,
) -> None:
    """Resolve one main-hand strike into an existing result."""
    before = int(target.health.current)
    message, hit, critical = user.weapon_damage(
        target,
        dmg_mod=damage_modifier,
        use_offhand=False,
        accuracy_modifier=accuracy_modifier,
    )
    result.hit = hit
    result.crit = critical if critical > 1 else None
    result.damage = max(0, before - int(target.health.current))
    result.message += message


class DisarmTraps(Class):
    """Enable a deliberate second approach to a detected dungeon trap."""

    def __init__(self) -> None:
        super().__init__(
            "Disarm Traps",
            (
                "After Find Traps stops you, approach again to attempt a DEX- and "
                "depth-based disarm. Lockpick tools and training improve the chance."
            ),
        )
        self.passive = True
        self.combat = False


class TakeItOnTheRun(Class):
    """Steal from the focused enemy during a successful Smoke Screen escape."""

    def __init__(self) -> None:
        super().__init__(
            "Take It On the Run",
            "A successful Smoke Screen escape also attempts to steal from the enemy.",
        )
        self.passive = True


class TurnTheTables(Class):
    """Convert accumulated Misfortune into a temporary combat advantage."""

    resource_type = "Misfortune"

    def __init__(self) -> None:
        super().__init__(
            "Turn the Tables",
            "Spend all Misfortune to raise Attack and Defense for three turns.",
        )
        self.cost = 6
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target, kwargs
        result = super().use(user, user)
        state = _luck_state(user)
        spent = int(state.get("misfortune", 0) or 0)
        if spent <= 0:
            result.message = "Turn the Tables requires Misfortune.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        state["misfortune"] = 0
        improved = _has_talent(user, "thief.reversal")
        amount = (5 if improved else 4) * spent
        duration = 4 if improved else 3
        for stat_name in ("Attack", "Defense"):
            effect = user.stat_effects[stat_name]
            effect.active = True
            effect.duration = max(int(effect.duration or 0), duration)
            effect.extra = max(int(effect.extra or 0), amount)
            effect.source = self.name
            result.effects_applied["Stat"].append(f"{stat_name} Buff")
        result.hit = True
        result.extra["misfortune_spent"] = spent
        result.message = (
            f"{user.name} turns {spent} Misfortune into +{amount} Attack and Defense.\n"
        )
        return result


class PilferingStrike(Skill):
    """Attack while lifting a small amount of ordinary enemy gold."""

    def __init__(self) -> None:
        super().__init__(
            "Pilfering Strike",
            "Strike for 90% weapon damage and steal gold on a successful hit.",
            weapon=True,
        )
        self.cost = 6
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Pilfering Strike needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        from ..classes import promotion_kits

        accuracy, luck_message = promotion_kits.consume_fortune_for_risky_action(
            user,
            self.name,
        )
        result.message += luck_message
        _weapon_result(
            result,
            user,
            target,
            damage_modifier=0.90,
            accuracy_modifier=accuracy,
        )
        if result.hit:
            stolen = min(
                max(0, int(getattr(target, "gold", 0) or 0)),
                max(1, int(user.stats.dex) // 10)
                * (2 if _has_talent(user, "thief.master-tools") else 1),
            )
            target.gold -= stolen
            user.gold += stolen
            result.extra["stolen_gold"] = stolen
            result.message += f"Pilfering Strike steals {stolen} gold.\n"
        result.message += promotion_kits.finish_fortune_payoff(user, bool(result.hit))
        if result.hit:
            result.message += promotion_kits.resolve_misfortune_payoff(
                user,
                target,
                result.damage,
                self.name,
                result=result,
            )
        return result


class CutAndRun(Skill):
    """Attack and gain a short burst of escape speed."""

    def __init__(self) -> None:
        super().__init__(
            "Cut and Run",
            "Strike for normal weapon damage; a hit raises Speed for two turns.",
            weapon=True,
        )
        self.cost = 7
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Cut and Run needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        _weapon_result(result, user, target, damage_modifier=1.0)
        if result.hit:
            speed = user.stat_effects["Speed"]
            speed.active = True
            duration = 3 if _has_talent(user, "thief.lasting-head-start") else 2
            amount = 8
            if _has_talent(user, "thief.fleet-footed"):
                amount = 12
            if _has_talent(user, "rogue.slippery-customer"):
                amount = 15
                duration = 3
            speed.duration = max(int(speed.duration or 0), duration)
            speed.extra = max(int(speed.extra or 0), amount)
            speed.source = self.name
            result.effects_applied["Stat"].append("Speed Buff")
            result.message += f"{user.name} gains {amount} Speed.\n"
        return result


class AllIn(Skill):
    """Spend both luck meters on a highly amplified weapon attack."""

    resource_type = "Fortune + Misfortune"

    def __init__(self) -> None:
        super().__init__(
            "All In",
            "Spend all Fortune and Misfortune on one accurate, amplified strike.",
            weapon=True,
        )
        self.cost = 10
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        state = _luck_state(user)
        fortune = int(state.get("fortune", 0) or 0)
        misfortune = int(state.get("misfortune", 0) or 0)
        total = fortune + misfortune
        if target is None or total <= 0:
            result.message = "All In requires a target and stored luck.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        state["fortune"] = 0
        state["misfortune"] = 0
        _weapon_result(
            result,
            user,
            target,
            damage_modifier=1.0 + (0.12 * total),
            accuracy_modifier=min(0.20, 0.05 * fortune),
        )
        if (
            result.hit
            and fortune > 0
            and _has_talent(user, "rogue.house-always-wins")
        ):
            state["fortune"] = 1
            result.message += "The House Always Wins preserves 1 Fortune.\n"
        result.extra.update({"fortune_spent": fortune, "misfortune_spent": misfortune})
        result.message += f"{user.name} goes All In with {total} stored luck.\n"
        return result


class SnakeEyes(Skill):
    """Cash in Misfortune through a blinding weapon attack."""

    resource_type = "Misfortune"

    def __init__(self) -> None:
        super().__init__(
            "Snake Eyes",
            "Spend all Misfortune on a weapon strike that blinds on hit.",
            weapon=True,
        )
        self.cost = 8
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        state = _luck_state(user)
        spent = int(state.get("misfortune", 0) or 0)
        if target is None or spent <= 0:
            result.message = "Snake Eyes requires a target and Misfortune.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        state["misfortune"] = 0
        _weapon_result(result, user, target, damage_modifier=1.0 + (0.08 * spent))
        if result.hit and target.is_alive():
            blind = target.status_effects["Blind"]
            blind.active = True
            blind.duration = max(int(blind.duration or 0), 1 + spent)
            blind.source = self.name
            result.effects_applied["Status"].append("Blind")
            result.message += f"Snake Eyes blinds {target.name}.\n"
        result.extra["misfortune_spent"] = spent
        return result


class DirtyTrick(Skill):
    """Trade damage for a reliable paired combat debuff."""

    def __init__(self) -> None:
        super().__init__(
            "Dirty Trick",
            "Strike for 80% weapon damage and reduce Attack and Defense on hit.",
            weapon=True,
        )
        self.cost = 8
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Dirty Trick needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        from ..classes import promotion_kits

        accuracy, luck_message = promotion_kits.consume_fortune_for_risky_action(
            user,
            self.name,
        )
        result.message += luck_message
        _weapon_result(
            result,
            user,
            target,
            damage_modifier=0.80,
            accuracy_modifier=accuracy,
        )
        if result.hit and target.is_alive():
            for stat_name in ("Attack", "Defense"):
                effect = target.stat_effects[stat_name]
                effect.active = True
                effect.duration = max(int(effect.duration or 0), 2)
                effect.extra = min(int(effect.extra or 0), -5)
                effect.source = self.name
                result.effects_applied["Stat"].append(f"{stat_name} Debuff")
            result.message += f"Dirty Trick compromises {target.name}.\n"
        result.message += promotion_kits.finish_fortune_payoff(user, bool(result.hit))
        if result.hit:
            result.message += promotion_kits.resolve_misfortune_payoff(
                user,
                target,
                result.damage,
                self.name,
                result=result,
            )
        return result
