# Lyra GIS status — 2026-09-29

## Verified live Berlin services
- WFS endpoint: https://gdi.berlin.de/services/wfs/ua_gebaeudehoehen
- Feature type: ua_gebaeudehoehen:gebaeudehoehen
- Default CRS: EPSG:25833 (ETRS89 / UTM zone 33N)
- WFS versions: 1.0.0, 1.1.0, 2.0.0
- Geometry: GML MultiSurface with 2D footprint coordinates
- Relevant attributes: gisid, gml_id, name, funktion, dachart, hoehe, geschosse, strasse, hnr, dachart_txt
- hoehe is the building ridge height in metres

## Important freshness distinction
The Gebäudehöhen layer is explicitly titled "Gebäudehöhen 2022" and is derived from Berlin LoD2 data.
It is suitable for spatial blockout and height/roof metadata, but it is not a live full CityGML roof mesh.
The separate ALKIS Berlin building service has newer cadastral maintenance metadata and should be added as a second source when footprint freshness matters.

## Falkenhagener Feld live check
The runtime geocoder resolves Falkenhagener Feld to approximately:
- latitude 52.5524034
- longitude 13.1668941
- EPSG:25833 approximately E 375716.66 / N 5824059.63

A 1.8 km x 1.8 km WFS query around that center returned 4,610 matching building features.

## Current Lyra branch
- branch: lyra-ue5-gis
- 20 map definitions mirrored from Source 2
- 20 map production specs mirrored from Source 2
- autonomous UE5 Python building importer created
- default map: falkenhagener_feld
- generated hierarchy: Berlin_LoD2_Autonomous_Import/<map>/Buildings

## Known next production layers
1. Replace per-building StaticMeshActors with HISM/combined geometry for large areas.
2. Add current ALKIS footprint source as optional override/freshness source.
3. Add DGM terrain pipeline and Landscape heightmap generation.
4. Add roads, water and vegetation.
5. Add custom landmark replacement layer.
6. Keep historical reconstruction separate from the modern GIS reference layer.

## Local workstation limitation
DESKTOP-BNDD1US currently has no Unreal Engine installation registered in:
C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat

Therefore the importer has been verified against the live Berlin service and its real GML schema, but has not yet been executed inside the UE5 editor on this workstation.
