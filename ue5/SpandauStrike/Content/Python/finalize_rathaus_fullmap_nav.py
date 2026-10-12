import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_fullmap_v1"
def log(s): unreal.log("[RATHAUS_FULLMAP_NAV] "+str(s))
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP):
        raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world=unreal.EditorLevelLibrary.get_editor_world()
    unreal.SystemLibrary.execute_console_command(world,"n.bNavmeshAllowPartitionedBuildingFromEditor 1")

    recasts=[a for a in actor_sub.get_all_level_actors() if a.get_class().get_name()=="RecastNavMesh"]
    if not recasts:
        nav=actor_sub.spawn_actor_from_class(unreal.RecastNavMesh,unreal.Vector(0,0,0),unreal.Rotator())
        nav.set_actor_label("RecastNavMesh-Default")
        nav.set_folder_path("RathausFull/Gameplay")
        recasts=[nav]
        log("spawned RecastNavMesh")

    nav=recasts[0]
    try: nav.set_editor_property("is_world_partitioned",True)
    except Exception as e: log("WP setting note "+str(e))
    try: nav.set_editor_property("runtime_generation",unreal.RuntimeGenerationType.STATIC)
    except Exception as e: log("runtime generation note "+str(e))
    try: nav.set_editor_property("is_spatially_loaded",False)
    except: pass
    nav.modify()

    unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    log("rebuild requested")
    if not lvl.save_current_level():
        raise RuntimeError("level save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("RECASTS="+str(len([a for a in actor_sub.get_all_level_actors() if a.get_class().get_name()=="RecastNavMesh"])))
    log("READY")
except Exception as e:
    unreal.log_error("[RATHAUS_FULLMAP_NAV] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
