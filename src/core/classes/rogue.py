"""Rogue class definition."""

from __future__ import annotations

from .base import Job


class Rogue(Job):
    """
    Promotion: Footpad -> Thief -> Rogue
    Additional Pros: Ability to dual wield swords and maces in offhand; increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Rogue",
            description="Rogues rely on skill, stealth, and their foes' vulnerabilities to "
            "get the upper hand in any situation. They have a knack for finding "
            "the solution to just about any problem, demonstrating a "
            "resourcefulness and versatility that has no rival. They gain the "
            "ability to dual wield swords, maces, and fist weapons.",
            str_plus=0,
            int_plus=1,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=3,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Fist", "Dagger", "Sword", "Club"],
                "OffHand": ["Fist", "Dagger", "Sword", "Club"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )
