import unreal,os,json,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_DOP_v82_TEST'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v82/M_Rathaus_DOP2025_v82_MATTE'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_dop_v82_testmap_apply.json')
out={'ok':False,'errors':[]}
try:
 lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not lvl.load_level(MAP): raise RuntimeError('load test map failed')
 mat=unreal.load_asset(MAT)
 if not mat: raise RuntimeError('v82 material missing')
 dgm=None
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if hasattr(a,'static_mesh_component'):
   c=a.static_mesh_component; sm=c.get_editor_property('static_mesh') if c else None; p=sm.get_path_name() if sm else ''
   if a.get_actor_label()=='A_Rathaus_DGM1_DOP_v79' or 'DGM1_DOP_v79_SMOOTH' in p: dgm=a; break
 if not dgm: raise RuntimeError('v79 DGM actor not found')
 c=dgm.static_mesh_component; old=c.get_material(0)
 out['old_material']=old.get_path_name() if old else None
 c.set_material(0,mat); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_editor_property('can_ever_affect_navigation',False)
 out['new_material']=c.get_material(0).get_path_name() if c.get_material(0) else None
 out['save']=bool(lvl.save_current_level()); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 out['ok']=out['save'] and out['new_material'].startswith(MAT)
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True); open(R,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str)); print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')