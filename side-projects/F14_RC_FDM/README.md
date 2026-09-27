# F-14 RC FDM

Independent RC side project inside **135er-Spandau-Defeat**.

> **Not part of the game.** No Source 2, map, server, build or deployment dependency.

## R2 milestone

The F-14 has now been rebuilt as a parametric OpenSCAD RC model.

- ~950 mm target length
- ~900 mm extended target span
- 20-60 degree model sweep range
- twin 50 mm EDF / 4S target power system
- PETG + CFK/metal reinforcement
- 35 exported STL parts
- 35/35 current STL parts pass watertight/winding/256 mm checks
- 17 Bambu Lab P2S plate layouts
- 3D assembly/exploded views generated from the actual exported STL geometry

## Files

- [OpenSCAD R2 master](scad/f14_r2_master.scad)
- [R2 build plan](docs/BUILD_PLAN_R2.md)
- [RC hardware BOM](docs/RC_HARDWARE_BOM.md)
- [P2S PETG profile](docs/P2S_PETG_PROFILE.md)
- [R2 validation status](docs/STATUS.md)
- [P2S plates notes](plates/README.md)

## Release status

**Geometry/printability validated; not flight validated.**

A real prototype must still establish final mass, CG, EDF thrust/current, sweep loads, control authority and flutter envelope before the design can be called flight-released.
