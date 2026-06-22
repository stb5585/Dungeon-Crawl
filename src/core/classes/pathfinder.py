"""Pathfinder class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Pathfinder(Job):
    """
    Promotion: Pathfinder -> Druid   -> Lycan
                          |          |
                          |          -> Archdruid
                          |
                          -> Diviner -> Astromancer
                          |
                          -> Shaman  -> Soulcatcher
                          |
                          -> Ranger  -> Beast Master
    """

    def __init__(self):
        super().__init__(
            name="Pathfinder",
            description="In philosophy, naturalism is the belief that only natural laws"
            " and forces operate in the universe. A pathfinder embraces "
            "this idea by being attuned to one or more of the various "
            "aspects of nature, mainly the 4 classical elements: Earth, "
            "Wind, Water, and Fire.",
            str_plus=0,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=1,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Dirk(),
                "OffHand": items.Buckler(),
                "Armor": items.HideArmor(),
            },
            restrictions={
                "Weapon": ["Dagger", "Club", "Polearm", "Hammer", "Staff"],
                "OffHand": ["Shield", "Tome"],
                "Armor": ["Cloth", "Light", "Medium"],
            },
            pro_level=1,
        )
