"""Basic Steamworks initialisation and app-info query."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamApps


def main():
    base = SteamShowBase(windowType='none')

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

    base.userExit()


if __name__ == "__main__":
    main()
