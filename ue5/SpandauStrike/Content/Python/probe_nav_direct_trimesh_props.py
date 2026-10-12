import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL';DGM='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60.SM_RathausSpandau_DGM1_DOP_v60';ROADS='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54.SM_RathausSpandau_ROADS_DGM_v54'
out={'ok':True,'errors':[]}
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lvl.load_level(MAP);smes=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
dgm=unreal.load_asset(DGM);out['dgm_nav_before']=str(dgm.get_editor_property('nav_collision'));out['convex_before']=smes.get_convex_collision_count(dgm);smes.remove_collisions(dgm);out['convex_after']=smes.get_convex_collision_count(dgm)
try:dgm.set_editor_property('nav_collision',None);out['dgm_nav_after_set']=str(dgm.get_editor_property('nav_collision'))
except Exception as e:out['nav_collision_set_error']=str(e)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 c=a.get_component_by_class(unreal.StaticMeshComponent)
 if c and c.static_mesh and c.static_mesh.get_path_name()==ROADS:
  out['roads_label']=a.get_actor_label()
  for prop in ['can_ever_affect_navigation','can_affect_navigation_generation','b_can_ever_affect_navigation']:
   try:out[prop+'_before']=str(c.get_editor_property(prop));c.set_editor_property(prop,False);out[prop+'_after']=str(c.get_editor_property(prop))
   except Exception as e:out[prop+'_error']=str(e)
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_direct_trimesh_property_probe.json');open(report,'w',encoding='utf-8').write(json.dumps(out,indent=2));unreal.log('[NAV_PROP_PROBE] '+json.dumps(out))
