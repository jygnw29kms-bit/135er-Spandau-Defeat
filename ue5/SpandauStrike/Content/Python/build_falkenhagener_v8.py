import unreal, math, os, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v8"
AS="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
GEN="/ShooterMaps/GeneratedGIS/FalkenhagenerFeld"
GIS=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS"

BUILDINGS={
 "Residential": os.path.join(GIS,"FalkenhagenerFeld_Buildings_Residential_DGM.obj"),
 "Public": os.path.join(GIS,"FalkenhagenerFeld_Buildings_Public_DGM.obj"),
 "Industrial": os.path.join(GIS,"FalkenhagenerFeld_Buildings_Industrial_DGM.obj"),
 "Aux": os.path.join(GIS,"FalkenhagenerFeld_Buildings_Aux_DGM.obj")
}

def log(s): unreal.log("[SS_V8] "+str(s))

def material(name,rgb,rough=0.9,metal=0.0,two=False):
    p=f"{AS}/{name}"
    m=unreal.EditorAssetLibrary.load_asset(p)
    if not m:
        m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,AS,unreal.Material,unreal.MaterialFactoryNew())
    try: unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
    except: pass
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.set_editor_property("constant",unreal.LinearColor(*rgb,1))
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,160)
    r.set_editor_property("r",rough)
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    me=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,300)
    me.set_editor_property("r",metal)
    unreal.MaterialEditingLibrary.connect_material_property(me,"",unreal.MaterialProperty.MP_METALLIC)
    m.set_editor_property("two_sided",two)
    try: m.set_editor_property("used_with_nanite",True)
    except: pass
    unreal.MaterialEditingLibrary.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m,False)
    return m
def import_obj(cat,filename):
    if not os.path.exists(filename): raise RuntimeError("missing "+filename)
    name="SM_Falkenhagener_Buildings_"+cat+"_DGM"
    task=unreal.AssetImportTask()
    task.filename=filename
    task.destination_path=GEN
    task.destination_name=name
    task.automated=True
    task.replace_existing=True
    task.replace_existing_settings=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.EditorAssetLibrary.load_asset(f"{GEN}/{name}")
    if not mesh: raise RuntimeError("import failed "+cat)
    bs=mesh.get_editor_property("body_setup")
    if not bs:
        try: unreal.StaticMeshEditorSubsystem().add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
        except: pass
        bs=mesh.get_editor_property("body_setup")
    if bs: bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    try: mesh.set_editor_property("nanite_settings",mesh.get_editor_property("nanite_settings"))
    except: pass
    unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
    log("imported "+cat+" "+mesh.get_path_name())
    return mesh

def set_complex(mesh):
    bs=mesh.get_editor_property("body_setup")
    if not bs:
        try: unreal.StaticMeshEditorSubsystem().add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
        except: pass
        bs=mesh.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)

def spawn_mesh(mesh,label,folder,mat,collision):
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator())
    a.set_actor_label(label); a.set_folder_path(folder)
    c=a.static_mesh_component; c.set_static_mesh(mesh); c.set_material(0,mat)
    c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION)
    return a
def add_gameplay():
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ps=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")
    coords=[(-65000,15000,441),(-60000,15000,464),(-70000,15000,449),(-65000,20000,443),
            (55000,45000,495),(60000,50000,485),(65000,55000,532),(60000,45000,506)]
    for i,(x,y,z) in enumerate(coords):
        yaw=math.degrees(math.atan2(-y,-x))
        a=actor_sub.spawn_actor_from_class(ps,unreal.Vector(x,y,z),unreal.Rotator(0,0,yaw))
        a.set_actor_label(f"SS_LyraPlayerStart_{i+1:02d}")
        a.set_folder_path("SpandauStrike_V8/Gameplay")
        a.set_editor_property("is_spatially_loaded",False)
        side="West" if i<4 else "East"
        a.set_editor_property("tags",["SpandauStrike",f"TeamSide={side}"])
    nav=actor_sub.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,500),unreal.Rotator())
    nav.set_actor_label("SS_NavMeshBounds"); nav.set_folder_path("SpandauStrike_V8/Gameplay")
    nav.set_actor_scale3d(unreal.Vector(950,950,35))
    try: nav.set_editor_property("is_spatially_loaded",False)
    except: pass

