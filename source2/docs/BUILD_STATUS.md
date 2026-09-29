# Build status

Version: 0.3.0-source2-map-production

Updated: 2026-09-29

## Current map production state

- 20 / 20 Source 2 Hammer VMAPs exist locally.
- 20 / 20 maps have exact LoD2 building integration from Berlin geodata.
- 20 / 20 previously passed Valve DMX validation and Source 2 World/Physics compilation.
- 20 / 20 DGM terrain reference VMAPs are now generated from the downloaded Berlin DGM samples.
- 20 / 20 DGM terrain reference VMAPs pass Valve `dmxconvert` validation.
- DGM terrain is staged separately and is not blindly overlaid on authored terrain. Teufelsberg, Hahneberg and Rodelberg need a custom merge because they already contain authored relief.

## Gameplay state

- Rathaus Spandau is the current full gameplay reference:
  - 16 Terrorist spawns
  - 16 Counter-Terrorist spawns
  - 2 bomb targets
  - 2 buyzones
  - point_nav_walkable + logic_navigation
- The other 19 maps previously contained only placeholder buyzones.
- Gameplay v2 is now generated for all 19 remaining maps using each map's actual geometry bounds:
  - 16 T spawns
  - 16 CT spawns
  - 2 bomb targets
  - corrected T/CT buyzone placement
  - map-specific opposing spawn sides
- NAV seed entities are staged for all 19 maps at their calculated map centers.
- Gameplay v2 + NAV-seed VMAPs pass Valve `dmxconvert`: 19 OK / 0 FAIL.

## Runtime compile status

The staged sources are intentionally kept separate from the active 19 maps until runtime compilation succeeds.

The current machine is a Mac Pro (2019) / Boot Camp system with Radeon Pro W5700X. The installed AMD Boot Camp display driver is 30.0.13044.22016. Source 2 warns about this driver branch during resource compilation. Direct and incremental command-line map compiles currently stall in map/light preprocessing.

The previous successful build context had Steam Workshop Tools AppID 2347779 loaded with a valid Steam session. Steam currently opens at the login screen, so the final staged gameplay rollout and NAV build remain blocked until the Workshop Tools Steam context is authenticated again.

## Reproducible automation

Tracked scripts:
- `source2/build/automation/gameplay_pass_v2.js`
- `source2/build/automation/navseed_pass.js`
- `source2/build/automation/build_dgm_terrain_maps.py`

Tracked reports:
- `source2/build/reports/gameplay_v2_report.json`
- `source2/build/reports/navseed_report.json`
- `source2/build/reports/dgm_terrain_report.json`

Valve-owned binaries and compiled proprietary runtime resources are not committed.
