from pathlib import Path
import re
p=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Content\Python\build_rathaus_fullmap_v1.py")
t=p.read_text(encoding="utf-8-sig")

new_gameplay=r'''def gameplay():
    actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ps_cls=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")

    # Deterministic playtest spawns on the Rathausplatz, in Unreal centimeters.
    starts=[
        ("west",-9000,-11500,350,20),
        ("west",-7000,-10000,350,20),
        ("west",-5000,-8500,350,20),
        ("west",-3000,-7000,350,20),
        ("east", 9000,-11500,350,160),
        ("east", 7000,-10000,350,160),
        ("east", 5000,-8500,350,160),
        ("east", 3000,-7000,350,160),
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
    a=actor_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-50),unreal.Rotator())
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

def lighting():'''
t2=re.sub(r'def gameplay\(\):.*?\ndef lighting\(\):',new_gameplay,t,flags=re.S)
if t2==t:
    raise SystemExit("gameplay replacement failed")
t2=t2.replace('    ca=spawn_mesh(collision,"RathausFull_Collision","RathausFull/Collision",True,False)\n\n    gameplay()',
'''    ca=spawn_mesh(collision,"RathausFull_Collision","RathausFull/Collision",True,False)
    floor=spawn_playtest_floor()

    gameplay()''')
p.write_text(t2,encoding="utf-8")
print("PATCHED",p)
