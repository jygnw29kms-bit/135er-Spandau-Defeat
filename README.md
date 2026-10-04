<p align="center">
  <img src="media/theme/repo-hero.svg" alt="135er Spandau Strike" width="100%">
</p>

<p align="center"><strong>135er - Spandau Strike | Berlin-Spandau | Unreal Engine 5 / Lyra</strong></p>

<p align="center"><code>Berlin GIS</code> | <code>Blender Master Pipeline</code> | <code>Unreal Engine 5 / Lyra</code></p>

# 135er - Spandau Strike

**Unreal Engine 5 / Lyra is the only active and future engine target.**


## Current production focus

- **Engine:** Unreal Engine 5 / Lyra
- **Current map:** Rathaus Spandau
- **Master authoring:** Blender
- **World data:** Berlin GIS / LoD2 / DGM1
- **Characters:** shared UE-compatible humanoid rig
- **Modern factions:** CT = Germany / Bundeswehr-inspired, T = United States
- **Historical factions:** CT = German period-correct forces, T = US period-correct forces

## Rathaus Spandau pipeline

1. Berlin geodata / reference acquisition
2. Blender master modeling
3. replacement of all visible blockouts with production geometry
4. architecture and micro-detail pass
5. street, tram, vegetation and set-dressing pass
6. UE5-oriented naming, collision and scale validation
7. FBX export to Unreal Engine 5
8. UE5 materials, Nanite/LOD, collision, lighting and navigation
9. gameplay validation
10. genuine UE5 in-engine screenshots and release packaging


## Maps

The project retains its Spandau map roster, but production is currently focused on **Rathaus Spandau**. Other maps resume after the Rathaus production standard has been established in UE5.

## Key project paths

| Area | Path |
|---|---|
| Current status | [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md) |
| Map roster / modes | [docs/MAPS_AND_MODES.md](docs/MAPS_AND_MODES.md) |
| UE5/Lyra GIS status | [lyra/docs/GIS_STATUS.md](lyra/docs/GIS_STATUS.md) |
| UE5/Lyra map definitions | [lyra/maps/maps.json](lyra/maps/maps.json) |
| Blender master pipeline | [tools/blender_pipeline/README.md](tools/blender_pipeline/README.md) |
| Capture policy | [docs/INGAME_CAPTURE_STANDARD.md](docs/INGAME_CAPTURE_STANDARD.md) |
| Image QA gate | [docs/IMAGE_QA.md](docs/IMAGE_QA.md) |

## Publication rule

Only genuine Unreal Engine 5 captures may be labeled as in-engine/gameplay imagery. Blender renders remain explicitly development/master renders until imported and verified in UE5.

---

<p align="center"><strong>135er - SPANDAU STRIKE</strong><br><sub>BERLIN GIS | BLENDER | UNREAL ENGINE 5 / LYRA</sub></p>
