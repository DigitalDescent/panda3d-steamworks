"""Use `SteamHtmlSurfaceRenderer` as an in-game web UI card in Panda3D."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks.html_surface import SteamHtmlSurfaceRenderer


class HTMLSurfaceDemo(SteamShowBase):
    """App that demonstrates the high-level HTML surface node wrapper."""

    def __init__(self):
        super().__init__()

        self.html_surface = SteamHtmlSurfaceRenderer(
            self,
            width=1920,
            height=1080,
            fullscreen=True,
            match_window_size=True,
            auto_resize_with_window=True,
            on_ready=self._on_ready,
        )

        self.accept("r", self._reload)
        self.accept("escape", self._cleanup)
        print("Controls: mouse move, mouse wheel, left-click, R reload, Esc quit")

    def _on_ready(self, handle: int):
        print(f"HTML surface ready (browser={handle})")
        self.html_surface.load_url("https://store.steampowered.com")

    def _reload(self):
        self.html_surface.reload()

    def _cleanup(self):
        self.html_surface.destroy()
        self.userExit()


if __name__ == "__main__":
    demo = HTMLSurfaceDemo()
    demo.run()
