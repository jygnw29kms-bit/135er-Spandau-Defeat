# Rathaus architecture recovery review

## Current decision

`SpandauStrike_Rathaus_WORLD_MASTER_v46_RETIRE_LEGACY_TOWER_ROOF.blend` is the current production world master. The recovered `RathausSpandau_REAL_Integrated_Master_v4.blend` remains reference/recovery material only and must not be wholesale-merged.

The original audit showed that the production chain contains substantially richer Rathaus geometry than v4. The later v42-v46 inspection confirmed that several elements initially suspected to be missing were already present in newer `V37_*` / `SM_MASTER_*` geometry.

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

v44 therefore recessed the four shadow/backplates 1.35 m toward the tower center. No mesh topology, materials, stone piers, copper roof, clock geometry, collision or gameplay objects changed.

## v45 main-roof ridge correction

Reference-driven front-elevation review against the current Rathaus photograph exposed a separate silhouette error in `SM_MainRoof`: its footprint is approximately 112 x 54 m, but the two existing ridge vertices ran along the 54 m transverse axis. This made the roof rise as a large triangular wedge toward the tower when viewed from the main facade.

v45 moves only those two existing ridge vertices to the midpoints of the short roof-end edges, aligning the ridge with the 112 m longitudinal/facade axis. The ridge height remains 29.5 m. No vertices or polygons are added or removed, and no facade, tower, material, collision or gameplay objects are changed.

The v44, v45 and v46 topology remains identical:

- 10,788 total objects
- 10,749 mesh objects
- 719,877 vertices
- 1,085,713 polygons
- identical world bounds and material count; v46 changes exactly one role assignment from landmark to reference

The v45 handoff remains 5 objectives / 8 spawns / 67 cover objects; objective, spawn and cover transforms are identical to v44.

## v46 legacy tower-roof retirement

A tower-only QA render exposed two copper roof meshes stacked on the same XY center: the authoritative `V37_CopperOctagonalRoof` and the older `V33_CopperOctagonalRoof`. Their XY centers are exactly coincident, both are 2.25 m high, and the V33 roof sits 1.20 m above the V37 roof. This produced a visibly doubled/stepped tower cap.

The surrounding superseded V33 crown geometry was already correctly marked `reference`, `ss_export=False` and hidden with `replaced_v37_tower_transition` tags. v46 applies that same non-destructive retirement policy to `V33_CopperOctagonalRoof`: it remains preserved in the Blend as hidden reference geometry, while `V37_CopperOctagonalRoof` remains the only exported production roof. No mesh topology, transforms, materials, gameplay or collision geometry changed.

The v46 role counts therefore change by exactly one object: landmark 414 -> 413 and reference 5176 -> 5177. All total object/mesh/vertex/polygon counts and world bounds remain unchanged. The runtime handoff remains exactly 5 objectives / 8 spawns / 67 cover objects, with gameplay transforms identical to v45.

## Remaining Rathaus review work

The central facade now has a correctly oriented main-roof silhouette. Further work should focus on reference-driven proportion/material/fenestration QA and later UE5 presentation quality rather than importing old v4 geometry merely because object names differ. Any new recovery or architecture change requires a proven spatial/reference match and must preserve the current gameplay/runtime invariants.
