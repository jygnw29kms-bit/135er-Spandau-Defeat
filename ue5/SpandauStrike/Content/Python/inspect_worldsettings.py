import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
w=unreal.EditorLevelLibrary.get_editor_world()
ws=w.get_world_settings()
unreal.log("[WS] class="+ws.get_class().get_path_name())
for n in ["default_game_mode","default_gameplay_experience","game_mode_override"]:
    try:
        v=ws.get_editor_property(n)
        unreal.log("[WS] %s=%s"%(n,v))
    except Exception as e:
        unreal.log("[WS] %s ERR %s"%(n,e))
for p in ws.get_class().get_properties():
    try:
        nm=p.get_name()
        if "experience" in nm.lower() or "game_mode" in nm.lower():
            unreal.log("[WS_PROP] %s=%s"%(nm,ws.get_editor_property(nm)))
    except: pass
