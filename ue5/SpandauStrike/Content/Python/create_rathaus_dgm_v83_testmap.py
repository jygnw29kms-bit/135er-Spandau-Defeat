import unreal, os, json, traceback
SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_DGM_v83_TEST'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dgm_v83_testmap_create.json')
out={'ok':False,'errors':[]}
try:
    if unreal.EditorAssetLibrary.does_asset_exist(DST): unreal.EditorAssetLibrary.delete_asset(DST)
    ok=unreal.EditorAssetLibrary.duplicate_asset(SRC,DST)
    out['duplicate']=bool(ok)
    if not ok: raise RuntimeError('duplicate FINAL to v83 test failed')
    unreal.EditorAssetLibrary.save_asset(DST,False)
    out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))