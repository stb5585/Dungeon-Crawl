"""Soulcatcher class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Soulcatcher(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Additional Pros: Chance to gain essence from enemies; increased strength gain
    Additional Cons: None
    Special Mechanic: gains power based on enemies slain
    """

    def __init__(self):
        super().__init__(
            name="Soulcatcher",
            description="The Soulcatcher is a mystic who has mastered the art of "
            "binding spirits and harnessing their power. As a promotion "
            "of the Shaman, they wield unparalleled control over "
            "elemental and spiritual energies, weaving them into "
            "devastating attacks or protective barriers. By capturing the"
            " essence of defeated foes, the Soulcatcher can unleash "
            "soul-charged magic upon enemies. Their deep connection to "
            "the spirit world grants them unique insight and power, "
            "making them both revered and feared on the battlefield.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.BattleGauntlet(),
                "OffHand": items.BattleGauntlet(),
                "Armor": items.Breastplate(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Club", "Staff"],
                "OffHand": ["Fist", "Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=3,
        )
