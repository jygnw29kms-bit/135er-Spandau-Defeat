import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP):raise RuntimeError("load fail")
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    cl=a.get_class()
    print("[V8ACT]",a.get_actor_label(),"|",cl.get_name(),"|",cl.get_path_name(),"| folder=",a.get_folder_path(),"| loc=",a.get_actor_location())
