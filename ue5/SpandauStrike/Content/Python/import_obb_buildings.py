import unreal, traceback
SRC=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\falkenhagener_buildings_obb.obj"
DEST="/ShooterMaps/GeneratedGIS/FalkenhagenerFeld"
NAME="SM_Falkenhagener_Buildings_OBB"
try:
    task=unreal.AssetImportTask()
    task.filename=SRC
    task.destination_path=DEST
    task.destination_name=NAME
    task.automated=True
    task.replace_existing=True
    task.replace_existing_settings=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    p=f"{DEST}/{NAME}"
    a=unreal.EditorAssetLibrary.load_asset(p)
    if not a: raise RuntimeError("import failed")
    unreal.EditorAssetLibrary.save_loaded_asset(a,False)
    unreal.log("[OBB_IMPORT] READY "+p)
except Exception as e:
    unreal.log_error("[OBB_IMPORT] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
