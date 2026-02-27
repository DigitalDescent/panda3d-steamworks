"""Interact with the Steam Workshop (User-Generated Content).

Demonstrates subscribing/unsubscribing to items, querying item state,
downloading items, favouriting, and checking the Workshop EULA status.

NOTE: Replace WORKSHOP_ITEM_ID with a real published file ID to test
download and state queries.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamItemState, SteamUGC, SteamCallbackManager

# Replace with a valid Workshop item ID for your app.
WORKSHOP_ITEM_ID = 0


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    app_id = SteamApps.get_app_id() if hasattr(SteamApps, "get_app_id") else 480

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
        if state & SteamItemState.k_EItemStateSubscribed:
            state_flags.append("Subscribed")
        if state & SteamItemState.k_EItemStateLegacyItem:
            state_flags.append("LegacyItem")
        if state & SteamItemState.k_EItemStateInstalled:
            state_flags.append("Installed")
        if state & SteamItemState.k_EItemStateNeedsUpdate:
            state_flags.append("NeedsUpdate")
        if state & SteamItemState.k_EItemStateDownloading:
            state_flags.append("Downloading")
        if state & SteamItemState.k_EItemStateDownloadPending:
            state_flags.append("DownloadPending")
        print(f"Item {WORKSHOP_ITEM_ID} state: {', '.join(state_flags) or 'None'}")

        # Start a download if the item needs updating
        if state & SteamItemState.k_EItemStateNeedsUpdate:
            ok = SteamUGC.download_item(WORKSHOP_ITEM_ID, True)
            print(f"Download started: {ok}")

    # ------------------------------------------------------------------
    # Subscribe / unsubscribe (async - requires callback pump)
    # ------------------------------------------------------------------
    # Uncomment to subscribe to an item:
    # SteamUGC.subscribe_item(WORKSHOP_ITEM_ID)

    # Uncomment to unsubscribe:
    # SteamUGC.unsubscribe_item(WORKSHOP_ITEM_ID)

    # ------------------------------------------------------------------
    # Favourites (async)
    # ------------------------------------------------------------------
    # SteamUGC.add_item_to_favorites(app_id, WORKSHOP_ITEM_ID)
    # SteamUGC.remove_item_from_favorites(app_id, WORKSHOP_ITEM_ID)

    # ------------------------------------------------------------------
    # Suspend / resume downloads
    # ------------------------------------------------------------------
    # SteamUGC.suspend_downloads(True)   # pause all Workshop downloads
    # SteamUGC.suspend_downloads(False)  # resume

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
