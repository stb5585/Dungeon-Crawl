"""Conjurer class definition."""

from __future__ import annotations

from .base import Job


class Conjurer(Job):
    """First Mage promotion devoted to short-lived independent conjurations."""

    def __init__(self) -> None:
        super().__init__(
            name="Conjurer",
            description=(
                "The Conjurer develops Constructs, Binding, Illusion and "
                "Movement, and Calling. Its called creatures remain short-lived; "
                "permanent Xenid bonds begin only with Thaumaturgist training."
            ),
            str_plus=0,
            int_plus=2,
            wis_plus=1,
            con_plus=0,
            cha_plus=2,
            dex_plus=1,
            att_plus=0,
            def_plus=1,
            magic_plus=3,
            magic_def_plus=3,
            restrictions={
                "Weapon": ["Dagger", "Staff"],
                "OffHand": ["Tome"],
                "Armor": ["Cloth"],
            },
            pro_level=2,
        )
