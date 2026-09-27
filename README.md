# 135er – Spandau Defeat

**Current milestone:** `0.5.1-sharp-ingame` · **Unreal Engine 5.8 / C++**

135er – Spandau Defeat is a native multiplayer first-person shooter built around recognizable locations in Berlin-Spandau and selected historical Berlin scenarios. The design target is fast objective play with a classic Day-of-Defeat-like immediacy, implemented as an independent Unreal project with original/licensed assets and its own visual identity.

![135er – Spandau Defeat map concepts](media/maps/map-gallery-concept.jpg)

## 0.5.1 sharp in-game pass

The client rendering baseline now has a dedicated production profile in [game/config/SharpIngame.ini](game/config/SharpIngame.ini).

It locks the current visual direction to:
- 100% native render percentage minimum
- 200% TSR history for showcase-quality reconstruction
- 16× anisotropic filtering
- full-resolution texture streaming / neutral mip bias
- Nanite, Lumen and Virtual Shadow Maps enabled
- restrained tonemapper sharpening
- motion blur, chromatic aberration and gameplay depth-of-field disabled for clear first-person readability
- increased view/foliage/mesh detail distance for production captures

The dedicated Linux server remains render-free and independent from these client graphics settings.

Real UE5 gameplay captures are kept separate from concept art under [media/ingame/](media/ingame/). Only images captured from a running map with live HUD/game state may be labeled **in-game**. See [docs/INGAME_CAPTURE_STANDARD.md](docs/INGAME_CAPTURE_STANDARD.md).

## Visual master lock

The approved map-preview images remain the **binding graphical master** for authored environment art. They define first-person framing, HUD language, cinematic realism, lighting density, material response, atmosphere and level readability. See [docs/VISUAL_MASTER.md](docs/VISUAL_MASTER.md).

The current gameplay foundation includes:
- native HUD: team tickets, match clock, A/B/C ownership, minimap and live ammo/health
- live ticket drain from deaths and full objective control
- real magazine/reserve ammo plus reload
- UE5 rendering defaults for Lumen, Nanite, Virtual Shadow Maps, TSR and volumetric fog
- runtime `SDVisualDirector` baseline for warm WWII/urban and colder Cold-War presentation
- server-authoritative multiplayer systems
- dedicated-server rendering disabled

## Engine and multiplayer

- Unreal Engine 5.8 C++
- native desktop client — no browser gameplay path
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

The latest packed code snapshot remains:

`game/releases/135er-spandau-defeat-unreal-0.5.0-visual-master-code.tar.xz`

The `0.5.1-sharp-ingame` changes are currently tracked directly in the repository as configuration/documentation additions. A refreshed source archive should only be cut from the full UE5 source tree so the archive and repo cannot drift apart.

A licensed Unreal Engine 5.8 installation/source build is required for compilation.

> This repository is the canonical project source for 135er – Spandau Defeat.
