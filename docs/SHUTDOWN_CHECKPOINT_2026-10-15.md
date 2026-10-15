# Shutdown checkpoint 2026-10-15

## Authoritative Git state
- branch: `main`
- baseline before this checkpoint: `452c5d9 Define Playermodel 2030 source pipeline`
- UE target: Unreal Engine 5.8 / Lyra only
- current Blender master: `v51_PEDIMENT_READABILITY`
- current first-play map: `/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY`
- gameplay contract: 5 objectives / 8 spawns / 67 cover

## First-play state
- `B_ShooterGame_Elimination` loads to `OnExperienceLoadComplete`.
- v72 contains 8 LyraPlayerStarts and 8 dedicated hidden `BlockAll` spawn-safety pads.
- spawn-safety validator passes 8/8.
- 45-second runtime test showed no `FellOutOfWorld`, KillZ, WorldBounds, failed-spawn, `Accessed None`, or fatal pawn/controller error.
- reproducible gate: `tools/ue5/run_rathaus_v72_first_play_check.cmd`.
- workflow rule: start UE only for concrete import/build/QA/runtime work, then close it again.

## Playermodel 2030 pipeline
Required production names:
- `PM_135_Operator`
- `PM_135_Scout`
- `PM_Opp_Assault`
- `PM_Opp_Recon`

Source contract and validator are committed under `tools/playermodels/`.
Expected SourceArt path: `ue5/SpandauStrike/SourceArt/Characters/2030/`.
The four production FBX files and `SpandauStrike_Playermodels_2030_Master.blend` are not present in the current repository yet; do not silently substitute placeholders.

## Lucas workstation local prerequisites
The Lucas workstation intentionally keeps local Epic/Lyra base content and plugins outside Git, including `DefaultGameData.uasset`, ShooterCore and related Lyra project content. Generated `Binaries`, `Intermediate`, `DerivedDataCache`, and `Saved` also remain local. These are prerequisites/cache, not project source.

## Resume order
1. Pull `origin/main` on the active workstation.
2. Run `python tools/playermodels/validate_playermodel_source.py` without opening UE.
3. Continue locating/reconstructing the four Playermodel 2030 source assets and validate rig naming before any UE import.
4. Preserve v72 as the stable first-play baseline.
5. For UE checks use the lifecycle gate so UE closes after the test.
6. Continue Rathaus modelling in a new revision only after the first-play baseline remains green.

## Preservation rules
- Do not overwrite v65/v67/v69/v70/v71/v72 checkpoints.
- Do not commit local restored Epic/Lyra base content blindly.
- Do not commit `DerivedDataCache`, `Intermediate`, `Saved`, or generated binaries.
- Use Git LFS for `.blend`, `.fbx`, `.uasset`, and `.umap` assets already covered by repository attributes.
