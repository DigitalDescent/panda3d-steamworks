---
layout: default
title: Getting Started
nav_order: 2
---

# Getting Started
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Installation

### From PyPI (recommended)

```bash
pip install panda3d-steamworks
```

Pre-built wheels include the compiled extension and the Steamworks shared library — no build tools required.

### From source

```bash
git clone --recurse-submodules https://github.com/DigitalDescent/panda3d-steamworks.git
cd panda3d-steamworks
pip install .
```

#### Build requirements

| Requirement | Notes |
|:------------|:------|
| [Panda3D SDK](https://www.panda3d.org/download/) | With headers — the pip `panda3d` package alone is **not** sufficient |
| [CMake](https://cmake.org/download/) ≥ 3.16 | |
| C++ compiler | Visual Studio (Windows), GCC/Clang (Linux/macOS) |
| [`panda3d-interrogate`](https://pypi.org/project/panda3d-interrogate/) | Generates Python bindings |

#### Build configuration

Options are constants at the top of `setup.py`:

| Constant | Default | Description |
|:---------|:--------|:------------|
| `GENERATE_PDB` | `True` | Emit `.pdb` debug symbols (Windows) |
| `OPTIMIZE` | `3` | Optimisation level — must match your Panda3D build |
| `VERBOSE_IGATE` | `0` | Interrogate verbosity (0 = quiet, 2 = very verbose) |
| `REQUIRE_LIB_BULLET` | `False` | Require Bullet physics library |
| `REQUIRE_LIB_FREETYPE` | `False` | Require Freetype library |

You can also pass options on the command line:

```bash
python setup.py build_ext --optimize=2
python setup.py build_ext --clean-build   # force clean rebuild
```

---

## Prerequisites

### steam_appid.txt

Create a file called `steam_appid.txt` in your working directory containing your Steam App ID:

```
480
```

{: .note }
App ID `480` is Valve's "Spacewar" test app. Replace it with your own App ID for production.

### Steam client

The Steam client must be running for the API to initialise. During development you can use the Spacewar test app without owning a real app.

---

## Minimal example

```python
from panda3d_steamworks import SteamApps

if SteamApps.init():
    print("Steam initialised!")
    print("Language:", SteamApps.get_current_game_language())
    print("Build ID:", SteamApps.get_app_build_id())
    SteamApps.shutdown()
else:
    print("Steam failed to initialise. Is the Steam client running?")
```

---

## Integration with Panda3D

In a real game you'll want to pump Steam callbacks every frame and use Panda3D's messenger for broadcast events:

```python
from direct.showbase.ShowBase import ShowBase
from panda3d_steamworks import SteamApps, SteamCallbackManager, SteamFriends

class MyGame(ShowBase):
    def __init__(self):
        super().__init__()

        if not SteamApps.init():
            raise RuntimeError("Steam failed to initialise")

        print(f"Hello, {SteamFriends.get_persona_name()}!")

        # Pump callbacks every frame
        self.taskMgr.add(self.steam_update, "steam_callbacks")

    def steam_update(self, task):
        SteamCallbackManager.run_callbacks()
        return task.cont

app = MyGame()
app.run()
```

---

## Async callbacks

Many Steamworks operations are asynchronous. Pass a Python callable as the last argument; it will receive a `dict` with the result:

```python
from panda3d_steamworks import SteamMatchmaking

def on_lobby_list(result):
    print(f"Found {result.get('num_lobbies_matching', 0)} lobbies")

SteamMatchmaking.add_request_lobby_list_result_count_filter(10)
SteamMatchmaking.request_lobby_list(on_lobby_list)
```

{: .warning }
You **must** call `SteamCallbackManager.run_callbacks()` every frame for async callbacks to fire. Without it, no callbacks will be dispatched.

---

## Broadcast events

Some Steam events are delivered as Panda3D messenger events (broadcast callbacks). Use `self.accept()` in a `DirectObject` subclass to listen for them:

```python
class MyGame(ShowBase):
    def __init__(self):
        super().__init__()
        SteamApps.init()
        self.taskMgr.add(self.steam_update, "steam_callbacks")

        # Listen for overlay activation
        self.accept("steam-overlay-activated", self.on_overlay)

    def on_overlay(self, active):
        if active:
            print("Overlay opened — consider pausing")
        else:
            print("Overlay closed — resume")

    def steam_update(self, task):
        SteamCallbackManager.run_callbacks()
        return task.cont
```

---

## Next steps

- Browse the [API Reference](api/) for detailed class documentation
- Check out the [Guides](guides/) for common patterns
- Look at the [examples/](https://github.com/DigitalDescent/panda3d-steamworks/tree/main/examples) directory for runnable scripts
