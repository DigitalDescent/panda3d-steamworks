"""Query ownership status for the current user."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    print("Ownership status:")
    print(f"  Subscribed           : {SteamApps.is_subscribed()}")
    print(f"  Low-violence licence : {SteamApps.is_low_violence()}")
    print(f"  Cybercafe licence    : {SteamApps.is_cybercafe()}")
    print(f"  VAC banned           : {SteamApps.is_vac_banned()}")
    print(f"  Free weekend         : {SteamApps.is_subscribed_from_free_weekend()}")
    print(f"  Family sharing       : {SteamApps.is_subscribed_from_family_sharing()}")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
