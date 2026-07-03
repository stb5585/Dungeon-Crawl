"""Troubadour class definition."""

from __future__ import annotations

from .base import Job


class Troubadour(Job):
    """
    Promotion: Healer -> Bard -> Troubadour
    Additional Pros: Increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Troubadour",
            description="The Troubadour is the pinnacle of the Bard's art, a legendary"
            " performer who wields songs and stories with unmatched "
            "mastery. Their melodies amplify their abilities, granting "
            "powerful buffs and healing over time, while their sharp wit "
            "and magical harmonies sow discord among foes. They are "
            "paragons of charisma, seamlessly blending support, "
            "enchantment, and clever combat tricks to uplift their "
            "companions and ensure victory through the power of "
            "performance.",
            str_plus=1,
            int_plus=1,
            wis_plus=1,
            con_plus=1,
            cha_plus=1,
            dex_plus=2,
            att_plus=1,
            def_plus=2,
            magic_plus=4,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Sword", "Staff"],
                "OffHand": ["Dagger", "Musical Instrument"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )
