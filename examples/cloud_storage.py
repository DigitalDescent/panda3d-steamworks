"""Check Steam Cloud status and list files stored in cloud storage."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamRemoteStorage


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Cloud account / app status
    # ------------------------------------------------------------------
    account_enabled = SteamRemoteStorage.is_cloud_enabled_for_account()
    app_enabled = SteamRemoteStorage.is_cloud_enabled_for_app()

    print("Steam Cloud Status")
    print(f"  Account cloud enabled : {account_enabled}")
    print(f"  App cloud enabled     : {app_enabled}")

    # ------------------------------------------------------------------
    # List files in cloud storage
    # ------------------------------------------------------------------
    file_count = SteamRemoteStorage.get_file_count()
    print(f"\nCloud files: {file_count}")

    if file_count == 0:
        print("  (no files in cloud storage)")
    else:
        for i in range(file_count):
            # get_file_name_and_size is usually available; here we can
            # demonstrate checking individual files by name if you know them.
            pass

    # ------------------------------------------------------------------
    # Check a specific file
    # ------------------------------------------------------------------
    test_file = "save_game.dat"
    exists = SteamRemoteStorage.file_exists(test_file)
    print(f"\nChecking '{test_file}':")
    print(f"  Exists    : {exists}")

    if exists:
        size = SteamRemoteStorage.get_file_size(test_file)
        ts = SteamRemoteStorage.get_file_timestamp(test_file)
        persisted = SteamRemoteStorage.file_persisted(test_file)
        print(f"  Size      : {size} bytes")
        print(f"  Timestamp : {ts}")
        print(f"  Persisted : {persisted}")

    # ------------------------------------------------------------------
    # Enable / disable cloud sync for this app
    # ------------------------------------------------------------------
    # Uncomment to toggle cloud for this app:
    # SteamRemoteStorage.set_cloud_enabled_for_app(True)

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
