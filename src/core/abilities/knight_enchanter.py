"""Knight Enchanter Blade Weave release abilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Class

if TYPE_CHECKING:
    from typing import Any

    from ..character import Character


class _WeaveRelease(Class):
    """Base class for releases that consume a prepared weave and charges."""

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
        self.cost = 0
        self.resource_type = "Blade Charges"

    def is_available(
        self,
        user: Character,
        target: Character | None = None,
    ) -> bool:
        """Return whether the user has a Foundation and at least one charge."""
        del target
        from ..classes import promotion_kits

        return promotion_kits.weave_release_available(user)


class AegisWeave(_WeaveRelease):
    """Convert the current pattern and charges into a temporary ward."""

    def __init__(self) -> None:
        super().__init__(
            "Aegis Weave",
            "Consume all Blade Charges and the current pattern to create a "
            "temporary ward shaped by its Foundation and Accent.",
        )
        self.target_self = True

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.aegis_weave(user)


class Spellbind(_WeaveRelease):
    """Bind the current pattern into the next damaging spell hit."""

    def __init__(self) -> None:
        super().__init__(
            "Spellbind",
            "Consume all Blade Charges and the current pattern to empower the "
            "next damaging spell hit within three turns.",
        )

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.spellbind(user)


class _KnightEnchanterPassive(Class):
    """Base class for passive Blade Weave training."""

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
        self.passive = True
        self.cost = 0


class CleavingEdge(_KnightEnchanterPassive):
    """Carry offensive releases into adjacent hostile slots."""

    def __init__(self) -> None:
        super().__init__(
            "Cleaving Edge",
            "Offensive Weave Releases also affect enemies adjacent to the primary target.",
        )


class ResonantStrike(_KnightEnchanterPassive):
    """Preserve one spent blade charge after a release."""

    def __init__(self) -> None:
        super().__init__(
            "Resonant Strike",
            "After releasing a Weave, preserve one spent blade charge. The "
            "Foundation's matching type is preserved when possible.",
        )


class EchoingBlade(_KnightEnchanterPassive):
    """Sometimes repeat the released effect on the following turn."""

    def __init__(self) -> None:
        super().__init__(
            "Echoing Blade",
            "Weave Releases have a 25% chance to repeat their effect at the "
            "start of your next turn.",
        )


class ArcaneRiposte(_KnightEnchanterPassive):
    """Guarantee that a parry counter can release a prepared weave."""

    def __init__(self) -> None:
        super().__init__(
            "Arcane Riposte",
            "Parry immediately releases a prepared Weave through its counterattack.",
        )


class WeaveReservoir(_KnightEnchanterPassive):
    """Regenerate while both blade-charge pools are full."""

    def __init__(self) -> None:
        super().__init__(
            "Weave Reservoir",
            "At the start of your turn, full Arcane and Elemental charge pools "
            "restore 3% of maximum HP and MP.",
        )


class ReDebuff(_KnightEnchanterPassive):
    """Refresh negative effects through offensive releases."""

    def __init__(self) -> None:
        super().__init__(
            "Re-debuff",
            "Offensive Weave Releases refresh active negative status effects "
            "on affected enemies to at least three turns.",
        )


class DefensiveRelease(_KnightEnchanterPassive):
    """Replace Defend with a stackable boost to the next release."""

    def __init__(self) -> None:
        super().__init__(
            "Defensive Release",
            "Replaces Defend. Each use increases the next Weave Release by "
            "25%, stacking up to three times; releasing consumes all stacks.",
        )


class StorageCapacity2(_KnightEnchanterPassive):
    """Increase both typed blade-charge pools by two."""

    def __init__(self) -> None:
        super().__init__(
            "Storage Capacity II",
            "Increase the number of Arcane and Elemental Blade Charges that "
            "can be held by 2. This stacks with Storage Capacity.",
        )


class QuickRecharge(_KnightEnchanterPassive):
    """Repeat a weapon-triggered release across a multi-hit attack."""

    def __init__(self) -> None:
        super().__init__(
            "Quick Recharge",
            "When releasing a Weave with a multi-hit attack, apply its effects "
            "to each successful hit in that attack.",
        )
