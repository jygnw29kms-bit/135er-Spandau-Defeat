# 06 - Engineering baseline v1

## Full-scale reference dimensions
Source basis: National Naval Aviation Museum F-14A specification plus NASA CR-163098 three-view/model geometry.

- length: 62 ft 8 in = 19.1008 m
- span, wings forward: 64 ft 1 in = 19.5326 m
- span, fully swept: 48 ft 2 in = 14.6812 m
- height: 16 ft = 4.8768 m
- reference wing area: 565 ft² = 52.49 m²
- wing leading-edge sweep range: 20° to 68°

## Model scale locked by span
Target forward-sweep span = 900.0 mm.

Scale factor = 0.900 / 19.5326 = 0.0460768
Scale = 1 : 21.703

Derived scale dimensions:
- overall length: 880.10 mm
- height: 224.71 mm
- span at 68°: 676.46 mm
- scale reference wing area: 0.11144 m² = 11.144 dm²

## Flight mass target
The earlier 1.15-1.35 kg target is rejected as too heavy for this scale.

New targets:
- design AUW: 950-1100 g
- preferred maiden AUW: <=1050 g
- redesign threshold: 1200 g
- no-detail structural target before finish: <=900 g

Approximate reference-area wing loading:
- 950 g: 85.2 g/dm²
- 1000 g: 89.7 g/dm²
- 1050 g: 94.2 g/dm²
- 1100 g: 98.7 g/dm²
- 1200 g: 107.7 g/dm²

This remains a fast EDF jet. Low-speed behavior must be treated as a primary design constraint.

## Propulsion target
Architecture: twin 50 mm EDF, 4S.

System-level design target:
- combined static thrust: >= 900 g, preferred 1000-1100 g
- thrust-to-weight at 1050 g AUW: >=0.86, preferred >=0.95
- total full-power current target: 60-80 A
- ESCs: 2 x 40 A minimum, 2 x 50 A preferred if mass penalty is small
- battery starting envelope: 4S 2600-3000 mAh, high-discharge, selected by measured sag/current rather than label C-rating
- independent receiver/BEC supply preferred

No specific EDF or battery is frozen until bench data are available.

## CG philosophy
CG is not copied from an RC product.
Initial CG will be established from the actual model aerodynamic geometry and then cross-checked against proven RC F-14 ranges.
Battery tray must provide at least 50 mm longitudinal adjustment.

## Safety factors
- primary wing-box / pivot static proof target: 6 g equivalent model weight minimum
- design check: 8 g equivalent without permanent deformation in metallic/carbon load path
- control-surface pivots: no printed polymer used as sole bearing surface
- sweep system: mechanical end stops independent of servo travel
- battery retention: primary strap plus secondary positive stop
