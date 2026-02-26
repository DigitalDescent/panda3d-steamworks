"""List and manage DLC for the running application."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps

# Replace with your actual DLC App IDs
EXAMPLE_DLC_IDS = [1234, 5678]


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    dlc_count = SteamApps.get_dlc_count()
    print(f"User owns {dlc_count} DLC(s).\n")

    for dlc_id in EXAMPLE_DLC_IDS:
        installed = SteamApps.is_dlc_installed(dlc_id)
        print(f"  DLC {dlc_id}: {'installed' if installed else 'not installed'}")

        # Uncomment the line below to trigger a DLC install via Steam:
        # if not installed:
        #     SteamApps.install_dlc(dlc_id)
        #     print(f"    -> Install requested for DLC {dlc_id}")

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
