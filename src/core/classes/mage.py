"""Mage class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Mage(Job):
    """
    Promotion: Mage -> Sorcerer    -> Wizard
                    |
                    -> Warlock     -> Shadowcaster
                    |              |
                    |              -> Demonologist
                    |
                    -> Spellblade  -> Knight Enchanter
                    |
                    -> Summoner    -> Grand Summoner
    """

    def __init__(self):
        super().__init__(
            name="Mage",
            description="Mages possess exceptional aptitude for spell casting, able to "
            "destroy an enemy with the wave of a finger. Weaker and more "
            "vulnerable than any other class, they more than make up for it "
            "with powerful magics.",
            str_plus=0,
            int_plus=3,
            wis_plus=1,
            con_plus=0,
            cha_plus=1,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=3,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Quarterstaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.Tunic(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=1,
        )
