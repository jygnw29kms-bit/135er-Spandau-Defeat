# Berlin-Spandau Lyra / UE5 GIS branch
This branch mirrors the 20-map roster from `/maps/maps.json` and adds a separate Unreal Engine 5 / Lyra automation pipeline.

## Goals
- keep Unreal Engine 5 untouched
- reuse the same map IDs, names and historical notes
- resolve each map location automatically
- query live Berlin building-height WFS data
- convert EPSG:25833 coordinates to Unreal centimeters
- spawn deterministic Lyra blockout geometry
- keep historical reconstruction separate from modern GIS reference data

## Layout
- `maps/maps.json` — mirrored 20-map roster
- `scripts/berlin_spandau_lyra_import.py` — UE5 Python importer
- `docs/SETUP.md` — required UE plugins and execution steps

## Default
The importer defaults to `falkenhagener_feld`.
Change `ACTIVE_MAP` at the top of the script to any ID from `maps/maps.json`.

The current implementation intentionally creates blockout buildings from live footprint/height data.
Detailed landmark meshes, roads, terrain Landscape and historical reconstruction remain separate production layers.
