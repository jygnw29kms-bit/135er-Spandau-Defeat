from pathlib import Path
ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree")
GIS=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1")
OUT=ROOT/"tools"/"blender_pipeline"/"rathaus_real"
OUT.mkdir(parents=True,exist_ok=True)
print("GIS_EXISTS",GIS.exists())
for p in sorted(GIS.glob("*")):
    if p.is_file():
        print(p.name,p.stat().st_size)
