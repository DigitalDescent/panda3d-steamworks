"""Render an HTML string as a full-window in-game Panda3D UI panel.

This sample uses `SteamHtmlSurfaceRenderer` and keeps the browser/card synced
with window size on resize.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from direct.gui.OnscreenText import OnscreenText
from panda3d_steamworks import SteamHTMLSurface
from panda3d_steamworks.html_surface import SteamHtmlSurfaceRenderer
from panda3d_steamworks.showbase import SteamShowBase


HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <style>
    :root {
      --bg0: #081423;
      --bg1: #102943;
      --accent: #2ebf91;
      --accent2: #7bffcf;
      --text: #f4f8ff;
      --muted: #a9c2d8;
      --panel: rgba(12, 24, 40, 0.82);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: 'Segoe UI', 'Trebuchet MS', sans-serif;
      background: transparent;
      display: grid;
      place-items: center;
    }

    .panel {
      width: min(900px, 92vw);
      border: 1px solid rgba(123, 255, 207, 0.35);
      border-radius: 18px;
      overflow: hidden;
      background: var(--panel);
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.35);
      backdrop-filter: blur(4px);
    }

    .head {
      padding: 16px 20px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.00));
    }

    .title {
      margin: 0;
      font-size: 22px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .pill {
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(123, 255, 207, 0.15);
      color: var(--accent2);
      font-size: 12px;
      letter-spacing: 0.07em;
      text-transform: uppercase;
      border: 1px solid rgba(123, 255, 207, 0.35);
    }

    .content {
      padding: 20px;
      display: grid;
      gap: 14px;
      color: var(--muted);
    }

    .row {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    button {
      border: 1px solid rgba(46, 191, 145, 0.5);
      background: linear-gradient(180deg, rgba(46,191,145,0.22), rgba(46,191,145,0.10));
      color: var(--text);
      padding: 10px 14px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 14px;
      transition: transform 100ms ease, filter 100ms ease;
    }

    button:hover {
      filter: brightness(1.08);
      transform: translateY(-1px);
    }

    .counter {
      margin-left: 8px;
      color: var(--text);
      font-weight: 600;
    }
  </style>
</head>
<body>
  <section class=\"panel\">
    <header class=\"head\">
      <h1 class=\"title\">Mission Control</h1>
      <span class=\"pill\">HTML Surface</span>
    </header>
    <div class=\"content\">
      <p>
        This panel is rendered by Steam HTML Surface and shown inside Panda3D.
      </p>
      <div class=\"row\">
        <button onclick=\"add()\">Increase Score</button>
        <button onclick=\"setStatus('Engines online')\">Set Status</button>
        <button onclick=\"setStatus('Route locked')\">Lock Route</button>
        <span class=\"counter\" id=\"counter\">Score: 0</span>
      </div>
      <p id=\"status\">Status: Ready</p>
    </div>
  </section>

  <script>
    let score = 0;

    function add() {
      score += 1;
      document.getElementById('counter').textContent = `Score: ${score}`;
      document.title = `Score ${score}`;
    }

    function setStatus(text) {
      document.getElementById('status').textContent = `Status: ${text}`;
    }
  </script>
</body>
</html>
"""


class HTMLSurfaceUIPanel(SteamShowBase):
    def __init__(self):
        super().__init__()

        self.disable_mouse()
        self.title = OnscreenText(
            text="Steam HTML Surface UI",
            pos=(0.0, 0.92),
            fg=(0.9, 0.98, 1.0, 1.0),
            scale=0.06,
            align=core.TextNode.A_center,
        )

        self.hint = OnscreenText(
            text="Move mouse over panel. Wheel scroll + left click are forwarded. R reloads.",
            pos=(0.0, -0.95),
            fg=(0.75, 0.86, 0.96, 1.0),
            scale=0.035,
            align=core.TextNode.A_center,
        )

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

    def _on_ready(self, handle: int):
        print(f"HTML surface ready (browser={handle})")
        SteamHTMLSurface.set_background_mode(handle, True)
        self.html_surface.load_html(HTML_TEMPLATE)

    def _reload(self):
        self.html_surface.reload()

    def _cleanup(self):
        self.html_surface.destroy()
        self.userExit()


if __name__ == "__main__":
    app = HTMLSurfaceUIPanel()
    app.run()
