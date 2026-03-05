# effects/__init__.py
from .base import Effect
from .damage import DamageEffect
from .healing import HealEffect, RegenEffect
from .status import StatusEffect
from .buffs import (
    StatModifierEffect,
    AttackBuffEffect,
    AttackDebuffEffect,
    DefenseBuffEffect,
    DefenseDebuffEffect,
    MagicBuffEffect,
    MagicDebuffEffect,
    SpeedBuffEffect,
    SpeedDebuffEffect,
    MultiStatBuffEffect,
    ResistanceEffect,
)
from .composite import (
    ConditionalEffect,
    CompositeEffect,
    ChanceEffect,
    ScalingEffect,
    LifestealEffect,
    ReflectDamageEffect,
    DamageOverTimeEffect,
    DispelEffect,
    ShieldEffect,
)

__all__ = [
    # Base
    "Effect",
    # Damage
    "DamageEffect",
    # Healing
    "HealEffect",
    "RegenEffect",
    # Status
    "StatusEffect",
    # Buffs/Debuffs
    "StatModifierEffect",
    "AttackBuffEffect",
    "AttackDebuffEffect",
    "DefenseBuffEffect",
    "DefenseDebuffEffect",
    "MagicBuffEffect",
    "MagicDebuffEffect",
    "SpeedBuffEffect",
    "SpeedDebuffEffect",
    "MultiStatBuffEffect",
    "ResistanceEffect",
    # Composite
    "ConditionalEffect",
    "CompositeEffect",
    "ChanceEffect",
    "ScalingEffect",
    "LifestealEffect",
    "ReflectDamageEffect",
    "DamageOverTimeEffect",
    "DispelEffect",
    "ShieldEffect",
]
