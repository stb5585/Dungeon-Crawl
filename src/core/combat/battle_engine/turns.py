"""Compatibility composition for battle turn-phase behavior."""

from .area_resolution import AreaActionResolutionMixin
from .turn_execution import TurnExecutionMixin
from .turn_lifecycle import TurnLifecycleMixin
from .turn_preparation import TurnPreparationMixin
from .turn_resolution import TurnResolutionMixin


class BattleTurnMixin(
    TurnPreparationMixin,
    TurnExecutionMixin,
    AreaActionResolutionMixin,
    TurnResolutionMixin,
    TurnLifecycleMixin,
):
    """Compose preparation, execution, resolution, and lifecycle phases."""
