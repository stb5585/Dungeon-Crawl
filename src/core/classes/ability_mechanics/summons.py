"""Summon recovery mechanics."""

from __future__ import annotations

from typing import Any


def heal_all_summons(character: Any, pct: float = 0.35) -> str:
    summons = getattr(character, "summons", {}) or {}
    if not summons:
        return f"{character.name} has no summons to heal.\n"
    lines = []
    for summon in summons.values():
        hp_max = max(1, int(getattr(summon.health, "max", 1) or 1))
        mp_max = max(1, int(getattr(summon.mana, "max", 1) or 1))
        hp = max(1, int(hp_max * pct))
        mp = max(1, int(mp_max * pct))
        before_hp = summon.health.current
        before_mp = summon.mana.current
        summon.health.current = min(hp_max, summon.health.current + hp)
        summon.mana.current = min(mp_max, summon.mana.current + mp)
        lines.append(
            f"{summon.name} recovers {summon.health.current - before_hp} HP "
            f"and {summon.mana.current - before_mp} MP."
        )
    return "\n".join(lines) + "\n"


def raise_all_summons(character: Any, pct: float = 0.25) -> str:
    summons = getattr(character, "summons", {}) or {}
    if not summons:
        return f"{character.name} has no summons to raise.\n"
    raised = []
    for summon in summons.values():
        if summon.health.current <= 0:
            summon.health.current = max(1, int(summon.health.max * pct))
            raised.append(summon.name)
    if not raised:
        return "No fallen summons answer the call.\n"
    return "Raised summons: " + ", ".join(raised) + ".\n"
