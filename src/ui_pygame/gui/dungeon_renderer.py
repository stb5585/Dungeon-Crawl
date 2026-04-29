from __future__ import annotations

from .dungeon.assets import TextureLibrary
from .dungeon.overlays import OverlayRenderer
from .dungeon.renderer import SceneRenderer


class DungeonRenderer:
    """Facade for the modular dungeon renderer implementation."""

    def __init__(self, presenter):
        self.presenter = presenter
        self.screen = presenter.screen
        self.width = presenter.width
        self.height = presenter.height

        self.textures = TextureLibrary()
        self.scene_renderer = SceneRenderer(presenter, self.textures)
        self.overlays = OverlayRenderer(presenter)

    def _refresh_screen_refs(self) -> None:
        self.screen = self.presenter.screen
        self.width, self.height = self.screen.get_size()

    def render_dungeon_view(self, player_char, world_dict):
        self._refresh_screen_refs()
        self.scene_renderer.render(player_char, world_dict)
        self.overlays.render_vignette()

    def render_message_area(self, messages, scroll_offset=0, lines_per_page=4):
        self._refresh_screen_refs()
        self.overlays.render_message_area(messages, scroll_offset=scroll_offset, lines_per_page=lines_per_page)

    def trigger_damage_flash(self, duration_ms=700, alpha=255, color=(255, 32, 16)):
        self.overlays.trigger_damage_flash(duration_ms=duration_ms, alpha=alpha, color=color)

    def render_damage_flash(self):
        self._refresh_screen_refs()
        self.overlays.render_damage_flash()
