import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
MATS=[
"/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Rathaus_Terrain",
"/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Rathaus_Building",
"/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Rathaus_Road",
"/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Rathaus_Water"]
SP=[
(-37574.0,-12360.3,170.0),(-38492.6,-3813.0,75.5),(-35577.1,8740.9,32.0),(-32770.3,17369.8,165.0),
(38461.5,13689.8,-136.8),(36347.9,2718.8,73.0),(37292.0,-7298.0,141.0),(31513.5,-17041.5,361.0)]
def log(s):unreal.log("[RATHAUS_FIX] "+str(s))
try:
 sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not sub.load_level(MAP):raise RuntimeError("map load failed")
 for p in MATS:
  m=unreal.EditorAssetLibrary.load_asset(p)
  if m:
   try:m.set_editor_property("used_with_nanite",True)
   except Exception as e:log("nanite flag "+p+" "+str(e))
   unreal.MaterialEditingLibrary.recompile_material(m)
   unreal.EditorAssetLibrary.save_loaded_asset(m,False)
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 starts=sorted([a for a in actors if a.get_class().get_name()=="LyraPlayerStart"],key=lambda a:a.get_actor_label())
 for a,xyz in zip(starts,SP):
  yaw=0 if xyz[0]<0 else 180
  a.set_actor_location(unreal.Vector(*xyz),False,False)
  a.set_actor_rotation(unreal.Rotator(0,yaw,0),False)
  a.modify()
  log(a.get_actor_label()+" -> "+str(xyz))
 recasts=[a for a in actors if a.get_class().get_name()=="RecastNavMesh"]
 if not recasts:
  try:
   nav=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.RecastNavMesh,unreal.Vector(),unreal.Rotator())
   nav.set_actor_label("RecastNavMesh-Default")
   recasts=[nav]
   log("spawned RecastNavMesh")
  except Exception as e:log("recast spawn failed "+str(e))
 for nav in recasts:
  try:nav.set_editor_property("is_world_partitioned",True)
  except Exception as e:log("WP flag error "+str(e))
  try:nav.set_editor_property("runtime_generation",unreal.RuntimeGenerationType.STATIC)
  except Exception as e:log("runtime_generation "+str(e))
  try:nav.set_editor_property("is_spatially_loaded",False)
  except Exception as e:log("spatial "+str(e))
  nav.modify()
 world=unreal.EditorLevelLibrary.get_editor_world()
 unreal.SystemLibrary.execute_console_command(world,"n.bNavmeshAllowPartitionedBuildingFromEditor 1")
 if not sub.save_current_level():raise RuntimeError("save failed")
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 log("READY recasts="+str(len(recasts)))
except Exception as e:
 unreal.log_error("[RATHAUS_FIX] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
