"""Spellblade class definition."""

from __future__ import annotations

from .base import Job


class Spellblade(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Pros: Adds melee damage based on mana percentage and level; higher strength and constitution gain; can equip swords
      and light armor
    Cons: Lower intelligence and wisdom gain; cannot equip staves; gains spells at a much slower pace
    """

    def __init__(self):
        super().__init__(
            name="Spellblade",
            description="The Spellblade combines a magical affinity with a higher level"
            " of martial prowess from the other magical classes. While they"
            " no longer gain many of the same arcane spells, the spellblade"
            " has unlocked the ability to channel the learned magical power"
            " through their blade to devastate enemies.",
            str_plus=2,
            int_plus=1,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=3,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=2,
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )
