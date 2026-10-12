import unreal, os, json
ASSET='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54.SM_RathausSpandau_ROADS_DGM_v54'
outdir=os.path.join(unreal.Paths.project_saved_dir(),'Exports'); os.makedirs(outdir,exist_ok=True)
outfile=os.path.join(outdir,'SM_RathausSpandau_ROADS_DGM_v54.obj')
mesh=unreal.load_asset(ASSET)
if not mesh: raise RuntimeError('mesh load failed')
task=unreal.AssetExportTask(); task.object=mesh; task.filename=outfile; task.automated=True; task.prompt=False; task.replace_identical=True; task.write_empty_files=False
try: task.exporter=unreal.StaticMeshExporterOBJ()
except: pass
ok=unreal.Exporter.run_asset_export_task(task)
rep={'ok':bool(ok),'outfile':outfile,'exists':os.path.exists(outfile),'size':os.path.getsize(outfile) if os.path.exists(outfile) else 0}
with open(os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_obj_export.json'),'w',encoding='utf-8') as f: json.dump(rep,f,indent=2)
unreal.log('[RATHAUS_ROADS_EXPORT] '+json.dumps(rep))
if not rep['ok'] or not rep['exists']: raise RuntimeError('roads export failed')