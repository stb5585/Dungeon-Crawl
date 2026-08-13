"""Spellblade-specific active and passive abilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Class, _load_yaml_ability

if TYPE_CHECKING:
    from typing import Any

    from ..character import Character


class KineticExplosion:
    """Send an Arcane explosion through every enemy."""

    def __new__(cls):
        return _load_yaml_ability(
            "kinetic_explosion.yaml",
            cls_name="KineticExplosion",
        )


class _SpellbladePassive(Class):
    """Base class for passive Spellblade skills."""

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
        self.passive = True
        self.cost = 0


class Breakdown(_SpellbladePassive):
    """Build a spell-defense weakness through successful melee hits."""

    def __init__(self) -> None:
        super().__init__(
            "Breakdown",
            "Each melee hit lowers that target's Magic Defense by 4, up to "
            "five stacks. The next damaging spell benefits and clears the stacks.",
        )


class CounterCharge(_SpellbladePassive):
    """Gain a typed blade charge after taking spell damage."""

    def __init__(self) -> None:
        super().__init__(
            "Counter Charge",
            "When a spell damages you in combat, gain an Arcane or Elemental "
            "blade charge matching its category.",
        )


class AmplifyArcane(_SpellbladePassive):
    """Amplify Arcane blade charges."""

    def __init__(self) -> None:
        super().__init__(
            "Amplify Arcane",
            "Arcane blade charges release at double power.",
        )


class AmplifyElemental(_SpellbladePassive):
    """Amplify Elemental blade charges."""

    def __init__(self) -> None:
        super().__init__(
            "Amplify Elemental",
            "Elemental blade charges release at double power.",
        )


class StorageCapacity(_SpellbladePassive):
    """Allow one additional charge of each blade-charge type."""

    def __init__(self) -> None:
        super().__init__(
            "Storage Capacity",
            "Store one additional Arcane charge and one additional Elemental charge.",
        )


class NovelShielding(Class):
    """Create a temporary damage-absorption pool from an equipped Tome."""

    def __init__(self) -> None:
        super().__init__(
            name="Novel Shielding",
            description=(
                "Create a three-turn shield with strength equal to twice the power "
                "of the equipped Tome."
            ),
        )
        self.cost = 20
        self.target_self = True

    @staticmethod
    def _equipped_tome(user: Character) -> Any | None:
        offhand = getattr(user, "equipment", {}).get("OffHand")
        if getattr(offhand, "subtyp", None) != "Tome":
            return None
        return offhand

    def is_available(
        self,
        user: Character,
        target: Character | None = None,
    ) -> bool:
        """Return whether a Tome is equipped and the user can pay the MP cost."""
        del target
        return (
            self._equipped_tome(user) is not None
            and int(getattr(getattr(user, "mana", None), "current", 0) or 0)
            >= self.cost
        )

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ):
        """Refresh the Tome-powered shield without stacking its pool."""
        del target, kwargs
        result = super().use(user, user)
        tome = self._equipped_tome(user)
        if tome is None:
            result.message = f"{user.name} must equip a Tome to use Novel Shielding.\n"
            return result
        if int(user.mana.current) < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        from ..classes import promotion_kits

        result.message = promotion_kits.activate_novel_shield(
            user,
            max(0, int(getattr(tome, "mod", 0) or 0) * 2),
        )
        return result
