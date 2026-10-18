# Spandau Strike – Playable Capture Milestone

## Stand
Der aktuelle Gameplay-Teststand ist **Rathaus v75 Front Spawns**. v73 bleibt der technische Ein-Sektor-Checkpoint, v74 die erste vollständige Vier-Sektor-Runde. v75 koppelt Respawns an die wandernde Front und besitzt inzwischen die erste echte Spawn-Sicherheitswertung.

## Runtime-Klassen
- `ASpandauCapturePoint`: serverautoritatives Capture, Contest-Pause, 45-s-Baseline, Spieler-Speedup bis 4, verzögerter Fortschrittsabbau, replizierter Zustand und Runtime-Debuganzeige.
- `ASpandauCaptureDirector`: vier Sektoren, je zwei notwendige Punkte, Angreifer-Tickets, 20-s-Sektorwechsel, Siegzustand, 10-s-Team-Respawnwellen, Bot-Objective-Routing und Recent-Death-Heat.
- `ULyraPlayerSpawningManagerComponent`: erkennt die aufgelösten Capture-Teams, filtert Respawns nach aktivem Sektor/Attacker/Defender und erzwingt die Spawn-Sicherheitswertung vor dem Lyra-Blueprint-Hook; vollständig unsichere Frontsets fallen kontrolliert auf die Basis-Spawns zurück.
- `ALyraCharacter`: meldet serverseitig den Todesort direkt beim Start der echten Lyra-Death-Sequenz an den CaptureDirector. Dadurch stammt Death-Heat jetzt von realen Toden und nicht nur von erzwungenen Restarts.
- `ALyraHUD`: minimales Test-HUD für Sektor, Tickets, Respawn-Welle sowie A/B-Zustand und Capture-Fortschritt.
- `ALyraGameMode`: Capture-Runden leiten Respawn-Anforderungen an den CaptureDirector weiter; der eigentliche Todesort wird nicht mehr im Restart-Pfad ermittelt.

## v75 Front-Spawns
Map:
`/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS`

Basis ist v74. Die acht bisherigen sicheren LyraPlayerStarts bleiben als Fallback erhalten. Zusätzlich gibt es **16 Front-Spawns**: pro Sektor je zwei für Angreifer und zwei für Verteidiger. Sie tragen Daten-Tags (`SSSpawn.Attacker`/`SSSpawn.Defender` + `SSSpawn.Sector.N`). Die Spawn-Auswahl wird zur Laufzeit mit den tatsächlich von Lyra vergebenen Team-IDs verknüpft und verwendet keine fest eincodierten Teamnummern.

Damit wandern die Respawns mit der Front. Nach dem Sektorwechsel wird automatisch der passende Spawn-Satz für den neuen Frontabschnitt verwendet. Fehlen passende Front-Spawns oder ist ein Team noch nicht aufgelöst, bleibt der normale Lyra-Fallback aktiv.

## Capture Round
Vier Frontsektoren sind angelegt, jeweils mit A/B. Ein Sektor gilt erst als genommen, wenn beide Punkte erobert wurden. Danach: +50 Angreifer-Tickets, 20 Sekunden Übergang und Aktivierung der nächsten Front. Nach Sektor 4 gewinnen die Angreifer.

## Respawn und Tickets
- Team-Respawnwelle: 10 Sekunden.
- Nur **echte Lyra-Tode** werden serverseitig in die nächste Welle eingereiht. Der Character markiert den Controller beim `OnDeathStarted`; reine Lyra-Runden-/Phasenresets umgehen die Capture-Welle.
- Erst bei erfolgreichem Angreifer-Respawn nach einem echten Tod wird ein Ticket abgezogen. Der Warmup→Playing-Reset darf dadurch keine Tickets mehr verbrauchen.
- Verteidiger respawnen ohne Ticketverbrauch.
- Bei 0 Angreifer-Tickets werden keine weiteren Angreifer-Respawns freigegeben.
- Respawns werden nach Teamrolle und aktivem Frontsektor auf die markierten Front-Spawns gefiltert.

## Spawn-Sicherheit
Die Auswahl bewertet jetzt drei Dinge gemeinsam:
1. **Direkte Gegnernähe:** Startpunkte innerhalb von 12 m zu einem lebenden Gegner werden verworfen.
2. **Direkte Feindsicht:** Startpunkte mit Enemy-Line-of-Sight werden verworfen.
3. **Recent-Death-Heat:** Todesorte werden 15 Sekunden lang gespeichert. Innerhalb eines Radius von 25 m erzeugen sie eine mit Alter und Entfernung abfallende Strafwertung. Mehrere frische Todesfälle addieren sich.

Unter den verbleibenden Kandidaten gewinnt der Start mit der besten Kombination aus Gegnerabstand und niedriger Death-Heat. Die Sicherheitswertung läuft jetzt **vor** dem Lyra-Blueprint-Hook und kann dadurch nicht mehr von dessen eigener Startwahl umgangen werden. Werden sämtliche Frontkandidaten verworfen, wird dies explizit protokolliert und auf die acht Basis-Spawns zurückgefallen. Damit soll die Front mitwandern, ohne dass ein gerade beschossener Spawn stumpf weiter Menschen ausspuckt.

