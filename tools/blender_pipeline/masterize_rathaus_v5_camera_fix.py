import bpy, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BLEND=ROOT/"RathausSpandau_MASTER_Aligned_v5.blend"
PNG=ROOT/"RathausSpandau_MASTER_Aligned_v5_preview.png"
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
sc=bpy.context.scene
AX=math.radians(47.5);CA,SA=math.cos(AX),math.sin(AX)
def xy(u,v): return (u*CA-v*SA,u*SA+v*CA)

# Darker historic materials / lower exposure
for name,col,rough in [
    ("M_MASTER_Stone",(0.27,0.23,0.18,1),.64),
    ("M_MASTER_StoneTrim",(0.42,0.36,0.28,1),.58),
    ("M_Stone",(0.30,0.26,0.20,1),.66),
    ("M_Trim",(0.46,0.40,0.32,1),.60),
    ("M_RedTile",(0.30,0.055,0.028,1),.68),
]:
    m=bpy.data.materials.get(name)
    if m and m.use_nodes:
        bs=m.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value=col
        bs.inputs["Roughness"].default_value=rough

# Master-like low plaza camera
cu,cv=-10,-160
cx,cy=xy(cu,cv)
tx,ty=xy(0,-22)
cam=sc.camera
cam.location=(cx,cy,7.8)
cam.data.lens=30
cam.rotation_euler=(Vector((tx,ty,27))-cam.location).to_track_quat('-Z','Y').to_euler()

# balance sky / sun
world=sc.world
if world and world.use_nodes:
    for n in world.node_tree.nodes:
        if n.type=="BACKGROUND":
            n.inputs["Strength"].default_value=.38
        if n.type=="TEX_SKY":
            n.sun_elevation=math.radians(18)
            n.sun_rotation=math.radians(125)
            n.dust_density=2.8
for o in [x for x in sc.objects if x.type=='LIGHT' and x.data.type=='SUN']:
    o.data.energy=3.0
    o.data.angle=math.radians(4.5)

sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=-.55
sc.render.filepath=str(PNG)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)
print("V5_CAMERA_FIXED",PNG)
