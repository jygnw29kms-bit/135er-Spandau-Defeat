import unreal, json, os, traceback
FINAL='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
TEST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_VISUAL_v77_TEST'
out={'ok':False,'errors':[]}
try:
    if unreal.EditorAssetLibrary.does_asset_exist(TEST):
        if not unreal.EditorAssetLibrary.delete_asset(TEST): raise RuntimeError('could not delete old test map')
    obj=unreal.EditorAssetLibrary.duplicate_asset(FINAL,TEST)
    if not obj: raise RuntimeError('duplicate failed')
    unreal.EditorAssetLibrary.save_asset(TEST,only_if_is_dirty=False)
    out['ok']=unreal.EditorAssetLibrary.does_asset_exist(TEST)
    out['test']=TEST
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
path=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v77_duplicate_map.json')
os.makedirs(os.path.dirname(path),exist_ok=True)
open(path,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str))
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')