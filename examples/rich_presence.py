"""Set and clear Steam Rich Presence so friends see your game status.

Shows how to:
- Set Rich Presence key/value pairs visible to friends
- Periodically update Rich Presence using a Panda3D task
- Clean up Rich Presence on exit via SteamShowBase lifecycle

Rich Presence keys must be configured in your Steamworks App Admin under
Community > Rich Presence Localization.  The special key "steam_display"
selects which localization token to show.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamFriends


class RichPresenceDemo(SteamShowBase):
    """App that maintains Rich Presence while running."""

    def __init__(self):
        super().__init__(windowType='none')

        self._score = 0

        print(f"Logged in as: {SteamFriends.get_persona_name()}\n")

        # ------------------------------------------------------------------
        # Set initial Rich Presence key/value pairs
        # ------------------------------------------------------------------
        SteamFriends.set_rich_presence("steam_display", "#StatusInGame")
        SteamFriends.set_rich_presence("currentmap", "Dustbowl")
        SteamFriends.set_rich_presence("score", str(self._score))
        print("Rich Presence set:")
        print("  steam_display = #StatusInGame")
        print("  currentmap    = Dustbowl")
        print(f"  score         = {self._score}")

        # ------------------------------------------------------------------
        # Periodically update Rich Presence (simulates gameplay)
        # ------------------------------------------------------------------
        self.taskMgr.doMethodLater(
            5.0, self._update_score, "rich_presence_update"
        )

        self.accept("escape", self._cleanup)
        print("\nRich Presence is now visible to friends.")
        print("Score updates every 5 seconds. press Ctrl + C to quit.\n")

    # ------------------------------------------------------------------
    # Periodic task
    # ------------------------------------------------------------------
    def _update_score(self, task):
        self._score += 100
        SteamFriends.set_rich_presence("score", str(self._score))
        print(f"  [update] score = {self._score}")
        return task.again

    # ------------------------------------------------------------------
    # Clean exit
    # ------------------------------------------------------------------
    def _cleanup(self):
        SteamFriends.clear_rich_presence()
        print("\nRich Presence cleared.")
        self.userExit()


if __name__ == "__main__":
    demo = RichPresenceDemo()
    demo.run()
