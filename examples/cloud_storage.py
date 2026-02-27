"""Read and write JSON data to Steam Cloud storage.

Demonstrates:
  - Writing a Python dict as JSON to a Steam Cloud file
  - Reading it back and deserialising to a dict
  - Listing cloud files and checking status
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamRemoteStorage

CLOUD_FILE = "settings.json"


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Cloud status
    # ------------------------------------------------------------------
    print("Steam Cloud Status")
    print(f"  Account cloud enabled : {SteamRemoteStorage.is_cloud_enabled_for_account()}")
    print(f"  App cloud enabled     : {SteamRemoteStorage.is_cloud_enabled_for_app()}")

    # ------------------------------------------------------------------
    # Write JSON to cloud
    # ------------------------------------------------------------------
    save_data = {
        "player_name": "Gordon",
        "level": 42,
        "inventory": ["crowbar", "gravity_gun", "medkit"],
        "settings": {
            "volume": 0.8,
            "fullscreen": True,
        },
    }

    payload = json.dumps(save_data, indent=2)
    ok = SteamRemoteStorage.file_write(CLOUD_FILE, payload)
    print(f"\nWrote '{CLOUD_FILE}': {'ok' if ok else 'FAILED'}")

    # ------------------------------------------------------------------
    # Read JSON back from cloud
    # ------------------------------------------------------------------
    if SteamRemoteStorage.file_exists(CLOUD_FILE):
        raw = SteamRemoteStorage.file_read(CLOUD_FILE)
        loaded = json.loads(raw)

        print(f"Read '{CLOUD_FILE}' ({len(raw)} bytes):")
        for key, value in loaded.items():
            print(f"  {key}: {value}")
    else:
        print(f"'{CLOUD_FILE}' not found in cloud storage.")

    # ------------------------------------------------------------------
    # List all cloud files
    # ------------------------------------------------------------------
    count = SteamRemoteStorage.get_file_count()
    print(f"\nCloud files ({count}):")
    if count == 0:
        print("  (none)")
    else:
        for i in range(count):
            pass  # get_file_name_and_size not yet wrapped

    # ------------------------------------------------------------------
    # Delete the test file (optional - uncomment to clean up)
    # ------------------------------------------------------------------
    # SteamRemoteStorage.file_delete(CLOUD_FILE)

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
