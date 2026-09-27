# F-14 R3 Scale — validation status

## Local construction/validation run

The R3 generator was executed before committing the automated pipeline.

Result:

- individual printable STL parts: **41**
- watertight: **41 / 41**
- winding-consistent: **41 / 41**
- fit within 256 mm P2S volume in at least one orientation: **41 / 41**
- failed individual geometry checks: **0**
- assembled reference STL generated
- 17 grouped P2S plate STL layouts generated
- one OpenSCAD polyhedron source generated per STL before STL export

The wing-root and sweep-crank geometry were revised during validation after initial mesh checks exposed defects. Only the corrected geometry is represented by the committed R3 generator.

## GitHub generation

The workflow `.github/workflows/f14-r3-build.yml` regenerates:

- `r3/scad/generated_parts/*.scad`
- `r3/stl/*.stl`
- `r3/plates/*.stl`
- `r3/docs/mesh_validation.csv`
- `r3/docs/mesh_validation.json`

The workflow requires GitHub Actions with repository content-write permission. When Actions are enabled, the generated STL files are committed back to the R3 directory and become directly viewable in GitHub's STL 3D viewer.

## Flight status

Geometry/printability validation is not a flight release. Physical prototype testing is still required for:

- final mass and centre of gravity
- EDF thrust and total current
- sweep-servo load
- sweep mechanism cycle test
- control throw and authority
- radio range/failsafe
- flutter envelope
- progressive sweep testing in flight
