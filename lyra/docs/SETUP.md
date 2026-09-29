# Setup

Enable these Unreal Engine plugins:
- Python Editor Script Plugin
- Editor Scripting Utilities
- Modeling Tools Editor Mode (recommended for later footprint extrusion)
- Landmass / Landscape tools (recommended for terrain work)
- World Partition support in the target level

Run `scripts/berlin_spandau_lyra_import.py` from the UE5 Python console or Execute Python Script command.

The script uses only Python standard-library modules plus Unreal's built-in `unreal` module.
No pip packages are required.

Generated actors are grouped under:
`Berlin_LoD2_Autonomous_Import/<map-id>/Buildings`

Historical maps use the modern Berlin GIS layer strictly as a spatial reference. Historical reconstruction should be authored in a separate Data Layer / Outliner hierarchy and must not overwrite the modern source geometry.