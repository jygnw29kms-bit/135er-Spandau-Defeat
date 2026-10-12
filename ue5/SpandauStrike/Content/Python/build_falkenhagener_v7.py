import unreal, math, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld_playable_v7"
AS="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
GEN="/ShooterMaps/GeneratedGIS/FalkenhagenerFeld"
EXP="/ShooterCore/Experiences/B_LyraShooterGame_ControlPoints.B_LyraShooterGame_ControlPoints_C"

def log(s): unreal.log("[SS_V7] "+str(s))

def mat(name,rgb,rough=0.9,metal=0.0):
    p=f"{AS}/{name}"
    m=unreal.EditorAssetLibrary.load_asset(p)
    if not m:
        m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,AS,unreal.Material,unreal.MaterialFactoryNew())
    try: unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
    except: pass
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-250,0)
    c.set_editor_property("constant",unreal.LinearColor(*rgb,1))
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-250,150)
    r.set_editor_property("r",rough)
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    me=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-250,300)
    me.set_editor_property("r",metal)
    unreal.MaterialEditingLibrary.connect_material_property(me,"",unreal.MaterialProperty.MP_METALLIC)
    unreal.MaterialEditingLibrary.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m,False)
    return m

def spawn_mesh(asset,label,folder,material,collision):
    mesh=unreal.EditorAssetLibrary.load_asset(asset)
    if not mesh: raise RuntimeError("missing "+asset)
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator())
    a.set_actor_label(label); a.set_folder_path(folder)
    c=a.static_mesh_component; c.set_static_mesh(mesh); c.set_material(0,material)
    c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION)
    return a
def add_gameplay():
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ps=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")
    coords=[(-65000,15000,441),(-60000,15000,464),(-70000,15000,449),(-65000,20000,443),(55000,45000,495),(60000,50000,485),(65000,55000,532),(60000,45000,506)]
    for i,(x,y,z) in enumerate(coords):
        yaw=math.degrees(math.atan2(-y,-x))
        a=actor_sub.spawn_actor_from_class(ps,unreal.Vector(x,y,z),unreal.Rotator(0,0,yaw))
        a.set_actor_label(f"SS_LyraPlayerStart_{i+1:02d}"); a.set_folder_path("SpandauStrike_V7/Gameplay")
        a.set_editor_property("is_spatially_loaded",False)
        side="West" if i<4 else "East"
        a.set_editor_property("tags",["SpandauStrike",f"TeamSide={side}"])
    nav=actor_sub.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,300),unreal.Rotator())
    nav.set_actor_label("SS_NavMeshBounds")
    nav.set_actor_scale3d(unreal.Vector(18,18,3))
    nav.set_folder_path("SpandauStrike_V7/Gameplay")
    sun=actor_sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-40,-25,0))
    sun.set_actor_label("Sun"); sun.set_folder_path("SpandauStrike_V7/Lighting")
    sun.light_component.set_editor_property("intensity",3.2)
    sky=actor_sub.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1000),unreal.Rotator())
    sky.set_actor_label("SkyLight"); sky.set_folder_path("SpandauStrike_V7/Lighting")
    try: sky.light_component.set_editor_property("real_time_capture",True)
    except: pass
    fog=actor_sub.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(),unreal.Rotator())
    fog.set_actor_label("Fog"); fog.set_folder_path("SpandauStrike_V7/Lighting")
    try:
        atm=actor_sub.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(),unreal.Rotator())
        atm.set_actor_label("SkyAtmosphere"); atm.set_folder_path("SpandauStrike_V7/Lighting")
    except: pass

def main():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        unreal.EditorAssetLibrary.delete_asset(MAP)
    if not sub.new_level(MAP,True): raise RuntimeError("new level failed")
    w=unreal.EditorLevelLibrary.get_editor_world()
    ws=w.get_world_settings()
    try: log("worldsettings=%s experience=%s"%(ws.get_class().get_path_name(),ws.get_editor_property("default_gameplay_experience")))
    except: pass
    terrain=mat("M_Falkenhagener_Terrain_V7",(0.10,0.20,0.07),0.96)
    building=mat("M_Falkenhagener_Buildings_V7",(0.32,0.29,0.25),0.92)
    building.set_editor_property("two_sided",True)
    unreal.MaterialEditingLibrary.recompile_material(building)
    unreal.EditorAssetLibrary.save_loaded_asset(building,False)
    road=mat("M_Falkenhagener_Road_V7",(0.035,0.04,0.045),0.94)
    water=mat("M_Falkenhagener_Water_V7",(0.02,0.12,0.22),0.28,0.05)
    trunk=mat("M_Falkenhagener_TreeTrunk_V7",(0.13,0.065,0.025),0.96)
    broad=mat("M_Falkenhagener_TreeBroadleaf_V7",(0.055,0.18,0.035),0.91)
    conif=mat("M_Falkenhagener_TreeConifer_V7",(0.035,0.12,0.028),0.94)
    spawn_mesh(f"{GEN}/SM_Falkenhagener_Buildings_OBB","SS_ExactBuildings","SpandauStrike_V7/World",building,True)
    spawn_mesh(f"{GEN}/SM_Falkenhagener_DGM10m","SS_DGM_Terrain","SpandauStrike_V7/World",terrain,True)
    spawn_mesh(f"{GEN}/SM_Falkenhagener_Roads_DGM","SS_Roads","SpandauStrike_V7/World",road,False)
    spawn_mesh(f"{GEN}/SM_Falkenhagener_Water_DGM","SS_Water","SpandauStrike_V7/World",water,False)
    spawn_mesh(f"{GEN}/SM_SS_TreeTrunks","SS_TreeTrunks","SpandauStrike_V7/Vegetation",trunk,False)
    spawn_mesh(f"{GEN}/SM_SS_TreeBroadleaf","SS_TreeBroadleaf","SpandauStrike_V7/Vegetation",broad,False)
    spawn_mesh(f"{GEN}/SM_SS_TreeConifer","SS_TreeConifer","SpandauStrike_V7/Vegetation",conif,False)
    add_gameplay()
    if not sub.save_current_level(): raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY combined_world + gameplay")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[SS_V7] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise



