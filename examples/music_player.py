"""Interact with the Steam Music player.

Shows how to:
- Query the current playback state
- Control playback using play / pause / next
- Listen for PlaybackStatusHasChanged and VolumeHasChanged broadcasts
- Use Panda3D tasks for timed actions instead of time.sleep()

The user must have Steam Music enabled and tracks available for these
calls to have a visible effect.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from direct.task import Task

from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamMusic

# Playback status constants (from EAudioPlayback_Status)
AUDIO_UNDEFINED = 0
AUDIO_PLAYING = 1
AUDIO_PAUSED = 2
AUDIO_IDLE = 3

_STATUS_LABELS = {
    AUDIO_UNDEFINED: "Undefined",
    AUDIO_PLAYING: "Playing",
    AUDIO_PAUSED: "Paused",
    AUDIO_IDLE: "Idle",
}

class MusicPlayerDemo(SteamShowBase):
    """App that drives the Steam Music player and reacts to callbacks."""

    def __init__(self):
        super().__init__(windowType='none')

        # ------------------------------------------------------------------
        # Listen for music broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-PlaybackStatusHasChanged", self._on_playback_changed)
        self.accept("Steam-VolumeHasChanged", self._on_volume_changed)

        # ------------------------------------------------------------------
        # Print initial state
        # ------------------------------------------------------------------
        print("Steam Music Player")
        print(f"  Enabled         : {SteamMusic.is_enabled()}")
        print(f"  Currently playing: {SteamMusic.is_playing()}")
        print(f"  Playback status : {self._status_label(SteamMusic.get_playback_status())}")
        print(f"  Volume          : {SteamMusic.get_volume():.0%}")

        if not SteamMusic.is_enabled():
            print("\nSteam Music is not enabled. Enable it in Steam settings.")
            self.userExit()
            return

        # ------------------------------------------------------------------
        # Schedule a sequence of playback actions using Panda3D tasks
        # ------------------------------------------------------------------
        self._original_volume = SteamMusic.get_volume()

        sequence = Task.sequence(
            Task.pause(0.5),
            self._make_task("Play", SteamMusic.play),
            Task.pause(2.0),
            self._make_task("Pause", SteamMusic.pause),
            Task.pause(1.0),
            self._make_task("Resume", SteamMusic.play),
            Task.pause(1.0),
            self._make_task("Next track", SteamMusic.play_next),
            Task.pause(1.0),
            self._make_task("Volume -> 50%", lambda: SteamMusic.set_volume(0.5)),
            Task.pause(1.5),
            self._make_task(
                f"Volume -> {self._original_volume:.0%}",
                lambda: SteamMusic.set_volume(self._original_volume),
            ),
            Task.pause(0.5),
        )
        self.taskMgr.add(sequence, "music_demo_sequence")

        self.accept("escape", self.userExit)
        print("\nRunning playback demo... (press Ctrl + C to quit)\n")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _status_label(status):
        return _STATUS_LABELS.get(status, f"Unknown ({status})")

    @staticmethod
    def _make_task(label, action):
        """Return a one-shot task that prints *label* and calls *action*."""
        def _fn(task):
            print(f"  -> {label}")
            action()
            return task.done
        return _fn

    # ------------------------------------------------------------------
    # Broadcast callback handlers
    # ------------------------------------------------------------------
    def _on_playback_changed(self, result):
        status = SteamMusic.get_playback_status()
        print(f"[BROADCAST] PlaybackStatusHasChanged -> {self._status_label(status)}")

    def _on_volume_changed(self, result):
        volume = SteamMusic.get_volume()
        print(f"[BROADCAST] VolumeHasChanged -> {volume:.0%}")


if __name__ == "__main__":
    demo = MusicPlayerDemo()
    demo.run()
