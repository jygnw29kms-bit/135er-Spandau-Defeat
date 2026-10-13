import unreal,os,json,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'; MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v81/SM_RathausSpandau_ROADS_DGM_v81_PROJECTED'; MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v80/M_Rathaus_ROADS_Asphalt_v80'; R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_roads_v81_final_install.json'); out={'ok':False,'errors':[]}
try:
 lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not lvl.load_level(MAP): raise RuntimeError('load FINAL failed')
 mesh=unreal.load_asset(MESH); mat=unreal.load_asset(MAT)
 if not mesh or not mat: raise RuntimeError('asset missing')
 road=None
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if hasattr(a,'static_mesh_component'):
   c=a.static_mesh_component; sm=c.get_editor_property('static_mesh') if c else None; p=sm.get_path_name() if sm else ''
   if a.get_actor_label()=='Rathaus_ROADS_VISUAL_v80' or 'ROADS_DGM_v80' in p or a.get_actor_label()=='Rathaus_ROADS_VISUAL_v81': road=a; break
 if not road: raise RuntimeError('road actor not found')
 c=road.static_mesh_component; old=c.get_editor_property('static_mesh'); out['old_mesh']=old.get_path_name() if old else None
 c.set_static_mesh(mesh); c.set_material(0,mat); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_editor_property('can_ever_affect_navigation',False); road.set_actor_label('Rathaus_ROADS_VISUAL_v81')
 out['new_mesh']=c.get_editor_property('static_mesh').get_path_name(); out['material']=c.get_material(0).get_path_name(); out['collision']=str(c.get_collision_enabled()); out['can_affect_navigation']=bool(c.get_editor_property('can_ever_affect_navigation'))
 out['save_current_level']=bool(lvl.save_current_level()); unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True); out['ok']=out['save_current_level']
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True); open(R,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False,default=str)); print(json.dumps(out,indent=2,ensure_ascii=False,default=str)); unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')