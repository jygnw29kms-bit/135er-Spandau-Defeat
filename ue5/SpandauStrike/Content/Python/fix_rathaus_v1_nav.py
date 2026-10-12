import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
def log(s): unreal.log("[RATHAUS_NAV] "+str(s))
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    recasts=[a for a in actor_sub.get_all_level_actors() if a.get_class().get_name()=="RecastNavMesh"]
    if not recasts: raise RuntimeError("RecastNavMesh missing")
    nav=recasts[0]
    nav.set_editor_property("is_world_partitioned",True)
    try: nav.set_editor_property("is_spatially_loaded",False)
    except Exception as e: log("spatial "+str(e))
    nav.modify()
    world=unreal.EditorLevelLibrary.get_editor_world()
    unreal.SystemLibrary.execute_console_command(world,"n.bNavmeshAllowPartitionedBuildingFromEditor 1")
    unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY world_partitioned="+str(nav.get_editor_property("is_world_partitioned")))
except Exception as e:
    unreal.log_error("[RATHAUS_NAV] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
