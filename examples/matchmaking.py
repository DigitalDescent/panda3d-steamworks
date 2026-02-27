"""Steam Matchmaking - lobbies and favourite servers.

Demonstrates creating and managing lobbies, setting lobby data,
enumerating members, and managing the favourite server list.

For async lobby operations (create, join, request list) see
async_callbacks.py which shows the full callback-driven flow.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamMatchmaking, SteamUser


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Favourite / history servers
    # ------------------------------------------------------------------
    fav_count = SteamMatchmaking.get_favorite_game_count()
    print(f"Favourite/history servers: {fav_count}")

    # Add a favourite server:
    # SteamMatchmaking.add_favorite_game(
    #     app_id, ip, conn_port, query_port, flags, last_played_time
    # )

    # ------------------------------------------------------------------
    # Lobby listing (async - see async_callbacks.py for full example)
    # ------------------------------------------------------------------
    # Apply filters before requesting the list:
    # SteamMatchmaking.add_request_lobby_list_result_count_filter(10)
    # SteamMatchmaking.add_request_lobby_list_filter_slots_available(1)
    # SteamMatchmaking.request_lobby_list(callback)

    # ------------------------------------------------------------------
    # Working with an existing lobby
    # ------------------------------------------------------------------
    # Assuming you have a lobby_id (CSteamID) from a callback:
    #
    # Members:
    #   count = SteamMatchmaking.get_num_lobby_members(lobby_id)
    #   for i in range(count):
    #       member = SteamMatchmaking.get_lobby_member_by_index(lobby_id, i)
    #
    # Lobby metadata (key-value pairs):
    #   SteamMatchmaking.set_lobby_data(lobby_id, "map", "dm_arena")
    #   map_name = SteamMatchmaking.get_lobby_data(lobby_id, "map")
    #   SteamMatchmaking.delete_lobby_data(lobby_id, "map")
    #   num_keys = SteamMatchmaking.get_lobby_data_count(lobby_id)
    #
    # Per-member metadata:
    #   SteamMatchmaking.set_lobby_member_data(lobby_id, "ready", "1")
    #   val = SteamMatchmaking.get_lobby_member_data(lobby_id, member_id, "ready")
    #
    # Lobby settings:
    #   SteamMatchmaking.set_lobby_member_limit(lobby_id, 8)
    #   limit = SteamMatchmaking.get_lobby_member_limit(lobby_id)
    #   SteamMatchmaking.set_lobby_joinable(lobby_id, True)
    #   SteamMatchmaking.set_lobby_owner(lobby_id, new_owner_id)
    #   owner = SteamMatchmaking.get_lobby_owner(lobby_id)
    #
    # Invite a user:
    #   SteamMatchmaking.invite_user_to_lobby(lobby_id, friend_id)
    #
    # Set the game server for lobby members to connect to:
    #   SteamMatchmaking.set_lobby_game_server(lobby_id, ip, port, server_steam_id)
    #
    # Leave the lobby:
    #   SteamMatchmaking.leave_lobby(lobby_id)

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
