# Berlin geodata -> Unreal Engine 5 map pipeline

This project uses official/open Berlin geodata to establish real-world scale and building massing before gameplay adaptation.

## Data priority

1. **Berlin LoD2 building model** — primary reusable geometry reference. Building footprints follow cadastral building outlines and generalized roof forms. License: Datenlizenz Deutschland – Zero 2.0.
2. **Berlin 3D Mesh 2025** — high-detail visual and spatial reference. Distributed as tiled OBJ + textures through the Berlin 3D download portal. Keep its original geometry/textures out of distributable game assets unless the portal terms explicitly permit that use.
3. **Esri Deutschland Berlin 3D scene** — interactive visual cross-check for building massing, roof orientation, terrain and neighborhood context. Viewer item: https://opendata-esridech.hub.arcgis.com/maps/50e8049abb5841dcb3c113210b2109fb/explore . Treat it as a visualization/reference layer; use the official Berlin LoD2 download as the geometry source of record.
4. **Terrain / streets** — use Berlin terrain data and OpenStreetMap context as alignment aids.

## School anchors


The three first targets are:

- Martin-Buber-Oberschule — Im Spektefeld 33, 13589 Berlin
- Askanier-Grundschule — Borkzeile 34, 13583 Berlin
- B.-Traven-Gemeinschaftsschule — Recklinghauser Weg 26 / Remscheider Straße 3, 13583 Berlin

## Extraction workflow

1. Open the Berlin 3D download portal and frame the site using the address/anchor in the site manifest. Cross-check the same footprint in the Esri Berlin 3D scene before extraction.
2. Select all mesh tiles intersecting the configured capture radius.
3. Download the OBJ tile ZIP archives and keep them under a local raw-data folder that is **not committed** to Git.
4. Obtain the matching LoD2 building geometry for the same footprint.
5. Import the mesh tiles into Blender without changing scale or orientation.
6. Verify the site anchor against the LoD2 building outlines and visible campus features.
7. Crop to gameplay context plus a safety margin.
8. Create a local origin near the campus center, while recording the georeferenced source position in the map spec.
9. Retopologize/rebuild playable architecture from the LoD2/mesh reference instead of shipping the dense city mesh as-is.
10. Export optimized geometry for Unreal Engine 5/Unreal Editor.
11. Build collision separately and keep decorative detail out of player collision.
12. Run Unreal Engine 5 validation: scale, routes, spawn safety, objectives, nav/bots, visibility and performance.

## Geometry rules

- Keep real-world campus proportions as the baseline.
- Cross-check LoD2 footprint, roof direction, relative height and surrounding block context against the Esri 3D scene before gameplay edits.
- LoD2 is a massing model: doors, windows, facade detail and small roof elements must be reconstructed from separate references rather than invented from the LoD2 shell.
- Gameplay edits are allowed for access, cover, routes and objectives, but should remain recognizable.
- Do not invent building footprints when LoD2 provides them.
- Treat 2025 mesh textures as reference material unless redistribution is explicitly allowed.
- Keep a per-map record of source tile IDs and extraction date once the portal selection has been made.

## Raw-data layout (local only)

```
raw_geodata/
  berlin_mesh_2025/<site-id>/<tile>.obj
  berlin_mesh_2025/<site-id>/textures/
  berlin_lod2/<site-id>/
```

Do not commit the raw 3D Mesh download archives by default. Commit only derived, license-safe project assets and metadata.


## Expanded Berlin source stack (research 2026-09-29)

Use the following layers together. No single dataset is authoritative for every visual feature.

