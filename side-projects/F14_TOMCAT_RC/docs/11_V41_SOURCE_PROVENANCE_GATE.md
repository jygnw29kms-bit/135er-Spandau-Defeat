# v41 exterior provenance gate — 13 October 2026

The installed add-in reports a completed v41 packaging run, but its original-aircraft exterior has not been validated. The recovered v37 generator explicitly calls build_upc_fuselage_oml and names the result REF_UPC_FUSELAGE_OUTER_OML_v37. That generator still uses analytic pear and twin-lobe sections previously excluded from production exterior work. The v41 containment result therefore cannot establish fit inside the original F-14 exterior.

The v37 patch source SHA256 is cde2cdc6b76e93ead36028a13650380e6188c2584ffa726244d1be68b6149967. The v41 installed-source checkpoint SHA256 is 4299e7f5fd1087a92e28402d7b8f80a654eeac804594d9e786a482633d82a575. Local checkpoints preserve both files. The installed checkpoint lacks the v37 rebuild function; preserve native archives before any cold rebuild.

The native v41 audit itself reports fully_packaged=false. Its best candidate has minimum crank containment 0.4082300524, while rod and slider containment are 1.0; these values apply only to the provisional reference solid. No mechanical, print or flight release follows.

Next work must reconstruct and register the original A–F body sections and fixed glove, then repeat all moving-part and skin-clearance checks against that source-based exterior. Preserve the v41 kinematics as a candidate, without modifying the original exterior to accommodate it.
