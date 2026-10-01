# Source 2 / CS2 project

This directory is the active engine workspace for **135er – Spandau Strike**.

## Current canonical build state

- Version: `0.2.1-source2-alpha`
- Engine/runtime: Counter-Strike 2 / Source 2
- Authoring: Hammer + CS2 Workshop Tools
- Server target: Linux CS2 dedicated server
- Server extension: CounterStrikeSharp
- Active map roster: **20 maps**
- Production specs: **20 / 20**
- Unreal Engine: retired

## Implemented baseline

- server plugin builds and loads
- A/B/C objective state
- configurable team tickets
- ticket loss on death
- 10-second ticket bleed while one team owns all three objectives
- map/mode/status commands
- PufferPanel/JL76 profile integration
- map metadata, maplist and per-map production specs
- Source 2 visual-master/capture policy

## Still pending before playable map alpha

- authored Hammer `.vmap` sources
- compiled Source 2 map packages
- map-side objective triggers
- final class/weapon rules
- final HUD
- genuine in-engine screenshots
- Workshop publication IDs

Valve-owned Counter-Strike 2 / Source 2 binaries and proprietary game content are not committed here.

See [docs/BUILD_STATUS.md](docs/BUILD_STATUS.md) and [maps/](maps/).
