"""Shadowcaster class definition."""

from __future__ import annotations

from .base import Job


class Shadowcaster(Job):
    """
    Promotion: Mage -> Warlock -> Shadowcaster
    Additional Pros: Increased intel, wisdom, and dex gain
    Additional Cons: Decreased charisma gain
    Special Mechanic:
    """

    def __init__(self):
        super().__init__(
            name="Shadowcaster",
            description="The Shadowcaster is highly attuned to the dark arts and can "
            "conjure the most demonic of powers, including the practicing"
            " of forbidden blood magic.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=1,
            cha_plus=0,
            dex_plus=1,
            att_plus=1,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )
