"""Footpad class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Footpad(Job):
    """
    Promotion: Footpad -> Thief         -> Rogue
                       |
                       -> Inquisitor    -> Seeker
                       |
                       -> Assassin      -> Ninja
                       |
                       -> Spell Stealer -> Arcane Trickster
    """

    def __init__(self):
        super().__init__(
            name="Footpad",
            description="Footpads are agile and perceptive, with an natural ability of "
            "deftness. While more than capable of holding their own in hand-"
            "to-hand combat, they truly excel at subterfuge. Footpads are the"
            " only base class that can dual wield, albeit the offhand weapon "
            "must be a dagger.",
            str_plus=0,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=2,
            att_plus=2,
            def_plus=1,
            magic_plus=1,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Dirk(),
                "OffHand": items.Dirk(),
                "Armor": items.PaddedArmor(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Sword", "Club"],
                "OffHand": ["Fist", "Dagger"],
                "Armor": ["Light"],
            },
            pro_level=1,
        )
