import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/staaken_playable_v1"
ROOT="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/"
MATS=["M_Staaken_Terrain","M_Staaken_Building","M_Staaken_Road","M_Staaken_Water"]
def log(s):unreal.log("[STAAKEN_FINAL] "+str(s))
try:
 sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not sub.load_level(MAP):raise RuntimeError("map load failed")
 actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 for name in MATS:
  m=unreal.EditorAssetLibrary.load_asset(ROOT+name)
  if not m:continue
  try:m.set_editor_property("used_with_nanite",True)
  except:pass
  unreal.MaterialEditingLibrary.recompile_material(m)
  unreal.EditorAssetLibrary.save_loaded_asset(m,False)
  log("material "+name)
 actors=actor_sub.get_all_level_actors()
 for a in actors:
  n=a.get_class().get_name()
  if n=="DirectionalLight":
   try:a.light_component.set_editor_property("intensity",2.35)
   except:pass
  elif n=="SkyLight":
   try:a.light_component.set_editor_property("intensity",0.9);a.light_component.set_editor_property("real_time_capture",True)
   except:pass
  elif n=="ExponentialHeightFog":
   try:a.component.set_editor_property("fog_density",0.0012);a.component.set_editor_property("start_distance",5000.0)
   except:pass
  elif n=="PostProcessVolume":
   try:
    s=a.get_editor_property("settings");s.set_editor_property("auto_exposure_bias",1.15);s.set_editor_property("override_auto_exposure_bias",True);a.set_editor_property("settings",s)
   except:pass
 world=unreal.EditorLevelLibrary.get_editor_world()
 unreal.SystemLibrary.execute_console_command(world,"n.bNavmeshAllowPartitionedBuildingFromEditor 1")
 unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
 recasts=[a for a in actor_sub.get_all_level_actors() if a.get_class().get_name()=="RecastNavMesh"]
 if recasts:
  nav=recasts[0]
  try:nav.set_editor_property("is_world_partitioned",True)
  except Exception as e:log("WP nav note "+str(e))
  try:nav.set_editor_property("runtime_generation",unreal.RuntimeGenerationType.STATIC)
  except Exception as e:log("static nav note "+str(e))
  try:nav.set_editor_property("is_spatially_loaded",False)
  except:pass
  nav.modify();log("recast configured")
 if not sub.save_current_level():raise RuntimeError("save failed")
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 log("READY")
except Exception as e:
 unreal.log_error("[STAAKEN_FINAL] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
