import unreal, os, json, traceback
SRC='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v83/SM_RathausSpandau_DGM1_DOP_v83_RAWDGM'
DST='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v84/SM_RathausSpandau_NAV_PROXY_v84'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_navproxy_v84_build.json')
out={'ok':False,'errors':[]}
try:
    if unreal.EditorAssetLibrary.does_asset_exist(DST): unreal.EditorAssetLibrary.delete_asset(DST)
    if not unreal.EditorAssetLibrary.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v83 to nav v84 failed')
    mesh=unreal.load_asset(DST)
    if not mesh: raise RuntimeError('v84 mesh load failed')
    mesh.set_editor_property('has_navigation_data',True)
    bs=mesh.get_editor_property('body_setup')
    if not bs: raise RuntimeError('body_setup missing on v84')
    bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    mesh.modify(); unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    out['mesh']=mesh.get_path_name(); out['has_navigation_data']=str(mesh.get_editor_property('has_navigation_data'))
    out['collision_trace_flag']=str(bs.get_editor_property('collision_trace_flag'))
    try: out['nanite_enabled']=str(mesh.get_editor_property('nanite_settings').enabled)
    except: pass
    out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))