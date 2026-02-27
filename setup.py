"""
setup.py - PyPI-publishable build for panda3d-steamworks.

This file provides a custom ``build_ext`` command that:

1. Invokes the CMake / P3DModuleBuilder build system directly (interrogate +
   compile) to produce the native extension.
2. Copies the resulting ``.pyd`` / ``.so`` into the ``panda3d_steamworks``
   Python package directory.
3. Copies the platform-specific Steamworks shared library (e.g.
   ``steam_api64.dll``) alongside it so that it is included in the wheel.
"""

import multiprocessing
import os
import platform
import shutil
import subprocess
import sys
import sysconfig

from setuptools import Distribution, Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

# ---------------------------------------------------------------------------
# Panda3D must be imported first (engine quirk)
# ---------------------------------------------------------------------------
import panda3d.core  # noqa: E402

# ---------------------------------------------------------------------------
# Build configuration - edit these instead of a config file
# ---------------------------------------------------------------------------
MODULE_NAME = "panda3d_steamworks"
GENERATE_PDB = True          # Emit .pdb debug symbols (Windows only)
OPTIMIZE = 3                 # Must match the Panda3D SDK build (1-4)
VERBOSE_IGATE = 0            # Interrogate verbosity: 0=quiet, 1=verbose, 2=very verbose
REQUIRE_LIB_BULLET = False   # Require Bullet physics library
REQUIRE_LIB_FREETYPE = False # Require Freetype library

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STEAMWORKS_REDIST = os.path.join(
    ROOT_DIR, "thirdparty", "steamworks", "redistributable_bin"
)

# Make the helper scripts importable
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
from common import (  # noqa: E402
    get_output_dir,
    get_output_name,
    get_script_dir,
    try_makedir,
    fatal_error,
    is_windows,
    is_linux,
    is_macos,
    is_freebsd,
    is_64_bit,
    is_installed_via_pip,
    join_abs,
    get_panda_lib_path,
    get_panda_msvc_version,
    get_win_thirdparty_dir,
    have_bullet,
    have_freetype,
    try_execute,
    print_error,
)
from panda3d.core import PandaSystem


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _native_ext_suffix():
    """Return the file extension for native extensions on the current platform."""
    if sys.platform == "win32":
        return ".pyd"
    return sysconfig.get_config_var("EXT_SUFFIX") or ".so"


def _pkg_dir():
    """Return the path to the panda3d_steamworks package directory."""
    return os.path.join(ROOT_DIR, "panda3d_steamworks")


def _built_module_path():
    """Return the path to the module built by the CMake step (package dir)."""
    if sys.platform == "win32":
        return os.path.join(_pkg_dir(), "panda3d_steamworks.pyd")
    return os.path.join(_pkg_dir(), "panda3d_steamworks.so")


def _steam_shared_libs():
    """
    Return a list of ``(src_path, filename)`` tuples for every Steamworks
    shared library that must be bundled with the wheel for the current
    platform.
    """
    libs = []

    if sys.platform == "win32":
        if platform.machine().endswith("64"):
            dll = os.path.join(STEAMWORKS_REDIST, "win64", "steam_api64.dll")
            libs.append((dll, "steam_api64.dll"))
        else:
            dll = os.path.join(STEAMWORKS_REDIST, "steam_api.dll")
            libs.append((dll, "steam_api.dll"))

    elif sys.platform == "darwin":
        dylib = os.path.join(STEAMWORKS_REDIST, "osx", "libsteam_api.dylib")
        libs.append((dylib, "libsteam_api.dylib"))

    else:
        # Linux / FreeBSD
        machine = platform.machine()
        if machine == "aarch64":
            so = os.path.join(STEAMWORKS_REDIST, "linuxarm64", "libsteam_api.so")
        elif machine in ("x86_64", "AMD64"):
            so = os.path.join(STEAMWORKS_REDIST, "linux64", "libsteam_api.so")
        else:
            so = os.path.join(STEAMWORKS_REDIST, "linux32", "libsteam_api.so")
        libs.append((so, "libsteam_api.so"))

    return libs


# ---------------------------------------------------------------------------
# CMake build helpers  (inlined from build.py / scripts/setup.py)
# ---------------------------------------------------------------------------

def _handle_cmake_error(output):
    """Pretty-print CMake errors."""
    print_error("\n" + "-" * 60)
    print_error("\nCMake Error:")
    if "Re-run cmake with a different source directory." in output:
        print_error("The project folder was moved - delete the build dir and retry.")
    elif "No CMAKE_CXX_COMPILER could be found." in output or \
         "No CMAKE_C_COMPILER could be found." in output:
        print_error("Could not find the required compiler!")
        if is_windows():
            bitness = "64 bit" if is_64_bit() else ""
            print_error(get_panda_msvc_version().cmake_str, bitness)
        else:
            print_error("The required compiler is:", PandaSystem.get_compiler())
    print_error("-" * 60 + "\n")
    sys.exit(1)


