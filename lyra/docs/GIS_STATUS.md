# Lyra GIS status — 2026-10-01

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

## Local workstation status
DESKTOP-BNDD1US now has a complete Lyra Starter Game project at:
C:\Users\dezen\Documents\Unreal Projects\SpandauStrike

Verified:
- launcher engine: UE 5.8.3 at C:\Program Files\Epic Games\UE_5.8
- project: C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SpandauStrike.uproject
- Content\DefaultGameData.uasset is present; the previous Lyra startup blocker is resolved
- PythonScriptPlugin enabled
- EditorScriptingUtilities enabled
- ShooterCore, ShooterMaps, ShooterExplorer, ShooterTests and TopDownArena load successfully
- production importer installed at Content\Python\berlin_spandau_lyra_import.py
- all 20 map specs mirrored to Design\BerlinSpandauGIS

The Epic launcher UE 5.8 Build.bat had a false self-lock loop during ValidatePlatforms. A backup was saved as Build.bat.lockfix-backup and the launcher copy was aligned with the working source-build behavior by calling :Main directly instead of :Lock.

## Verified Unreal GIS execution — 2026-09-30
Smoke test, 240 m x 240 m:
- WFS features: 142
- usable buildings: 141
- UE actors created: 141
- World Partition map saved at /Game/Maps/BerlinSpandauSmoke/falkenhagener_feld
- runtime: 4.55 seconds

Full Falkenhagener Feld import, 1.8 km x 1.8 km:
- WFS features: 4,610
- usable buildings: 4,560
- UE actors created: 4,560
- World Partition map saved at /Game/Maps/BerlinSpandau/falkenhagener_feld
- runtime: 100.40 seconds

The end-to-end chain is therefore verified: Lyra startup -> Python 3.11 -> Berlin WFS -> EPSG:25833 transform -> World Partition level -> actors -> save.


## Playable Falkenhagener Feld milestone — 2026-09-30
Verified in UE 5.8.3 rendered game mode:
- final gameplay map: /ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld
- WorldSettings: SpandauStrikeWorldSettings
- Experience: B_LyraShooterGame_ControlPoints
- ShooterCore transitions to Active
- eight LyraPlayerStart actors
- NavMeshBoundsVolume and runtime navmesh generation
- Control Points A/B/C
- Shooter HUD, pawn and weapon active
- game phase transitions Warmup -> Playing
- real in-engine capture verified during development; current blockout capture is intentionally not published because it does not yet pass the public image QA gate

The current visual is still a GIS/gameplay blockout. Building volumes are data-driven proxies and the temporary gameplay ground uses WorldGrid. DGM1 terrain, streets, water, vegetation, final materials and landmark geometry remain production-quality work after the playable milestone.

## Playable ShooterMaps milestone � 2026-09-30
Playable runtime map:
- /ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld
- 8 LyraPlayerStart actors
- NavMeshBoundsVolume + RecastNavMesh
- DirectionalLight, SkyLight and fog
- Lyra ShooterCore runtime verified

Real OSM overlay:
- 1,096 OSM elements processed
- 4,805 road/path segments
- 230 water segments
- saved as World Partition external actors

Standalone validation:
- URL option ?NumBots=7 verified
- ShooterGame.GamePhase.Playing entered
- Warmup phase ended successfully
- real 1280x720 in-game screenshots captured
- r.WarnOfBadDrivers=0 used in project SystemSettings to avoid the development machine driver warning dialog

The map is now playable as a Lyra standalone ShooterMaps level. Visual fidelity remains a production pass: building/road/water materials, terrain elevation, vegetation and landmark-specific geometry should continue to be refined.


## DGM + optimized GIS milestone — 2026-10-01
Falkenhagener Feld now uses official Berlin DGM1 terrain data for the 1.8 x 1.8 km playable area.

- source tiles: DGM1_374_5822, DGM1_376_5822, DGM1_374_5824, DGM1_376_5824
- source CRS: EPSG:25833
- derived terrain grid: 181 x 181 at 10 m spacing (32,761 vertices)
- source elevation range in crop: 27.92 m to 41.32 m
- center reference elevation: 33.32 m
- resulting relative relief: 13.4 m
- terrain collision: complex-as-simple
- all 8 LyraPlayerStart actors aligned to DGM elevation

