import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
w=unreal.EditorLevelLibrary.get_editor_world()
unreal.log("[OBJSCAN] world="+w.get_path_name())
# scan unreal module for object/outer helpers
for n in sorted(dir(unreal)):
    if "outer" in n.lower() or ("object" in n.lower() and ("get_" in n.lower() or "find" in n.lower())):
        unreal.log("[OBJSCAN] api="+n)
# inspect world and world partition members
for obj,label in [(w,"WORLD"),(w.get_world_settings(),"WS")]:
    unreal.log("[OBJSCAN] "+label+" class="+obj.get_class().get_name())
    for n in sorted(dir(obj)):
        if "partition" in n.lower() or "hlod" in n.lower() or "runtime" in n.lower():
            try:
                v=obj.get_editor_property(n)
                unreal.log("[OBJSCAN] "+label+"."+n+"="+str(v))
            except:
                unreal.log("[OBJSCAN] "+label+".member="+n)
try:
    wp=w.get_editor_property("world_partition")
    unreal.log("[OBJSCAN] WP="+str(wp)+" class="+wp.get_class().get_name())
    for n in sorted(dir(wp)):
        if "hlod" in n.lower() or "runtime" in n.lower() or "partition" in n.lower():
            try: unreal.log("[OBJSCAN] WP."+n+"="+str(wp.get_editor_property(n)))
            except: unreal.log("[OBJSCAN] WP.member="+n)
except Exception as e:
    unreal.log_error("[OBJSCAN] WP ERR "+str(e))
