import unreal, json, os, traceback
ASSET='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73/SM_RathausSpandau_NAV_PROXY_v73'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_proxy_collision_mode.json')
out={'ok':False,'errors':[]}
try:
    mesh=unreal.EditorAssetLibrary.load_asset(ASSET)
    if not mesh: raise RuntimeError('proxy missing')
    smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    body=mesh.get_editor_property('body_setup')
    out['before']={'complexity':str(smes.get_collision_complexity(mesh)),'simple':smes.get_simple_collision_count(mesh),'convex':smes.get_convex_collision_count(mesh)}
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    mesh.set_editor_property('has_navigation_data',False)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    mesh.set_editor_property('has_navigation_data',True)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    out['after']={'complexity':str(smes.get_collision_complexity(mesh)),'simple':smes.get_simple_collision_count(mesh),'convex':smes.get_convex_collision_count(mesh),'has_navigation_data':str(mesh.get_editor_property('has_navigation_data')),'nav_collision':str(mesh.get_editor_property('nav_collision'))}
    out['ok']=out['after']['convex']>0 and 'USE_DEFAULT' in out['after']['complexity']
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_PROXY_MODE] '+json.dumps(out))
if not out['ok']: raise RuntimeError('nav proxy mode failed')
