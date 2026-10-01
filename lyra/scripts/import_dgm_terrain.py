import unreal, traceback

OBJ = r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1\falkenhagener_dgm_257.obj"
DEST = "/Game/SpandauStrikeGIS/Terrain"
NAME = "falkenhagener_dgm_257"

def main():
    task = unreal.AssetImportTask()
    task.filename = OBJ
    task.destination_path = DEST
    task.destination_name = NAME
    task.automated = True
    task.replace_existing = True
    task.save = True
    task.replace_existing_settings = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    unreal.log("[DGM_IMPORT] imported="+str(task.imported_object_paths))
    paths = list(task.imported_object_paths)
    if not paths:
        raise RuntimeError("OBJ import produced no asset")
    mesh = unreal.EditorAssetLibrary.load_asset(paths[0])
    if not mesh:
        raise RuntimeError("Imported mesh not loadable: "+paths[0])
    try:
        mesh.set_editor_property("allow_cpu_access", False)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    unreal.log("[DGM_IMPORT] READY "+mesh.get_path_name())

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        unreal.log_error("[DGM_IMPORT] FAILED "+str(exc))
        unreal.log_error(traceback.format_exc())
        raise

