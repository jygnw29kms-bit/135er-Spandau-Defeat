import unreal, os, json, traceback
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_DGM1_DOP_v78.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v78'; NAME='SM_RathausSpandau_DGM1_DOP_v78'
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_dgm_v78_probe.json')
out={'ok':False,'errors':[],'rows':[]}
try:
    task=unreal.AssetImportTask(); task.filename=SRC; task.destination_path=DEST; task.destination_name=NAME; task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    path=(list(task.imported_object_paths)[0] if task.imported_object_paths else DEST+'/'+NAME)
    mesh=unreal.EditorAssetLibrary.load_asset(path)
    if not mesh: raise RuntimeError('v78 import failed')
    sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    out['asset']=mesh.get_path_name(); out['uv_channels']=int(sub.get_num_uv_channels(mesh,0))
    sub.remove_collisions(mesh)
    bs=mesh.get_editor_property('body_setup'); bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor=eas.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator()); actor.set_actor_label('TEMP_Rathaus_VisualDGM_v78_PROBE')
    c=actor.static_mesh_component; c.set_static_mesh(mesh); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY); c.set_collision_profile_name('BlockAll')
    origin,extent=actor.get_actor_bounds(False); out['bounds']={'origin':[float(origin.x),float(origin.y),float(origin.z)],'extent':[float(extent.x),float(extent.y),float(extent.z)]}
    for x,y in [(-12000.0,-12000.0),(12000.0,-12000.0)]:
        r=c.line_trace_component(unreal.Vector(x,y,2000),unreal.Vector(x,y,-3000),True,False)
        out['rows'].append({'xy':[x,y],'hit':None if r is None else [float(r[0].x),float(r[0].y),float(r[0].z)]})
    eas.destroy_actor(actor); out['ok']=out['uv_channels']>=1 and all(r['hit'] is not None for r in out['rows'])
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
