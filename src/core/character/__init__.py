"""Public character API.

The concrete character and its behavior live in focused submodules. Existing
imports from the character package remain supported.
"""

from .core import Character
from .models import (
    AbilityBook,
    AbsorptionResult,
    BLEED_MELEE_DAMAGE_TAKEN_MULTIPLIER,
    Combat,
    DamageReductionResult,
    DefenseResolution,
    EffectMap,
    InventoryMap,
    Level,
    POISON_HEALING_MULTIPLIER,
    Resource,
    STUN_IMMUNITY_TURNS_AFTER_EXPIRY,
    STUN_LEVEL_DIFF_CAP,
    STUN_LEVEL_DIFF_MULT_MAX,
    STUN_LEVEL_DIFF_MULT_MIN,
    STUN_LEVEL_DIFF_SCALE,
    Stats,
    StatusEffect,
    WeaponDamageResult,
    _class_name,
    _combat_level,
    armor_resistance_modifier,
    armor_spell_modifier,
    scaled_decay_function,
    sigmoid,
)
from .offense import random
