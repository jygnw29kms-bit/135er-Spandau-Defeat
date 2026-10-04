# 135er F-14 Tomcat RC

Clean-sheet restart of the RC/FDM F-14 project.

## Current engineering status - 4 October 2026

The latest Fusion geometry is v04 and remains provisional. The aircraft is not
print-ready or flight-released. An executed beam FE screen identifies an unsuitable
full-span tube-spar assumption. Tapered carbon caps are a sizing candidate only.
The source audit identifies a swept-span conflict and unverified fuselage/tail geometry.

See [engineering audit](docs/09_ENGINEERING_AUDIT_20261004.md),
[reproducible calculation](analysis/structural_screen.py),
[results](analysis/structural_screen_results.csv) and
[summary](analysis/structural_screen_summary.json).
The inherited 676.46-mm swept-span parameter is not a frozen production dimension.

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
