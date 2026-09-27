# In-game image standard

Status: **binding for public screenshots and map showcase images**.

The repository must not present low-resolution concept thumbnails as if they were final gameplay captures. Public in-game images must be captured from the UE5.8 client build with the live HUD and the same rendering path used in normal play.

## Capture quality

- native 2560×1440 minimum; 3840×2160 preferred for master captures
- PNG master files; JPEG/WebP only for derived web previews
- 100% screen percentage minimum
- TSR history at 200% for showcase captures
- 16× anisotropic filtering
- no negative texture quality bias
- full-resolution textures loaded before capture
- Nanite, Lumen, Virtual Shadow Maps and volumetric effects enabled where the map uses them
- motion blur, chromatic aberration and gameplay depth-of-field disabled for readability
- restrained sharpening only; no halo-producing oversharpening

## Gameplay authenticity

Every screenshot labeled **in-game** must be captured from a running map. HUD values, weapon state, objectives, tickets and health must be live game state. Concept art remains clearly labeled as concept art.

## Required first production set

1. Rathaus Spandau
2. Zitadelle Spandau
3. Falkenhagener Feld
4. Freiheit / industrial rail
5. Fort Hahneberg 1945
6. Teufelsberg Cold War

For each map, capture one overview/combat lane frame and one close material/detail frame.

## Repository layout

Final masters: `media/ingame/<map>/<name>-4k.png`

Web previews: `media/ingame/<map>/<name>-1440p.webp`

Do not replace a master with a recompressed thumbnail.
