"""SpellStealer class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class SpellStealer(Job):
    """
    Promotion: Footpad -> Spell Stealer -> Arcane Trickster
    Pros: Intel and wisdom gain; can use Tomes in offhand and can wear cloth armor
    Cons: Lower dex and no constitution gain; lose access to fist and club weapons
    Special Mechanic: can steal magic from enemies  TODO
    """

    def __init__(self):
        super().__init__(
            name="Spell Stealer",
            description="The Spell Stealer is an elite evolution of the Footpad, "
            "blending agility and cunning with mystical talent. Masters"
            " of magical deception, they can cast a variety of spells "
            "while uniquely able to steal magic from enemies. Spells "
            "directed at them may be absorbed or reflected back at "
            "their casters. Their versatility allows them to adapt to "
            "both offensive and defensive situations, disrupting foes' "
            "strategies while empowering themselves with stolen magic.",
            str_plus=0,
            int_plus=2,
            wis_plus=1,
            con_plus=0,
            cha_plus=1,
            dex_plus=2,
            att_plus=1,
            def_plus=1,
            magic_plus=4,
            magic_def_plus=2,
            equipment={
                "Weapon": items.Kris(),
                "OffHand": items.ElementalPrimer(),
                "Armor": items.Cuirboulli(),
            },
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Dagger", "Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=2,
        )
