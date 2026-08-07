"""Terminal Thaumaturgist class definition."""

from __future__ import annotations

from .base import Job


class Thaumaturgist(Job):
    """Terminal Mage promotion that perfects seven permanent Xenid bonds."""

    def __init__(self) -> None:
        super().__init__(
            name="Thaumaturgist",
            description=(
                "The Thaumaturgist perfects seven Xenid Callings, strengthening "
                "those permanent bonds with invocations, Miracles, revival, "
                "and conduit rites."
            ),
            str_plus=0,
            int_plus=3,
            wis_plus=3,
            con_plus=0,
            cha_plus=4,
            dex_plus=1,
            att_plus=0,
            def_plus=1,
            magic_plus=5,
            magic_def_plus=5,
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=3,
        )
