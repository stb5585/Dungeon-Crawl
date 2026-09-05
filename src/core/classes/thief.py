"""Thief class definition."""

from __future__ import annotations

from .base import Job


def has_thief_talent(character, talent_key: str) -> bool:
    """Return whether a Thief-line talent has been purchased."""
    try:
        from ..progression import has_talent

        return has_talent(character, talent_key)
    except (AttributeError, KeyError, TypeError, ValueError):
        return False


class Thief(Job):
    """
    Promotion: Footpad -> Thief-> Rogue
    Pros: Access to stealth abilities earlier than other classes; gains bonus to damage from dex; increased
        intel gain
    Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Thief",
            description="Thieves prefer stealth over brute force, although a well-placed "
            "backstab is still highly effective. They gain stealth abilities "
            "more quickly than other classes and are typically more well-"
            "balanced.",
            str_plus=0,
            int_plus=1,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=2,
            att_plus=2,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Fist", "Dagger", "Sword", "Club"],
                "OffHand": ["Fist", "Dagger"],
                "Armor": ["Light"],
            },
            pro_level=2,
        )
