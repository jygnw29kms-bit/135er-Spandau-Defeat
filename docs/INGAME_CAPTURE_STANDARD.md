# In-game image policy

Status: **binding**.

For **135er – Spandau Defeat**, every public project image must be generated directly by the running Unreal Engine 5.8 game client.

## Allowed

- screenshots captured from a running UE5 map
- captures from actual game geometry, materials, lighting and effects
- real gameplay HUD/state when HUD is shown
- engine-generated cinematic shots using the same project content and renderer

## Not allowed

- concept art
- AI-generated images
- mockups
- external renders
- composited fake gameplay scenes
- placeholder screenshots
- images from another engine or unrelated project
- images that have not been rendered by the actual game project

No image may be presented on GitHub, the project website, documentation, release notes or promotional material unless its source is the running game engine.

## Capture quality

- 2560×1440 minimum; 3840×2160 preferred
- PNG master
- 100% native screen percentage minimum
- TSR history at 200% for showcase captures
- 16× anisotropic filtering
- full-resolution textures loaded
- Nanite, Lumen, Virtual Shadow Maps and project volumetrics active where applicable
- motion blur and chromatic aberration disabled for clear FPS presentation
- restrained sharpening only

## Authenticity

If HUD is visible, tickets, objectives, ammo, health and weapon state must come from live game state.

Public engine captures are stored under:

`media/ingame/<map>/`

Derived web previews may be generated only from those engine captures.
