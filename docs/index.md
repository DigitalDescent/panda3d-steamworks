---
layout: default
title: Home
nav_order: 1
permalink: /
---

# panda3d-steamworks
{: .fs-9 }

Python bindings for Valve's Steamworks SDK for the Panda3D game engine.
{: .fs-6 .fw-300 }

[Get started](/panda3d-steamworks/getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[API Reference](/panda3d-steamworks/api/){: .btn .fs-5 .mb-4 .mb-md-0 }

---

**panda3d-steamworks** provides full access to the Steamworks SDK from your Panda3D Python code — achievements, matchmaking, cloud saves, Workshop, friends, networking, and much more.

## Features

| Feature | Class | Description |
|:--------|:------|:------------|
| **App & DLC** | `SteamApps` | Ownership checks, DLC management, language queries, beta branches |
| **Achievements & Stats** | `SteamUserStats` | Unlock achievements, track stats, leaderboards |
| **Friends & Social** | `SteamFriends` | Friends list, rich presence, overlay, clan chat |
| **Matchmaking** | `SteamMatchmaking` | Lobby creation, discovery, filtering, game servers |
| **Cloud Storage** | `SteamRemoteStorage` | Read/write save files to Steam Cloud |
| **Workshop** | `SteamUGC` | Browse, create, and manage user-generated content |
| **Inventory** | `SteamInventory` | In-game item management and microtransactions |
| **Input** | `SteamInput` | Modern controller support with glyphs |
| **Networking** | `SteamNetworkingSockets` | Modern relay-based networking |
| **Game Servers** | `SteamGameServer` | Dedicated server registration and management |
| **HTML Surface** | `SteamHTMLSurface` | Embedded Chromium browser |
| **Screenshots** | `SteamScreenshots` | Screenshot capture and tagging |
| **Music** | `SteamMusic` | Steam music player control |
| **Timeline** | `SteamTimeline` | Game recording timeline events |
| **Remote Play** | `SteamRemotePlay` | Remote Play Together sessions |
| **Parties** | `SteamParties` | Steam Parties beacon system |
| **Parental** | `SteamParentalSettings` | Parental control queries |
| **Utilities** | `SteamUtils` | Overlay, text filtering, device info |

## Quick example

```python
from panda3d_steamworks import SteamApps, SteamCallbackManager

if SteamApps.init():
    print("Steam initialised!")
    print("Language:", SteamApps.get_current_game_language())
    print("Build ID:", SteamApps.get_app_build_id())
    print("Subscribed:", SteamApps.is_subscribed())
    print("DLC count:", SteamApps.get_dlc_count())

    SteamApps.shutdown()
```

{: .note }
A `steam_appid.txt` file containing your app ID must be present in the working directory, or your game must be launched through Steam.

## Architecture

All classes are **static** — you call methods directly on the class (e.g. `SteamApps.init()`) rather than creating instances. Async operations accept a Python callable as the last argument; the callback receives a `dict` with the result fields.

You **must** call `SteamCallbackManager.run_callbacks()` every frame to pump both async call-results and broadcast events. In Panda3D, this is typically done via a task:

```python
from direct.showbase.ShowBase import ShowBase
from panda3d_steamworks import SteamApps, SteamCallbackManager

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()
        SteamApps.init()
        self.taskMgr.add(self.steam_task, "steam_callbacks")

    def steam_task(self, task):
        SteamCallbackManager.run_callbacks()
        return task.cont
```
