import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
DEST="/ShooterMaps/GeneratedGIS/FalkenhagenerFeld"
TERRAIN=DEST+"/SM_Falkenhagener_DGM10m.SM_Falkenhagener_DGM10m"
ROAD_OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_Roads_DGM.obj"
WATER_OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_Water_DGM.obj"
MATS={
 "terrain":"/Game/SpandauStrikeGIS/Materials/M_SS_Terrain.M_SS_Terrain",
 "road":"/Game/SpandauStrikeGIS/Materials/M_SS_Road.M_SS_Road",
 "water":"/Game/SpandauStrikeGIS/Materials/M_SS_Water.M_SS_Water"
}

def log(s): unreal.log("[GIS_OPT] "+str(s))

def import_obj(filename,name):
    task=unreal.AssetImportTask()
    task.filename=filename
    task.destination_path=DEST
    task.destination_name=name
    task.automated=True
    task.replace_existing=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log(name+" paths="+str(task.imported_object_paths))
    for p in task.imported_object_paths:
        a=unreal.EditorAssetLibrary.load_asset(p)
        if isinstance(a,unreal.StaticMesh): return a
    raise RuntimeError("No StaticMesh imported for "+name)
def spawn_layer(actors,label,mesh,mat_path,collision,folder):
    a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    a.static_mesh_component.set_static_mesh(mesh)
    mat=unreal.EditorAssetLibrary.load_asset(mat_path)
    if mat: a.static_mesh_component.set_material(0,mat)
    a.static_mesh_component.set_collision_profile_name(collision)
    if collision=="NoCollision":
        try: a.static_mesh_component.set_editor_property("cast_shadow",False)
        except: pass
    a.set_actor_label(label)
    a.set_folder_path(folder)
    try: a.set_is_spatially_loaded(False)
    except Exception as e: log(label+" spatial warning "+str(e))
    return a

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("Map load failed")
    terrain=unreal.EditorAssetLibrary.load_asset(TERRAIN)
    if not terrain: raise RuntimeError("Terrain asset missing")
    roads=import_obj(ROAD_OBJ,"SM_Falkenhagener_Roads_DGM")
    water=import_obj(WATER_OBJ,"SM_Falkenhagener_Water_DGM")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    spawn_layer(actors,"SS_DGM_Terrain",terrain,MATS["terrain"],"BlockAll","SpandauStrike_GIS/Terrain")
    spawn_layer(actors,"SS_DGM_Roads",roads,MATS["road"],"NoCollision","SpandauStrike_GIS/Roads")
    spawn_layer(actors,"SS_DGM_Water",water,MATS["water"],"NoCollision","SpandauStrike_GIS/Water")
    try:
        world=unreal.EditorLevelLibrary.get_editor_world()
        unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
        log("navigation rebuild requested")
    except Exception as e:
        log("navigation rebuild warning "+str(e))
    if not sub.save_current_level(): raise RuntimeError("Map save failed")
    log("OPTIMIZED_GIS_READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[GIS_OPT] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
