"""Inquisitor class definition."""

from __future__ import annotations

from .base import Job


class Inquisitor(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Pros: Increased strength and constitution gain; ability to perceive enemy status and weaknesses; access to medium
          armor, shields, and some spells; increased resistance to shadow damage
    Cons: Lower dexterity and charisma gain; lose ability to dual wield and stealth skills and access to fist weapons
    """

    def __init__(self):
        super().__init__(
            name="Inquisitor",
            description="Inquisitors exchange the stealth of the shadows for a pure"
            "distain. They excel at rooting out hidden secrets and "
            "unraveling mysteries. They rely on a sharp eye for detail, "
            "but also on a finely honed ability to read the words and "
            "deeds of other creatures to determine their true intent. "
            "They excel at defeating creatures that hide in the shadows "
            " and their mastery of lore and sharp eye make them "
            "well-equipped to expose and end hidden evils.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            restrictions={
                "Weapon": ["Dagger", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )
