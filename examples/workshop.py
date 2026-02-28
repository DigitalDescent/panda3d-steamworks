"""Interact with the Steam Workshop (User-Generated Content).

Shows how to:
- Query subscribed items and item state
- Subscribe to Workshop items with async callback handling
- Download items and listen for download progress
- Handle the Workshop EULA

NOTE: Replace WORKSHOP_ITEM_ID with a real published file ID to test
download and state queries.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamItemState, SteamUGC
from panda3d_steamworks.showbase import SteamShowBase

# Replace with a valid Workshop item ID for your app.
WORKSHOP_ITEM_ID = 0


class WorkshopDemo(SteamShowBase):
    """App that demonstrates Workshop operations with proper callbacks."""

    def __init__(self):
        super().__init__(windowType='none')

        self._app_id = SteamApps.get_app_id() if hasattr(SteamApps, "get_app_id") else 480

        # ------------------------------------------------------------------
        # Listen for Workshop broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-DownloadItemResult", self._on_download_result)
        self.accept("Steam-ItemInstalled", self._on_item_installed)
        self.accept("Steam-UserSubscribedItemsListChanged", self._on_sub_list_changed)

        # ------------------------------------------------------------------
        # Subscribed items
        # ------------------------------------------------------------------
        num_subscribed = SteamUGC.get_num_subscribed_items(False)
        print(f"Subscribed Workshop items: {num_subscribed}")

        # ------------------------------------------------------------------
        # Workshop EULA
        # ------------------------------------------------------------------
        print("Opening Workshop EULA (if available)...")
        SteamUGC.show_workshop_eula()

        # ------------------------------------------------------------------
        # Item state (requires a valid item ID)
        # ------------------------------------------------------------------
        if WORKSHOP_ITEM_ID:
            state = SteamUGC.get_item_state(WORKSHOP_ITEM_ID)
            state_flags = []
            if state & 0x01:
                state_flags.append("Subscribed")
            if state & 0x02:
                state_flags.append("LegacyItem")
            if state & 0x04:
                state_flags.append("Installed")
            if state & 0x08:
                state_flags.append("NeedsUpdate")
            if state & 0x10:
                state_flags.append("Downloading")
            if state & 0x20:
                state_flags.append("DownloadPending")
            print(f"Item {WORKSHOP_ITEM_ID} state: {', '.join(state_flags) or 'None'}")

            # Start a download if the item needs updating.
            # Result arrives via Steam-DownloadItemResult.
            if state & 0x08:
                ok = SteamUGC.download_item(WORKSHOP_ITEM_ID, True)
                print(f"Download requested: {ok}")

            # Subscribe to the item (async).
            # Confirmation comes via Steam-UserSubscribedItemsListChanged.
            # SteamUGC.subscribe_item(WORKSHOP_ITEM_ID)

        self.accept("escape", self.userExit)
        print("\nWaiting for callbacks... (press Ctrl + C to quit)\n")

    # ------------------------------------------------------------------
    # Broadcast callback handlers
    # ------------------------------------------------------------------
    def _on_download_result(self, result):
        """Fires when download_item() finishes."""
        print(f"[BROADCAST] DownloadItemResult: {result}")

    def _on_item_installed(self, result):
        """Fires when a Workshop item has been installed or updated."""
        print(f"[BROADCAST] ItemInstalled: {result}")

    def _on_sub_list_changed(self, result):
        """Fires when the user's subscribed-items list changes."""
        print(f"[BROADCAST] UserSubscribedItemsListChanged: {result}")


if __name__ == "__main__":
    demo = WorkshopDemo()
    demo.run()
