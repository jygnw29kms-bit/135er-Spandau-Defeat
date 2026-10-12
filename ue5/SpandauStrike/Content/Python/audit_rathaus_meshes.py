import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
def log(x): unreal.log("[RATHAUS_MESH] "+str(x))
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
assets=unreal.EditorAssetLibrary.list_assets(ROOT,True,False)
for p in assets:
    try:
        a=unreal.EditorAssetLibrary.load_asset(p)
        if a and a.get_class().get_name()=="StaticMeshActor":
            c=a.static_mesh_component
            m=c.get_editor_property("static_mesh")
            loc=a.get_actor_location()
            log("actor="+a.get_actor_label())
            log("loc="+str((loc.x,loc.y,loc.z)))
            log("mesh="+str(m.get_path_name() if m else None))
            try: log("collision="+str(c.get_collision_enabled()))
            except Exception as e: log("collision_err="+str(e))
            try: log("bounds="+str(c.bounds.box_extent))
            except Exception as e: log("bounds_err="+str(e))
    except Exception as e: log("load_fail "+p+" "+str(e))
log("DONE")