import bpy, math, random, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BASE=ROOT/"RathausSpandau_REAL_Integrated_Master_v4.blend"
OUT=ROOT/"RathausSpandau_MASTER_Aligned_v5.blend"
PNG=ROOT/"RathausSpandau_MASTER_Aligned_v5_preview.png"
META=ROOT/"RathausSpandau_MASTER_Aligned_v5.json"

bpy.ops.wm.open_mainfile(filepath=str(BASE))
sc=bpy.context.scene
AX=math.radians(47.5); CA,SA=math.cos(AX),math.sin(AX)
def xy(u,v): return (u*CA-v*SA,u*SA+v*CA)

MASTER=bpy.data.collections.get("MASTER_Optical_SetDressing")
if not MASTER:
    MASTER=bpy.data.collections.new("MASTER_Optical_SetDressing");sc.collection.children.link(MASTER)
DETAIL=bpy.data.collections.get("MASTER_Facade_Detail")
if not DETAIL:
    DETAIL=bpy.data.collections.new("MASTER_Facade_Detail");sc.collection.children.link(DETAIL)

def move(o,col):
    for cc in list(o.users_collection): cc.objects.unlink(o)
    col.objects.link(o); return o

def mat(name,color,rough=.5,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m

STONE=mat("M_MASTER_Stone",(0.33,0.29,0.235),.58)
TRIM=mat("M_MASTER_StoneTrim",(0.50,0.44,0.35),.52)
DARK=mat("M_MASTER_Dark",(0.025,0.027,0.03),.38,.35)
GLASS=mat("M_MASTER_Glass",(0.018,0.045,0.065),.12,.08)
COPPER=mat("M_MASTER_Copper",(0.055,0.30,0.23),.40,.28)
GOLD=mat("M_MASTER_Gold",(0.72,0.50,0.10),.25,.65)
RED=mat("M_MASTER_Red",(0.48,0.025,0.018),.42)
WHITE=mat("M_MASTER_White",(0.72,0.70,0.66),.55)
YELLOW=mat("M_MASTER_TramYellow",(0.90,0.52,0.02),.35)
BLACK=mat("M_MASTER_BlackMetal",(0.018,0.02,0.023),.28,.55)
CONC=mat("M_MASTER_Concrete",(0.30,0.29,0.27),.76)
LEAF=mat("M_MASTER_AutumnLeaves",(0.50,0.18,0.025),.70)
TRUNK=mat("M_MASTER_Trunk",(0.12,0.055,0.02),.88)
WET=mat("M_MASTER_Wet",(0.02,0.035,0.05),.08,.05)

def box_uv(name,u,v,z,su,sv,sz,material,col=DETAIL,bev=.04):
    x,y=xy(u,v)
    bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,AX))
    o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material:o.data.materials.append(material)
    if bev:
        md=o.modifiers.new("Bevel","BEVEL");md.width=bev;md.segments=2
    return move(o,col)

def cyl_uv(name,u,v,z,r,depth,material,col=DETAIL,verts=32):
    x,y=xy(u,v)
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z))
    o=bpy.context.object;o.name=name
    if material:o.data.materials.append(material)
    return move(o,col)

def text_uv(name,text,u,v,z,size,material,col=MASTER):
    x,y=xy(u,v)
    cu=bpy.data.curves.new(name+"_Curve",'FONT');cu.body=text;cu.align_x='CENTER';cu.size=size;cu.extrude=.035
    o=bpy.data.objects.new(name,cu);col.objects.link(o);o.location=(x,y,z);o.rotation_euler=(math.pi/2,0,AX)
    cu.materials.append(material);return o

# Remove earlier simple master objects that are replaced
for prefix in ("MASTER_Tram","MASTER_Stop","MASTER_Statue","MASTER_Rail","MASTER_Puddle"):
    for o in list(sc.objects):
        if o.name.startswith(prefix):
            bpy.data.objects.remove(o,do_unlink=True)

# Facade: stone texture treatment on clean rebuild
for o in sc.objects:
    if o.type!='MESH': continue
    if o.name in ("FrontWing","Central_Risalit","WestSideWing","EastSideWing","RearWing") or o.name.startswith("CrossWing_"):
        o.data.materials.clear();o.data.materials.append(STONE)

# front cornices and pilasters
FRONT_V=-37.0
for z in (2.6,6.6,10.9,15.2,19.3):
    box_uv(f"MASTER_Cornice_{z}",0,FRONT_V-.35,z,117,.55,.32,TRIM,DETAIL,.025)
for u in (-51,-43,-35,-27,-19,-13,13,19,27,35,43,51):
    box_uv(f"MASTER_Pilaster_{u}",u,FRONT_V-.48,10.8,.9,.65,20.4,TRIM,DETAIL,.035)

