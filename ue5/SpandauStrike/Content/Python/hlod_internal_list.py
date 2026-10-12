import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
w=unreal.EditorLevelLibrary.get_editor_world()
for cls in ["WorldPartition","WorldPartitionRuntimeHashSet","RuntimePartitionLHGrid","RuntimePartitionPersistent","RuntimePartitionHLODSetup"]:
    unreal.log("[HLODINT] LIST "+cls)
    unreal.SystemLibrary.execute_console_command(w,"obj list class="+cls)
