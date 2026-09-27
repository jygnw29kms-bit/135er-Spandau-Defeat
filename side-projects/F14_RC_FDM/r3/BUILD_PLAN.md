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

## P2S / PETG target

- 0.4 mm nozzle
- 0.20 mm normal layer
- 0.16 mm for wing box, pivot and sweep mechanism
- PETG baseline ~245 °C nozzle / 80 °C bed, then calibrate for the real spool
- light shells: 3 walls / low infill
- structural mechanism: 6 walls / 35–45% Gyroid or Cubic
- EDF ducts: 3 walls, prioritize smooth inside surfaces
- identical settings on left/right aerodynamic pairs

The final generated package contains **22 optimized P2S plates**. See [PRINT_PLATES.md](PRINT_PLATES.md).

## Assembly order

1. Inspect all prints; reject warp, layer separation and distorted mating surfaces.
2. Dry-fit fuselage sections `fuse_01`–`fuse_06` with their joiner rings.
3. Install longitudinal CFK reinforcement before permanent fuselage joining.
4. Assemble the central wing box with two M5 steel pivot shafts and printed doublers/spacers.
5. Fit the >=20–25 kg·cm metal-gear sweep servo and equal-length ball-link pushrods.
6. Assemble left/right root, mid and tip wing sections with 5 mm CFK reinforcement.
7. Balance the left and right wing assemblies before installation.
8. Install both 50 mm EDF units and their retaining rings.
9. Install one metal-gear servo per all-moving taileron with short rigid linkage.
10. Install battery tray, receiver, external BEC and both ESCs.
11. Test wing sweep unloaded; use mechanical end stops plus transmitter endpoint limits.
12. Determine final CG on the completed physical model, not from the render/STL alone.
13. Run EDF thrust/current, servo load, sweep-cycle and receiver range/failsafe tests before flight.

## First-flight configuration

- wings near the forward/extended position
- conservative taileron throws and expo
- full sweep disabled until the basic airframe is proven
- no automatic sweep schedule during initial flight testing

## GitHub 3D inspection

Open [F14_R3_assembled_reference.stl](stl/F14_R3_assembled_reference.stl) directly in GitHub's interactive STL viewer.

The assembled file is a reference model only. Print the individual STL/3MF files or prepared P2S plates.