def _make_output_dir(clean=False):
    """Create (or clean) the CMake build directory and cd into it."""
    output_dir = get_output_dir()
    if os.path.isdir(output_dir) and clean:
        print("Cleaning up output directory …")
        shutil.rmtree(output_dir)
    try_makedir(output_dir)
    if not os.path.isdir(output_dir):
        fatal_error("Could not create output directory at:", output_dir)
    os.chdir(output_dir)


def _run_cmake(config):
    """Configure the CMake project."""
    configuration = "RelWithDebInfo" if config["generate_pdb"] else "Release"

    cmake_args = [
        "-DCMAKE_BUILD_TYPE=" + configuration,
        "-DPYTHON_EXECUTABLE:STRING=" + sys.executable,
        "-DPROJECT_NAME:STRING=" + config["module_name"],
    ]

    lib_prefix = "lib" if is_windows() else ""

    if is_installed_via_pip():
        fatal_error(
            "Panda3D appears to be installed as a pip package. "
            "Headers are not included — install the Panda3D SDK instead: "
            "http://www.panda3d.org/download.php?sdk"
        )

    # Interrogate library detection
    if PandaSystem.get_major_version() > 1 or PandaSystem.get_minor_version() > 9:
        interrogatedb_lib = lib_prefix + "p3interrogatedb"
        # Determine the actual library filename on disk for the existence check.
        # On Windows: libp3interrogatedb.lib   (lib_prefix="lib", ext=".lib")
        # On macOS:   libp3interrogatedb.dylib  (file prefix="lib", ext=".dylib")
        # On Linux:   libp3interrogatedb.so     (file prefix="lib", ext=".so")
        if is_windows():
            check_filename = interrogatedb_lib + ".lib"
        elif is_macos():
            check_filename = "libp3interrogatedb.dylib"
        else:
            check_filename = "libp3interrogatedb.so"
        if os.path.isfile(join_abs(get_panda_lib_path(), check_filename)):
            cmake_args.append("-DINTERROGATE_LIB:STRING=" + interrogatedb_lib)
        else:
            cmake_args.append("-DINTERROGATE_LIB:STRING=" + lib_prefix + "panda")
    else:
        if not os.path.isfile(join_abs(get_panda_lib_path(), "core.lib")):
            cmake_args.append("-DINTERROGATE_LIB:STRING=" + lib_prefix + "panda")
        else:
            cmake_args.append("-DINTERROGATE_LIB:STRING=core")

    # Generator / architecture
    if is_windows():
        cmake_args += ["-G" + get_panda_msvc_version().cmake_str]
        cmake_args += ["-Ax64"] if is_64_bit() else ["-AWin32"]
    elif is_macos():
        cmake_args.append("-DCMAKE_CL_64:STRING=1")

    # Python version
    pyver = "{}{}".format(sys.version_info.major, sys.version_info.minor)
    pyver_dot = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
    if is_windows():
        cmake_args.append("-DPYTHONVER:STRING=" + pyver)
    if is_linux() or is_freebsd() or is_macos():
        cmake_args.append("-DPYTHONVERDOT:STRING=" + pyver_dot)

    # Thirdparty directory
    if is_windows():
        cmake_args.append("-DTHIRDPARTY_WIN_DIR=" + get_win_thirdparty_dir())
    else:
        cmake_args.append("-DTHIRDPARTY_WIN_DIR=")

    # Library requirements
    cmake_args.append("-DHAVE_LIB_EIGEN=TRUE")

    if config["require_lib_bullet"]:
        if not have_bullet():
            fatal_error("Panda3D was not compiled with bullet support, but it is required!")
        cmake_args.append("-DHAVE_LIB_BULLET=TRUE")

    if config["require_lib_freetype"]:
        if not have_freetype():
            fatal_error("Panda3D was not compiled with freetype support, but it is required!")
        cmake_args.append("-DHAVE_LIB_FREETYPE=TRUE")

    # Optimisation
    cmake_args.append("-DOPTIMIZE=" + str(config["optimize"]))

    # Interrogate verbosity
    cmake_args.append("-DIGATE_VERBOSE=" + str(config["verbose_igate"]))

    try_execute("cmake", join_abs(get_script_dir(), ".."), *cmake_args,
                error_formatter=_handle_cmake_error)


