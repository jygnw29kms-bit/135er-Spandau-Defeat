# Epic Developer Assistant - aktuelle Frage

Wir arbeiten an einem Unreal Engine 5.8.3 Projekt unter Windows 10/11 und brauchen den von Epic empfohlenen Weg fuer reproduzierbares Performance-Profiling einer echten gerenderten Gameplay-Map mit Bots.

Projektkontext:
- UE 5.8.3
- DX12
- Gameplay-Map: `/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v77_ROADS_V85_GAMEPLAY`
- 15 Bots
- komplette Capture-Runde ist bereits funktional getestet
- MapCheck 0 Fehler / 0 Warnungen
- Headless/NullRHI-Gates sind gruen

Problem:
PresentMon 1.8 startet und beendet Aufzeichnungen, liefert in unserer Session-/Task-Konstellation aber keine nutzbare CSV. UE5.8 eigener CSV Profiler liefert dagegen eine ca. 5,3 MB grosse Datei mit 2400 Frames in einem globalen Profiling-Ordner.

Fragen:
1. Was ist in UE 5.8.3 der offiziell empfohlene CLI-/Automation-Weg, um nach einer Warmup-Phase z. B. 30 Sekunden echte DX12-Gameplay-Frametimes automatisiert aufzunehmen?
2. Welche CSV-Profiler-Flags bzw. Console Commands sind dafuer vorgesehen?
3. Wie erzwingt man einen projektlokalen Output-Pfad bzw. wie laesst sich der resultierende Pfad verlaesslich ermitteln?
4. Welche CSV-Spalten sollen fuer CPU Game Thread, Render Thread, RHI Thread und GPU als primaere Bottleneck-Metriken ausgewertet werden?
5. Wie empfiehlt Epic, 1%-Low / 0,1%-Low bzw. Hitches aus UE-Profiler-Daten zu beurteilen?
6. Ist fuer einen automatisierten Regression-Gate CSV Profiler oder Unreal Insights/Trace in UE 5.8.3 die bessere Wahl?

Bitte nur UE-5.8-kompatible Vorgehensweisen nennen und relevante Epic-Dokumentation/API-Referenzen angeben. Wenn sich Flags oder APIs zwischen Versionen geaendert haben, bitte explizit darauf hinweisen.
