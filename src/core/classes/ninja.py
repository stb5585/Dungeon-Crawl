"""Ninja class definition."""

from __future__ import annotations

from .base import Job


class Ninja(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Additional Pros: Gains access to class only Ninja Blade weapons
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Ninja",
            description="Since a Ninja desires quickness, they are very specific about the "
            "items they use. Ninjas are not allowed to wear most types of armor "
            "and other items. However, having access to special weapons that "
            "only they can use, Ninjas possess the skills of Critically hitting "
            "and Backstabbing their opponents, along with moderate thieving "
            "skills.",
            str_plus=0,
            int_plus=0,
            wis_plus=2,
            con_plus=0,
            cha_plus=2,
            dex_plus=3,
            att_plus=4,
            def_plus=1,
            magic_plus=1,
            magic_def_plus=4,
            restrictions={
                "Weapon": ["Fist", "Dagger", "Ninja Blade"],
                "OffHand": ["Fist", "Dagger", "Ninja Blade"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )
