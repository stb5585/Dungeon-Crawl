"""Assassin class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Assassin(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills; can use fist
      weapons in the offhand slot; gains bonus to damage from dex
    Cons: Lower constitution; can only equip daggers or fist weapons
    """

    def __init__(self):
        super().__init__(
            name="Assassin",
            description="You focus your training on the grim art of death. Those who "
            "adhere to this archetype are diverse: hired killers, spies, "
            "bounty hunters, and even specially anointed priests trained to "
            "exterminate  the enemies of their deity. Stealth, poison, and "
            "disguise help you eliminate your foes with deadly efficiency.",
            str_plus=0,
            int_plus=0,
            wis_plus=1,
            con_plus=0,
            cha_plus=2,
            dex_plus=3,
            att_plus=3,
            def_plus=1,
            magic_plus=1,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.Kris(),
                "Armor": items.Cuirboulli(),
            },
            restrictions={
                "Weapon": ["Fist", "Dagger"],
                "OffHand": ["Fist", "Dagger"],
                "Armor": ["Light"],
            },
            pro_level=2,
        )
