# F-14A Tomcat RC FDM — R3 Scale

This is the **scale rebuild** of the F-14 RC side project. It is isolated from the Source 2 game and does not participate in any game build or deploy path.

## Geometry basis

The exterior proportions are reconstructed from:

- the supplied 4-page 1/24 F-14A model plan (fuselage stations, side/top/front geometry, wing/tail shapes and structure),
- published real-aircraft overall dimensions used as the scale reference,
- public RC/FDM layouts only as engineering references for printable segmentation and twin-EDF packaging.

The target scale is approximately **1:20**:

- length: **955 mm**
- extended span target: **977.5 mm**
- characteristic F-14 variable-sweep layout
- twin 50 mm EDF internal arrangement
- segmented so every individual printable STL fits a **Bambu Lab P2S 256 × 256 mm** build volume in at least one orientation.

This is a reconstruction, not Grumman OEM CAD. The project therefore calls it *scale reconstructed* rather than claiming access to original manufacturer surface data.

## OpenSCAD export pipeline

`generate_r3.py` builds each mesh, writes a separate OpenSCAD `polyhedron(...)` source for that part, then calls **OpenSCAD** to create the final STL. The generated STL is then re-opened and checked.

Current automated acceptance criteria:

- watertight
- consistent winding
- individual P2S build-volume fit
- mirrored left/right component symmetry checks by construction
- assembled-reference generation

## GitHub 3D viewer

After the build workflow completes, click these files directly in GitHub:

- [Complete assembled F-14 R3](stl/F14_R3_assembled_reference.stl)
- [Wing box](stl/wing_box.stl)
- [Left wing root](stl/wing_L_root.stl)
- [Right wing root](stl/wing_R_root.stl)
- [Left intake](stl/intake_L.stl)
- [Right intake](stl/intake_R.stl)
- [Left vertical tail](stl/vstab_L.stl)
- [Right vertical tail](stl/vstab_R.stl)

GitHub renders STL files with its built-in interactive 3D viewer.

## Build plan

See [BUILD_PLAN.md](BUILD_PLAN.md) for RC hardware, assembly order, sweep mechanism, PETG recommendations and pre-flight validation.

## Generated output

- `scad/generated_parts/` — one OpenSCAD polyhedron source per printed part
- `stl/` — OpenSCAD-exported STL parts
- `plates/` — grouped P2S plate STLs and manifest
- `docs/mesh_validation.csv` — per-part geometry check
- `docs/mesh_validation.json` — validation summary

## Release state

**Print-geometry validated by automation; physical flight validation remains required.**

Before flight release, the real printed prototype still needs measured mass/CG, EDF thrust/current, sweep-servo load and cycle tests, range/failsafe tests and progressively expanded flight/sweep testing.
