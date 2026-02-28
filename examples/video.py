"""Query Steam Video information.

The Steam Video interface lets you retrieve video URLs and OPF (Open
Projection Format) settings for apps that have associated video content
such as 360-degree videos or trailers.

NOTE: Most apps do not have video content configured.  Results arrive
asynchronously via broadcast events (Steam-GetVideoURLResult,
Steam-GetOPFSettingsResult).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks import SteamApps, SteamVideo


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # The app ID to query video info for (use your own app ID).
    app_id = 480  # Spacewar (Valve test app)

    # ------------------------------------------------------------------
    # Request the video URL for an app (async)
    # ------------------------------------------------------------------
    SteamVideo.get_video_url(app_id)
    print(f"Requested video URL for app {app_id} (async).")

    # ------------------------------------------------------------------
    # Request OPF settings (async - used for 360° video playback)
    # ------------------------------------------------------------------
    SteamVideo.get_opf_settings(app_id)
    print(f"Requested OPF settings for app {app_id} (async).")

    # Results arrive via broadcast callbacks:
    #   Steam-GetVideoURLResult
    #   Steam-GetOPFSettingsResult
    # Use self.accept() in a Panda3D app to receive them.

    SteamApps.shutdown()


if __name__ == "__main__":
    main()
