"""Query Steam Video information.

Shows how to:
- Request video URLs and OPF settings asynchronously
- Listen for GetVideoURLResult and GetOPFSettingsResult broadcast events

The Steam Video interface lets you retrieve video URLs and OPF (Open
Projection Format) settings for apps that have associated video content
such as 360-degree videos or trailers.

NOTE: Most apps do not have video content configured.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d import core
from panda3d_steamworks.showbase import SteamShowBase
from panda3d_steamworks import SteamVideo


class VideoDemo(SteamShowBase):
    """App that requests video info and handles the async results."""

    def __init__(self):
        super().__init__(windowType='none')

        # The app ID to query video info for (use your own app ID).
        self._app_id = 480  # Spacewar (Valve test app)

        # ------------------------------------------------------------------
        # Listen for video broadcast callbacks
        # ------------------------------------------------------------------
        self.accept("Steam-GetVideoURLResult", self._on_video_url)
        self.accept("Steam-GetOPFSettingsResult", self._on_opf_settings)

        # ------------------------------------------------------------------
        # Request the video URL for an app (async)
        # ------------------------------------------------------------------
        SteamVideo.get_video_url(self._app_id)
        print(f"Requested video URL for app {self._app_id} (async).")

        # ------------------------------------------------------------------
        # Request OPF settings (async — used for 360° video playback)
        # ------------------------------------------------------------------
        SteamVideo.get_opf_settings(self._app_id)
        print(f"Requested OPF settings for app {self._app_id} (async).")

        self.accept("escape", self.userExit)
        print("\nWaiting for callbacks... (press Escape to quit)\n")

    # ------------------------------------------------------------------
    # Broadcast callback handlers
    # ------------------------------------------------------------------
    def _on_video_url(self, result):
        """Fires when get_video_url() resolves."""
        print(f"[BROADCAST] GetVideoURLResult: {result}")

    def _on_opf_settings(self, result):
        """Fires when get_opf_settings() resolves."""
        print(f"[BROADCAST] GetOPFSettingsResult: {result}")


if __name__ == "__main__":
    demo = VideoDemo()
    demo.run()
