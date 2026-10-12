import unreal, os, json, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/rathaus_spandau_fullmap_v1"
DEST="/ShooterMaps/GeneratedGIS/RathausFullMap"
VISIBLE=r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\fullmap_engine\SpandauStrike_Rathaus_FULLMAP_Visible.fbx"
COLLISION=r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\fullmap_engine\SpandauStrike_Rathaus_FULLMAP_Collision.fbx"
SPAWNS=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\safe_spawns.json"

CX,CY=377931.576,5822067.058
OE,ON=377897.8969272321,5822086.91786854
BASELINE=33.45
GROUND=31.0
DX=CX-OE
DY=ON-CY
DZ=BASELINE-GROUND

def log(s):
    unreal.log("[RATHAUS_FULLMAP] "+str(s))

def import_fbx(path,name,materials=False,collision=False):
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
    ui.set_editor_property("import_materials",materials)
    ui.set_editor_property("import_textures",False)
    data=ui.get_editor_property("static_mesh_import_data")
    data.set_editor_property("combine_meshes",True)
    data.set_editor_property("generate_lightmap_u_vs",True)
    data.set_editor_property("auto_generate_collision",collision)
    try:
        data.set_editor_property("remove_degenerates",True)
    except:
        pass
    task.options=ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.EditorAssetLibrary.load_asset(DEST+"/"+name)
    if not mesh:
        raise RuntimeError("FBX import failed: "+path)
    return mesh

def set_complex(mesh):
    bs=mesh.get_editor_property("body_setup")
    if bs:
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)

def spawn_mesh(mesh,label,folder,collision,visible=True):
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0),unreal.Rotator(0,0,0))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    c=a.static_mesh_component
    c.set_static_mesh(mesh)
    c.set_collision_profile_name("BlockAll" if collision else "NoCollision")
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if collision else unreal.CollisionEnabled.NO_COLLISION)
    c.set_editor_property("visible",visible)
    try:
        c.set_editor_property("hidden_in_game",not visible)
    except:
        pass
    try:
        a.set_editor_property("is_spatially_loaded",False)
    except:
        pass
    return a

def gameplay():
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ps_cls=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")

    # Deterministic playtest spawns on the Rathausplatz, in Unreal centimeters.
    starts=[
        ("west",-4000,-7800,650,20),
        ("west",-3000,-7000,650,20),
        ("west",-2000,-6500,650,20),
        ("west",-1000,-6000,650,20),
        ("east", 1000,-6000,650,160),
        ("east", 2000,-6500,650,160),
        ("east", 5000,-8500,650,160),
        ("east", 7000,-10000,650,160),
    ]
    for i,(side,x,y,z,yaw) in enumerate(starts):
        p=actor_sub.spawn_actor_from_class(ps_cls,unreal.Vector(x,y,z),unreal.Rotator(0,yaw,0))
        p.set_actor_label("RathausFull_PlayerStart_%02d"%(i+1))
        p.set_folder_path("RathausFull/Gameplay")
        p.set_editor_property("is_spatially_loaded",False)
        try:
            p.set_editor_property("tags",["SpandauStrike","TeamSide="+side.title(),"PlaytestSpawn"])
        except:
            pass

    nav=actor_sub.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,3000),unreal.Rotator())
    nav.set_actor_label("RathausFull_NavMeshBounds")
    nav.set_folder_path("RathausFull/Gameplay")
    nav.set_actor_scale3d(unreal.Vector(500,500,40))
    try:
        nav.set_editor_property("is_spatially_loaded",False)
    except:
        pass

def spawn_playtest_floor():
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
    if not cube:
        raise RuntimeError("Engine Cube asset missing")
    a=actor_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,400),unreal.Rotator())
    a.set_actor_label("RathausFull_PlaytestGround")
    a.set_folder_path("RathausFull/Collision")
    a.set_actor_scale3d(unreal.Vector(1000,1000,1))
    a.set_editor_property("is_spatially_loaded",False)
    c=a.static_mesh_component
    c.set_static_mesh(cube)
    c.set_collision_profile_name("BlockAll")
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    c.set_editor_property("visible",False)
    try:
        c.set_editor_property("hidden_in_game",True)
        c.set_editor_property("can_ever_affect_navigation",True)
    except:
        pass
    return a

def lighting():
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sun=actor_sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,50000),unreal.Rotator(-38,-25,0))
    sun.set_actor_label("RathausFull_Sun");sun.set_folder_path("RathausFull/Lighting")
    sun.light_component.set_editor_property("intensity",3.8)
    try:
        sun.light_component.set_editor_property("atmosphere_sun_light",True)
    except:
        pass
    sky=actor_sub.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,1000),unreal.Rotator())
    sky.set_actor_label("RathausFull_SkyLight");sky.set_folder_path("RathausFull/Lighting")
    try:
        sky.light_component.set_editor_property("real_time_capture",True)
        sky.light_component.set_editor_property("intensity",1.15)
    except:
        pass
    try:
        atm=actor_sub.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(),unreal.Rotator())
        atm.set_actor_label("RathausFull_SkyAtmosphere");atm.set_folder_path("RathausFull/Lighting")
    except:
        pass
    fog=actor_sub.spawn_actor_from_class(unreal.ExponentialHeightFog,unreal.Vector(),unreal.Rotator())
    fog.set_actor_label("RathausFull_Fog");fog.set_folder_path("RathausFull/Lighting")
    try:
        fog.component.set_editor_property("fog_density",.0025)
        fog.component.set_editor_property("start_distance",5000.0)
    except:
        pass

def main():
    if not os.path.exists(VISIBLE): raise RuntimeError("missing visible FBX")
    if not os.path.exists(COLLISION): raise RuntimeError("missing collision FBX")

    visible=import_fbx(VISIBLE,"SM_Rathaus_FULLMAP_Visible",True,False)
    collision=import_fbx(COLLISION,"SM_Rathaus_FULLMAP_Collision",False,False)
    set_complex(collision)

    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        unreal.EditorAssetLibrary.delete_asset(MAP)
    if not lvl.new_level(MAP,True):
        raise RuntimeError("new level failed")

    va=spawn_mesh(visible,"RathausFull_Visible","RathausFull/World",False,True)
    ca=spawn_mesh(collision,"RathausFull_Collision","RathausFull/Collision",True,False)
    floor=spawn_playtest_floor()

    gameplay()
    lighting()

    if not lvl.save_current_level():
        raise RuntimeError("level save failed")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)

    log("VISIBLE_BOUNDS="+str(visible.get_bounding_box()))
    log("COLLISION_BOUNDS="+str(collision.get_bounding_box()))
    log("ACTORS="+str(len(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())))
    log("READY map="+MAP)

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        unreal.log_error("[RATHAUS_FULLMAP] FAILED "+str(e))
        unreal.log_error(traceback.format_exc())
        raise



