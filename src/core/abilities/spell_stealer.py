"""Active techniques for the Spell Stealer and Arcane Trickster."""

from __future__ import annotations

from typing import Any

from ..combat.targeting import TargetScope
from .base import Class, Skill


def _spend_mana(user: Any, cost: int, action: str) -> str:
    """Spend mana after validation, returning an error when unavailable."""
    if int(user.mana.current) < cost:
        return f"{user.name} does not have enough mana for {action}.\n"
    user.mana.current -= cost
    return ""


def _apply_stat_effect(
    target: Any,
    stat_name: str,
    amount: int,
    duration: int,
    source: str,
) -> None:
    """Apply a signed stat modifier without weakening a stronger effect."""
    effect = target.stat_effects[stat_name]
    effect.active = True
    effect.duration = max(int(effect.duration or 0), duration)
    if amount < 0:
        effect.extra = min(int(effect.extra or 0), amount)
    else:
        effect.extra = max(int(effect.extra or 0), amount)
    effect.source = source


class SpellbreakersCut(Skill):
    """Make a light weapon strike that opens the target to stolen magic."""

    def __init__(self) -> None:
        super().__init__(
            "Spellbreaker's Cut",
            "Strike for 95% weapon damage and reduce the target's Magic Defense.",
            weapon=True,
        )
        self.cost = 7
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Spellbreaker's Cut needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        before = int(target.health.current)
        message, hit, critical = user.weapon_damage(
            target,
            dmg_mod=0.95,
            use_offhand=False,
        )
        result.hit = hit
        result.crit = critical if critical > 1 else None
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        if hit:
            penalty = max(2, int(user.stats.intel) // 5)
            _apply_stat_effect(target, "Magic Defense", -penalty, 3, self.name)
            result.effects_applied["Stat"].append("Magic Defense Debuff")
            result.message += f"{target.name}'s Magic Defense falls by {penalty}.\n"
        return result


class BorrowedWard(Class):
    """Convert every stored charge into a short defensive ward."""

    def __init__(self) -> None:
        super().__init__(
            "Borrowed Ward",
            "Spend all Stolen Charge to raise Defense and Magic Defense for three turns.",
        )
        self.cost = 5
        self.subtyp = "Defensive"
        self.target_scope = TargetScope.SELF

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        del target
        from ..classes import promotion_kits

        return int(promotion_kits.combat_state(user).get("stolen_charge", 0) or 0) > 0

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target, kwargs
        from ..classes import promotion_kits

        result = super().use(user, user)
        state = promotion_kits.combat_state(user)
        stacks = max(0, int(state.get("stolen_charge", 0) or 0))
        if stacks <= 0:
            result.message = f"{user.name} has no Stolen Charge to ward with.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        state["stolen_charge"] = 0
        amount = 4 * stacks
        for stat_name in ("Defense", "Magic Defense"):
            _apply_stat_effect(user, stat_name, amount, 3, self.name)
            result.effects_applied["Stat"].append(f"{stat_name} Buff")
        result.hit = True
        result.extra["stolen_charge_spent"] = stacks
        result.message = (
            f"{user.name} folds {stacks} Stolen Charge into a ward, raising "
            f"Defense and Magic Defense by {amount}.\n"
        )
        return result


class ArcaneAmbush(Skill):
    """Deliver a decisive weapon strike suited to a charged opening."""

    def __init__(self) -> None:
        super().__init__(
            "Arcane Ambush",
            "Strike for 130% weapon damage; committed Stolen Charge releases normally.",
            weapon=True,
        )
        self.cost = 10
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Arcane Ambush needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        before = int(target.health.current)
        message, hit, critical = user.weapon_damage(
            target,
            dmg_mod=1.30,
            use_offhand=False,
        )
        result.hit = hit
        result.crit = critical if critical > 1 else None
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        return result


class VanishingAct(Class):
    """Spend one charge to create a defensive arcane afterimage."""

    def __init__(self) -> None:
        super().__init__(
            "Vanishing Act",
            "Spend one Stolen Charge to raise Speed and Defense for three turns.",
        )
        self.cost = 6
        self.subtyp = "Defensive"
        self.target_scope = TargetScope.SELF

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        del target
        from ..classes import promotion_kits

        return int(promotion_kits.combat_state(user).get("stolen_charge", 0) or 0) > 0

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target, kwargs
        from ..classes import promotion_kits

        result = super().use(user, user)
        state = promotion_kits.combat_state(user)
        if int(state.get("stolen_charge", 0) or 0) <= 0:
            result.message = f"{user.name} has no Stolen Charge to misdirect.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        try:
            from ..progression import has_talent

            escape_artist = has_talent(user, "arcane-trickster.escape-artist")
        except (AttributeError, KeyError, TypeError, ValueError):
            escape_artist = False
        state["stolen_charge"] = int(state["stolen_charge"]) - 1
        amount = 12 if escape_artist else 8
        duration = 4 if escape_artist else 3
        for stat_name in ("Speed", "Defense"):
            _apply_stat_effect(user, stat_name, amount, duration, self.name)
            result.effects_applied["Stat"].append(f"{stat_name} Buff")
        result.hit = True
        result.extra["stolen_charge_spent"] = 1
        result.message = (
            f"{user.name} spends 1 Stolen Charge and vanishes behind an afterimage, "
            f"raising Speed and Defense by {amount}.\n"
        )
        return result


class FalseOpening(Skill):
    """Bait the target into exposing both martial and magical offense."""

    def __init__(self) -> None:
        super().__init__(
            "False Opening",
            "Strike for 85% weapon damage and reduce the target's Attack and Magic.",
            weapon=True,
        )
        self.cost = 8
        self.subtyp = "Control"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "False Opening needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        before = int(target.health.current)
        message, hit, critical = user.weapon_damage(
            target,
            dmg_mod=0.85,
            use_offhand=False,
        )
        result.hit = hit
        result.crit = critical if critical > 1 else None
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        if hit:
            penalty = max(3, (int(user.stats.intel) + int(user.stats.dex)) // 10)
            for stat_name in ("Attack", "Magic"):
                _apply_stat_effect(target, stat_name, -penalty, 3, self.name)
                result.effects_applied["Stat"].append(f"{stat_name} Debuff")
            result.message += (
                f"The false opening lowers {target.name}'s Attack and Magic by " f"{penalty}.\n"
            )
        return result
