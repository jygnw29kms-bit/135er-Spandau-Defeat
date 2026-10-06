# Engineering continuation - 6 October 2026

Status: **CAD/engineering development only - not print released, not flight released.**

## Native Fusion progress

The Fusion control bridge was repaired and verified after a startup failure caused by a UTF-8 BOM in the add-in JSON configuration and a stale dynamic-reload hash lookup. The active bridge now reports revision `v24_restartable_event_bridge` and a matching loaded/executed source hash on controlled builds.

Completed native Fusion artifacts:

- **v08** - Grumman/NASA source-wing loft review, 900 mm source span.
- **v10** - source-wing spar packaging review. Upper/lower carbon caps and shear webs are completely contained inside both native wing solids. Structural capacity, bond, buckling and continuous skin clearance remain unverified.
- **v14** - normalized source-section gallery for topology review.
- **v15** - native solid-envelope wing segmentation. Four envelope segments were generated and their span boundaries verified. All four fit the assumed 240 x 240 x 250 mm usable P2S envelope. These are still solid envelopes, not printable hollow shells.
- **v16** - source pivot / sweep datum review. No mechanical pivot is released.

## v15 numerical split gate

The first v15 native BRep split failed a 1 ppm volume-conservation threshold. Diagnostics showed each original wing at 210.425378665 cm3 and each split sum at 210.426217886 cm3, a +0.000839220 cm3 difference (3.988 ppm). The audit gate was changed to a documented 10 ppm ShapeManager split-volume tolerance and now stores delta, relative error and tolerance explicitly. Both sides pass this numerical gate.

This change does **not** relax geometric span-boundary checks. All four segment boundaries are independently verified against the defining WBL split.

## Pivot datum gate

A Naval Air Development Center 1/12-scale F-14 report (`NADC-81293-60`, accession `AD-A124468`) lists model pivot coordinates FS 43.68 in and BL 8.92 in. Scaling those model coordinates by 12 gives full-scale FS 524.16 in and BL 107.04 in. At the current source-wing scale this corresponds to model coordinates approximately X=613.132 mm and |Y|=125.209 mm in the unshifted aircraft FS/BL system.

The previous project pivot `(456.5 mm, +/-131 mm)` is therefore retired as a production datum.

However, rotating the NASA/Grumman 20-degree source-wing planform about the NADC source pivot yields a calculated 68-degree planform span of approximately 559.19 mm, while published F-14 68-degree span is about 38 ft 2 in (roughly 536 mm at this project scale). The conflict is now an explicit geometry gate rather than being hidden by the old provisional pivot.

No physical pivot boss, bearing stack, synchronizer or wing box will be frozen until:

1. the exact pivot datum is cross-checked against a second dimensional source or original station drawing;
2. pivot waterline / bearing vertical stack is established;
3. the fixed glove/body geometry is registered in the same FS/BL/WL coordinate system;
4. the 20-68 degree body/glove clearance is checked using native geometry.

## Propulsion benchmark

A provisional packaging/performance benchmark has been recorded in `analysis/propulsion_baseline_v17.json`:

- 2 x QX-MOTOR QF2611 50 mm 12-blade 4000KV 4S EDF, published mass 76 g each;
- published 4S test point: 34 A, 550.8 W, 950 g static thrust per unit at 16.2 V;
- 2 x 40 A ESC minimum published recommendation;
- Tattu Classic 4S 1800 mAh 75C benchmark battery: 202 g, 106 x 36 x 25 mm.

These values fit the current mass budget, but all thrust/current/thermal values remain **bench-test gates**. Final ducts and printed mounts can materially change installed thrust and current.

## Current release blockers

- authoritative full-airframe outer mold line is not frozen;
- fixed glove/body datum and pivot WL are unresolved;
- no validated mechanical sweep mechanism or hard stops;
- no wing-box torsion/contact/bearing analysis;
- no hollow printable wing/fuselage shells or verified joints;
- no slicer mass / wall / support validation;
- no final CG and swept stability envelope;
- no final EDF duct integration or measured installed propulsion data;
- no physical coupon, pivot, wing-box, battery-restraint, vibration or thermal tests.

## Next controlled CAD sequence

1. reconcile pivot datum and 68-degree span conflict;
2. register fixed glove/body geometry to FS/BL/WL;
3. construct metallic pivot/bearing reference stack and central wing-box load path;
4. run native 20-68 degree sweep collision envelopes;
5. integrate actual EDF, ESC and battery service envelopes;
6. generate hollow FDM wing shells around the validated carbon load path;
7. build joining lips/ribs/fastener access and verify P2S slicer fit;
8. update mass properties and CG before fuselage production segmentation.
