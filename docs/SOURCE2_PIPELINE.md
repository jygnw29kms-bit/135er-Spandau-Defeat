# Source 2 production pipeline

## Decision

Source 2 / CS2 is one of the two active engine/runtime targets for 135er – Spandau Strike. Unreal Engine 5.8 / Lyra is developed in parallel from the same Berlin GIS / Blender master data, while this document covers only the Source 2 production path.

## Toolchain

1. Counter-Strike 2 installation/runtime
2. CS2 Workshop Tools
3. Hammer for map authoring
4. Source 2 material/asset tools
5. Linux CS2 dedicated server for multiplayer validation

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