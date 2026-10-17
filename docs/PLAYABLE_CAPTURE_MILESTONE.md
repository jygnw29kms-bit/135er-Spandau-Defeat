# Spandau Strike – Playable Capture Milestone

## Stand
Der aktuelle Gameplay-Teststand ist **Rathaus v75 Front Spawns**. v73 bleibt der technische Ein-Sektor-Checkpoint, v74 die erste vollständige Vier-Sektor-Runde. v75 koppelt nun auch Respawns an die wandernde Front.

## Runtime-Klassen
- `ASpandauCapturePoint`: serverautoritatives Capture, Contest-Pause, 45-s-Baseline, Spieler-Speedup bis 4, verzögerter Fortschrittsabbau, replizierter Zustand und Runtime-Debuganzeige.
- `ASpandauCaptureDirector`: vier Sektoren, zwei notwendige Punkte je Sektor, Angreifer-Tickets, 20-s-Sektorwechsel, Siegzustand, 10-s-Team-Respawnwellen und Bot-Objective-Routing.
- `ULyraPlayerSpawningManagerComponent`: erkennt die aufgelösten Capture-Teams und bevorzugt beim Respawn die zum aktuellen Sektor und zur Rolle Attacker/Defender gehörenden Front-Spawns.
- `ALyraHUD`: minimales Test-HUD für Sektor, Tickets, Respawn-Welle sowie A/B-Zustand und Capture-Fortschritt.
- `ALyraGameMode`: Capture-Runden leiten Respawn-Anforderungen an den CaptureDirector weiter; Erstspawns bleiben als sicherer Bootstrap im normalen Lyra-Pfad.

## v75 Front-Spawns
Map:
`/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS`

Basis ist v74. Die acht bisherigen sicheren LyraPlayerStarts bleiben als Fallback erhalten. Zusätzlich gibt es **16 Front-Spawns**: pro Sektor je zwei für Angreifer und zwei für Verteidiger. Sie tragen ausschließlich Daten-Tags (`SSSpawn.Attacker`/`SSSpawn.Defender` + `SSSpawn.Sector.N`). Die Spawn-Auswahl wird zur Laufzeit mit den tatsächlich von Lyra vergebenen Team-IDs verknüpft, also nicht mit hart codierten Teamnummern.

Damit wandern die Respawns mit der Front. Sektor 1 nutzt nur die Sektor-1-Startpunkte, nach der Einnahme und dem 20-s-Übergang wechselt die Auswahl auf Sektor 2 usw. Fehlen passende Front-Spawns oder ist ein Team noch nicht aufgelöst, bleibt der normale Lyra-Fallback aktiv statt den Spieler im Nirwana abzusetzen. Auch Software kann gelegentlich Selbstachtung besitzen.

## Capture Round
Vier Frontsektoren sind angelegt, jeweils mit A/B. Ein Sektor gilt erst als genommen, wenn beide Punkte erobert wurden. Danach: +50 Angreifer-Tickets, 20 Sekunden Übergang und Aktivierung der nächsten Front. Nach Sektor 4 gewinnen die Angreifer.

## Respawn und Tickets
- Team-Respawnwelle: 10 Sekunden.
- Tote Controller werden serverseitig in die nächste Welle eingereiht.
- Erst bei erfolgreichem Angreifer-Respawn wird ein Ticket abgezogen.
- Verteidiger respawnen ohne Ticketverbrauch.
- Bei 0 Angreifer-Tickets werden keine weiteren Angreifer-Respawns freigegeben.
- Ab v75 werden Respawns nach Teamrolle und aktivem Frontsektor auf die markierten Front-Spawns gefiltert.

## Bots
Alle zwei Sekunden wird für lebende Bots das aktuelle Objective neu bewertet. Angreifer und Verteidiger laufen zu offenen A/B-Punkten des aktiven Sektors. Der v74-Runtime-Test bestätigte `routed=15 failed=0`; dieses Verhalten bleibt in v75 erhalten. Objective-Routing und Kampf-KI bleiben getrennte Verantwortlichkeiten, damit ein Bot nicht gleichzeitig drei widersprüchliche Lebensziele verfolgt.

## HUD
Oben mittig zeigt das funktionale Test-HUD Sektor x/4, Angreifer-Tickets, Zeit bis zur nächsten Respawn-Welle sowie A/B-Status und Capture-Prozent. Das ist bewusst kein Final-UI.

## Start
`tools/ue5/launch_rathaus_v75_front_spawns.ps1`

Standard: Lyra Shooter Elimination als Waffen-/Pawn-/Bot-Unterbau, 15 Bots. Unsere Capture-, Respawn-, Ticket-, HUD-, Objective- und Front-Spawn-Runtime läuft darüber.

## Automatische Gates
- `tools/ue5/run_rathaus_v75_front_spawn_headless_check.ps1`
- statische Map-Prüfung: 24 PlayerStarts gesamt, davon 16 Front-Spawns, 8 CapturePoints, 1 Director, je exakt 2 Attacker- und 2 Defender-Spawns pro Sektor
- Runtime-Prüfung: Teams aufgelöst, 15 Bots zu Objectives geroutet, keine FellOutOfWorld/KillZ/Spawn/Fatal-Fehler

## Nächste Gameplay-Schritte
1. v75 sichtbar anspielen und Front-Spawn-Laufwege sowie direkte Sichtlinien prüfen.
2. Spawn-Sicherheit um Gegnerdistanz, direkte Sicht und Recent-Death-Heat ergänzen.
3. Bot-Kampfverhalten mit Objective-Routing koppeln, ohne den bestehenden Lyra-Kampf zu überschreiben.
4. echte Capture-/Kill-/Respawn-Telemetrie protokollieren und Waffen/Movement nur anhand gemessener Werte nachbalancieren.
5. Capture anschließend aus dem Elimination-Unterbau in eine eigene Spandau-Strike-Lyra-Experience überführen.