def _run_cmake_build(config):
    """Run the actual CMake build step."""
    configuration = "RelWithDebInfo" if config["generate_pdb"] else "Release"

    if is_linux() or is_macos() or is_freebsd():
        core_option = "-j" + str(max(1, multiprocessing.cpu_count() - 1))
    else:
        core_option = "/m"

    try_execute("cmake", "--build", ".", "--config", configuration, "--", core_option)


# ---------------------------------------------------------------------------
# Dummy Extension - just so setuptools knows there is a native component
# ---------------------------------------------------------------------------

class CMakeExtension(Extension):
    """Sentinel extension - no *real* sources; CMake does the heavy lifting."""

    def __init__(self, name):
        super().__init__(name, sources=[])


# ---------------------------------------------------------------------------
# Custom build_ext
# ---------------------------------------------------------------------------

class CMakeBuild(_build_ext):
    """
    Custom ``build_ext`` that configures, compiles, and copies the native
    extension + Steamworks shared libraries into the wheel staging directory.
    """

    user_options = _build_ext.user_options + [
        ("optimize=", None, "Optimisation level (must match Panda3D build)"),
        ("clean-build", None, "Force a clean CMake rebuild"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.optimize = None
        self.clean_build = False

    def finalize_options(self):
        super().finalize_options()
        if self.optimize is not None:
            self.optimize = int(self.optimize)

    def run(self):
        # Verify CMake is available
        try:
            subprocess.check_output(["cmake", "--version"])
        except Exception:
            raise RuntimeError(
                "CMake is required to build this package. "
                "Install it from https://cmake.org/download/"
            )
        super().run()

    def build_extension(self, ext):
        # ---- 0. Run code generation from steam_api.json --------------------
        from codegen import run_codegen
        print("Running Steamworks code generation …")
        run_codegen(root_dir=ROOT_DIR)

        # ---- 1. Build config dict from top-of-file constants ----------------
        config = {
            "module_name": MODULE_NAME,
            "generate_pdb": GENERATE_PDB,
            "optimize": OPTIMIZE,
            "verbose_igate": VERBOSE_IGATE,
            "require_lib_bullet": REQUIRE_LIB_BULLET,
            "require_lib_freetype": REQUIRE_LIB_FREETYPE,
        }

        # Apply command-line overrides
        if self.optimize is not None:
            config["optimize"] = self.optimize

        # ---- 2. Run CMake configure + build --------------------------------
        saved_cwd = os.getcwd()
        try:
            _make_output_dir(clean=bool(self.clean_build))
            _run_cmake(config)
            _run_cmake_build(config)
        finally:
            os.chdir(saved_cwd)

        # ---- 3. Copy Steamworks shared libs into the package dir -----------
        #     (finalize.py already placed the .pyd/.so + .pdb there)
        pkg = _pkg_dir()
        for src_path, filename in _steam_shared_libs():
            if not os.path.isfile(src_path):
                raise RuntimeError(
                    f"Steamworks shared library not found: {src_path}\n"
                    "Make sure the steamworks SDK submodule is initialised:\n"
                    "  git submodule update --init"
                )
            shutil.copy2(src_path, os.path.join(pkg, filename))

        # ---- 4. Determine wheel staging directory ---------------------------
        ext_fullpath = self.get_ext_fullpath(ext.name)
        dest_dir = os.path.dirname(os.path.abspath(ext_fullpath))
        os.makedirs(dest_dir, exist_ok=True)

        # ---- 5. Copy everything into the wheel staging directory ------------
        built = _built_module_path()
        if not os.path.isfile(built):
            raise RuntimeError(
                f"Build succeeded but the extension was not found at {built}"
            )
        shutil.copy2(built, ext_fullpath)

        for _, filename in _steam_shared_libs():
            src = os.path.join(pkg, filename)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest_dir, filename))

        # ---- 6. Copy PDB if present (debug info, Windows only) --------------
        if sys.platform == "win32":
            pdb = os.path.join(pkg, "panda3d_steamworks.pdb")
            if os.path.isfile(pdb):
                shutil.copy2(pdb, os.path.join(dest_dir, "panda3d_steamworks.pdb"))


# ---------------------------------------------------------------------------
# Force platform-specific wheel tag even though we have no "real" Extension
# ---------------------------------------------------------------------------

class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


# ---------------------------------------------------------------------------
# Package definition
# ---------------------------------------------------------------------------

setup(
    ext_modules=[
        # The extension is placed *inside* the panda3d_steamworks package so
        # __init__.py can do ``from .panda3d_steamworks import *``.
        CMakeExtension("panda3d_steamworks.panda3d_steamworks"),
    ],
    cmdclass={"build_ext": CMakeBuild},
    distclass=BinaryDistribution,
)
