"""Models behavior for the renderer package."""

from dataclasses import dataclass

from ..geometry import Quad


@dataclass(frozen=True)
class RenderCommand:
    depth: int
    order: int
    panel_id: str
    texture_key: str
    quad: Quad
    darkness: float
