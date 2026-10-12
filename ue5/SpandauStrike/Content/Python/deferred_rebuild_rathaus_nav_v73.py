import unreal, json, os, traceback, time
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_v73_deferred_build.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
state={'ticks':0,'phase':'init','started':time.time(),'build_requested':False,'finished':False}
out={'ok':False,'map':MAP,'errors':[]}
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eass=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('map load failed')
world=ues.get_editor_world(); nav=unreal.NavigationSystemV1.get_navigation_system(world)
handle=None

def finish(ok, note=''):
    global handle
    if state['finished']: return
    state['finished']=True
    out['ok']=ok; out['note']=note; out['ticks']=state['ticks']; out['phase']=state['phase']; out['elapsed']=time.time()-state['started']
    try:
        actors=eass.get_all_level_actors(); starts=sorted([a for a in actors if 'PlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
        if len(starts)>=2:
            a=starts[0].get_actor_location(); b=starts[1].get_actor_location()
            p=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None)
            out['path_valid']=bool(p and p.is_valid()); out['path_partial']=bool(p and p.is_partial()) if p else None
            out['starts']=[[a.x,a.y,a.z],[b.x,b.y,b.z]]
            if ok and not out['path_valid']: out['ok']=False
    except Exception as e: out['path_test_error']=str(e); out['ok']=False
    try: lvl.save_current_level(); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    except Exception as e: out['save_error']=str(e)
    with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
    unreal.log('[RATHAUS_NAV_V73_DEFERRED] '+json.dumps(out))
    if handle is not None:
        try: unreal.unregister_slate_post_tick_callback(handle)
        except: pass
    unreal.SystemLibrary.execute_console_command(world,'QUIT_EDITOR')

def tick(delta):
    try:
        state['ticks']+=1
        locked=bool(unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world))
        if not state['build_requested']:
            state['phase']='waiting_unlock'
            if not locked and state['ticks']>20:
                state['phase']='building'; state['build_requested']=True
                unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
        else:
            if not locked and state['ticks']>30:
                state['phase']='validating'; finish(True,'navigation build completed/unlocked')
        if state['ticks']>1800: finish(False,'timeout waiting for navigation')
    except Exception as e:
        out['errors'].append(str(e)); out['traceback']=traceback.format_exc(); finish(False,'exception')

handle=unreal.register_slate_post_tick_callback(tick)
unreal.log('[RATHAUS_NAV_V73_DEFERRED] callback registered')
