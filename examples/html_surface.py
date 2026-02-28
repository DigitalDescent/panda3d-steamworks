"""Use the Steam HTML Surface to render web content.

Shows how to:
- Initialise the HTML Surface subsystem
- Create a browser instance asynchronously and handle the callback
- Load a URL once the browser handle is available
- Listen for navigation and title-change broadcast events

The HTML Surface provides a Chromium-based browser that can be used for
in-game web views (e.g. news pages, community hubs, or custom UI).
In a real game you would render the resulting texture to a Panda3D card.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamHTMLSurface


class HTMLSurfaceDemo(SteamShowBase):
    """App that creates an HTML Surface browser and handles its callbacks."""

    def __init__(self):
        super().__init__(windowType='none')

        self._browser_handle = None

        # ------------------------------------------------------------------
        # Listen for HTML Surface broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-HTML_BrowserReady", self._on_browser_ready)
        self.accept("Steam-HTML_StartRequest", self._on_start_request)
        self.accept("Steam-HTML_FinishedRequest", self._on_finished_request)
        self.accept("Steam-HTML_ChangedTitle", self._on_title_changed)
        self.accept("Steam-HTML_URLChanged", self._on_url_changed)

        # ------------------------------------------------------------------
        # Initialise the HTML Surface subsystem
        # ------------------------------------------------------------------
        ok = SteamHTMLSurface.init()
        print(f"HTMLSurface.init(): {ok}")

        if not ok:
            print("Failed to initialise HTML Surface.")
            self.userExit()
            return

        # ------------------------------------------------------------------
        # Create a browser (async — result comes via callback)
        # ------------------------------------------------------------------
        SteamHTMLSurface.create_browser("Panda3D Game", "")
        print("CreateBrowser requested (async) — waiting for callback...")

        self.accept("escape", self._cleanup)
        print("Press Escape to quit.\n")

    # ------------------------------------------------------------------
    # Callback handlers
    # ------------------------------------------------------------------
    def _on_browser_ready(self, result):
        """Fires when CreateBrowser completes.  We now have a valid handle."""
        print(f"[BROADCAST] BrowserReady: {result}")
        handle = result.get("browser_handle", result.get("unBrowserHandle", None))
        if handle is None:
            print("  Could not retrieve browser handle.")
            return

        self._browser_handle = handle
        print(f"  Browser handle: {handle}")

        # Configure and load a page
        SteamHTMLSurface.set_size(handle, 1280, 720)
        SteamHTMLSurface.load_url(handle, "https://store.steampowered.com", "")
        print("  Loading https://store.steampowered.com ...")

    def _on_start_request(self, result):
        """Fires when the browser begins loading a URL."""
        url = result.get("url", result.get("pchURL", "?"))
        print(f"[BROADCAST] StartRequest: {url}")
        # Allow the navigation to proceed
        if self._browser_handle is not None:
            SteamHTMLSurface.allow_start_request(self._browser_handle, True)

    def _on_finished_request(self, result):
        """Fires when a page finishes loading."""
        url = result.get("url", result.get("pchURL", "?"))
        print(f"[BROADCAST] FinishedRequest: {url}")

    def _on_title_changed(self, result):
        """Fires when the page title changes."""
        title = result.get("title", result.get("pchTitle", "?"))
        print(f"[BROADCAST] TitleChanged: {title}")

    def _on_url_changed(self, result):
        """Fires when the browser navigates to a new URL."""
        url = result.get("url", result.get("pchURL", "?"))
        print(f"[BROADCAST] URLChanged: {url}")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def _cleanup(self):
        if self._browser_handle is not None:
            SteamHTMLSurface.remove_browser(self._browser_handle)
            print("Browser removed.")
        SteamHTMLSurface.shutdown()
        self.userExit()


if __name__ == "__main__":
    demo = HTMLSurfaceDemo()
    demo.run()
