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
