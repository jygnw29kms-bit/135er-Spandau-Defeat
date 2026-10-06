# 135er F-14 Tomcat RC

Clean-sheet restart of the RC/FDM F-14 project.

## Current engineering status - 6 October 2026

The aircraft remains **not print-ready and not flight-released**, but the native Fusion
source-geometry workflow has advanced substantially beyond the older v04 scaffold.
Validated development artifacts now include the v08 Grumman/NASA source-wing loft,
v10 carbon-cap/shear-web packaging review, v14 source-section gallery, v15 native
wing-envelope segmentation and v16 source-pivot/sweep datum review.

The candidate carbon load path is fully contained by both native wing solids, and the
four v15 solid-envelope segments pass defining-section boundary checks and the assumed
240 x 240 x 250 mm P2S packaging envelope. They are **not yet hollow printable shells**.
A source-backed pivot review has also retired the old provisional `(456.5, +/-131 mm)`
pivot, but a remaining 68-degree swept-span/source-datum conflict prevents release of
the mechanical pivot and wing box.

See [4 Oct engineering audit](docs/09_ENGINEERING_AUDIT_20261004.md),
[6 Oct continuation](docs/10_ENGINEERING_CONTINUATION_20261006.md),
[reproducible structure calculation](analysis/structural_screen.py),
[structure summary](analysis/structural_screen_summary.json) and
[propulsion benchmark](analysis/propulsion_baseline_v17.json).

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
