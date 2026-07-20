"""Hierophant class definition."""

from __future__ import annotations

from .base import Job


class Hierophant(Job):
    """
    Promotion: Healer -> Cleric -> Hierophant
    Additional Pros: Keeps staff and shield combat while deepening Devotion as a divine battle-caster.
    Additional Cons: Cannot wear medium or heavy armor and does not gain Templar hammer training.
    """

    def __init__(self):
        super().__init__(
            name="Hierophant",
            description="A hierophant carries the cleric's shield and holy resolve "
            "into a more mystical form of combat. Staff, ward, and prayer move "
            "together, letting the hierophant stand forward without abandoning "
            "the healer's spellcraft.",
            str_plus=1,
            int_plus=1,
            wis_plus=3,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=2,
            def_plus=2,
            magic_plus=3,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Club", "Staff"],
                "OffHand": ["Shield"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )
