"""Archbishop class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Archbishop(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Additional Pros: Only class that can create and equip the Princess Guard; increased intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Archbishop",
            description="An archbishop attunes with the holy light for the most "
            "powerful healing, protective, and holy magics available.",
            str_plus=0,
            int_plus=3,
            wis_plus=3,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=1,
            def_plus=2,
            magic_plus=4,
            magic_def_plus=3,
            equipment={
                "Weapon": items.HolyStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.CloakEnchantment(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )
