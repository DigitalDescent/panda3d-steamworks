"""Enumerate the user's Steam friends list."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamFriends, SteamFriendFlags
from panda3d_steamworks.showbase import SteamShowBase

def main():
    base = SteamShowBase(windowType='none')

    persona = SteamFriends.get_persona_name()
    print(f"Logged in as: {persona}\n")

    friend_count = SteamFriends.get_friend_count(SteamFriendFlags.k_EFriendFlagImmediate)
    print(f"You have {friend_count} friend(s):\n")

    # Print the first 25 friends (to avoid flooding the console)
    limit = min(friend_count, 25)
    for i in range(limit):
        friend_id = SteamFriends.get_friend_by_index(i, SteamFriendFlags.k_EFriendFlagImmediate)
        # Note: GetFriendPersonaName requires the friend's data to be cached.
        # For friends on your list this is usually available immediately.
        print(f"  [{i+1:3d}] Steam ID: {friend_id}")

    if friend_count > limit:
        print(f"  ... and {friend_count - limit} more.")

    # Friend groups (tags)
    group_count = SteamFriends.get_friends_group_count()
    if group_count > 0:
        print(f"\nFriend groups: {group_count}")

    # Clans (groups the user belongs to)
    clan_count = SteamFriends.get_clan_count()
    if clan_count > 0:
        print(f"\nSteam groups: {clan_count}")
        for i in range(min(clan_count, 10)):
            clan_id = SteamFriends.get_clan_by_index(i)
            print(f"  [{i+1}] Clan Steam ID: {clan_id}")

    # Recently played with
    coplay_count = SteamFriends.get_coplay_friend_count()
    if coplay_count > 0:
        print(f"\nRecently played with: {coplay_count} player(s)")
        for i in range(min(coplay_count, 10)):
            coplay_id = SteamFriends.get_coplay_friend(i)
            print(f"  [{i+1}] Steam ID: {coplay_id}")

    base.userExit()


if __name__ == "__main__":
    main()
