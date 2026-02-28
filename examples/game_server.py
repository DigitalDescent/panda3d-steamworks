"""Steam Game Server and Game Server Stats.

Demonstrates configuring a dedicated game server, setting server
metadata, and managing player stats/achievements via the server.

NOTE: Game server functions are meant for dedicated server executables.
Running them from a regular client will have limited effect.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamGameServer, SteamGameServerStats
from panda3d_steamworks.showbase import SteamShowBase


def main():
    base = SteamShowBase(windowType='none')

    # ==================================================================
    # SteamGameServer - server identity & metadata
    # ==================================================================
    print("=== Game Server ===")

    steam_id = SteamGameServer.get_steam_id()
    logged_on = SteamGameServer.logged_on()
    secure = SteamGameServer.secure()

    print(f"  Server SteamID : {steam_id}")
    print(f"  Logged on      : {logged_on}")
    print(f"  VAC secure     : {secure}")

    # ------------------------------------------------------------------
    # Server configuration - set metadata visible in the server browser
    # ------------------------------------------------------------------
    SteamGameServer.set_product("panda3d_game")
    SteamGameServer.set_game_description("Panda3D Steamworks Example")
    SteamGameServer.set_mod_dir("panda3d_mod")
    SteamGameServer.set_dedicated_server(True)
    SteamGameServer.set_max_player_count(16)
    SteamGameServer.set_bot_player_count(0)
    SteamGameServer.set_server_name("My Panda3D Server")
    SteamGameServer.set_map_name("de_panda")
    SteamGameServer.set_password_protected(False)
    SteamGameServer.set_spectator_port(27020)
    SteamGameServer.set_spectator_server_name("My Panda3D Server - Spectator")
    SteamGameServer.set_region("us-east")

    # ------------------------------------------------------------------
    # Game tags and key-value data (shown in server browser filters)
    # ------------------------------------------------------------------
    SteamGameServer.set_game_tags("panda3d,example,coop")
    SteamGameServer.set_game_data("version=1.0;mode=coop")
    SteamGameServer.set_key_value("build", "2026.02")

    # Clear all custom key-values:
    # SteamGameServer.clear_all_key_values()

    # ------------------------------------------------------------------
    # Server authentication
    # ------------------------------------------------------------------
    # Log on anonymously (no game server account needed):
    # SteamGameServer.log_on_anonymous()
    #
    # Log on with a game server login token:
    # SteamGameServer.log_on("your_login_token")
    #
    # Log off:
    # SteamGameServer.log_off()

    # ------------------------------------------------------------------
    # Advertise the server so it appears in the server browser
    # ------------------------------------------------------------------
    # SteamGameServer.set_advertise_server_active(True)

    # ------------------------------------------------------------------
    # Player licence check
    # ------------------------------------------------------------------
    # Check if a connected player owns a specific app:
    # has_licence = SteamGameServer.user_has_license_for_app(player_steam_id, app_id)
    # print(f"User has licence: {has_licence}")

    # ==================================================================
    # SteamGameServerStats - manage player stats from the server
    # ==================================================================
    print("\n=== Game Server Stats ===")

    # Request stats for a connected player (async):
    # SteamGameServerStats.request_user_stats(player_steam_id)

    # After stats are loaded, set values:
    # SteamGameServerStats.set_user_stat(player_steam_id, "kills", 10)
    # SteamGameServerStats.update_user_avg_rate_stat(
    #     player_steam_id, "avg_damage", 150.0, 1.0
    # )
    # SteamGameServerStats.set_user_achievement(player_steam_id, "ACH_FIRST_BLOOD")
    # SteamGameServerStats.clear_user_achievement(player_steam_id, "ACH_FIRST_BLOOD")

    # Commit changes:
    # SteamGameServerStats.store_user_stats(player_steam_id)

    base.userExit()


if __name__ == "__main__":
    main()
