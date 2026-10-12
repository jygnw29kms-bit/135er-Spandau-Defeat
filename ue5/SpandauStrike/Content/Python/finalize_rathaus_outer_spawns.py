import unreal, math, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
CENTER=(10033.0,-232.5,3000.0)
SP=[
(5500,-10000,279),(8000,-10500,279),(12000,-10500,107),(14500,-10000,320),
(4500,9000,101),(7500,9500,101),(12500,9500,179),(15500,9000,179)]
def log(s):unreal.log("[RATHAUS_OUTER_SPAWN] "+str(s))
try:
 sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not sub.load_level(MAP):raise RuntimeError("map load failed")
 eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 starts=sorted([a for a in eas.get_all_level_actors() if a.get_class().get_name()=="LyraPlayerStart"],key=lambda a:a.get_actor_label())
 for a,xyz in zip(starts,SP):
  a.set_actor_location(unreal.Vector(*xyz),False,False)
  yaw=math.degrees(math.atan2(CENTER[1]-xyz[1],CENTER[0]-xyz[0]))
  a.set_actor_rotation(unreal.Rotator(0,yaw,0),False)
  try:a.set_editor_property("is_spatially_loaded",False)
  except:pass
  log(f"{a.get_actor_label()} {xyz} yaw={yaw:.1f}")
 if not sub.save_current_level():raise RuntimeError("save failed")
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 log("READY")
except Exception as e:
 unreal.log_error("[RATHAUS_OUTER_SPAWN] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
