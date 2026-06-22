"""Lancer class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Lancer(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; charisma gain
    Cons: Cannot equip other 2-handed weapons or dual wield; loses access to light armor
    Special Mechanic: Jump ability takes 1 turn to complete and can be modified by certain skills
    """

    def __init__(self):
        super().__init__(
            name="Lancer",
            description="Lancers are typically more at home on the back of a horse but one"
            " benefit this affords is the skill to wield a two-handed polearm "
            "while also using a shield. They are also adept at leaping high "
            "into the air and driving that polearm into their enemies.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=3,
            def_plus=3,
            magic_plus=0,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Halberd(),
                "OffHand": items.Glagwa(),
                "Armor": items.Splint(),
            },
            restrictions={
                "Weapon": ["Sword", "Polearm"],
                "OffHand": ["Shield"],
                "Armor": ["Medium", "Heavy"],
            },
            pro_level=2,
        )
