"""Panda3D Steamworks integration module.

Provides Python bindings for the Steamworks SDK via Panda3D's interrogate
system.  Ships the platform-specific Steamworks shared library so that the
native extension can find it at import time.

Usage::

    from panda3d_steamworks import SteamApps
"""

import os
import sys

# ---------------------------------------------------------------------------
# Ensure the Steamworks shared library can be found at import time.
# On Windows (Python 3.8+) the DLL search paths no longer include the
# working directory or PATH by default for extension modules, so we
# explicitly register this package's directory.
# ---------------------------------------------------------------------------
_pkg_dir = os.path.dirname(os.path.abspath(__file__))

if sys.platform == "win32":
    if hasattr(os, "add_dll_directory"):
        # Python 3.8+
        os.add_dll_directory(_pkg_dir)
        # Also register Panda3D's DLL directory so the extension can find
        # libp3dtool, libp3dtoolconfig, etc. when not using ppython.
        try:
            import panda3d.core  # noqa: F401
            _p3d_dir = os.path.dirname(os.path.abspath(panda3d.core.__file__))
            os.add_dll_directory(_p3d_dir)
        except Exception:
            pass
    else:
        # Older Python - prepend to PATH
        os.environ["PATH"] = _pkg_dir + os.pathsep + os.environ.get("PATH", "")
elif sys.platform == "darwin":
    # macOS: ensure DYLD_LIBRARY_PATH includes the package directory
    os.environ["DYLD_LIBRARY_PATH"] = (
        _pkg_dir + os.pathsep + os.environ.get("DYLD_LIBRARY_PATH", "")
    )
else:
    # Linux / FreeBSD: extend LD_LIBRARY_PATH so the dynamic linker can
    # locate libsteam_api.so that lives next to the extension module.
    os.environ["LD_LIBRARY_PATH"] = (
        _pkg_dir + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    )

# ---------------------------------------------------------------------------
# Import everything from the compiled extension module so that users can
# simply write:
#
#     from panda3d_steamworks import SteamApps
#
# ---------------------------------------------------------------------------
from panda3d_steamworks.panda3d_steamworks import *  # noqa: F401, F403, E402

del os, sys, _pkg_dir
