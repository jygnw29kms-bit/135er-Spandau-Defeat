# CAD coordinates and NASA contour repair — 2026-10-04

The user confirmed that v05 is now visibly horizontal in Fusion. Aircraft coordinates are X longitudinal, Y lateral and Z vertical. The builder selects Z-up before creating its document and maps global model points into each sketch. Signed extrusions account for the construction-plane normal. The camera is set before archive export.

The saved active Fusion snapshot contains the confirmed orientation. It remains a provisional, solid approximation, not a printable or flight-qualified airframe.

## Rejected reference interpretation

The old NASA side trace started at pixel (1179,329), on the waterline annotation. Its longitudinal scale used 1179−196 pixels instead of the actual 26.19 cm dimension extension lines at approximately x=195 and x=1036. Correcting this changes the axial millimetres-per-pixel factor by 16.8847%. This error concerns the side reference sketch; the existing fuselage loft uses separate UPC-derived station numbers and has not been corrected by this change.

The old plan outline also doubled back through internal wing details and included a dimension extension. It is superseded by five separate, manually digitized contour candidates in `NASA_F14_reference_trace_v06.json`.

## v06 reference candidates

The data separates the plan assembly silhouette without wings, each wing silhouette, side airframe silhouette without vertical tail, and side vertical tail. Plan calibration uses the nose-to-tail and wingtip-to-wingtip vectors to account for scan skew. Side calibration uses the printed airframe-length and vertical-tail-above-waterline dimensions. The drawing represents a 1/72 wind-tunnel model. Scale here remains 900 mm open span.

The raster overlay was inspected visually. All five polygons have unique vertices and no proper segment self-intersections. The assumed digitization uncertainty is three pixels, not a certified source tolerance. The assembly silhouette contains stabilator and nacelle projections and must not be used directly as a fuselage half-width function.

`build_reference_model_v06` creates a separate Fusion reference document and archive; it does not overwrite the existing approximation or infer 3D cross-section shapes from silhouettes. Its native execution remains pending until the updated add-in is loaded. Python syntax checks pass.

## Remaining exterior work

Verify the actual fuselage sections, canopy, inlet ramps, nacelles, nozzles and beavertail against the reference sources. The current rounded/pear/lobed section formulas are engineering guesses and cannot establish original exterior fidelity. Separate those components before designing print shells. Reconcile NASA airframe length with Navy overall-length datum and swept-span discrepancy.

No production STL/3MF is released from this provisional geometry.

## Cross-section source audit

The actual `UPC_F14_Structure_Report.pdf` has 85 PDF pages. The older `UPC_F14_Report.pdf` text extraction contains a server security interstitial and must not be used as engineering evidence.

PDF page 31 (printed page 19), Figure 3.15, contains the three-view drawing with section letters A–F. Its embedded raster is 2113 × 2953 pixels and was extracted at its native resolution for further section tracing. This is a reproduced third-party blueprint, cited as reference [37], rather than an original factory station drawing. Its station marks must be registered to the NASA length and waterline datums before sections are lofted.

PDF pages 42–43 (printed pages 30–31), Figures 5.5–5.11, compare seven source section examples with the thesis CAD sections. They show the transition from a circular nose section through a canopy-bearing forward section to the inlet/glove region, separate engine lobes, and separate aft circles. Those topology changes are not represented by the current single rounded/lobed loft.

PDF page 44 (printed page 32) explicitly explains that the cockpit top was omitted from the structural model. The same passage describes manually fitted spline profiles and reconstructed sections where plan cuts were unavailable. PDF page 62 (printed page 50) notes that the lateral structural representation differs because the skin is absent and crossbeam placement does not follow its shape closely. Consequently the 30 thesis structural sections cannot be accepted directly as the aircraft outer skin.

Next exterior step: trace the available source sections, preserve separate canopy and engine components, and register section-letter stations against the orthographic views. Record any interpolation as provisional, rather than asserting original factory geometry.

## Native execution and section candidates — 2026-10-05

Fusion successfully generated `F14_Tomcat_RC_v06_NASA_REFERENCE_REVIEW.f3d` and its native viewport image on 2026-10-05. The exported plan image was inspected. It contains five reference sketches and no completed airframe body. The installed controlled event handler also exported an active snapshot. The previous pending-native-execution limitation is resolved for this reference document only.

Seven manually digitized contour loops from the original image in Figure 3.15 are recorded in `analysis/upc_source_section_candidates_v07.json`: A–E and the two engine contours at F. Source axis origins are retained, including the common aircraft axis for the F pair, so canopy height and nacelle lateral separation are not lost by independently recentering each loop. All loops passed a proper segment-crossing check. The overlay was inspected against the embedded source raster.

The station fractions are candidates read from the lower side-view A–F marks. They are not original factory station dimensions. The profiles remain dimensionless and unregistered. Applying a common pixel scale to the separately drawn section views is prohibited; the profile sizes and axis/waterline positions must first be reconciled with the calibrated orthographic envelopes. Section C includes projected intake edges and needs separate opening and outer-skin topology. Thin fin/wing projections have not been included in the two F nacelle loops.