## Bots
Alle zwei Sekunden wird für lebende Bots das aktuelle Objective neu bewertet. Angreifer und Verteidiger laufen zu offenen A/B-Punkten des aktiven Sektors. Die ShooterCore-Assets wurden zusätzlich geprüft: der Behavior Tree arbeitet mit dem Blackboard-Key **`TargetEnemy`**, `BTS_SetFocus` und `BTS_Shoot`. Sobald Lyra entweder bereits `TargetEnemy` gesetzt hat oder einen feindlichen `FocusActor` hält, setzt der CaptureDirector für diesen Bot bewusst keinen neuen `MoveToLocation`-Befehl ab; der Routing-Log weist solche Fälle als `combatHeld` aus. Damit bleibt Objective-Routing der Navigator und Lyra die Kampf-KI. Der neue Combat-Probe setzt nach einem echten Wellen-Respawn kontrolliert `TargetEnemy`/Focus und nutzt anschließend denselben ShooterCore-Eingang wie `BTS_Shoot`: das Gameplay-Event **`InputTag.Weapon.Fire`**. Der Headless-Gate hat damit `combatHeld=1` sowie echten Schaden im zentralen `ULyraDamageExecution` nachgewiesen; der Combat-Pfad ist damit nicht mehr nur indirekt über Blackboard/Focus verifiziert.

## HUD
Oben mittig zeigt das funktionale Test-HUD Sektor x/4, Angreifer-Tickets, Zeit bis zur nächsten Respawn-Welle sowie A/B-Status und Capture-Prozent. Das ist bewusst kein Final-UI.

## Start
`tools/ue5/launch_rathaus_v75_front_spawns.ps1`

Standard: Lyra Shooter Elimination als Waffen-/Pawn-/Bot-Unterbau, 15 Bots. Unsere Capture-, Respawn-, Ticket-, HUD-, Objective- und Front-Spawn-Runtime läuft darüber.

## Automatische Gates
- Bevorzugt: `tools/ue5/run_rathaus_v75_front_spawn_headless_check.py`; der PowerShell-Einstieg `run_rathaus_v75_front_spawn_headless_check.ps1` delegiert nur noch an denselben Runner.
- statische Map-Prüfung: 24 PlayerStarts gesamt, davon 16 Front-Spawns, 8 CapturePoints, 1 Director, je exakt 2 Attacker- und 2 Defender-Spawns pro Sektor.
- Runtime-Prüfung: Teams aufgelöst, 15 Bots zu Objectives geroutet und anschließend ein echter Lyra-Bot-Tod über `DamageSelfDestruct()` ausgelöst.
- Der normale Gate verlangt Death-Heat, Respawn-Queue, Wellen-Respawn, **Spawn-to-Action** sowie entweder einen sicheren Frontspawn oder einen protokollierten Sicherheits-Fallback auf Basisspawns. Im optionalen `--combat-probe`-Modus ersetzt der bestätigte **Spawn-to-Combat**-Pfad die Objective-Action-Pflicht, weil der Bot absichtlich im Kampf gehalten wird.
- Bei Läufen ab 45 Sekunden muss zusätzlich der Warmup→Playing-Wechsel beobachtet werden und mindestens ein Nicht-Todes-Restart den Capture-Respawn explizit umgehen. Die alte Fehler-Signatur `spawned=16 attackerTicketSpawns=8` lässt den Gate scheitern.
- Spawn-to-Action misst pro respawntem Bot die Zeit bis zur ersten erfolgreich angenommenen Objective-Bewegung. Bestätigte normale Probeläufe lagen bei etwa `0,16–0,20 s`.
- Spawn-to-Combat ist im zentralen `ULyraDamageExecution` instrumentiert und misst den ersten tatsächlich verursachten Schaden nach dem Respawn. Der Combat-Probe hält den respawnten Bot an seinem echten Spawn, setzt ein gegnerisches Testziel kollisionssicher in freie Sichtlinie und nutzt anschließend den echten ShooterCore-Eingang `InputTag.Weapon.Fire` bis zum realen Treffer.
- Der Runner schreibt `spawn_to_combat_seconds`, `spawn_to_combat_damage` und `spawn_to_combat_target` maschinenlesbar in den JSON-Report. `tools/ue5/collect_spawn_to_combat_baseline.py` führt mehrere vollständige Combat-Gates aus und erzeugt daraus Min/Mean/Median/Max-Baselines.
- Erste bestätigte 3er-Baseline: **3/3 bestanden**, jeweils `0,01 s` bis Erstschaden und `36` Schaden, bei allen Läufen `unexpected_bad_count=0`. Der reproduzierbare Testkontakt lag bei **350 cm**; Abstand und Zieltyp werden jetzt ebenfalls im Gate-Report erfasst. Der Baseline-Report liegt unter `Saved/Reports/spawn_to_combat_baseline.json`.
- Bekannte rein visuelle `-nullrhi`-Warnungen von Spawn-/Death-Cues sowie Muzzleflash, Hülsenauswurf, Tracer und Decals werden separat gezählt. Andere FellOutOfWorld/KillZ/Spawn/Fatal/Ensure-/Script-Fehler lassen den Gate weiterhin scheitern.
- Letzter bestätigter Combat-Gate-Lauf: kompletter Death→Heat→Queue→Safety→Respawn→Combat-Zyklus bestanden, Kampfpriorität mit `combatHeld` bestätigt, echter Schaden erzeugt, Warmup-Reset ohne Capture-Ticketverlust und `unexpected_bad_count=0`.

## Nächste Gameplay-Schritte
1. v75 sichtbar anspielen und Front-Spawn-Laufwege sowie tatsächliche Sichtlinien prüfen.
2. Die reproduzierbare Spawn-to-Combat-Baseline um echte Distanz-, Waffen- und Gegnerkontakt-Samples erweitern.
3. Bot-Kampfverhalten mit Objective-Routing weiter koppeln, ohne den bestehenden Lyra-Kampf zu überschreiben.
4. echte Capture-/Kill-/Respawn-Telemetrie weiter verdichten und Waffen/Movement nur anhand gemessener Werte nachbalancieren.
5. Capture anschließend aus dem Elimination-Unterbau in eine eigene Spandau-Strike-Lyra-Experience überführen.
