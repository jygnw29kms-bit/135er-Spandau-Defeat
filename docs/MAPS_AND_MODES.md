
All active map work targets a shared **Blender/Berlin-GIS master** with two engine outputs: **Unreal Engine 5 / Lyra Unreal Editor** and **Unreal Engine 5.8 / Lyra**.

UE/Lyra has already reached a first playable Falkenhagener Feld GIS milestone. Unreal Engine 5 remains an active parallel target, with Unreal Editor-authored geometry, Unreal Engine 5 materials/lighting, gameplay entities and dedicated-server validation. Both engine branches share the same 20-map roster and geographic/reference foundation.

## Core Spandau maps — 12

| Map ID | Display name | Gameplay character | Primary objective flow |
|---|---|---|---|
| `rathaus_spandau` | Rathaus Spandau | dense civic / urban | square → Rathaus approach → east street |
| `zitadelle` | Zitadelle Spandau | fortress / courtyards | outer bridge → gatehouse → inner courtyard |
| `staaken` | Staaken | suburban / rail corridors | west rail → crossing → east residential |
| `rodelberg` | Rodelberg | hill / open terrain | lower slope → crest → east trench |
| `kiesteich` | Kiesteich | shoreline / park | west shore → central park → east shore |
| `falkenhagener_feld` | Falkenhagener Feld | housing estate | west blocks → central plaza → east blocks |
| `lynarstrasse` | Lynarstraße | dense urban | west choke → junction → east block |
| `wroehmaennerpark` | Wröhmännerpark | riverside park | west park → river path → east gate |
| `freiheit` | Freiheit | industrial | west yard → freight hall → east tracks |
| `martin_buber_schule` | Martin-Buber-Schule | school campus | west perimeter → schoolyard → main building |
| `askanier_schule` | Askanier-Schule | compact school complex | street approach → courtyard → sports/building wing |
| `b_traven_schule` | B.-Traven-Schule | broad school campus | outer grounds → central campus → rear access |

## Historical / special maps — 8

`fort_hahneberg_1945`, `teufelsberg_coldwar`, `flugplatz_gatow_1945`, `gatow_luftbruecke_1948`, `radeland_1945`, `hakenfelde_heeresamt_1944`, `zitadelle_1945`, `britischer_sektor_spandau`.

## Unreal Engine 5 map pipeline

1. reference pass
2. Unreal Editor blockout
3. spawns/objectives
4. sightline and lane validation
5. bot-safe geometry
6. Unreal Engine 5 material/light pass
7. props/particles/atmosphere
8. compile and local test
9. dedicated-server test
10. genuine engine capture
11. Workshop packaging when alpha-ready

## Modes

- A/B/C territory capture
- attack / defend
- breakthrough
- sabotage / demolition where technically appropriate
- logistics/objective variants for historical non-battle scenarios
