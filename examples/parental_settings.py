"""Query Steam Parental Settings (Family View).

Steam Family View lets parents restrict access to certain games and
features.  This example checks whether parental controls are active
and whether a specific app or feature is blocked.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamParentalSettings


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Parental lock status
    # ------------------------------------------------------------------
    enabled = SteamParentalSettings.is_parental_lock_enabled()
    locked = SteamParentalSettings.is_parental_lock_locked()

    print("Steam Parental Settings (Family View)")
    print(f"  Enabled : {enabled}")
    print(f"  Locked  : {locked}")

    # ------------------------------------------------------------------
    # Check whether a specific app is blocked
    # ------------------------------------------------------------------
    test_app_id = 440  # Team Fortress 2
    blocked = SteamParentalSettings.is_app_blocked(test_app_id)
    in_list = SteamParentalSettings.is_app_in_block_list(test_app_id)
    print(f"\nApp {test_app_id}:")
    print(f"  Blocked       : {blocked}")
    print(f"  In block list : {in_list}")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
