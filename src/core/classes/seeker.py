"""Seeker class definition."""

from __future__ import annotations

from .base import Job


class Seeker(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Additional Pros: Additional intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Seeker",
            description="Seekers are very good at moving through the dungeon, being able to"
            " levitate, locate other characters, and teleport. They can't "
            "directly kill monsters with their magical abilities, but a Seeker "
            "does well with a weapon in hand. They are also the best at "
            "mapping the dungeon and detecting any types of 'anomalies' they "
            "may encounter in the depths.",
            str_plus=2,
            int_plus=1,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=3,
        )
