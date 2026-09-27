# Maps and modes — 0.6.0-source2-migration

All active map work now targets **Source 2 / CS2 Hammer**.

The former Unreal graybox pipeline is retired. Map IDs and gameplay identities are retained, but geometry, materials, lighting, nav/gameplay data and runtime integration are rebuilt for Source 2.

## Core Spandau maps

| Map ID | Display name | Gameplay character | Primary objective flow |
|---|---|---|---|
| `rathaus_spandau` | Rathaus Spandau | dense civic / urban | square → central crossing → rear streets |
| `zitadelle` | Zitadelle Spandau | fortress / courtyards | outer approach → courtyard → inner approach |
| `staaken` | Staaken | suburban / rail corridors | west streets → rail axis → east blocks |
| `rodelberg` | Rodelberg | hill / open terrain | lower slope → crest → rear slope |
| `kiesteich` | Kiesteich | shoreline / park | west shore → central crossing → east shore |
| `falkenhagener_feld` | Falkenhagener Feld | housing estate | estate west → boulevard → estate east |
| `lynarstrasse` | Lynarstraße | narrow urban | north blocks → street choke → south blocks |
| `wroehmaennerpark` | Wröhmännerpark | riverside park | west park → central lawn/path → east edge |
| `freiheit` | Freiheit | industrial | warehouses → yard/rail choke → warehouses |
| `martin_buber_schule` | Martin-Buber-Schule | school campus / courtyards | perimeter → schoolyard → main building |
| `askanier_schule` | Askanier-Schule | dense school complex | street approach → courtyard → sports/building wing |
| `b_traven_schule` | B.-Traven-Schule | campus / residential edge | outer grounds → central campus → rear access |

## Historical / special maps

`fort_hahneberg_1945`, `teufelsberg_coldwar`, `flugplatz_gatow_1945`, `gatow_luftbruecke_1948`, `radeland_1945`, `hakenfelde_heeresamt_1944`, `zitadelle_1945`, `britischer_sektor_spandau`.

## Source 2 map pipeline

Each map follows:
1. Hammer blockout with Source 2 grid discipline
2. spawn and objective placement
3. core sightline/route validation
4. recognizable landmark massing
5. Source 2 material/light pass
6. props, particles and atmosphere
7. nav/gameplay validation
8. dedicated-server test
9. real Source 2 in-game capture
10. public preview replacement only after capture validation

## Modes

Primary production target:
- A/B/C territory capture
- attack / defend
- breakthrough
- sabotage / demolition where technically appropriate
- logistics/objective variants for non-battle historical settings

Map geometry should remain recognizable in composition and landmarks while routes, cover, distances and sightlines are adapted for balanced multiplayer.