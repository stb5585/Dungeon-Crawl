"""BeastMaster class definition."""

from __future__ import annotations

from .base import Job


class BeastMaster(Job):
    """
    Promotion: Pathfinder -> Ranger -> Beast Master
    Additional Pros: Increased charisma gain; increased companion strength from charisma
    Additional Cons: Lose access to medium armor
    """

    def __init__(self):
        super().__init__(
            name="Beast Master",
            description="The Beast Master is the pinnacle of the Ranger's journey, "
            "embodying an unbreakable bond with the wild. Beast Masters "
            "thrive in harmony with their companion, fighting as one "
            "unified force. With heightened instincts and the ability "
            "to channel primal energy, they inspire and protect their "
            "allies, making them guardians of the natural world and "
            "champions of untamed strength.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=1,
            cha_plus=2,
            dex_plus=2,
            att_plus=4,
            def_plus=2,
            magic_plus=1,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Sword", "Longsword", "Battle Axe", "Polearm"],
                "OffHand": ["Dagger", "Crossbow"],
                "Armor": ["Light"],
            },
            pro_level=3,
        )
