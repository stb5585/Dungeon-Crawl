"""Druid class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Druid(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Pros: gains animal abilities and statistics when shifted; increased strength and dex gain
    Cons: loses ability to wear medium armor and shields; lower intel gain
    """

    def __init__(self):
        super().__init__(
            name="Druid",
            description="Druids act as an extension of nature to call upon the elemental"
            " forces, embodying nature's wrath and mystique. This attunement "
            "with nature allows druids to emulate creatures of the animal world,"
            " transforming into them and gaining there specs and abilities. They"
            " lose the ability to wear medium armor and shields but gain "
            "natural weapons and armor when transformed.",
            str_plus=1,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.SerpentStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.Cuirboulli(),
            },
            restrictions={
                "Weapon": ["Dagger", "Club", "Polearm", "Hammer", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )
