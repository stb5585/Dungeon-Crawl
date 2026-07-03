"""Ranger class definition."""

from __future__ import annotations

from .base import Job


class Ranger(Job):
    """
    Promotion: Pathfinder -> Ranger -> Beast Master
    Pros: Increased strength and dex gain; gain dual wielding with daggers; can use swords
        and 2-handed axes
    Cons: Lose access to attack spells, some weapons and armor, shields, and tomes
    Special Mechanic: can tame a beast to aid in and out of combat; companion strength
        affected by charisma
    """

    def __init__(self):
        super().__init__(
            name="Ranger",
            description="Rangers blend their deep wilderness expertise with fierce melee "
            "combat capabilities. Skilled in tracking and survival, they excel"
            " in close-quarters combat using precision and agility. Their true"
            " strength lies in their ability to tame and command powerful "
            "animals, forging bonds with beasts to fight alongside them. "
            "Rangers leverage their primal connection to nature and combat "
            "mastery, creating a formidable duo of human and beast.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=3,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=2,
            restrictions={
                "Weapon": ["Dagger", "Sword", "Longsword", "Battle Axe", "Polearm"],
                "OffHand": ["Dagger"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )
