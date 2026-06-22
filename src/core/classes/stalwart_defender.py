"""StalwartDefender class definition."""

from __future__ import annotations

from .base import Job
from .. import items


class StalwartDefender(Job):
    """
    Promotion: Warrior -> Sentinel -> Stalwart Defender
    Additional Pros: Additional constitution gain
    Additional Cons: None
    Special Mechanic:  TODO
    """

    def __init__(self):
        super().__init__(
            name="Stalwart Defender",
            description="The Stalwart Defender embodies unyielding resilience "
            "and unmatched defensive mastery. These protectors are "
            "immovable bastions, capable of absorbing devastating "
            "blows and locking down enemies at will. With "
            "impenetrable defenses and a commanding presence, "
            "they are the epitome of strength and fortitude.",
            str_plus=2,
            int_plus=0,
            wis_plus=0,
            con_plus=4,
            cha_plus=0,
            dex_plus=1,
            att_plus=2,
            def_plus=5,
            magic_plus=0,
            magic_def_plus=4,
            equipment={
                "Weapon": items.Shamshir(),
                "OffHand": items.KiteShield(),
                "Armor": items.PlateMail(),
            },
            restrictions={
                "Weapon": ["Fist", "Sword", "Club"],
                "OffHand": ["Shield"],
                "Armor": ["Heavy"],
            },
            pro_level=3,
        )
