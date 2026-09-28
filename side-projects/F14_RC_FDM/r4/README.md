# F-14 Tomcat RC — R4 Scale Master 900

R4 is a complete exterior rebuild. R3.1 is retained only as an engineering reference for the RC mechanism.

## Locked scale

The master is derived from the real F-14 overall dimensions:

- real extended span: **19,550 mm**
- R4 extended span target: **900 mm**
- scale: **1:21.7222**
- real length: **19,100 mm**
- R4 length: **879.28 mm**
- normal wing sweep range: **20°–68°**

Source dimensions:
- https://de.wikipedia.org/wiki/Grumman_F-14
- https://www.globalsecurity.org/military/systems/aircraft/f-14-design.htm

The supplied four-page F-14A plan remains the reconstruction reference for fuselage stations, wing/tail geometry and general cross-sectional proportions.

## Construction rule

**The external F-14 shape is the master. RC hardware must fit inside it; the exterior is not distorted to make electronics fit.**

R4 includes:

- new nose/forebody/centerbody/aftbody loft
- separate scale twin-engine nacelles and intakes
- central beavertail/tunnel
- fixed wing gloves
- variable-sweep wings
- two all-moving tailerons
- twin vertical tails
- canopy
- Twin-50-mm EDF packaging
- 5-mm steel pivots / 5×10×4 bearing target
- 6-mm CFK wing spar channels
- dual sweep-servo mounts
- battery, ESC, receiver and BEC carriers
- P2S segmentation

## GitHub 3D viewer

After the workflow generates the release:

- [R4 — wings at 20°](stl/F14_R4_assembled_20deg.stl)
- [R4 — wings at 68°](stl/F14_R4_assembled_68deg.stl)
- [R4 wing box](stl/wing_box.stl)

## Release validation

The GitHub workflow refuses to publish unless every printable STL is:

- watertight
- winding-consistent
- within the Bambu Lab P2S 256×256-mm print envelope in at least one orientation

Current generated result:

- target scale: **1:21.7222**
- target extended span: **900.000 mm**
- generated 20° assembly span: **900.002 mm**
- target length: **879.284 mm**
- generated 20° assembly length: **879.284 mm**
- printable parts: **40**
- STL files including both assembled references: **42**
- individual 3MF files including both assembled references: **42**
- optimized P2S plate 3MF files: **27**
- watertight: **40 / 40**
- winding-consistent: **40 / 40**
- P2S fit: **40 / 40**
- failed checks: **0**

See `docs/mesh_validation.json` for the generated validation data.
