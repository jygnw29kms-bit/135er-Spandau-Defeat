# Source 2 / CS2 project

This directory is the active engine workspace for **135er – Spandau Strike**.

## Current canonical build state

- Version: `0.3.0-source2-map-production`
- Engine/runtime: Counter-Strike 2 / Source 2
- Authoring: Hammer + CS2 Workshop Tools
- Server target: Linux CS2 dedicated server
- Server extension: CounterStrikeSharp
- Active map roster: **20 maps**
- Production specs: **20 / 20**
- Exact LoD2 geometry pipeline: **20 / 20**
- DGM terrain-reference pipeline: **20 / 20**
- Gameplay reference: **Rathaus Spandau**
- Gameplay v2 + NAV seed staging: **19 / 19 remaining maps**
- Unreal/Lyra work is maintained separately and does not replace this Source 2 branch.

## Implemented baseline

- server plugin builds and loads
- A/B/C objective state
- configurable team tickets
- ticket loss on death
- ticket bleed while one team owns all objectives
- map/mode/status commands
- PufferPanel/JL76 profile integration
- 20-map metadata and production specs
- Source 2 visual-master rules
- Berlin LoD2 ingestion and exact building geometry integration
- Berlin DGM terrain-reference generation
- automated map-specific CS2 spawn/bomb/buyzone staging
- automated NAV seed staging
- Valve DMX validation reports

## Current runtime gate

The 19 non-Rathaus gameplay-v2 sources are staged rather than promoted because the current Boot Camp/Workshop Tools command-line environment stalls during Source 2 map preprocessing. The previous successful compiler context used Steam Workshop Tools AppID 2347779 with an authenticated Steam session; Steam currently requires login on the machine.

See `docs/BUILD_STATUS.md`, `build/automation/`, `build/reports/` and `maps/`.
