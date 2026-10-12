import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_rebuild_test.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    starts={a.get_actor_label():a for a in actors if 'PlayerStart' in a.get_class().get_name()}
    bounds=[a for a in actors if 'NavMeshBoundsVolume' in a.get_class().get_name()]
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    labels=sorted(starts)
    out['before_projection']={}
    for label,a in starts.items():
        p=a.get_actor_location()
        try:
            q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,None,None,unreal.Vector(500,500,1000))
            out['before_projection'][label]=str(q)
        except Exception as e: out['before_projection'][label]='ERR '+str(e)
    for b in bounds:
        try: unreal.NavigationSystemV1.on_navigation_bounds_updated(b)
        except Exception as e: out.setdefault('bounds_update_errors',[]).append(str(e))
    unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
    out['building_after_command']=unreal.NavigationSystemV1.is_navigation_being_built(world)
    out['after_projection']={}
    for label,a in starts.items():
        p=a.get_actor_location()
        try:
            q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,None,None,unreal.Vector(500,500,1000))
            out['after_projection'][label]=str(q)
        except Exception as e: out['after_projection'][label]='ERR '+str(e)
    a=starts[labels[0]].get_actor_location(); b=starts[labels[1]].get_actor_location()
    path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None)
    out['path_object']=str(path); out['path_valid']=bool(path.is_valid()) if path and hasattr(path,'is_valid') else False; out['path_partial']=bool(path.is_partial()) if path and hasattr(path,'is_partial') else None
    try: out['path_points']=str(path.get_editor_property('path_points')) if path else None
    except Exception as e: out['path_points_error']=str(e)
    out['ok']=out['path_valid'] and not out.get('path_partial',False)
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f:json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_REBUILD_TEST] '+json.dumps(out))
