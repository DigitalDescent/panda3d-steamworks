"""Initialise and query the Steam Input system.

Shows how to:
- Initialise Steam Input and poll each frame via a Panda3D task
- Listen for device connect/disconnect broadcast callbacks
- Query session configuration settings

Steam Input provides a unified API for gamepads, the Steam Deck controls,
and other input devices.

NOTE: A valid Input Action Manifest (IGA file) is usually required for full
functionality.  See the Steamworks documentation for details.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamInput


class InputDemo(SteamShowBase):
    """App that polls Steam Input each frame and reacts to device events."""

    def __init__(self):
        super().__init__(windowType='none')

        # ------------------------------------------------------------------
        # Initialise Steam Input
        # ------------------------------------------------------------------
        # Pass True to call RunFrame yourself, False to let Steam handle it.
        ok = SteamInput.init(True)
        print(f"SteamInput.init(): {ok}")

        if not ok:
            print("Failed to initialise Steam Input.")
            self.userExit()
            return

        # ------------------------------------------------------------------
        # Listen for device connect/disconnect broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-SteamInputDeviceConnected", self._on_device_connected)
        self.accept("Steam-SteamInputDeviceDisconnected", self._on_device_disconnected)

        SteamInput.enable_device_callbacks()
        print("Device callbacks enabled.")

        # ------------------------------------------------------------------
        # Print initial configuration
        # ------------------------------------------------------------------
        config = SteamInput.get_session_input_configuration_settings()
        print(f"Session input configuration: {config}")

        # ------------------------------------------------------------------
        # Poll for new input data each frame
        # ------------------------------------------------------------------
        self.taskMgr.add(self._poll_input, "steam_input_poll")

        self.accept("escape", self._cleanup)
        print("\nPolling for input... (press Escape to quit)\n")

    # ------------------------------------------------------------------
    # Per-frame polling task
    # ------------------------------------------------------------------
    def _poll_input(self, task):
        SteamInput.run_frame(False)
        if SteamInput.new_data_available():
            print("  [poll] New input data available")
        return task.cont

    # ------------------------------------------------------------------
    # Broadcast callback handlers
    # ------------------------------------------------------------------
    def _on_device_connected(self, result):
        print(f"[BROADCAST] SteamInputDeviceConnected: {result}")

    def _on_device_disconnected(self, result):
        print(f"[BROADCAST] SteamInputDeviceDisconnected: {result}")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def _cleanup(self):
        SteamInput.shutdown()
        self.userExit()


if __name__ == "__main__":
    demo = InputDemo()
    demo.run()
