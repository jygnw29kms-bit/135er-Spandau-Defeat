import unreal
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
def log(x): unreal.log("[RATHAUS_DETAIL] "+str(x))
sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not sub.load_level(MAP): raise RuntimeError("map load failed")
for p in unreal.EditorAssetLibrary.list_assets(ROOT,True,False):
    a=unreal.EditorAssetLibrary.load_asset(p)
    if not a or a.get_class().get_name()!="StaticMeshActor": continue
    c=a.static_mesh_component
    m=c.get_editor_property("static_mesh")
    if not m: continue
    origin,extent=a.get_actor_bounds(False)
    log("actor="+a.get_actor_label())
    log("bounds_origin="+str((origin.x,origin.y,origin.z)))
    log("bounds_extent="+str((extent.x,extent.y,extent.z)))
    log("materials="+str([str(x.get_path_name()) if x else "None" for x in c.get_materials()]))
    try:
        bs=m.get_editor_property("body_setup")
        log("body_setup="+str(bs.get_path_name() if bs else None))
        if bs:
            agg=bs.get_editor_property("agg_geom")
            log("simple_box="+str(len(agg.get_editor_property("box_elems"))))
            log("simple_sphere="+str(len(agg.get_editor_property("sphere_elems"))))
            log("simple_capsule="+str(len(agg.get_editor_property("sphyl_elems"))))
            log("simple_convex="+str(len(agg.get_editor_property("convex_elems"))))
            log("collision_trace="+str(bs.get_editor_property("collision_trace_flag")))
    except Exception as e: log("body_err="+str(e))
log("DONE")