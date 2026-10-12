import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
sub.load_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    comp=getattr(a,"static_mesh_component",None)
    mesh=comp.get_static_mesh() if comp else None
    print("[ACTOR]",a.get_actor_label(),"|",mesh.get_path_name() if mesh else "")
