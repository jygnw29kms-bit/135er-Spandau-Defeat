# F-14 RC FDM – RC-Hardware R2

Dies ist die **Zielhardware für den R2-Prototyp**. Exakte Komponenten können nach Schub-, Masse- und Schwerpunktmessungen noch angepasst werden.

## Antrieb

| Komponente | Menge | Zielvorgabe |
|---|---:|---|
| EDF | 2 | 50 mm, 4S, ausgewuchtet |
| Motor | 2 | passend zum jeweiligen 50-mm-EDF, typ. ca. 4500–5200 KV bei 4S |
| ESC | 2 | 40–50 A brushless, mit ausreichender Kühlung |
| Akku | 1 | 4S LiPo, 3300–4000 mAh, mind. 45C |
| Hauptstecker | 1 | XT90 oder hochwertiger XT60 je nach gemessenem Gesamtstrom |
| Stromverteiler | 1 | Y-Kabel/PDB für beide ESC |

### Ziel für den Antrieb
Der statische Gesamtschub soll vor dem Erstflug **gemessen** werden. Ziel ist ein Schub-Gewichts-Verhältnis, das sichere Starts und Steigflug erlaubt; die endgültige Freigabe erfolgt anhand des realen Abfluggewichts.

## Servos

| Funktion | Menge | Empfehlung |
|---|---:|---|
| Tailerons | 2 | Digital Metal Gear, ca. 12–17 g, ≥3 kg·cm |
| Seitenruder optional | 2 | Digital Metal Gear, ca. 9–12 g |
| Schwenkflügel | 1 | Standard/HV Metal Gear, **mind. 20–25 kg·cm** |
| Fahrwerk optional | 1 Set | elektrisches Retract-System passend zur Modellmasse |

Für den Schwenkservo ist Drehmoment wichtiger als Geschwindigkeit. Die Flügelmechanik darf nicht so konstruiert werden, dass der Servo permanent gegen einen Anschlag arbeitet.

## Funkanlage

- Empfänger: **mindestens 8 Kanäle empfohlen**
- Sender mit:
  - Elevon/Taileron-Mix
  - frei programmierbaren Kurven
  - Servo-Speed für Flügelschwenkung
  - Endpunkt-/Travel-Einstellung
  - Fail-Safe
- Telemetrie empfohlen:
  - Empfängerspannung
  - Akku-Spannung
  - optional Stromsensor

## BEC / Stromversorgung

Für mehrere Digitalservos ist ein separates leistungsfähiges BEC sinnvoll:

- 6–8.4 V je nach Servo
- mindestens 5 A Dauer, höhere Spitzenreserve
- Schwenkservo und Tailerons dürfen den Empfänger nicht durch Spannungseinbruch resetten

## Mechanische Hardware

- 2 × Pivotachse M4/M5, Stahl
- passende selbstsichernde Muttern
- Unterlegscheiben / Distanzscheiben
- Kugelköpfe M2/M3
- Gewindestangen M2/M3
- hochwertige Servoarme
- CFK-Rohre/-Stäbe für Flügelholme
- CFK-Stäbe für Rumpflängsverstärkung
- Messing-/POM-Buchsen oder Miniaturlager für Schwenkpivots
- M2/M3 Heat-Set Inserts für Wartungsklappen
- M2/M3 Schrauben in mehreren Längen

## Verkabelung

- EDF-Leistungskabel kurz halten
- ESCs nahe an den EDFs
- Akkuleitung ausreichend dimensionieren
- Servo-/Empfängerleitungen getrennt von Hochstromleitungen führen
- alle Steckverbinder gegen Vibration sichern

## Optionales Fahrwerk

Für R2 zunächst **optional**. Ein Belly-/Handstart-fähiger Prototyp reduziert Masse und Komplexität. Retracts erst nach erfolgreicher Flugerprobung der Grundzelle integrieren.
