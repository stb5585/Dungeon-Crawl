"""Healer class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Healer(Job):
    """
    Promotion: Healer -> Cleric -> Templar
                      |
                      -> Priest -> Archbishop
                      |
                      -> Monk   -> Master Monk
                      |
                      -> Bard   -> Troubadour

    """

    def __init__(self):
        super().__init__(
            name="Healer",
            description="Healers primary role in battle is to preserve the party with "
            "healing and protective spells. Well, how does that work when "
            "they are alone? Pretty much the same way!",
            str_plus=0,
            int_plus=1,
            wis_plus=2,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Quarterstaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.PaddedArmor(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Shield", "Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=1,
        )
