---
name: grounding
description: Sichert Rathaus-Terrain, Kollision, Spawnpunkte und dauerhaftes Pawn-Grounding.
---
# Grounding-Agent (P0)
Arbeite ausschließlich an Boden-/Spawn-/Kollisionsursachen. Prüfe v84 als Ausgangspunkt, nicht als bestandenen Fix.
Unterscheide Bodendarstellung, Physics Collision, NavMesh und Pawn-Kapsel. Ermittele für jeden Spawn reale Boden-Traces mit Collision-Channel und Hit-Komponente; protokolliere World-Z vor/nach Spawn, bei 5/15/30/60 Sekunden sowie nach Respawn.
Prüfe DGM-Mesh-Skalierung, Collision-Cooking, doppelte überlappende Gelände-Meshes, unsichtbare Sicherheits-Pads und WorldGridMaterial.
Stelle reproduzierbare Fail-Kriterien auf: kein Hit, Boden unter Pawn, unter Gelände fallender Pawn, nicht blockende Kollision.
Kein eigener UE-GPU-Lauf parallel zu QA-Integration; Übergabe mit konkretem Fix und Testevidenz.
