"""Shaman class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Shaman(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Pros: Can dual wield fist weapons; can imbue weapons with elemental fury; increased
        strength and dex gain
    Cons: Loses access to cloth armor, tomes, and some weapons; lower intel gain
    """

    def __init__(self):
        super().__init__(
            name="Shaman",
            description="The Shaman is a master of the natural elements, channeling the "
            "raw forces of fire, water, earth, and air to devastate their "
            "enemies. By imbuing weapons with elemental fury, they transform "
            "mundane strikes into catastrophic blows. As warriors of nature, "
            "they bring balance to the battlefield, wielding power both "
            "destructive and enhancing.",
            str_plus=1,
            int_plus=0,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Cestus(),
                "OffHand": items.Cestus(),
                "Armor": items.ScaleMail(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger", "Club", "Staff"],
                "OffHand": ["Fist", "Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )
