"""Sentinel class definition."""

from __future__ import annotations

from .base import Job


class Sentinel(Job):
    """
    Promotion: Warrior -> Sentinel -> Stalwart Defender
    Pros: Increased constitution gain
    Cons: Can only wear heavy armor and cannot equip 2-handed weapons
    Special Mechanic: Resolve - guard and mitigate pressure to fuel shield actions.
    """

    def __init__(self):
        super().__init__(
            name="Sentinel",
            description="Masters of defensive tactics, Sentinels excel at enduring "
            "heavy assaults. Equipped with impenetrable shields and an array"
            " of defensive skills, this class specializes in mitigating "
            "damage, taunting enemies, and bolstering their resilience. "
            "Their unique abilities allow them to reflect enemy strikes "
            "and maintain a near-impervious stance against even the fiercest"
            " foes.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=3,
            cha_plus=0,
            dex_plus=1,
            att_plus=1,
            def_plus=4,
            magic_plus=0,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Fist", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Heavy"],
            },
            pro_level=2,
        )
