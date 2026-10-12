import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_proxy_nav_deferred_validation.json')
state={'ticks':0,'stable':0,'done':False,'result':{'ok':False,'errors':[]}}
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ue=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError('FINAL load failed')

def validate():
    world=ue.get_editor_world()
    actors=list(eas.get_all_level_actors())
    nav=next((a for a in actors if a.get_class().get_name()=='RecastNavMesh'),None)
    starts=sorted([a for a in actors if 'PlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
    grid=[]
    for y in [-12000,-6000,0,6000,12000]:
        for x in [-12000,-6000,0,6000,12000]:
            q=unreal.NavigationSystemV1.project_point_to_navigation(world,unreal.Vector(float(x),float(y),500.0),nav,None,unreal.Vector(1000,1000,3000)) if nav else None
            grid.append({'in':[x,y,500.0],'projected':None if q is None else [q.x,q.y,q.z]})
    sp=[]; projected=[]
    for s in starts[:2]:
        p=s.get_actor_location()
        q=unreal.NavigationSystemV1.project_point_to_navigation(world,p,nav,None,unreal.Vector(1200,1200,3500)) if nav else None
        sp.append({'label':s.get_actor_label(),'raw':[p.x,p.y,p.z],'projected':None if q is None else [q.x,q.y,q.z]})
        projected.append(q)
    path=None
    if len(projected)==2 and all(q is not None for q in projected):
        path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world,projected[0],projected[1],None,None)
    return {
        'grid':grid,
        'valid_count':sum(1 for p in grid if p['projected'] is not None),
        'total':len(grid),
        'starts':sp,
        'path_valid':bool(path and path.is_valid()),
        'path_partial':bool(path.is_partial()) if path else None,
        'nav10m_count':sum(1 for a in actors if a.get_actor_label().startswith('NAV10M_')),
        'spawn_pad_count':sum(1 for a in actors if a.get_actor_label().startswith('TECH_SpawnSafetyPad_')),
        'proxy_present':any(a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v73' for a in actors),
    }

def finish(extra):
    if state['done']: return
    state['done']=True
    r=state['result']; r.update(extra); r['ticks']=state['ticks']; r['stable_ticks']=state['stable']
    r['ok']=r.get('valid_count',0)>=20 and r.get('path_valid',False) and r.get('nav10m_count',1)==0 and r.get('spawn_pad_count',1)==0 and r.get('proxy_present',False)
    os.makedirs(os.path.dirname(REPORT),exist_ok=True)
    with open(REPORT,'w',encoding='utf-8') as f: json.dump(r,f,indent=2,ensure_ascii=False)
    unreal.log('[RATHAUS_PROXY_NAV_DEFERRED] '+json.dumps(r))
    try: unreal.unregister_slate_post_tick_callback(state['handle'])
    except: pass
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)
    unreal.SystemLibrary.execute_console_command(ue.get_editor_world(),'QUIT_EDITOR')

def tick(dt):
    state['ticks']+=1
    try:
        world=ue.get_editor_world()
        busy=unreal.NavigationSystemV1.is_navigation_being_built_or_locked(world)
        if state['ticks']>=90:
            state['stable']=0 if busy else state['stable']+1
            if state['stable']>=30:
                finish(validate()); return
        if state['ticks']>=600:
            r=validate(); r['timeout']=True; finish(r)
    except Exception as e:
        state['result']['errors'].append(str(e)); state['result']['traceback']=traceback.format_exc(); finish({})
state['handle']=unreal.register_slate_post_tick_callback(tick)
unreal.log('[RATHAUS_PROXY_NAV_DEFERRED] registered')
