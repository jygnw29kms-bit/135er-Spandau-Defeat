# Rathaus World Master v23

Updated: 2026-10-14

## Authoritative production master

`tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v23_GROUNDED_CLEAN.blend`

This is the current Blender production master for the Rathaus Spandau map. Unreal test levels v70/v77/REAL_FINAL are not production geometry sources.

## Coordinate frame

The FULLMAP coordinate frame is fixed to EPSG:25833 local origin:
- E = 377931.576
- N = 5822067.058
- Z reference = 31.0 m

Local coordinates are `X = E-originE`, `Y = N-originN`, `Z = absolute height-31.0`.

The older GIS import origin was E 377897.8969272321 / N 5822086.91786854. Its documented FULLMAP alignment offset is -33.679072768 m X / +19.859868539 m Y / +2.45 m Z. New production geometry must not inherit that object transform; it must be baked into the common FULLMAP frame.

## Terrain

Source: Berlin DGM1 tiles 376_5820, 378_5820, 376_5822, 378_5822.

Active playable terrain:
- 1000 x 1000 m
- 513 x 513 grid
- 1.953125 m sample spacing
- 263,169 vertices
- 524,288 triangles
- no missing DGM grid cells

Collision terrain:
- 129 x 129 samples
- 16,641 vertices
- 32,768 triangles

Generator: `tools/blender_pipeline/build_rathaus_dgm_master.py`

## Roads

`SM_Rathaus_ROADS_DGM_v21` is normalized into the same FULLMAP frame and projected onto the DGM.

Validation inside the playable terrain:
- 15,381 road vertices checked
- every vertex is DGM + 0.03 m
- 0 vertices differ by more than 0.05 m
- 2,307 road vertices outside the 1 km terrain are retained as context

## Buildings

`SM_FULLMAP_SurroundingBuildings` contains 1,716 disconnected building components.

Grounding validation:
- 1,643 components inside playable terrain
- all 1,643 grounded to DGM
- 0 components differ by more than 0.05 m
- 73 context components outside the active terrain remain unchanged
- building collision was regenerated from the grounded visual mesh

## Gameplay grounding

Validated at DGM surface + 0.02 m:
- 8 primary spawn points
- 4 spawn-ring markers
- Objective A and Objective B
- 5 pallet covers
- 2 barrier covers
- 5 production crate-shell assemblies

Spawn corrections made for map-boundary safety:
- WEST_3 center clamped to X = -495 m
- EAST_3 center clamped to Y = +495 m

Five obsolete `SM_COVER_CASE_*` template meshes are retained as hidden `reference` objects with `ss_export=false`; the `P_Crate*` production assemblies replace them.

## Rathaus architecture

v23 includes the v16/v17 architecture and gameplay-planning work:
- improved portal arches
- expanded mansard/dormer rhythm
- central pediment/cornice detail
- tower crown/balustrade detail
- planning-only routes, choke candidates, cover zones and sightline-risk markers

Hard QA targets remain:
- 116 m main facade
- 80 m tower
- rectangular massing with three symmetric courtyards
- high mansard roof
- seven-part facade/window-axis articulation
- central gabled risalit

The Rathaus landmark itself still requires further production-detail modelling before UE re-import is approved.

## Reproduction chain

1. Start from tracked `WORLD_MASTER_v17_GAMEPLAY_TAGGED`.
2. Generate DGM with `build_rathaus_dgm_master.py`.
3. Run `build_rathaus_world_master_v21_geoframe.py`.
4. Run `build_rathaus_world_master_v23_grounding_clean.py`.
5. Run QA scripts:
   - `audit_rathaus_road_terrain_alignment.py`
   - `audit_rathaus_v23_grounding_targets.py`
   - `audit_production_bounds.py`
   - `audit_world_master.py`
   - `export_world_master_manifest.py`

v18-v22 experimental/intermediate builds are intentionally excluded from Git and archived locally for recovery only.
