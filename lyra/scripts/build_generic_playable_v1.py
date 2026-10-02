import unreal, os, json, sys, traceback
from pathlib import Path

MAPID=sys.argv[1] if len(sys.argv)>1 else "staaken"
ROOT=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike")
SRC=ROOT/"Saved"/"GIS"/f"{MAPID}_v1"
CFG=json.loads((SRC/"gameplay_points.json").read_text(encoding="utf-8"))
SAFE="".join(c for c in MAPID.title() if c.isalnum())
MAP=f"/ShooterMaps/Maps/SpandauStrikeGIS/{MAPID}_playable_v1"
AS="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
GEN=f"/ShooterMaps/GeneratedGIS/{SAFE}"
CPCLASS="/ShooterCore/Blueprint/B_ControlPointVolume.B_ControlPointVolume_C"

def log(s): unreal.log(f"[GENERIC_V1:{MAPID}] "+str(s))
def material(name,rgb,rough=.9,metal=0.0,two=False):
    p=f"{AS}/{name}"; m=unreal.EditorAssetLibrary.load_asset(p)
    if not m:m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,AS,unreal.Material,unreal.MaterialFactoryNew())
    try:unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
    except:pass
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.set_editor_property("constant",unreal.LinearColor(*rgb,1))
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    r=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,160)
    r.set_editor_property("r",rough);unreal.MaterialEditingLibrary.connect_material_property(r,"",unreal.MaterialProperty.MP_ROUGHNESS)
    me=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,300)
    me.set_editor_property("r",metal);unreal.MaterialEditingLibrary.connect_material_property(me,"",unreal.MaterialProperty.MP_METALLIC)
    m.set_editor_property("two_sided",two)
    try:m.set_editor_property("used_with_nanite",True)
    except:pass
    unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m,False)
    return m

def import_obj(name,file):
    task=unreal.AssetImportTask();task.filename=str(SRC/file);task.destination_path=GEN;task.destination_name=name
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
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator())
    a.set_actor_label(label);a.set_folder_path(folder)
    c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_material(0,mat)
    c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION)
    return a

def gameplay():
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ps=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")
    starts=CFG["west"]+CFG["east"]
    if len(starts)<8:raise RuntimeError("not enough safe starts")
    for i,xyz in enumerate(starts[:8]):
        yaw=0 if i<4 else 180
        p=sub.spawn_actor_from_class(ps,unreal.Vector(*xyz),unreal.Rotator(0,yaw,0))
        p.set_actor_label(f"{SAFE}_PlayerStart_{i+1:02d}");p.set_folder_path(f"{SAFE}_V1/Gameplay")
        try:p.set_editor_property("is_spatially_loaded",False)
        except:pass
        p.set_editor_property("tags",["SpandauStrike","TeamSide="+("West" if i<4 else "East")])
    cls=unreal.load_class(None,CPCLASS)
    if not cls:raise RuntimeError("control point class missing")
    for i,xyz in enumerate(CFG["control_points"][:3]):
        a=sub.spawn_actor_from_class(cls,unreal.Vector(*xyz),unreal.Rotator())
        a.set_actor_label(f"{SAFE}_ControlPoint_{chr(65+i)}");a.set_folder_path(f"{SAFE}_V1/Gameplay/ControlPoints")
        try:a.set_editor_property("is_spatially_loaded",False);a.set_actor_scale3d(unreal.Vector(1.35,1.35,1.0))
        except:pass
    nav=sub.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,500),unreal.Rotator())
    nav.set_actor_label(f"{SAFE}_NavMeshBounds");nav.set_folder_path(f"{SAFE}_V1/Gameplay")
    nav.set_actor_scale3d(unreal.Vector(680,680,35))
    try:nav.set_editor_property("is_spatially_loaded",False)
    except:pass

def environment():
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sun=sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-42,-30,0))
    sun.set_actor_label(f"{SAFE}_Sun");sun.set_folder_path(f"{SAFE}_V1/Lighting");sun.light_component.set_editor_property("intensity",1.4)
    try:sun.light_component.set_editor_property("atmosphere_sun_light",True)
    except:pass
    sky=sub.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1000),unreal.Rotator())
    sky.set_actor_label(f"{SAFE}_SkyLight");sky.set_folder_path(f"{SAFE}_V1/Lighting")
    try:sky.light_component.set_editor_property("real_time_capture",True);sky.light_component.set_editor_property("intensity",0.65)
    except:pass
    fog=sub.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(),unreal.Rotator())
    fog.set_actor_label(f"{SAFE}_Fog");fog.set_folder_path(f"{SAFE}_V1/Lighting")
    try:fog.component.set_editor_property("fog_density",.002);fog.component.set_editor_property("fog_height_falloff",.22);fog.component.set_editor_property("start_distance",3500.)
    except:pass
    try:
        atm=sub.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(),unreal.Rotator());atm.set_actor_label(f"{SAFE}_SkyAtmosphere");atm.set_folder_path(f"{SAFE}_V1/Lighting")
    except:pass
    pp=sub.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(),unreal.Rotator())
    pp.set_actor_label(f"{SAFE}_DaylightPostProcess");pp.set_folder_path(f"{SAFE}_V1/Lighting");pp.set_editor_property("unbound",True)
    st=pp.get_editor_property("settings")
    try:st.set_editor_property("auto_exposure_bias",1.0);st.set_editor_property("override_auto_exposure_bias",True);pp.set_editor_property("settings",st)
    except:pass

def main():
    mats={"Terrain":material(f"M_{SAFE}_Terrain",(0.08,.17,.055),.97),
          "Building":material(f"M_{SAFE}_Building",(.40,.30,.20),.91,0,True),
          "Road":material(f"M_{SAFE}_Road",(.028,.031,.035),.94),
          "Water":material(f"M_{SAFE}_Water",(.015,.08,.17),.22,.06)}
    terrain=import_obj(f"SM_{SAFE}_DGM",f"{MAPID}_terrain.obj")
    buildings=import_obj(f"SM_{SAFE}_Buildings",f"{MAPID}_buildings.obj")
    roads=import_obj(f"SM_{SAFE}_Roads",f"{MAPID}_roads.obj")
    water=import_obj(f"SM_{SAFE}_Water",f"{MAPID}_water.obj")
    set_complex(terrain);set_complex(buildings)
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):unreal.EditorAssetLibrary.delete_asset(MAP)
    if not lvl.new_level(MAP,True):raise RuntimeError("new level failed")
    spawn(terrain,f"{SAFE}_DGM_Terrain",f"{SAFE}_V1/World",mats["Terrain"],True)
    spawn(buildings,f"{SAFE}_ExactBuildings",f"{SAFE}_V1/Buildings",mats["Building"],True)
    spawn(roads,f"{SAFE}_Roads",f"{SAFE}_V1/World",mats["Road"],False)
    spawn(water,f"{SAFE}_Water",f"{SAFE}_V1/World",mats["Water"],False)
    gameplay();environment()
    if not lvl.save_current_level():raise RuntimeError("save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("READY actors="+str(len(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())))

if __name__=="__main__":
    try:main()
    except Exception as e:
        unreal.log_error(f"[GENERIC_V1:{MAPID}] FAILED "+str(e));unreal.log_error(traceback.format_exc());raise
