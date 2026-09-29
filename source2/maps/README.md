# Source 2 maps

All 20 maps are in active Source 2 / CS2 map production.

## Canonical roster

- rathaus_spandau
- zitadelle
- staaken
- rodelberg
- kiesteich
- falkenhagener_feld
- lynarstrasse
- wroehmaennerpark
- freiheit
- martin_buber_schule
- askanier_schule
- b_traven_schule
- fort_hahneberg_1945
- teufelsberg_coldwar
- flugplatz_gatow_1945
- gatow_luftbruecke_1948
- radeland_1945
- hakenfelde_heeresamt_1944
- zitadelle_1945
- britischer_sektor_spandau

## Current technical state

- 20 / 20 VMAP geometry builds exist locally.
- 20 / 20 exact-LoD2 integration builds exist locally.
- 20 / 20 DGM terrain-reference VMAPs are generated and Valve-DMX-valid.
- Rathaus Spandau is the gameplay/reference map.
- Gameplay v2 + NAV seeds are generated and Valve-DMX-valid for the other 19 maps.
- The 19 staged gameplay builds are not yet promoted over the active sources because the current command-line runtime compiler is blocked by the Workshop-Tools/Steam graphics context.

Per-map production intent and A/B/C layout notes remain in `specs/`.
