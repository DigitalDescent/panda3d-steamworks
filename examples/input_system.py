"""Initialise and query the Steam Input system.

Steam Input provides a unified API for gamepads, the Steam Deck controls,
and other input devices.  This example initialises the subsystem, polls for
new data, and prints session configuration settings.

NOTE: A valid Input Action Manifest (IGA file) is usually required for full
functionality.  See the Steamworks documentation for details.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamInput


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Initialise Steam Input
    # ------------------------------------------------------------------
    # Pass True to call RunFrame yourself, or False to let Steam handle it.
    ok = SteamInput.init(False)
    print(f"SteamInput.init(): {ok}")

    # ------------------------------------------------------------------
    # Poll for new data
    # ------------------------------------------------------------------
    SteamInput.run_frame(False)

    if SteamInput.new_data_available():
        print("New input data is available.")
    else:
        print("No new input data at this time.")

    # ------------------------------------------------------------------
    # Session configuration
    # ------------------------------------------------------------------
    config = SteamInput.get_session_input_configuration_settings()
    print(f"Session input configuration: {config}")

    # ------------------------------------------------------------------
    # Enable device callbacks (broadcasts connect/disconnect events)
    # ------------------------------------------------------------------
    SteamInput.enable_device_callbacks()
    print("Device callbacks enabled.")

    # ------------------------------------------------------------------
    # Clean up
    # ------------------------------------------------------------------
    SteamInput.shutdown()
    SteamApps.shutdown()


if __name__ == "__main__":
    main()
