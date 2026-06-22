"""Lycan class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Lycan(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Additional Pros: Can learn to transform into Red Dragon; increased constitution gain
    Additional Cons: Lower intel gain
    Special Mechanic: Can shapeshift into alternative forms
    """

    def __init__(self):
        super().__init__(
            name="Lycan",
            description="Unlike the lycans of mythology who have little choice in morphing "
            "into their animal form, these lycans have gained mastery over their"
            " powers to become something truly terrifying.",
            str_plus=1,
            int_plus=0,
            wis_plus=1,
            con_plus=2,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.EarthHammer(),
                "OffHand": items.NoOffHand(),
                "Armor": items.StuddedLeather(),
            },
            restrictions={
                "Weapon": ["Dagger", "Club", "Polearm", "Hammer", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )
