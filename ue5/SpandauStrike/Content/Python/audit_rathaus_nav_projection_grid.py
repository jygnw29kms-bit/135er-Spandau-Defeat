import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_projection_grid.json')
out={'ok':False,'points':[],'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('map load failed')
    world=ues.get_editor_world(); recasts=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='RecastNavMesh']
    nav=recasts[0] if recasts else None
    for y in [-12000,-6000,0,6000,12000]:
        for x in [-12000,-6000,0,6000,12000]:
            p=unreal.Vector(float(x),float(y),500.0)
            try: q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,nav,None,unreal.Vector(600,600,2000))
            except Exception as e: q=None; out['errors'].append(f'{x},{y}: {e}')
            out['points'].append({'in':[x,y,500.0],'projected':None if q is None else [q.x,q.y,q.z]})
    valid=sum(1 for p in out['points'] if p['projected'] is not None); out['valid_count']=valid; out['total']=len(out['points']); out['ok']=valid>0
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_GRID] '+json.dumps(out))
