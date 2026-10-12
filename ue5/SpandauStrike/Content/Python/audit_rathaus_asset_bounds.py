import unreal
MESHES=[
"/ShooterMaps/GeneratedGIS/RathausSpandau/SM_Rathaus_DGM.SM_Rathaus_DGM",
"/ShooterMaps/GeneratedGIS/RathausSpandau/SM_Rathaus_Buildings.SM_Rathaus_Buildings",
"/ShooterMaps/GeneratedGIS/RathausSpandau/SM_Rathaus_Roads.SM_Rathaus_Roads",
"/ShooterMaps/GeneratedGIS/RathausSpandau/SM_Rathaus_Water.SM_Rathaus_Water"]
def log(x): unreal.log("[RATHAUS_ASSET] "+str(x))
for p in MESHES:
    m=unreal.load_asset(p)
    log("mesh="+p)
    if not m:
        log("MISSING"); continue
    try:
        b=m.get_bounds()
        log("origin="+str((b.origin.x,b.origin.y,b.origin.z)))
        log("extent="+str((b.box_extent.x,b.box_extent.y,b.box_extent.z)))
        log("radius="+str(b.sphere_radius))
    except Exception as e: log("bounds_err="+str(e))
    try:
        log("lods="+str(m.get_num_lods()))
    except Exception as e: log("lod_err="+str(e))
    try:
        smss=unreal.EditorStaticMeshLibrary.get_number_materials(m)
        log("material_slots="+str(smss))
    except Exception as e: log("matcount_err="+str(e))
log("DONE")