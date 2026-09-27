# F-14 RC FDM – Bauplan R2

## 1. Konstruktionsziel

Die R2 wird als RC-Flugmodell neu aufgebaut und nicht als massiv skalierte Display-F-14. Außenkontur und charakteristische Proportionen orientieren sich an der realen F-14, während Innenstruktur, Wandstärken, Teilung, Schwenklager, EDF-Kanäle und RC-Einbauten speziell für FDM und Flugbelastung konstruiert werden.

### Zielwerte

| Merkmal | Ziel |
|---|---:|
| Rumpflänge | ~950 mm |
| Spannweite ausgefahren | ~900 mm |
| Schwenkbereich | 20°–60° |
| EDF | 2 × 50 mm |
| Abflugmasse | Ziel 1.6–2.0 kg, nach Prototyp zu bestätigen |
| Akku | 4S 3300–4000 mAh |
| Kanäle | 6–8 |
| Drucker | Bambu Lab P2S |
| Hauptmaterial | PETG |

## 2. Baugruppen

### A. Nase / Cockpit
- abnehmbare Nasenspitze
- vorderes Rumpfsegment
- Cockpit-/Akkuklappe
- Akkuwanne mit verschiebbarem Akku zur Schwerpunktkorrektur
- Empfängerbereich getrennt von den ESC-Leitungen

### B. Mittelrumpf / Wing Box
- hoch belastete zentrale Wing-Box
- M4/M5 Pivotachsen mit Buchsen oder Lagern
- CFK-Quer-/Längsverstärkung
- zentraler Schwenkservo
- mechanisch gekoppelte linke/rechte Flügel
- mechanische Anschläge bei ausgefahren und maximal geschwenkt

### C. Schwenkflügel
- linker/rechter Flügel als leichte Hohlstruktur
- CFK-Holmkanal
- verstärkte Wurzel um den Pivot
- Schwenkbewegung ca. 20° bis 60°
- aerodynamische Wing-Gloves decken die Wurzel ab

### D. EDF-/Hecksektion
- zwei getrennte 50-mm-EDF-Kanäle
- möglichst glatte Einlauf- und Auslassflächen
- je EDF eigener ESC
- Servicezugang von unten/oben
- ESC-Kühlung im Luftstrom vorsehen

### E. Leitwerk / Steuerflächen
- zwei Tailerons als primäre Nick-/Rollsteuerung
- je Taileron eigener Servo
- zwei Seitenleitwerke
- Seitenruder optional separat anlenkbar
- Doppelservo-Tailerons elektronisch gemischt

## 3. Aufbau-Reihenfolge

1. Alle gedruckten Teile entgraten und Passflächen trocken zusammenstecken.
2. CFK-Verstärkungen ablängen und ohne Kleber probeweise einsetzen.
3. Wing-Box mit Pivotachsen und Lager/Buchsen montieren.
4. Schwenkservo und zentrale Kopplung montieren; Flügel zunächst ohne Außenhaut bewegen.
5. Mechanische Endanschläge prüfen. Servo darf die Anschläge nicht elektrisch erzwingen.
6. Linken und rechten Flügel mit CFK-Holm montieren.
7. EDFs und ESCs in die Heckbaugruppe einsetzen.
8. Taileron-Servos und Gestänge spielfrei montieren.
9. Rumpfsegmente trocken zusammenfügen; Kabelwege prüfen.
10. Empfänger, BEC und Akkuwanne installieren.
11. Schwerpunkt über Akkuverschiebung einstellen.
12. Erst nach vollständiger Funktionsprüfung die endgültigen Rumpfverbindungen verkleben/verschrauben.

## 4. Schwenkflügel-Mechanik

Die Mechanik wird nicht direkt über gedruckte Zahnflächen als einzige tragende Struktur ausgeführt. Vorgesehen sind:

- Metall-Pivotachsen
- gedruckte, verstärkte Lagerblöcke
- austauschbare Gleitbuchsen oder Miniaturlager
- zentrale Servo-Kurbel
- zwei symmetrische Anlenkgestänge
- mechanische Endanschläge
- CFK-Verstärkung der Flügelwurzel

### Fail-Safe

Bei Ausfall der Schwenkfunktion müssen die Flügel mechanisch in einer flugfähigen Stellung bleiben. Für die ersten Flüge wird die Schwenkfunktion auf einen kleinen getesteten Bereich begrenzt.

## 5. Schwerpunkt / Erstflug

Der endgültige Schwerpunkt wird **nicht aus dem Renderbild abgeleitet**. Er wird nach vollständiger CAD-Massenbilanz und anschließend am real gebauten Modell bestimmt.

Für den Erstflug:
- Flügel in weitgehend ausgefahrener Stellung
- kein Einziehfahrwerk nötig
- reduzierte Ausschläge
- Expo am Sender
- Schwenkfunktion zunächst gesperrt oder nur in großer Höhe verwenden
- Schwerpunkt konservativ kopflastig beginnen und schrittweise erfliegen

## 6. 3D-Aufbauplan

Die endgültigen Explosions- und Montagebilder werden aus dem **gleichen OpenSCAD/STL-Stand** erzeugt. KI-Konzeptbilder dürfen nur als optische Referenz dienen und werden nicht als technische Bauansicht gekennzeichnet.
