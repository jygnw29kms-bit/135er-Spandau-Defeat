# Rathaus architecture recovery review

## Current decision

`SpandauStrike_Rathaus_WORLD_MASTER_v44_CROWN_OPENING_DEPTH.blend` is the current production world master. The recovered `RathausSpandau_REAL_Integrated_Master_v4.blend` remains reference/recovery material only and must not be wholesale-merged.

The original audit already showed that the production chain contains substantially richer Rathaus geometry than v4. The later v42-v44 inspection confirmed that several elements initially suspected to be missing were already present in newer `V37_*` / `SM_MASTER_*` geometry.

## What was actually recovered from v4

Only the entrance stair run `Step_0` through `Step_5` was worth recovering. The three v4 portals map to the production doors with an effectively exact translation:

`[-5.1978047689, +4.7629114787, +0.1000001431] m`

Residual RMS is about `0.0000013 m`. These six steps were therefore added safely in v43 without changing existing geometry. Gameplay remained 5 objectives / 8 spawns / 67 runtime-cover objects.

## Rejected v4 recovery candidates

The following v4 elements are no longer merge candidates:

- **Tower crown/cupola/finial:** rejected. The current master already contains the postwar/current tower termination as `V37_CrownBase`, four `V37_CrownCorner_*`, four `V37_CrownOpening*`, `V37_CrownTopBand` and `V37_CopperOctagonalRoof`. The old v4 cupola/crown is not the production target and its clock-frame alignment was also too weak (~3.57 m RMS).
- **Rathausplatz/plaza:** no v4 merge. Current production geometry already contains plaza/set-dressing including `SM_MASTER_PlazaWet`.
- **Statue/plinth:** no v4 merge. Current production geometry already contains `SM_MASTER_StatuePlinth`, `SM_MASTER_StatueBase`, `SM_MASTER_StatueBody` and `SM_MASTER_StatueHead`.
- **Doors/portals, risalit, facade bands, pilasters, windows, plinth, tram and shelter detail:** current production geometry is already richer than v4.

`SM_Finial` at the historical/experimental tower top remains `reference` with `ss_export=False` and must not be promoted blindly.

## v44 crown refinement

Visual review showed that the four existing `V37_CrownOpening*` objects were only 0.16 m thick and sat flush in the lantern openings. This made the open lantern read like four flat dark panels.

v44 therefore performs a transform-only refinement: the four shadow/backplates are recessed 1.35 m toward the tower center. No mesh topology, materials, stone piers, copper roof, clock geometry, collision or gameplay objects are changed.

The v43 and v44 topology is identical:

- 10,788 total objects
- 10,749 mesh objects
- 719,877 vertices
- 1,085,713 polygons
- identical world bounds and material count

The result was visually reviewed in Blender and validated by the real UE5.8 project dry-run with 5 objectives / 8 spawns / 67 cover objects and no map-actor modifications.

## Remaining Rathaus review work

The central gable and facade silhouette still need reference-driven visual review, but no additional v4 geometry should be merged merely because its object name appears unique. New recovery/import work requires a proven spatial match and must preserve the current gameplay/runtime invariants.
