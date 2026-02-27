"""Record gameplay events on the Steam Timeline.

The Steam Timeline lets players and viewers see annotated highlights
of a play session.  This example demonstrates tooltips, game phases,
phase tags, and attributes.

NOTE: Timeline features require Steam client with Timeline support.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamTimeline


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Tooltips - short descriptions that appear on the timeline bar
    # ------------------------------------------------------------------
    # flTimeDelta is seconds relative to "now" (negative = past).
    SteamTimeline.set_timeline_tooltip("Entered the dungeon", 0.0)
    print("Set tooltip: 'Entered the dungeon'")

    # Clear a previous tooltip (e.g. when returning to neutral gameplay)
    # SteamTimeline.clear_timeline_tooltip(0.0)

    # ------------------------------------------------------------------
    # Game phases - bracketed sections of gameplay (e.g. a boss fight)
    # ------------------------------------------------------------------
    SteamTimeline.start_game_phase()
    print("Game phase started.")

    # Give the phase a human-readable ID
    SteamTimeline.set_game_phase_id("boss_fight_01")

    # Add tags that describe the phase (shown in overlay UI)
    SteamTimeline.add_game_phase_tag(
        "Boss Fight",       # tag name
        "boss_icon",        # tag icon (Steam-defined or custom)
        "Encounters",       # tag group
        0,                  # priority (0 = highest)
    )

    # Attributes provide key-value metadata for the phase
    SteamTimeline.set_game_phase_attribute("Difficulty", "Hard", 0)

    # End the phase (e.g. boss defeated)
    SteamTimeline.end_game_phase()
    print("Game phase ended.")

    # ------------------------------------------------------------------
    # Open the overlay to a recorded game phase
    # ------------------------------------------------------------------
    # SteamTimeline.open_overlay_to_game_phase("boss_fight_01")

    # ------------------------------------------------------------------
    # Check whether a recording exists for a phase
    # ------------------------------------------------------------------
    # async - result arrives via callback
    # SteamTimeline.does_game_phase_recording_exist("boss_fight_01")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
