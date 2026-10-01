import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\FalkenhagenerFeld_DGM10m.obj"
DEST="/ShooterMaps/GeneratedGIS/FalkenhagenerFeld"
NAME="SM_Falkenhagener_DGM10m"
FOLDER="SpandauStrike_GIS/Terrain"

def log(x): unreal.log("[DGM_IMPORT] "+str(x))

def import_mesh():
    task=unreal.AssetImportTask()
    task.filename=OBJ
    task.destination_path=DEST
    task.destination_name=NAME
    task.automated=True
    task.replace_existing=True
    task.save=True
    task.options=None
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log("paths="+str(task.imported_object_paths))
    if not task.imported_object_paths:
        raise RuntimeError("OBJ import returned no assets")
    for p in task.imported_object_paths:
        a=unreal.EditorAssetLibrary.load_asset(p)
        if isinstance(a,unreal.StaticMesh):
            return a
    raise RuntimeError("No StaticMesh among imported assets")
def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP):
        raise RuntimeError("Map load failed")
    mesh=import_mesh()
    log("mesh="+mesh.get_path_name())
    try:
        b=mesh.get_bounds()
        log("extent_cm="+str(b.box_extent)+" radius_cm="+str(b.sphere_radius))
    except Exception as e:
        log("bounds warning: "+str(e))
    try:
        body=mesh.get_editor_property("body_setup")
        body.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        log("complex collision enabled and saved")
    except Exception as e:
        log("collision setup warning: "+str(e))
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in actors.get_all_level_actors():
        if a.get_actor_label()=="SS_DGM_Terrain":
            actors.destroy_actor(a)
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_collision_profile_name("BlockAll")
    actor.set_actor_label("SS_DGM_Terrain")
    actor.set_folder_path(FOLDER)
    try:
        actor.set_is_spatially_loaded(False)
    except: pass
    mat=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")
    if mat:
        actor.static_mesh_component.set_material(0,mat)
    if not sub.save_current_level():
        raise RuntimeError("Map save failed")
    log("DGM_TERRAIN_READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[DGM_IMPORT] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