Additional primary-source geometry evidence: [NASA CR-3992](https://ntrs.nasa.gov/api/citations/19880019510/downloads/19880019510.pdf), printed page 17 / PDF page 24, describes NASA Langley's digitized one-tenth-scale F-14 cross sections, including nacelles and the wing-pivot glove. Figure 48, printed page 81 / PDF page 88, shows those sections in an oblique view. The report notes minor deviations from the production aircraft. Figure 49 deliberately simplifies the geometry by filling the space between nacelles and blending the inlets into the nose for the flow code; it must not be used as the original outer skin. No directly usable fuselage coordinate table was found in the inspected passage or figure. The oblique drawing alone does not supply a calibrated station-coordinate dataset.

## Original defining wing sections and native v08 CAD

NASA CR-3992 Appendix 2 provides the **basic Grumman wing** at 20° leading-edge sweep: eight defining WBL stations with 50 paired upper/lower ordinates each, leading/trailing FS values and reference vertical WL. These tables already incorporate incidence. The later Mach 0.8/0.7 experimental glove tables were excluded.

`analysis/extract_nasa_basic_wing.py` extracts the basic table and fails on missing rows, unequal paired chord coordinates, non-monotonic chord stations or reversed thickness. Eight OCR corrections were individually checked against enlarged PDF table crops, including lost negative signs, a lost decimal point and a space in WBL 311.15283. The source PDF hash and corrections are retained with the extracted data.

Fusion generated two solid wing bodies from all eight defining sections and exported `F14_v08_GRUMMAN_BASIC_WINGS_SOURCE_REVIEW.f3d`, a native bounds audit and a viewport image. The image was inspected. At the chosen 900 mm span, the root defining WBL is ±148.8264 mm, the tip is ±450 mm, and the root-to-tip panel length is 301.1736 mm. The source full span is 19542.75746 mm, slightly different from the museum dimension used in the earlier scale baseline. Root chord is 147.9312 mm and tip chord 51.7768 mm. Maximum tabulated thickness is 14.2739 mm at the root and 4.6361 mm at the tip.

The wings retain aircraft FS/WBL/WL coordinates. The nose FS datum and body-relative WL transformation have **not** been verified, so these wings are not yet integrated into the provisional fuselage. Between the defining sections Fusion interpolates the loft; that interpolation and component integration need verification before release. The existing 319 mm panel-span structural screen and CST wing geometry must be revisited against this source dataset. No production print shell is exported.

The controlled CAD request interface includes a fixed `build_project_revision` entry point for subsequent installed source revisions. It reads only the installed project module at a fixed path and accepts no request-supplied code, file path or shell command. Installing/loading that interface revision remains distinct from its later native execution.

## Aircraft nose datum and excluded transonic body model — 2026-10-05

The original US Navy *Airman*, NAVEDTRA 14014, Chapter 4 page 4-7 / Figure 4-7, states that the F-14 aircraft FS origin is 93.0 inches ahead of the nose. The reproduced primary-document passage is available [here](https://navyaviation.tpub.com/14014/css/Fuselage-Station-Diagram-Of-An-F-14-Aircraft-79.htm). NASA CR-172559 Table 1 independently starts the nose geometry at FS 93.0. This resolves the longitudinal datum: at the source-wing scale, translate aircraft FS coordinates by −108.7861 mm to put the nose at model X=0. The defining wing root leading edge then lies at X=479.4839 mm. The actual v08 archive still retains its original absolute FS coordinates; no native translation has been claimed.

`F14_aircraft_datum_v09.json` records the verified longitudinal mapping. Its vertical reference remains null; a guessed WL offset must not be silently applied. The A–F source-section file records candidate FS positions derived from its side-view station marks and the Navy nominal overall length. Those section positions still require verification of the blueprint's aft datum and section sizes/waterline, so `scale_verified` remains false.

NASA CR-172559's main geometry description explicitly says its fuselage/nacelle model is based on a 1/40-scale line drawing. It does not exactly represent the aft nacelle/pancake region, because the quick-geometry code requires a single-valued radius; the inlet face is covered with a modeled ramp. These numerical body tables must not be treated as an original production outer-skin dataset. The report distinguishes manufactured wing contours from the alternative Appendix A wind-tunnel Wing 7 shape. Only the former basic-wing definition is applicable here.

The new defining panel span of 301.1736 mm does not by itself establish the pivot-to-tip structural cantilever length. A pivot inboard of the first defining WBL would add the intervening distance. Reassess the structural geometry once the actual pivot and glove interface are registered; do not simply replace the earlier 319 mm cantilever with the shorter source-panel span.

## Cross-view section registration diagnostic - v09

`analysis/section_registration_audit.py` now intersects the calibrated NASA plan and side polygons at all seven UPC candidate sections. It retains all intersection intervals and uses a half-open edge convention checked against a rectangle, an exact vertex and a concave shape with disconnected intervals. Station fractions map into the NASA raster's own 868.4967 mm length; the production-aircraft inch scale is not silently mixed with this wind-tunnel drawing.

The forward A and B section aspect ratios closely agree with the projected views: A has a 62.07 mm projected width and 65.10 mm height; B has 77.56 mm width and 106.86 mm height. Isotropic fit candidates preserve each original section's aspect ratio and record height mismatch and the source-axis translation. No independent vertical stretching is applied. These are numerical registration candidates, with unverified cross-source station pairing and waterline; they are not a verified outer skin or native CAD execution.

The aft sections expose why a global fit is invalid. At F the plan assembly spans 357.44 mm, including the stabilator projection, whereas each F contour is an individual nacelle. Scaling each nacelle to that full width would grossly enlarge the rear fuselage. C-E also disagree in aspect ratio; projected glove, canopy and ventral-fin contributions and unverified station pairing are candidate causes that require checking against component-specific contours. The generated audit explicitly prohibits production lofting for every candidate. The next reconstruction step is component-specific aft contours and station pairing, rather than forcing those silhouettes into one body.

## Source-wing internal packaging screen - v09

`analysis/source_wing_internal_fit.py` replaces reliance on the obsolete CST shape for local packaging decisions. It uses all eight published basic-wing sections. Segment-distance checks account for nearby sloping boundaries when fitting a circular tube; rectangular cap bounds include normal offsets of 0.8 mm skin and 0.2 mm assembly clearance. Independent rectangle, normal-distance and endpoint-distance checks pass. These are section packaging computations, not structural FEA or a continuous-span collision check.

At the defining tip, a circle centered at the mid-ordinate at 30% chord admits only 2.4484 mm outside diameter. Searching mid-ordinate centers at 0.5% chord intervals from 15% to 60% gives a sampled maximum of 2.6256 mm at 40% chord. This sampled search is not proof of a globally optimal circle. None of the screened 4/6/8/10/12 mm tubes fits at the tip at 30% chord; section-by-section fit elsewhere does not establish that a straight tube fits the swept/twisted loft.

The earlier 16-to-8 mm width, 1 mm thick cap pair at 30% chord fails at the tip: the caps overlap by 0.2059 mm after the skin/clearance offsets. Eighteen variants covering 4/6/8 mm tip widths, 0.8/1 mm cap thickness and 30/35/40% chord do not retain the assumed 0.8 mm minimum web height at every defining section. Do not enlarge the original wing to conceal this packaging failure.

A candidate cap spar ending at the penultimate defining section, WBL 347.93726 / model Y=406.9971 mm, fits the retained seven defining sections with at least 1.5639 mm web height. It leaves a 43.0029 mm outer panel that needs a designed load-transfer termination and verified printed-tip strength. This is a packaging candidate only; continuous loft clearance, carbon bending, torsion, bonding, buckling and attachment strength remain unverified. No internal native CAD or print release has been claimed.

## Native spar construction prepared - v10

The installed Fusion add-in now includes `build_source_spar_review_v10()`. It creates a separate review document with the two original basic-wing lofts and six independent material-envelope bodies: upper cap, lower cap and web for each wing. Seven source stations define the truncated spar. Rectangle coordinates use the audited cap bounds in the same absolute FS/WBL/WL frame as v08; no unverified body waterline transformation is applied. It requires the matching source hash, station identities, positive section heights and eight resulting bodies before exporting a native archive and bounds/volume audit. The original source-wing design is retained.

The v10 source and its fit dataset have been installed; Python syntax validation passed. The controlled request `source-spar-review-20261005-1000` returned `Unsupported controlled CAD operation`, confirming that the running add-in still has the older event handler. Therefore **v10 native execution and all v10 native results remain unverified**. The prepared operation requires loading the updated add-in. No geometry, interference, simulation, material assignment or print readiness is inferred from syntax validation or installation alone.

## Outer-panel load-transfer sensitivity - v10

`analysis/source_wing_tip_loads.py` integrates three explicitly assumed spanwise distributions over the original defining panel: uniform, proportional to local chord, and elliptic over the full semispan. It assigns the entire wing-side load to this panel, omitting inboard glove/body lift. Uniform force and moment agree with closed forms; 4096/8192 interval refinement passes. These equilibrium integrations do not establish the real aerodynamic distribution.

With the 1.05 kg baseline and 8g 70/30 high-side load, the assigned force is 57.6631 N. Under the chord-proportional assumption, the 43.0029 mm outer panel carries 4.8333 N and introduces 0.09986 N m bending moment at the proposed spar termination. A separate bound that puts the entire assigned nonnegative force at the tip gives 57.6631 N shear and 2.47968 N m at that termination. The bound does not cover self-equilibrated loads or torsion.

Moments at the first defining WBL are not pivot loads: the unknown inboard lever arm must be added before assessing the attachment. The previous conservative 250 mm resultant-arm load cases remain applicable pending a verified load path. The new results provide explicit inputs for tip ribs and cap termination design; no printed-skin, adhesive, joint, carbon, buckling or physical proof-test capacity is claimed.
