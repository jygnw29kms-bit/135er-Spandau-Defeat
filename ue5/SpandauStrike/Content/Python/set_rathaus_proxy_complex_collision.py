import unreal,json,os,traceback
ASSET='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73/SM_RathausSpandau_NAV_PROXY_v73'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_proxy_complex_collision.json')
out={'ok':False,'errors':[]}
try:
    mesh=unreal.EditorAssetLibrary.load_asset(ASSET)
    if not mesh: raise RuntimeError('proxy mesh missing')
    body=mesh.get_editor_property('body_setup')
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    mesh.set_editor_property('has_navigation_data',True)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    geom=body.get_editor_property('agg_geom')
    out.update({'ok':True,'asset':ASSET,'trace_flag':str(body.get_editor_property('collision_trace_flag')),'convex_count':len(geom.get_editor_property('convex_elems')),'has_navigation_data':str(mesh.get_editor_property('has_navigation_data'))})
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False))
unreal.log('[RATHAUS_PROXY_COMPLEX] '+json.dumps(out))
if not out['ok']: raise RuntimeError('proxy complex collision failed')
