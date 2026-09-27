# R3.1 electronics and mechanism mount dimensions

This file documents the **actual generated R3.1 mount geometry**. Dimensions are millimetres.

## Wing sweep

### Primary 23 g-class mount

Generated files:

- `sweep_servo_mount_L.stl`
- `sweep_servo_mount_R.stl`

Geometry:

- overall STL envelope: **70 × 46 × 10**
- clear servo-body opening: **31 × 16.5**
- heavy structural frame and mounting feet
- P2S profile: **STRUCT**

The opening was selected around the compact 23 g metal-gear class used in comparable EDF F-14 designs. Example published servo dimensions are about 28.3–28.5 × 13–13.5 × 30–33.4 mm.

**Always test the real servo before final assembly.** Servo tabs, cable exit and horn height vary even when body dimensions are similar.

### Standard-servo adapter

Generated files:

- `sweep_servo_adapter_STD_L.stl`
- `sweep_servo_adapter_STD_R.stl`

Geometry:

- overall: **62 × 42 × 7**
- clear opening: **42 × 22**
- P2S profile: **STRUCT**

This is an alternate adapter, not the default R3.1 sweep-servo choice.

## Taileron servo mounts

Generated files:

- `taileron_servo_mount_L.stl`
- `taileron_servo_mount_R.stl`

Geometry:

- overall: **48 × 30 × 8**
- clear opening: **31 × 16.5**
- intended for 17 g-class metal-gear servos
- P2S profile: **STRUCT**

Comparable published 17 g Freewing servo dimensions are around 28.3 × 13.3 × 34.9 mm.

## Battery tray

File: `battery_tray.stl`

- overall: **220 × 58 × 14**
- base thickness: 5
- side rails: 4 mm nominal
- usable centre width approx. **50 mm**
- profile: **STRUCT_LIGHT**

The long tray deliberately allows longitudinal battery movement for final CG adjustment. Use two independent hook-and-loop straps or equivalent mechanical restraint.

## ESC trays

Files:

- `esc_tray_L.stl`
- `esc_tray_R.stl`

- overall each: **82 × 40 × 10**
- profile: **STRUCT_LIGHT**
- intended for common 40–50 A ESC class
- mount in cooling airflow and keep power wiring clear of the receiver/antenna installation

## Receiver tray

File: `receiver_tray.stl`

- overall: **62 × 44 × 9**
- profile: **STRUCT_LIGHT**

Use foam/dual-lock/strap restraint as appropriate for the chosen receiver. Keep antennas away from EDF/ESC high-current wiring and carbon shadowing where practical.

## BEC tray

File: `bec_tray.stl`

- overall: **58 × 38 × 9**
- profile: **STRUCT_LIGHT**

R3.1 expects a separate BEC with enough current margin for both sweep servos plus flight controls.

## EDF retaining rings

Files:

- `edf_ring_L.stl`
- `edf_ring_R.stl`

- outside diameter: **72**
- clear housing opening: **56**
- thickness: **10**
- profile: **DUCT**

A nominal “50 mm EDF” does **not** guarantee a 50 mm outer housing. Measure the purchased EDF housing before printing the final rings. Modify the generator if the real housing requires another fit diameter.

## Wing pivot / bearings

- wing-box envelope: **170 × 250 × 26**
- bearing pocket target: **10.2 mm**
- pivot shaft target: **5 mm smooth steel**
- recommended bearing: **5×10×4 mm**
- target quantity: **8** for a redundant/stiff bearing-supported assembly
- wing-root CFK tunnel: **6.4 mm**
- CFK tube target: **6 mm**
- sweep linkage hole in root: **3.2 mm** for M3-class linkage hardware

Print and test one bearing/doubler/spacer set before committing to the entire airframe.

## Research basis

Public reference comparison and source links are recorded in [REFERENCE_RESEARCH.md](REFERENCE_RESEARCH.md). No third-party STL geometry is copied into R3.1.
