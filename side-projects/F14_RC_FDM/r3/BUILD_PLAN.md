# F-14A RC R3.1 — assembly and hardware plan

R3.1 follows one priority: **stability before weight**. Printed PETG is combined with carbon and metal hardware; the printed plastic is not expected to carry the complete swing-wing load by itself.

## RC hardware target

| Part | Qty | R3.1 specification |
|---|---:|---|
| EDF | 2 | 50 mm 4S units; verify actual housing OD before final ring print |
| ESC | 2 | 40–50 A brushless with cooling |
| Flight battery | 1 | 4S 3300–4000 mAh, >=45C |
| Receiver | 1 | 8-channel recommended, failsafe/telemetry preferred |
| Taileron servos | 2 | 17 g-class digital metal gear, body around 28×13×35 mm |
| Wing-sweep servos | 2 | 23 g-class high-torque metal gear; >=6 kg·cm preferred |
| Standard-servo adapters | 2 | included as printable alternative adapters |
| External BEC | 1 | 6 V preferred for listed servo class, >=5 A continuous |
| Wing pivot shafts | 2 | 5 mm smooth steel shafts with collars/retainers |
| Pivot bearings | 8 | 5×10×4 mm recommended; test fit before assembly |
| Wing CFK | 2 | 6 mm CFK tube, approx. 420 mm each then trim |
| Additional carbon strip | 2 | optional 5×1 or 6×1 mm across high-load root area |
| Fuselage CFK | 2–4 | 4 mm rods/tubes as required |
| Sweep linkage | 2 | M3 ball links / threaded rod |
| Heat-set inserts | as needed | M2/M3 for serviceable hardware |

The two sweep servos are independent mechanical drives but should be synchronized by transmitter/controller setup. Use matched endpoints and slow sweep movement.

## Pivot and wing structure

R3.1 uses:

- pivot position moved inboard under the wing glove
- 10.2 mm printed bearing pockets
- 5 mm steel shaft target
- printed pivot doublers and retaining spacers
- 6.4 mm internal channel through root/mid/tip for 6 mm CFK tube
- 3.2 mm linkage hole in each root for the sweep linkage
- truss-style wing box with perimeter rails, central cross beams, diagonals and large pivot zones

Do not substitute a threaded bolt rubbing directly in PETG for the bearing/shaft arrangement if avoidable.

## Electronics mount dimensions

See [ELECTRONICS_MOUNTS.md](ELECTRONICS_MOUNTS.md).

Key clearances:

- sweep-servo primary opening: **31 × 16.5 mm**
- standard-servo adapter opening: **42 × 22 mm**
- taileron-servo opening: **31 × 16.5 mm**
- battery tray external: **220 × 58 × 14 mm**
- ESC tray external: **82 × 40 × 10 mm**
- receiver tray external: **62 × 44 × 9 mm**
- BEC tray external: **58 × 38 × 9 mm**
- EDF retaining ring: **72 mm OD / 56 mm opening / 10 mm thick**

## P2S / PETG target

- 0.4 mm nozzle
- PETG baseline around 245 °C nozzle / 80 °C bed, then calibrate for the real spool

Profile families generated with the release:

- **SHELL** — 0.20 mm, 4 walls, 4 top/bottom, 8% infill
- **WING** — 0.20 mm, 4 walls, 5 top/bottom, 12% infill
- **STRUCT** — 0.16 mm, 8 walls, 8 top/bottom, 55% infill
- **STRUCT_LIGHT** — 0.20 mm, 5 walls, 6 top/bottom, 25% infill
- **DUCT** — 0.20 mm, 4 walls, 4 top/bottom, 10% infill
- **COSMETIC** — 0.16 mm, 3 walls, 8% infill

The current release contains **25 optimized P2S plates**. The 250 mm-wide wing box is intentionally printed alone with a reduced plate-edge margin instead of weakening the component to gain extra clearance.

## Assembly order

1. Print the mechanism test parts first: pivot spacer/doubler, one sweep-servo mount, one taileron mount and one EDF ring.
2. Verify real bearing, servo and EDF housing fit before printing the longest structural jobs.
3. Print the wing box and inspect every layer around the pivot areas.
4. Install bearing stacks and 5 mm steel pivot shafts without binding.
5. Assemble each wing root/mid/tip around the continuous 6 mm CFK spar.
6. Bond/secure the wing root joints; add optional 5×1/6×1 carbon strip across the high-load region.
7. Install the two 23 g-class sweep servos and equal-length ball-link pushrods.
8. Set mechanical end stops before programming transmitter endpoints.
9. Dry-fit fuselage sections `fuse_01`–`fuse_06` and install longitudinal CFK reinforcement before permanent joining.
10. Install twin 50 mm EDFs, their retaining rings and the two ESCs in cooling airflow.
11. Install the two taileron servos in the dedicated structural frames.
12. Install battery tray, receiver and BEC; strap and retain the battery mechanically.
13. Verify sweep motion through the complete range with EDFs off and no aerodynamic load.
14. Balance left/right wing assemblies.
15. Determine actual CG on the completed physical model.
16. Run EDF thrust/current, servo-load, repeated sweep-cycle and radio range/failsafe tests before flight.

## First-flight configuration

- wings close to the forward/extended position
- conservative taileron throws
- expo enabled
- sweep function initially limited or locked
- no automatic full-sweep schedule until the physical model is proven
- expand the sweep envelope progressively only after structural inspection

## GitHub 3D inspection

Open [F14_R3_assembled_reference.stl](stl/F14_R3_assembled_reference.stl) in GitHub's interactive STL viewer.

The assembled file is a visual/fit reference. Print the individual STL/3MF files or the prepared P2S plates.
