import unreal, json, os, traceback
ASSET='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73/SM_RathausSpandau_NAV_PROXY_v73'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_proxy_simple_collision.json')
out={'ok':False,'asset':ASSET,'errors':[]}
try:
    mesh=unreal.EditorAssetLibrary.load_asset(ASSET)
    if not mesh: raise RuntimeError('proxy missing')
    smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    out['before']={'simple':smes.get_simple_collision_count(mesh),'convex':smes.get_convex_collision_count(mesh),'complexity':str(smes.get_collision_complexity(mesh))}
    ok=smes.set_convex_decomposition_collisions(mesh,64,16,100000)
    if not ok: raise RuntimeError('convex decomposition returned false')
    mesh.set_editor_property('has_navigation_data',True)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    out['after']={'simple':smes.get_simple_collision_count(mesh),'convex':smes.get_convex_collision_count(mesh),'complexity':str(smes.get_collision_complexity(mesh)),'has_navigation_data':str(mesh.get_editor_property('has_navigation_data')),'nav_collision':str(mesh.get_editor_property('nav_collision'))}
    out['ok']=out['after']['convex']>0
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_PROXY_SIMPLE] '+json.dumps(out))
if not out['ok']: raise RuntimeError('nav proxy simple collision failed')
