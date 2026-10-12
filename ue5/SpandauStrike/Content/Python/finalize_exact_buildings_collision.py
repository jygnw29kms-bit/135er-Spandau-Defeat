import unreal, traceback

OBJ=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld\falkenhagener_buildings_exact.obj"
DEST="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
EXACT=DEST+"/SM_Falkenhagener_ExactBuildings"
DGM=DEST+"/SM_Falkenhagener_DGM1"
MAT_B=DEST+"/M_Falkenhagener_Buildings"
MAT_T=DEST+"/M_Falkenhagener_Terrain"
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"

def log(s): unreal.log("[FINALGIS] "+str(s))

def rebuild_material(path,rgb,rough):
    mat=unreal.EditorAssetLibrary.load_asset(path)
    if not mat: raise RuntimeError("missing material "+path)
    try: unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
    except Exception as e: log("delete expressions warning "+str(e))
    c=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.constant=unreal.LinearColor(*rgb,1.0)
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,180)
    r.r=rough
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat
def reimport_exact():
    task=unreal.AssetImportTask()
    task.filename=OBJ
    task.destination_path=DEST
    task.destination_name="SM_Falkenhagener_ExactBuildings"
    task.automated=True
    task.replace_existing=True
    task.replace_existing_settings=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log("imported="+str(list(task.imported_object_paths)))
    m=unreal.EditorAssetLibrary.load_asset(EXACT)
    if not m: raise RuntimeError("exact mesh missing after import")
    return m

def set_complex(mesh,mat=None):
    if mat: mesh.set_material(0,mat)
    bs=mesh.get_editor_property("body_setup")
    if not bs:
        unreal.StaticMeshEditorSubsystem().add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
        bs=mesh.get_editor_property("body_setup")
    bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    mesh.modify()
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    log("collision "+mesh.get_path_name()+"="+str(bs.get_editor_property("collision_trace_flag")))

def update_external_actors(mat_b,mat_t):
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    assets=reg.get_assets_by_path(EXT,recursive=True)
    changed=0
    for a in assets:
        lab=str(a.get_tag_value("ActorLabel") or "")
        if lab!="SS_ExactBuildings" and not lab.startswith("SS_DGM"):
            continue
        obj=a.get_asset()
        if not obj: continue
        try:
            c=obj.static_mesh_component
            if lab=="SS_ExactBuildings":
                c.set_static_mesh(unreal.EditorAssetLibrary.load_asset(EXACT))
                c.set_material(0,mat_b)
            else:
                c.set_material(0,mat_t)
            c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            c.set_collision_profile_name("BlockAll")
            obj.modify()
            if unreal.EditorAssetLibrary.save_asset(str(a.package_name),only_if_is_dirty=False):
                changed+=1
                log("saved actor "+lab)
        except Exception as e:
            unreal.log_warning("[FINALGIS] actor "+lab+" warning "+str(e))
    log("external actors changed="+str(changed))

def main():
    mb=rebuild_material(MAT_B,(0.32,0.29,0.25),0.88)
    mt=rebuild_material(MAT_T,(0.10,0.18,0.07),0.94)
    exact=reimport_exact()
    dgm=unreal.EditorAssetLibrary.load_asset(DGM)
    if not dgm: raise RuntimeError("DGM mesh missing")
    set_complex(exact,mb)
    set_complex(dgm,mt)
    update_external_actors(mb,mt)
    log("FINALIZE_READY")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[FINALGIS] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
