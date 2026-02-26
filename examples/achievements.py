"""Demonstrate achievement querying, unlocking, and progress tracking.

IMPORTANT: Achievements must be configured in Steamworks App Admin for your
App ID before they can be used.  Replace the example names below with your
actual achievement API names.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamUserStats

# Replace with your own achievement API names
ACHIEVEMENT_FIRST_BLOOD = "ACH_FIRST_BLOOD"
ACHIEVEMENT_LEVEL_5 = "ACH_LEVEL_5"


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # List all registered achievements
    # ------------------------------------------------------------------
    num_achievements = SteamUserStats.get_num_achievements()
    print(f"This game has {num_achievements} achievement(s) defined.\n")

    for i in range(num_achievements):
        name = SteamUserStats.get_achievement_name(i)
        display_name = SteamUserStats.get_achievement_display_attribute(name, "name")
        description = SteamUserStats.get_achievement_display_attribute(name, "desc")
        print(f"  [{i+1}] {display_name}")
        print(f"       API name    : {name}")
        if description:
            print(f"       Description : {description}")
        print()

    # ------------------------------------------------------------------
    # Unlock an achievement
    # ------------------------------------------------------------------
    print(f"Unlocking '{ACHIEVEMENT_FIRST_BLOOD}' ...")
    if SteamUserStats.set_achievement(ACHIEVEMENT_FIRST_BLOOD):
        # You MUST call store_stats() to commit to the server.
        SteamUserStats.store_stats()
        print("  Achievement unlocked and stored!\n")
    else:
        print("  Failed (achievement may not exist for this App ID).\n")

    # ------------------------------------------------------------------
    # Show incremental progress (UI toast without unlocking)
    # ------------------------------------------------------------------
    print(f"Showing progress for '{ACHIEVEMENT_LEVEL_5}' (3 / 5) ...")
    SteamUserStats.indicate_achievement_progress(ACHIEVEMENT_LEVEL_5, 3, 5)

    # ------------------------------------------------------------------
    # Stats: set and read
    # ------------------------------------------------------------------
    print("\nSetting stat 'num_games' to 42 ...")
    SteamUserStats.set_stat("num_games", 42)
    SteamUserStats.store_stats()

    # ------------------------------------------------------------------
    # Reset (for testing only!)
    # ------------------------------------------------------------------
    # Uncomment the lines below to wipe achievements and stats:
    # SteamUserStats.reset_all_stats(True)  # True = also clear achievements
    # print("All stats and achievements have been reset.")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
