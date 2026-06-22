"""Priest class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Priest(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Pros: Access to the best healing and holy spells; only class that can equip the holy staff except Archbishop;
        increased intel and wisdom gain
    Cons: Can only equip cloth armor; lose access to shields; lower constitution gain
    """

    def __init__(self):
        super().__init__(
            name="Priest",
            description="A priest channels the holy light through prayer, accessing "
            "powerful regenerative and cleansing spells. While they can only "
            "equip cloth armor, they gain the ability to increase their "
            "defense at the expense of mana.",
            str_plus=0,
            int_plus=2,
            wis_plus=3,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=2,
            magic_plus=3,
            magic_def_plus=3,
            equipment={
                "Weapon": items.SerpentStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.GoldCloak(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )
