import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_NAV_PROXY_v73.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73'
NAME='SM_RathausSpandau_NAV_PROXY_v73'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_proxy_v73_install.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'errors':[]}
try:
    task=unreal.AssetImportTask(); task.filename=SRC; task.destination_path=DEST; task.destination_name=NAME
    task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    paths=list(task.imported_object_paths)
    mesh=unreal.EditorAssetLibrary.load_asset(paths[0] if paths else DEST+'/'+NAME)
    if not mesh: raise RuntimeError('proxy import failed')
    smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    smes.remove_collisions(mesh)
    body=mesh.get_editor_property('body_setup')
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('map load failed')
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=='NAV_Rathaus_TerrainProxy_v73': eas.destroy_actor(a)
    actor=eas.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    actor.set_actor_label('NAV_Rathaus_TerrainProxy_v73'); actor.set_folder_path('Rathaus/NAV')
    c=actor.static_mesh_component; c.set_static_mesh(mesh); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    c.set_collision_profile_name('BlockAll'); c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN,unreal.CollisionResponseType.ECR_IGNORE)
    try: c.set_editor_property('hidden_in_game',True)
    except: pass
    try: actor.set_editor_property('is_spatially_loaded',False)
    except: pass
    bounds=[a for a in eas.get_all_level_actors() if a.get_class().get_name()=='NavMeshBoundsVolume']
    if not bounds: raise RuntimeError('NavMeshBoundsVolume missing')
    b=bounds[0]; old_scale=b.get_actor_scale3d(); b.set_actor_scale3d(unreal.Vector(185.0,185.0,18.0))
    world=unreal.EditorLevelLibrary.get_editor_world(); unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
    if not lvl.save_current_level(): raise RuntimeError('level save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    origin,extent=actor.get_actor_bounds(False)
    bout_origin,bout_extent=b.get_actor_bounds(False)
    out.update({'ok':True,'mesh':mesh.get_path_name(),'proxy_bounds':{'origin':[origin.x,origin.y,origin.z],'extent':[extent.x,extent.y,extent.z]},'nav_bounds':{'origin':[bout_origin.x,bout_origin.y,bout_origin.z],'extent':[bout_extent.x,bout_extent.y,bout_extent.z]},'old_nav_scale':[old_scale.x,old_scale.y,old_scale.z],'new_nav_scale':[b.get_actor_scale3d().x,b.get_actor_scale3d().y,b.get_actor_scale3d().z]})
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_PROXY_V73] '+json.dumps(out))
if not out['ok']: raise RuntimeError('nav proxy install failed')
