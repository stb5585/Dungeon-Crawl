"""Active investigation and wayfinding techniques for the Inquisitor line."""

from __future__ import annotations

from typing import Any

from ..combat.targeting import TargetScope
from .base import Class, Skill


def _has_talent(user: Any, key: str) -> bool:
    from ..progression import has_talent

    return has_talent(user, key)


def _spend_mana(user: Any, cost: int, action: str) -> str:
    if int(user.mana.current) < cost:
        return f"{user.name} does not have enough mana for {action}.\n"
    user.mana.current -= cost
    return ""


def _weapon_hit(result: Any, user: Any, target: Any, modifier: float) -> None:
    before = int(target.health.current)
    message, hit, critical = user.weapon_damage(
        target,
        dmg_mod=modifier,
        use_offhand=False,
    )
    result.hit = hit
    result.crit = critical if critical > 1 else None
    result.damage = max(0, before - int(target.health.current))
    result.message += message


class TakeNotes(Class):
    """Review the Case Journal as a readable out-of-combat notebook."""

    def __init__(self) -> None:
        super().__init__(
            "Take Notes",
            "Outside combat, review the rank of every enemy type recorded in your Notebook.",
        )
        self.combat = False

    def use_out(self, game_or_user: Any) -> str:
        from ..classes import promotion_kits

        user = getattr(game_or_user, "player_char", game_or_user)
        journal = promotion_kits.ensure_state(user).get("case_journal", {})
        if not journal:
            return "The Notebook has no case notes yet.\n"
        lines = ["Notebook:\n"]
        for enemy_type, progress in sorted(journal.items()):
            lines.append(f"- {enemy_type}: {promotion_kits.case_rank(progress)}\n")
        return "".join(lines)


class DeductiveStrike(Skill):
    """Weapon payoff that is strongest against a studied target."""

    def __init__(self) -> None:
        super().__init__(
            "Deductive Strike",
            "Strike for 110% weapon damage, rising to 135% against a Weakness Brief target.",
            weapon=True,
        )
        self.cost = 8
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Deductive Strike needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        from ..classes import promotion_kits

        threshold = 25 if _has_talent(user, "seeker.patient-deduction") else 50
        modifier = 1.35 if promotion_kits.case_progress(user, target) >= threshold else 1.10
        _weapon_hit(result, user, target, modifier)
        return result


class ForegoneConclusion(Class):
    """Spend all Revelation to suppress a target's combat ratings."""

    resource_type = "Revelation"

    def __init__(self) -> None:
        super().__init__(
            "Foregone Conclusion",
            "Spend all Revelation on a target to reduce Attack and Magic for three turns.",
        )
        self.cost = 10

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Foregone Conclusion needs a target.\n"
            return result
        from ..classes import promotion_kits

        stacks = promotion_kits.revelation_stacks(user, target)
        if stacks <= 0:
            result.message = "Foregone Conclusion requires Revelation on the target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        promotion_kits.clear_revelation(user, target)
        amount = (8 if _has_talent(user, "seeker.proven-case") else 6) * stacks
        duration = 4 if _has_talent(user, "seeker.inevitable-conclusion") else 3
        for stat in ("Attack", "Magic"):
            effect = target.stat_effects[stat]
            effect.active = True
            effect.duration = max(int(effect.duration or 0), duration)
            existing = int(effect.extra or 0)
            effect.extra = min(-amount, existing if existing < 0 else 0)
            effect.source = self.name
            result.effects_applied["Stat"].append(f"{stat} Debuff")
        result.hit = True
        result.message = (
            f"{user.name} proves the case, reducing {target.name}'s Attack and Magic by {amount}.\n"
        )
        return result


class SurveyorsStep(Class):
    """Convert familiarity with the current floor into combat mobility."""

    def __init__(self) -> None:
        super().__init__(
            "Surveyor's Step",
            "Gain Speed for three turns based on how much of the current floor is mapped.",
        )
        self.cost = 7
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target
        result = super().use(user, user, **kwargs)
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        from ..classes import promotion_kits

        mapped = promotion_kits.level_mapping_progress(user)
        amount = 8 + int(mapped * 12)
        if _has_talent(user, "seeker.light-footed"):
            amount += 5
        speed = user.stat_effects["Speed"]
        speed.active = True
        speed.duration = max(int(speed.duration or 0), 3)
        speed.extra = max(int(speed.extra or 0), amount)
        speed.source = self.name
        result.hit = True
        result.effects_applied["Stat"].append("Speed Buff")
        result.message = f"{user.name} follows the surveyed route and gains {amount} Speed.\n"
        return result


class SafePassage(Class):
    """Create a defensive route through incoming magical pressure."""

    def __init__(self) -> None:
        super().__init__(
            "Safe Passage",
            "Raise Defense and Magic Defense for three turns; mapped floors strengthen the ward.",
        )
        self.cost = 9
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target
        result = super().use(user, user, **kwargs)
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        from ..classes import promotion_kits

        threshold = 0.35 if _has_talent(user, "seeker.master-cartographer") else 0.50
        amount = 10 if promotion_kits.level_mapping_progress(user) < threshold else 16
        duration = 4 if _has_talent(user, "seeker.sanctuary-route") else 3
        for stat in ("Defense", "Magic Defense"):
            effect = user.stat_effects[stat]
            effect.active = True
            effect.duration = max(int(effect.duration or 0), duration)
            effect.extra = max(int(effect.extra or 0), amount)
            effect.source = self.name
            result.effects_applied["Stat"].append(f"{stat} Buff")
        result.hit = True
        result.message = f"{user.name} establishes Safe Passage with +{amount} defenses.\n"
        return result
