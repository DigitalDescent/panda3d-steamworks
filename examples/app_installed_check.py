"""Check whether another app is owned / installed and get its install path."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps

# Replace with the App ID you want to query
OTHER_APP_ID = 440  # Team Fortress 2


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    subscribed = SteamApps.is_subscribed_app(OTHER_APP_ID)
    installed = SteamApps.is_app_installed(OTHER_APP_ID)
    print(f"App {OTHER_APP_ID}:")
    print(f"  Subscribed : {subscribed}")
    print(f"  Installed  : {installed}")

    if installed:
        install_dir = SteamApps.get_app_install_dir(OTHER_APP_ID)
        print(f"  Install dir: {install_dir}")

    purchase_time = SteamApps.get_earliest_purchase_unix_time(OTHER_APP_ID)
    if purchase_time:
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(purchase_time, tz=timezone.utc)
        print(f"  Purchased  : {dt.isoformat()}")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
