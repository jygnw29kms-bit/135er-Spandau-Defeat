# Rathaus P0: verified baseline, 2026-11-08

Source: `ue5/SpandauStrike/Saved/Logs/v84_ground_smoke_20261107_164233.log` and matching `Saved/Reports/v84_ground_smoke_20261107_164233.json` (local generated evidence; not necessarily Git-tracked).

- Map: `LV_RathausSpandau_REAL_v84_GROUND_LOCK_QA`, 15 bots plus human pawn (16 sampled per interval).
- At t=0.2/5.2/10.2/15.2/20.2 seconds: 5/2/6/6/6 failed ground probes. Total 25 failed of 80 samples; 10 no-hit samples; 5 human samples. **FAIL**.
- Runtime was only 22 seconds. No movement, capsule sweep or respawn PASS was recorded. No valid 60-second acceptance.
- `SourceData/Rathaus/rathaus_dgm1_height_513.r16` is 526338 bytes = 513*513*2, matching a 16-bit heightmap. This verifies dimensions only, not correct landscape XY/Z transform or collision.
- `Saved/Reports/v84_dgm_collision_asset_inspect.json` shows a *static mesh* with complex-as-simple collision and initially double-sided geometry false. `v84_dgm_double_sided_apply.json` reports a later double-sided change, but does not prove runtime blocking. Do not confuse this with an actual Landscape heightfield collision component.

## Next exclusive UE5 integration gate

1. Record current v84 map transform, DGM origin, height scaling and pawn spawn coordinates. Create a **native Landscape actor** from the 513x513 R16 with correct height conversion and XY spacing, without replacing unrelated visuals or overwriting the v84 baseline.
2. Verify Landscape collision component exists and blocks Pawn and Visibility/ground trace channels. Log trace hit actor/component, collision channel, impact Z, pawn capsule bottom Z and gap. Confirm no duplicate terrain or hidden pad masks the result.
3. Run 15 bots plus player through 0/5/15/30/60s, movement and respawn. Require no missing hit, sinking, fall or KillZ; capture actual UE screenshots and exit code. Mark **PASS** only after all checks.

No UE run was executed while preparing this evidence note. Existing untracked work must remain untouched.
