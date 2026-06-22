"""Berserker class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Berserker(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Additional Pros: Can dual wield 2-handed weapons; additional charisma gain
    Additional Cons: Can only equip light armor
    Special Mechanic: Battle Scars - surviving combat with less than 10% health gives
        chance of permanent scar  TODO
    """

    def __init__(self):
        super().__init__(
            name="Berserker",
            description="Berserkers are combat masters, driven by pure rage and "
            "vengeance. Their strength is so great, they gain the "
            "ability to dual wield two-handed weapons. Their further "
            "reliance on maneuverability limits the type of armor to light "
            "armor.",
            str_plus=3,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=5,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Parashu(),
                "OffHand": items.Changdao(),
                "Armor": items.StuddedLeather(),
            },
            restrictions={
                "Weapon": ["Longsword", "Battle Axe", "Polearm", "Hammer"],
                "OffHand": ["Longsword", "Battle Axe", "Polearm", "Hammer"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )
