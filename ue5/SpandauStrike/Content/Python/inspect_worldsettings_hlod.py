import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
w=unreal.EditorLevelLibrary.get_editor_world()
ws=w.get_world_settings()
unreal.log("[WSHLOD] class="+ws.get_class().get_name())
for n in sorted(dir(ws)):
    if "hlod" in n.lower() or "navigation" in n.lower() or "nav" in n.lower():
        try:
            v=ws.get_editor_property(n)
            unreal.log("[WSHLOD] "+n+"="+str(v))
        except:
            unreal.log("[WSHLOD] member="+n)
