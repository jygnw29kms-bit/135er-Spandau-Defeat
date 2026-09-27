# 135er – Spandau Defeat

**Current milestone:** `0.5.1-sharp-ingame` · **Unreal Engine 5.8 / C++**

135er – Spandau Defeat is a native multiplayer first-person shooter built around recognizable locations in Berlin-Spandau and selected historical Berlin scenarios.

## Engine-only image policy

**All public images must be generated directly by the running Unreal Engine 5.8 project.**

The project does not use concept art, AI-generated imagery, mockups, external renders or placeholder screenshots as public game imagery.

Real engine captures are stored under [media/ingame/](media/ingame/) and must follow [docs/INGAME_CAPTURE_STANDARD.md](docs/INGAME_CAPTURE_STANDARD.md).

## Sharp in-game rendering

The production graphics baseline is defined in [game/config/SharpIngame.ini](game/config/SharpIngame.ini):

- 100% native render percentage minimum
- 200% TSR history for showcase-quality reconstruction
- 16× anisotropic filtering
- full-resolution texture streaming / neutral mip bias
- Nanite, Lumen and Virtual Shadow Maps enabled
- restrained sharpening
- motion blur, chromatic aberration and gameplay depth-of-field disabled for clear FPS presentation
- increased view/foliage/mesh detail distance for production captures

The Linux dedicated server remains render-free and independent from client graphics settings.

## Engine and multiplayer

- Unreal Engine 5.8 C++
- native desktop client
- Windows 10+, Linux x86_64 and macOS desktop target
- Linux x86_64 headless Dedicated Server target
- server-authoritative CharacterMovement and hitscan combat
- replicated health, ammo, kills/deaths and capture ownership
- automatic team balancing
- three replicated capture objectives per battlefield
- nominal ~1 km × 1 km battlefield profiles
- 60 Hz server/network configuration

## Maps

Core Spandau set: Rathaus Spandau, Zitadelle, Staaken, Rodelberg, Kiesteich, Falkenhagener Feld, Lynarstraße, Wröhmännerpark and Freiheit.

Historical/special set: Fort Hahneberg 1945, Teufelsberg Cold War, Flugplatz Gatow 1945, Gatow Luftbrücke 1948, Radelandstraße 1945, Hakenfelde/Heeresamt 1944, Zitadelle 1. Mai 1945 and Britischer Sektor Spandau.

Historical material is labeled so documented events are not confused with gameplay fiction. See [docs/HISTORY_MAPS.md](docs/HISTORY_MAPS.md).

## Source snapshot

Latest packed code snapshot:

`game/releases/135er-spandau-defeat-unreal-0.5.0-visual-master-code.tar.xz`

The `0.5.1-sharp-ingame` changes are tracked directly in the repository.

> This repository is the canonical project source for 135er – Spandau Defeat.
