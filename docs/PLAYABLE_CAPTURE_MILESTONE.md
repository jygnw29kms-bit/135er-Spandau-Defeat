# Spandau Strike – Playable Capture Milestone

## Ziel
Der nächste spielbare Meilenstein ist kein weiterer Konzeptstand, sondern ein echter UE5/Lyra-Runtime-Test auf Rathaus Spandau mit Waffen, Bots, sicheren Spawns und der ersten eigenen Spandau-Strike-Capture-Logik.

## Runtime-Klassen
- `ASpandauCapturePoint`: serverautoritatives Capture, Contest-Pause, 45-s-Baseline, Spieler-Speedup bis 4, verzögerter Fortschrittsabbau, replizierter Zustand und Runtime-Debuganzeige.
- `ASpandauCaptureDirector`: verwaltet aktiven Sektor, zwei notwendige Punkte pro Sektor, Angreifer-Tickets, Sektorabschluss, Übergangszeit und Siegzustand.

## v73 Capture Prototype
Map:
`/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v73_CAPTURE_PROTO`

Basis ist v72 FIRST_PLAY. Architektur, Licht, Materialien, Straßen, DGM/DOP, acht LyraPlayerStarts und Spawn-Safety-Pads bleiben erhalten.

Der erste Testslice enthält bewusst nur einen aktiven Sektor mit zwei Punkten:
- S01-A: westlicher Straßen-/Anmarschbereich
- S01-B: Rathaus-Zentralbereich

Damit lassen sich bereits echtes Gunplay, Team-Interaktion, Contest-Verhalten, Capture-Fortschritt, Respawn-Rhythmus des vorhandenen Lyra-Shooter-Experiments und Map-Lesbarkeit gemeinsam testen, ohne gleich vier Sektoren voller Fehler gleichzeitig zu debuggen.

## Start
`tools/ue5/launch_rathaus_v73_capture_prototype.ps1`

Standardstart: Lyra Shooter Elimination als Waffen-/Pawn-/Bot-Unterbau, 15 Bots. Die eigene Capture-Runtime läuft parallel auf der Rathaus-Map. Nach Stabilisierung wird der Elimination-Unterbau schrittweise durch den finalen Spandau-Strike-Modusfluss ersetzt.

## Automatischer Gate-Test
`tools/ue5/run_rathaus_v73_capture_check.ps1`

Der Gate-Test prüft:
- 8 LyraPlayerStarts
- 2 SpandauCapturePoints
- 1 SpandauCaptureDirector
- erfolgreich geladenes Shooter-Erlebnis
- Runtime-Aktivierung der eigenen Capture-Klassen
- keine FellOutOfWorld/KillZ/Spawn/Fatal-Fehler im Testfenster

## Ausbau nach v73
1. v73 technisch und manuell spielbar bestätigen.
2. Sektor 2–4 hinzufügen, jeweils A/B.
3. Respawn-Wellen direkt an SpandauCaptureDirector koppeln.
4. Angreifer-Tickets bei tatsächlichem Respawn abbuchen.
5. Capture-/Ticketdaten in das minimale HUD bringen.
6. Bots auf aktive Capture-Ziele lenken.
7. Erst danach Waffen- und Movement-Baseline im echten Spieltest nachschärfen.
