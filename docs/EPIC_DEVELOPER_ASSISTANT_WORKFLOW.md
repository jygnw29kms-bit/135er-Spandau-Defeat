# Epic Developer Assistant Workflow

## Zweck
Der Epic Developer Assistant wird als offizielle Epic-Zweitmeinung fuer Unreal-Engine-spezifische Fragen genutzt. Er ersetzt weder Projektlogik noch unsere Tests.

## Verbindlicher Ablauf
1. Problem lokal reproduzieren und konkrete Engine-Version nennen: UE 5.8.3.
2. Minimalen technischen Kontext liefern: relevante C++/Python-Datei, Logausschnitt, Map/Asset und beobachtetes Verhalten.
3. Epic Developer Assistant nach dem offiziell empfohlenen UE5.8-Weg fragen.
4. Antwort gegen Epic-Dokumentation/API-Referenz gegenpruefen, wenn sie Engine-API, CLI-Flags oder Editor-Automation betrifft.
5. Empfehlung nur in einem isolierten Test anwenden.
6. Build, Runtime-Gate und Regression laufen lassen.
7. Erst danach in `main` committen/pushen.

## Gute Einsatzfaelle
- UE5.8 Editor-/Python-/C++-API
- Rendering, CSV Profiler, Unreal Insights, RDG/RHI
- Automation Framework und Headless/Editor-Unterschiede
- Navigation, Collision, World Partition/Level-Handling
- Asset-Registry- und Save/Load-Verhalten
- Engine-CLI-Flags und Profiling
- bekannte Versionsaenderungen in UE 5.8

## Nicht blind uebernehmen
- Projektarchitektur
- Gameplay-Regeln
- Map-/Art-Design
- generierten Code ohne Compile/Test
- Vermutungen ohne passende UE5.8-Quelle

## Spandau-Strike-Kontext
- Rechner: Lucas / DESKTOP-SMN4ATU
- Engine: Unreal Engine 5.8.3
- Projekt: `ue5/SpandauStrike/SpandauStrike.uproject`
- aktueller Gameplay-Stand: `LV_RathausSpandau_REAL_v77_ROADS_V85_GAMEPLAY`
- letzter stabiler Commit: `c43e9e0 Validate full Rathaus capture round`
- 24 PlayerStarts, 16 Frontspawns, 8 CapturePoints, 1 CaptureDirector
- komplette Runde Sektor 1 -> 4 getestet
- 15/15 Bots pro Sektor geroutet, 0 Routingfehler
- MapCheck 0 Fehler / 0 Warnungen
- aktueller Arbeitsblock: echtes DX12-Rendering, CSV-Profiling, FPS/Frametime und Spielerperspektive

## Ergebnisregel
Epic Assistant = technische Referenz. Unser Build und unsere Runtime-Tests entscheiden, ob eine Empfehlung wirklich in Spandau Strike gehoert.
