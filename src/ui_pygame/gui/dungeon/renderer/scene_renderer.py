"""Scene renderer behavior for the renderer package."""

from .commands import RendererCommandMixin
from .core import RendererCoreMixin
from .debug import RendererDebugMixin
from .overlays import RendererOverlayMixin
from .specials import RendererSpecialTileMixin


class SceneRenderer(RendererOverlayMixin,RendererSpecialTileMixin,RendererDebugMixin,RendererCommandMixin,RendererCoreMixin):
    """Render the dungeon scene from explicit quads and cached projections."""
