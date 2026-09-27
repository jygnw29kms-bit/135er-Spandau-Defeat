# R3.1 engineering reference research

This document records **public specifications and engineering principles only**. No third-party commercial STL geometry is copied into this project.

## 1. 3D-printed twin-50 mm F-14 reference

Public Cults3D information for the 1050 mm-span F-14 v2.2 reports:

- span 1050 mm unswept / 620 mm swept
- length 1020 mm
- flying weight about 1.32 kg with 4S 3300 mAh
- twin 50 mm 4S EDF, quoted combined thrust about 1.6 kg
- four 9 g servos, with high torque recommended especially for wing sweep
- eight 6x12x4 mm bearings
- 6 mm carbon tube reinforcement
- 6x1 or 5x1 mm carbon strip reinforcement
- separate left/right wing-sweep servo mount files
- separate battery tray, main spar, spar inserts, fan covers and taileron bearings

Reference:
https://cults3d.com/pt/modelo-3d/diversos/f-14-rc-aircraft-twin-50mm-fan-960mm-span

**R3.1 takeaway:** separate serviceable sweep-servo mounts, carbon reinforcement, real bearing/pivot hardware and modular fan/electronics access are proven concepts for this size class.

## 2. Freewing 64 mm F-14 reference

Freewing's current 1/15 F-14 is approximately 1217 mm long and 1250 mm span, with twin 64 mm EDF, a 6S 4000-5000 mAh pack, retracts and multiple digital metal-gear servos.

Reference:
https://www.freewing-model.com/freewing-f-14-tomcat-twin-v2-64mm-edf-jet-arf-plus-fj11421ap-rc-airplane.html

Motion RC identifies a Freewing 23 g smart metal-gear servo as used on the 64 mm F-14 swing wing. Published dimensions are approximately 28.5 x 13.5 x 30 mm.

Reference:
https://www.motionrc.com/eu/products/freewing-23g-metal-gear-smart-servo-with-200mm-6-lead-fss33232

A higher-torque Freewing 23 g coreless metal-gear servo uses essentially the same package class (28.3 x 13.0 x 33.4 mm) and is specified up to 8.0 kgf.cm at 6 V.

Reference:
https://www.freewingmodel.com/654.html

**R3.1 takeaway:** primary sweep-servo openings are sized to the compact 23 g class, with separate standard-servo adapter plates rather than weakening the wing box with an oversized universal cutout.

## 3. Freewing 1550 mm F-14 reference

The larger Freewing F-14 uses:

- rigid aluminium wing-box construction
- carbon spars
- bearing-supported hardware
- twin EDF propulsion
- metal-gear control servos
- serviceable preinstalled wing sweep actuation

Reference:
https://natterer-modellbau.de/Freewing-F-14-Tomcat-upgrade-version-EPO-1550mm-PNP

Manual:
https://www.freewing-model.com/download/freewing-f-14-manual.pdf

**R3.1 takeaway:** the sweep pivot and central wing box are treated as primary structure. R3.1 therefore prioritizes PETG wall thickness, metal M5 pivots, CFK reinforcement and replaceable servo/pivot hardware over minimum printed mass.

## 4. Other 3D-printed EDF practice

3DLabPrint describes extensive internal structural reinforcement in its printed MiG-15 EDF design, while Eclipson's Inferno demonstrates practical 0.4 mm-nozzle EDF printing on a 200x200x220 mm-class printer.

References:
https://3dlabprint.com/shop/mig-15-fagot/
https://www.eclipson-airplanes.com/inferno

**R3.1 takeaway:** printed shells are not treated as the only load path. R3.1 combines printed structure with CFK and metal hardware.

## R3.1 design rules derived from the comparison

1. **Stability before weight.**
2. Dual independent sweep-servo mounts.
3. Compact 23 g metal-gear sweep-servo class as primary fit.
4. Optional standard-servo adapter plates.
5. 17 g metal-gear class taileron mounts.
6. M5 steel wing pivots.
7. 6 mm-class carbon reinforcement around wing/sweep structure where the final prototype allows it.
8. Thickened PETG wing box, pivot doublers and structural slicer profile.
9. Dedicated ESC, receiver and BEC trays.
10. EDF retaining rings sized to the actual fan housing, not merely the nominal rotor diameter.
11. All generated parts must pass watertight, winding and P2S-volume checks before release.
12. Physical CG, sweep load, thrust/current and flutter tests remain mandatory before flight release.
