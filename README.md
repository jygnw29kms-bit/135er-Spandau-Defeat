<p align="center">
  <img src="media/theme/repo-hero.svg" alt="135er Spandau Strike" width="100%">
</p>

<p align="center"><strong>135er – Spandau Strike · Berlin-Spandau · Source 2 + Unreal Engine 5 / Lyra</strong></p>

<p align="center"><code>20 maps</code> · <code>Berlin GIS</code> · <code>Blender Master Pipeline</code> · <code>Source 2 / CS2</code> · <code>UE 5.8 / Lyra</code></p>

# Current project status — 2026-10-01

The project is now developed in **two active engine targets** from one shared Berlin/Blender data pipeline:

- **Unreal Engine 5.8 / Lyra** — first playable GIS-based Falkenhagener Feld milestone reached.
- **Counter-Strike 2 / Source 2** — technical server/plugin baseline is working; native Hammer map production remains in progress.
- **Blender master** — shared geometry/terrain preparation layer for both engines.
- **Berlin geodata** — LoD2-derived building heights, OSM roads/water and DGM1 terrain are used as real-world reference/input.

> Project naming: **135er – Spandau Strike**. Older repository/package names may still contain “Spandau Defeat” for compatibility and will be migrated gradually.

## Verified UE5 / Lyra milestone

- UE 5.8.3 Lyra Starter Game project: `C:\Users\dezen\Documents\Unreal Projects\SpandauStrike`
- playable map: `/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld`
- ShooterCore runtime and Control Points A/B/C active
- 8 LyraPlayerStart actors
- NavMeshBoundsVolume + RecastNavMesh
- game phase verified from Warmup to Playing
- standalone `?NumBots=7` validated
- real in-engine screenshot committed at `lyra/docs/screenshots/falkenhagener_feld_ingame_01.png`
- 4,560 usable GIS building actors generated for the 1.8 km × 1.8 km production import
- 1,096 OSM elements processed
- 4,805 road/path segments and 230 water segments generated

The current UE map is a **playable GIS/gameplay blockout**, not final art. Building meshes are still proxy geometry; terrain elevation, collision quality, street surfaces, water, vegetation, landmark replacements and final materials are active production work.

## Blender / terrain master

The shared Blender pipeline lives under `tools/blender_pipeline/`.

Current Falkenhagener Feld terrain coverage uses four Berlin DGM1 tiles because the 1.8 × 1.8 km map crosses 2 km tile boundaries:

- `374_5822`
- `376_5822`
- `374_5824`
- `376_5824`

The Blender master is intended to become the common source for optimized terrain/geometry exports to both **UE5** and **Source 2**, avoiding duplicate manual modeling work.

## Source 2 / CS2 status
Implemented:
- Linux CS2 dedicated-server baseline
- CounterStrikeSharp plugin builds and loads
- A/B/C objective state, tickets and ticket bleed
- map / mode / status commands
- PufferPanel / JL76 integration
- 20-map roster and 20 production specs
- Source 2 map/nav/capture standards

Still required for the first native playable Source 2 map:
- authored Hammer `.vmap` geometry
- compiled Source 2 map output
- map-side objective triggers
- validated collision/navmesh
- final materials/lighting/HUD
- genuine Source 2 in-engine screenshots
- Workshop packaging

## Maps — 20 total

**12 core maps:** Rathaus Spandau · Zitadelle · Staaken · Rodelberg · Kiesteich · Falkenhagener Feld · Lynarstraße · Wröhmännerpark · Freiheit · Martin-Buber-Schule · Askanier-Schule · B.-Traven-Schule

**8 historical/special maps:** Fort Hahneberg 1945 · Teufelsberg – Kalter Krieg · Flugplatz Gatow 1945 · Gatow – Luftbrücke 1948 · Radelandstraße 1945 · Hakenfelde – Heeresamt 1944 · Zitadelle – 1. Mai 1945 · Britischer Sektor Spandau

## Production order

1. Berlin geodata/reference acquisition
2. Blender master cleanup and terrain generation
3. engine-specific export
4. blockout and landmark architecture
5. playable collision, spawns, objectives and navigation
6. materials, roads, water and vegetation
7. combat readability / sightline pass
8. compile and standalone/server validation
9. genuine in-engine screenshots
10. release packaging

## Image rule
- **In-game/gameplay screenshots must come from the actual running engine.**
- AI-generated visuals may only be used as clearly marked optical/reference masters.
- Unreal screenshots are valid only for the UE/Lyra branch; Source 2 screenshots must come from Source 2/CS2.
- README preview images are replaced with genuine engine captures as soon as each map reaches that milestone.

## Key project paths

| Area | Path |
|---|---|
| Current cross-engine status | [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md) |
| Map roster / modes | [docs/MAPS_AND_MODES.md](docs/MAPS_AND_MODES.md) |
| UE5/Lyra GIS status | [lyra/docs/GIS_STATUS.md](lyra/docs/GIS_STATUS.md) |
| UE5/Lyra map definitions | [lyra/maps/maps.json](lyra/maps/maps.json) |
| Source 2 build status | [source2/docs/BUILD_STATUS.md](source2/docs/BUILD_STATUS.md) |
| Source 2 map definitions | [source2/maps/maps.json](source2/maps/maps.json) |
| Source 2 production pipeline | [source2/docs/MAP_PRODUCTION_PIPELINE.md](source2/docs/MAP_PRODUCTION_PIPELINE.md) |
| Blender master pipeline | [tools/blender_pipeline/README.md](tools/blender_pipeline/README.md) |
| Capture policy | [docs/INGAME_CAPTURE_STANDARD.md](docs/INGAME_CAPTURE_STANDARD.md) |

---

<p align="center"><strong>135er – SPANDAU STRIKE</strong><br><sub>BERLIN GIS · BLENDER · SOURCE 2 · UNREAL ENGINE 5</sub></p>
