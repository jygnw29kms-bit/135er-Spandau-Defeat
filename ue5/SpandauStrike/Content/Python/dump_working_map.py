import unreal,collections
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=unreal.EditorLevelLibrary.get_editor_world(); ws=w.get_world_settings()
try: unreal.log("[WORK] WS=%s EXP=%s"%(ws.get_class().get_path_name(),ws.get_editor_property("default_gameplay_experience")))
except Exception as e: unreal.log("[WORK] ws err "+str(e))
classes=collections.Counter()
for a in actors.get_all_level_actors():
    classes[a.get_class().get_name()]+=1
    if a.get_class().get_name()=="LyraPlayerStart":
        l=a.get_actor_location(); r=a.get_actor_rotation()
        try: tags=a.get_editor_property("tags")
        except: tags=[]
        try: spt=a.get_editor_property("start_point_tags")
        except: spt="ERR"
        try: spatial=a.get_editor_property("is_spatially_loaded")
        except: spatial="ERR"
        unreal.log("[WORK] PS %s loc=(%.1f,%.1f,%.1f) rot=(%.1f,%.1f,%.1f) tags=%s spt=%s spatial=%s"%(a.get_actor_label(),l.x,l.y,l.z,r.pitch,r.yaw,r.roll,tags,spt,spatial))
for k,v in classes.most_common(): unreal.log("[WORK] class %s=%d"%(k,v))
