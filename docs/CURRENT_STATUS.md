# Current Status - UE5 only

Updated: **2026-10-15**

**135er Spandau Strike uses Unreal Engine 5.8 / Lyra as its sole engine target.**

## Rathaus Spandau - active production focus

The recovered large Blender world master remains the authoritative spatial source. Unreal receives controlled runtime handoffs and playable map revisions; the old isolated GIS/test chain is reference-only.

Authoritative spatial inputs include Berlin3D / LoD2, Berlin DGM1, aerial/reference imagery, verified OSM/road data and manually rebuilt landmark geometry.

## Current Blender production master

Current authoritative master:

`tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v51_PEDIMENT_READABILITY.blend`

v51 keeps the validated v50 tower/crown/clock work and improves only existing V34 central-pediment details: the two inscription meshes are 1.50x taller and the shield is 1.15x larger in its facade plane. The round pediment, medallion, facade structure, topology, world bounds and all gameplay/collision geometry remain unchanged.

Verified v51 full-master metrics:
- **10,792** total objects
- **10,753** mesh objects
- **720,101** vertices
- **1,085,881** polygons
- **155** materials
- world bounds unchanged from v46
- gameplay core unchanged from v46

Tracked QA / handoff files:
- `SpandauStrike_Rathaus_WORLD_MASTER_v51_PEDIMENT_READABILITY_AUDIT.json`
- `SpandauStrike_Rathaus_WORLD_MASTER_v51_PEDIMENT_READABILITY_EXPORT_MANIFEST.json`
- `SpandauStrike_Rathaus_WORLD_MASTER_v51_PEDIMENT_READABILITY_REPORT.json`
- `ue5/SpandauStrike/Design/RathausSpandau/runtime_gameplay_handoff_v51.json`

## Current gameplay contract

The current runtime gameplay handoff contains:
- **5 objectives**
- **8 team spawn anchors**
- **67 cover objects**
- 3 primary lanes
- 3 crosslinks
- 4 choke groups
- 3 power-position groups
- Rathaus objective requires 2 simultaneous players
- back-capping disabled

All current gameplay tags use the `SpandauStrike.*` namespace.

## Current UE5 playable baseline

Current architecture/runtime validation map:

`/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY`

v65 remains the known-good spawn/runtime fallback. v67 is the validated lighting checkpoint, v68 the v49 geometry checkpoint, v69 the reference-facing material checkpoint, v70 the v50 clock-scale checkpoint, v71 carries the v51 pediment-readability correction, and v72 is the first-play checkpoint with Lyra Shooter Elimination plus dedicated spawn-ground safety pads.

v65 was created from v64 specifically to replace the two temporary generic PlayerStarts with the **8 LyraPlayerStart locations from the v47 runtime handoff** (v65 remains the known-good playable checkpoint; v48 gameplay transforms are machine-verified identical).

Runtime validation on the Lucas workstation (UE 5.8.3):
- map loads successfully in Development runtime
- world reaches play state successfully
- 8/8 LyraPlayerStarts are present
- previous `B_AI_Controller_LyraShooter` / `Accessed None` pawn errors no longer occur
- 45-second unattended runtime test completed without fatal errors or spawn failures
- only engine-start automation-test diagnostics remain; these are not the previous Rathaus AI failure path


### v66 architecture handoff

The v48 Blender production building is exported reproducibly through `tools/blender_pipeline/export_rathaus_building_v48_ue5.py` to:

`ue5/SpandauStrike/SourceArt/Rathaus/v48/RathausSpandau_BUILDING_v48.fbx`

The export contains 583 selected Rathaus architecture objects joined into one UE handoff mesh: 65,238 vertices / 59,646 polygons / 34 material slots. Plaza benches, lamps, crates and the statue are deliberately excluded from the building mesh.

UE asset:

`/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v48/SM_RathausSpandau_BUILDING_v48`

A small reference-driven material set under `/Game/SpandauStrike/Maps/Rathaus/Materials/v48` replaces the old WorldGrid-only appearance with sandstone/trim, red roof tile, dark glass/window frame, gold clock details, copper, dark metal, concrete and dark openings.

v66 runtime validation on Lucas (UE 5.8.3):
- map reaches play state successfully
- 8 PlayerStarts preserved
- DGM/DOP and roads actors unchanged
- only `Rathaus_BUILDING_v32` is replaced by `Rathaus_BUILDING_v48`
- building transform remains world origin / identity / scale 1
- no `Accessed None`, AI-controller, spawn, or fatal runtime errors
- the only recurring error-level startup lines are the same 17 engine automation-test diagnostics already present in v65
### v67 reference-facing lighting

