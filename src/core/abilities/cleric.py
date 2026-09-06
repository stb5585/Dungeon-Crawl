"""Active techniques for Cleric, Templar, and Hierophant progression."""

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


def _has_talent(character: Any, key: str) -> bool:
    """Return whether the character owns an authored Cleric-line talent."""
    try:
        from ..progression import has_talent

        return has_talent(character, key)
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


class BastionPrayer(Class):
    """Spend one Devotion without emptying the held defensive reserve."""

    def __init__(self) -> None:
        super().__init__(
            "Bastion Prayer",
            "Spend one Devotion to raise Defense and Magic Defense for three turns.",
        )
        self.cost = 5
        self.subtyp = "Defensive"
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target, kwargs
        from ..classes import promotion_kits

        result = super().use(user, user)
        state = promotion_kits.combat_state(user)
        if int(state.get("devotion", 0) or 0) <= 0:
            result.message = "Bastion Prayer requires Devotion.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        state["devotion"] = int(state["devotion"]) - 1
        amount = 10 if _has_talent(user, "cleric.bastion-practice") else 7
        for stat_name in ("Defense", "Magic Defense"):
            effect = user.stat_effects[stat_name]
            effect.active = True
            effect.duration = max(int(effect.duration or 0), 3)
            effect.extra = max(int(effect.extra or 0), amount)
            effect.source = self.name
            result.effects_applied["Stat"].append(f"{stat_name} Buff")
        result.hit = True
        result.extra["devotion_spent"] = 1
        result.message = (
            f"{user.name} spends 1 Devotion on Bastion Prayer, raising both "
            f"defenses by {amount}.\n"
        )
        return result


class DevotionalRebuke(Skill):
    """Strike with a weapon and follow through with typed Holy damage."""

    def __init__(self) -> None:
        super().__init__(
            "Devotional Rebuke",
            "Strike for normal weapon damage and add a Wisdom-scaled Holy rebuke.",
            weapon=True,
        )
        self.cost = 8
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Devotional Rebuke needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        before = int(target.health.current)
        message, hit, critical = user.weapon_damage(
            target,
            dmg_mod=1.0,
            use_offhand=False,
        )
        result.hit = hit
        result.crit = critical if critical > 1 else None
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        if not hit or not target.is_alive():
            return result
        scale = 1.0
        if _has_talent(user, "cleric.measured-judgment"):
            scale += 0.25
        if _has_talent(user, "templar.exacting-judgment"):
            scale += 0.25
        raw_holy = max(4, int(int(user.stats.wisdom) * 0.35 * scale))
        holy_hit, reduction, holy_damage = target.damage_reduction(
            raw_holy,
            user,
            typ="Holy",
        )
        holy_damage = (
            max(0, min(int(holy_damage or 0), int(target.health.current)))
            if holy_hit
            else 0
        )
        result.message += reduction
        if holy_damage:
            target.health.current -= holy_damage
            result.damage += holy_damage
            user._emit_damage_event(
                target,
                holy_damage,
                damage_type="Holy",
                source="skill",
                ability_name=self.name,
                attack_source="special_attack",
            )
            result.message += (
                f"Devotional Rebuke burns {target.name} for {holy_damage} Holy damage.\n"
            )
        return result


class SacredMending(Class):
    """Restore health through a shared Cleric rite."""

    def __init__(self) -> None:
        super().__init__(
            "Sacred Mending",
            "Restore your health through a rite of the Cleric faith.",
        )
        self.cost = 8
        self.subtyp = "Support"
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target, kwargs
        result = super().use(user, user)
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        scale = 1.25 if _has_talent(user, "cleric.open-ministry") else 1.0
        healing = min(
            int(user.health.max) - int(user.health.current),
            max(1, int((12 + int(user.stats.wisdom)) * scale)),
        )
        user.health.current += healing
        if healing and hasattr(user, "_emit_healing_event"):
            user._emit_healing_event(healing, source=self.name)
        result.hit = True
        result.healing = healing
        result.message = f"{user.name}'s Sacred Mending restores {healing} HP.\n"
        return result


class HallowedReadiness(Class):
    """Raise both defenses without spending held Devotion."""

    def __init__(self) -> None:
        super().__init__(
            "Hallowed Readiness",
            "Raise Defense and Magic Defense.",
        )
        self.cost = 10
        self.subtyp = "Defensive"
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target, kwargs
        result = super().use(user, user)
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        mastered = _has_talent(user, "cleric.common-purpose")
        amount = 12 if mastered else 8
        duration = 3 if mastered else 2
        for stat_name in ("Defense", "Magic Defense"):
            effect = user.stat_effects[stat_name]
            effect.active = True
            effect.duration = max(int(effect.duration or 0), duration)
            effect.extra = max(int(effect.extra or 0), amount)
            effect.source = self.name
            result.effects_applied["Stat"].append(stat_name)
        result.hit = True
        result.message = (
            f"{user.name}'s Hallowed Readiness raises both defenses by {amount}.\n"
        )
        return result


class ConduitStrike(Skill):
    """Deliver a focused staff strike for Hierophant conduit builds."""

    def __init__(self) -> None:
        super().__init__(
            "Conduit Strike",
            "Strike for 120% staff damage and conduct prepared sacred power.",
            weapon=True,
        )
        self.cost = 9
        self.subtyp = "Offensive"

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        weapon = getattr(user, "equipment", {}).get("Weapon")
        return target is not None and getattr(weapon, "subtyp", None) == "Staff"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if not self.is_available(user, target):
            result.message = "Conduit Strike requires a staff and a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        before = int(target.health.current)
        message, hit, critical = user.weapon_damage(
            target,
            dmg_mod=1.20,
            use_offhand=False,
            attack_slots=("Weapon",),
        )
        result.hit = hit
        result.crit = critical if critical > 1 else None
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        return result


class GracefulIntercession(Class):
    """Spend one Devotion on immediate healing and a modest ward."""

    def __init__(self) -> None:
        super().__init__(
            "Graceful Intercession",
            "Spend one Devotion to restore health and raise a two-turn ward.",
        )
        self.cost = 8
        self.subtyp = "Support"
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target, kwargs
        from ..classes import promotion_kits

        result = super().use(user, user)
        state = promotion_kits.combat_state(user)
        if int(state.get("devotion", 0) or 0) <= 0:
            result.message = "Graceful Intercession requires Devotion.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        state["devotion"] = int(state["devotion"]) - 1
        scale = 1.35 if _has_talent(user, "hierophant.greater-intercession") else 1.0
        healing = min(
            int(user.health.max) - int(user.health.current),
            max(1, int((10 + int(user.stats.wisdom)) * scale)),
        )
        user.health.current += healing
        ward = user.magic_effects["Nature Shield"]
        ward.active = True
        ward.duration = max(int(ward.duration or 0), 3 if scale > 1 else 2)
        ward.extra = max(int(ward.extra or 0), int(10 * scale))
        result.hit = True
        result.healing = healing
        result.effects_applied["Magic"].append("Nature Shield")
        result.message = (
            f"{user.name} spends 1 Devotion; Graceful Intercession restores "
            f"{healing} HP and raises a ward.\n"
        )
        return result
