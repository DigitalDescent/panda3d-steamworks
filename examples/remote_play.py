"""Steam Remote Play Together.

Remote Play Together allows a local multiplayer game to be played
by friends over the internet.  This example queries active sessions
and demonstrates inviting a friend and toggling direct input.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamRemotePlay, SteamFriends


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Active Remote Play sessions
    # ------------------------------------------------------------------
    session_count = SteamRemotePlay.get_session_count()
    print(f"Remote Play sessions: {session_count}")

    # ------------------------------------------------------------------
    # Show the Remote Play Together invite UI
    # ------------------------------------------------------------------
    # Opens the Steam overlay panel that lets the user invite friends.
    # SteamRemotePlay.show_remote_play_together_ui()

    # ------------------------------------------------------------------
    # Invite a specific friend programmatically
    # ------------------------------------------------------------------
    # friend_count = SteamFriends.get_friend_count(0x04)  # k_EFriendFlagImmediate
    # if friend_count > 0:
    #     first_friend = SteamFriends.get_friend_by_index(0, 0x04)
    #     ok = SteamRemotePlay.send_remote_play_together_invite(first_friend)
    #     name = SteamFriends.get_friend_persona_name(first_friend)
    #     print(f"Invited {name}: {ok}")

    # ------------------------------------------------------------------
    # Direct input mode (for games that want raw input from guests)
    # ------------------------------------------------------------------
    # ok = SteamRemotePlay.enable_remote_play_together_direct_input()
    # print(f"Direct input enabled: {ok}")
    # SteamRemotePlay.disable_remote_play_together_direct_input()

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