v67 duplicates v66 without changing the building, DGM/DOP, roads, spawns, objectives or cover. It updates only the technical lighting used by the Rathaus validation map:
- `TECH_Sun_v64`: rotation pitch `-35`, yaw `-137.5`, intensity `4.0`
- `TECH_Sky_v64`: intensity `2.3`
- 8 LyraPlayerStarts preserved

The values were selected through fixed-camera A/B QA against `media/theme/rathaus-spandau-photo.jpg`. They remove the false near-black mansard/facade appearance seen in v66 while preserving readable architectural shadow depth. A 30-second unattended Development runtime test completed with `REAL_BAD_COUNT=0` and the v67 world reached play state successfully.

Reproducible scripts:
- `ue5/SpandauStrike/Content/Python/build_rathaus_v67_lighting.py`
- `ue5/SpandauStrike/Content/Python/qa_v67_front_screenshot.py`

### v68 v49 architecture handoff

v68 duplicates v67 and replaces only `Rathaus_BUILDING_v48` with the v49 building handoff. The v49 FBX remains 583 selected architecture objects / 65,238 vertices / 59,646 polygons / 34 material slots, with the five crown proportion transforms baked into the exported building. Existing v48 material assignments are copied slot-for-slot onto the v49 mesh.

Lucas UE 5.8.3 validation:
- 8/8 PlayerStarts preserved
- building transform remains world origin / identity / scale 1
- v67 sun/skylight values preserved
- real Development runtime world reaches play state successfully
- `REAL_BAD_COUNT=0` for fatal, AI-controller, `Accessed None`, and PlayerStart failure patterns
- fixed-camera GPU QA confirms the narrower v49 crown/roof silhouette while the main roof, dormers, facade and lighting remain unchanged

Reproducible sources/scripts:
- `tools/blender_pipeline/export_rathaus_building_v49_ue5.py`
- `ue5/SpandauStrike/SourceArt/Rathaus/v49/RathausSpandau_BUILDING_v49.fbx`
- `ue5/SpandauStrike/Content/Python/import_rathaus_v49_validation.py`
- `ue5/SpandauStrike/Content/Python/apply_rathaus_v49_materials.py`
- `ue5/SpandauStrike/Content/Python/build_rathaus_v68_v49_architecture.py`
- `ue5/SpandauStrike/Content/Python/qa_v68_front_screenshot.py`

### v69 reference-facing material palette

v69 duplicates v68 and swaps only the Rathaus building mesh to an identical v49 geometry copy with a dedicated material set. The palette uses darker/rougher warm sandstone, less-white trim, a deeper terracotta roof, darker glazing/window frames, subdued copper and dark metal. Geometry, transforms, lighting, DGM/DOP, roads and all 8 PlayerStarts remain unchanged.

Lucas UE 5.8.3 validation:
- fixed-camera GPU QA completed successfully
- real Development runtime reaches play state
- `REAL_BAD_COUNT=0`
- v68 remains the geometry checkpoint; v69 is the current visual/runtime validation map

Reproducible scripts:
- `ue5/SpandauStrike/Content/Python/build_rathaus_v49_reference_materials.py`
- `ue5/SpandauStrike/Content/Python/build_rathaus_v69_reference_materials.py`
- `ue5/SpandauStrike/Content/Python/qa_v69_front_screenshot.py`

### v70 v50 clock-scale handoff

v70 duplicates v69 and replaces only the Rathaus building mesh with the v50 handoff. v50 scales the existing open radial V33 clock boss, 12 markers and two hands on each of the four tower faces by 1.45 around the existing face center. The real Rathaus reference uses an open radial clock, so no circular face or ring is promoted. Geometry outside those 60 clock-detail meshes is unchanged.

Lucas UE 5.8.3 validation:
- 8/8 PlayerStarts preserved by the build gate
- fixed-camera GPU QA confirms a substantially more reference-faithful clock-to-tower proportion
- real Development runtime reaches play state
- `REAL_BAD_COUNT=0`
- v69 remains the material fallback; v70 is the current visual/runtime validation map

Reproducible sources/scripts:
- `tools/blender_pipeline/build_world_master_v50_clock_scale.py`
- `tools/blender_pipeline/export_rathaus_building_v50_ue5.py`
- `ue5/SpandauStrike/SourceArt/Rathaus/v50/RathausSpandau_BUILDING_v50.fbx`
- `ue5/SpandauStrike/Content/Python/import_rathaus_v50_validation.py`
- `ue5/SpandauStrike/Content/Python/apply_rathaus_v50_reference_materials.py`
- `ue5/SpandauStrike/Content/Python/build_rathaus_v70_clock_qa.py`
- `ue5/SpandauStrike/Content/Python/qa_v70_front_screenshot.py`

### v71 v51 pediment-readability handoff

