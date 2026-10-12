import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
w=unreal.EditorLevelLibrary.get_editor_world()
for cmd in [
"obj refs name=falkenhagener_feld_HLODLayer_Instanced shortest",
"obj refs name=falkenhagener_feld_HLODLayer_Merged shortest"]:
    unreal.log("[HLODTRACE] CMD "+cmd)
    unreal.SystemLibrary.execute_console_command(w,cmd)
