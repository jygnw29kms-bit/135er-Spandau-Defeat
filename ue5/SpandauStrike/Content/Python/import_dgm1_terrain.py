import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\DGM1\falkenhagener_terrain_10m.obj"
DEST="/ShooterMaps/Generated/SpandauStrikeGIS"
MESH_NAME="SM_Falkenhagener_DGM1_10m"

def log(s): unreal.log("[DGM_IMPORT] "+str(s))

def make_material(name,color,rough=0.9,metal=0.0):
    path=f"{DEST}/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    fac=unreal.MaterialFactoryNew()
    mat=tools.create_asset(name,DEST,unreal.Material,fac)
    c=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector)
    c.set_editor_property("constant",unreal.LinearColor(*color,1.0))
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant)
    r.set_editor_property("r",rough)
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    m=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant)
    m.set_editor_property("r",metal)
    unreal.MaterialEditingLibrary.connect_material_property(m,"",unreal.MaterialProperty.MP_METALLIC)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(path,False)
    return mat

def import_mesh():
    path=f"{DEST}/{MESH_NAME}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    task=unreal.AssetImportTask()
    task.set_editor_property("filename",OBJ)
    task.set_editor_property("destination_path",DEST)
    task.set_editor_property("destination_name",MESH_NAME)
    task.set_editor_property("automated",True)
    task.set_editor_property("save",True)
    task.set_editor_property("replace_existing",True)
    opts=unreal.FbxImportUI()
    opts.set_editor_property("import_mesh",True)
    opts.set_editor_property("import_as_skeletal",False)
    opts.static_mesh_import_data.set_editor_property("combine_meshes",True)
    opts.static_mesh_import_data.set_editor_property("generate_lightmap_u_vs",False)
    task.set_editor_property("options",opts)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    asset=unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        raise RuntimeError("terrain import failed")
    return asset

def main():
    terrain_mat=make_material("M_SS_Terrain",(0.19,0.24,0.12),0.95,0.0)
    make_material("M_SS_Road",(0.035,0.04,0.045),0.9,0.0)
    make_material("M_SS_Water",(0.03,0.16,0.28),0.25,0.05)
    mesh=import_mesh()
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    actors=unreal.EditorLevelLibrary.get_all_level_actors()
    for a in actors:
        if a.get_actor_label()=="SS_DGM1_Terrain":
            unreal.EditorLevelLibrary.destroy_actor(a)
    a=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    a.set_actor_label("SS_DGM1_Terrain")
    a.set_folder_path("SpandauStrike_GIS/Terrain")
    a.static_mesh_component.set_static_mesh(mesh)
    a.static_mesh_component.set_material(0,terrain_mat)
    a.static_mesh_component.set_collision_profile_name("BlockAll")
    a.static_mesh_component.set_editor_property("mobility",unreal.ComponentMobility.STATIC)
    if not sub.save_current_level(): raise RuntimeError("save failed")
    log("TERRAIN_READY")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        unreal.log_error("[DGM_IMPORT] FAILED "+str(exc))
        unreal.log_error(traceback.format_exc())
        raise
