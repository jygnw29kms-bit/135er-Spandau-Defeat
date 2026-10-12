import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
ASSET='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v75/SM_RathausSpandau_NAV_PROXY_v75'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_proxy_v75_install_2026-10-12.json')
out={'ok':False,'errors':[],'starts':[],'stage':0}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    mesh=unreal.load_asset(ASSET)
    if not mesh: raise RuntimeError('v75 asset missing')
    actors=eas.get_all_level_actors()
    proxy=next((a for a in actors if a.get_actor_label() in ('NAV_Rathaus_TerrainProxy_v73','NAV_Rathaus_TerrainProxy_v75')),None)
    if not proxy: raise RuntimeError('proxy actor missing')
    comp=proxy.static_mesh_component
    old=comp.get_editor_property('static_mesh')
    out['old_mesh']=old.get_path_name() if old else None
    comp.set_static_mesh(mesh)
    comp.set_collision_profile_name('BlockAll')
    comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    comp.set_editor_property('can_ever_affect_navigation',True)
    comp.set_editor_property('hidden_in_game',True)
    comp.set_editor_property('visible',True)
    proxy.set_actor_label('NAV_Rathaus_TerrainProxy_v75')
    try: proxy.set_editor_property('is_spatially_loaded',False)
    except: pass
    if not lvl.save_current_level(): raise RuntimeError('stage1 save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['stage']=1
    # Reload so the static-mesh component recreates its physics state from v75.
    if not lvl.load_level(MAP): raise RuntimeError('reload after v75 install failed')
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=eas.get_all_level_actors()
    proxy=next((a for a in actors if a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v75'),None)
    if not proxy: raise RuntimeError('v75 proxy actor missing after reload')
    comp=proxy.static_mesh_component
    actual=comp.get_editor_property('static_mesh')
    out['new_mesh']=actual.get_path_name() if actual else None
    if not actual or 'REAL_v75/SM_RathausSpandau_NAV_PROXY_v75' not in out['new_mesh']:
        raise RuntimeError('v75 mesh not persisted')
    starts=sorted([a for a in actors if 'LyraPlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
    if len(starts)!=2: raise RuntimeError('expected 2 starts')
    for s in starts:
        p=s.get_actor_location()
        tr=comp.line_trace_component(unreal.Vector(p.x,p.y,2000),unreal.Vector(p.x,p.y,-3000),True,False)
        if tr is None: raise RuntimeError('no v75 hit after reload at '+str(s.get_actor_label()))
        hit_z=float(tr[0].z); new_z=hit_z+120.0
        before=[float(p.x),float(p.y),float(p.z)]
        s.set_actor_location(unreal.Vector(p.x,p.y,new_z),False,False)
        out['starts'].append({'label':str(s.get_actor_label()),'surface_z':hit_z,'before':before,'after':[float(p.x),float(p.y),new_z]})
    if not lvl.save_current_level(): raise RuntimeError('stage2 save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['stage']=2; out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
