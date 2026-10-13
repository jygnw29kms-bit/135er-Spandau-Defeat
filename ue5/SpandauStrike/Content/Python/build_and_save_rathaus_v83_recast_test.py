import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_DGM_v83_TEST'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v83_recast_test.json')
state={'ticks':0,'stable':0,'done':False,'result':{'ok':False,'errors':[]}}
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('v83 test map load failed')
world=ue.get_editor_world()
try: unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
except: pass

def finish():
    if state['done']: return
    state['done']=True; r=state['result']; r['ticks']=state['ticks']; r['stable_ticks']=state['stable']
    try:
        w=ue.get_editor_world(); r['building']=bool(unreal.NavigationSystemV1.is_navigation_being_built_or_locked(w)); r['save_current_level']=bool(lvl.save_current_level()); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); r['ok']=r['save_current_level'] and not r['building']
    except Exception as e: r['errors'].append(str(e)); r['traceback']=traceback.format_exc()
    os.makedirs(os.path.dirname(REPORT),exist_ok=True)
    with open(REPORT,'w',encoding='utf-8') as f: json.dump(r,f,indent=2,ensure_ascii=False)
    unreal.log('[RATHAUS_V83_RECAST] '+json.dumps(r))
    try: unreal.unregister_slate_post_tick_callback(state['handle'])
    except: pass
    unreal.EditorPythonScripting.set_keep_python_script_alive(False); unreal.SystemLibrary.execute_console_command(ue.get_editor_world(),'QUIT_EDITOR')

def tick(dt):
    state['ticks']+=1
    try:
        busy=unreal.NavigationSystemV1.is_navigation_being_built_or_locked(ue.get_editor_world())
        if state['ticks']>=90:
            state['stable']=0 if busy else state['stable']+1
            if state['stable']>=45: finish(); return
        if state['ticks']>=700: state['result']['errors'].append('timeout waiting nav build'); finish()
    except Exception as e: state['result']['errors'].append(str(e)); state['result']['traceback']=traceback.format_exc(); finish()
state['handle']=unreal.register_slate_post_tick_callback(tick)
unreal.log('[RATHAUS_V83_RECAST] waiting')