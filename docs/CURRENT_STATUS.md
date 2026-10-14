# Current Status - UE5 only

Updated: **2026-10-14**

**135er Spandau Strike uses Unreal Engine 5 / Lyra as its sole engine target. Source/Source2 are no longer part of active production.**

## Rathaus Spandau - active production focus

The Rathaus map is being reset onto the recovered large Blender world master rather than continuing the broken isolated UE test chain.

Authoritative spatial inputs:
- Berlin3D / LoD2 reference data
- Berlin DGM1 elevation data
- aerial/reference imagery
- OSM/verified road and environment data
- manually rebuilt landmark geometry

## Recovered full-map baseline

`SpandauStrike_Rathaus_FULLMAP_v13_UE5_READY.blend` was recovered and audited.

Verified baseline:
- approximately **1.855 km x 4.201 km** scene extent
- approximately **110.2 m** vertical range
- **10,118** total objects
- **10,100** mesh objects
- **364,197** vertices
- **463,378** polygons
- gameplay, collision, environment, urban-detail, street/tram and rebuilt-architecture collections already exist

This is materially more complete than the later isolated Rathaus/GIS UE test levels.

## Rejected as production baseline

The following chain remains available as reference/test data but is not the production world master:
- `REAL_v70` Berlin3D Rathaus mesh
- `LV_RathausSpandau_VISUAL_v77_TEST`
- DOP/DGM v82/v83 test levels
- former `LV_RathausSpandau_REAL_FINAL`

The v83 DGM test surface is only about **358 m x 358 m** and was intentionally built as a local Rathaus test crop. It must not be confused with the full production map.

## Current master workflow

1. Blender world master is the authoritative map/model source.
2. Terrain, roads, buildings, Rathaus, props and gameplay planning stay spatially coherent in Blender.
3. Objects receive semantic roles such as spawn, objective, cover, nav, collision, terrain, road and landmark.
4. Obsolete blockout/reference layers are retained for traceability but excluded from production export.
5. Unreal Engine receives controlled modular export packages.
6. UE5 handles gameplay systems, lighting, final runtime materials, navigation, AI, Nanite/LOD policy, effects and runtime optimization.

Current tracked files:
- `tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v15_OPTIMIZED.blend` - production-cleaned world master
- `tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v15_OPTIMIZED_AUDIT.json`
- `tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v15_OPTIMIZED_EXPORT_MANIFEST.json`
- `docs/RATHAUS_WORLD_MASTER.md`

The v14 recovery checkpoint is archived locally outside Git at `Documents/SpandauStrike/Blender/archive/Rathaus_WORLD_MASTER_recovery_2026-10-14/`.

## v15 verified cleanup

- 8,690 mesh objects safely reassigned to identical shared mesh datablocks
- unique mesh datablocks reduced from 10,100 to 1,410
- all seven Berlin3D image references repaired and packed
- zero missing image references after validation
- all 10,118 scene objects carry semantic/export metadata
- 2,439 blockout objects and two photo-reference objects remain preserved but excluded from production export
- geometry bounds, vertex count and polygon count remain unchanged

## Gameplay metadata already present

Recovered data already contains:
- 12 spawn markers
- Objective A/B
- cover objects/markers
- nav blockers
- terrain and roads
- Rathaus collision
- surrounding-building collision
- water, vegetation and street/tram detail layers

## Immediate production priority

- complete Rathaus landmark geometry to production quality
- classify routes, choke points, cover heights and playable interiors in the Blender master
- keep terrain/roads/buildings aligned to verified spatial data
- build tagged modular UE5 export/import packages
- validate scale, terrain, collision and navigation in UE5
- only then designate a new Rathaus UE level as FINAL
