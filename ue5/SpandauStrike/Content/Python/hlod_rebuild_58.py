import unreal, traceback
DIR="/ShooterMaps/Maps/SpandauStrikeGIS"
def log(s): unreal.log("[HLOD58] "+str(s))
def create(name, layer_type):
    p=DIR+"/"+name
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        if not unreal.EditorAssetLibrary.delete_asset(p):
            raise RuntimeError("cannot replace "+p)
    a=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,DIR,unreal.HLODLayer,unreal.HLODLayerFactory())
    if not a: raise RuntimeError("create failed "+name)
    a.set_editor_property("layer_type",layer_type)
    a.set_editor_property("cell_size",25600)
    a.set_editor_property("loading_range",76800.0)
    a.set_editor_property("is_spatially_loaded",True)
    unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
    log(name+" type="+str(a.get_editor_property("layer_type"))+" settings="+str(a.get_editor_property("hlod_builder_settings")))
    return a
def main():
    create("falkenhagener_feld_HLODLayer_Instanced",unreal.HLODLayerType.INSTANCING)
    create("falkenhagener_feld_HLODLayer_Merged",unreal.HLODLayerType.MESH_MERGE)
    log("READY")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[HLOD58] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
