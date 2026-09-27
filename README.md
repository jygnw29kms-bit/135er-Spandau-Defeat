<p align="center">
  <img src="media/theme/repo-hero.svg" alt="135er – Spandau Defeat" width="100%">
</p>

<p align="center"><strong>Native UE5 multiplayer FPS set across recognizable Spandau locations and selected historical scenarios.</strong></p>

<p align="center"><code>0.5.1-sharp-ingame</code> &nbsp;•&nbsp; <code>Unreal Engine 5.8 / C++</code> &nbsp;•&nbsp; <code>Windows / Linux / macOS</code> &nbsp;•&nbsp; <code>Linux Dedicated Server</code></p>

<p align="center"><img src="media/theme/section-divider.svg" alt="" width="100%"></p>

## MISSION PROFILE

**135er – Spandau Defeat** is a native multiplayer first-person shooter focused on fast objective infantry combat, recognizable Berlin-Spandau locations and a clear, cinematic visual identity.

The current gameplay foundation includes server-authoritative movement and hitscan combat, replicated health/ammo/stats, team balancing, A/B/C capture objectives, ticket drain, live HUD state and dedicated-server support.

> **Visual rule:** approved concept images are the **optical master** for composition, lighting, atmosphere and map identity. They are not labeled as gameplay. Public images labeled **in-game** must be captured directly from the running Unreal Engine 5.8 client.

<p align="center"><img src="media/theme/map-matrix.svg" alt="135er Spandau Defeat map matrix" width="100%"></p>

## CORE MAPS

| Urban / landmark | Terrain / park | School maps |
|---|---|---|
| Rathaus Spandau | Rodelberg | Martin-Buber-Schule |
| Zitadelle Spandau | Kiesteich | Askanier-Schule |
| Staaken | Wröhmännerpark | B.-Traven-Schule |
| Falkenhagener Feld | Freiheit | |
| Lynarstraße | | |

All core battlefields use a nominal **~1 km × 1 km** profile. School maps use recognizable campus massing and local character as visual anchors while routes, cover and sightlines are adapted for balanced multiplayer.

## HISTORICAL / SPECIAL MAPS

Fort Hahneberg 1945 · Teufelsberg Cold War · Flugplatz Gatow 1945 · Gatow Luftbrücke 1948 · Radelandstraße 1945 · Hakenfelde/Heeresamt 1944 · Zitadelle 1. Mai 1945 · Britischer Sektor Spandau.

Historical material is labeled so documented events are not confused with fictional gameplay. See [HISTORY_MAPS](docs/HISTORY_MAPS.md).

<p align="center"><img src="media/theme/section-divider.svg" alt="" width="100%"></p>

## RENDER TARGET

| System | Production baseline |
|---|---|
| Renderer | Unreal Engine 5.8 desktop renderer |
| GI / reflections | Lumen |
| Geometry | Nanite where suitable |
| Shadows | Virtual Shadow Maps |
| AA / reconstruction | TSR |
| Capture baseline | 100% native screen percentage minimum |
| Showcase TSR history | 200% |
| Texture filtering | 16× anisotropic |
| FPS clarity | motion blur / chromatic aberration / gameplay DOF disabled |
| Dedicated server | render-free Linux x86_64 |

The exact sharpness profile is in [`game/config/SharpIngame.ini`](game/config/SharpIngame.ini).

## IMAGE STANDARD

**Optical masters:** concept images may be used as binding art-direction references.

**Engine captures:** only screenshots from the running UE5 project may be described as **in-game**. HUD values shown in gameplay captures must be live game state.

See [`VISUAL_MASTER.md`](docs/VISUAL_MASTER.md) and [`INGAME_CAPTURE_STANDARD.md`](docs/INGAME_CAPTURE_STANDARD.md).

## PROJECT NAVIGATION

| Area | Location |
|---|---|
| Map definitions / modes | [`docs/MAPS_AND_MODES.md`](docs/MAPS_AND_MODES.md) |
| Visual master | [`docs/VISUAL_MASTER.md`](docs/VISUAL_MASTER.md) |
| Historical maps | [`docs/HISTORY_MAPS.md`](docs/HISTORY_MAPS.md) |
| In-game capture standard | [`docs/INGAME_CAPTURE_STANDARD.md`](docs/INGAME_CAPTURE_STANDARD.md) |
| GitHub visual theme | [`docs/GITHUB_THEME.md`](docs/GITHUB_THEME.md) |
| Client render profile | [`game/config/SharpIngame.ini`](game/config/SharpIngame.ini) |
| Engine captures | [`media/ingame/`](media/ingame/) |

## BUILD TARGETS

- Windows 10+ client
- Linux x86_64 desktop client
- macOS desktop client
- Linux x86_64 headless dedicated server
- default gameplay port: `27135`
- 60 Hz server/network configuration target

### Current packed source snapshot

`game/releases/135er-spandau-defeat-unreal-0.5.0-visual-master-code.tar.xz`

The active repository state contains newer `0.5.1-sharp-ingame` configuration/documentation changes beyond that packed snapshot.

---

<p align="center"><strong>135er – SPANDAU DEFEAT</strong><br><sub>SPANDAU • HISTORY • URBAN WARFARE</sub></p>