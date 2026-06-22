"""Cleric class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Cleric(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Pros: Can equip medium armor; gains additional protective abilities including turn undead; increased strength and
        constitution
    Cons: gains fewer healing spells compared to Priest class; no longer gains holy damage spells; lose access to tomes;
        lower intel gain
    """

    def __init__(self):
        super().__init__(
            name="Cleric",
            description="Where the paladin is a warrior that can heal, a cleric is a "
            "healer that can hold their own in combat. The biggest difference"
            " is that the cleric cannot equip heavy armor (yet...) but gain "
            "additional protective abilities that paladins do not.",
            str_plus=1,
            int_plus=0,
            wis_plus=2,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.WarHammer(),
                "OffHand": items.Glagwa(),
                "Armor": items.ScaleMail(),
            },
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )
