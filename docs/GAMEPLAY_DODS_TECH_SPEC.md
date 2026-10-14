# 135er Spandau Strike – DoD:S Gameplay Technical Specification

## Status
Verbindliche Gameplay-Basis für 135er Spandau Strike. Engine: Unreal Engine 5 / Lyra. World Master: Blender. Day of Defeat: Source dient als funktionale Referenz für Movement, Gunplay, Klassenrollen und Territorial Control.

## Core Pillars
- hohe Letalität, geringe TTK, kein Shield-Gameplay
- schweres, griffiges Movement mit Stamina, Prone und begrenztem Air Control
- Hip-Fire-orientiertes Gunplay; ADS nur wo die Waffenrolle es verlangt
- Bolt Rifles: Oberkörper-One-Shot, langsamer Bolt Cycle
- MG: undeployed unpräzise, deployed lane-dominant, immer mit Flank/Smoke-Counterplay
- 6 Rollen: Rifleman, Assault, Support, Sniper, MG, Rocket
- teambasierte lineare Front statt freiem Back-Cap

## Lyra Architecture
- `USpandaCharacterMovementComponent`
- `USpandaStaminaSet`
- `USpandaWeaponHandlingSet`
- `USpandaWeaponInstance` + Rifle/MG Spezialklassen
- GAS Abilities: Sprint, Prone, BipodDeploy, BipodUndeploy, BoltCycle, Scope
- `ASpandaCapturePoint`, `ASpandaTerritorialGameState`, `ASpandaSpawnManager`
- server authoritative: Damage, Capture, Stamina, Weapon Fire, Bipod, Class Selection

## Movement Targets
- Walk/Run/Sprint über datengetriebene Profile
- Sprint und Sprünge kosten Stamina; Low Stamina erhöht Sway und verlangsamt Recoil Recovery
- Richtungswechsel müssen abbremsen/beschleunigen statt instant A/D zu spiegeln
- geringe Air Control; Jump-Spam erzeugt Fatigue
- Prone Transition ca. 0.65–0.9 s; Aufstehen ca. 0.8–1.1 s
- Prone reduziert Recoil/Spread/Sway, schränkt Turn Rate und View Arc ein

## Weapon Handling
- Crosshair repräsentiert realen Cone of Fire
- Spread = Base + Movement + Shot Bloom + Jump + Stamina
- MG-Bipod benötigt gültige Supportfläche oder Prone Ground Support
- Bipod: stark reduzierte Bewegung, Yaw/Pitch Arc, starke Recoil-/Spread-Reduktion
- K98k/Springfield: Head und UpperTorso tödlich; Bolt-Cycle etwa 1.1–1.5 s

## Classes
- Rifleman: Präzision / Mid Range
- Assault: mobilster Frontkämpfer
- Support: mittlere Mobilität / Area Pressure
- Sniper: lange Sichtachsen, verwundbar gegen Smoke/Flank
- MG: langsam, schwer, deployed dominant
- Rocket: schwer, Anti-MG / Area Denial
- Klassen über Hero/Pawn Data + Ability Sets + Gameplay Tags; Experiences definieren primär den Modus.

## Territorial Control – Rathaus Map
Aktueller World-Master-Flow ab v38/v39:

1. `FLAG_1_WEST_HOME` – 1 Spieler
2. `FLAG_2_WEST_STREET` – 1 Spieler
3. `FLAG_3_RATHAUS` – **2 Spieler gleichzeitig**
4. `FLAG_4_EAST_STREET` – 1 Spieler
5. `FLAG_5_EAST_HOME` – 1 Spieler

Regeln:
- nur angrenzende Frontpunkte aktiv
- Back-Cap deaktiviert
- beide Teams im Radius => `Contested`, Fortschritt stoppt
- Capture Progress bleibt kurz erhalten und darf erst danach langsam verfallen
- zentrale Rathaus-Flagge ist bewusster Teamplay-Bottleneck

## Map Flow
Drei Hauptlanes:
- `north`: Rathaus-Rückseite / nördliche Umgehung
- `mid`: Rathaus / zentrale Kampfzone
- `south`: Plaza / südliche Straßenachse

Drei Crosslinks:
- `CROSSLINK_WEST`
- `CROSSLINK_MID`
- `CROSSLINK_EAST`

Kein Lane-Tunnel: alle drei Lanes müssen über Querverbindungen wechselbar bleiben.

## Chokes / Counterplay
- `CHOKE_RATHAUS_FRONT`: hard choke, Mid
- `CHOKE_RATHAUS_WEST`: medium, South
- `CHOKE_RATHAUS_EAST`: medium, Mid
- `CHOKE_RATHAUS_REAR`: medium, North

Jeder starke Choke erhält mindestens:
- Frontangriff
- Flankenroute oder Lane-Switch
- Smoke-Anker

MG-/Sniper-Positionen sind nur zulässig, wenn mindestens Smoke oder alternative Flanke als Gegenmittel existiert.

## Blender Metadata Contract
Wichtige `ss_*` Properties:
- `ss_role`, `ss_tag`, `ss_export`, `ss_runtime`
- `ss_team`, `ss_lane`, `ss_zone`
- `ss_capture_players`, `ss_sequence`, `ss_linear`
- `ss_cover_class`
- `ss_weapon_role`, `ss_requires_bipod`
- `ss_counterplay`

Exportmanifest muss diese Metadaten vollständig an UE5-Importtools weitergeben.

## Current Production Policy
Blender World Master -> Gameplay/Architecture QA -> tagged modular export -> UE5/Lyra. UE5-FINAL wird erst mit geprüften Masterständen aktualisiert; kaputte ältere Rathaus-v70/v77-Geometrie gilt nicht als Produktionsbasis.
