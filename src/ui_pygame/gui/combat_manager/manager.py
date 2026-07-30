"""Manager behavior for the combat manager package."""

from .core import CombatManagerCoreMixin
from .lifecycle import CombatLifecycleMixin
from .outcomes import CombatOutcomeMixin
from .selections import CombatSelectionMixin


class GUICombatManager(CombatOutcomeMixin,CombatSelectionMixin,CombatLifecycleMixin,CombatManagerCoreMixin):
    """Coordinates pygame combat flow around the core battle engine."""
