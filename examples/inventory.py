"""Query the Steam Inventory Service.

Shows how to:
- Load item definitions asynchronously and wait for the result callback
- Send the item-drop heartbeat periodically via a Panda3D task
- Listen for SteamInventoryResultReady and SteamInventoryDefinitionUpdate

The Steam Inventory Service lets games define, grant, and manage in-game
items.

NOTE: Your app must have inventory items configured in the Steamworks
partner site for most of these calls to return meaningful results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamInventory


class InventoryDemo(SteamShowBase):
    """App that loads inventory definitions and listens for results."""

    def __init__(self):
        super().__init__(windowType='none')

        # ------------------------------------------------------------------
        # Listen for inventory broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-SteamInventoryResultReady", self._on_result_ready)
        self.accept("Steam-SteamInventoryDefinitionUpdate", self._on_def_update)
        self.accept("Steam-SteamInventoryFullUpdate", self._on_full_update)

        # ------------------------------------------------------------------
        # Load item definitions from the Steamworks backend (async)
        # ------------------------------------------------------------------
        ok = SteamInventory.load_item_definitions()
        print(f"LoadItemDefinitions: {'requested' if ok else 'failed (no items configured?)'}")

        # ------------------------------------------------------------------
        # Store prices
        # ------------------------------------------------------------------
        num_priced = SteamInventory.get_num_items_with_prices()
        print(f"Items with store prices: {num_priced}")

        # ------------------------------------------------------------------
        # Periodically send the item-drop heartbeat so the backend
        # knows the player is active and can grant timed drops.
        # ------------------------------------------------------------------
        self.taskMgr.doMethodLater(
            60.0, self._heartbeat, "inventory_heartbeat"
        )
        SteamInventory.send_item_drop_heartbeat()
        print("Item drop heartbeat sent.")

        self.accept("escape", self.userExit)
        print("\nWaiting for inventory callbacks... (press Ctrl + C to quit)\n")

    # ------------------------------------------------------------------
    # Periodic heartbeat task
    # ------------------------------------------------------------------
    def _heartbeat(self, task):
        SteamInventory.send_item_drop_heartbeat()
        print("  [heartbeat] Item drop heartbeat sent")
        return task.again

    # ------------------------------------------------------------------
    # Broadcast callback handlers
    # ------------------------------------------------------------------
    def _on_result_ready(self, result):
        """Fires when an inventory result handle is ready."""
        print(f"[BROADCAST] SteamInventoryResultReady: {result}")

    def _on_def_update(self, result):
        """Fires when item definitions have been updated."""
        print(f"[BROADCAST] SteamInventoryDefinitionUpdate: {result}")
        num_priced = SteamInventory.get_num_items_with_prices()
        print(f"  Items with store prices: {num_priced}")

    def _on_full_update(self, result):
        """Fires when a full inventory update is available."""
        print(f"[BROADCAST] SteamInventoryFullUpdate: {result}")


if __name__ == "__main__":
    demo = InventoryDemo()
    demo.run()
