"""Steam Parties (Beacons).

Steam Parties lets games create discoverable "beacons" that other
players can join.  This is used for activities like finding a group
for a raid or co-op mission.

NOTE: Most operations are async - results arrive via the callback
system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamParties


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Active beacons
    # ------------------------------------------------------------------
    num_beacons = SteamParties.get_num_active_beacons()
    print(f"Active party beacons: {num_beacons}")

    # ------------------------------------------------------------------
    # Join a beacon (async)
    # ------------------------------------------------------------------
    # beacon_id = <some PartyBeaconID_t>
    # SteamParties.join_party(beacon_id)

    # ------------------------------------------------------------------
    # Manage your own beacon
    # ------------------------------------------------------------------
    # When a player joins your beacon:
    # SteamParties.on_reservation_completed(beacon_id, steam_id_of_joiner)
    #
    # Cancel a pending reservation:
    # SteamParties.cancel_reservation(beacon_id, steam_id_of_joiner)
    #
    # Update available slots:
    # SteamParties.change_num_open_slots(beacon_id, 2)
    #
    # Destroy your beacon when the activity ends:
    # SteamParties.destroy_beacon(beacon_id)

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