OSM layers are now draped onto DGM and merged:
- roads: 19,224 vertices / 9,612 triangles
- water: 696 vertices / 248 triangles
- former per-segment GIS external actors backed up: 5,039
- active optimized GIS actors: SS_DGM_Terrain, SS_DGM_Roads, SS_DGM_Water
- active LyraPlayerStart actors remain: 8

Standalone Lyra runtime was revalidated with ?NumBots=7 after the optimization pass and a fresh 1280x720 in-game screenshot was captured.

## V7 playable production milestone � 2026-10-01
Verified standalone map:
- /ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v7
- Lyra ControlPoints experience enters ShooterGame.GamePhase.Playing
- Warmup ends normally
- 7 bots verified in standalone gameplay
- combat, health/ammo HUD and kill feed verified
- real in-game screenshots captured from the running UE5.8 window

Critical collision fix:
- combined 4,610-building OBB mesh switched to CTF_USE_COMPLEX_AS_SIMPLE
- DGM terrain switched to CTF_USE_COMPLEX_AS_SIMPLE
- merged roads use NoCollision; DGM terrain supplies walkable collision
- this removed the whole-map simple bounding-box collision that previously caused NO PLAYERSTART / origin fallback spawning

V7 presentation/runtime:
- DGM terrain + exact building OBB + draped OSM roads/water + tree inventory loaded
- all V7 materials compiled with Nanite usage enabled
- NavMeshBoundsVolume expanded to full 1.8 x 1.8 km production area
- remaining optimization: persist generated navigation data so standalone startup no longer rebuilds nav at runtime

## Falkenhagener Feld V8 — 2026-10-01

New safe production map (V7 retained as rollback):
- /ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8
- exact Berlin WFS-derived building footprint meshes split into Residential, Public, Industrial and Aux categories
- DGM10 terrain, OSM roads/water and Berlin tree inventory retained
- 8 LyraPlayerStart actors and Lyra ControlPoints gameplay verified
- standalone ?NumBots=7 reaches ShooterGame.GamePhase.Playing and ends Warmup normally
- category-specific materials and reduced sun/sky/fog exposure pass
- project renderer config disables default auto exposure for the GIS production pass

Navigation optimization:
- RecastNavMesh RuntimeGeneration changed to Static
- bForceRebuildOnLoad=False and bCanSpawnOnRebuild=True
- level re-saved with persistent RecastNavMesh actor before running WorldPartitionNavigationDataBuilder
- final clean-start verification is performed after the offline builder completes

### V8 gameplay anchor pass
- PlayerStarts moved from open terrain into OSM-derived real street corridors:
  - west: Am Bogen / Paul-Gerhardt-Ring
  - east: Pionierstrasse corridor
- three native ShooterCore B_ControlPointVolume actors added for A/B/C
- ControlPoints experience loads without control-point errors
- NS_CapturePoint effect loads in standalone runtime
- ?NumBots=7 reaches ShooterGame.GamePhase.Playing after Warmup

### Remaining navigation performance issue
WorldPartitionNavigationDataBuilder completes with 0 errors after setting Recast RuntimeGeneration=Static, but a fresh standalone launch still reports SpawnMissingNavigationData and rebuilds the default navmesh at runtime. Gameplay is functional after that rebuild; persistent World Partition nav-data serialization remains an open optimization item and is not marked fixed.

## Falkenhagener Feld V8 daylight/runtime validation � 2026-10-01
- V8 standalone runtime verified with ?NumBots=7
- ShooterGame.GamePhase.Playing reached after warmup
- daylight pass: DirectionalLight 4.0, SkyLight 1.25, reduced fog, unbound post-process exposure bias
- engine on-screen warnings hidden for clean runtime capture
- clean in-game screenshot captured from the actual UE 5.8 game window

## Falkenhagener Feld V8 persistent World Partition navigation � 2026-10-01
- RecastNavMesh diagnosis: RuntimeGeneration was already Static, but Is World Partitioned was false.
- Is World Partitioned enabled and saved on RecastNavMesh-Default.
- WorldPartitionNavigationDataBuilder completed all 4 iterative cells.
- Navigation data chunk actors were generated and saved for the 1.8 km production world.
- Fresh standalone validation with ?NumBots=7: no SpawnMissingNavigationData and no runtime RebuildAll building NavData.
- ShooterGame.GamePhase.Playing reached normally and Warmup ended.
