"""Sorcerer class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Sorcerer(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Earlier access to spells and access to higher level spells
    Cons: None
    Special Mechanic: Elemental Affinity Wheel TODO
    """

    def __init__(self):
        super().__init__(
            name="Sorcerer",
            description="A Sorcerer is someone who practices magic derived from "
            "supernatural, occult, or arcane sources. They spend most of "
            "their life reading massive tomes to expand their "
            "knowledge and the rest of the time applying that knowledge at "
            "the expense of anything in their path.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.SerpentStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.GoldCloak(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )
