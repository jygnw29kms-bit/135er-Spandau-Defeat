import unreal, traceback

OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\falkenhagener_dgm1_10m.obj"
DEST="/Game/SpandauStrike/GIS"
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"

def log(s): unreal.log("[SS_DGM] "+str(s))

def make_mat(name, rgb, rough):
    path=DEST+"/Materials"
    full=path+"/"+name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    mat=tools.create_asset(name,path,unreal.Material,unreal.MaterialFactoryNew())
    color=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
    color.constant=unreal.LinearColor(rgb[0],rgb[1],rgb[2],1.0)
    unreal.MaterialEditingLibrary.connect_material_property(color,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,180)
    r.r=rough
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
def import_mesh():
    full=DEST+"/SM_Falkenhagener_DGM1_10m"
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    task=unreal.AssetImportTask()
    task.filename=OBJ
    task.destination_path=DEST
    task.destination_name="SM_Falkenhagener_DGM1_10m"
    task.automated=True
    task.replace_existing=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.EditorAssetLibrary.load_asset(full)
    if not mesh:
        paths=list(task.imported_object_paths)
        log("imported="+str(paths))
        if paths: mesh=unreal.EditorAssetLibrary.load_asset(paths[0])
    if not mesh: raise RuntimeError("DGM mesh import failed")
    return mesh

def main():
    terrain=make_mat("M_SS_Terrain",(0.12,0.20,0.08),0.92)
    make_mat("M_SS_Road",(0.035,0.04,0.045),0.88)
    make_mat("M_SS_Water",(0.02,0.14,0.24),0.22)
    make_mat("M_SS_Building",(0.28,0.29,0.30),0.82)
    mesh=import_mesh()
    try:
        mesh.set_material(0,terrain)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    except Exception as exc: log("mesh material warning "+str(exc))
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actors=unreal.EditorLevelLibrary.get_all_level_actors()
    for a in actors:
        if a.get_actor_label()=="SS_DGM1_Terrain":
            unreal.EditorLevelLibrary.destroy_actor(a)
    actor=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    actor.static_mesh_component.set_static_mesh(mesh)
    actor.static_mesh_component.set_material(0,terrain)
    actor.set_actor_label("SS_DGM1_Terrain")
    actor.set_folder_path("SpandauStrike_GIS/Terrain")
    try:
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    except Exception as exc: log("collision warning "+str(exc))
    if not sub.save_current_level(): raise RuntimeError("map save failed")
    log("DGM_READY")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        unreal.log_error("[SS_DGM] FAILED "+str(exc))
        unreal.log_error(traceback.format_exc())
        raise
