import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
WEST=[
(-33106.3465,-28486.0605,163.0),
(-32665.073,38261.75925,121.0),
(-47041.6485,8439.50425,138.5),
(-18779.47375,-1525.5355,110.5)]
EAST=[
(43856.54275,-2794.59525,192.0),
(18885.18575,47095.844,-128.5),
(41435.02,-47980.2645,237.0),
(18977.2985,14933.2365,2.0)]

def log(s):
    unreal.log("[RATHAUS_V2] "+str(s))

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP):
        raise RuntimeError("map load failed")
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=actor_sub.get_all_level_actors()
    starts=sorted([a for a in actors if a.get_class().get_name()=="LyraPlayerStart"],key=lambda a:a.get_actor_label())
    if len(starts)<8:
        raise RuntimeError("not enough player starts")
    for a,p in zip(starts[:4],WEST):
        a.set_actor_location(unreal.Vector(*p),False,False)
        a.set_actor_rotation(unreal.Rotator(0,0,0),False)
        a.modify()
        log(a.get_actor_label()+" -> "+str(p))
    for a,p in zip(starts[4:8],EAST):
        a.set_actor_location(unreal.Vector(*p),False,False)
        a.set_actor_rotation(unreal.Rotator(0,180,0),False)
        a.modify()
        log(a.get_actor_label()+" -> "+str(p))
    pp=None
    for a in actors:
        n=a.get_class().get_name()
        if n=="DirectionalLight":
            a.light_component.set_editor_property("intensity",3.2)
        elif n=="SkyLight":
            a.light_component.set_editor_property("intensity",1.15)
        elif n=="PostProcessVolume":
            pp=a
    if not pp:
        pp=actor_sub.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(),unreal.Rotator())
        pp.set_actor_label("Rathaus_V2_PostProcess")
    pp.set_editor_property("unbound",True)
    s=pp.get_editor_property("settings")
    s.set_editor_property("override_auto_exposure_bias",True)
    s.set_editor_property("auto_exposure_bias",1.35)
    pp.set_editor_property("settings",s)
    if not sub.save_current_level():
        raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY")
if __name__=="__main__":
    try:
        main()
    except Exception as e:
        unreal.log_error("[RATHAUS_V2] FAILED "+str(e))
        raise
