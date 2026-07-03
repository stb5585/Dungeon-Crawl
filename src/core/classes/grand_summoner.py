"""GrandSummoner class definition."""

from __future__ import annotations

from .base import Job


class GrandSummoner(Job):
    """
    Promotion: Mage -> Summoner -> Grand Summoner
    Additional Pros: Summoned creatures have increased power
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Grand Summoner",
            description="The Grand Summoner represents the pinnacle of summoning "
            "mastery, channeling immense magical power to enhance "
            "their summoned creatures. These legendary conjurers can "
            "summon stronger, larger, and more formidable entities "
            "than ever before, each imbued with enhanced abilities and"
            " resilience. The bond between the Grand Summoner and "
            "their creatures is unbreakable, allowing for precise "
            "control and synergy.",
            str_plus=0,
            int_plus=2,
            wis_plus=2,
            con_plus=0,
            cha_plus=3,
            dex_plus=0,
            att_plus=0,
            def_plus=2,
            magic_plus=4,
            magic_def_plus=4,
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )
