# Local Resume After Offline Git Work

When `DESKTOP-BNDD1US` comes back online, do **not** run a blind pull or hard reset first. The machine disconnected while local repo-only work may still have uncommitted changes in Unreal config/generated handoff files.

## Safe sequence

From `C:\Users\dezen\Desktop\135er-Spandau-Defeat`:

```powershell
git status --short
git branch --show-current
git remote -v
git fetch origin
git rev-list --left-right --count origin/main...main
git diff -- ue5/SpandauStrike/Config/DefaultGameplayTags.ini
git diff -- ue5/SpandauStrike/Design/RathausSpandau/runtime_gameplay_handoff_v45.json
```

If there are local changes, save a patch before reconciliation:

```powershell
New-Item -ItemType Directory -Force C:\Users\dezen\Documents\SpandauStrike\resume_safety | Out-Null
git diff > C:\Users\dezen\Documents\SpandauStrike\resume_safety\pre_pull_worktree.patch
git diff --cached > C:\Users\dezen\Documents\SpandauStrike\resume_safety\pre_pull_index.patch
```

Then inspect and reconcile the local changes with current `origin/main`. Do not discard `DefaultGameplayTags.ini` changes until compared against the canonical tag list:

`tools/gameplay/spandau_strike_gameplay_tags.json`

Generate the expected Unreal config snippet with:

```powershell
python tools/gameplay/generate_ue_gameplay_tag_snippet.py --out C:\Users\dezen\Documents\SpandauStrike\resume_safety\SpandauStrikeGameplayTags.ini
```

After reconciliation and pull, run:

```powershell
python tools/repo/validate_spandau_scope.py
python tools/gameplay/validate_gameplay_bundle.py
python tools/gameplay/validate_gameplay_config.py
python -m unittest discover -s tools/gameplay/tests -p "test_*.py" -v
python tools/gameplay/build_runtime_gameplay_handoff.py
python tools/gameplay/build_ue_datatable_csv.py
```

Only after those checks pass should Unreal Engine be opened.

## First Unreal check

Run the dry-run validator without changing the map:

`ue5/SpandauStrike/Content/Python/validate_rathaus_runtime_handoff.py`

Expected report:

`Saved/Reports/rathaus_runtime_handoff_validation.json`

The dry run must pass before runtime actors are created or the current Rathaus FINAL map is modified.

## Current authoritative world baseline

- Blender world master: `v45_MAIN_ROOF_RIDGE_ALIGNMENT`
- Gameplay bundle: `SpandauStrike.GameplayBundle.v1`
- Five territorial objectives
- Eight team spawn anchors
- Three primary lanes
- Three crosslinks
- Four main choke groups
- Three MG/sniper power-position groups with mandatory counterplay

The Blender world master remains the authoritative spatial source. Generated JSON/CSV files are handoff/derived data and must not replace Blender as the spatial source of truth.