# central grand entrance and deep arches
for u in (-5.4,0,5.4):
    box_uv(f"MASTER_PortalDark_{u}",u,FRONT_V-3.6,3.3,4.2,.75,6.6,DARK,DETAIL,.08)
    x,y=xy(u,FRONT_V-3.65)
    bpy.ops.mesh.primitive_torus_add(major_radius=2.05,minor_radius=.25,major_segments=48,minor_segments=12,location=(x,y,6.4),rotation=(math.pi/2,0,AX))
    tor=bpy.context.object;tor.name=f"MASTER_Arch_{u}";tor.data.materials.append(TRIM);move(tor,DETAIL)
# stairs wider like reference
for i in range(8):
    box_uv(f"MASTER_EntryStep_{i}",0,FRONT_V-4.2-i*.62,.16+i*.15,14+2.0*i,1.2,.30,CONC,DETAIL,.02)

# roof dormers + central ornament
for i,u in enumerate(range(-46,47,9)):
    if abs(u)<15: continue
    box_uv(f"MASTER_Dormer_{i}",u,FRONT_V+4.8,23.5,2.8,3.0,3.2,TRIM,DETAIL,.05)
    x,y=xy(u,FRONT_V+4.8)
    bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=2.1,radius2=.15,depth=2.0,location=(x,y,26.0),rotation=(0,0,AX+math.pi/4))
    o=bpy.context.object;o.name=f"MASTER_DormerRoof_{i}";o.data.materials.append(bpy.data.materials.get("M_RedTile") or RED);move(o,DETAIL)

# vertical civic banners on central risalit
for u,material in [(-6.3,RED),(0,WHITE),(6.3,RED)]:
    box_uv(f"MASTER_Banner_{u}",u,FRONT_V-3.75,16.5,2.7,.08,11.5,material,DETAIL,0)

# tower richer detailing and copper crown
for z in (39,50,58,69):
    box_uv(f"MASTER_TowerLedge_{z}",-.8,2.5-10.9,z,19.0,.7,.50,TRIM,DETAIL,.03)
# clock front accent
x,y=xy(-.8,2.5-10.9)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=2.8,depth=.24,location=(x,y,63.0),rotation=(math.pi/2,0,AX))
clock=bpy.context.object;clock.name="MASTER_ClockFront";clock.data.materials.append(DARK);move(clock,DETAIL)
for a in range(0,360,30):
    ra=math.radians(a); du=math.sin(ra)*2.15; dz=math.cos(ra)*2.15
    box_uv(f"MASTER_ClockTick_{a}",-.8+du,2.5-11.05,63+dz,.18,.08,.48,GOLD,DETAIL,.01)

# copper lantern/spire added atop existing tower
cyl_uv("MASTER_CopperLantern",-.8,2.5,82.7,2.2,3.0,COPPER,DETAIL,8)
x,y=xy(-.8,2.5)
bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=2.6,radius2=.35,depth=3.0,location=(x,y,85.6),rotation=(0,0,AX))
cap=bpy.context.object;cap.name="MASTER_CopperCap";cap.data.materials.append(COPPER);move(cap,DETAIL)
cyl_uv("MASTER_Spire",-.8,2.5,89.4,.25,5.0,COPPER,DETAIL,20)

# plaza wet sheen: thin broad reflective plates
for i,(u,v,su,sv) in enumerate([(-30,-66,24,8),(-4,-69,18,7),(24,-67,20,7),(46,-70,12,6),(-12,-53,15,5)]):
    box_uv(f"MASTER_Puddle_{i}",u,v,.07,su,sv,.025,WET,MASTER,0)

# tram tracks in front plaza
for u in (-5.0,5.0):
    box_uv(f"MASTER_Rail_{u}",u,-78,.06,.10,70,.10,BLACK,MASTER,0)

# tram left
box_uv("MASTER_TramBody",-47,-80,2.0,28,4.8,3.8,YELLOW,MASTER,.28)
box_uv("MASTER_TramGlass",-47,-82.45,2.75,24,.10,1.55,GLASS,MASTER,.02)
for du in (-9,-4.5,0,4.5,9):
    box_uv(f"MASTER_TramWindow_{du}",-47+du,-82.55,2.75,3.5,.08,1.45,GLASS,MASTER,.01)

# shelters left/right
for side,u in [("L",-41),("R",43)]:
    for du in (-7,7):
        box_uv(f"MASTER_StopPost_{side}_{du}",u+du,-70,2.3,.18,.18,4.6,BLACK,MASTER,.02)
    box_uv(f"MASTER_StopRoof_{side}",u,-70,4.75,17,4.5,.28,BLACK,MASTER,.06)
    box_uv(f"MASTER_StopGlass_{side}",u,-67.85,2.4,16,.10,3.9,GLASS,MASTER,.02)
text_uv("MASTER_StopName","Rathaus Spandau",-41,-72.2,3.65,.78,WHITE,MASTER)

# statue right
box_uv("MASTER_StatuePlinth",38,-56,2.0,9,9,4,TRIM,MASTER,.10)
box_uv("MASTER_StatueBase",38,-56,5.0,5.5,5.5,2.0,STONE,MASTER,.08)
cyl_uv("MASTER_StatueFigure",38,-56,9.0,1.1,6.0,STONE,MASTER,20)

