"""Demonstrate async methods and callbacks with Panda3D Steamworks.

Shows how to:
- Subclass SteamShowBase for automatic Steam init, callback pumping, and shutdown
- Use async matchmaking (create/join/list lobbies) with Python callables
- Handle broadcast callbacks via Panda3D's accept()/ignore() pattern

Requires steam_appid.txt in the working directory with a valid App ID.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import (
    SteamApps,
    SteamCallbackManager,
    SteamChatRoomEnterResponse,
    SteamLobbyType,
    SteamMatchmaking,
    SteamResult,
    SteamUserStats,
)
from panda3d_steamworks.showbase import SteamShowBase


class AsyncDemo(SteamShowBase):
    """Minimal app that exercises the async callback system.

    SteamShowBase automatically:
      - Calls SteamApps.init() during __init__
      - Pumps SteamCallbackManager.run_callbacks() every frame
      - Shuts down Steam cleanly in finalizeExit()
    """

    def __init__(self):
        super().__init__(windowType='none')

        # ------------------------------------------------------------------
        # Listen for broadcast callbacks via Panda3D messenger
        #
        # Event names are "Steam-" + the struct name without the _t suffix.
        # Use self.accept() / self.ignore() just like any Panda3D event.
        # ------------------------------------------------------------------
        self.accept("Steam-GameOverlayActivated", self._on_overlay)
        self.accept("Steam-GameLobbyJoinRequested", self._on_join_request)
        self.accept("Steam-LobbyDataUpdate", self._on_lobby_data)
        self.accept("Steam-LobbyChatUpdate", self._on_lobby_chat)
        self.accept("Steam-DlcInstalled", self._on_dlc_installed)

        # ------------------------------------------------------------------
        # Kick off some async operations (pass callback directly)
        # ------------------------------------------------------------------
        print("\n--- Requesting lobby list ---")
        handle = SteamMatchmaking.request_lobby_list(self._on_lobby_list)
        if handle:
            print(f"  request_lobby_list() call handle: {handle}")
        else:
            print("  Failed to request lobby list.")

        print("\n--- Requesting current player count ---")
        handle = SteamUserStats.get_number_of_current_players(
            self._on_current_players)
        if handle:
            print(f"  get_number_of_current_players() call handle: {handle}")
        else:
            print("  Failed to request player count.")

        print("\n--- Creating a lobby ---")
        handle = SteamMatchmaking.create_lobby(
            SteamLobbyType.k_ELobbyTypePublic, 4, self._on_lobby_created)
        if handle:
            print(f"  create_lobby() call handle: {handle}")
        else:
            print("  Failed to create lobby.")

        print("\nWaiting for callbacks... (press Ctrl + C to quit)\n")
        self.accept("escape", self.userExit)

    # ------------------------------------------------------------------
    # Async call result handlers (receive a dict)
    # ------------------------------------------------------------------
    def _on_lobby_created(self, result):
        """Fires when create_lobby() completes."""
        if result["io_failure"]:
            print("[CALLBACK] Lobby creation failed (IO error).")
            return
        eresult = result["result"]
        lobby_id = result["steam_id_lobby"]
        if eresult == SteamResult.k_EResultOK:
            print(f"[CALLBACK] Lobby created!  ID = {lobby_id}")
        else:
            print(f"[CALLBACK] Lobby creation failed, EResult = {eresult}")

    def _on_lobby_list(self, result):
        """Fires when request_lobby_list() completes."""
        if result["io_failure"]:
            print("[CALLBACK] Lobby list request failed (IO error).")
            return
        count = result["lobbies_matching"]
        print(f"[CALLBACK] Found {count} lobbies matching the filter.")

    def _on_lobby_entered(self, result):
        """Fires when join_lobby() completes."""
        if result["io_failure"]:
            print("[CALLBACK] Join lobby failed (IO error).")
            return
        lobby_id = result["steam_id_lobby"]
        status = result["chat_room_enter_response"]
        if status == SteamChatRoomEnterResponse.k_EChatRoomEnterResponseSuccess:
            print(f"[CALLBACK] Entered lobby {lobby_id}")
        else:
            print(f"[CALLBACK] Failed to enter lobby, response = {status}")

    def _on_current_players(self, result):
        """Fires when get_number_of_current_players() completes."""
        if result["io_failure"]:
            print("[CALLBACK] Current players request failed (IO error).")
            return
        success = result["success"]
        players = result["players"]
        print(f"[CALLBACK] Current players: {players}  (success={success})")

    # ------------------------------------------------------------------
    # Broadcast callback handlers (receive a dict via Panda3D messenger)
    # ------------------------------------------------------------------
    def _on_overlay(self, result):
        active = result["active"]
        print(f"[BROADCAST] Steam overlay {'opened' if active else 'closed'}")

    def _on_join_request(self, result):
        lobby_id = result["steam_id_lobby"]
        friend_id = result["steam_id_friend"]
        print(f"[BROADCAST] Join requested: lobby={lobby_id}, friend={friend_id}")
        # Automatically join the lobby:
        # SteamMatchmaking.join_lobby(lobby_id, self._on_lobby_entered)

    def _on_lobby_data(self, result):
        lobby_id = result["steam_id_lobby"]
        print(f"[BROADCAST] Lobby data updated: {lobby_id}")

    def _on_lobby_chat(self, result):
        lobby_id = result["steam_id_lobby"]
        user_id = result["steam_id_user_changed"]
        print(f"[BROADCAST] Lobby chat update: lobby={lobby_id}, user={user_id}")

    def _on_dlc_installed(self, result):
        app_id = result["app_id"]
        print(f"[BROADCAST] DLC installed: {app_id}")


if __name__ == "__main__":
    demo = AsyncDemo()
    demo.run()
