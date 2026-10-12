import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if a.get_class().get_name()=="RecastNavMesh":
        unreal.log("[NAVCHECK] actor="+a.get_actor_label())
        for p in ("is_world_partitioned","runtime_generation","is_spatially_loaded","tile_size_uu","cell_size","cell_height"):
            try: unreal.log("[NAVCHECK] "+p+"="+str(a.get_editor_property(p)))
            except Exception as e: unreal.log("[NAVCHECK] "+p+" ERR "+str(e))
