"""Screen behavior for the modern character screen package."""

from ..town_base import TownScreenBase
from .core import CharacterCoreMixin
from .data import CharacterDataMixin
from .equipment import CharacterEquipmentMixin
from .layout import CharacterLayoutMixin
from .mechanics import CharacterMechanicsMixin


class ModernCharacterScreen(CharacterEquipmentMixin,CharacterMechanicsMixin,CharacterLayoutMixin,CharacterDataMixin,CharacterCoreMixin,TownScreenBase):
    """RPG-style character menu used by the standard pygame character flow."""
