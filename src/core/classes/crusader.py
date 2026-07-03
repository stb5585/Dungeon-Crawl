"""Crusader class definition."""

from __future__ import annotations

from .base import Job


class Crusader(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Additional Pros: additional strength gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Crusader",
            description="The Crusader is a holy warrior, who values order and justice "
            "above all else. Crusaders continue the path of the paladin, "
            "fully embracing all aspects that carry over.",
            str_plus=2,
            int_plus=0,
            wis_plus=2,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=3,
            def_plus=3,
            magic_plus=2,
            magic_def_plus=2,
            restrictions={
                "Weapon": ["Sword", "Club", "Longsword", "Hammer"],
                "OffHand": ["Shield"],
                "Armor": ["Medium", "Heavy"],
            },
            pro_level=3,
        )
