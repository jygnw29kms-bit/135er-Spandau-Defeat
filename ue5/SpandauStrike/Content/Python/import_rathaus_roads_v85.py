import unreal,os,json,traceback
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_ROADS_DGM_v85_PROJECTED_V83.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v85'; NAME='SM_RathausSpandau_ROADS_DGM_v85_PROJECTED_V83'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_v85_import.json'); out={'ok':False,'errors':[]}
try:
    task=unreal.AssetImportTask(); task.filename=SRC; task.destination_path=DEST; task.destination_name=NAME; task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]); paths=list(task.imported_object_paths); out['imported_paths']=[str(x) for x in paths]
    if not paths: raise RuntimeError('v85 road import produced no asset')
    mesh=unreal.load_asset(paths[0]);
    if not mesh: raise RuntimeError('v85 mesh load failed')
    mesh.set_editor_property('has_navigation_data',False)
    bs=mesh.get_editor_property('body_setup')
    if bs: bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,False); out['mesh']=mesh.get_path_name(); out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))