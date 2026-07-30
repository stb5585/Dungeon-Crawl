"""Public data-driven ability API.

Implementations live in focused spell and skill modules. Existing imports from
the data-driven ability package remain supported.
"""

from .base import DataDrivenSpell
from .jump import DataDrivenJumpSkill
from .missile import DataDrivenMagicMissileSpell
from .movement import DataDrivenMovementSpell
from .skills import DataDrivenSkill, DataDrivenStatusSkill
from .special import DataDrivenChargingSkill, DataDrivenCustomSpell, DataDrivenWeaponSpell
from .spells import (
    DataDrivenHealSpell,
    DataDrivenStatusSpell,
    DataDrivenSupportSpell,
)

from src.core.abilities import Skill, Spell
from .base import (
    CombatResult,
    TYPE_CHECKING,
    _fate_floor,
    _floor_int,
    _floor_uniform,
    _get_heal_spell_class,
    _get_status_spell_class,
    _get_support_spell_class,
    random,
)
from .movement import _get_movement_spell_class
