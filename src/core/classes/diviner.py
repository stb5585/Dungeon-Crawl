"""Diviner class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Diviner(Job):
    """
    Promotion: Pathfinder -> Diviner -> Astromancer
    Pros: Increased intel and wisdom gain; gain access to time magic
    Cons: loses access to shields and some weapon choices; lower dex gain
    Special Mechanic: similar to a Blue Mage, gains spells from enemy use
    """

    def __init__(self):
        super().__init__(
            name="Diviner",
            description="A diviner works with nature to balance the four classical "
            "elements of Earth, Wind, Water, and Fire, and can learn certain "
            "spells cast against them within these domains. Diviners are also "
            "hyper aware of their surroundings, limiting the effect of traps "
            "and magic effects.",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.ElementalPrimer(),
                "Armor": items.GoldCloak(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome", "Rod"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )
