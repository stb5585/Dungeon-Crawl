"""Warrior class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Warrior(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
                       |                |
                       |                -> Grandmaster of Arms
                       |
                       -> Paladin       -> Crusader
                       |
                       -> Lancer        -> Dragoon
                       |
                       -> Sentinel      -> Stalwart Defender
    """

    def __init__(self):
        super().__init__(
            name="Warrior",
            description="Warriors are weapon specialists that rely on strength and "
            "defense. While unable to cast spells, they have access to a wide"
            " variety of combat skills that make them deadly in combat. The "
            "most stout of the bass classes, this character is best for "
            "someone who wants to hack and slash their way through the game.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=2,
            cha_plus=0,
            dex_plus=1,
            att_plus=3,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=1,
            equipment={
                "Weapon": items.Rapier(),
                "OffHand": items.Aspis(),
                "Armor": items.HideArmor(),
            },
            restrictions={
                "Weapon": [
                    "Dagger",
                    "Sword",
                    "Club",
                    "Longsword",
                    "Battle Axe",
                    "Hammer",
                ],
                "OffHand": ["Shield"],
                "Armor": ["Light", "Medium", "Heavy"],
            },
            pro_level=1,
        )
