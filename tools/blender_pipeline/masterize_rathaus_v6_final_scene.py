import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BASE=ROOT/"RathausSpandau_MASTER_Aligned_v5.blend"
OUT=ROOT/"RathausSpandau_MASTER_Aligned_v6.blend"
PNG=ROOT/"RathausSpandau_MASTER_Aligned_v6_preview.png"
META=ROOT/"RathausSpandau_MASTER_Aligned_v6.json"
bpy.ops.wm.open_mainfile(filepath=str(BASE))
sc=bpy.context.scene

AX=math.radians(47.5);CA,SA=math.cos(AX),math.sin(AX)
def xy(u,v):return (u*CA-v*SA,u*SA+v*CA)
MASTER=bpy.data.collections.get("MASTER_Optical_SetDressing")

def mat(name,color,rough=.5,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m
DARK=mat("M_MASTER_Dark",(0.025,0.027,0.03),.38,.35)
CONC=mat("M_MASTER_Concrete",(0.28,0.27,0.25),.72)
RED=mat("M_MASTER_Red",(0.48,0.025,0.018),.40)
YELLOW=mat("M_MASTER_TramYellow",(0.90,0.52,0.02),.35)
GLASS=mat("M_MASTER_Glass",(0.018,0.045,0.065),.12,.08)
STONE=mat("M_MASTER_Stone",(0.27,0.23,0.18),.62)
WHITE=mat("M_MASTER_White",(0.75,0.73,0.69),.55)

def move(o,col):
    for cc in list(o.users_collection):cc.objects.unlink(o)
    col.objects.link(o);return o

def box_uv(name,u,v,z,su,sv,sz,material,bev=.05):
    x,y=xy(u,v)
    bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,AX))
    o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bev:
        md=o.modifiers.new("Bevel","BEVEL");md.width=bev;md.segments=2
    return move(o,MASTER)

def text_uv(name,text,u,v,z,size,material):
    x,y=xy(u,v)
    cu=bpy.data.curves.new(name+"_Curve",'FONT');cu.body=text;cu.align_x='CENTER';cu.size=size;cu.extrude=.05
    o=bpy.data.objects.new(name,cu);MASTER.objects.link(o);o.location=(x,y,z);o.rotation_euler=(math.pi/2,0,AX)
    cu.materials.append(material);return o

# Re-stage foreground like optical master: cover closer to camera
for o in list(sc.objects):
    if o.name.startswith(("MASTER_Final","MASTER_A_Final","MASTER_B_Final")):
        bpy.data.objects.remove(o,do_unlink=True)

# Left A wall / cover
box_uv("MASTER_A_Final_Wall",-12,-103,1.45,15,1.8,2.9,CONC,.08)
text_uv("MASTER_A_Final","A ↔",-12,-104.0,1.85,1.45,RED)
for i,(u,v) in enumerate([(-23,-99),(-17,-99),(-8,-98),(-2,-98)]):
    box_uv(f"MASTER_Final_Crate_A_{i}",u,v,1.45,5.5,3.7,2.9,DARK,.10)

# Right B wall / cover
box_uv("MASTER_B_Final_Wall",31,-101,1.45,16,1.8,2.9,CONC,.08)
text_uv("MASTER_B_Final","↔ B",31,-102.0,1.85,1.45,RED)
for i,(u,v) in enumerate([(22,-98),(28,-98),(36,-97),(42,-97)]):
    box_uv(f"MASTER_Final_Crate_B_{i}",u,v,1.45,5.5,3.7,2.9,DARK,.10)

# Move/add tram further left but clearly visible
box_uv("MASTER_Final_Tram",-50,-86,2.1,30,5.0,4.0,YELLOW,.28)
box_uv("MASTER_Final_TramGlass",-50,-88.55,2.8,25,.10,1.55,GLASS,.02)
for du in (-9,-4.5,0,4.5,9):
    box_uv(f"MASTER_Final_TramWindow_{du}",-50+du,-88.65,2.8,3.4,.08,1.45,GLASS,.01)

