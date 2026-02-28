"""Steam overlay, utility queries, and platform information.

Shows how to:
- Query Steam utility info (app ID, language, battery, etc.)
- Open the Steam overlay programmatically
- Listen for GameOverlayActivated broadcast callbacks
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamUtils, SteamFriends


class OverlayDemo(SteamShowBase):
    """App that opens the Steam overlay and listens for activation events."""

    def __init__(self):
        super().__init__(windowType='none')

        # ------------------------------------------------------------------
        # Listen for overlay activation
        # ------------------------------------------------------------------
        self.accept("Steam-GameOverlayActivated", self._on_overlay)

        # ------------------------------------------------------------------
        # General utility info
        # ------------------------------------------------------------------
        print("Steam Utility Information")
        print(f"  App ID                : {SteamUtils.get_app_id()}")
        print(f"  UI language           : {SteamUtils.get_steam_ui_language()}")
        print(f"  IP country            : {SteamUtils.get_ip_country()}")
        print(f"  Server real time      : {SteamUtils.get_server_real_time()}")
        print(f"  Secs since app active : {SteamUtils.get_seconds_since_app_active()}")
        print(f"  IPC call count        : {SteamUtils.get_ipc_call_count()}")

        battery = SteamUtils.get_current_battery_power()
        if battery == 255:
            print(f"  Battery power         : AC powered (plugged in)")
        else:
            print(f"  Battery power         : {battery}%")

        # ------------------------------------------------------------------
        # Overlay status
        # ------------------------------------------------------------------
        print(f"\nOverlay")
        print(f"  Overlay enabled       : {SteamUtils.is_overlay_enabled()}")
        print(f"  Overlay needs present : {SteamUtils.overlay_needs_present()}")

        # ------------------------------------------------------------------
        # Platform / environment detection
        # ------------------------------------------------------------------
        print(f"\nPlatform")
        print(f"  Running in VR         : {SteamUtils.is_steam_running_in_vr()}")
        print(f"  Big Picture mode      : {SteamUtils.is_steam_in_big_picture_mode()}")
        print(f"  Steam Deck            : {SteamUtils.is_steam_running_on_steam_deck()}")
        print(f"  China launcher        : {SteamUtils.is_steam_china_launcher()}")

        # ------------------------------------------------------------------
        # Open Steam Overlay programmatically
        # ------------------------------------------------------------------
        # Common dialog names: "Friends", "Community", "Players",
        # "Settings", "OfficialGameGroup", "Stats", "Achievements"
        print("\nOpening the Steam overlay to the Achievements page ...")
        SteamFriends.activate_game_overlay("Achievements")

        self.accept("escape", self.userExit)
        print("\nWaiting for overlay events... (press Escape to quit)\n")

    def _on_overlay(self, result):
        active = result["active"]
        print(f"[BROADCAST] Steam overlay {'opened' if active else 'closed'}")


if __name__ == "__main__":
    demo = OverlayDemo()
    demo.run()
