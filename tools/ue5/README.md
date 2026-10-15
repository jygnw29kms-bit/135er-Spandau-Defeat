# UE5 Rathaus workflow

The default rule is: keep Unreal Engine closed unless a concrete import, build, shader, QA, or runtime step requires it.

## Automated v72 first-play gate

Run `run_rathaus_v72_first_play_check.cmd` from `tools/ue5`.

The gate:
1. refuses to run if an UnrealEditor process is already open;
2. runs the checked-in v72 spawn-safety validator headlessly;
3. starts only the v72 Lyra Shooter Elimination runtime;
4. waits for the requested runtime window (45 seconds by default);
5. requires map load + experience identification + experience load completion;
6. rejects fall-through, KillZ/world-bounds, spawn, Accessed None and fatal patterns;
7. closes only the Unreal process it started;
8. writes `ue5/SpandauStrike/Saved/Reports/v72_firstplay_workflow.json`.

Use `run_rathaus_v72_first_play_check.cmd -RuntimeSeconds 60` for a longer gate.

## Interactive first play

`launch_rathaus_v72_first_play.ps1` remains the interactive launcher. On machines with restrictive PowerShell execution policy, invoke it through `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ...`; do not change the system policy globally.
