import unreal, json, os, traceback

MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_proxy_unify_2026-10-10.json')
out={'ok':False,'errors':[],'removed':[],'starts':[]}

try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP):
        raise RuntimeError('FINAL map load failed')
    actors=list(eas.get_all_level_actors())

    proxy=None
    for a in actors:
        label=a.get_actor_label()
        if label=='NAV_Rathaus_TerrainProxy_v73':
            proxy=a
        if label.startswith('NAV10M_') or label.startswith('TECH_SpawnSafetyPad_'):
            out['removed'].append(label)
            eas.destroy_actor(a)
    if proxy is None:
        proxy_mesh=unreal.EditorAssetLibrary.load_asset('/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73/SM_RathausSpandau_NAV_PROXY_v73')
        if not proxy_mesh:
            raise RuntimeError('NAV proxy actor and asset missing')
        proxy=eas.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
        proxy.set_actor_label('NAV_Rathaus_TerrainProxy_v73')
        proxy.set_folder_path('Rathaus/NAV')
        proxy.static_mesh_component.set_static_mesh(proxy_mesh)
        out['proxy_spawned']=True
    else:
        out['proxy_spawned']=False

    c=proxy.static_mesh_component
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    c.set_collision_profile_name('BlockAll')
    c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN,unreal.CollisionResponseType.ECR_BLOCK)
    c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY,unreal.CollisionResponseType.ECR_BLOCK)
    try: c.set_editor_property('hidden_in_game',True)
    except: pass
    try: proxy.set_editor_property('is_spatially_loaded',False)
    except: pass

    mesh=c.get_editor_property('static_mesh')
    if not mesh:
        raise RuntimeError('proxy mesh missing')
    mesh.set_editor_property('has_navigation_data',True)
    body=mesh.get_editor_property('body_setup')
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)

    # Keep visual terrain/roads out of nav generation; building and hidden proxy remain nav sources.
    for a in list(eas.get_all_level_actors()):
        label=a.get_actor_label()
        if label in ('Rathaus_DGM1_DOP2025_v61','Rathaus_ROADS_DATA_v61'):
            sm=a.static_mesh_component.get_editor_property('static_mesh') if hasattr(a,'static_mesh_component') else None
            if sm:
                sm.set_editor_property('has_navigation_data',False)
                unreal.EditorAssetLibrary.save_loaded_asset(sm,only_if_is_dirty=False)
        elif label=='Rathaus_BERLIN3D_REAL_v70':
            sm=a.static_mesh_component.get_editor_property('static_mesh') if hasattr(a,'static_mesh_component') else None
            if sm:
                sm.set_editor_property('has_navigation_data',True)
                unreal.EditorAssetLibrary.save_loaded_asset(sm,only_if_is_dirty=False)

    world=unreal.EditorLevelLibrary.get_editor_world()
    starts=sorted([a for a in eas.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()],key=lambda a:a.get_actor_label())
    for s in starts:
        p=s.get_actor_location()
        hit=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(p.x,p.y,3000.0),unreal.Vector(p.x,p.y,-3000.0),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[s],unreal.DrawDebugTrace.NONE,True)
        hit_loc=None
        hit_actor=None
        if hit:
            try:
                hp=hit[4]; hit_loc=[hp.x,hp.y,hp.z]
                ha=hit[9]; hit_actor=ha.get_actor_label() if ha else None
                # place capsule safely above detected terrain surface
                s.set_actor_location(unreal.Vector(p.x,p.y,hp.z+150.0),False,False)
            except Exception:
                pass
        np=s.get_actor_location()
        out['starts'].append({'label':s.get_actor_label(),'before':[p.x,p.y,p.z],'ground_hit':hit_loc,'hit_actor':hit_actor,'after':[np.x,np.y,np.z]})

    unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
    if not lvl.save_current_level():
        raise RuntimeError('FINAL level save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)

    body=mesh.get_editor_property('body_setup')
    geom=body.get_editor_property('agg_geom')
    out['proxy']={
        'profile':str(c.get_collision_profile_name()),
        'enabled':str(c.get_collision_enabled()),
        'pawn':str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)),
        'visibility':str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY)),
        'hidden_in_game':str(c.get_editor_property('hidden_in_game')),
        'has_navigation_data':str(mesh.get_editor_property('has_navigation_data')),
        'trace_flag':str(body.get_editor_property('collision_trace_flag')),
        'convex_count':len(geom.get_editor_property('convex_elems')),
    }
    out['remaining_nav10m']=sum(1 for a in eas.get_all_level_actors() if a.get_actor_label().startswith('NAV10M_'))
    out['remaining_spawn_pads']=sum(1 for a in eas.get_all_level_actors() if a.get_actor_label().startswith('TECH_SpawnSafetyPad_'))
    out['ok']=out['remaining_nav10m']==0 and out['remaining_spawn_pads']==0 and out['proxy']['convex_count']>0
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()

os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f:
    json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_PROXY_UNIFY] '+json.dumps(out))
if not out['ok']:
    raise RuntimeError('proxy unify failed')
