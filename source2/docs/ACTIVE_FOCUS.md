# Active production focus

Updated: 2026-10-02

Current production target: **Rathaus Spandau only**.

Source map: `rathaus_spandau.vmap`
Unreal reference: `rathaus_spandau_playable_v1`

All other maps are frozen until Rathaus Spandau passes runtime, gameplay and visual QA in both engines.
Do not start multi-map compilation or rollout while this focus is active.

## Verbindliche Map-Bau-Regel

Für jede Map gilt ab sofort:
1. Reale/ bekannte 3D- und Geodaten zuerst (Berlin3D, LoD2, DGM1, Straßen, Wasser).
2. Daraus saubere Spielgeometrie ableiten; keine frei erfundene finale Architektur.
3. Gameplay-Layer danach: Spawns, Ziele, Cover, Sichtachsen, Collision, Nav.
4. Masterbilder zuletzt als Look-/Atmosphäre-/Setdressing-Referenz.

Die reale Geometrie hat Vorrang vor Konzept-/KI-Bildern.
