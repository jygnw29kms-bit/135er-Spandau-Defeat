# Rathaus v84 Grounding: reproduzierter P0-Fehler (2026-11-07)

Status: **FAIL**, niemals als final spielbar deklarieren.

## Umgebung
Lucas-PC `DESKTOP-SMN4ATU`, UE 5.8.3 LyraEditor, Level `LV_RathausSpandau_REAL_v84_GROUND_LOCK_QA`, 15 Bots + 1 menschlicher Pawn, `-nullrhi -SpandauGroundProbe`.

## Reproduzierbare Ausführung
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/ue5/run_rathaus_v84_ground_smoke.ps1 -RuntimeSeconds 35`

## Befunde
1. Erster Lauf vor Double-Sided-Änderung: `v84_ground_smoke_20261107_163658.json`, 128 Proben, 101 FAIL, 99 ohne Bodentreffer. Spielerzentrum bei t=5.2 s: Z=-12094.8 cm, t=20.2 s: Z=-72105.6 cm. **Echtes Durchfallen**.
2. DGM BodySetup: `ComplexAsSimple`, aber `double_sided_geometry=False` (Report `v84_dgm_collision_asset_inspect.json`).
3. Kontrollierte Änderung: DGM `double_sided_geometry=True`, erfolgreich gespeichert in `SM_RathausSpandau_DGM1_v86_GAMEPLAY1000.uasset`. Report `v84_dgm_double_sided_apply.json`.
4. Zweiter Lauf `v84_ground_smoke_20261107_164018.json`: 96 Proben, 38 FAIL, 14 ohne Bodentreffer. Verbesserung, **nicht vollständig gelöst**.
5. Dritter Lauf mit erweitertem Collision-Logging `v84_ground_smoke_20261107_164233.json`: 80 Proben, 25 FAIL, 10 ohne Bodentreffer. Hit-Komponente teils `StaticMeshActor_11` mit `BlockAll`, `enabled=3` (QueryAndPhysics), `pawnResponse=2` (Block), `blockingHit=1`. Einige Pawns sinken trotzdem trotz positiver Visibility-Raycasts. Andere starten an einzelnen Positionen ohne Terrain-Hit. Echte Kapselbewegungs-Kollision ist nicht flächendeckend stabil.

## Nächste technische Maßnahmen
- Visuelles DGM und begehbaren **Landscape-/Heightfield-Kollider** auseinanderziehen. Nur eine langfristig stabile Physical-Collision-Fläche statt vereinzelt wirkender statischer Mesh-Triangles.
- DGM Quell-OBJ (513x513 Höhenraster, 1000m) für eine echte Heightfield-Kollision importieren; physikalische Oberflächenhöhe und Visual-Mesh-Abweichungen entlang aller 24 PlayerStarts nachmessen. Nicht durch globale Z-Verschiebung vertuschen.
- Problem-Spawns `SS_SM_SPAWN_EAST_1` / `SS_FRONTSPAWN_S04_DEFENDER_01` und weitere negative Höhen gezielt prüfen. Bis dahin keine Fallback-Spawns auf unvalidiertem Boden.
- Laufzeitabnahme: 15 Bots + Spieler, Ground-Trace **und Pawn-Kapsel-Sweep**, mindestens 60 s, Laufen, Respawn, Navigationsziele; null FAIL über mehrere Seeds. Danach Ingame-Screenshot und GitHub-Stand aktualisieren.

## Beweise
Die JSON-Reports und Logs liegen lokal unter `ue5/SpandauStrike/Saved/Reports` bzw. `Saved/Logs`. Diese Verzeichnisse sind üblicherweise generierte Dateien, nicht automatisch auf GitHub. Kein PASS aus `FellOutOfWorld=0` ableiten: die Pawns wurden mit Z-Werten unter -70.000 cm bestätigt.

## Heightfield-Quelle vorbereitet
- `node tools/ue5/convert_rathaus_dgm_obj_to_r16.js` erzeugt ein geprüftes Unreal-Landscape-Raster `ue5/SpandauStrike/SourceData/Rathaus/rathaus_dgm1_height_513.r16` plus Metadaten-JSON.
- 513x513 Punkte, Weltbereich X/Y je -500..+500 m, Rasterabstand 1,953125 m, ZScale 100; Höhenspanne -3,255..8,0 m.
- **Noch keine Landscape-Collision in v84 eingebaut**. Dafür müssen Landscape-Import, Ausrichtung, physikalische Höhen und die erneuten 15-Bot-Tests bestätigt werden. Die R16 allein behebt kein Durchfallen.
