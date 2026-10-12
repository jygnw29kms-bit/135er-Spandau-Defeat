import unreal, os, json
ASSET='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60.SM_RathausSpandau_DGM1_DOP_v60'
outdir=os.path.join(unreal.Paths.project_saved_dir(),'Exports')
os.makedirs(outdir,exist_ok=True)
outfile=os.path.join(outdir,'SM_RathausSpandau_DGM1_DOP_v60.obj')
mesh=unreal.load_asset(ASSET)
if not mesh: raise RuntimeError('mesh load failed')
task=unreal.AssetExportTask()
task.object=mesh
task.filename=outfile
task.automated=True
task.prompt=False
task.replace_identical=True
task.write_empty_files=False
try: task.exporter=unreal.StaticMeshExporterOBJ()
except Exception: pass
ok=unreal.Exporter.run_asset_export_task(task)
report={'ok':bool(ok),'asset':ASSET,'outfile':outfile,'exists':os.path.exists(outfile),'size':os.path.getsize(outfile) if os.path.exists(outfile) else 0}
with open(os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_obj_export.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
unreal.log('[RATHAUS_DGM_EXPORT] '+json.dumps(report))
if not report['ok'] or not report['exists']: raise RuntimeError('OBJ export failed')
