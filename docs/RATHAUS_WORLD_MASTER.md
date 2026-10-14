# Rathaus World Master

Updated: 2026-10-14

## Production decision

The authoritative Rathaus map workflow is now **Blender world master -> tagged modular export -> Unreal Engine 5**.

The later isolated Rathaus/GIS test chain (`REAL_v70`, `VISUAL_v77`, DOP/DGM v82/v83 and the former `REAL_FINAL`) is **not** the production geometry baseline. Those files remain useful only as reference, GIS validation and data sources.

## Recovered full-map baseline

Recovered source:
`SpandauStrike_Rathaus_FULLMAP_v13_UE5_READY.blend`

Verified scene extent:
- approx. 1.855 km x 4.201 km
- approx. 110.2 m vertical range
- 10,118 total objects
- 10,100 mesh objects
- 364,197 vertices
- 463,378 polygons

Important collections already present:
- `PRODUCTION_MODELS` (4,222 meshes)
- `ZERO_BLOCKOUT_MODELS` (2,439 meshes; obsolete/reference layer)
- `FULLMAP_Gameplay`
- `GAMEPLAY_Layer`
- `FULLMAP_Collision`
- `FULLMAP_Environment`
- `FULLMAP_UrbanDetail`
- `STREET_TRAM_DETAIL`
- `REAL_Rebuilt_Architecture`
- `REAL_Rebuilt_Detail`

## Verified semantic content

Already present in the recovered master:
- 12 spawn markers
- Objective A/B geometry
- cover markers/objects
- nav blocker meshes
- DGM terrain
- OSM road geometry
- water geometry
- Rathaus collision meshes
- surrounding-building collision
- vegetation / street / tram detail layers

## Problems found in v13

- obsolete blockout and production geometry exist in parallel
- all 10,100 mesh objects initially used separate mesh datablocks
- seven Berlin3D image references pointed to old local paths
- no reusable semantic custom properties were stored on objects
- several old photo/reference layers should not be exported to UE5
- the former UE5 `REAL_FINAL` map was based on a much smaller 358 m x 358 m GIS test surface and must not be treated as the full production map

## New master chain

- `WORLD_MASTER_v14`: preserved recovery checkpoint archived locally outside Git
- `WORLD_MASTER_v15_OPTIMIZED`: non-destructive production cleanup
  - semantic tags (`spawn`, `objective`, `cover`, `nav`, `collision`, `terrain`, `road`, `water`, `rathaus`)
  - obsolete blockout/reference collections excluded from production export
  - Berlin3D texture paths repaired and images packed where available
  - exact duplicate mesh datablocks deduplicated where safe

## Gameplay metadata policy

Objects/collections exported toward Unreal should carry explicit semantic roles. Current core tags:
- spawn
- objective
- cover
- nav
- collision
- terrain
- road
- water
- rathaus
- production
- setdressing
- reference/blockout (never production-exported)

Future tags should add:
- choke
- route
- sniper_pos
- cover_low / cover_high
- vaultable
- interior_playable / interior_closed
- no_nav

## UE5 handoff policy

Unreal receives controlled modular export packages from the Blender master. It is responsible for gameplay systems, lighting, final materials, Nanite/LOD policy, navigation, AI, effects and runtime optimization. It is no longer the primary place to repair incomplete Rathaus geometry.

