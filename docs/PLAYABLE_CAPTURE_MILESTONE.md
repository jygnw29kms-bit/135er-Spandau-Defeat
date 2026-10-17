# Spandau Strike – Playable Capture Milestone

## Stand
Der spielbare Rathaus-Prototyp ist von v73 auf **v74 Capture Round** erweitert. v73 bleibt als technischer Ein-Sektor-Checkpoint erhalten; v74 ist der aktuelle Gameplay-Teststand.

## Runtime-Klassen
- `ASpandauCapturePoint`: serverautoritatives Capture, Contest-Pause, 45-s-Baseline, Spieler-Speedup bis 4, verzögerter Fortschrittsabbau, replizierter Zustand und Runtime-Debuganzeige.
- `ASpandauCaptureDirector`: verwaltet vier Sektoren, jeweils zwei notwendige Punkte, Angreifer-Tickets, 20-s-Sektorwechsel, Siegzustand, 10-s-Team-Respawnwellen und Bot-Objective-Routing.
- `ALyraHUD`: zeigt im Capture-Test minimal Sektor, Tickets, nächste Respawn-Welle sowie A/B-Capturezustand und Fortschritt. Keine Schadenszahlen oder Feindmarker.
- `ALyraGameMode`: laufende Capture-Runden leiten Respawn-Anforderungen an den CaptureDirector weiter; Erstspawns bleiben im normalen Lyra-Pfad.

## v74 Capture Round
Map:
`/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v74_CAPTURE_ROUND`

Basis ist v73. Architektur, Licht, Materialien, Straßen, DGM/DOP und die acht vorhandenen sicheren LyraPlayerStarts bleiben unangetastet.

Vier Frontsektoren sind angelegt, jeweils mit A/B:
1. westlicher Anmarsch
2. westlich/zentraler Rathausbereich
3. östlich/zentraler Rathausbereich
4. östlicher Abschluss

Ein Sektor gilt erst als genommen, wenn **beide Punkte** erobert wurden. Dann werden 50 Angreifer-Tickets gutgeschrieben und nach 20 Sekunden die nächste Front aktiviert. Nach Sektor 4 gewinnen die Angreifer.

## Respawn und Tickets
- Team-Respawnwelle: 10 Sekunden.
- Tote Controller werden serverseitig in eine Welle eingereiht.
- Erst wenn der Respawn wirklich einen Pawn erzeugt, wird bei Angreifern ein Ticket abgezogen.
- Verteidiger respawnen ohne Ticketverbrauch.
- Bei 0 Angreifer-Tickets werden keine weiteren Angreifer-Respawns freigegeben.

## Bots
Alle zwei Sekunden wird für lebende Bots das aktuelle Objective neu bewertet. Angreifer und Verteidiger werden zu einem noch offenen A/B-Punkt des aktiven Sektors geführt. Der Runtime-Test mit 15 Bots bestätigt das Routing: `routed=15 failed=0`. Falls Recast beim Mapstart noch keine verwendbare Route liefert, fällt die Test-Runtime auf direkte Zielbewegung zurück, bis Navigation verfügbar ist. Damit entsteht erstmals Objective-Druck statt reinem Elimination-Herumirren. Die endgültige Kampf-KI bleibt ein späterer eigener Ausbau.

## HUD
Oben mittig erscheint im Testmodus eine knappe Runtime-Anzeige:
- Sektor x/4
- Angreifer-Tickets
- Zeit bis zur nächsten Respawn-Welle
- A/B Status: Active, Capturing, Contested, Captured
- A/B Fortschritt in Prozent

Das ist bewusst funktional und nicht das spätere Final-UI. Es dient dem Gameplay-Test und der Telemetrie.

## Start
`tools/ue5/launch_rathaus_v74_capture_round.ps1`

Standard: Lyra Shooter Elimination als Waffen-/Pawn-/Bot-Unterbau, 15 Bots. Unsere Capture-, Respawn-, Ticket-, HUD- und Objective-Runtime läuft darüber.

## Automatischer Runtime-Gate
`tools/ue5/run_rathaus_v74_capture_headless_check.ps1`

Der aktuelle v74-Headless-Gate ist grün (`passed=true`, `bad_count=0`) und prüft:
- 8 LyraPlayerStarts
- 8 SpandauCapturePoints
- 1 SpandauCaptureDirector
- 4 Sektoren
- Shooter-Erlebnis erfolgreich geladen
- Capture-Runtime aktiv
- keine FellOutOfWorld/KillZ/Spawn/Fatal-Fehler im Beobachtungsfenster

## Nächste Gameplay-Schritte
1. v74 sichtbar mit Spieler + 15 Bots anspielen und reale Laufwege prüfen.
2. Sektorpositionen anhand echter Laufzeit und Sichtlinien nachschärfen.
3. Spawn-Auswahl pro Frontsektor anstatt nur der acht statischen Basisstarts.
4. Bot-Kampfverhalten so koppeln, dass Objective-Routing und Feindkontakt sauber zusammenarbeiten.
5. Waffen-/Movement-Baseline im echten Gefecht messen und nur anhand der Testergebnisse nachbalancieren.
6. Danach Capture aus dem Elimination-Unterbau in eine eigene Spandau-Strike-Lyra-Experience überführen.
