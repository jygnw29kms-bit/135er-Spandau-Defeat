import unreal, os, json, traceback
TEX='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v61/RathausSpandau_DOP2025_360m'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Exports','RathausSpandau_DOP2025_360m_export.png')
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_texture_export.json')
out={'ok':False,'errors':[],'output':OUT}
try:
    tex=unreal.load_asset(TEX)
    if not tex: raise RuntimeError('texture missing')
    task=unreal.AssetExportTask(); task.object=tex; task.filename=OUT; task.automated=True; task.prompt=False; task.replace_identical=True
    task.exporter=unreal.TextureExporterPNG()
    ok=unreal.Exporter.run_asset_export_task(task)
    out['ok']=bool(ok) and os.path.exists(OUT)
    out['size']=os.path.getsize(OUT) if os.path.exists(OUT) else 0
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2,default=str))
print(json.dumps(out,indent=2,default=str))
