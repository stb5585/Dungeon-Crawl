"""KnightEnchanter class definition."""

from __future__ import annotations

from .base import Job


class KnightEnchanter(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Additional Pros: adds armor based on intel and mana percentage; additional dex gain
    Additional Cons: None
    """

    def __init__(self):
        super().__init__(
            name="Knight Enchanter",
            description=(
                "The Knight Enchanter weaves spell signatures through Arcane "
                "and Elemental Blade Charges, then shapes the pattern into "
                "weapon, ward, or bound-spell releases."
            ),
            str_plus=2,
            int_plus=1,
            wis_plus=0,
            con_plus=2,
            cha_plus=1,
            dex_plus=1,
            att_plus=4,
            def_plus=1,
            magic_plus=2,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Sword"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth", "Light"],
            },
            pro_level=3,
        )