| Priority | Dataset | What it contributes to Unreal Engine 5 reconstruction |
|---|---|---|
| A | Berlin LoD2 building model | cadastral building footprints, generalized roof forms and building massing |
| A | ALKIS Berlin buildings / parcels | exact present-day building/parcel geometry and cadastral alignment |
| A | ATKIS DGM 1 m | bare-earth terrain, slopes, embankments and elevation baseline |
| A | TrueDOP 2026, 20 cm | current ground truth for paths, curbs, roofs, courts, parking, vegetation edges and small site layout |
| A | Berlin 3D Mesh 2025 / Esri Berlin 3D scene | visual cross-check of facade massing, roof detail, trees and surrounding block context |
| B | ALS primary point cloud / DOM 1 m / bDOM 1 m | object heights, tree canopy, walls/structures and independent height validation |
| B | ATKIS Basis-DLM | topographic objects: transport, water, land cover and other landscape structure |
| B | Detailnetz Berlin | roads, paths, junctions, bridges/tunnels and traffic-level topology |
| B | Baumbestand Berlin | street trees and part of park-tree inventory |
| B | Grünanlagenbestand | official parks, green spaces and playground footprints |
| B | Gewässerverzeichnis | official water bodies / water network context |
| B | Sportanlagen WFS | public sports facilities; useful around school/sports maps |
| B | Denkmalkarte / Denkmalliste | protected landmark identity and historic structure cross-check |
| C | K5 1:5,000 | readable cadastral/topographic sanity check with parcel boundaries, names, numbers and actual-use areas |
| H | Historical aerial-photo portal 1928–1999 | era reconstruction and change detection |
| H | Aerial imagery 1938 1:4,000 | strongest pre-war visual baseline for 1944/45 maps where coverage exists |
| H | Städtebauliche Entwicklung / Gebäudeschäden 1945 | 1940 urban structure plus documented 1945 building-damage layer |
| H | Freiflächenentwicklung 1945–2020 | checks whether an area was built/open in the target era |
| H | West-Berlin aerials 1974/1979/1984/1989 | Cold-War reconstruction, especially Teufelsberg and British-sector context |

### Era rule

For a contemporary map, build the spatial baseline from **ALKIS + LoD2 + DGM + TrueDOP**, then validate heights with **ALS/DOM/bDOM** and visual appearance with the **3D Mesh / Esri scene**.

For a 1944/45 map, never back-date the current city by appearance alone. Start from the current georeferenced frame only for coordinates, then reconstruct the period footprint from **1938 aerial imagery + 1940/1945 historical layers + 1945 damage information + historical aerial-photo holdings**. Current LoD2/ALKIS geometry may only be retained for structures proven to have existed in the target period.

For Cold-War maps, use the closest available historical aerial year (1974/1979/1984/1989) as the spatial truth for buildings, compounds, roads and vegetation. Do not mix current structures into the period scene unless verified.

### Map-specific source emphasis

- **Rathaus / Zitadelle:** LoD2, ALKIS, DGM, TrueDOP, Denkmalkarte, historical aerials and 1945 damage/urban-development maps.
- **Staaken / Freiheit / Lynarstraße:** ALKIS, ATKIS, Detailnetz, DGM, TrueDOP; for 1945 versions add 1938 aerials and 1945 historical layers. ATKIS/orthophotos are also the rail/industrial alignment check.
- **Rodelberg / Kiesteich / Wröhmännerpark:** DGM + ALS/DOM are mandatory for terrain; add water, green-space and tree layers.
- **Falkenhagener Feld:** ALKIS + LoD2 + TrueDOP + 3D Mesh/Esri + Detailnetz + tree/green layers.
- **Martin-Buber / Askanier / B.-Traven schools:** ALKIS + LoD2 + TrueDOP + 3D Mesh/Esri; add sports-facility, green-space and tree data for grounds.
- **Fort Hahneberg:** DGM/ALS for earthworks first; LoD2/3D reference for surviving structures; historical imagery for period state.
- **Gatow 1945 / Gatow Airlift 1948:** historical aerial-photo holdings are primary for runway, apron, hangar and support-layout reconstruction; current geodata only anchors coordinates/elevation.
- **Teufelsberg / British Sector:** closest Cold-War aerial imagery is primary; current DGM remains useful for terrain.
- **Radelandstraße / Hakenfelde Heeresamt / Zitadelle 1 May 1945:** 1938 aerials + 1940/1945 urban-development/damage layers + historical aerial-photo archive before any current geometry is accepted.

### Accuracy / provenance gate

Each authored Unreal Editor map must eventually carry a small provenance manifest containing: source dataset name, source date/era, tile or feature IDs where available, CRS, extraction date, license, local-origin transform and whether each geometry group is **measured**, **historically reconstructed**, or **gameplay adapted**. This makes later corrections reproducible and prevents AI/reference art from becoming accidental geometry truth.
