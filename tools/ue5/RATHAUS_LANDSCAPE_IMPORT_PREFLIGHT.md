# Rathaus native Landscape: R16 import preflight

Scope: non-UE preparation only. No Landscape actor, collision or gameplay PASS is claimed.

Source: `ue5/SpandauStrike/SourceData/Rathaus/rathaus_dgm1_height_513.json` and `convert_rathaus_dgm_obj_to_r16.js`.

- 513 x 513 unsigned 16-bit little-endian samples (263169 vertices, 526338 bytes).
- Source OBJ X and Y span -500 to +500 metres, sampled in rows from Y=-500 to +500 and columns X=-500 to +500. Grid interval = 100000 / 512 = **195.3125 cm**.
- Source height z in metres is encoded as `round(32768 + z * 128)`. Unreal Landscape at Z scale **100** decodes height in cm as `(sample - 32768) / 128 * 100`; quantization is approximately 0.78125 cm.
- Source elevation range: -3.255 to +8 metres. Preserve source vertical datum. Do not normalize heights to zero.
- For a Landscape whose 513x513 grid is centred at world XY=(0,0), use actor XY=(0,0) and XY scale=(195.3125,195.3125). Verify in UE with four corner traces at approximately (-50000,-50000), (50000,-50000), (-50000,50000), (50000,50000) cm. If the actor pivot/import mode differs, compute and document its actual world transform before saving.
- Set Landscape Z scale to 100 and verify sample-derived Z at several known points against the existing DGM mesh. Check for swapped axes or flipped rows, not just matching bounds.
- Require actual `LandscapeHeightfieldCollisionComponent` / Landscape collision at runtime, Pawn-blocking and trace hits naming the Landscape component. A static-mesh `ComplexAsSimple` setup is not sufficient evidence.
- Preserve v84 baseline and all untracked validation maps. Do not delete or overwrite existing `.umap` files. Use one exclusive UE integration session after verified local-idle clearance.
- Acceptance still requires 15 bots plus human, capsule and ground traces, 0/5/15/30/60-second standing, movement, respawn, no falls and real screenshots.
