import unreal,math,traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
CENTER=(10033.0,-232.5,3500.0)
SP=[
(8296.5,-10080.1,107),(6612.8,-9628.9,279),(13453.2,-9628.9,320),(5033.0,-8892.3,279),
(8036.0,-11557.3,107),(6099.8,-11038.5,279),(7775.6,-13034.5,289),(10033.0,-17732.0,320)]
def log(s):unreal.log("[RATHAUS_CLEAR_SPAWN] "+str(s))
try:
 sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
 if not sub.load_level(MAP):raise RuntimeError("map load failed")
 eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 starts=sorted([a for a in eas.get_all_level_actors() if a.get_class().get_name()=="LyraPlayerStart"],key=lambda a:a.get_actor_label())
 for a,xyz in zip(starts,SP):
  a.set_actor_location(unreal.Vector(*xyz),False,False)
  yaw=math.degrees(math.atan2(CENTER[1]-xyz[1],CENTER[0]-xyz[0]))
  a.set_actor_rotation(unreal.Rotator(0,yaw,0),False)
  log(f"{a.get_actor_label()} {xyz} yaw={yaw:.1f}")
 if not sub.save_current_level():raise RuntimeError("save failed")
 unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
 log("READY")
except Exception as e:
 unreal.log_error("[RATHAUS_CLEAR_SPAWN] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
