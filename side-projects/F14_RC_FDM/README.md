# F-14 RC FDM

Separates RC-Modellbau-Nebenprojekt innerhalb dieses Repositories.

> **Nicht Bestandteil von 135er Spandau Defeat / Spandau Strike.**
> Dieser Bereich wird weder vom Source-2-Spiel noch von dessen Build-, Map-, Server- oder Release-Struktur verwendet.

## Ziel

FDM-druckfähiges RC-Flugmodell nach dem Formvorbild der Grumman F-14 mit funktionsfähigen Schwenkflügeln.

## Aktueller Konstruktionsstand

- ca. 950 mm Rumpflänge
- ca. 900 mm Spannweite bei ausgefahrenen Flügeln
- modularer FDM-Aufbau
- Schwenkflügel mit mechanischer Kopplung / Servo-Anlenkung
- CFK-Verstärkungen vorgesehen
- EDF-Antrieb vorgesehen
- Konstruktion und Flugerprobung noch in Entwicklung

## Verzeichnisstruktur

- `stl/` – druckbare Einzelteile und Baugruppen
- `docs/` – Bauplan, Stückliste, Druck- und Montagehinweise
- `renders/` – ausschließlich aus dem jeweiligen CAD/STL-Stand abgeleitete Kontroll- und Produktansichten
- `releases/` – gepackte, versionierte Druckstände

## Trennung zum Spielprojekt

Es bestehen bewusst **keine Imports, Build-Abhängigkeiten, Source-2-Pfade oder automatischen Deployments** zwischen diesem Verzeichnis und dem eigentlichen Spielprojekt.

Der visuelle F-14-Master dient als Formreferenz. Ein Render gilt nur dann als technische Projektansicht, wenn er aus dem dazugehörigen CAD/STL-Stand erzeugt wurde.
