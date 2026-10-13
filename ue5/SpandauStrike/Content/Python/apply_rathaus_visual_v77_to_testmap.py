import unreal, os, json, traceback
TEST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_VISUAL_v77_TEST'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v77/SM_RathausSpandau_DGM1_DOP_v77'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v76/M_Rathaus_DOP2025_v76'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_visual_v77_testmap_apply.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(TEST): raise RuntimeError('test map load failed')
    mesh=unreal.load_asset(MESH); mat=unreal.load_asset(MAT)
    if not mesh or not mat: raise RuntimeError('v77 mesh or v76 material missing')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    dgm=next((a for a in actors if a.get_actor_label() in ('Rathaus_DGM1_DOP2025_v61','Rathaus_DGM1_DOP2025_v77_TEST')),None)
    if not dgm: raise RuntimeError('visible DGM actor missing')
    comp=dgm.static_mesh_component
    old=comp.get_editor_property('static_mesh')
    out['old_mesh']=old.get_path_name() if old else None
    comp.set_static_mesh(mesh); comp.set_material(0,mat)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    comp.set_editor_property('can_ever_affect_navigation',False)
    dgm.set_actor_label('Rathaus_DGM1_DOP2025_v77_TEST')
    origin,extent=dgm.get_actor_bounds(False)
    out['bounds']={'origin':[float(origin.x),float(origin.y),float(origin.z)],'extent':[float(extent.x),float(extent.y),float(extent.z)]}
    out['new_mesh']=comp.get_editor_property('static_mesh').get_path_name()
    out['material']=comp.get_material(0).get_path_name() if comp.get_material(0) else None
    if not lvl.save_current_level(): raise RuntimeError('test map save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str))
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')