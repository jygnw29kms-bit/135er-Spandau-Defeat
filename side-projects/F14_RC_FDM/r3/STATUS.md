# F-14 R3.1 Scale — validation status

## Final automated geometry gate

GitHub Actions build: **PASS**

- printable STL parts: **50**
- assembled reference STL: **1**
- total STL in `stl/`: **51**
- watertight printable parts: **50 / 50**
- winding-consistent printable parts: **50 / 50**
- P2S 256 mm fit: **50 / 50**
- failed individual geometry checks: **0**
- individual 3MF including assembled reference: **51**
- optimized P2S plate 3MF: **25**
- combined plate STL previews: **25**
- P2S plate bound failures: **0**

## R3.1 structural changes

- fuselage wall target increased to 2.8 mm
- heavy solid wing-box concept replaced by a structural truss wing box
- wing box: **170 × 250 × 26 mm**
- wing-box CAD volume reduced to about **721 cm³** while retaining the STRUCT profile
- pivot moved inboard under the wing glove
- 10.2 mm bearing pockets added
- 5 mm steel pivot shaft target retained
- 6.4 mm continuous CFK spar tunnels added to wing root/mid/tip
- 3.2 mm sweep-linkage holes added to wing roots
- dual 23 g-class sweep-servo mounts added
- standard-servo adapter option added
- 17 g-class taileron servo frames added
- dedicated ESC, receiver and BEC trays added
- battery tray reinforced
- EDF rings changed to 56 mm housing opening

## Strength-first P2S profiles

- SHELL: 4 walls / 8% infill
- WING: 4 walls / 12% infill
- STRUCT: 8 walls / 55% infill / 0.16 mm layers
- STRUCT_LIGHT: 5 walls / 25% infill
- DUCT: 4 walls / 10% infill

Current geometry/profile planning estimate: **~81.85 h total**.

This is not a Bambu Studio/OrcaSlicer time prediction. Slice the generated 3MF files with the real P2S and actual PETG calibration for final time and material usage.

## Engineering research

The R3.1 structural approach was cross-checked against public specifications for:

- a 1050 mm twin-50 mm 3D-printed F-14 using separate sweep-servo mounts, bearings and 6 mm carbon reinforcement
- Freewing 64 mm and 80 mm F-14 designs using metal-gear servos, rigid wing-box structures and carbon reinforcement
- other 3D-printed EDF aircraft using reinforced internal load paths

Details and source URLs: [REFERENCE_RESEARCH.md](REFERENCE_RESEARCH.md).

## Flight release

**Geometry and print package: validated.**  
**Physical flight release: pending.**

Still required:

- real printed airframe mass
- measured CG
- EDF static thrust and total current
- real servo current / BEC load
- bearing and pivot fit inspection
- sweep-servo load test
- repeated sweep cycle/end-stop test
- receiver range/failsafe test
- ground/glide testing where appropriate
- progressive flight and flutter-envelope testing
