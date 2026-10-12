import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_spawn_safety_pads.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'pads':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('load failed')
    cube=unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube.Cube')
    if not cube: raise RuntimeError('engine cube missing')
    starts=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='LyraPlayerStart']
    if len(starts)<2: raise RuntimeError('expected LyraPlayerStart actors')
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith('TECH_SpawnSafetyPad_'): eas.destroy_actor(a)
    for i,s in enumerate(sorted(starts,key=lambda x:x.get_actor_label()),1):
        p=s.get_actor_location(); z=p.z-145.0
        pad=eas.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(p.x,p.y,z),unreal.Rotator())
        pad.set_actor_label(f'TECH_SpawnSafetyPad_{i}'); pad.set_folder_path('Rathaus/TECH/SpawnSafety')
        c=pad.static_mesh_component; c.set_static_mesh(cube); pad.set_actor_scale3d(unreal.Vector(40.0,40.0,0.5))
        c.set_collision_profile_name('BlockAll'); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        c.set_editor_property('visible',False)
        try: c.set_editor_property('hidden_in_game',True)
        except: pass
        try: pad.set_editor_property('is_spatially_loaded',False)
        except: pass
        out['pads'].append({'label':pad.get_actor_label(),'location':[p.x,p.y,z]})
        s.set_actor_location(unreal.Vector(p.x,p.y,p.z+120.0),False,False)
    if not lvl.save_current_level(): raise RuntimeError('save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_SPAWN_SAFETY] '+json.dumps(out))
if not out['ok']: raise RuntimeError('spawn safety pad failed')
