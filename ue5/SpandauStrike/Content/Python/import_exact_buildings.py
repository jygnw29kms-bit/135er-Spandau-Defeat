import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\falkenhagener_buildings_exact.obj"
ASSET_DIR="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
MESH=ASSET_DIR+"/SM_Falkenhagener_ExactBuildings"
MAT=ASSET_DIR+"/M_Falkenhagener_Buildings"

def log(s): unreal.log("[BLDG_IMPORT] "+str(s))

def ensure_mat():
    if unreal.EditorAssetLibrary.does_asset_exist(MAT):
        return unreal.EditorAssetLibrary.load_asset(MAT)
    m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_Falkenhagener_Buildings",ASSET_DIR,unreal.Material,unreal.MaterialFactoryNew())
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-250,-50)
    c.set_editor_property("constant",unreal.LinearColor(0.22,0.24,0.26,1.0))
    r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-250,80)
    r.set_editor_property("r",0.78)
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT)
    return m
def import_mesh():
    if unreal.EditorAssetLibrary.does_asset_exist(MESH):
        unreal.EditorAssetLibrary.delete_asset(MESH)
    task=unreal.AssetImportTask()
    task.filename=OBJ
    task.destination_path=ASSET_DIR
    task.destination_name="SM_Falkenhagener_ExactBuildings"
    task.automated=True
    task.save=True
    task.replace_existing=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if not task.imported_object_paths:
        raise RuntimeError("building OBJ import failed")
    return unreal.EditorAssetLibrary.load_asset(task.imported_object_paths[0])

def main():
    mat=ensure_mat()
    mesh=import_mesh()
    if not mesh: raise RuntimeError("mesh missing")
    try:
        bs=mesh.get_editor_property("body_setup")
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        mesh.mark_package_dirty()
        unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
    except Exception as e:
        log("complex collision setup skipped: "+str(e))
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    root="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
    for p in unreal.EditorAssetLibrary.list_assets(root,recursive=True,include_folder=False):
        o=unreal.EditorAssetLibrary.load_asset(p)
        if isinstance(o,unreal.StaticMeshActor) and o.get_actor_label()=="SS_ExactBuildings":
            try: unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(o)
            except: pass
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    a.set_actor_label("SS_ExactBuildings")
    a.set_folder_path("SpandauStrike_GIS/Buildings")
    a.static_mesh_component.set_static_mesh(mesh)
    a.static_mesh_component.set_material(0,mat)
    a.static_mesh_component.set_collision_profile_name("BlockAll")
    if not sub.save_current_level(): raise RuntimeError("save failed")
    b=mesh.get_bounds()
    log("bounds origin=%s extent=%s"%(b.origin,b.box_extent))
    log("EXACT_BUILDINGS_READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[BLDG_IMPORT] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
