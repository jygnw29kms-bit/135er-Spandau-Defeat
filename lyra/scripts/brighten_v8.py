import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
def log(s): unreal.log("[V8LIGHT] "+str(s))
try:
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=actor_sub.get_all_level_actors()
    pp=None
    for a in actors:
        n=a.get_class().get_name()
        if n=="DirectionalLight":
            a.light_component.set_editor_property("intensity",4.0)
            try:a.light_component.set_editor_property("indirect_lighting_intensity",1.15)
            except:pass
            log("sun=4.0")
        elif n=="SkyLight":
            a.light_component.set_editor_property("intensity",1.25)
            try:a.light_component.set_editor_property("real_time_capture",True)
            except:pass
            log("sky=1.25")
        elif n=="ExponentialHeightFog":
            try:
                c=a.component
                c.set_editor_property("fog_density",0.001)
                c.set_editor_property("fog_height_falloff",0.18)
                c.set_editor_property("start_distance",5000.0)
            except: pass
        elif n=="PostProcessVolume":
            pp=a
    if not pp:
        pp=actor_sub.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(),unreal.Rotator())
        pp.set_actor_label("SS_DaylightPostProcess")
        pp.set_folder_path("SpandauStrike_V8/Lighting")
    pp.set_editor_property("unbound",True)
    s=pp.get_editor_property("settings")
    try:
        s.set_editor_property("override_auto_exposure_bias",True)
        s.set_editor_property("auto_exposure_bias",1.0)
    except Exception as e: log("exposure bias warning "+str(e))
    try:
        s.set_editor_property("override_color_saturation",True)
        s.set_editor_property("color_saturation",unreal.Vector4(1.04,1.04,1.04,1.0))
    except: pass
    pp.set_editor_property("settings",s)
    world=unreal.EditorLevelLibrary.get_editor_world()
    try: unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    except: pass
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY daylight")
except Exception as e:
    unreal.log_error("[V8LIGHT] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
