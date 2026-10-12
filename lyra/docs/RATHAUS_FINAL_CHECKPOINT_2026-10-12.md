# Rathaus FINAL checkpoint - 2026-10-12

## Saved working checkpoint
Local checkpoint folder:
`C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Backups\Rathaus_FINAL_checkpoint_2026-10-12_2055`

Contains 95 files (~13.14 MB) from the current Rathaus workset plus project/config snapshot and `SHA256_MANIFEST.csv`.

## Verified today
- Spectator-only behavior isolated to the Control Points experience; Elimination/TDM produces a real local Shooter pawn.
- Spawn rotations fixed: start 1 = 0/0/0, start 2 = pitch 0 / yaw 180 / roll 0.
- v73 proxy collision had the wrong Y orientation.
- v75 proxy fixes the mirror and winding issue.
- Measured v75 collision near test spawns: approximately -85.20 cm and -148.01 cm Z.
- PlayerStarts reset to measured collision +120 cm.
- Recast rebuilt and FINAL saved; MapCheck was 0 errors / 0 warnings at the stable collision checkpoint.
- DOP2025 texture export verified visually as the correct Rathaus Spandau aerial imagery.
- Visible DGM has one UV channel (UV0). Current DGM import source is the historical FBX pipeline; visible terrain/material alignment remains the next production task.

## Next production task
Rebuild/repair the visible DGM import and UV orientation so the DOP2025 image aligns with the corrected v75 collision, then rebuild navmesh and repeat the live TDM runtime test.