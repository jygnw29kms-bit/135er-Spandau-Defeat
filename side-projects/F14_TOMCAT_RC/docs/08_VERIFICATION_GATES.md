# 08 - Verification gates and release criteria

## Design baseline
- nominal AUW: 1.05 kg
- wings-forward span: 900 mm
- primary proof load: 6 g
- structural design check: 8 g
- asymmetric design check: 8 g with 70/30 wing-load split
- battery restraint proof: 20 g forward
- twin EDF axial mount load: 5 N per side minimum baseline
- sweep actuator jam/stall torque envelope: 2.0 N*m

## Calculated baseline loads
At 1.05 kg:
- 3 g total vertical load: 30.891 N
- 6 g total vertical load: 61.782 N
- 8 g total vertical load: 82.376 N
- 8 g symmetric per side: 41.188 N
- conservative 8 g root bending moment at 250 mm resultant arm: 10.297 N*m
- asymmetric 8 g 70% high-side force: 57.663 N
- asymmetric high-side root moment: 14.416 N*m
- 220 g battery at 20 g: 43.149 N forward restraint load

## Fusion study acceptance criteria

### Wing box / pivots
6 g proof:
- no local FDM allowable exceeded
- factor of safety >= 1.5 against the orientation-dependent design allowable
- no permanent deformation in metal/carbon load path
- pivot relative displacement low enough that wing sweep remains free without binding

8 g design check:
- no catastrophic load-path failure
- no pivot pull-through
- deformation must remain recoverable
- any local FDM exceedance triggers geometry/orientation redesign

8 g asymmetric:
- no excessive torsional twist of center wing box
- no interference between wing root and glove
- linkage remains below buckling/yield limits

### Stabilators
- no bearing pull-out
- no printed journal as sole primary bearing
- full-load deflection must not permit tail/nacelle interference
- servo/linkage load must remain below measured stall margin

### EDF mounts
- axial thrust load plus vibration allowance must not crack mount-ring roots
- fan unit removable without cutting structure
- ducts may not ovalize enough to rub rotor/shroud

### Fuselage joints
- no single printed tongue carries primary bending load alone
- joints use distributed overlap, keyed geometry, carbon/stringer continuity or through-fasteners
- critical joint proof load must reach 6 g equivalent without visible crack growth

### Battery restraint
- 43.2 N forward proof load minimum
- primary strap plus positive mechanical stop
- battery cannot contact wing sweep mechanism, receiver or EDF under proof load

## Physical correlation tests
Simulation release is provisional until printed coupons and assemblies are tested.

1. PETG/ASA XY tensile/bending coupon
2. layer-normal joint coupon
3. heat-set insert pull-out coupon
4. carbon-tube bonded overlap coupon
5. wing-pivot subassembly proof test
6. complete wing-box 6 g equivalent static test
7. stabilator pivot proof test
8. EDF full-throttle vibration/temperature run
9. battery-restraint 20 g equivalent static pull
10. full-airframe control and failsafe test

## Flight release gates
No maiden until all are true:
- measured AUW and CG recorded
- thrust/current/voltage sag measured
- control directions and throws verified
- sweep mechanism cycles repeatedly without binding
- 6 g structural proof tests passed
- receiver failsafe verified
- ESC/BEC thermal test passed
- no loose fasteners, cracked prints or delamination
- wings locked to forward/maiden-safe position for first flight unless the final control strategy has already been validated

## Post-maiden envelope expansion
1. conservative rates / wings forward
2. trim and CG confirmation
3. progressive speed
4. progressive load factor
5. limited sweep at safe altitude
6. full sweep only after telemetry and structural inspection
