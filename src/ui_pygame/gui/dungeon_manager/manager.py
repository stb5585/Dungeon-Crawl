"""Manager behavior for the dungeon manager package."""

from .core import DungeonCoreMixin
from .exploration import DungeonExplorationMixin
from .interactions import DungeonInteractionMixin
from .navigation import DungeonNavigationMixin
from .story import DungeonStoryMixin


class DungeonManager(DungeonExplorationMixin,DungeonStoryMixin,DungeonInteractionMixin,DungeonNavigationMixin,DungeonCoreMixin):
    """Coordinates dungeon input, interactions, combat, and rendering."""
