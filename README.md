# panda3d-steamworks

Python bindings for [Valve's Steamworks SDK](https://partner.steamgames.com/doc/sdk) for the [Panda3D](https://www.panda3d.org/) game engine.

Provides access to Steamworks features — app ownership, DLC management, language queries, and more — directly from your Panda3D Python code.

## Installation

### From PyPI

```bash
pip install panda3d-steamworks
```

### From source

```bash
git clone --recurse-submodules https://github.com/DigitalDescent/panda3d-steamworks.git
cd panda3d-steamworks
pip install --no-build-isolation .
```

## Quick start

```python
from panda3d_steamworks import SteamApps

if SteamApps.init():
    print("Steam initialised!")
    print("Language:", SteamApps.get_current_game_language())
    print("Build ID:", SteamApps.get_app_build_id())
    print("Subscribed:", SteamApps.is_subscribed())

    # DLC
    print("DLC count:", SteamApps.get_dlc_count())

    SteamApps.shutdown()
```

> **Note:** A valid `steam_appid.txt` file must be present in the working
> directory (or your game must be launched through Steam) for `SteamApps.init()`
> to succeed.

## Requirements

- [Panda3D SDK](https://www.panda3d.org/download/) (with headers — the pip `panda3d` package alone is **not** sufficient for building from source)
- [CMake](https://cmake.org/download/) 3.16 or higher
- A C++ compiler compatible with your Panda3D build (Visual Studio on Windows, GCC/Clang on Linux/macOS)
- [`panda3d-interrogate`](https://pypi.org/project/panda3d-interrogate/) for generating Python bindings

Pre-built wheels include the compiled extension and the Steamworks shared library, so end users only need `pip install panda3d-steamworks`.

## Building from source

```bash
# Clone with the Steamworks SDK submodule
git clone --recurse-submodules https://github.com/DigitalDescent/panda3d-steamworks.git
cd panda3d-steamworks

# Install in development mode
pip install --no-build-isolation -e .

# Or build a wheel for distribution
pip install build
python -m build --wheel
```

### Build configuration

Build options are constants at the top of `setup.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `GENERATE_PDB` | `True` | Generate a `.pdb` debug symbol file (Windows). |
| `OPTIMIZE` | `3` | Optimisation level (must match your Panda3D build). |
| `VERBOSE_IGATE` | `0` | Interrogate verbosity (`0` = quiet, `1` = verbose, `2` = very verbose). |
| `REQUIRE_LIB_BULLET` | `False` | Require the Bullet physics library. |
| `REQUIRE_LIB_FREETYPE` | `False` | Require the Freetype library. |

You can also pass options via `setup.py`:

- `python setup.py build_ext --optimize=N`
- `python setup.py build_ext --clean-build` — force a clean rebuild

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

The Steamworks SDK is Copyright © Valve Corporation and is subject to the the rules outlined at [Distributing Open source](https://partner.steamgames.com/doc/sdk/uploading/distributing_opensource).

