# Visual Master Standard — 135er Spandau Defeat

Status: **binding art direction** · current graphics pass: **0.5.1-sharp-ingame**.

The approved map-preview images are master references for final graphical output. They define composition, density, lighting, readability, first-person weapon framing and HUD language. They are targets for authored UE5 production art; they are not presented as captured screenshots of the current procedural graybox.

## Rendering target

- Unreal Engine 5.8 desktop renderer
- photorealistic PBR material response
- Nanite for suitable authored environment meshes
- Lumen GI/reflections
- Virtual Shadow Maps
- TSR
- volumetric fog / smoke integration
- World Partition/HLOD for final authored maps
- 60 FPS gameplay target on recommended PC hardware
- dedicated server remains render-free

The production sharpness baseline is stored in [../game/config/SharpIngame.ini](../game/config/SharpIngame.ini). Public screenshots must follow [INGAME_CAPTURE_STANDARD.md](INGAME_CAPTURE_STANDARD.md).

## Sharp first-person presentation

- native 100% screen percentage minimum
- TSR history resolution 200% for showcase captures
- 16× anisotropic filtering
- neutral texture mip bias and fully loaded textures
- restrained sharpening only
- no motion blur during normal FPS presentation
- no chromatic aberration
- no gameplay depth-of-field that obscures targets
- increased LOD/view distance for captured production frames
- no artificial sharpening halos or low-resolution JPEG masters

## Camera and first-person presentation

- 16:9 master composition
- natural first-person eye height
- weapon occupies the lower-right third without blocking the main route
- restrained field of view; no fisheye presentation
- teammates form readable silhouettes and visually guide players toward objectives

## HUD master

Implemented in `ASDHUD`:
- blue team tickets left, red team tickets right, match clock centered
- A/B/C ownership row below the score bar
- compact local minimap lower-left
- map/location identity near the minimap
- live magazine/reserve ammo and player health lower-right
- translucent dark backing only where needed
- no browser-game UI and no screenshot-only dummy counters

All displayed gameplay values must come from live game state.

## Lighting master

Implemented baseline in `ASDVisualDirector`:
- warm low-angle treatment for WWII/urban maps
- colder late-Cold-War treatment for Teufelsberg
- restrained bloom and vignette
- volumetric fog for smoke/haze
- slightly conservative exposure so fire, muzzle flashes and sky retain detail

The same sunset must not be copied onto every map. The requirement is cinematic realism plus competitive readability.

## Master map identities

| Map | Primary visual cue |
|---|---|
| Rathaus Spandau | civic square, tram/street cover, landmark tower |
| Zitadelle | fortress/courtyard massing, brick/stone, water approaches |
| Staaken | rail corridor + suburban street |
| Rodelberg | elevation, trenches, wooded hill |
| Kiesteich | water edge, reeds, park routes |
| Falkenhagener Feld | housing estate, broad lanes, concrete massing |
| Lynarstraße | close urban choke points, shops, tram-street language |
| Wröhmännerpark | riverside park, stone/iron furniture, tree canopy |
| Freiheit | rail yard, cranes, warehouses, industrial haze |
| Fort Hahneberg 1945 | brick fortification, earthworks, casemate approaches |
| Teufelsberg Cold War | radomes, communications structures, Cold-War equipment |
| Flugplatz Gatow 1945 | hangars, apron/runway, aircraft/airfield cover |

Remaining historical variants inherit the nearest parent master until a dedicated image is approved.

## Authenticity rule

Historical art may be period-authentic, but fictional combat must not be described as documented history. Environment art should preserve recognizable local identity before spectacle.
