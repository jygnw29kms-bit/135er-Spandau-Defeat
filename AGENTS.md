# Spandau Strike: verbindliche Agentenregeln

## Einziger Entwicklungsrechner
- Spandau Strike wird ausschließlich auf Lucas PC (DESKTOP-SMN4ATU) entwickelt. Jens/BND und Server Büro nicht als Ausweich-Buildrechner nutzen.
- Windows-Konto `anony` ist das eigene Automations-/Arbeitskonto, NICHT Lucas. Seine Existenz oder aktiven Prozesse sind kein Beweis für Lucas' Nutzung.
- Vor GPU-lastigen Builds, UE5-Editor-Sessions oder Eingabesimulation echte lokale Nutzeraktivität möglichst zuverlässig erkennen. Bei nicht zuordenbaren lokalen Maus-/Tastatureingaben konservativ pausieren; eigene automatisierte Eingaben nicht mit Lucas verwechseln.
- Bei Offline-/Nutzungssperre keine neuen UE-Läufe starten. Keine unbewachten Endlosschleifen, die nach dem Chat weiterarbeiten.
- Nur UE5 als Engine; FreeCAD für CAD-Arbeiten. Der verbindliche Final-Master bzw. Referenz-Mockup hat Vorrang vor eigenmächtigen visuellen Interpretationen.

## Arbeitsorganisation
- Vier Fachrollen: `grounding`, `gameplay`, `visual`, `qa-integration`, siehe .github/agents/.
- Fachrollen dürfen Analysen parallel liefern, aber nur ein Integrator schreibt UE-.umap/.uasset und startet GPU/Editor zur selben Zeit. Kein gleichzeitiges Bearbeiten derselben Dateien.
- Jede Änderung muss vorhandene Assets/Tests erhalten; keine destruktiven Zurücksetzungen, kein pauschales Löschen fremder oder uncommitteter Änderungen.
- Arbeitsordner unter JL1976, sofern neue dauerhafte Ablagen angelegt werden; bestehende Repo-Pfade respektieren.

## Rathaus / Grounding: Blocker P0
- Das Fallen von Player- und Bot-Pawns durch den Boden ist NICHT behoben, bis ein echter Spieltest es nachweist.
- v84 Ground-Lock-QA ist nur ein Kandidat. 24 PlayerStarts wurden auf DGM-Höhe + 120 cm gesetzt; DGM `BlockAll`, `ComplexAsSimple`. Das bestätigt lediglich Setup, nicht persistente Kollisionswirkung.
- Keine reine Building-only-Visual-Probe als Gameplay-Abnahme.
- Künftige Abnahme: 15 Bots plus menschlicher Pawn, Spawn / 30-60 s Stand / Bewegung / Respawn, tatsächliche Z-Höhen und Trace zum Boden, zeitgestempelte Logs; bei jedem Sink/Fall FAIL.
- Die Startposition allein genügt ausdrücklich nicht, um Collision/Physik zu bestätigen.
- Neue Karte nie `final spielbar` nennen, bevor Spawn, Kollision, Navigation, Objectives, Stabilität und reale Ingame-Screenshots geprüft sind.

## Evidenz / Integration
- Jeder Agent liefert: geänderte Dateien, Kommandos, Testresultate, Risiken, reproduzierbaren nächsten Schritt.
- Auf v84 aufbauen, keine Versionen inflationär erzeugen.
- Screenshots nur als solche kennzeichnen, wenn sie tatsächlich aus UE-Spiel/Editor stammen. Neue Ingame-Bilder ins Repo/README integrieren, wenn verifiziert.
- `git status` vor und nach Änderungen prüfen; zunächst kleine, getrennte Commits; Push nur nach Prüfung. Keine leeren Fortschrittsmeldungen.
