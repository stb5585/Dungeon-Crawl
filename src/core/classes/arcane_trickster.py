"""ArcaneTrickster class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class ArcaneTrickster(Job):
    """
    Promotion: Footpad -> Spell Stealer -> Arcane Trickster
    Additional Pros: Increased intel gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Arcane Trickster",
            description="The Arcane Trickster elevates the Spell Stealer's "
            "cunning and arcane mastery to new heights. Adept at "
            "weaving magic and subterfuge, these versatile "
            "spellcasters manipulate the battlefield with illusions,"
            " stealth, and devastating arcane strikes. Their ability"
            " to enhance their physical attacks with magical force "
            "and cast debilitating spells ensures they are as "
            "dangerous in close quarters as from afar.",
            str_plus=0,
            int_plus=3,
            wis_plus=1,
            con_plus=0,
            cha_plus=1,
            dex_plus=2,
            att_plus=1,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=3,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.DragonRouge(),
                "Armor": items.StuddedLeather(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Dagger", "Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )
