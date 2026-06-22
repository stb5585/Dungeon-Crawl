"""Templar class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Templar(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Additional Pros: Can equip heavy armor and hammers; increased strength and dex gain
    Additional Cons: lose access to staff weapons; lower wisdom gain
    """

    def __init__(self):
        super().__init__(
            name="Templar",
            description="A templar exemplifies the best of both worlds, able to heal and"
            " protect while also being able to dish out quite a bit of damage"
            " along the way. While a templar is right at home with a mace and"
            " a shield, they have also trained in the art of the 2-handed "
            "hammer.",
            str_plus=2,
            int_plus=0,
            wis_plus=1,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Pernach(),
                "OffHand": items.KiteShield(),
                "Armor": items.PlateMail(),
            },
            restrictions={
                "Weapon": ["Club", "Hammer"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium", "Heavy"],
            },
            pro_level=3,
        )
