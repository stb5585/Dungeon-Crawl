"""Warlock class definition."""

from __future__ import annotations

from .base import Job


class Warlock(Job):
    """
    Promotion: Mage -> Warlock -> Shadowcaster
                               |
                               -> Demonologist
    Pros: Higher charisma and constitution gain; access to additional skills; gains access to shadow spells and familiar
    Cons: Lower intelligence gain and limited access to higher level spells; lose access to learned arcane Mage spells
    Special Mechanic: Gains familiar that sometimes acts in or out of combat
    """

    def __init__(self):
        super().__init__(
            name="Warlock",
            description="The Warlock specializes in the dark arts, forsaking the arcane "
            "training learned as a Mage. However this focus unlocks powerful "
            "abilities, including the ability to summon a familiar to aid "
            "them.",
            str_plus=0,
            int_plus=2,
            wis_plus=1,
            con_plus=1,
            cha_plus=2,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=2,
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )
