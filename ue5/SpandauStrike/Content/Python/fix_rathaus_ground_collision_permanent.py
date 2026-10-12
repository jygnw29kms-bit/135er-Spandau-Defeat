import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
ASSETS=[
('/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60','DGM'),
('/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54','ROADS')]
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_ground_collision_permanent_fix.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'assets':[],'errors':[]}
try:
    smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for path,label in ASSETS:
        mesh=unreal.EditorAssetLibrary.load_asset(path)
        if not mesh: raise RuntimeError('missing '+path)
        before={'simple':smes.get_simple_collision_count(mesh),'convex':smes.get_convex_collision_count(mesh),'complexity':str(smes.get_collision_complexity(mesh))}
        smes.remove_collisions(mesh)
        body=mesh.get_editor_property('body_setup')
        if not body: raise RuntimeError('no body setup '+path)
        body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
        after={'simple':smes.get_simple_collision_count(mesh),'convex':smes.get_convex_collision_count(mesh),'complexity':str(smes.get_collision_complexity(mesh))}
        out['assets'].append({'label':label,'path':path,'before':before,'after':after})
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('map load failed')
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith('TECH_SpawnSafetyPad_'): eas.destroy_actor(a)
    starts=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='LyraPlayerStart']
    ground=[(-12000.0,-12000.0,-101.04101085734858),(12000.0,-12000.0,-151.28204601765145)]
    for s,g in zip(sorted(starts,key=lambda x:x.get_actor_label()),ground):
        s.set_actor_location(unreal.Vector(g[0],g[1],g[2]+250.0),False,False)
    if not lvl.save_current_level(): raise RuntimeError('level save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_COLLISION_PERMANENT] '+json.dumps(out))
if not out['ok']: raise RuntimeError('collision fix failed')
