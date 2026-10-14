# Spandau Strike Gameplay Data

This directory contains the engine-facing, data-driven baseline for Spandau Strike gameplay.

## Source of truth

- `core_gameplay_tuning_v1.json` — movement, stamina, stance, bipod, class-weight and territorial-control baseline values.
- `weapon_archetypes_v1.json` — neutral weapon-role tuning used to seed future Lyra equipment/data assets.
- `class_loadouts_v1.json` — six class roles mapped to project gameplay tags and primary weapon archetypes.
- `tools/gameplay/spandau_strike_gameplay_tags.json` — canonical project-owned Gameplay Tag namespace.
- Rathaus world-master gameplay metadata — authoritative map-space positions for spawns, objectives and cover.

## Generated / derived data

`tools/gameplay/build_runtime_gameplay_handoff.py` converts the current Rathaus export manifest into an Unreal-facing handoff package. Generated handoff files are derived data and must never become the spatial source of truth.

`tools/gameplay/generate_ue_gameplay_tag_snippet.py` converts the canonical tag list into `GameplayTagList` entries for Unreal config.

## Validation

Run without starting Unreal:

```powershell
python tools/gameplay/validate_gameplay_config.py
python tools/gameplay/build_runtime_gameplay_handoff.py --out runtime_gameplay_handoff_v42.json
python tools/repo/validate_spandau_scope.py
```

GitHub Actions run these validations automatically. A failed invariant blocks promotion of the affected gameplay data to a production UE5 map.

## Calibration policy

The values are a production baseline, not final balance. Changes must be driven by controlled playtests and committed as explicit data changes. Do not hide tuning constants inside Blueprint graphs or unrelated C++ classes.

## Naming policy

All project-specific runtime tags use the `SpandauStrike.*` namespace. External inspiration, retired engines and unrelated projects must not appear in active project assets, source naming or metadata.
