# Blender master pipeline

Shared geometry and terrain preparation for **135er Spandau Strike**.

## Purpose

Blender is the neutral master layer between Berlin geodata and the two active engine targets:

- Unreal Engine 5.8 / Lyra
- Counter-Strike 2 / Source 2

The master pipeline prevents the same Berlin terrain and base geometry from being rebuilt independently in both engines.

## Current Falkenhagener Feld input

The 1.8 km × 1.8 km production extent crosses four Berlin DGM1 tile areas:

- `374_5822`
- `376_5822`
- `374_5824`
- `376_5824`

Raw DGM source data is kept locally under `terrain_src/`.

## Scripts

- `blender_pipeline.py` — shared orchestration
- `terrain_mesh.py` — terrain mesh preparation
- `import_terrain.py` — Blender terrain import path
- `../../lyra/scripts/build_dgm_obj.py` — UE-oriented DGM preparation
- `../../lyra/scripts/import_dgm_terrain.py` — UE terrain import
- `../../lyra/scripts/create_gis_materials.py` — GIS material setup
## Output layout

- `output/master/` — engine-neutral intermediate/master data
- `output/ue5/` — Unreal-oriented exports
- `output/source2/` — Source 2-oriented exports

## Git policy

Commit:
- scripts
- documentation
- small configuration/metadata files

Do not commit normal generated/raw working data:
- DGM ZIP archives
- extracted raw terrain tiles
- Blender backup files
- generated export/cache directories
- large temporary meshes

The authoritative production status is tracked in `docs/CURRENT_STATUS.md`.

## Quality gates

A map export is not considered production-ready until:
1. coordinate scale/origin is validated
2. terrain elevation is visibly correct
3. collision is validated
4. landmark replacement geometry is identified
5. engine-specific navigation is generated
6. gameplay routes and objectives are tested
7. genuine in-engine screenshots are captured
