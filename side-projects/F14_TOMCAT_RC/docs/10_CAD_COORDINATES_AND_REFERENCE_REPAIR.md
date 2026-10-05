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
