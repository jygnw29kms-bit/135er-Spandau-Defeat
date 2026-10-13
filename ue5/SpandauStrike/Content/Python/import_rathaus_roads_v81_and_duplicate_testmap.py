import unreal, os, json, traceback
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_ROADS_DGM_v81_PROJECTED.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v81'; NAME='SM_RathausSpandau_ROADS_DGM_v81_PROJECTED'
FINAL='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'; TEST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_ROADS_v81_TEST'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_v81_import_duplicate.json'); out={'ok':False,'errors':[]}
try:
 t=unreal.AssetImportTask(); t.filename=SRC; t.destination_path=DEST; t.destination_name=NAME; t.automated=True; t.replace_existing=True; t.replace_existing_settings=True; t.save=True
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]); mesh=unreal.load_asset(DEST+'/'+NAME)
 if not mesh: raise RuntimeError('v81 import failed')
 sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem); out['uv_channels']=sub.get_num_uv_channels(mesh,0)
 try: sub.remove_collisions(mesh)
 except: pass
 unreal.EditorAssetLibrary.save_loaded_asset(mesh,False); out['asset']=mesh.get_path_name()
 if unreal.EditorAssetLibrary.does_asset_exist(TEST): unreal.EditorAssetLibrary.delete_asset(TEST)
 if not unreal.EditorAssetLibrary.duplicate_asset(FINAL,TEST): raise RuntimeError('test map duplicate failed')
 unreal.EditorAssetLibrary.save_asset(TEST,only_if_is_dirty=False); out['test_map']=TEST; out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True); open(R,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str)); print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')