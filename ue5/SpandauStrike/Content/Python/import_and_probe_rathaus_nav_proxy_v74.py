import unreal, os, json, traceback
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_NAV_PROXY_v74.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v74'
NAME='SM_RathausSpandau_NAV_PROXY_v74'
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_proxy_v74_probe.json')
out={'ok':False,'errors':[],'rows':[]}
try:
    task=unreal.AssetImportTask(); task.filename=SRC; task.destination_path=DEST; task.destination_name=NAME
    task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.EditorAssetLibrary.load_asset((list(task.imported_object_paths)[0] if task.imported_object_paths else DEST+'/'+NAME))
    if not mesh: raise RuntimeError('v74 import failed')
    sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem); sub.remove_collisions(mesh)
    bs=mesh.get_editor_property('body_setup'); bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor=eas.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    actor.set_actor_label('TEMP_NAV_Rathaus_TerrainProxy_v74_PROBE')
    c=actor.static_mesh_component; c.set_static_mesh(mesh); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS); c.set_collision_profile_name('BlockAll')
    for x,y in [(-12000.0,-12000.0),(12000.0,-12000.0)]:
        r=c.line_trace_component(unreal.Vector(x,y,2000),unreal.Vector(x,y,-3000),True,False)
        out['rows'].append({'xy':[x,y],'hit':None if r is None else [float(r[0].x),float(r[0].y),float(r[0].z)],'normal':None if r is None else [float(r[1].x),float(r[1].y),float(r[1].z)]})
    origin,extent=actor.get_actor_bounds(False)
    out['bounds']={'origin':[float(origin.x),float(origin.y),float(origin.z)],'extent':[float(extent.x),float(extent.y),float(extent.z)]}
    eas.destroy_actor(actor)
    out['ok']=all(row['hit'] is not None for row in out['rows'])
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
