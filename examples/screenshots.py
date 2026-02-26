"""Hook into the Steam screenshot system.

When screenshot hooking is enabled, pressing the Steam screenshot key
(default F12) will NOT automatically capture — instead your game is
expected to handle it (e.g. via a callback) so you can capture the
frame at the right moment without UI overlays.
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamScreenshots


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    hooked = SteamScreenshots.is_screenshots_hooked()
    print(f"Screenshots currently hooked: {hooked}")

    # ------------------------------------------------------------------
    # Trigger a screenshot manually
    # ------------------------------------------------------------------
    print("\nTriggering a Steam screenshot ...")
    SteamScreenshots.trigger_screenshot()
    print("  Screenshot triggered!  Check your Steam screenshot library.")

    # ------------------------------------------------------------------
    # Hook / unhook screenshots
    # ------------------------------------------------------------------
    # When hooked, your app is responsible for capturing frames.
    # This is useful to avoid capturing debug UI or overlays.
    print("\nEnabling screenshot hook ...")
    SteamScreenshots.hook_screenshots(True)
    print(f"  Hooked: {SteamScreenshots.is_screenshots_hooked()}")

    time.sleep(2)

    print("Disabling screenshot hook ...")
    SteamScreenshots.hook_screenshots(False)
    print(f"  Hooked: {SteamScreenshots.is_screenshots_hooked()}")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
