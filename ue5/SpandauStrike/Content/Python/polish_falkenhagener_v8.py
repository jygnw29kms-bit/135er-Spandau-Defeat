import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
def log(s): unreal.log("[V8POLISH] "+str(s))
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        n=a.get_class().get_name()
        if n=="DirectionalLight":
            a.light_component.set_editor_property("intensity",1.15)
            log("sun=1.15")
        elif n=="SkyLight":
            a.light_component.set_editor_property("intensity",0.45)
            try:a.light_component.set_editor_property("real_time_capture",True)
            except:pass
            log("sky=0.45")
        elif n=="ExponentialHeightFog":
            try:
                c=a.component
                c.set_editor_property("fog_density",0.002)
                c.set_editor_property("fog_height_falloff",0.22)
                c.set_editor_property("start_distance",3500.0)
            except Exception as e: log("fog warning "+str(e))
    world=unreal.EditorLevelLibrary.get_editor_world()
    try: unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    except: pass
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY")
except Exception as e:
    unreal.log_error("[V8POLISH] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
