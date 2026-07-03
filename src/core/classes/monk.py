"""Monk class definition."""

from __future__ import annotations

from .base import Job


class Monk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Pros: Adds wisdom to damage rolls; gains special skills; increased strength and dex gain
    Cons: Can only wear light armor; loses access to spells; lower intel and wisdom gain
    """

    def __init__(self):
        super().__init__(
            name="Monk",
            description="Monks abandon the cloth to focus the mind into the body, harnessing "
            "the inner power of the chi. Monks specialize in hand-to-hand combat,"
            " adding both strength and wisdom to their melee damage.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=2,
            restrictions={
                "Weapon": ["Fist", "Staff"],
                "OffHand": ["Fist"],
                "Armor": ["Light"],
            },
            pro_level=2,
        )
