import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_deferred_rebuild.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
state={'ticks':0,'phase':'waiting','rebuild_tick':None,'done':False,'result':{'ok':False,'map':MAP,'errors':[]}}
try:
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
except Exception as e:
    state['result']['errors'].append('keep_alive: '+str(e))
    with open(REPORT,'w',encoding='utf-8') as f: json.dump(state['result'],f,indent=2)
    raise

lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP):
    raise RuntimeError('FINAL load failed')

def finish(ok, extra=None):
    if state['done']: return
    state['done']=True
    r=state['result']; r['ok']=bool(ok); r['ticks']=state['ticks']; r['phase']=state['phase']
    if extra: r.update(extra)
    with open(REPORT,'w',encoding='utf-8') as f: json.dump(r,f,ensure_ascii=False,indent=2)
    unreal.log('[RATHAUS_NAV_DEFERRED] '+json.dumps(r))
    try: unreal.unregister_slate_post_tick_callback(state['handle'])
    except: pass
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)

def validate():
    actors=actorsub.get_all_level_actors()
    starts={a.get_actor_label():a for a in actors if 'PlayerStart' in a.get_class().get_name()}
    labels=sorted(starts)
    if len(labels)!=2:
        return False, {'error':'Expected 2 PlayerStarts, found %d'%len(labels)}
    world=ue.get_editor_world()
    projections={}
    for label,a in starts.items():
        p=a.get_actor_location()
        q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,None,None,unreal.Vector(500,500,1000))
        projections[label]=str(q)
    a=starts[labels[0]].get_actor_location(); b=starts[labels[1]].get_actor_location()
    path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None)
    valid=bool(path and path.is_valid())
    partial=bool(path.is_partial()) if path else None
    try: points=str(path.get_editor_property('path_points')) if path else None
    except Exception as e: points='ERR '+str(e)
    return valid and not partial, {'projections':projections,'path_valid':valid,'path_partial':partial,'path_points':points}

def tick(dt):
    if state['done']: return
    state['ticks']+=1
    try:
        world=ue.get_editor_world()
        nav=unreal.NavigationSystemV1.get_navigation_system(world)
        locked=unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world)
        if state['phase']=='waiting':
            # Wait well beyond UE's 16-tick delayed AsyncLoadLock release and until the nav system reports unlocked.
            if state['ticks']>=40 and not locked:
                state['phase']='rebuilding'; state['rebuild_tick']=state['ticks']
                unreal.log('[RATHAUS_NAV_DEFERRED] lock clear at tick %d; rebuilding navigation'%state['ticks'])
                unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
        elif state['phase']=='rebuilding':
            building=unreal.NavigationSystemV1.is_navigation_being_built(world)
            if state['ticks']>=state['rebuild_tick']+5 and not building:
                state['phase']='validating'
                ok, extra=validate()
                if ok:
                    saved=lvl.save_current_level()
                    extra['saved']=bool(saved)
                    finish(bool(saved),extra)
                else:
                    extra['saved']=False
                    finish(False,extra)
        if state['ticks']>600:
            finish(False,{'error':'timeout waiting for navigation unlock/build'})
    except Exception as e:
        state['result']['errors'].append(str(e)); state['result']['traceback']=traceback.format_exc(); finish(False)

state['handle']=unreal.register_slate_post_tick_callback(tick)
unreal.log('[RATHAUS_NAV_DEFERRED] registered; editor kept alive for deferred nav rebuild')