# A/B combat cover from master
for i,(u,v,su,sv,sz) in enumerate([
    (-20,-60,7,4,3),(-12,-60,7,4,3),
    (20,-61,7,4,3),(28,-61,7,4,3),
    (37,-66,7,4,3),(-3,-64,6,4,3)
]):
    box_uv(f"MASTER_Crate_{i}",u,v,sz/2,su,sv,sz,DARK,MASTER,.10)
box_uv("MASTER_A_Wall",-7,-57,1.45,13,1.5,2.9,CONC,MASTER,.08)
box_uv("MASTER_B_Wall",44,-61,1.45,13,1.5,2.9,CONC,MASTER,.08)
text_uv("MASTER_A","A ↔",-7,-57.8,1.8,1.35,RED,MASTER)
text_uv("MASTER_B","↔ B",44,-61.8,1.8,1.35,RED,MASTER)

# overhead tram wires and lamps
for u in (-7,7):
    for v in (-90,-72,-54):
        box_uv(f"MASTER_WirePole_{u}_{v}",u,v,5.8,.20,.20,11.6,BLACK,MASTER,.02)
for u in (-3.6,3.6):
    box_uv(f"MASTER_OverheadWire_{u}",u,-72,10.7,.045,70,.045,BLACK,MASTER,0)
for u,v in [(-24,-58),(24,-58),(-50,-64),(50,-64)]:
    box_uv(f"MASTER_LampPost_{u}_{v}",u,v,4.0,.20,.20,8.0,BLACK,MASTER,.02)
    box_uv(f"MASTER_LampHead_{u}_{v}",u,v-.8,7.8,.7,1.8,.28,BLACK,MASTER,.04)

# autumn trees framing
for i,(u,v,s) in enumerate([(-58,-52,1.1),(58,-52,1.1),(-68,-72,.9),(68,-72,.9),(-48,-88,.8),(50,-88,.8)]):
    cyl_uv(f"MASTER_TreeTrunk_{i}",u,v,5.5*s,.55*s,11*s,TRUNK,MASTER,12)
    x,y=xy(u,v)
    for j,(du,dv,dz) in enumerate([(0,0,12),(2,0,14),(-2,1,14),(1,-2,16),(-1,2,16)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=3.9*s,location=(x+du*s,y+dv*s,dz*s))
        o=bpy.context.object;o.name=f"MASTER_TreeCrown_{i}_{j}";o.data.materials.append(LEAF);move(o,MASTER)

# fallen leaves
random.seed(135)
for i in range(140):
    u=random.uniform(-62,62); v=random.uniform(-92,-45)
    x,y=xy(u,v)
    bpy.ops.mesh.primitive_circle_add(vertices=6,radius=random.uniform(.07,.20),fill_type='NGON',location=(x,y,.09),rotation=(0,0,random.random()*math.tau))
    o=bpy.context.object;o.name=f"MASTER_Leaf_{i}";o.scale.y=random.uniform(.35,.8);o.data.materials.append(LEAF);move(o,MASTER)

# golden-hour lighting like master
world=sc.world
if world:
    world.use_nodes=True
    nt=world.node_tree
    for n in list(nt.nodes):
        if n.type not in {'OUTPUT_WORLD'}: nt.nodes.remove(n)
    out=nt.nodes.get("World Output")
    sky=nt.nodes.new("ShaderNodeTexSky");sky.sky_type='NISHITA';sky.sun_elevation=math.radians(20);sky.sun_rotation=math.radians(125);sky.dust_density=2.2
    bg=nt.nodes.new("ShaderNodeBackground");bg.inputs["Strength"].default_value=.55
    nt.links.new(sky.outputs["Color"],bg.inputs["Color"]);nt.links.new(bg.outputs["Background"],out.inputs["Surface"])
for o in [x for x in sc.objects if x.type=='LIGHT' and x.data.type=='SUN']:
    o.data.energy=4.2;o.data.angle=math.radians(4.5);o.rotation_euler=(math.radians(48),math.radians(-10),AX+math.radians(130))

# master camera: low plaza 3/4, not overhead
cu,cv=-18,-112
cx,cy=xy(cu,cv); tx,ty=xy(0,-10)
cam=sc.camera
cam.location=(cx,cy,10.5);cam.data.lens=32
cam.rotation_euler=(Vector((tx,ty,32))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.filepath=str(PNG);sc.view_settings.look='AgX - Medium High Contrast'

meta={
 "build":"RathausSpandau_MASTER_Aligned_v5",
 "base":"RathausSpandau_REAL_Integrated_Master_v4",
 "master_reference":"RathausSpandau_OpticalMaster.png",
 "real_geometry_preserved":True,
 "master_applied_to":["facade detailing","materials","wet plaza","tram/stop","statue","overhead wires","autumn vegetation","A/B cover","lighting/camera"],
 "policy":"real geometry remains authoritative; master controls look/gameplay set dressing"
}
META.write_text(json.dumps(meta,indent=2),encoding='utf-8')

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
print("MASTER_V5_READY",OUT)
print("PREVIEW",PNG)
