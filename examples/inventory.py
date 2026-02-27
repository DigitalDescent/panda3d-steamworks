"""Query the Steam Inventory Service.

The Steam Inventory Service lets games define, grant, and manage
in-game items.  This example loads item definitions, triggers the
drop heartbeat, checks prices, and queries promo eligibility.

NOTE: Your app must have inventory items configured in the Steamworks
partner site for most of these calls to return meaningful results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamInventory


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Load item definitions from the Steamworks backend
    # ------------------------------------------------------------------
    ok = SteamInventory.load_item_definitions()
    print(f"LoadItemDefinitions: {'ok' if ok else 'failed (no items configured?)'}")

    # ------------------------------------------------------------------
    # Item drop heartbeat - call periodically so the backend knows
    # the player is active and can grant timed drops.
    # ------------------------------------------------------------------
    SteamInventory.send_item_drop_heartbeat()
    print("Item drop heartbeat sent.")

    # ------------------------------------------------------------------
    # Store prices
    # ------------------------------------------------------------------
    num_priced = SteamInventory.get_num_items_with_prices()
    print(f"Items with store prices: {num_priced}")

    # ------------------------------------------------------------------
    # Clean up
    # ------------------------------------------------------------------
    SteamApps.shutdown()


if __name__ == "__main__":
    main()
