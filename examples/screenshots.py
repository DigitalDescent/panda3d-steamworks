"""Hook into the Steam screenshot system.

Shows how to:
- Hook screenshots so your app controls capture timing
- Listen for ScreenshotRequested (user pressed F12)
- Listen for ScreenshotReady (screenshot saved to library)
- Trigger screenshots programmatically

When screenshot hooking is enabled, pressing the Steam screenshot key
(default F12) will NOT automatically capture — instead the
Steam-ScreenshotRequested broadcast fires so your game can capture
the frame at the right moment without UI overlays.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamScreenshots


class ScreenshotDemo(SteamShowBase):
    """App that demonstrates screenshot hooking with proper callbacks."""

    def __init__(self):
        super().__init__(windowType='none')

        # ------------------------------------------------------------------
        # Listen for screenshot broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-ScreenshotRequested", self._on_screenshot_requested)
        self.accept("Steam-ScreenshotReady", self._on_screenshot_ready)

        # ------------------------------------------------------------------
        # Hook screenshots — your app is now responsible for captures
        # ------------------------------------------------------------------
        SteamScreenshots.hook_screenshots(True)
        print(f"Screenshots hooked: {SteamScreenshots.is_screenshots_hooked()}")
        print("Press F12 in Steam to trigger a ScreenshotRequested callback.")

        # ------------------------------------------------------------------
        # Trigger a screenshot programmatically
        # ------------------------------------------------------------------
        print("\nTriggering a screenshot programmatically ...")
        SteamScreenshots.trigger_screenshot()

        self.accept("escape", self._cleanup)
        print("\nWaiting for callbacks... (press Ctrl + C to quit)\n")

    # ------------------------------------------------------------------
    # Broadcast callback handlers
    # ------------------------------------------------------------------
    def _on_screenshot_requested(self, result):
        """Fires when the user presses the screenshot key (F12) while hooked."""
        print(f"[BROADCAST] ScreenshotRequested: {result}")
        # In a real game you would capture the frame buffer here and call
        # SteamScreenshots.write_screenshot() or add_screenshot_to_library().
        print("  -> Your app should capture the frame now.")

    def _on_screenshot_ready(self, result):
        """Fires when a screenshot has been saved to the Steam library."""
        print(f"[BROADCAST] ScreenshotReady: {result}")

    def _cleanup(self):
        """Unhook screenshots before exiting."""
        SteamScreenshots.hook_screenshots(False)
        print("Screenshots unhooked.")
        self.userExit()


if __name__ == "__main__":
    demo = ScreenshotDemo()
    demo.run()
