# Current Status - UE5 only

Updated: **2026-10-15**

**135er Spandau Strike uses Unreal Engine 5.8 / Lyra as its sole engine target.**

## Rathaus Spandau - active production focus

The recovered large Blender world master remains the authoritative spatial source. Unreal receives controlled runtime handoffs and playable map revisions; the old isolated GIS/test chain is reference-only.

Authoritative spatial inputs include Berlin3D / LoD2, Berlin DGM1, aerial/reference imagery, verified OSM/road data and manually rebuilt landmark geometry.

## Current Blender production master

Current authoritative master:

`tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v47_CROWN_GUARDRAILS.blend`

v47 is an additive architectural refinement of the validated Rathaus tower crown. It adds the low metal guardrail visible in the real Rathaus reference imagery while preserving the previous world and gameplay transforms.

Verified v47 full-master metrics:
- **10,792** total objects
- **10,753** mesh objects
- **720,101** vertices
- **1,085,881** polygons
- **155** materials
- world bounds unchanged from v46
- gameplay core unchanged from v46

Tracked QA / handoff files:
- `SpandauStrike_Rathaus_WORLD_MASTER_v47_CROWN_GUARDRAILS_AUDIT.json`
- `SpandauStrike_Rathaus_WORLD_MASTER_v47_CROWN_GUARDRAILS_EXPORT_MANIFEST.json`
- `SpandauStrike_Rathaus_WORLD_MASTER_v47_CROWN_GUARDRAILS_REPORT.json`
- `ue5/SpandauStrike/Design/RathausSpandau/runtime_gameplay_handoff_v47.json`

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

Current validated playable map:

`/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v65_PLAYABLE`

v65 was created from v64 specifically to replace the two temporary generic PlayerStarts with the **8 LyraPlayerStart locations from the v47 runtime handoff**.

Runtime validation on the Lucas workstation (UE 5.8.3):
- map loads successfully in Development runtime
- world reaches play state successfully
- 8/8 LyraPlayerStarts are present
- previous `B_AI_Controller_LyraShooter` / `Accessed None` pawn errors no longer occur
- 45-second unattended runtime test completed without fatal errors or spawn failures
- only engine-start automation-test diagnostics remain; these are not the previous Rathaus AI failure path

Git checkpoint:

`b118ae3 Add Rathaus playable v65 with runtime spawn layout`

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
- carry validated v47 architectural improvements into the next UE handoff
- keep v65 as the known-good playable/runtime baseline while testing later revisions
- preserve the 5 objectives / 8 spawns / 67 cover gameplay contract
- compare editor and runtime presentation for material, lighting, LOD/Nanite and streaming differences
- promote a new FINAL level only after editor and runtime views match the validated Rathaus reference closely enough