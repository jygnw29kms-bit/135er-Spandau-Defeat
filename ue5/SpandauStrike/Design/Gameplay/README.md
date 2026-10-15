# Spandau Strike Gameplay Data

This directory contains the engine-facing, data-driven baseline for Spandau Strike gameplay.

## Versioned bundle

`gameplay_bundle_v1.json` is the current compatibility manifest. It pins the authoritative Rathaus world-master version, all gameplay source files, generators, validators and required invariants that belong together.

Current spatial baseline: `v47_CROWN_GUARDRAILS`.

## Source of truth

- `core_gameplay_tuning_v1.json` Ã¢â‚¬â€ movement, stamina, stance, bipod, class-weight and territorial-control baseline values.
- `weapon_archetypes_v1.json` Ã¢â‚¬â€ neutral weapon-role tuning used to seed future Lyra equipment/data assets.
- `class_loadouts_v1.json` Ã¢â‚¬â€ six class roles mapped to project gameplay tags and primary weapon archetypes.
- `rathaus_lane_flow_v1.json` Ã¢â‚¬â€ five objectives, three primary lanes and three crosslinks.
- `rathaus_combat_flow_v1.json` Ã¢â‚¬â€ choke groups, MG/sniper power positions and mandatory counterplay anchors.
- `tools/gameplay/spandau_strike_gameplay_tags.json` Ã¢â‚¬â€ canonical project-owned Gameplay Tag namespace.
- Rathaus Blender world-master metadata Ã¢â‚¬â€ authoritative map-space positions for spawns, objectives and runtime cover.

## Generated / derived data

Generated files are handoff/build products and must never replace the Blender world master or versioned gameplay JSON as source of truth.

- `build_runtime_gameplay_handoff.py` Ã¢â‚¬â€ validates v42 metadata and produces the UE-facing objective/spawn/cover handoff.
- `generate_ue_gameplay_tag_snippet.py` Ã¢â‚¬â€ creates Unreal `GameplayTagList` entries from the canonical tag list.
- `build_ue_datatable_csv.py` Ã¢â‚¬â€ creates CSV seeds for class, weapon-archetype and movement DataTables.
- `build_ue_import_plan.py` Ã¢â‚¬â€ creates the ordered UE import plan and SHA-256 fingerprints all source files.
- `build_map_flow_report.py` Ã¢â‚¬â€ derives flag gaps, lane lengths, crosslink lengths and lane distribution of chokes/power positions.
- `build_balance_report.py` Ã¢â‚¬â€ derives sprint/recovery timing, class traversal metrics and weapon lethality/handling review metrics.

GitHub Actions publishes these products as the `spandau-strike-rathaus-runtime-handoff` artifact.

## Validation

Run without starting Unreal:

```powershell
python tools/repo/validate_spandau_scope.py
python tools/gameplay/validate_gameplay_bundle.py
python tools/gameplay/validate_gameplay_config.py
python -m unittest discover -s tools/gameplay/tests -p "test_*.py" -v
python tools/gameplay/build_runtime_gameplay_handoff.py
python tools/gameplay/build_ue_import_plan.py
python tools/gameplay/build_map_flow_report.py
python tools/gameplay/build_balance_report.py
python tools/gameplay/build_ue_datatable_csv.py
```

GitHub Actions run syntax checks, repository-scope checks, regression tests and all gameplay invariants automatically. A failed invariant blocks promotion of the affected gameplay data to a production UE5 map.

## UE validation policy

The first Unreal step remains a non-mutating dry run through:

`ue5/SpandauStrike/Content/Python/validate_rathaus_runtime_handoff.py`

Only after that succeeds may a **separate Rathaus runtime test map** be created. The current production/final map must not be overwritten during first import validation.

## Offline/local resume

If the development PC was offline while GitHub advanced, follow `docs/LOCAL_RESUME_AFTER_OFFLINE.md` before pulling. Preserve any local Unreal config edits as a patch first and reconcile them with the canonical gameplay-tag source.

## Calibration policy

The values are a production baseline, not final balance. Changes must be driven by controlled playtests and committed as explicit data changes. Do not hide tuning constants inside Blueprint graphs or unrelated C++ classes.

## Naming policy

All project-specific runtime tags use the `SpandauStrike.*` namespace. External inspiration, retired engines and unrelated projects must not appear in active project assets, source naming or metadata.
