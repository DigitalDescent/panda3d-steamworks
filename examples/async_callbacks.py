"""Demonstrate async methods and callbacks with Panda3D Steamworks.

Shows how to:
- Process Steam callbacks every frame via a Panda3D task
- Use async matchmaking (create/join/list lobbies) with Python callables
- Handle broadcast callbacks via Panda3D's accept()/ignore() pattern

Requires steam_appid.txt in the working directory with a valid App ID.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from direct.showbase.ShowBase import ShowBase
from panda3d import core
from panda3d_steamworks import (
    SteamApps,
    SteamCallbackManager,
    SteamMatchmaking,
    SteamUserStats,
)


class AsyncDemo(ShowBase):
    """Minimal app that exercises the async callback system."""

    def __init__(self):
        super().__init__()

        # ------------------------------------------------------------------
        # Initialise Steam
        # ------------------------------------------------------------------
        if not SteamApps.init():
            print("ERROR: Steam failed to initialise.")
            sys.exit(1)

        # Pump Steam callbacks every frame.  This is **required** for any
        # async method or broadcast callback to fire.
        self.task_mgr.add(self._steam_update, "steam_update")

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
        # ELobbyType: 0=Private, 1=FriendsOnly, 2=Public, 3=Invisible
        handle = SteamMatchmaking.create_lobby(
            2, 4, self._on_lobby_created)  # Public, 4 slots
        if handle:
            print(f"  create_lobby() call handle: {handle}")
        else:
            print("  Failed to create lobby.")

        print("\nWaiting for callbacks... (press Escape to quit)\n")
        self.accept("escape", self._shutdown)

    # ------------------------------------------------------------------
    # Task: pump Steam every frame
    # ------------------------------------------------------------------
    def _steam_update(self, task):
        SteamCallbackManager.run_callbacks()
        return task.cont

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
        if eresult == 1:  # k_EResultOK
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
        if status == 1:  # k_EChatRoomEnterResponseSuccess
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

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def _shutdown(self):
        print("\nShutting down...")
        # ignore_all() cleans up all accepted events automatically
        self.ignore_all()
        SteamCallbackManager.shutdown()
        SteamApps.shutdown()
        self.userExit()


if __name__ == "__main__":
    demo = AsyncDemo()
    demo.run()
