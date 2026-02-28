"""Query information about the currently logged-in Steam user."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamUser, SteamFriends


def main():
    base = SteamShowBase(windowType='none')

    steam_id = SteamUser.get_steam_id()
    persona = SteamFriends.get_persona_name()
    level = SteamUser.get_player_steam_level()

    print("Current Steam User")
    print(f"  Persona name     : {persona}")
    print(f"  Steam ID (64-bit): {steam_id}")
    print(f"  Steam level      : {level}")
    print(f"  Logged on        : {SteamUser.logged_on()}")
    print(f"  Behind NAT       : {SteamUser.is_behind_nat()}")

    # Account security flags
    print("\nAccount Security")
    print(f"  Phone verified   : {SteamUser.is_phone_verified()}")
    print(f"  Two-factor auth  : {SteamUser.is_two_factor_enabled()}")

    # Game badge info (series 1, non-foil and foil)
    badge = SteamUser.get_game_badge_level(1, False)
    badge_foil = SteamUser.get_game_badge_level(1, True)
    if badge or badge_foil:
        print(f"\nGame Badge (series 1)")
        print(f"  Regular level    : {badge}")
        print(f"  Foil level       : {badge_foil}")

    base.userExit()


if __name__ == "__main__":
    main()
