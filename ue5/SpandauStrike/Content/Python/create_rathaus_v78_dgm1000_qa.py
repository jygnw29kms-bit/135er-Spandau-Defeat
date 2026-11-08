import json, os, traceback, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v78_GAMEPLAY_DGM1000_QA'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v86/SM_RathausSpandau_DGM1_v86_GAMEPLAY1000'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v78_dgm1000_create.json')
out={'ok':False,'errors':[]}
try:
    if unreal.EditorAssetLibrary.does_asset_exist(DST):
        unreal.EditorAssetLibrary.delete_asset(DST)
    if not unreal.EditorAssetLibrary.duplicate_asset(SRC,DST):
        raise RuntimeError('duplicate v77 -> v78 DGM1000 QA failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(DST):
        raise RuntimeError('load v78 QA map failed')
    mesh=unreal.load_asset(MESH)
    if not mesh:
        raise RuntimeError('v86 DGM1000 mesh missing')
    try:
        body=mesh.get_editor_property('body_setup')
        if body:
            body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
            out['collision']='complex_as_simple'
    except Exception as ce:
        out['collision_warning']=str(ce)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ext=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator(0,0,0))
    if not ext:
        raise RuntimeError('spawn DGM1000 actor failed')
    ext.set_actor_label('Rathaus_DGM1_GAMEPLAY1000_v86_EXT')
    ext.set_actor_scale3d(unreal.Vector(100.0,100.0,100.0))
    comp=ext.static_mesh_component
    comp.set_static_mesh(mesh)
    try:
        comp.set_collision_profile_name('BlockAll')
    except Exception:
        pass
    b=ext.get_actor_bounds(False,False)
    out['actor_bounds_origin']=[b[0].x,b[0].y,b[0].z]
    out['actor_bounds_extent']=[b[1].x,b[1].y,b[1].z]
    out['mesh']=mesh.get_path_name()
    out['save']=bool(lvl.save_current_level())
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=bool(out['save'])
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
