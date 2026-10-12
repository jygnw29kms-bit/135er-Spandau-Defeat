import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actor_sub.get_all_level_actors():
    if a.get_class().get_name()=="LyraPlayerStart":
        l=a.get_actor_location(); r=a.get_actor_rotation()
        unreal.log("[GOODSPAWN] %s loc=(%.3f,%.3f,%.3f) rot=(%.3f,%.3f,%.3f)"%(a.get_actor_label(),l.x,l.y,l.z,r.pitch,r.yaw,r.roll))
