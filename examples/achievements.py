"""Demonstrate achievement querying, unlocking, and progress tracking.

Shows how to:
- Listen for UserStatsReceived to know when stats are ready
- Unlock achievements and store stats
- Handle UserStatsStored and UserAchievementStored confirmations

IMPORTANT: Achievements must be configured in Steamworks App Admin for your
App ID before they can be used.  Replace the example names below with your
actual achievement API names.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamUserStats

# Replace with your own achievement API names
ACHIEVEMENT_FIRST_BLOOD = "ACH_FIRST_BLOOD"
ACHIEVEMENT_LEVEL_5 = "ACH_LEVEL_5"


class AchievementsDemo(SteamShowBase):
    """App that demonstrates the full achievement lifecycle with callbacks."""

    def __init__(self):
        super().__init__(windowType='none')

        # ------------------------------------------------------------------
        # Listen for stats / achievement broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-UserStatsReceived", self._on_stats_received)
        self.accept("Steam-UserStatsStored", self._on_stats_stored)
        self.accept("Steam-UserAchievementStored", self._on_achievement_stored)

        # ------------------------------------------------------------------
        # Request the current user's stats from Steam.  The result arrives
        # asynchronously via Steam-UserStatsReceived.
        # ------------------------------------------------------------------
        print("Requesting user stats...")
        SteamUserStats.request_current_stats()

        self.accept("escape", self.userExit)
        print("Waiting for callbacks... (press Escape to quit)\n")

    # ------------------------------------------------------------------
    # Broadcast callback handlers
    # ------------------------------------------------------------------
    def _on_stats_received(self, result):
        """Fires when RequestCurrentStats() completes."""
        print(f"[BROADCAST] UserStatsReceived: result={result}")

        # Now that stats are loaded we can inspect achievements
        num = SteamUserStats.get_num_achievements()
        print(f"\nThis game has {num} achievement(s) defined.")

        for i in range(num):
            name = SteamUserStats.get_achievement_name(i)
            display = SteamUserStats.get_achievement_display_attribute(name, "name")
            desc = SteamUserStats.get_achievement_display_attribute(name, "desc")
            print(f"  [{i+1}] {display}  ({name})")
            if desc:
                print(f"       {desc}")

        # Unlock an achievement
        print(f"\nUnlocking '{ACHIEVEMENT_FIRST_BLOOD}' ...")
        if SteamUserStats.set_achievement(ACHIEVEMENT_FIRST_BLOOD):
            # store_stats() commits to Steam; confirmation arrives via
            # Steam-UserStatsStored and Steam-UserAchievementStored.
            SteamUserStats.store_stats()
            print("  store_stats() called — waiting for confirmation...")
        else:
            print("  Failed (achievement may not exist for this App ID).")

        # Show incremental progress (UI toast without unlocking)
        print(f"\nShowing progress for '{ACHIEVEMENT_LEVEL_5}' (3 / 5) ...")
        SteamUserStats.indicate_achievement_progress(ACHIEVEMENT_LEVEL_5, 3, 5)

        # Set a stat
        print("\nSetting stat 'num_games' to 42 ...")
        SteamUserStats.set_stat("num_games", 42)
        SteamUserStats.store_stats()

    def _on_stats_stored(self, result):
        """Fires when store_stats() finishes on the backend."""
        print(f"[BROADCAST] UserStatsStored: result={result}")

    def _on_achievement_stored(self, result):
        """Fires when an achievement unlock is confirmed by Steam."""
        print(f"[BROADCAST] UserAchievementStored: {result}")


if __name__ == "__main__":
    demo = AchievementsDemo()
    demo.run()
