"""
Copyright (c) 2026 Digital Descent LLC. All rights reserved.
"""

from panda3d import core
from panda3d_steamworks import SteamApps, SteamCallbackManager, SteamNetworkingSockets, SteamUserStats, SteamMatchmaking, SteamFriends

from direct.showbase.ShowBase import ShowBase

class SteamShowBase(ShowBase):
    """
    Variant of the Panda3D ShowBase class for use in Steam applications.
    Automatically handles integrations with Valve's Steamworks SDK, such as processing Steam callbacks and
    ensuring the Steam API is properly initialized and shut down.  Users can subclass this to create their main application class, 
    and it will take care of the necessary Steamworks integration behind the scenes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Verify Steamworks is initialized
        if not SteamApps.init():
            raise RuntimeError("Failed to initialize Steamworks API. Make sure Steam is running and the app is launched through Steam.")

        # Execute Steam callbacks every frame. This is **required** for any
        # async operations or broadcast callbacks to function properly.
        self.task_mgr.add(self._steam_callbacks, "steam_callbacks")

    def _steam_callbacks(self, task: object) -> int:
        """
        Task to invoke SteamAPI_RunCallbacks every frame, 
        which is required for any async operations or broadcast callbacks 
        to function properly.
        """

        SteamCallbackManager.run_callbacks()
        SteamNetworkingSockets.run_callbacks()
        
        return task.cont

    def finalizeExit(self) -> None:
        """
        Called by `userExit()` to quit the application. 
        Automatically shuts down the Steam API and callback manager before exiting.
        """

        SteamCallbackManager.shutdown()
        SteamApps.shutdown()

        super().finalizeExit()