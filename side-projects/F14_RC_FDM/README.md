# F-14 RC FDM

Eigenständiges RC-Modellbau-Nebenprojekt im Repository **135er-Spandau-Defeat**.

> **Nicht Bestandteil des Spiels.**  
> Keine Source-2-, Map-, Server-, Build- oder Deployment-Abhängigkeiten zum eigentlichen Spandau-Strike/Defeat-Projekt.

## Ziel

Eine **neu konstruierte, FDM-druckfähige RC-F-14** mit funktionsfähigen Schwenkflügeln, die sich optisch an der realen Grumman F-14 orientiert, konstruktiv aber als leichtes RC-Flugmodell ausgelegt wird.

Der neue Master wird **parametrisch in OpenSCAD** aufgebaut. STL-Dateien gelten erst dann als freigegeben, wenn sie exportiert, auf geschlossene/manifold Meshes, Abmessungen, Druckbett-Tauglichkeit und Montagepassungen geprüft wurden.

## Zielabmessungen R2

- Länge: ca. **950 mm**
- Spannweite ausgefahren: ca. **900 mm**
- Schwenkbereich im Modell: ca. **20°–60°**
- Antrieb: **Twin 50 mm EDF**
- Material: primär **PETG**, P2S-Druckplatten
- Verstärkungen: CFK-Rohre/-Stäbe an Flügeln und Rumpf
- Steuerung: Tailerons + optional Seitenruder
- Einziehfahrwerk: optional, nicht für den Erstflug erforderlich

## Dokumentation

- [3D-/Montage-Bauplan](docs/BUILD_PLAN.md)
- [RC-Hardware und Elektronik](docs/RC_HARDWARE.md)
- [P2S PETG Druckvorgaben](docs/P2S_PETG_PRINTING.md)
- [Konstruktions- und Prüfstatus](docs/STATUS.md)

## Projektstruktur

- `scad/` – parametrische OpenSCAD-Quellen
- `stl/` – ausschließlich geprüfte Export-STLs
- `docs/` – Bauplan, Hardware, Druckparameter und Prüfstatus
- `renders/` – Ansichten aus dem jeweils zugehörigen SCAD/STL-Stand
- `releases/` – versionierte, freigegebene Druckstände

## Wichtiger Statushinweis

Der bisherige R1-Meshsatz wird **nicht als finale Flugversion** behandelt. Die F-14 wird für R2 neu in OpenSCAD modelliert. Bis zur abgeschlossenen Struktur-, Schwerpunkt- und Flugerprobung ist der Stand als **Prototype / Ground-Test** zu betrachten.
