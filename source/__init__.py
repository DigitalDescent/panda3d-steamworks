"""Panda3D Steamworks integration module.

Provides Python bindings for the Steamworks SDK via Panda3D's interrogate
system.  Ships the platform-specific Steamworks shared library so that the
native extension can find it at import time.

Usage::

    from panda3d_steamworks import SteamApps
"""
# ---------------------------------------------------------------------------
# Import everything from the compiled native extension module so that users
# can simply write:
#
#     from panda3d_steamworks import SteamApps
#
# ---------------------------------------------------------------------------
from panda3d_steamworks.native import *  # noqa: F401, F403, E402