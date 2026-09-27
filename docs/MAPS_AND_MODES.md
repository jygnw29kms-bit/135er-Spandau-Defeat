# Maps and modes — 0.5.1-sharp-ingame

All core battlefields use a nominal **1,000 x 1,000 metre** gameplay footprint. The current native Unreal source generates deterministic 3D graybox geometry with blocking collision, spawn areas and three replicated capture zones. Graybox geometry is replaced by final authored environment art without changing map IDs or game rules.

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

The three school maps are modern Spandau locations and use recognizable campus massing, surrounding streets, sports/courtyard spaces and local urban character as gameplay anchors. Their routes and cover are adapted for balanced multiplayer rather than being literal one-to-one replicas.

## Historical / special expansion

`fort_hahneberg_1945`, `teufelsberg_coldwar`, `flugplatz_gatow_1945`, `gatow_luftbruecke_1948`, `radeland_1945`, `hakenfelde_heeresamt_1944`, `zitadelle_1945`, `britischer_sektor_spandau`.

Each profile carries era/history metadata plus a flag distinguishing documented local combat from historically inspired gameplay. Details are in [HISTORY_MAPS.md](HISTORY_MAPS.md).

## Modes

Primary production target is objective infantry combat built around:
- A/B/C territory capture
- attack / defend
- breakthrough
- sabotage / demolition where appropriate
- logistics/objective variants for non-battle historical settings

Map geometry should remain recognizable in composition and landmarks while routes, cover, distances and sightlines are adapted for balanced multiplayer. No copyrighted third-party game maps or assets are copied.
