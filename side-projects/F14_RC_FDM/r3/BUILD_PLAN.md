# F-14A RC R3 — 3D assembly and RC build plan

## RC hardware target

| Part | Qty | Specification |
|---|---:|---|
| EDF | 2 | 50 mm, balanced, 4S capable |
| ESC | 2 | 50 A brushless with cooling |
| Flight battery | 1 | 4S 3300–4000 mAh, >=45C |
| Receiver | 1 | 8 channel recommended, failsafe/telemetry preferred |
| Taileron servos | 2 | digital metal gear, 12–17 g, >=3 kg·cm |
| Wing-sweep servo | 1 | metal gear, >=20–25 kg·cm |
| External BEC | 1 | 6–8.4 V adjustable, >=5 A continuous |
| Wing pivot shafts | 2 | M5 steel with washers + Nyloc |
| Wing reinforcement | 2 | 5 mm CFK tube/rod |
| Fuselage reinforcement | 2–4 | 4 mm CFK rods |
| Sweep linkage | 2 | M2/M3 threaded rod + ball links |
| Heat-set inserts | as needed | M2/M3 |

## Print target — Bambu Lab P2S / PETG

Baseline:

- 0.4 mm nozzle
- 0.20 mm layer; use 0.16 mm for wing-box/pivot/sweep parts
- PETG around 245 °C nozzle / 80 °C bed as a starting point, then calibrate for the actual spool
- light shells: 3 walls, low infill
- wing box/pivot parts: 6 walls, 35–45 % Gyroid/Cubic
- EDF ducts: 3 walls and smooth inner surfaces
- identical settings left/right for wing and tail pairs

The generated `plates/` directory groups 17 print plates. Always inspect the plate in the slicer before printing.

## Assembly order

1. Print and inspect all parts. Reject warping, layer separation or distorted joint surfaces.
2. Dry-fit fuselage sections `fuse_01` through `fuse_06` with their joiner rings.
3. Install longitudinal CFK reinforcement before permanently joining fuselage sections.
4. Build the central wing box with two M5 steel pivots and the printed pivot doublers/spacers.
5. Fit the wing-sweep servo. The sweep crank is intentionally supplied as a robust blank; drill the centre/link holes to the hardware actually used and ream accurately.
6. Assemble left and right wing root/mid/tip groups. Use the pivot doublers as drill guides for the exact M5 pivot through the wing roots.
7. Add 5 mm CFK reinforcement to each wing. Balance left/right wing masses before installation.
8. Install both 50 mm EDF units with the printed EDF retaining rings.
9. Install one servo per all-moving taileron. Keep linkage short and rigid.
10. Install battery tray, receiver, BEC and both ESCs. Keep receiver/antenna wiring away from high-current EDF wiring.
11. Test the sweep mechanism without aerodynamic load. Use mechanical stops and transmitter endpoint limits so the servo never stalls at full travel.
12. Determine actual CG from the completed physical airframe. Do not infer final CG from the illustration or STL alone.
13. Perform EDF thrust/current test, servo load test, sweep cycle test and receiver range/failsafe test before flight.

## First-flight configuration

- wings near the forward/extended position
- conservative taileron throws
- expo enabled
- sweep function initially locked or only enabled high and slow after the basic airframe is proven
- no automatic full-sweep schedule until the physical prototype has been validated

## 3D assembly inspection

Open [F14_R3_assembled_reference.stl](stl/F14_R3_assembled_reference.stl) directly on GitHub for the interactive 3D assembly view.

The assembled STL is a visual/fit reference. Print the individual files, not the combined assembly.
