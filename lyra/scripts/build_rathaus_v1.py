import unreal, os, math, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_playable_v1"
AS="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
GEN="/ShooterMaps/GeneratedGIS/RathausSpandau"
SRC=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1"

def log(s): unreal.log("[RATHAUS_V1] "+str(s))
def material(name,rgb,rough=.9,metal=0.0,two=False):
    p=f"{AS}/{name}"; m=unreal.EditorAssetLibrary.load_asset(p)
    if not m:m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,AS,unreal.Material,unreal.MaterialFactoryNew())
    try:unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
    except:pass
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.set_editor_property("constant",unreal.LinearColor(*rgb,1))
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,160);r.set_editor_property("r",rough)
    unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    me=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,300);me.set_editor_property("r",metal)
    unreal.MaterialEditingLibrary.connect_material_property(me,"",unreal.MaterialProperty.MP_METALLIC)
    m.set_editor_property("two_sided",two);unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m,False)
    return m
def import_obj(name,file):
    task=unreal.AssetImportTask();task.filename=os.path.join(SRC,file);task.destination_path=GEN;task.destination_name=name
    task.automated=True;task.replace_existing=True;task.replace_existing_settings=True;task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.EditorAssetLibrary.load_asset(f"{GEN}/{name}")
    if not mesh:raise RuntimeError("import failed "+file)
    return mesh
def set_complex(mesh):
    bs=mesh.get_editor_property("body_setup")
    if not bs:
        try:unreal.StaticMeshEditorSubsystem().add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
        except:pass
        bs=mesh.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
def spawn(mesh,label,folder,mat,collision):
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator())
    a.set_actor_label(label);a.set_folder_path(folder);c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_material(0,mat)
    c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION)
    return a
def gameplay():
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); ps=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")
    coords=[(-42000,-14000,600),(-40000,-8000,600),(-44000,0,600),(-40000,8000,600),
            (42000,14000,600),(40000,8000,600),(44000,0,600),(40000,-8000,600)]
    for i,(x,y,z) in enumerate(coords):
        yaw=0 if i<4 else 180
        p=a.spawn_actor_from_class(ps,unreal.Vector(x,y,z),unreal.Rotator(0,yaw,0))
        p.set_actor_label(f"Rathaus_PlayerStart_{i+1:02d}");p.set_folder_path("Rathaus_V1/Gameplay")
        p.set_editor_property("is_spatially_loaded",False)
        p.set_editor_property("tags",["SpandauStrike","TeamSide="+("West" if i<4 else "East")])
    nav=a.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,500),unreal.Rotator())
    nav.set_actor_label("Rathaus_NavMeshBounds");nav.set_folder_path("Rathaus_V1/Gameplay");nav.set_actor_scale3d(unreal.Vector(520,520,30))
    try:nav.set_editor_property("is_spatially_loaded",False)
    except:pass
def environment():
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sun=a.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-42,-30,0))
    sun.set_actor_label("Rathaus_Sun");sun.set_folder_path("Rathaus_V1/Lighting");sun.light_component.set_editor_property("intensity",4.0)
    try:sun.light_component.set_editor_property("atmosphere_sun_light",True)
    except:pass
    sky=a.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1000),unreal.Rotator());sky.set_actor_label("Rathaus_SkyLight");sky.set_folder_path("Rathaus_V1/Lighting")
    try:sky.light_component.set_editor_property("real_time_capture",True);sky.light_component.set_editor_property("intensity",1.25)
    except:pass
    fog=a.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(),unreal.Rotator());fog.set_actor_label("Rathaus_Fog");fog.set_folder_path("Rathaus_V1/Lighting")
    try:fog.component.set_editor_property("fog_density",.003);fog.component.set_editor_property("start_distance",3500.)
    except:pass
    try:
        atm=a.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(),unreal.Rotator());atm.set_actor_label("Rathaus_SkyAtmosphere");atm.set_folder_path("Rathaus_V1/Lighting")
    except:pass
def main():
    mats={"Terrain":material("M_Rathaus_Terrain",(0.08,.17,.055),.97),"Building":material("M_Rathaus_Building",(.40,.30,.20),.91,0,True),
          "Road":material("M_Rathaus_Road",(.028,.031,.035),.94),"Water":material("M_Rathaus_Water",(.015,.08,.17),.22,.06)}
    terrain=import_obj("SM_Rathaus_DGM","rathaus_terrain.obj");buildings=import_obj("SM_Rathaus_Buildings","rathaus_buildings.obj")
    roads=import_obj("SM_Rathaus_Roads","rathaus_roads.obj");water=import_obj("SM_Rathaus_Water","rathaus_water.obj")
    set_complex(terrain);set_complex(buildings)
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):unreal.EditorAssetLibrary.delete_asset(MAP)
    if not sub.new_level(MAP,True):raise RuntimeError("new level failed")
    spawn(terrain,"Rathaus_DGM_Terrain","Rathaus_V1/World",mats["Terrain"],True)
    spawn(buildings,"Rathaus_ExactBuildings","Rathaus_V1/Buildings",mats["Building"],True)
    spawn(roads,"Rathaus_Roads","Rathaus_V1/World",mats["Road"],False)
    spawn(water,"Rathaus_Water","Rathaus_V1/World",mats["Water"],False)
    gameplay();environment()
    if not sub.save_current_level():raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY actors="+str(len(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())))
if __name__=="__main__":
    try:main()
    except Exception as e:unreal.log_error("[RATHAUS_V1] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
