"""Compatibility composition for pygame combat selections."""

from .selection_abilities import AbilitySelectionMixin
from .selection_class_mechanics import ClassMechanicSelectionMixin
from .selection_special import SpecialSelectionMixin
from .selection_support import SelectionSupportMixin


class CombatSelectionMixin(
    SpecialSelectionMixin,
    AbilitySelectionMixin,
    ClassMechanicSelectionMixin,
    SelectionSupportMixin,
):
    """Compose the focused combat-selection responsibilities."""
