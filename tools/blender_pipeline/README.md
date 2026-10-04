# Blender master pipeline

Authoritative geometry and terrain preparation for **135er Spandau Strike**.

## Engine target

**Unreal Engine 5 / Lyra is the sole production target.**

The former export path has been retired and removed from active production. Blender is the master authoring layer between Berlin geodata and UE5.

## Current Rathaus Spandau workflow

- Berlin LoD2 / 3D city data for real-world massing and reference
- DGM1 terrain input
- detailed Rathaus landmark reconstruction
- street / tram / urban set dressing
- collision helper geometry
- UE5-oriented mesh naming and scale
- FBX export for UE5

## Output layout

- `output/master/` — engine-neutral Blender/master intermediates
- `output/ue5/` — Unreal Engine 5 exports

## Quality gates

A map export is production-ready only after:
1. coordinate scale/origin validation
2. visible blockout audit passes
3. terrain elevation is validated
4. collision helpers are valid
5. landmark/detail pass is complete
6. UE5 import succeeds
7. materials, Nanite/LOD and collision are validated in UE5
8. navigation/gameplay routes work
9. genuine UE5 screenshots pass visual QA
