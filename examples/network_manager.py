"""SteamNetworkManager — high-level GameSockets example.

Demonstrates the SteamNetworkManager class which wraps the
ISteamNetworkingSockets API into a Panda3D-friendly interface with
Datagram-based messaging and an event queue.

Run with --server to host, or --client <ip:port> to connect.

    ppython examples/network_manager.py --server
    ppython examples/network_manager.py --client 127.0.0.1:27015
"""

import sys
import argparse
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

PORT = 27015


# ------------------------------------------------------------------
# Combined server + client in one process
# ------------------------------------------------------------------
def main():
    base = SteamShowBase(windowType="none")
    mgr = SteamNetworkManager.get_global_ptr()

    # --- server setup ---
    listen = mgr.create_ip_socket(PORT)
    print(f"[server] Listening on port {PORT}  (handle {listen})")

    poll_group = mgr.create_poll_group()
    server_clients = {}  # connection handle -> True

    # --- client setup ---
    addr = core.NetAddress()
    addr.set_host("127.0.0.1", PORT)

    client_conn = mgr.connect_by_ip_address(addr)
    print(f"[client] Connecting to 127.0.0.1:{PORT}  (handle {client_conn})")

    client_sent = [False]

    def poll(task):
        # ---- process ALL events in one place ----
        event = mgr.get_next_event()
        while event is not None:
            conn = event.connection
            old = event.old_state
            new = event.state
            print(f"  Event: conn={conn}  old_state={old}  state={new}")

            # -- server-side events (any connection that is NOT our client handle) --
            if conn != client_conn:
                if old == STATE_NONE and new == STATE_CONNECTING:
                    mgr.accept_connection(conn)
                    mgr.set_connection_poll_group(conn, poll_group)
                    server_clients[conn] = True
                    print(f"[server] Accepted connection {conn}")

                elif new == STATE_CONNECTED:
                    print(f"[server] Connection {conn} is now fully connected.")

                elif new in (STATE_CLOSED_BY_PEER, STATE_PROBLEM):
                    print(f"[server] Connection {conn} lost (state {new}).")
                    mgr.close_connection(conn)
                    server_clients.pop(conn, None)

            # -- client-side events --
            else:
                if new == STATE_CONNECTING:
                    print(f"[client] Connecting …")

                elif new == STATE_CONNECTED and not client_sent[0]:
                    print("[client] Connected!  Sending test datagram …")
                    dg = core.Datagram()
                    dg.add_string("Hello from panda3d-steamworks!")
                    mgr.send_datagram(client_conn, dg, SEND_RELIABLE)
                    client_sent[0] = True

                elif new in (STATE_CLOSED_BY_PEER, STATE_PROBLEM):
                    print(f"[client] Connection lost (state {new}).")
                    mgr.close_connection(client_conn)

            event = mgr.get_next_event()

        # ---- server: receive via poll group ----
        msg = SteamNetworkMessage()
        while mgr.receive_message_on_poll_group(poll_group, msg):
            dgi = msg.dgi
            text = dgi.get_string()
            sender = msg.connection
            print(f"[server] Received from {sender}: {text!r}")

            reply = core.Datagram()
            reply.add_string(f"echo: {text}")
            mgr.send_datagram(sender, reply, SEND_RELIABLE)
            msg = SteamNetworkMessage()

        # ---- client: receive replies ----
        msg = SteamNetworkMessage()
        while mgr.receive_message_on_connection(client_conn, msg):
            dgi = msg.dgi
            text = dgi.get_string()
            print(f"[client] Server replied: {text!r}")
            msg = SteamNetworkMessage()

        return task.cont

    base.taskMgr.add(poll, "network-poll")

    print("Running … press Ctrl+C to quit.\n")
    base.run()


if __name__ == "__main__":
    main()
