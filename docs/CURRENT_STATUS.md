# Current Status - UE5 only

Updated: **2026-10-14**

**135er Spandau Strike uses Unreal Engine 5 / Lyra as its sole engine target.**

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
- `tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v32_TOWER_ACCURACY.blend` - current production world master
- `tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v32_TOWER_ACCURACY_AUDIT.json`
- `tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v32_TOWER_ACCURACY_EXPORT_MANIFEST.json`
- `docs/RATHAUS_WORLD_MASTER.md`

Intermediate v24-v31 Blender builds are archived locally outside Git under `Documents/SpandauStrike/local_repo_archive_2026-10-14/worldmaster_v24-v31_diagnostics/`.

## v32 verified production cleanup and rebuild

- legacy Rathaus detail generations are preserved as reference but excluded from production export
- 3,955 obsolete/overlapping Rathaus-detail objects were retired from export in the production-clean pass
- clean architecture layers now use the verified 47.5-degree geoframe
- the front facade uses a new instanced 5 m horizontal / 4.2 m vertical window rhythm
- 76 facade window instances share one window mesh
- central risalit uses five window axes and a broad round pediment matching Rathaus Spandau reference proportions
- tower now has four clock faces, four levels of small shaft windows, corner articulation, an open upper stage and a low green copper roof
- old `P_CopperCap*` geometry is reference-only
- QA renderer explicitly excludes collision/nav/gameplay helper meshes, avoiding false visual blockers

## v32 technical QA

- 10,538 total scene objects / 10,502 mesh objects
- 657,077 vertices / 1,028,835 polygons across the full master scene
- 2,997 meshes currently marked for production export
- full world bounds remain approximately 1.855 km x 4.201 km
- road mesh: 15,381 sampled vertices inside DGM; median road offset +0.03 m; zero points above 0.05 m mismatch
- building grounding: maximum terrain error below 0.000001 m for in-terrain samples
- zero missing material assignments in the world audit

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

- continue Rathaus facade sculpt/detail pass: stone reliefs, portal, pediment crest/inscription zone and side elevations
- complete tower architectural detailing while preserving the verified v32 silhouette
- classify routes, choke points, cover heights and playable interiors in the Blender world master
- keep terrain/roads/buildings aligned to verified spatial data
- produce a tagged modular UE5 handoff only after the Blender landmark and immediate Rathaus environment pass are visually approved
- only then designate a new Rathaus UE level as FINAL
