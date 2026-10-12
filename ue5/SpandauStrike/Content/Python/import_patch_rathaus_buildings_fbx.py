import unreal, traceback
MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
GEN="/ShooterMaps/GeneratedGIS/RathausSpandauFinal"
FBX=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_buildings_no_landmark.fbx"
def log(s): unreal.log("[RATHAUS_FBX_PATCH] "+str(s))
def import_mesh():
    task=unreal.AssetImportTask()
    task.filename=FBX; task.destination_path=GEN; task.destination_name="SM_Rathaus_Buildings_NoLandmark"
    task.automated=True; task.replace_existing=True; task.replace_existing_settings=True; task.save=True
    opt=unreal.FbxImportUI(); opt.import_mesh=True; opt.import_as_skeletal=False
    opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    opt.import_materials=False; opt.import_textures=False
    opt.static_mesh_import_data.combine_meshes=True
    opt.static_mesh_import_data.generate_lightmap_u_vs=True
    task.options=opt
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    a=unreal.EditorAssetLibrary.load_asset(GEN+"/SM_Rathaus_Buildings_NoLandmark")
    if not a: raise RuntimeError("FBX buildings import failed")
    return a
try:
    new=import_mesh()
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    hits=[]
    for a in eas.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor):
            m=a.static_mesh_component.get_static_mesh()
            mp=m.get_path_name() if m else ""
            lab=a.get_actor_label()
            log("ACTOR "+lab+" | "+mp)
            low=(mp+" "+lab).lower()
            if ("rathaus_buildings" in low or "rathaus_exactbuildings" in low) and "nolandmark" not in low:
                hits.append(a)
    log("HITS="+str(len(hits)))
    for a in hits:
        a.static_mesh_component.set_static_mesh(new)
        a.set_actor_label("Rathaus_Buildings_NoLandmark")
        a.static_mesh_component.set_collision_profile_name("BlockAll")
        log("REPLACED "+a.get_name())
    if not sub.save_current_level(): raise RuntimeError("level save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY")
except Exception as e:
    unreal.log_error("[RATHAUS_FBX_PATCH] FAILED "+str(e))
    unreal.log_error(traceback.format_exc())
    raise
