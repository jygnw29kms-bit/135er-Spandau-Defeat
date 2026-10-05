# 135er F-14 Tomcat RC

Clean-sheet restart of the RC/FDM F-14 project.

## Current engineering status - 6 October 2026

The user confirmed the v05 orientation. Native Fusion v06 reference sketches and
v08 original Grumman basic-wing solids were executed and archived. The original
wing dataset contains eight defining sections; the native review has two wing
bodies, not a complete aircraft. The fuselage, tail, sweep mechanism and RC
installation remain unfinished. No print-ready aircraft or flight release exists.

Prepared native spar, source-profile and wing-segmentation reviews (v10/v14/v15)
have not executed. Fusion window capture times out and the installed event bridge
has not confirmed a reload. The installed add-in includes revision fingerprints
and a restart lifecycle correction; installing code does not prove native execution.

Source contour, EDF and battery calculations are provisional geometry screens.
Metric body registration, continuous clearance, actual hardware, mass properties,
strength, slicing and physical tests remain open. The beam FE screen rejects the
full-span tube-spar assumption; tapered caps remain candidates.

See [engineering audit](docs/09_ENGINEERING_AUDIT_20261004.md),
[reproducible calculation](analysis/structural_screen.py),
[results](analysis/structural_screen_results.csv) and
[summary](analysis/structural_screen_summary.json).
The inherited 676.46-mm swept-span parameter is not a frozen production dimension.

See the [current source and CAD audit](docs/10_CAD_COORDINATES_AND_REFERENCE_REPAIR.md)
and [archived native source review](cad/fusion/source_review/README.md).

## Design target
- visually scale-faithful Grumman F-14 Tomcat outer mold line
- 900 mm span at 20 deg wing sweep
- approximately 1:21.7 scale
- twin 50 mm EDF
- 4S LiPo
- functional 20-68 deg variable-sweep wings
- full-flying stabilators
- FDM-first structure for Bambu Lab P2S
- Autodesk Fusion master CAD

## Non-negotiable rule
The retired F14_RC_FDM R2/R3/R4 geometry, OpenSCAD, STL/3MF files and hardware assumptions are not design inputs for this project.

## Engineering workflow
1. establish authoritative full-scale reference geometry
2. lock scale and outer mold line
3. define aerodynamic and CG envelope
4. design central wing box and sweep mechanism
5. package EDF/ESC/battery/electronics
6. design lightweight FDM structure and carbon reinforcement
7. mass-properties review
8. export printable modules
9. bench verification
10. controlled flight-test expansion

## Documentation
- [Requirements](docs/00_PROJECT_REQUIREMENTS.md)
- [Reference baseline](docs/01_REFERENCE_BASELINE.md)
- [RC benchmark references](docs/02_RC_BENCHMARKS.md)
- [System architecture](docs/03_SYSTEM_ARCHITECTURE.md)
- [Mass budget](docs/04_MASS_BUDGET.md)
- [Verification plan](docs/05_DESIGN_VERIFICATION.md)

## CAD
The Fusion add-in under cad/fusion/F14TomcatRC is the new parametric CAD bootstrap. It is an early OML/packaging scaffold and is not yet the frozen production surface.

The [mass budget v2](docs/04_MASS_BUDGET.md) sets the 1050 g target and 1200 g
redesign threshold. The 1300 g sum of subsystem warning ceilings is not an
acceptable flight target. CAD and measured component mass roll-ups are pending.
