# Active production focus - UE5 only

Updated: 2026-10-12

Current production target: **Rathaus Spandau in Unreal Engine 5 only**.

Primary project: `C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SpandauStrike.uproject`
Primary map: `/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL`


## Current Rathaus FINAL state
- Lyra runtime test works with `B_ShooterGame_Elimination`; local player receives a real Shooter pawn.
- PlayerStart rotations corrected to normal FPS orientation.
- Previous v73 terrain collision proxy had a Y-axis mirror error.
- Corrected collision geometry is v75 (Y mirrored + triangle winding corrected).
- FINAL uses v75 collision proxy; starts were placed 120 cm above measured collision surface.
- Recast was rebuilt after the collision/spawn correction and MapCheck returned 0 errors / 0 warnings at that checkpoint.
- DOP2025 aerial texture itself is valid. The current remaining visual issue is the visible DGM/UV/import path; v76 material wiring is under validation and must not be treated as final visual quality yet.

## Binding map build rule
1. Real geodata first: Berlin3D/LoD2, DGM1, roads and DOP aerial data.
2. Derive clean UE5 gameplay geometry from those sources; do not invent final architecture.
3. Gameplay layer after geometry: spawns, objectives, cover, sightlines, collision and nav.
4. Visual/detail pass only after runtime collision and walkability are stable.
5. Rathaus Spandau stays the active map until runtime, gameplay and visual QA are passed.

Real geometry and verified engine output take priority over concept/placeholder material.