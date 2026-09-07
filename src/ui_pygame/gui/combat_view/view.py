"""View behavior for the combat view package."""

from .core import CombatViewCoreMixin
from .overlay import CombatOverlayMixin
from .rendering import CombatRenderingMixin
from .sprites import CombatSpriteMixin
from .status import CombatStatusMixin


class CombatView(
    CombatOverlayMixin,
    CombatRenderingMixin,
    CombatSpriteMixin,
    CombatStatusMixin,
    CombatViewCoreMixin,
):
    """Renders combat state and transient presentation effects."""
