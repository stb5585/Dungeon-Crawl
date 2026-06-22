"""Paladin class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Paladin(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can cast healing spells; additional wisdom and charisma gain
    Cons: Cannot equip 2-handed weapons except hammers and cannot equip light armor; no dex
        and lower strength gain
    Special Mechanic: Oathbringer - choose a path of devotion that grants unique abilities
        and buffs  TODO
    """

    def __init__(self):
        super().__init__(
            name="Paladin",
            description="The Paladin is a holy knight, crusading in the name of good and "
            "order. Gaining some healing and damage spells, paladins become a"
            " more balanced class and are ideal for players who always forget"
            " to restock health potions.",
            str_plus=1,
            int_plus=0,
            wis_plus=2,
            con_plus=2,
            cha_plus=1,
            dex_plus=0,
            att_plus=2,
            def_plus=2,
            magic_plus=2,
            magic_def_plus=2,
            equipment={
                "Weapon": items.WarHammer(),
                "OffHand": items.Glagwa(),
                "Armor": items.Splint(),
            },
            restrictions={
                "Weapon": ["Sword", "Club", "Longsword", "Hammer"],
                "OffHand": ["Shield"],
                "Armor": ["Medium", "Heavy"],
            },
            pro_level=2,
        )
