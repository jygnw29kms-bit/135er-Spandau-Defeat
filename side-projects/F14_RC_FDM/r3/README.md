<p align="center">
  <img src="assets/header.svg" alt="F-14 R3.1 naval aviation RC FDM project banner" width="100%">
</p>

# F-14A Tomcat RC FDM — R3.1 Stability Build

> **135er Naval Aviation Lab** — scale-reconstructed F-14A RC model for FDM printing on the Bambu Lab P2S.  
> Independent side project: **not part of the Spandau Strike / Source 2 build.**

## Mission profile

| Item | R3.1 target |
|---|---:|
| Scale | approx. 1:20 |
| Length | 955 mm |
| Extended span target | 977.5 mm |
| Power | Twin 50 mm EDF |
| Battery | 4S 3300–4000 mAh |
| Printer | Bambu Lab P2S, 256 × 256 mm |
| Material | PETG |
| Printable STL parts | **50** |
| STL incl. assembled reference | **51** |
| Individual 3MF incl. assembly | **51** |
| Optimized P2S plate 3MF | **25** |
| Combined plate STL previews | **25** |

The exterior is reconstructed from the supplied F-14A plan and published overall aircraft dimensions. Public RC/FDM models are used only as engineering references for structure, electronics packaging and proven mechanisms. This is **not Grumman OEM CAD**.

## R3.1 design rule: stability before weight

R3.1 deliberately shifts the project toward a more robust RC structure:

- 2.8 mm nominal fuselage shell geometry
- 170 × 250 × 26 mm truss-style structural wing box
- 5 mm steel pivot shafts
- 10.2 mm bearing pockets sized for 5×10×4 mm bearings
- 6.4 mm internal spar tunnels for 6 mm CFK tube
- dual independent wing-sweep servo mounts
- dedicated 23 g-class metal-gear sweep-servo fit
- optional standard-servo adapter frames
- dedicated 17 g-class taileron servo mounts
- separate ESC, receiver and BEC trays
- reinforced battery tray
- 56 mm EDF-housing retaining-ring opening
- structural PETG profile: 8 walls / 55% infill / 0.16 mm

See [ELECTRONICS_MOUNTS.md](ELECTRONICS_MOUNTS.md) and [REFERENCE_RESEARCH.md](REFERENCE_RESEARCH.md).

## 3D viewer

GitHub can display the generated STL files directly:

- [Full assembled F-14 R3.1 — GitHub 3D viewer](stl/F14_R3_assembled_reference.stl)
- [Structural wing box](stl/wing_box.stl)
- [Left wing root](stl/wing_L_root.stl)
- [Right wing root](stl/wing_R_root.stl)
- [Left intake](stl/intake_L.stl)
- [Right intake](stl/intake_R.stl)

The assembled STL is a visualization/fit reference. Print the individual files or prepared P2S plates.

## P2S release package

The automated build generates:

- `stl/` — **50 printable STL parts + assembled reference**
- `p2s/individual_3mf/` — **51 individual 3MF files including assembly**
- `p2s/plates_3mf/` — **25 optimized P2S plate 3MF files**
- `p2s/plate_stl/` — **25 combined plate STL previews/fallbacks**
- `p2s/plate_manifest.csv` / `.json` — contents and planning-time estimates
- `p2s/profiles.json` — strength-first PETG profile families
- `docs/mesh_validation.*` — automated mesh validation
- `scad/generated_parts/` — generated OpenSCAD source for every printed part

The wing box and wing sections use native OpenSCAD CSG for critical structural cut-outs, bearing bores and CFK channels.

## Validation gate

Current R3.1 GitHub build:

- **50 / 50** printable STL parts watertight
- **50 / 50** winding-consistent
- **50 / 50** fit the P2S build volume
- **25 / 25** optimized plate layouts pass P2S bounds validation
- failed geometry checks: **0**
- current planning-time estimate: **~81.85 h**

Planning time is geometry/profile based. Exact P2S time must be obtained by slicing the 3MF files with the real PETG filament profile.

## Build documentation

- [RC assembly and hardware](BUILD_PLAN.md)
- [Electronics and servo mount dimensions](ELECTRONICS_MOUNTS.md)
- [P2S plate plan](PRINT_PLATES.md)
- [Reference research](REFERENCE_RESEARCH.md)
- [Validation status](STATUS.md)

---

### Deck status

**R3.1 geometry: GREEN**  
**R3.1 P2S package: GREEN**  
**Electronics mount package: GREEN**  
**Physical flight validation: PENDING**
