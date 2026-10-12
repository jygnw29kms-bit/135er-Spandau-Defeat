# -*- coding: utf-8 -*-
import unreal, os, traceback

SRC="/Game/Maps/BerlinSpandau/falkenhagener_feld_prod_v2"
DST="/Game/Maps/BerlinSpandau/falkenhagener_feld_prod_v3"
DEST="/Game/SpandauStrikeGIS/Combined"
BASE=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\DGM1_FalkenhagenerFeld"
BLDG_OBJ=os.path.join(BASE,"falkenhagener_buildings_exact.obj")
ROAD_OBJ=os.path.join(BASE,"OSM_Combined","falkenhagener_roads_dgm.obj")
WATER_OBJ=os.path.join(BASE,"OSM_Combined","falkenhagener_water_dgm.obj")
TERRAIN="/Game/SpandauStrikeGIS/Terrain/falkenhagener_dgm_257"
MAT_T="/Game/SpandauStrikeGIS/Materials/M_SS_Terrain"
MAT_B="/Game/SpandauStrikeGIS/Materials/M_SS_Building"
MAT_R="/Game/SpandauStrikeGIS/Materials/M_SS_Road"
MAT_W="/Game/SpandauStrikeGIS/Materials/M_SS_Water"
ROOT="SpandauStrike_PROD_V3"

def log(s): unreal.log("[SS_V3] "+str(s))
def import_obj(src,name):
    if not os.path.isfile(src): raise RuntimeError("missing "+src)
    task=unreal.AssetImportTask()
    task.filename=src
    task.destination_path=DEST
    task.destination_name=name
    task.automated=True
    task.replace_existing=True
    task.replace_existing_settings=True
    task.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    p=list(task.imported_object_paths)
    if not p: raise RuntimeError("import failed "+name)
    m=unreal.EditorAssetLibrary.load_asset(p[0])
    if not m: raise RuntimeError("load failed "+name)
    log("imported "+m.get_path_name())
    return m

def set_complex(mesh):
    bs=mesh.get_editor_property("body_setup")
    if not bs:
        unreal.StaticMeshEditorSubsystem().add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
        bs=mesh.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    mesh.modify()
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
def collect_spawns():
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(SRC): raise RuntimeError("cannot load prod_v2")
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    starts=[a for a in actors if a.get_class().get_name()=="LyraPlayerStart"]
    starts.sort(key=lambda a:a.get_actor_label())
    data=[]
    for a in starts:
        data.append((a.get_actor_label(),a.get_actor_location(),a.get_actor_rotation()))
    log("collected spawns="+str(len(data)))
    return data

def spawn_static(mesh,mat,label,folder,collision):
    a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator())
    a.set_actor_label(label)
    a.set_folder_path(folder)
    c=a.static_mesh_component
    c.set_static_mesh(mesh)
    if mat: c.set_material(0,mat)
    if collision:
        c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        c.set_collision_profile_name("BlockAll")
    else:
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_collision_profile_name("NoCollision")
    return a
def build_world(spawns,bldg,roads,water):
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(DST):
        unreal.EditorAssetLibrary.delete_asset(DST)
    if not sub.new_level(DST,True):
        raise RuntimeError("new_level failed "+DST)

    terrain=unreal.EditorAssetLibrary.load_asset(TERRAIN)
    mt=unreal.EditorAssetLibrary.load_asset(MAT_T)
    mb=unreal.EditorAssetLibrary.load_asset(MAT_B)
    mr=unreal.EditorAssetLibrary.load_asset(MAT_R)
    mw=unreal.EditorAssetLibrary.load_asset(MAT_W)
    if not all((terrain,mt,mb,mr,mw)): raise RuntimeError("required assets missing")

    spawn_static(terrain,mt,"DGM1_Terrain_Real",ROOT+"/Terrain",True)
    spawn_static(bldg,mb,"SS_ExactBuildings",ROOT+"/Buildings",True)
    spawn_static(roads,mr,"SS_GIS_Roads_DGM",ROOT+"/Roads",False)
    spawn_static(water,mw,"SS_GIS_Water_DGM",ROOT+"/Water",False)
    sun=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-35,-25,0))
    sun.set_actor_label("Sun"); sun.set_folder_path(ROOT+"/Environment")
    try: sun.light_component.set_editor_property("intensity",5.0)
    except: pass
    sky=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.SkyLight,unreal.Vector(0,0,2000),unreal.Rotator())
    sky.set_actor_label("SkyLight"); sky.set_folder_path(ROOT+"/Environment")
    try:
        atm=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
            unreal.SkyAtmosphere,unreal.Vector(),unreal.Rotator())
        atm.set_actor_label("SkyAtmosphere"); atm.set_folder_path(ROOT+"/Environment")
    except: pass
    try:
        fog=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
            unreal.ExponentialHeightFog,unreal.Vector(),unreal.Rotator())
        fog.set_actor_label("HeightFog"); fog.set_folder_path(ROOT+"/Environment")
    except: pass
    cls=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart") or unreal.PlayerStart
    for i,(label,loc,rot) in enumerate(spawns):
        a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(cls,loc,rot)
        a.set_actor_label(label if label else "SS_PlayerStart_%02d"%(i+1))
        a.set_folder_path(ROOT+"/Gameplay/PlayerStarts")
    nav=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.NavMeshBoundsVolume,unreal.Vector(0,0,10000),unreal.Rotator())
    nav.set_actor_label("SS_NavMeshBounds"); nav.set_folder_path(ROOT+"/Gameplay")
    nav.set_actor_scale3d(unreal.Vector(1000,1000,250))
    if not sub.save_current_level(): raise RuntimeError("save level failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    log("V3_LEVEL_READY")
def main():
    spawns=collect_spawns()
    if len(spawns)<8: raise RuntimeError("too few source spawns")
    bldg=import_obj(BLDG_OBJ,"SM_Falkenhagener_ExactBuildings_V3")
    roads=import_obj(ROAD_OBJ,"SM_Falkenhagener_Roads_DGM_V3")
    water=import_obj(WATER_OBJ,"SM_Falkenhagener_Water_DGM_V3")
    terrain=unreal.EditorAssetLibrary.load_asset(TERRAIN)
    set_complex(terrain)
    set_complex(bldg)
    build_world(spawns,bldg,roads,water)
    log("READY actors_expected~25")

if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[SS_V3] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise
