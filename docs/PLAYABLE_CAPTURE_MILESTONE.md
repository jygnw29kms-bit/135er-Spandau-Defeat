# Spandau Strike – Playable Capture Milestone

## Stand
Der aktuelle Gameplay-Teststand ist **Rathaus v75 Front Spawns**. v73 bleibt der technische Ein-Sektor-Checkpoint, v74 die erste vollständige Vier-Sektor-Runde. v75 koppelt Respawns an die wandernde Front und besitzt inzwischen die erste echte Spawn-Sicherheitswertung.

## Runtime-Klassen
- `ASpandauCapturePoint`: serverautoritatives Capture, Contest-Pause, 45-s-Baseline, Spieler-Speedup bis 4, verzögerter Fortschrittsabbau, replizierter Zustand und Runtime-Debuganzeige.
- `ASpandauCaptureDirector`: vier Sektoren, je zwei notwendige Punkte, Angreifer-Tickets, 20-s-Sektorwechsel, Siegzustand, 10-s-Team-Respawnwellen, Bot-Objective-Routing und Recent-Death-Heat.
- `ULyraPlayerSpawningManagerComponent`: erkennt die aufgelösten Capture-Teams, filtert Respawns nach aktivem Sektor/Attacker/Defender und bewertet Spawn-Sicherheit.
- `ALyraHUD`: minimales Test-HUD für Sektor, Tickets, Respawn-Welle sowie A/B-Zustand und Capture-Fortschritt.
- `ALyraGameMode`: Capture-Runden leiten Respawn-Anforderungen an den CaptureDirector weiter und melden den letzten Pawn-Ort vor einem erzwungenen Death-Reset als Death-Heat-Ereignis.

## v75 Front-Spawns
Map:
`/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS`

Basis ist v74. Die acht bisherigen sicheren LyraPlayerStarts bleiben als Fallback erhalten. Zusätzlich gibt es **16 Front-Spawns**: pro Sektor je zwei für Angreifer und zwei für Verteidiger. Sie tragen Daten-Tags (`SSSpawn.Attacker`/`SSSpawn.Defender` + `SSSpawn.Sector.N`). Die Spawn-Auswahl wird zur Laufzeit mit den tatsächlich von Lyra vergebenen Team-IDs verknüpft und verwendet keine fest eincodierten Teamnummern.

Damit wandern die Respawns mit der Front. Nach dem Sektorwechsel wird automatisch der passende Spawn-Satz für den neuen Frontabschnitt verwendet. Fehlen passende Front-Spawns oder ist ein Team noch nicht aufgelöst, bleibt der normale Lyra-Fallback aktiv.

## Capture Round
Vier Frontsektoren sind angelegt, jeweils mit A/B. Ein Sektor gilt erst als genommen, wenn beide Punkte erobert wurden. Danach: +50 Angreifer-Tickets, 20 Sekunden Übergang und Aktivierung der nächsten Front. Nach Sektor 4 gewinnen die Angreifer.

## Respawn und Tickets
- Team-Respawnwelle: 10 Sekunden.
- Tote Controller werden serverseitig in die nächste Welle eingereiht.
- Erst bei erfolgreichem Angreifer-Respawn wird ein Ticket abgezogen.
- Verteidiger respawnen ohne Ticketverbrauch.
- Bei 0 Angreifer-Tickets werden keine weiteren Angreifer-Respawns freigegeben.
- Respawns werden nach Teamrolle und aktivem Frontsektor auf die markierten Front-Spawns gefiltert.

## Spawn-Sicherheit
Die Auswahl bewertet jetzt drei Dinge gemeinsam:
1. **Direkte Gegnernähe:** Startpunkte innerhalb von 12 m zu einem lebenden Gegner werden verworfen.
2. **Direkte Feindsicht:** Startpunkte mit Enemy-Line-of-Sight werden verworfen.
3. **Recent-Death-Heat:** Todesorte werden 15 Sekunden lang gespeichert. Innerhalb eines Radius von 25 m erzeugen sie eine mit Alter und Entfernung abfallende Strafwertung. Mehrere frische Todesfälle addieren sich.

Unter den verbleibenden Kandidaten gewinnt der Start mit der besten Kombination aus Gegnerabstand und niedriger Death-Heat. Damit soll die Front mitwandern, ohne dass ein gerade beschossener Spawn stumpf weiter Menschen ausspuckt. Falls alle Frontkandidaten ungeeignet sind, bleibt der Lyra-Fallback als Sicherheitsnetz bestehen.

## Bots
Alle zwei Sekunden wird für lebende Bots das aktuelle Objective neu bewertet. Angreifer und Verteidiger laufen zu offenen A/B-Punkten des aktiven Sektors. Der Runtime-Gate bestätigt weiterhin `routed=15 failed=0`. Objective-Routing und Kampf-KI bleiben getrennte Verantwortlichkeiten.

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
1. v75 sichtbar anspielen und Front-Spawn-Laufwege sowie tatsächliche Sichtlinien prüfen.
2. Spawn-Telemetrie für gewählte Kandidaten, abgelehnte Gründe, Death-Heat und Spawn-to-Action erfassen.
3. Bot-Kampfverhalten mit Objective-Routing koppeln, ohne den bestehenden Lyra-Kampf zu überschreiben.
4. echte Capture-/Kill-/Respawn-Telemetrie protokollieren und Waffen/Movement nur anhand gemessener Werte nachbalancieren.
5. Capture anschließend aus dem Elimination-Unterbau in eine eigene Spandau-Strike-Lyra-Experience überführen.
