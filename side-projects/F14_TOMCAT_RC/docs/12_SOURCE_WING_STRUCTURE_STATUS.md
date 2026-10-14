# Source-wing structure status — 14 October 2026

Native Fusion results are archived under cad/fusion/source_review. These are engineering review artifacts, not a complete or print-released aircraft.

| Review | Executed result | Remaining limit |
|---|---|---|
| v10 source spar | Six cap/web envelopes inside original wing solids | Containment alone does not prove skin gap or strength |
| v54 hollow shells | Right inside-shell at 0.8 mm, mirrored left; valid solids | No segment joints or manufacturing qualification |
| v57 hollow segments | Four valid material solids fit the assumed print envelope | Strict 10 ppm volume gate fails at 10.75031 ppm; numerical measurement consistency is documented separately |
| v58 native distances | Minimum 0.188973 mm | Nominal 0.2 mm gap fails |
| v59 inward caps | Cap copies shifted inward 0.03 mm; minimum gap 0.218958 mm | Web interfaces initially unchanged |
| v62 trimmed webs | Temporary BRep differences fit webs to shifted caps; twelve gap checks pass | Bond transfer, buckling and load capacity unverified |
| v63 section screen | Seven defining-station rectangle properties; root cap-only I 958.4402 mm4 | Continuous native section stiffness and actual material properties unverified |

The root-only bending screen uses an assumed 250 mm resultant arm and gives 89.721 MPa for 1.05 kg, 8g and 70 percent side loading. The 1.2 kg sensitivity gives 102.538 MPa. Neither is a strength qualification: bonded cap/web behavior, compression buckling, pivot loads, torsion, outer-tip load transfer and print joints remain open.

Next geometry work is the segment connection and alignment system while retaining continuous cap load paths across the shell split. A registered original fuselage and fixed glove are still required before integrating the pivot mechanism. The v42 analytic fuselage remains excluded from original-exterior release; see the provenance gate.

No final STL/3MF, slicer, structural or flight release exists.


Native span-load sensitivity v66 uses the 17 executed v65 cap sections, Y150..405 mm. A uniform load over the full root-to-tip panel (Y148.8263775..450 mm) gives sampled peak stress screens at Y150: 29.0272 MPa (1050 g, 6g, 50% side share), 54.1842 MPa (1050 g, 8g, 70%), and 33.1740 / 61.9248 MPa at 1200 g. Only the cap centroid parallel-axis contribution is credited; local profile inertia, web and skin stiffness are excluded. The 1 mm cap thickness and uniform cap modulus remain assumptions. Checks cover an independent parallel-axis identity, native cap X alignment and the uniform-load moment identity.

These values differ from v63 because uniform loading places the resultant about 150.6 mm from the root; v63 assumed 250 mm. Neither loading is validated by aerodynamics. Seventeen samples do not prove continuous capacity. Sweep/torsion coupling, shear, root attachment, the unsupported outer-tip load path, bonding, buckling and material allowables remain unverified. This is a load sensitivity calculation, not Fusion Simulation or a strength/print release.
