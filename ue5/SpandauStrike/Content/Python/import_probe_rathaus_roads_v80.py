import unreal, os, json, traceback
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_ROADS_DGM_v80.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v80'; NAME='SM_RathausSpandau_ROADS_DGM_v80'
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_v80_probe.json')
out={'ok':False,'errors':[],'rows':[]}
try:
    task=unreal.AssetImportTask(); task.filename=SRC; task.destination_path=DEST; task.destination_name=NAME
    task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    path=(list(task.imported_object_paths)[0] if task.imported_object_paths else DEST+'/'+NAME)
    mesh=unreal.EditorAssetLibrary.load_asset(path)
    if not mesh: raise RuntimeError('v80 roads import failed')
    sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    out['asset']=mesh.get_path_name(); out['uv_channels']=int(sub.get_num_uv_channels(mesh,0))
    sub.remove_collisions(mesh)
    bs=mesh.get_editor_property('body_setup'); bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=eas.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator()); a.set_actor_label('TEMP_Rathaus_ROADS_v80_PROBE')
    c=a.static_mesh_component; c.set_static_mesh(mesh); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY); c.set_collision_profile_name('BlockAll')
    o,e=a.get_actor_bounds(False); out['bounds']={'origin':[float(o.x),float(o.y),float(o.z)],'extent':[float(e.x),float(e.y),float(e.z)]}
    for x,y in [(-12000.0,-12000.0),(12000.0,-12000.0),(0.0,0.0),(3000.0,0.0)]:
        r=c.line_trace_component(unreal.Vector(x,y,2000),unreal.Vector(x,y,-3000),True,False)
        out['rows'].append({'xy':[x,y],'hit':None if r is None else [float(r[0].x),float(r[0].y),float(r[0].z)]})
    eas.destroy_actor(a)
    out['ok']=out['uv_channels']>=1 and out['bounds']['extent'][0]>17000 and out['bounds']['extent'][1]>17000
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(),'QUIT_EDITOR')
