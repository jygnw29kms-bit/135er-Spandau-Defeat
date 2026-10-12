import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
DGM='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60.SM_RathausSpandau_DGM1_DOP_v60'
ROADS='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54.SM_RathausSpandau_ROADS_DGM_v54'
TILES=r'C:/Users/dezen/Documents/Unreal Projects/SpandauStrike/Saved/Reports/rathaus_nav_corridor_tiles_5m.json'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_support_corridor_test.json')
state={'ticks':0,'phase':'waiting','rebuild_tick':0,'done':False,'result':{'ok':False,'errors':[],'saved':False}}
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
with open(TILES,'r',encoding='utf-8') as f: tiledata=json.load(f)
# Remove prior transient test actors in case a previous process crashed.
for a in list(actorsub.get_all_level_actors()):
    if a.get_actor_label().startswith('NAVSUP_TEST_'):
        actorsub.destroy_actor(a)
# Temporarily exclude imported DGM/roads from nav gathering; physical collision stays intact.
for a in actorsub.get_all_level_actors():
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    if c and c.static_mesh and c.static_mesh.get_path_name() in (DGM,ROADS):
        try:
            state['result'].setdefault('disabled_nav_components',[]).append({'actor':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'before':str(c.get_editor_property('can_ever_affect_navigation'))})
            c.set_editor_property('can_ever_affect_navigation',False)
        except Exception as e: state['result']['errors'].append('nav disable '+a.get_actor_label()+': '+str(e))
cube=unreal.load_asset('/Engine/BasicShapes/Cube.Cube')
if not cube: raise RuntimeError('Engine Cube asset missing')
spawned=[]
for i,t in enumerate(tiledata['tiles']):
    if t.get('z') is None or t.get('missing_gradient'): continue
    # 20 cm thick support, top nominally 10 cm below sampled DGM surface.
    loc=unreal.Vector(float(t['x']),float(t['y']),float(t['z'])-30.0)
    rot=unreal.Rotator(float(t.get('pitch',0.0)),0.0,float(t.get('roll',0.0)))
    a=actorsub.spawn_actor_from_class(unreal.StaticMeshActor,loc,rot,False)
    if not a: continue
    a.set_actor_label('NAVSUP_TEST_%03d'%i,mark_dirty=False)
    a.set_actor_scale3d(unreal.Vector(5.8,5.8,0.4))
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    c.set_static_mesh(cube)
    c.set_collision_profile_name('BlockAll')
    try: c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    except: pass
    try: c.set_editor_property('can_ever_affect_navigation',True)
    except Exception as e: state['result']['errors'].append('nav enable tile: '+str(e))
    try: c.set_hidden_in_game(True)
    except: pass
    try: c.set_visibility(False,True)
    except: pass
    spawned.append(a)
state['result']['spawned_tiles']=len(spawned)

def cleanup():
    for a in list(actorsub.get_all_level_actors()):
        if a.get_actor_label().startswith('NAVSUP_TEST_'):
            try: actorsub.destroy_actor(a)
            except: pass

def finish(ok,extra=None):
    if state['done']: return
    state['done']=True
    r=state['result']; r['ok']=bool(ok); r['ticks']=state['ticks']; r['phase']=state['phase']
    if extra:r.update(extra)
    with open(REPORT,'w',encoding='utf-8') as f: json.dump(r,f,ensure_ascii=False,indent=2)
    unreal.log('[NAVSUP_CORRIDOR_TEST] '+json.dumps(r))
    cleanup()
    try: unreal.unregister_slate_post_tick_callback(state['handle'])
    except: pass
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)

def validate():
    world=ue.get_editor_world(); starts={a.get_actor_label():a for a in actorsub.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()}; labels=sorted(starts)
    pro={}
    for label,a in starts.items():
        p=a.get_actor_location(); q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,None,None,unreal.Vector(250,250,500))
        pro[label]=None if q is None else [q.x,q.y,q.z]
    a=starts[labels[0]].get_actor_location(); b=starts[labels[1]].get_actor_location()
    path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None)
    valid=bool(path and path.is_valid()); partial=bool(path.is_partial()) if path else None
    try: pts=[[v.x,v.y,v.z] for v in path.get_editor_property('path_points')] if path else []
    except: pts=[]
    return valid and not partial, {'projections':pro,'path_valid':valid,'path_partial':partial,'path_points':pts,'path_point_count':len(pts)}

def tick(dt):
    state['ticks']+=1
    try:
        world=ue.get_editor_world(); locked=unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world)
        if state['phase']=='waiting' and state['ticks']>=50 and not locked:
            state['phase']='rebuilding'; state['rebuild_tick']=state['ticks']; unreal.log('[NAVSUP_CORRIDOR_TEST] rebuilding at tick %d'%state['ticks']); unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
        elif state['phase']=='rebuilding' and state['ticks']>=state['rebuild_tick']+8 and not unreal.NavigationSystemV1.is_navigation_being_built(world):
            state['phase']='validating'; ok,extra=validate(); finish(ok,extra)
        if state['ticks']>800: finish(False,{'error':'timeout'})
    except Exception as e:
        state['result']['errors'].append(str(e));state['result']['traceback']=traceback.format_exc();finish(False)
state['handle']=unreal.register_slate_post_tick_callback(tick)
unreal.log('[NAVSUP_CORRIDOR_TEST] registered transient corridor with %d tiles'%len(spawned))

