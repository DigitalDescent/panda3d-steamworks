"""Use the Steam HTML Surface to render web content.

The HTML Surface provides a Chromium-based browser that can be used for
in-game web views (e.g. news pages, community hubs, or custom UI).

This example creates a browser instance, loads a URL, and demonstrates
basic browser operations.  In a real game you would render the resulting
texture to a Panda3D card or GUI element.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from panda3d_steamworks import SteamApps, SteamHTMLSurface, SteamCallbackManager


def on_browser_created(result):
    """Called when CreateBrowser completes (async)."""
    print(f"Browser created (async result): {result}")


def main():
    if not SteamApps.init():
        print("Steam failed to initialise.")
        return

    # ------------------------------------------------------------------
    # Initialise the HTML Surface subsystem
    # ------------------------------------------------------------------
    ok = SteamHTMLSurface.init()
    print(f"HTMLSurface.init(): {ok}")

    if not ok:
        SteamApps.shutdown()
        return

    # ------------------------------------------------------------------
    # Create a browser (async - result comes via callback)
    # ------------------------------------------------------------------
    SteamHTMLSurface.create_browser("Panda3D Game", "")
    print("CreateBrowser requested (async).")

    # In a real application you would pump callbacks until you receive
    # the browser handle, then use it for all further operations.
    # For demonstration purposes we show the available API surface:

    # ------------------------------------------------------------------
    # Browser operations (require a valid browser handle)
    # ------------------------------------------------------------------
    # handle = <received from CreateBrowser callback>
    #
    # SteamHTMLSurface.load_url(handle, "https://store.steampowered.com", "")
    # SteamHTMLSurface.set_size(handle, 1280, 720)
    # SteamHTMLSurface.go_back(handle)
    # SteamHTMLSurface.go_forward(handle)
    # SteamHTMLSurface.reload(handle)
    # SteamHTMLSurface.stop_load(handle)
    # SteamHTMLSurface.find(handle, "panda", False, False)
    # SteamHTMLSurface.stop_find(handle)
    #
    # Mouse / scroll interaction:
    # SteamHTMLSurface.mouse_move(handle, 640, 360)
    # SteamHTMLSurface.mouse_wheel(handle, -120)
    # SteamHTMLSurface.set_horizontal_scroll(handle, 0)
    # SteamHTMLSurface.set_vertical_scroll(handle, 200)
    #
    # Execute JavaScript in the page:
    # SteamHTMLSurface.execute_javascript(handle, "alert('Hello from Panda3D!')")
    #
    # Developer tools and page inspection:
    # SteamHTMLSurface.open_developer_tools(handle)
    # SteamHTMLSurface.view_source(handle)
    #
    # Clipboard:
    # SteamHTMLSurface.copy_to_clipboard(handle)
    # SteamHTMLSurface.paste_from_clipboard(handle)
    #
    # Appearance:
    # SteamHTMLSurface.set_page_scale_factor(handle, 1.5, 0, 0)
    # SteamHTMLSurface.set_dpi_scaling_factor(handle, 2.0)
    # SteamHTMLSurface.set_background_mode(handle, True)
    # SteamHTMLSurface.set_key_focus(handle, True)
    #
    # Custom headers and cookies:
    # SteamHTMLSurface.add_header(handle, "X-Custom", "value")
    # SteamHTMLSurface.set_cookie("example.com", "key", "val", "/", 0, True, False)
    #
    # Dialog / navigation control:
    # SteamHTMLSurface.js_dialog_response(handle, True)
    # SteamHTMLSurface.allow_start_request(handle, True)
    #
    # Destroy the browser when done:
    # SteamHTMLSurface.remove_browser(handle)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    SteamHTMLSurface.shutdown()
    SteamApps.shutdown()


if __name__ == "__main__":
    main()