def add_environment():
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sun=a.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-42,-28,0))
    sun.set_actor_label("Sun"); sun.set_folder_path("SpandauStrike_V8/Lighting")
    sun.light_component.set_editor_property("intensity",2.25)
    try: sun.light_component.set_editor_property("atmosphere_sun_light",True)
    except: pass
    sky=a.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1000),unreal.Rotator())
    sky.set_actor_label("SkyLight"); sky.set_folder_path("SpandauStrike_V8/Lighting")
    try: sky.light_component.set_editor_property("real_time_capture",True)
    except: pass
    fog=a.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(),unreal.Rotator())
    fog.set_actor_label("Fog"); fog.set_folder_path("SpandauStrike_V8/Lighting")
    try:
        fc=fog.component
        fc.set_editor_property("fog_density",0.006)
        fc.set_editor_property("fog_height_falloff",0.18)
        fc.set_editor_property("start_distance",2500.0)
    except: pass
    try:
        atm=a.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(),unreal.Rotator())
        atm.set_actor_label("SkyAtmosphere"); atm.set_folder_path("SpandauStrike_V8/Lighting")
    except: pass
def main():
    # V7 may be running; caller stops runtime before this script.
    mats={
      "Residential":material("M_V8_Residential",(0.34,0.27,0.19),0.92,0.0,True),
      "Public":material("M_V8_Public",(0.38,0.18,0.12),0.90,0.0,True),
      "Industrial":material("M_V8_Industrial",(0.18,0.22,0.24),0.84,0.02,True),
      "Aux":material("M_V8_Aux",(0.20,0.18,0.15),0.94,0.0,True),
      "Terrain":material("M_V8_Terrain",(0.075,0.16,0.045),0.97),
      "Road":material("M_V8_Road",(0.025,0.028,0.032),0.93),
      "Water":material("M_V8_Water",(0.015,0.08,0.16),0.20,0.08),
      "Trunk":material("M_V8_Trunk",(0.11,0.05,0.018),0.96),
      "Broad":material("M_V8_Broadleaf",(0.035,0.13,0.025),0.92),
      "Conif":material("M_V8_Conifer",(0.022,0.085,0.018),0.95)
    }
    bmeshes={k:import_obj(k,v) for k,v in BUILDINGS.items()}
    terrain=unreal.EditorAssetLibrary.load_asset(f"{GEN}/SM_Falkenhagener_DGM10m")
    roads=unreal.EditorAssetLibrary.load_asset(f"{GEN}/SM_Falkenhagener_Roads_DGM")
    water=unreal.EditorAssetLibrary.load_asset(f"{GEN}/SM_Falkenhagener_Water_DGM")
    trunk=unreal.EditorAssetLibrary.load_asset(f"{GEN}/SM_SS_TreeTrunks")
    broad=unreal.EditorAssetLibrary.load_asset(f"{GEN}/SM_SS_TreeBroadleaf")
    conif=unreal.EditorAssetLibrary.load_asset(f"{GEN}/SM_SS_TreeConifer")
    for obj,name in [(terrain,"terrain"),(roads,"roads"),(water,"water"),(trunk,"trunk"),(broad,"broad"),(conif,"conif")]:
        if not obj: raise RuntimeError("missing "+name)
    set_complex(terrain)

    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(MAP): unreal.EditorAssetLibrary.delete_asset(MAP)
    if not sub.new_level(MAP,True): raise RuntimeError("new level failed")

    for cat,mesh in bmeshes.items():
        spawn_mesh(mesh,"SS_Buildings_"+cat,"SpandauStrike_V8/Buildings",mats[cat],True)
    spawn_mesh(terrain,"SS_DGM_Terrain","SpandauStrike_V8/World",mats["Terrain"],True)
    spawn_mesh(roads,"SS_Roads","SpandauStrike_V8/World",mats["Road"],False)
    spawn_mesh(water,"SS_Water","SpandauStrike_V8/World",mats["Water"],False)
    spawn_mesh(trunk,"SS_TreeTrunks","SpandauStrike_V8/Vegetation",mats["Trunk"],False)
    spawn_mesh(broad,"SS_TreeBroadleaf","SpandauStrike_V8/Vegetation",mats["Broad"],False)
    spawn_mesh(conif,"SS_TreeConifer","SpandauStrike_V8/Vegetation",mats["Conif"],False)
    add_gameplay(); add_environment()
    world=unreal.EditorLevelLibrary.get_editor_world()
    try: unreal.SystemLibrary.execute_console_command(world,"RebuildNavigation")
    except: pass
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY V8 exact categorized buildings + DGM + OSM + trees")
    log("actors="+str(len(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())))

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[SS_V8] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
