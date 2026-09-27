# P2S PETG — optimized print plates

The R3 print package uses **22 plates**. Times below are planning estimates from geometry/profile data, not Bambu Studio sliced times. Exact P2S time must be taken from the slicer after loading the 3MF and selecting the actual PETG spool.

| # | Plate | Est. | Parts |
|---:|---|---:|---|
| 01 | Fuselage Nose / Service | 0.92 h | fuse_01, joiner_160, joiner_800 |
| 02 | Fuselage Cockpit | 4.97 h | fuse_02, canopy |
| 03 | Fuselage Center A | 1.17 h | fuse_03, joiner_320 |
| 04 | Fuselage Center B | 2.03 h | fuse_04, battery_tray |
| 05 | Fuselage Rear | 0.91 h | fuse_05, joiner_640 |
| 06 | Fuselage Tail | 1.39 h | fuse_06, joiner_480, electronics_hatch |
| 07 | Wingbox Structural | 6.68 h | wing_box |
| 08 | Sweep Hardware | 3.27 h | crank, doublers, spacers, servo mount |
| 09 | Left Wing Root | 2.42 h | wing_L_root |
| 10 | Right Wing Root | 2.42 h | wing_R_root |
| 11 | Left Wing Mid | 1.67 h | wing_L_mid |
| 12 | Left Wing Tip | 1.06 h | wing_L_tip |
| 13 | Right Wing Mid | 1.67 h | wing_R_mid |
| 14 | Right Wing Tip | 1.06 h | wing_R_tip |
| 15 | Left Wing Glove | 2.73 h | glove_L |
| 16 | Right Wing Glove | 2.73 h | glove_R |
| 17 | Tailerons | 1.64 h | taileron_L, taileron_R |
| 18 | Left Vertical Tail | 1.05 h | vstab_L |
| 19 | Right Vertical Tail | 1.05 h | vstab_R |
| 20 | EDF Intakes | 1.84 h | intake_L/R, EDF rings |
| 21 | EDF Nacelles Mid | 1.76 h | nacelle_L/R_mid |
| 22 | EDF Nacelles Rear | 1.64 h | nacelle_L/R_rear |

**Planning total:** ~46.1 hours.

## Profile families

- **SHELL** — 0.20 mm, 3 walls, 5% infill
- **WING** — 0.20 mm, 3 walls, 7% infill
- **STRUCT** — 0.16 mm, 6 walls, 45% infill
- **STRUCT_LIGHT** — 0.20 mm, 4 walls, 18% infill
- **DUCT** — 0.20 mm, 3 walls, 8% infill
- **COSMETIC** — 0.16 mm, 3 walls, 8% infill

PETG baseline: start around **245 °C nozzle / 80 °C bed**, then use the actual filament's flow/temperature calibration. Structural parts should be printed conservatively; do not trade layer adhesion for speed.

The generated 3MF files contain geometry and placement. Exact printer/filament process settings remain slicer-side so they can be matched to the real P2S and PETG spool.
