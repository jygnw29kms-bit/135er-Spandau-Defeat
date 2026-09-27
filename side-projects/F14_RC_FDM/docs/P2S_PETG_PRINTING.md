# P2S PETG – Druckvorgaben für F-14 R2

## Grundprofil
- Drucker: Bambu Lab P2S
- Düse: 0.4 mm
- Material: PETG
- Layer: 0.20 mm Standard, 0.16 mm für Pivot-/Passungsteile
- Düsentemperatur: Startwert 240–250 °C, filamentabhängig kalibrieren
- Bett: ca. 75–85 °C
- Volumenstrom: konservativ, Qualität/Layerhaftung vor Geschwindigkeit
- Brim bei hohen/schmalen Teilen

## Leichtbau-Rumpf / Flügel
- 2–3 Perimeter
- 5–10 % Infill nur wo konstruktiv benötigt
- bevorzugt konstruktive Rippen/Stege statt hohes Infill
- Top/Bottom-Layer nur dort, wo geschlossene Haut erforderlich ist

## Strukturteile
Wing-Box, Pivotblöcke, Servo-Crank und hoch belastete Halter:
- 5–7 Perimeter
- 30–50 % Gyroid/Cubic
- 0.16–0.20 mm Layer
- Bauteilorientierung so, dass Layer nicht entlang der Hauptbruchlinie liegen

## Materialstrategie
PETG ist für Prototypen robust und schlagzäh. Hoch belastete Schwenkkomponenten werden dennoch mit Metallachsen und CFK ergänzt. Gedruckte Teile ersetzen keine metallischen Pivots.

## P2S-Druckplatten
Die R2-Platten werden erst nach abgeschlossenem SCAD-Export erzeugt. Jede Platte wird auf:
- 256×256-mm-Bauraum
- Kollisionen
- Druckorientierung
- Supportbedarf
- Profilgruppe
geprüft.
