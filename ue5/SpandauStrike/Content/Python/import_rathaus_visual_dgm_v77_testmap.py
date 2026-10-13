import unreal, os, json, traceback
SRC=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\Exports\SM_RathausSpandau_DGM1_DOP_v77.obj'
DEST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v77'
NAME='SM_RathausSpandau_DGM1_DOP_v77'
FINAL='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
TEST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_VISUAL_v77_TEST'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_dgm_v77_import_testmap.json')
out={'ok':False,'errors':[]}
try:
    task=unreal.AssetImportTask(); task.filename=SRC; task.destination_path=DEST; task.destination_name=NAME
    task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.load_asset(DEST+'/'+NAME)
    if not mesh: raise RuntimeError('v77 import failed')
    sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    out['uv_channels']=sub.get_num_uv_channels(mesh,0)
    # Visual mesh only: no player collision/nav contribution; v75 proxy remains authoritative.
    try: sub.remove_collisions(mesh)
    except: pass
    bs=mesh.get_editor_property('body_setup')
    if bs: bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    if unreal.EditorAssetLibrary.does_asset_exist(TEST): unreal.EditorAssetLibrary.delete_asset(TEST)
    if not unreal.EditorAssetLibrary.duplicate_asset(FINAL,TEST): raise RuntimeError('test map duplicate failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(TEST): raise RuntimeError('test map load failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    dgm=next((a for a in actors if a.get_actor_label()=='Rathaus_DGM1_DOP2025_v61'),None)
    if not dgm: raise RuntimeError('visible DGM actor missing')
    comp=dgm.static_mesh_component
    old=comp.get_editor_property('static_mesh')
    out['old_mesh']=old.get_path_name() if old else None
    comp.set_static_mesh(mesh)
    mat=unreal.load_asset(MAT)
    if not mat: raise RuntimeError('v76 material missing')
    comp.set_material(0,mat)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    comp.set_editor_property('can_ever_affect_navigation',False)
    dgm.set_actor_label('Rathaus_DGM1_DOP2025_v77_TEST')
    origin,extent=dgm.get_actor_bounds(False)
    out['bounds']={'origin':[float(origin.x),float(origin.y),float(origin.z)],'extent':[float(extent.x),float(extent.y),float(extent.z)]}
    out['new_mesh']=comp.get_editor_property('static_mesh').get_path_name()
    out['material']=comp.get_material(0).get_path_name() if comp.get_material(0) else None
    if not lvl.save_current_level(): raise RuntimeError('test map save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['test_map']=TEST; out['ok']=out['uv_channels']==1
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')