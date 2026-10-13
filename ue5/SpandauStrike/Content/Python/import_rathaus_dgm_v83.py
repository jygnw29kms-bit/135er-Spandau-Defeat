import unreal, os, json, traceback
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_DGM1_DOP_v83_RAWDGM.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v83'
NAME='SM_RathausSpandau_DGM1_DOP_v83_RAWDGM'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_v83_import.json')
out={'ok':False,'errors':[]}
try:
    task=unreal.AssetImportTask(); task.filename=SRC; task.destination_path=DEST; task.destination_name=NAME
    task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    paths=list(task.imported_object_paths); out['imported_paths']=[str(x) for x in paths]
    if not paths: raise RuntimeError('v83 import produced no assets')
    mesh=unreal.load_asset(paths[0]); out['mesh']=mesh.get_path_name() if mesh else None
    if not mesh: raise RuntimeError('v83 mesh load failed')
    try: mesh.set_editor_property('nanite_settings', mesh.get_editor_property('nanite_settings'))
    except: pass
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))