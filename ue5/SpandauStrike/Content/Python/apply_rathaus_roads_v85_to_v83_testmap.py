import unreal,os,json,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_DGM_v83_TEST'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v85/SM_RathausSpandau_ROADS_DGM_v85_PROJECTED_V83'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v80/M_Rathaus_ROADS_Asphalt_v80'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_v85_v83_testmap_apply.json')
out={'ok':False,'errors':[]}
try:
 lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not lvl.load_level(MAP): raise RuntimeError('load test map failed')
 mesh=unreal.load_asset(MESH); mat=unreal.load_asset(MAT)
 if not mesh or not mat: raise RuntimeError('asset missing')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors(); road=None
 for a in actors:
  c=getattr(a,'static_mesh_component',None)
  sm=c.get_editor_property('static_mesh') if c else None
  p=sm.get_path_name() if sm else ''
  lab=a.get_actor_label()
  if 'ROADS_VISUAL' in lab or 'ROADS_DGM_v8' in p: road=a; break
 if not road: raise RuntimeError('road actor not found')
 c=road.static_mesh_component
 out['old_label']=road.get_actor_label(); out['old_mesh']=c.get_editor_property('static_mesh').get_path_name()
 c.set_static_mesh(mesh); c.set_material(0,mat); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_editor_property('can_ever_affect_navigation',False)
 road.set_actor_label('Rathaus_ROADS_VISUAL_v85_TEST')
 out['new_mesh']=c.get_editor_property('static_mesh').get_path_name(); out['material']=c.get_material(0).get_path_name()
 out['save']=bool(lvl.save_current_level()); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); out['ok']=out['save']
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True); open(R,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str)); print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')