"""Steam Networking overview.

This example shows the available networking APIs:

1. **SteamNetworking** (legacy P2P) - simple peer-to-peer connections
   identified by SteamID.  Deprecated in favour of GameNetworkingSockets.
2. **SteamNetworkingSockets** - modern reliable/unreliable messaging.
3. **SteamNetworkingUtils** - relay network access, ping data, and config.

Most real networking happens through SteamNetworkingSockets with
connection handles.  The methods exposed here are the subset that
don't require raw buffer / pointer parameters.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import (
    SteamNetworkingSocket,
    SteamNetworkingUtil,
)


def main():
    base = SteamShowBase(windowType='none')

    # ==================================================================
    # SteamNetworkingUtils - relay network & configuration
    # ==================================================================
    print("=== NetworkingUtils ===")

    # Kick off the relay network (needed before using Steam Datagram Relay)
    SteamNetworkingUtil.init_relay_network_access()
    print("Relay network access initialised.")

    # Check whether cached ping data is fresh enough (max age in seconds)
    fresh = SteamNetworkingUtil.check_ping_data_up_to_date(300.0)
    print(f"Ping data up-to-date (within 5 min): {fresh}")

    # Number of Points-of-Presence in the relay network
    pop_count = SteamNetworkingUtil.get_pop_count()
    print(f"Relay PoP count: {pop_count}")

    # Check if an IPv4 address is a Steam fake IP
    is_fake = SteamNetworkingUtil.is_fake_i_pv4(0x0A000001)  # 10.0.0.1
    print(f"10.0.0.1 is fake IP: {is_fake}")

    # ==================================================================
    # SteamNetworkingSockets - modern networking
    # ==================================================================
    print("\n=== NetworkingSockets ===")

    port = SteamNetworkingSocket.get_hosted_dedicated_server_port()
    print(f"Hosted dedicated server port: {port}")
    
    base.userExit()

if __name__ == "__main__":
    main()
