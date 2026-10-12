import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_between_spawns.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'map':MAP,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    starts={a.get_actor_label():a for a in actors if 'PlayerStart' in a.get_class().get_name()}
    recasts=[a for a in actors if 'RecastNavMesh' in a.get_class().get_name()]
    navbounds=[a for a in actors if 'NavMeshBoundsVolume' in a.get_class().get_name()]
    out['recast_count']=len(recasts); out['navbounds_count']=len(navbounds)
    out['starts']={k:[v.get_actor_location().x,v.get_actor_location().y,v.get_actor_location().z] for k,v in starts.items()}
    labels=sorted(starts)
    if len(labels)<2: raise RuntimeError('need two PlayerStarts')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    a=starts[labels[0]].get_actor_location(); b=starts[labels[1]].get_actor_location()
    try:
        path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None)
        out['path_object']=str(path)
        if path:
            out['path_valid']=bool(path.is_valid()) if hasattr(path,'is_valid') else None
            out['path_partial']=bool(path.is_partial()) if hasattr(path,'is_partial') else None
            try:
                pts=path.get_path_points(); out['path_points']=[[p.x,p.y,p.z] for p in pts]
            except Exception as e: out['path_points_error']=str(e)
        else:
            out['path_valid']=False
    except Exception as e:
        out['path_error']=str(e)
    out['ok']=len(recasts)>0 and len(navbounds)>0 and out.get('path_valid') is True and not out.get('path_partial',False)
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_AUDIT] '+json.dumps(out))
if not out['ok']: raise RuntimeError('nav audit failed; see '+REPORT)
