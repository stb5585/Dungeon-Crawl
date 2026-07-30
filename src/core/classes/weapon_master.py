"""WeaponMaster class definition."""

from __future__ import annotations

from .base import Job


class WeaponMaster(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
                                        |
                                        -> Grandmaster of Arms
    Pros: Can dual wield some one handed weapons; higher dexterity gain
    Cons: Cannot use shields or heavy armor; lower constitution gain
    Special Mechanic: Weapon Discipline - gain proficiency with weapon types in worthy battles.
    """

    def __init__(self):
        super().__init__(
            name="Weapon Master",
            description="Weapon Masters focus on the mastery of weapons and their"
            " skill with them. They can equip many weapons and learn "
            "the ability to dual wield one-handed weapons. Since Weapon"
            " Masters rely on agility, they lose the ability to "
            "wear heavy armor and shields.",
            str_plus=2,
            int_plus=1,
            wis_plus=0,
            con_plus=1,
            cha_plus=0,
            dex_plus=2,
            att_plus=4,
            def_plus=2,
            magic_plus=0,
            magic_def_plus=2,
            restrictions={
                "Weapon": [
                    "Fist",
                    "Dagger",
                    "Sword",
                    "Club",
                    "Longsword",
                    "Battle Axe",
                    "Polearm",
                    "Hammer",
                ],
                "OffHand": ["Fist", "Dagger", "Sword", "Club"],
                "Armor": ["Light", "Medium"],
            },
            pro_level=2,
        )
