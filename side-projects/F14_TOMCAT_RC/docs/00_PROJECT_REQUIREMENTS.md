# 00 - Project requirements

## Objective
Create a flyable FDM RC F-14 Tomcat whose visible outer mold line follows the real aircraft as closely as practical at model scale.

## Priority
1. flight safety and controllability
2. original F-14 external geometry
3. structural integrity
4. low mass / correct CG
5. propulsion efficiency and cooling
6. serviceability
7. printability
8. scale detailing

## Baseline
- Wingspan at 20 deg: 900 mm
- Target length: ~868 mm
- Twin 50 mm EDF
- 4S LiPo
- Functional synchronized wing sweep 20-68 deg
- Full-flying stabilators
- FDM-first construction
- Autodesk Fusion as master CAD

## Structural rules
- Wing pivot loads go into a dedicated wing box.
- Metal pivot shafts / bolts; printed skin never carries pivot load alone.
- Carbon reinforcement used where it beats printed mass.
- Repeatedly serviced joints use inserts, nuts or through-fasteners.
- Battery, EDFs, ESCs, receiver and sweep mechanism remain serviceable.

## Weight
- Target AUW: 950-1100 g; subsystem budget target 1050 g
- Redesign threshold: 1200 g predicted AUW
- The 1300 g sum of subsystem warning ceilings is not an acceptable flight target.
- These values follow [mass budget v2](04_MASS_BUDGET.md); they supersede the older 1.15-1.35 kg range and 1.40 kg threshold.
- Every subsystem gets a mass budget before detail design.

## Geometry rule
RC packaging may not change the visible OML unless a documented safety reason requires it.
