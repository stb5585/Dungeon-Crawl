"""MasterMonk class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class MasterMonk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Additional Pros: increased constitution gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Master Monk",
            description="A master monk has fully attuned to the power of the chi, "
            "becoming unparalleled at dealing damage with fists or a "
            "staff.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=4,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=3,
            equipment={
                "Weapon": items.BattleGauntlet(),
                "OffHand": items.BattleGauntlet(),
                "Armor": items.StuddedLeather(),
            },
            restrictions={
                "Weapon": ["Fist", "Staff"],
                "OffHand": ["Fist"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )
