import unreal, traceback

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
FOLDER="SpandauStrike_Gameplay"
EXP="/ShooterCore/Experiences/B_LyraShooterGame_ControlPoints.B_LyraShooterGame_ControlPoints_C"
CP="/ShooterCore/Blueprint/B_ControlPointVolume.B_ControlPointVolume_C"

def log(s): unreal.log("[SS_PLAYABLE] "+s)

def spawn(cls, loc, rot=None, label=None, scale=None):
    sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=sub.spawn_actor_from_class(cls, unreal.Vector(*loc), rot or unreal.Rotator(0,0,0))
    if label: a.set_actor_label(label)
    a.set_folder_path(FOLDER)
    if scale: a.set_actor_scale3d(unreal.Vector(*scale))
    return a

lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not lvl.load_level(MAP): raise RuntimeError("Could not load "+MAP)
world=unreal.EditorLevelLibrary.get_editor_world()
ws=world.get_world_settings()
log("WorldSettings="+ws.get_class().get_name())
if ws.get_class().get_name() != "SpandauStrikeWorldSettings":
    raise RuntimeError("Unexpected WorldSettings: "+ws.get_class().get_name())
experience = str(ws.get_editor_property("default_gameplay_experience"))
log("Experience="+experience)
if "B_LyraShooterGame_ControlPoints" not in experience:
    raise RuntimeError("Control Points experience not configured")

# Remove only our own previous gameplay layer for idempotent reruns.
actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actor_sub.get_all_level_actors():
    try:
        if str(a.get_folder_path()).startswith(FOLDER):
            actor_sub.destroy_actor(a)
    except Exception:
        pass

cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
mat=unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/WorldGridMaterial.WorldGridMaterial")
ground=spawn(unreal.StaticMeshActor,(0,0,-50),label="SS_Ground_1800m",scale=(1800,1800,1))
ground.static_mesh_component.set_static_mesh(cube)
if mat: ground.static_mesh_component.set_material(0,mat)
ground.static_mesh_component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
ground.set_editor_property("tags",["SpandauStrike","GameplayGround","GISReference"])
log("Ground created")

ps_cls=unreal.load_class(None,"/Script/LyraGame.LyraPlayerStart")
if not ps_cls: raise RuntimeError("LyraPlayerStart class missing")
starts=[
 (-76000,-24000,160),(-76000,-8000,160),(-76000,8000,160),(-76000,24000,160),
 (76000,-24000,160),(76000,-8000,160),(76000,8000,160),(76000,24000,160)]
for i,p in enumerate(starts,1):
    a=spawn(ps_cls,p,label="SS_LyraPlayerStart_%02d"%i)
    a.set_editor_property("tags",["SpandauStrike","TeamSide="+("West" if p[0]<0 else "East")])
log("PlayerStarts=8")

nav=spawn(unreal.NavMeshBoundsVolume,(0,0,1000),label="SS_NavMeshBounds",scale=(900,900,20))
log("NavMesh bounds created")

# Lighting for editor/game rendering.
sun=spawn(unreal.DirectionalLight,(0,0,25000),unreal.Rotator(-45,-35,0),label="SS_Sun")
try:
    sun.directional_light_component.set_editor_property("intensity",8.0)
except Exception: pass
sky=spawn(unreal.SkyLight,(0,0,10000),label="SS_SkyLight")
try:
    sky.light_component.set_editor_property("intensity",1.0)
except Exception: pass
fog=spawn(unreal.ExponentialHeightFog,(0,0,0),label="SS_HeightFog")

cp_cls=unreal.load_class(None,CP)
if not cp_cls: raise RuntimeError("Control point class missing: "+CP)
for name,pos in [
    ("A",(-45000,-35000,100)),
    ("B",(0,0,100)),
    ("C",(45000,35000,100))]:
    a=spawn(cp_cls,pos,label="SS_ControlPoint_"+name,scale=(4,4,2))
    a.set_editor_property("tags",["SpandauStrike","ControlPoint="+name])
log("ControlPoints=A,B,C")

if not lvl.save_current_level():
    raise RuntimeError("save_current_level returned false")
log("Saved playable map "+MAP)
