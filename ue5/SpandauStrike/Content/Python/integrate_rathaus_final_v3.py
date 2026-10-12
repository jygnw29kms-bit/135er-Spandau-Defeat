import unreal, os, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
DEST="/ShooterMaps/GeneratedGIS/RathausSpandauFinal"
FBX0=r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\engine\RathausSpandau_Landmark_LOD0.fbx"
FBX1=r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\engine\RathausSpandau_Landmark_LOD1.fbx"
FBX2=r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\engine\RathausSpandau_Landmark_LOD2.fbx"
BUILDINGS=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\rathaus_buildings_no_landmark.obj"

def log(x): unreal.log("[RATHAUS_FINAL_V3] "+str(x))

def import_static(path,name,material_import=False):
    task=unreal.AssetImportTask()
    task.filename=path
    task.destination_path=DEST
    task.destination_name=name
    task.automated=True
    task.replace_existing=True
    task.replace_existing_settings=True
    task.save=True
    ui=unreal.FbxImportUI()
    ui.set_editor_property("import_mesh",True)
    ui.set_editor_property("import_as_skeletal",False)
    ui.set_editor_property("import_materials",material_import)
    ui.set_editor_property("import_textures",False)
    sid=ui.get_editor_property("static_mesh_import_data")
    sid.set_editor_property("combine_meshes",True)
    sid.set_editor_property("generate_lightmap_u_vs",True)
    sid.set_editor_property("auto_generate_collision",False)
    task.options=ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.EditorAssetLibrary.load_asset(DEST+"/"+name)
    if not mesh: raise RuntimeError("Import failed "+path)
    return mesh
def make_mat(name,color,rough=.8,metal=0.0):
    path=DEST+"/"+name
    m=unreal.EditorAssetLibrary.load_asset(path)
    if not m:
        m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,DEST,unreal.Material,unreal.MaterialFactoryNew())
    try: unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
    except: pass
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.set_editor_property("constant",unreal.LinearColor(color[0],color[1],color[2],1))
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,150)
    r.set_editor_property("r",rough)
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    mt=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,300)
    mt.set_editor_property("r",metal)
    unreal.MaterialEditingLibrary.connect_material_property(mt,"",unreal.MaterialProperty.MP_METALLIC)
    unreal.MaterialEditingLibrary.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m,False)
    return m

def find_actor(label):
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label()==label: return a
    return None

def ensure_actor(label,mesh,folder):
    a=find_actor(label)
    if not a:
        a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator())
        a.set_actor_label(label)
    a.set_folder_path(folder)
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_location(unreal.Vector(0,0,0),False,False)
    a.set_actor_rotation(unreal.Rotator(0,0,0),False)
    a.static_mesh_component.set_collision_profile_name("BlockAll")
    a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    return a
def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("Map load failed")

    landmark=import_static(FBX0,"SM_Rathaus_Landmark_Final",False)
    smsub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for idx,src in ((1,FBX1),(2,FBX2)):
        try:
            ok=smsub.import_lod(landmark,idx,src)
            log("LOD%d import=%s"%(idx,ok))
        except Exception as e:
            log("LOD%d import warning: %s"%(idx,e))
    bs=landmark.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(landmark,False)

    buildings=import_static(BUILDINGS,"SM_Rathaus_Buildings_NoLandmark",False)
    bbs=buildings.get_editor_property("body_setup")
    if bbs:
        bbs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(buildings,False)

    lm=ensure_actor("Rathaus_Landmark_Final",landmark,"Rathaus_V3/Landmark")
    bg=ensure_actor("Rathaus_SurroundingBuildings",buildings,"Rathaus_V3/Buildings")
    # Remove any obsolete exact-building actor that still includes the old GIS Rathaus.
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in list(actor_sub.get_all_level_actors()):
        if a.get_actor_label() in ("Rathaus_ExactBuildings","Rathaus_Buildings"):
            actor_sub.destroy_actor(a)

    mats=[
      ("M_Rathaus_Stone_Final",(0.46,0.36,0.24),.78,0.0),
      ("M_Rathaus_Trim_Final",(0.72,0.64,0.49),.67,0.0),
      ("M_Rathaus_Roof_Final",(0.45,0.085,0.045),.82,0.0),
      ("M_Rathaus_Copper_Final",(0.08,0.31,0.25),.46,.35),
      ("M_Rathaus_Glass_Final",(0.035,0.07,0.09),.18,.08),
      ("M_Rathaus_Door_Final",(0.055,0.035,0.025),.72,0.0),
      ("M_Rathaus_Gold_Final",(0.74,0.52,0.12),.30,.55),
      ("M_Rathaus_Steps_Final",(0.38,0.36,0.32),.90,0.0)]
    created=[make_mat(*m) for m in mats]
    # Material order follows the Blender master slots; only set as many slots as exist.
    for i,m in enumerate(created):
        try: lm.static_mesh_component.set_material(i,m)
        except: pass
    bmat=make_mat("M_Rathaus_SurroundingBuildings",(0.34,0.29,0.23),.92,0.0)
    try: bg.static_mesh_component.set_material(0,bmat)
    except: pass

    if not sub.save_current_level(): raise RuntimeError("Level save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY landmark="+landmark.get_path_name())
    log("LANDMARK_BOUNDS="+str(landmark.get_bounding_box()))
    log("ACTORS="+str(len(actor_sub.get_all_level_actors())))

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[RATHAUS_FINAL_V3] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
