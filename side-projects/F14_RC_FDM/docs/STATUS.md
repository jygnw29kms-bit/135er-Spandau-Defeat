# F-14 RC FDM – Status

## Aktuell

**R2 wird vollständig neu in OpenSCAD konstruiert.**

Der frühere R1-Satz dient nur als Entwicklungsreferenz und ist **nicht final flugfreigegeben**.

## Freigabekriterien für STL

Eine STL wird erst nach allen folgenden Prüfungen in den freigegebenen Satz übernommen:

- [ ] aus aktuellem SCAD-Master exportiert
- [ ] manifold / watertight
- [ ] keine Self-Intersections
- [ ] korrekte Maße
- [ ] P2S-Bauraum bzw. definierte Teilung geprüft
- [ ] passende Druckorientierung festgelegt
- [ ] mechanische Passungen geprüft
- [ ] Pivot-/CFK-/Servo-Schnittstellen geprüft
- [ ] Baugruppenkollisionen geprüft
- [ ] Masse für Schwerpunktmodell erfasst
- [ ] aus STL erzeugte Kontrollansicht geprüft

## Flugfreigabe

Zusätzlich erforderlich:
- [ ] EDF-Schub gemessen
- [ ] Gesamtstrom gemessen
- [ ] realer Schwerpunkt bestimmt
- [ ] Servo-Lasttest
- [ ] Schwenkmechanik Last-/Zyklentest
- [ ] Reichweitentest
- [ ] Boden-/Gleitversuch
- [ ] Erstflug
