# UE5 Runtime Gameplay Handoff

The Rathaus Blender world master is the authoritative spatial source. `tools/gameplay/build_runtime_gameplay_handoff.py` validates the current gameplay metadata and creates a deterministic UE5-facing package at:

`ue5/SpandauStrike/Design/RathausSpandau/runtime_gameplay_handoff_v51.json`

Validated invariants:
- exactly five linear territorial objectives in sequence 1..5
- Rathaus is objective 3 and requires two simultaneous players
- back-capping is disabled
- exactly eight team spawn anchors split between west/east
- at least twenty runtime cover objects

The generated package contains source-space meters plus centimeters for UE-side placement. Axis/handedness conversion remains the responsibility of the importer; the generator intentionally does not guess an FBX/UE transform convention.

Gameplay tags use only the project-owned `SpandauStrike.*` namespace. The canonical list is stored in `tools/gameplay/spandau_strike_gameplay_tags.json` and covers movement states, weapon deployment/bolt cycling, six class roles, objective states, team spawns, lanes, cover classes and bipod-support surfaces.

Regenerate and validate without opening Unreal:

```powershell
python tools/gameplay/build_runtime_gameplay_handoff.py
```

A non-zero exit means the current world-master metadata violates a runtime invariant and must not be imported as production gameplay.

The generated JSON is a handoff contract, not the final Unreal actor implementation. Runtime actor spawning and axis conversion remain UE5-side responsibilities.
