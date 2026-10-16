# Local Resume / Lucas Workstation

Spandau Strike is worked on **only on Lucas' workstation `DESKTOP-SMN4ATU`**.
The BnD/Jens PC is not a Spandau Strike work machine and must not be used for Blender, Unreal, builds, screenshots or Git working changes.

## Authoritative local path

`C:\Users\anony\Documents\SpandauStrike\repo`

## Toolchain

- Git: `C:\Program Files\Git\cmd\git.exe`
- Blender production binary: `C:\Users\anony\Apps\blender-4.5.10-windows-x64\blender.exe`
- Unreal Engine: `C:\Program Files\Epic Games\UE_5.8`
- Unreal project: `ue5\SpandauStrike\SpandauStrike.uproject`
- Fusion is not part of the Spandau Strike workflow.

The Blender 4.5.10 LTS binary remains the production Blender version for the existing Rathaus pipeline. Do not silently switch the production master to another Blender major/minor version.

## Safe resume sequence

From `C:\Users\anony\Documents\SpandauStrike\repo`:

```powershell
git status --short
git branch --show-current
git remote -v
git fetch origin
git rev-list --left-right --count origin/main...main
```

If there are intentional local tracked changes, save a patch before reconciliation:

```powershell
$backup = Join-Path $env:USERPROFILE 'Documents\SpandauStrike\resume_safety'
New-Item -ItemType Directory -Force $backup | Out-Null
git diff > (Join-Path $backup 'pre_pull_worktree.patch')
git diff --cached > (Join-Path $backup 'pre_pull_index.patch')
```

Then reconcile against `origin/main`; do not discard intentional source changes.

## Lightweight validation before Unreal

```powershell
python tools/repo/validate_spandau_scope.py
python tools/gameplay/validate_gameplay_bundle.py
python tools/gameplay/validate_gameplay_config.py
python -m unittest discover -s tools/gameplay/tests -p "test_*.py" -v
```

Before Blender rendering, bulk export, shader compilation or Unreal runtime work, run the workstation activity guards in `tools/workstation/`. Heavy work must not start while Lucas is actively using the PC or a game is consuming the machine.

## Current authoritative baseline

- Blender world master: `tools/blender_pipeline/builds/rathaus_spandau/SpandauStrike_Rathaus_WORLD_MASTER_v51_PEDIMENT_READABILITY.blend`
- UE5 first-play map: `/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY`
- Gameplay bundle: `SpandauStrike.GameplayBundle.v1`
- Five territorial objectives
- Eight team spawn anchors
- Three primary lanes
- Three crosslinks
- Four main choke groups
- Three MG/sniper power-position groups with mandatory counterplay

The Blender world master remains the authoritative spatial source. UE5 owns runtime gameplay, materials, lighting, navigation and engine integration.
