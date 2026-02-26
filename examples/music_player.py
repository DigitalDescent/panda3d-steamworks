"""Interact with the Steam Music player.

The user must have Steam Music enabled and tracks available for these
calls to have a visible effect.
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamMusic

# Playback status constants (from EAudioPlayback_Status)
AUDIO_UNDEFINED = 0
AUDIO_PLAYING = 1
AUDIO_PAUSED = 2
AUDIO_IDLE = 3


def status_label(status):
    return {
        AUDIO_UNDEFINED: "Undefined",
        AUDIO_PLAYING: "Playing",
        AUDIO_PAUSED: "Paused",
        AUDIO_IDLE: "Idle",
    }.get(status, f"Unknown ({status})")


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    enabled = SteamMusic.is_enabled()
    playing = SteamMusic.is_playing()
    status = SteamMusic.get_playback_status()
    volume = SteamMusic.get_volume()

    print("Steam Music Player")
    print(f"  Enabled         : {enabled}")
    print(f"  Currently playing: {playing}")
    print(f"  Playback status : {status_label(status)}")
    print(f"  Volume          : {volume:.0%}")

    if not enabled:
        print("\nSteam Music is not enabled. Enable it in Steam settings.")
        SteamApps.shutdown()
        return

    # ------------------------------------------------------------------
    # Playback controls
    # ------------------------------------------------------------------
    print("\nControls demo:")

    print("  -> Playing ...")
    SteamMusic.play()
    time.sleep(2)

    print("  -> Pausing ...")
    SteamMusic.pause()
    time.sleep(1)

    print("  -> Resuming ...")
    SteamMusic.play()
    time.sleep(1)

    print("  -> Next track ...")
    SteamMusic.play_next()
    time.sleep(1)

    # Volume adjustment
    original_vol = SteamMusic.get_volume()
    SteamMusic.set_volume(0.5)
    print(f"  -> Volume set to 50%  (was {original_vol:.0%})")
    time.sleep(1)
    SteamMusic.set_volume(original_vol)
    print(f"  -> Volume restored to {original_vol:.0%}")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
