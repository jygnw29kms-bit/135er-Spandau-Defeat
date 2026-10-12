import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_proxy_bounds_nav_audit.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('load failed')
    world=ue.get_editor_world()
    actors=list(eas.get_all_level_actors())
    rows=[]
    for a in actors:
        label=a.get_actor_label()
        if label in ('NAV_Rathaus_TerrainProxy_v73','Rathaus_DGM1_DOP2025_v61','Rathaus_ROADS_DATA_v61') or 'PlayerStart' in a.get_class().get_name() or a.get_class().get_name() in ('RecastNavMesh','NavMeshBoundsVolume'):
            o,e=a.get_actor_bounds(False,False)
            p=a.get_actor_location()
            rows.append({'label':label,'class':a.get_class().get_name(),'loc':[p.x,p.y,p.z],'bounds_origin':[o.x,o.y,o.z],'bounds_extent':[e.x,e.y,e.z],'min':[o.x-e.x,o.y-e.y,o.z-e.z],'max':[o.x+e.x,o.y+e.y,o.z+e.z]})
    out['actors']=rows
    proxy=next((a for a in actors if a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v73'),None)
    starts=sorted([a for a in actors if 'PlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
    recast=next((a for a in actors if a.get_class().get_name()=='RecastNavMesh'),None)
    out['recast_present']=bool(recast)
    out['samples']=[]
    for s in starts[:2]:
        p=s.get_actor_location()
        q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,recast,None,unreal.Vector(1000,1000,3000)) if recast else None
        out['samples'].append({'label':s.get_actor_label(),'loc':[p.x,p.y,p.z],'projected':None if q is None else [q.x,q.y,q.z]})
    proj=[x['projected'] for x in out['samples']]
    if len(proj)==2 and all(x for x in proj):
        a=unreal.Vector(*proj[0]); b=unreal.Vector(*proj[1])
        path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,a,b,None,None)
        out['path_valid']=bool(path and path.is_valid()); out['path_partial']=bool(path.is_partial()) if path else None
    else:
        out['path_valid']=False; out['path_partial']=None
    out['ok']=proxy is not None and len(starts)>=2
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False))
unreal.log('[RATHAUS_PROXY_BOUNDS_NAV] '+json.dumps(out))
