# Berlin geodata -> Source 2 map pipeline

This project uses official/open Berlin geodata to establish real-world scale and building massing before gameplay adaptation.

## Data priority

1. **Berlin LoD2 building model** — primary reusable geometry reference. Building footprints follow cadastral building outlines and generalized roof forms. License: Datenlizenz Deutschland – Zero 2.0.
2. **Berlin 3D Mesh 2025** — high-detail visual and spatial reference. Distributed as tiled OBJ + textures through the Berlin 3D download portal. Keep its original geometry/textures out of distributable game assets unless the portal terms explicitly permit that use.
3. **Esri Deutschland Berlin 3D scene** — interactive visual cross-check for building massing, roof orientation, terrain and neighborhood context. Viewer item: https://opendata-esridech.hub.arcgis.com/maps/50e8049abb5841dcb3c113210b2109fb/explore . Treat it as a visualization/reference layer; use the official Berlin LoD2 download as the geometry source of record.
4. **Terrain / streets** — use Berlin terrain data and OpenStreetMap context as alignment aids.

## School anchors

Canonical site definitions are stored in `source2/geodata/school_sites.json`.

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
10. Export optimized geometry for Source 2/Hammer.
11. Build collision separately and keep decorative detail out of player collision.
12. Run Source 2 validation: scale, routes, spawn safety, objectives, nav/bots, visibility and performance.

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
