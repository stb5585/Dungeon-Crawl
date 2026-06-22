"""Wizard class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Wizard(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Additional Pros: Increased dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Wizard",
            description="The Wizard is a master of arcane magic, unparalleled in their "
            "magical ability. Being able to cast the most powerful spells makes"
            " the wizard an ideal class for anyone who prefers to live fast "
            "and die hard if not properly prepared.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=0,
            cha_plus=1,
            dex_plus=1,
            att_plus=0,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=4,
            equipment={
                "Weapon": items.RuneStaff(),
                "OffHand": items.NoOffHand(),
                "Armor": items.CloakEnchantment(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )
