# Source 2 production pipeline

## Decision

Source 2 / CS2 is the active engine/runtime for 135er – Spandau Defeat. Unreal Engine is no longer part of the active project.

## Toolchain

1. Counter-Strike 2 installation/runtime
2. CS2 Workshop Tools
3. Hammer for map authoring
4. Source 2 material/asset tools
5. Blender for Berlin geodata cleanup/reference prep
6. Linux CS2 dedicated server for multiplayer validation

## Geodata baseline

For maps based on real Berlin locations, establish scale and massing from real geodata before gameplay adaptation.

- Berlin LoD2 building model: primary building geometry reference.
- Berlin 3D Mesh 2025: detailed visual/spatial reference.
- Terrain and street data: alignment/context.
- Per-site anchors and capture radii: `source2/geodata/school_sites.json`.
- Full workflow: `docs/BERLIN_GEODATA_PIPELINE.md`.

Do not ship the dense Berlin mesh directly as game geometry. Rebuild or retopologize optimized Source 2 assets and respect the source license/portal terms.

## Map production

**Blockout**
- real-place silhouette and road/campus/fortress massing
- primary/secondary routes
- spawn separation
- A/B/C or mode-specific objectives

**Gameplay pass**
- cover cadence
- sightline control
- flanking routes
- objective timing
- performance-safe geometry

**Art pass**
- Spandau landmark fidelity
- Source 2 materials
- props/decals
- lighting
- fog/particles
- era-specific dressing

**Validation**
- runtime load
- objective behavior
- spawn safety
- navigation/bot compatibility where used
- dedicated-server test
- frame/readability review

**Capture**
- only captures from the running Source 2 project may be labeled in-game
- optical masters remain separate and clearly labeled

## Migration rule

Legacy Unreal-specific files, render profiles and source archives are retired and must not be used as implementation references.
