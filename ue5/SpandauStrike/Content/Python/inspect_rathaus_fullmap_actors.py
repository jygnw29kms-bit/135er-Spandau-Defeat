import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_fullmap_v1"
lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lvl.load_level(MAP)
sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    label=a.get_actor_label()
    if label.startswith("RathausFull_") or "PlayerStart" in label or "NavMesh" in label:
        b=a.get_actor_bounds(False,False)
        try: spatial=a.get_editor_property("is_spatially_loaded")
        except: spatial="NA"
        unreal.log("[FULLMAP_INSPECT] %s loc=%s bounds=%s spatial=%s hidden=%s" % (
            label,str(a.get_actor_location()),str(b),str(spatial),str(a.is_hidden_ed())
        ))
        if hasattr(a,"static_mesh_component"):
            c=a.static_mesh_component
            unreal.log("[FULLMAP_INSPECT]   mesh=%s visible=%s hidden_game=%s collision=%s" % (
                str(c.get_editor_property("static_mesh")),
                str(c.get_editor_property("visible")),
                str(c.get_editor_property("hidden_in_game")),
                str(c.get_collision_enabled())
            ))
