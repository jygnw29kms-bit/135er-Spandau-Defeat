# Engineering continuation - 4 October 2026

The aircraft is **not print-ready or flight-released**. This update contains an
executed preliminary beam finite-element calculation and source audit. It contains
no new Fusion solid, full-airframe FEA, CFD, or verified aircraft STL/3MF.
The v04 F3D archive remains the latest CAD artifact. Baseline commit: `37c16f7`.

## Geometry findings

- The inherited 48 ft 2 in swept-span figure gives 676.463 mm. NASA SP-4519
  gives 38.2 ft, corresponding to 536.489 mm at the current scale. The existing
  four-corner wing planform rotated from 20 to 68 degrees about its `(456.5,131)`
  mm pivot gives **546.658 mm**. This is a planform calculation, not a whole-aircraft
  collision check. Reconcile the 10.169-mm discrepancy with a dimensioned full-scale
  swept plan view. The 676.463-mm parameter is not a verified production dimension.
- `upc_section_profile` generates assumed superellipse/teardrop and Gaussian
  twin-lobe sections. These are not digitized original station profiles. Only
  16 of 30 stations are lofted, plus unverified nose/tail closures.
- The NASA plan trace doubles back near wings/tail and needs visual cleanup.
  Whole-aircraft silhouette extrema cannot identify every local fuselage section.
- UPC drawings describe a reproduction of the internal structure, with 3-mm
  structural pieces and some undimensioned splines. Its frames must not automatically
  be equated to original full-scale exterior skin geometry.
- Stabilators and fins remain constant-thickness extruded plates. Original airfoil
  sections, fin cant, stabilator incidence/pivots and nozzle/beavertail details
  remain unresolved.
- Many geometric dimensions are numeric constants rather than expressions linked
  to Fusion user parameters; changing a parameter does not necessarily update solids.
- NASA Fig.4 yields 868.497-mm airframe length; Navy overall length scales to
  about 880.1 mm; the UPC-derived station baseline is 879.284 mm. Reconcile
  nose/boom/tail datums before imposing a global rescaling.

## Executed structural screening

Reproduce with Python plus numpy: `python analysis/structural_screen.py`.
Inputs: 1.05-kg AUW, 319-mm cantilever span, concentrated lift at 250 mm,
rigid root clamp, no printed-skin stiffness credit. Carbon modulus 70 GPa,
allowable 350 MPa and density 1600 kg/m3 are **sensitivity assumptions**, not
certified or measured properties.

Sixteen tube/load combinations were solved: 6/4, 8/6, 10/8 and 12/10-mm tubes
under 3g, 6g, 8g and asymmetric 8g with 70% load on one wing. Meshes of
16/32/64 beam elements agree with closed-form deflection and root equilibrium.

| Tube | 6g stress MPa | 6g predicted tip deflection mm | Assumed allowable/stress |
|---|---:|---:|---:|
| 6/4 | 453.826 | 63.662 | 0.771 |
| 8/6 | 224.752 | 23.646 | 1.557 |
| 10/8 | 133.237 | 11.214 | 2.627 |
| 12/10 | 87.925 | 6.167 | 3.981 |

Large deflections invalidate the linear small-deflection assumption for several
cases; those values indicate rejection and are not accurate nonlinear predictions.
Tip nominal thickness is 4.903 mm. With two 0.8-mm skins, maximum nominal
internal height is 3.303 mm. None of these full-span constant-diameter tubes fits.

### Candidate tapered carbon-cap spar

Two 16 x 1-mm caps per wing, with an assumed continuous shear web, give a
nominal cap centroid separation taper of 11.889 to 2.303 mm. Carbon caps alone
weigh 32.666 g for both wings; glue, web, root fittings and reinforcement are extra.

| Load | Cap stress MPa | Tip deflection mm |
|---|---:|---:|
| 3g | 21.924 | 2.388 |
| 6g | 43.848 | 4.777 |
| 8g | 58.463 | 6.369 |
| 8g, 70% high side | 81.849 | 8.917 |

32/64/128-element solutions converged; 64-to-128 deflection change is 0.0114%.
An independent virtual-work integral agreed within 0.5%; force/moment equilibrium
passed. This is a **sizing candidate**, not a CAD-validated or manufactured spar.
Actual placement must use upper/lower airfoil ordinates across the full cap width,
not nominal maximum airfoil thickness. Full shear transfer is assumed. Bond failure,
web compliance, compression/buckling, torsion, pivot compliance and skin joints
are excluded and may govern failure. No flight safety factor is established.

Battery restraint remains 43.149 N at 220 g and 20g forward acceleration.
Total vertical design forces are 61.782 N at 6g and 82.376 N at 8g.

## Access limitations and required continuation

Fusion is running with `F14_Tomcat_RC_4S_900mm*` and Personal Use licensing.
Two native captures failed: `FrameArrived timed out` and `window capture timed out`.
Window enumeration/accessibility reads work, but the 3D canvas and meaningful CAD
toolbar controls are not exposed. The Scripts shortcut yielded no readable dialog.
No blind geometry edits or claimed Fusion simulation runs were made.
Autodesk documents that Personal Use excludes Simulation; no paid license or tokens
were purchased.

Required next work: restore usable Fusion capture/script execution; reconcile datums
and original station geometry; build OML-faithful surfaces; implement tapered spar,
metallic pivots, wing-box, synchronized sweep/stops; verify 20-68-degree clearances;
integrate actual EDF/ESC/servo/battery parts and ducts; establish swept CG/stability
envelope; solve joints, contact, shells, buckling and torsion with a capable solver;
segment for the verified P2S profile; check mesh, walls and sliced masses; then
complete the physical material, structural, propulsion, thermal and control tests
in `08_VERIFICATION_GATES.md`. All these steps remain open.

## Sources

- [NASA CR-163098, Fig.4](https://ntrs.nasa.gov/api/citations/19800024842/downloads/19800024842.pdf), locally read and visually inspected.
- [NASA SP-4519 specifications](https://www.nasa.gov/wp-content/uploads/2023/04/sp-4519.pdf), swept-span search excerpt; the web reader could not fetch the full PDF because of its size.
- [Navy Museum F-14A specification](https://www.history.navy.mil/content/history/museums/nnam/explore/collections/aircraft/f/f-14a-tomcat.html), conflicting swept-span entry.
- Supplied `UPC_F14_Drawings.pdf`, introduction and assembly side drawing; supplied UPC structural report.
- [Autodesk Personal Use exclusions](https://help.autodesk.com/view/fusion360/ENU/?caas=caas%2Fsfdcarticles%2Fsfdcarticles%2FFusion-360-Free-License-Changes.html).
