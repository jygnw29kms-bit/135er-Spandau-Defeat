import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("load failed")
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for a in actors:
    label=a.get_actor_label()
    if "Rathaus" in label or "Building" in label or "GIS" in label:
        mesh=""
        try:
            smc=a.get_component_by_class(unreal.StaticMeshComponent)
            if smc and smc.static_mesh: mesh=smc.static_mesh.get_path_name()
        except: pass
        unreal.log("[RATHAUS_INSPECT] "+label+" | "+a.get_class().get_name()+" | "+mesh+" | "+str(a.get_actor_location()))
unreal.log("[RATHAUS_INSPECT] COUNT="+str(len(actors)))
