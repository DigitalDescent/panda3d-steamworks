"""Set and clear Steam Rich Presence so friends see your game status.

Rich Presence keys must be configured in your Steamworks App Admin under
Community > Rich Presence Localization.  The special key "steam_display"
selects which localization token to show.
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamFriends


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    print(f"Logged in as: {SteamFriends.get_persona_name()}\n")

    # ------------------------------------------------------------------
    # Set Rich Presence key/value pairs
    # ------------------------------------------------------------------
    # These are the custom keys you define in Steamworks App Admin.
    # "steam_display" is the special key that picks the localization token.
    SteamFriends.set_rich_presence("steam_display", "#StatusInGame")
    SteamFriends.set_rich_presence("currentmap", "Dustbowl")
    SteamFriends.set_rich_presence("score", "1500")
    print("Rich Presence set:")
    print("  steam_display = #StatusInGame")
    print("  currentmap    = Dustbowl")
    print("  score         = 1500")

    # Simulate gameplay — Rich Presence stays active
    print("\nRich Presence is now visible to friends.")
    print("Press Ctrl+C to clear and exit.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    # ------------------------------------------------------------------
    # Clear all Rich Presence when done
    # ------------------------------------------------------------------
    SteamFriends.clear_rich_presence()
    print("\nRich Presence cleared.")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
