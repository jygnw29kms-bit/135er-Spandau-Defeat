import unreal
for p in (
"/ShooterMaps/Maps/SpandauStrikeGIS/Assets/SM_Falkenhagener_ExactBuildings",
"/ShooterMaps/Maps/SpandauStrikeGIS/Assets/SM_Falkenhagener_DGM1",
"/Game/SpandauStrike/GIS/SM_Falkenhagener_DGM1_10m"):
    m=unreal.EditorAssetLibrary.load_asset(p)
    if not m:
        unreal.log_warning("[MESHCHK] missing "+p); continue
    unreal.log("[MESHCHK] "+p)
    try: unreal.log("[MESHCHK] bounds="+str(m.get_bounds()))
    except Exception as e: unreal.log_warning("[MESHCHK] bounds fail "+str(e))
    try:
        imp=m.get_editor_property("asset_import_data")
        unreal.log("[MESHCHK] import="+str(imp.extract_filenames()))
    except Exception as e: unreal.log_warning("[MESHCHK] import fail "+str(e))
    try:
        bs=m.get_editor_property("body_setup")
        unreal.log("[MESHCHK] collision="+str(bs.get_editor_property("collision_trace_flag")))
    except Exception as e: unreal.log_warning("[MESHCHK] collision fail "+str(e))
