# F-14 R3 Scale — validation status

## Geometry and P2S package

Validated local R3 generation:

- printable STL parts: **41**
- watertight: **41 / 41**
- winding-consistent: **41 / 41**
- P2S 256 mm fit: **41 / 41**
- failed individual geometry checks: **0**
- assembled reference STL generated
- individual 3MF exports: **41**, plus assembled-reference 3MF
- optimized P2S plate 3MF files: **22**
- optimized plate combined STL previews: **22**
- P2S plate bounds failures after final repack: **0**
- OpenSCAD polyhedron source generated before each STL export

Two original mid+tip wing plate combinations exceeded the safe 256 mm envelope. They were deliberately split into four plates; the final **22/22** plate set stays inside the P2S XY volume.

## Print planning

The final plate plan is component/risk aware:

- wing box isolated
- left/right wing roots isolated
- paired EDF and taileron parts share identical process conditions where practical
- fuselage/ducts oriented on cut faces
- long structural jobs are not used as filler plates

Planning-time estimate: **~46.1 h total**. This is not a Bambu Studio slice result.

## GitHub build

The workflow regenerates:

- `r3/scad/generated_parts/*.scad`
- `r3/stl/*.stl`
- `r3/docs/mesh_validation.*`
- `r3/p2s/individual_3mf/*.3mf`
- `r3/p2s/plates_3mf/*.3mf`
- `r3/p2s/plate_stl/*.stl`
- `r3/p2s/plate_manifest.*`
- `r3/p2s/profiles.json`

## Flight status

**Geometry/print package validated; physical flight release pending.**

Still required: real mass/CG, EDF thrust/current, sweep-servo load, cycle/end-stop test, range/failsafe, ground/glide testing and progressive flight/sweep envelope expansion.
