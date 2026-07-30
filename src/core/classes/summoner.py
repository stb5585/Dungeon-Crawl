"""Summoner class definition."""

from __future__ import annotations

from .base import Job


class Summoner(Job):
    """
    Promotion: Mage -> Summoner -> Grand Summoner
    Pros: Increased charisma and dominion over powerful allies
    Cons: No longer gains attack spells and lower intelligence
    Special Mechanic: Summon Bonds - summoned allies grow stronger as they fight beside you.
    """

    def __init__(self):
        super().__init__(
            name="Summoner",
            description="The Summoner has dominion over distant realms, capable of "
            "calling forth powerful creatures to aid them in battle. These "
            "summoned entities range from ferocious beasts to mystical"
            " elementals, each with unique abilities tailored to specific "
            "combat needs. Summoners form bonds with their creatures, "
            "allowing for synergistic strategies and unparalleled "
            "versatility. Highly charismatic individuals will see the "
            "greatest increase in summoning power.",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=0,
            cha_plus=2,
            dex_plus=0,
            att_plus=0,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )
