"""Basic Steamworks initialisation and app-info query."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps


def main():
    if not SteamApps.init():
        print("Steam failed to initialise - is Steam running and steam_appid.txt present?")
        return

    print("Steam initialised successfully!")
    print(f"  Build ID      : {SteamApps.get_app_build_id()}")
    print(f"  Language       : {SteamApps.get_current_game_language()}")
    print(f"  Available langs: {SteamApps.get_available_game_languages()}")
    print(f"  Owner Steam ID : {SteamApps.get_app_owner()}")

    beta = SteamApps.get_current_beta_name()
    if beta:
        print(f"  Beta branch    : {beta}")
    else:
        print("  Beta branch    : (none)")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
