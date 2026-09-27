# 135er – Spandau Defeat

**Current milestone:** `0.5.0-visual-master` · **Unreal Engine 5.8 / C++**

135er – Spandau Defeat is a native multiplayer first-person shooter built around recognizable locations in Berlin-Spandau and selected historical Berlin scenarios. The design target is fast objective play with a classic Day-of-Defeat-like immediacy, implemented as an independent Unreal project with original/licensed assets and its own visual identity.

![135er – Spandau Defeat map concepts](media/maps/map-gallery-concept.jpg)

## Visual master lock

The approved map-preview images are now the **binding graphical master** for the project. They define first-person framing, HUD language, cinematic realism, lighting density, material response, atmosphere and level readability. See [docs/VISUAL_MASTER.md](docs/VISUAL_MASTER.md).

The current source implements that direction with:
- native HUD: team tickets, match clock, A/B/C ownership, minimap and live ammo/health
- live ticket drain from deaths and full objective control
- real magazine/reserve ammo plus reload
- UE5 rendering defaults for Lumen, Nanite, Virtual Shadow Maps, TSR and volumetric fog
- runtime `SDVisualDirector` baseline for warm WWII/urban and colder Cold-War presentation
- dedicated-server rendering kept disabled and independent from graphical assets

The procedural graybox remains the gameplay scaffold. Final authored maps must converge on the approved visual masters rather than redefining the style.

## Engine and multiplayer

- Unreal Engine 5.8 C++
- native desktop client — no browser gameplay path
- Windows 10+, Linux x86_64 and macOS desktop target
- Linux x86_64 headless Dedicated Server target
- server-authoritative CharacterMovement and hitscan combat
- replicated health, ammo, kills/deaths and capture ownership
- automatic team balancing
- three replicated capture objectives per battlefield
- nominal ~1 km x 1 km battlefield profiles
- 60 Hz server/network configuration

## Maps

Core Spandau set: Rathaus Spandau, Zitadelle, Staaken, Rodelberg, Kiesteich, Falkenhagener Feld, Lynarstraße, Wröhmännerpark and Freiheit.

Historical/special set: Fort Hahneberg 1945, Teufelsberg Cold War, Flugplatz Gatow 1945, Gatow Luftbrücke 1948, Radelandstraße 1945, Hakenfelde/Heeresamt 1944, Zitadelle 1. Mai 1945 and Britischer Sektor Spandau.

Historical material is labeled so documented events are not confused with gameplay fiction. See [docs/HISTORY_MAPS.md](docs/HISTORY_MAPS.md).

## Source snapshot

Current code snapshot:

`game/releases/135er-spandau-defeat-unreal-0.5.0-visual-master-code.tar.xz`

This archive intentionally contains code/config/docs only. Full-resolution visual master PNGs are kept in the production source package and are not required by the headless server.

A licensed Unreal Engine 5.8 installation/source build is required for compilation.

> This repository is the canonical project source for 135er – Spandau Defeat.