v71 duplicates v70 and replaces only the Rathaus building mesh with the v51 handoff. v51 changes exactly three existing exported V34 pediment-detail meshes: both inscription blocks are scaled 1.50x in world vertical and the central shield 1.15x in its facade plane. Their positions, depth, materials and the round pediment/medallion remain unchanged. No new geometry is introduced.

Lucas UE 5.8.3 validation:
- 8/8 PlayerStarts preserved by the build gate
- fixed-camera A/B GPU QA shows substantially clearer facade inscription and slightly stronger shield presence without changing the pediment silhouette
- real Development runtime reaches play state
- `REAL_BAD_COUNT=0`
- v70 remains the clock-scale fallback; v71 is the current visual/runtime validation map

Reproducible sources/scripts:
- `tools/blender_pipeline/build_world_master_v51_pediment_readability.py`
- `tools/blender_pipeline/export_rathaus_building_v51_ue5.py`
- `ue5/SpandauStrike/SourceArt/Rathaus/v51/RathausSpandau_BUILDING_v51.fbx`
- `ue5/SpandauStrike/Content/Python/import_rathaus_v51_validation.py`
- `ue5/SpandauStrike/Content/Python/apply_rathaus_v51_reference_materials.py`
- `ue5/SpandauStrike/Content/Python/build_rathaus_v71_pediment_qa.py`
- `ue5/SpandauStrike/Content/Python/qa_v71_front_screenshot.py`
### v72 first-play checkpoint

v72 duplicates v71 without changing Rathaus architecture, lighting, materials, objectives, cover, roads or DGM/DOP. It is the first dedicated Lyra gameplay-start revision and is launched with `B_ShooterGame_Elimination`.

Spawn safety is explicit: each of the 8 LyraPlayerStarts has a hidden 6 x 6 m, 20 cm thick `BlockAll` safety pad centered on the same XY location. The pad center is 100 cm below the PlayerStart origin, putting its top surface about 90 cm below the spawn origin for the Lyra character capsule. This prevents a first-play pawn from falling through even where current terrain/DGM collision is incomplete.

Lucas UE 5.8.3 validation:
- 8/8 PlayerStarts and 8/8 spawn safety pads validated
- all pads have identical spawn XY, `BlockAll`, scale `6,6,0.2`, and `StartZ - PadZ = 100 cm`
- `B_ShooterGame_Elimination` is identified and reaches `OnExperienceLoadComplete`
- 45-second Development runtime reaches play state
- no `FellOutOfWorld`, KillZ, world-bounds, failed-spawn, `Accessed None` or fatal pawn/controller error found

Reproducible scripts:
- `ue5/SpandauStrike/Content/Python/build_rathaus_v72_first_play.py`
- `ue5/SpandauStrike/Content/Python/validate_rathaus_v72_spawn_safety.py`
- `tools/ue5/launch_rathaus_v72_first_play.ps1`
## UE workstation prerequisites recovered

The Lucas workstation now has the required local UE 5.8 / Lyra runtime prerequisites restored:
- UE 5.8 installed on C:
- Visual C++ build tools / Windows SDK / .NET Framework SDK available
- Lyra project plugins restored locally
- Lyra base content restored locally, including `DefaultGameData.uasset`
- LyraGame / LyraEditor and project plugin binaries compile successfully

These large Epic/Lyra base assets are local prerequisites and are intentionally not included in the Spandau project commit created for v65.

## Rejected as production baseline

The following remain reference/test data only:
- `REAL_v70` Berlin3D Rathaus mesh
- `LV_RathausSpandau_VISUAL_v77_TEST`
- DOP/DGM v82/v83 test levels
- former `LV_RathausSpandau_REAL_FINAL`

The v83 DGM surface is only a local Rathaus crop and must not be confused with the full production world.

## Current master workflow

1. Blender world master is the authoritative geometry/spatial source.
2. Terrain, roads, buildings, Rathaus and gameplay planning remain spatially coherent there.
3. Obsolete/reference layers stay traceable but are excluded from production export.
4. UE5 receives controlled modular handoffs.
5. UE5 owns runtime gameplay, lighting, materials, navigation, AI, Nanite/LOD, effects and optimization.
6. Runtime changes are validated in a new playable revision before any map is promoted as FINAL.

## Immediate production priority

- continue reference-driven Rathaus facade/window/material QA without speculative geometry changes
- continue reference-driven Rathaus architecture/material QA from the validated v51 geometry while preserving UE v72 as the first-play baseline
- keep v65 as the known-good spawn/runtime fallback; v67 remains the lighting checkpoint, v69 the material fallback, v70 the clock-scale checkpoint, and v72 is the current first-play validation map
- preserve the 5 objectives / 8 spawns / 67 cover gameplay contract
- compare editor and runtime presentation for material, lighting, LOD/Nanite and streaming differences
- promote a new FINAL level only after editor and runtime views match the validated Rathaus reference closely enough
