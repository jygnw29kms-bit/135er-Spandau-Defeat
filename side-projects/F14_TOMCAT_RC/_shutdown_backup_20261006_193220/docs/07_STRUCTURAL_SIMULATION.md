# 07 - Structural simulation and optimization plan

## Objective
Use Autodesk Fusion simulation as an engineering filter to minimize mass while maintaining adequate strength, stiffness and damage tolerance for a fully FDM-printed RC F-14.

## Core principle
Do not make the entire model thicker. Reinforce only verified load paths and local stress concentrations.

## Primary simulation zones
1. central wing box
2. left/right wing pivot structure
3. variable-sweep wing root
4. carbon spar interfaces
5. stabilator pivot structure
6. EDF mounts and duct support rings
7. fuselage segment joints
8. battery tray and restraint points
9. servo and actuator hardpoints
10. vertical-tail roots

## Structural load cases

### LC1 - normal flight
Equivalent 3 g positive maneuver load.
Purpose: stiffness, deflection and normal operating margin.

### LC2 - proof maneuver
Equivalent 6 g aircraft load.
Purpose: minimum proof condition for primary structure.

### LC3 - design check
Equivalent 8 g aircraft load.
Purpose: identify weak areas and stress concentrations. No permanent deformation is acceptable in metallic/carbon primary load paths.

### LC4 - asymmetric wing load
One wing loaded more strongly than the other.
Purpose: wing-box torsion and pivot asymmetry.

### LC5 - wing-sweep transient / jam
Actuator torque combined with aerodynamic wing load.
Purpose: pivot, linkage and hard-stop validation.

### LC6 - stabilator maneuver load
Full stabilator aerodynamic load at high dynamic pressure.
Purpose: pivot tube, bearing and servo linkage validation.

### LC7 - EDF vibration / thrust load
Motor thrust plus conservative radial vibration load.
Purpose: mount fatigue and local shell cracking.

### LC8 - battery impact / restraint
Forward acceleration and abrupt deceleration.
Purpose: battery tray and retention system.

## FDM material treatment
Printed PETG/ASA is anisotropic. Fusion's standard isotropic material assumptions are therefore not sufficient by themselves.

Engineering method:
- use conservative custom material properties
- reduce allowable strength for layer-normal loading
- avoid placing major tensile load across layer interfaces
- orient parts so primary loads run within layer planes where possible
- use carbon/metal inserts for high-cycle and concentrated loads
- validate critical printed joints with physical coupons and destructive bench tests

## Design targets

### Primary structure
- safety factor target under 6 g: >= 1.5 using conservative material allowables
- 8 g case: no catastrophic failure in primary load path
- pivot bearing deformation: minimal enough to prevent sweep misalignment
- wing-tip elastic deflection: controlled, symmetric and free from local buckling

### Secondary structure
- no visible local buckling in normal flight load case
- no cracking at fastener holes or heat-set inserts
- shell deformation must not interfere with EDF ducts or wing sweep

## Optimization loop
1. create accurate OML
2. establish internal load paths
3. create initial lightweight structure
4. assign realistic component masses
5. run structural analysis
6. inspect von Mises stress, principal stress and displacement
7. identify stress concentrations and low-utilization regions
8. add ribs/gussets/carbon only where required
9. remove material from low-stress zones
10. repeat until strength/stiffness and mass targets are satisfied
11. print critical test coupons
12. correlate physical test behavior with simulation assumptions

## Geometry rules for FDM durability
- no abrupt wall-thickness transitions in highly loaded areas
- generous fillets around hardpoints
- no sharp internal corners at pivots or spar sockets
- load-spreading washers / metal plates where useful
- through-bolts preferred over self-tapping screws in primary structure
- heat-set inserts only where surrounding wall thickness is sufficient
- carbon tubes must be bonded over adequate overlap length
- printed bearing surfaces are sacrificial or bushed, never critical precision journals

## Mass-control rule
Every reinforcement requires a reason and a mass cost.
Every simulation revision records:
- part mass before
- part mass after
- maximum stress
- maximum displacement
- safety factor
- reason for change

Goal: minimum mass for required structural performance, not maximum apparent rigidity.