# Stop sign / shelters stronger
box_uv("MASTER_Final_StopRoofL",-40,-91,4.7,18,4.2,.28,DARK,.06)
for du in (-7,7):box_uv(f"MASTER_Final_StopPostL_{du}",-40+du,-91,2.3,.20,.20,4.6,DARK,.02)
text_uv("MASTER_Final_StopName","Rathaus Spandau",-40,-93.2,3.7,.82,WHITE)

box_uv("MASTER_Final_StopRoofR",43,-90,4.7,17,4.2,.28,DARK,.06)
for du in (-7,7):box_uv(f"MASTER_Final_StopPostR_{du}",43+du,-90,2.3,.20,.20,4.6,DARK,.02)

# Statue: taller, silhouette visible on right
box_uv("MASTER_Final_StatuePlinth",40,-74,2.2,9,9,4.4,STONE,.10)
box_uv("MASTER_Final_StatueBase",40,-74,5.0,5.5,5.5,1.8,STONE,.08)
x,y=xy(40,-74)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1.2,location=(x,y,11.2))
o=bpy.context.object;o.name="MASTER_Final_StatueHead";o.data.materials.append(STONE);move(o,MASTER)
bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=1.25,depth=7.0,location=(x,y,8.0))
o=bpy.context.object;o.name="MASTER_Final_StatueBody";o.data.materials.append(STONE);move(o,MASTER)

# Material micro-noise for stone/roof
for name in ("M_MASTER_Stone","M_MASTER_StoneTrim","M_Stone","M_Trim","M_RedTile"):
    m=bpy.data.materials.get(name)
    if not m or not m.use_nodes:continue
    nt=m.node_tree;bs=nt.nodes.get("Principled BSDF")
    if not any(n.type=="TEX_NOISE" for n in nt.nodes):
        noise=nt.nodes.new("ShaderNodeTexNoise");noise.inputs["Scale"].default_value=7.0;noise.inputs["Detail"].default_value=4.0
        bump=nt.nodes.new("ShaderNodeBump");bump.inputs["Strength"].default_value=.16;bump.inputs["Distance"].default_value=.12
        nt.links.new(noise.outputs["Fac"],bump.inputs["Height"]);nt.links.new(bump.outputs["Normal"],bs.inputs["Normal"])

# Camera now slightly left, lower, full square composition
cu,cv=-22,-152
cx,cy=xy(cu,cv);tx,ty=xy(0,-35)
cam=sc.camera
cam.location=(cx,cy,6.8);cam.data.lens=31
cam.rotation_euler=(Vector((tx,ty,28))-cam.location).to_track_quat('-Z','Y').to_euler()

# stronger wet reflections / golden-hour contrast
sc.view_settings.exposure=-.85
world=sc.world
if world and world.use_nodes:
    for n in world.node_tree.nodes:
        if n.type=="BACKGROUND":n.inputs["Strength"].default_value=.32
        if n.type=="TEX_SKY":
            n.sun_elevation=math.radians(16);n.sun_rotation=math.radians(125);n.dust_density=3.2
for o in [x for x in sc.objects if x.type=='LIGHT' and x.data.type=='SUN']:
    o.data.energy=3.2;o.data.angle=math.radians(5.0)

sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.filepath=str(PNG);sc.view_settings.look='AgX - Medium High Contrast'

meta={
 "build":"RathausSpandau_MASTER_Aligned_v6",
 "base":"RathausSpandau_MASTER_Aligned_v5",
 "real_geometry_preserved":True,
 "master_reference":"RathausSpandau_OpticalMaster.png",
 "master_features":["historical facade treatment","copper tower crown","tram + stops","statue","overhead wires","wet plaza","autumn vegetation","foreground A/B cover","master camera and golden-hour light"]
}
META.write_text(json.dumps(meta,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
print("MASTER_V6_READY",OUT)
print("PREVIEW",PNG)
