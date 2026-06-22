"""Bard class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Bard(Job):
    """
    Promotion: Healer -> Bard -> Troubadour
    Pros: Gain access to musical instruments, can dual wield daggers; gains songs that have affects in and out of
      combat; increased strength and dex gain
    Cons: Lose access to certain priest spells; lower wisdom gain
    Special Mechanic: Plays songs that boost self, hurt foes, or affects actions out of combat  TODO
    """

    def __init__(self):
        super().__init__(
            name="Bard",
            description="The Bard is a master of performance and inspiration, blending "
            "healing arts with the power of music and storytelling. They can "
            "weave enchanting melodies to bolster their own strength, restore "
            "health, and demoralize enemies. Bards excel at turning the tide of "
            "battle through clever improvisation, crowd control, and "
            "spellcasting.",
            str_plus=1,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=1,
            att_plus=1,
            def_plus=1,
            magic_plus=3,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.Lute(),
                "Armor": items.Cuirboulli(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword", "Staff"],
                "OffHand": ["Dagger", "Musical Instrument"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )
