# P2S PETG — R3.1 optimized print plates

The final R3.1 package contains **25 plate 3MF files** and matching combined STL previews.

Times below are geometry/profile planning estimates, **not** Bambu Studio or OrcaSlicer slice times.

| # | Plate | Est. | Profile / parts |
|---:|---|---:|---|
| 01 | Fuselage Nose / Service | 1.26 h | fuse_01, joiner_160, joiner_800 |
| 02 | Fuselage Cockpit | 5.51 h | fuse_02, canopy |
| 03 | Fuselage Center A | 1.85 h | fuse_03, joiner_320 |
| 04 | Fuselage Center B | 2.88 h | fuse_04, battery_tray |
| 05 | Fuselage Rear | 1.37 h | fuse_05, joiner_640 |
| 06 | Fuselage Tail | 2.05 h | fuse_06, joiner_480, electronics_hatch |
| 07 | Wingbox Structural | **22.95 h** | STRUCT — wing_box |
| 08 | Sweep Hardware | 5.32 h | STRUCT — crank, doublers, spacers |
| 09 | Sweep Servo Mounts | 2.84 h | STRUCT — 2 compact mounts + 2 standard adapters |
| 10 | Left Wing Root | 3.37 h | WING |
| 11 | Right Wing Root | 3.37 h | WING |
| 12 | Left Wing Mid | 2.30 h | WING |
| 13 | Left Wing Tip | 1.41 h | WING |
| 14 | Right Wing Mid | 2.30 h | WING |
| 15 | Right Wing Tip | 1.41 h | WING |
| 16 | Left Wing Glove | 3.90 h | WING |
| 17 | Right Wing Glove | 3.90 h | WING |
| 18 | Tailerons | 2.26 h | WING — left + right |
| 19 | Taileron Servo Mounts | 0.76 h | STRUCT — left + right |
| 20 | Left Vertical Tail | 1.44 h | WING |
| 21 | Right Vertical Tail | 1.44 h | WING |
| 22 | EDF Intakes | 2.36 h | DUCT — pair + EDF rings |
| 23 | EDF Nacelles Mid | 2.14 h | DUCT — pair |
| 24 | EDF Nacelles Rear | 1.98 h | DUCT — pair |
| 25 | Electronics Trays | 1.48 h | STRUCT_LIGHT — 2 ESC + receiver + BEC |

**Planning total: ~81.85 hours.**

## Why the plates are split this way

- The **wing box prints alone** because it is the highest-load and highest-cost failure item.
- Its 250 mm width intentionally uses a reduced edge margin on the 256 mm P2S bed rather than weakening the structure.
- Left/right wing roots print separately so a single defect does not ruin both roots.
- Sweep hardware and sweep servo mounts use the same STRUCT profile but are separated from the long wing-box job.
- Taileron servo mounts are structural and are therefore not mixed into the lighter taileron plate.
- EDF parts are grouped by identical duct profile and print orientation.
- Electronics trays share a separate reinforced profile.

## Profile families

- **SHELL** — 0.20 mm, 4 walls, 4 top/bottom, 8% infill
- **WING** — 0.20 mm, 4 walls, 5 top/bottom, 12% infill
- **STRUCT** — 0.16 mm, 8 walls, 8 top/bottom, 55% infill
- **STRUCT_LIGHT** — 0.20 mm, 5 walls, 6 top/bottom, 25% infill
- **DUCT** — 0.20 mm, 4 walls, 4 top/bottom, 10% infill
- **COSMETIC** — 0.16 mm, 3 walls, 4 top/bottom, 8% infill

PETG baseline: start around **245 °C nozzle / 80 °C bed**, then use actual filament calibration.

The generated 3MF files contain geometry and placement. Exact temperature, flow, cooling and speed remain slicer-side so the project can be matched to the real P2S and the actual PETG spool.
