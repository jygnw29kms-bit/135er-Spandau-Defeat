# Rathaus acceptance candidate – 2026-11-01

## Status

Source changes prepared from `1ec8b5cac00faeb07b1f20511f0f9a1363411100`.
This candidate is **not UE-built or ingame accepted**. Lucas was reported offline during preparation. Unreal builds, runtime probes and rendered playtests remain exclusively on Lucas.

## Changes

- Ticket exhaustion now finishes Capture with a defender victory; the final sector uses the same terminal-state path for an attacker victory.
- A finished Capture match owns restart requests until reset/reload. Failed safe respawns retain their queued-death identity, retry through the wave and consume a ticket only after a successful spawn.
- Front-spawn rejection considers only the eight legacy untagged base starts next. Base starts pass the same safety checks; no Blueprint or random fallback reopens another role-tagged front. Team-appropriate base placement still needs the live check below. If no safe start exists, the spawn is deferred.
- MapCheck, normal runtime, combat collectors, round probe, launcher and CSV capture share `tools/ue5/rathaus_validation_target.json`. The candidate map is `/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA`.
- The finalization workflow builds before UE gates, checks the source revision again at the end and cannot report green after skipped build/matrix phases.
- CSV analysis fails for a missing ready event, invalid timing or an incomplete measurement. Incomplete measurements retain their JSON/Markdown report.
- The 12,000-frame CSV capture gets a 900-second timeout; the old 180-second timeout expired before completion at a 60-FPS cap.
- Distance samples require a successful fresh runner result, the requested map and the requested distance. Stale reports are removed before each sample.
- The three previously failing scope references were rewritten without weakening the scope validator.

## Portable validation completed

- 9 existing gameplay regression tests passed.
- 18 new runner/CSV/provenance regression tests passed.
- Gameplay bundle, runtime combat configuration and repository scope validators passed on the fetched source subset.
- Changed Python tools compiled; Node syntax check and `git diff --check` passed.

The repository CI must still verify the complete tree. These results provide no C++ compilation, nav-arrival, rendered performance or multiplayer evidence.

## Required Lucas validation

Reconcile the working tree without discarding local changes; use the existing workstation activity guards. Run the candidate branch from Lucas' existing project checkout:

```powershell
python tools/ue5/rathaus_finalization_workflow.py
```

The workflow performs the build before MapCheck, normal runtime, distance matrix, controlled sector-round probe and the new ticket-end probe. `--skip-build` and `--skip-matrix` are diagnostic modes and deliberately return a partial result.

The new ticket probe can also run separately after the build:

```powershell
python tools/ue5/run_rathaus_v75_front_spawn_headless_check.py --runtime-seconds 60 --ticket-exhaustion-probe
```

It starts with one attacker ticket, waits for Playing, uses a real attacker bot death and wave respawn, then requires exactly one defender-victory terminal event and no later respawn-completed event throughout the observation window. Its report is `Saved/Reports/rathaus_ticket_exhaustion_probe.json`.

## Interactive gates still open

1. Exercise both roles in all four sectors; block the front starts and then every base start. Confirm safe fallback/deferred retry, occupancy, team placement and ticket accounting.
2. Prove actual objective arrivals and recovery from blocked paths. Accepted `MoveToLocation` requests are not arrival evidence.
3. Play a full normal Capture round without probe flags, including contest, decay, combat handoff, normal transition times and both win conditions. Verify the reset/reload into the next match; the dedicated Capture Experience remains separate pending work.
4. Repeat at least three rendered rounds; inspect collision, visibility, input, HUD and runtime errors. Capture complete post-ready frame-time windows on the same map and source revision. Record hardware/settings and evaluate against an explicit performance budget.
5. Save genuine ingame captures with the map/build identity and finish interactive visual QA. Network/multiplayer load acceptance remains separate.

Only after these gates may this candidate be promoted as final playable.
