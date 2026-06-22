"""Dragoon class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Dragoon(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Additional Pros: additional dex gain
    Additional Cons: Lose access to medium armor
    """

    def __init__(self):
        super().__init__(
            name="Dragoon",
            description="Masters of spears, lances, and polearms and gifted with "
            "supernatural abilities, Dragoons have become legendary for their"
            " grace and power. Their intense training, said to have been "
            "passed down by the dragon riders of old, allows these warriors to"
            " leap unnaturally high into the air and strike their foes with "
            "deadly force from above.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=2,
            att_plus=4,
            def_plus=3,
            magic_plus=0,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Naginata(),
                "OffHand": items.KiteShield(),
                "Armor": items.PlateMail(),
            },
            restrictions={
                "Weapon": ["Sword", "Polearm"],
                "OffHand": ["Shield"],
                "Armor": ["Heavy"],
            },
            pro_level=3,
        )
