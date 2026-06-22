"""Astromancer class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class Astromancer(Job):
    """
    Promotion: Pathfinder -> Diviner -> Astromancer
    Additional Pros: can learn rank 2 enemy specials when cast against; increased intel gain
    Additional Cons: None
    Special Mechanic: Runic Alterations - defeating enemies with elemental spells gives chance
        to drop runes
    """

    def __init__(self):
        super().__init__(
            name="Astromancer",
            description="Classified among the forbidden arts, astromancers study the celestial "
            "forces that govern magic, destiny, and the hidden threads of fate. Through careful "
            "observation they can learn spells cast by friend and foe alike, gradually unraveling"
            " the mysteries of the arcane. Those who master the stars gain the power to bend "
            "probability itself, turning fortune against their enemies and ensuring destiny "
            "unfolds according to their design.",
            str_plus=0,
            int_plus=3,
            wis_plus=2,
            con_plus=1,
            cha_plus=1,
            dex_plus=0,
            att_plus=1,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=4,
            equipment={
                "Weapon": items.Rondel(),
                "OffHand": items.DragonRouge(),
                "Armor": items.CloakEnchantment(),
            },
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome", "Rod"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )
