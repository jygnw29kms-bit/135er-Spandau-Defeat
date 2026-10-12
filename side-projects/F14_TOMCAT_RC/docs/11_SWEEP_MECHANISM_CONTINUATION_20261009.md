# F-14 sweep mechanism continuation — 9 October 2026

## Scope
This note records the transition from packaging-only linkage work to a mechanically useful synchronized wing-sweep linkage. The aircraft remains not print-ready and not flight-released.

## v37 — direct-linkage plane scan
The direct root-link concept did not package cleanly. The best scanned plane at z = 184 mm retained only about 76.6% minimum rod containment inside the reference outer mold line, so the direct arrangement was not carried forward.

## v38 — inboard crank packaging success
The v38 inboard-crank scan solved the immediate packaging problem: all 24 scanned candidates were reported fully packaged, with no fixed-structure hits in the tested envelopes. The original v38 selection minimized slider travel and chose a [-10, -20] mm crank vector with a 3.23 mm slider stroke.

That selection is now treated as a packaging proof, not as a released mechanism.

## v39 — load-screen finding: near-toggle geometry
A preliminary mechanical/load screen exposed a critical issue that the v38 packaging metric did not measure: the restricted v38 candidate family approaches a toggle condition during the 20–68 degree sweep. A representative ~18 mm-stroke candidate produced only about 0.70 mm minimum effective linkage moment arm, giving only about 0.083 N·m theoretical minimum wing torque when screened against the provisional 2.0 N·m servo assumption.

The v38 minimum-stroke candidate is therefore rejected as a production mechanism despite its excellent geometric containment.

## v40 — moment-arm-optimized kinematic search
The v40 search broadens crank direction, crank radius, slider station and initial slider position. The search rejects candidates with inadequate minimum moment arm and constrains slider travel to a range that remains achievable with the provisional 17 mm servo horn.

Current selected analytical candidate:
- crank vector at 20 degrees: [+25, -20] mm
- crank radius: 32.016 mm
- synchronized slider attachment Y: 65 mm
- slider X at 20 degrees: 580 mm
- rod length: 70.684 mm
- slider travel: 29.796 mm
- minimum linkage moment arm: 30.043 mm
- maximum linkage moment arm: 32.014 mm
- estimated servo travel with 17 mm horn: 122.41 degrees
- theoretical minimum wing torque at a provisional 2.0 N·m servo stall torque: 3.535 N·m

This is a major improvement over v38 because the effective moment arm remains large throughout the sweep instead of collapsing near a toggle.

## Preliminary hardware/load screen
Using a deliberately conservative 2.5 dynamic multiplier on the provisional servo tangential force gives a design rod-force screen of approximately 294 N. Under simple section checks, an M3 pin in single shear is about 41.6 MPa and a 5 mm-thick, 14 mm-wide crank neck with a 3.3 mm pin bore is about 5.50 MPa net-section nominal stress. These are screening calculations only; they do not constitute material or flight release.

## Release gates still open
Before mechanism release, the project still requires:
1. Fusion OML containment and collision verification of the v40 geometry over the entire 20–68 degree sweep.
2. Actual sweep-servo selection and torque/speed verification at the intended operating voltage.
3. Rod-end, pin bearing, crank bearing and guide-load checks.
4. Material/coupon verification for any printed load-bearing mechanism parts.
5. Physical proof-load test and repeated full-cycle endurance test.
6. Integration with the final hollow FDM structure and mass/CG review.

`mechanical_detail_release`, `print_release` and `flight_release` remain false until those gates are closed.
