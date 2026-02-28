"""SteamNetworkManager — P2P (Steam ID) connection example.

Demonstrates peer-to-peer connections using Steam ID relay instead of
raw IP addresses.  Runs both host and joiner in a single process
with one shared event queue.

    ppython examples/network_manager_p2p.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import (
    SteamConstants,
    SteamNetworkingConnectionState,
    SteamNetworkManager,
    SteamNetworkConnectionInfo,
    SteamNetworkMessage,
    SteamUser,
)

# Convenience aliases for send flags
SEND_RELIABLE = SteamConstants.k_nSteamNetworkingSend_Reliable
SEND_UNRELIABLE = SteamConstants.k_nSteamNetworkingSend_Unreliable

# Connection state constants
STATE_NONE = SteamNetworkingConnectionState.k_ESteamNetworkingConnectionState_None
STATE_CONNECTING = SteamNetworkingConnectionState.k_ESteamNetworkingConnectionState_Connecting
STATE_CONNECTED = SteamNetworkingConnectionState.k_ESteamNetworkingConnectionState_Connected
STATE_CLOSED_BY_PEER = SteamNetworkingConnectionState.k_ESteamNetworkingConnectionState_ClosedByPeer
STATE_PROBLEM = SteamNetworkingConnectionState.k_ESteamNetworkingConnectionState_ProblemDetectedLocally

# Virtual port used for P2P listen/connect (can be any agreed-upon int)
VIRTUAL_PORT = 0


# ------------------------------------------------------------------
# Combined host + joiner in one process
# ------------------------------------------------------------------
def main():
    base = SteamShowBase(windowType="none")
    mgr = SteamNetworkManager.get_global_ptr()

    my_id = SteamUser.get_steam_id()
    print(f"Your Steam ID: {my_id}\n")

    # --- host setup: P2P listen socket ---
    listen = mgr.create_steam_id_socket(VIRTUAL_PORT)
    print(f"[host] P2P listen socket created  (handle {listen})")

    poll_group = mgr.create_poll_group()
    host_peers = {}  # connection handle -> True

    # --- joiner setup: connect to ourselves by Steam ID ---
    join_conn = mgr.connect_by_steam_id(str(my_id))
    print(f"[join] P2P connection initiated to self  (handle {join_conn})")

    join_sent = [False]

    def poll(task):
        # ---- process ALL events in one place ----
        event = mgr.get_next_event()
        while event is not None:
            conn = event.connection
            old = event.old_state
            new = event.state
            print(f"  Event: conn={conn}  old_state={old}  state={new}")

            # -- host-side events (any connection that is NOT our joiner handle) --
            if conn != join_conn:
                if old == STATE_NONE and new == STATE_CONNECTING:
                    mgr.accept_connection(conn)
                    mgr.set_connection_poll_group(conn, poll_group)
                    host_peers[conn] = True
                    print(f"[host] Accepted P2P connection {conn}")

                elif new == STATE_CONNECTED:
                    print(f"[host] Connection {conn} is now fully connected.")

                elif new in (STATE_CLOSED_BY_PEER, STATE_PROBLEM):
                    print(f"[host] Connection {conn} lost (state {new}).")
                    mgr.close_connection(conn)
                    host_peers.pop(conn, None)

            # -- joiner-side events --
            else:
                if new == STATE_CONNECTING:
                    print("[join] Connecting …")

                elif new == STATE_CONNECTED and not join_sent[0]:
                    print("[join] Connected!  Sending test datagram …")
                    dg = core.Datagram()
                    dg.add_string("Hello over P2P from panda3d-steamworks!")
                    mgr.send_datagram(join_conn, dg, SEND_RELIABLE)
                    join_sent[0] = True

                elif new in (STATE_CLOSED_BY_PEER, STATE_PROBLEM):
                    print(f"[join] Connection lost (state {new}).")
                    mgr.close_connection(join_conn)

            event = mgr.get_next_event()

        # ---- host: receive via poll group ----
        msg = SteamNetworkMessage()
        while mgr.receive_message_on_poll_group(poll_group, msg):
            dgi = msg.dgi
            text = dgi.get_string()
            sender = msg.connection
            print(f"[host] Received from {sender}: {text!r}")

            reply = core.Datagram()
            reply.add_string(f"echo: {text}")
            mgr.send_datagram(sender, reply, SEND_RELIABLE)
            msg = SteamNetworkMessage()

        # ---- joiner: receive replies ----
        msg = SteamNetworkMessage()
        while mgr.receive_message_on_connection(join_conn, msg):
            dgi = msg.dgi
            text = dgi.get_string()
            print(f"[join] Host replied: {text!r}")
            msg = SteamNetworkMessage()

        return task.cont

    base.taskMgr.add(poll, "network-poll")

    print("Running … press Ctrl+C to quit.\n")
    base.run()


if __name__ == "__main__":
    main()
