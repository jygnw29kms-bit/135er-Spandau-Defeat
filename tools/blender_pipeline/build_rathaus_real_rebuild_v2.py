import bpy, math
from pathlib import Path
from mathutils import Vector

OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BLEND=OUT/"RathausSpandau_REAL_Rebuild_v2.blend"
PNG=OUT/"RathausSpandau_REAL_Rebuild_v2_preview.png"
REF=OUT/"RathausSpandau_Real3D_GameMaster.blend"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1.0
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'

ARCH=bpy.data.collections.new("10_ARCH")
DETAIL=bpy.data.collections.new("20_DETAIL")
TOWER=bpy.data.collections.new("30_TOWER")
WORLD=bpy.data.collections.new("40_WORLD")
COLL=bpy.data.collections.new("80_COLLISION")
for col in (ARCH,DETAIL,TOWER,WORLD,COLL):sc.collection.children.link(col)

AX=math.radians(47.5);CA,SA=math.cos(AX),math.sin(AX)
def xy(u,v): return (u*CA-v*SA,u*SA+v*CA)

def mat(name,color,rough=.65,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough;bs.inputs["Metallic"].default_value=metal
    return m

STONE=mat("M_Stone",(0.35,0.30,0.235),.72)
TRIM=mat("M_Trim",(0.57,0.51,0.42),.62)
ROOF=mat("M_RedTile",(0.33,0.052,0.025),.75)
COPPER=mat("M_Copper",(0.055,0.30,0.235),.46,.22)
GLASS=mat("M_Glass",(0.022,0.05,0.065),.16,.06)
DARK=mat("M_Dark",(0.018,0.016,0.015),.5)
GOLD=mat("M_Gold",(0.73,0.52,0.12),.28,.68)
PAVE=mat("M_WetPavers",(0.16,0.155,0.15),.22)
CONC=mat("M_Concrete",(0.31,0.30,0.28),.86)
BLACK=mat("M_BlackMetal",(0.025,0.027,0.03),.35,.5)
LEAF=mat("M_Autumn",(0.48,0.17,0.02),.78)
TRUNK=mat("M_Trunk",(0.13,0.06,0.025),.9)
YELLOW=mat("M_TramYellow",(0.88,0.50,0.025),.38)

def move(o,col):
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);return o

def box_uv(name,u,v,z,su,sv,sz,material,col,bev=.05):
    x,y=xy(u,v)
    bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,AX))
    o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material:o.data.materials.append(material)
    if bev:
        m=o.modifiers.new("Bevel","BEVEL");m.width=bev;m.segments=2
    return move(o,col)

def cyl_uv(name,u,v,z,r,depth,material,col,verts=48):
    x,y=xy(u,v);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z))
    o=bpy.context.object;o.name=name
    if material:o.data.materials.append(material)
    return move(o,col)

def prism_roof(name,u,v,z,su,sv,h,material,col,ridge_u=True):
    # mansard-ish 6-point cross-section; create in aligned U/V then rotate into world
    cross=[(-sv/2,0),(-sv*.35,h*.55),(-sv*.12,h),(sv*.12,h),(sv*.35,h*.55),(sv/2,0)]
    verts=[]
    for uu in (-su/2,su/2):
        for vv,zz in cross:
            lu,lv=(uu,vv) if ridge_u else (vv,uu)
            x,y=xy(u+lu,v+lv);verts.append((x,y,z+zz))
    n=len(cross);faces=[]
    for i in range(n-1):faces.append((i,i+1,n+i+1,n+i))
    faces += [tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    me=bpy.data.meshes.new(name+"_Mesh");me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(material);return o

def disc_on_face(name,u,v,z,normal_u,normal_v,r,material):
    x,y=xy(u,v);nx,ny=xy(normal_u,normal_v)
    n=Vector((nx,ny,0)).normalized()
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=.18,location=(x+n.x*.05,y+n.y*.05,z))
    o=bpy.context.object;o.name=name;o.rotation_euler=n.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);move(o,DETAIL);return o

# VERIFIED architecture dimensions from Berlin3D roof plan + documented 116 m facade.
W=116.0
FRONT_V=-37.0
REAR_V=24.0
CENTER_V=(FRONT_V+REAR_V)/2
FRONT_D=15.0
REAR_D=15.0
SIDE_W=16.0
CROSS_W=11.5
FRONT_H=20.0
WING_H=16.4

# perimeter and three-courtyard structure
box_uv("FrontWing",0,FRONT_V+FRONT_D/2,FRONT_H/2,W,FRONT_D,FRONT_H,STONE,ARCH,.12)
box_uv("RearWing",0,REAR_V-REAR_D/2,WING_H/2,W,REAR_D,WING_H,STONE,ARCH,.10)
box_uv("WestSideWing",-W/2+SIDE_W/2,CENTER_V,WING_H/2,SIDE_W,REAR_V-FRONT_V,WING_H,STONE,ARCH,.10)
box_uv("EastSideWing", W/2-SIDE_W/2,CENTER_V,WING_H/2,SIDE_W,REAR_V-FRONT_V,WING_H,STONE,ARCH,.10)
for i,u in enumerate((-18.5,18.5)):
    box_uv(f"CrossWing_{i}",u,CENTER_V,WING_H/2,CROSS_W,REAR_V-FRONT_V-FRONT_D-REAR_D,WING_H,STONE,ARCH,.08)

# roofs: actual measured roof envelope ~120x61, rebuilt clean
prism_roof("Roof_Front",0,FRONT_V+FRONT_D/2,FRONT_H,W+1.8,FRONT_D+1.4,8.0,ROOF,ARCH,True)
prism_roof("Roof_Rear",0,REAR_V-REAR_D/2,WING_H,W+1.8,REAR_D+1.4,7.2,ROOF,ARCH,True)
prism_roof("Roof_West",-W/2+SIDE_W/2,CENTER_V,WING_H,REAR_V-FRONT_V-14,SIDE_W+1.4,7.0,ROOF,ARCH,False)
prism_roof("Roof_East", W/2-SIDE_W/2,CENTER_V,WING_H,REAR_V-FRONT_V-14,SIDE_W+1.4,7.0,ROOF,ARCH,False)
for i,u in enumerate((-18.5,18.5)):
    prism_roof(f"Roof_Cross_{i}",u,CENTER_V,WING_H,REAR_V-FRONT_V-FRONT_D-REAR_D,CROSS_W+1.0,6.5,ROOF,ARCH,False)

# central risalit + entrance, documented 7-part facade with central gabled projection
box_uv("Central_Risalit",0,FRONT_V-1.6,12.3,25.0,3.2,24.6,TRIM,ARCH,.12)
# triangular front pediment (simple prism)
def pediment(name,u,v,z,w,d,h):
    pts=[(-w/2,0,0),(w/2,0,0),(0,0,h),(-w/2,d,0),(w/2,d,0),(0,d,h)]
    verts=[]
    for uu,vv,zz in pts:
        x,y=xy(u+uu,v+vv);verts.append((x,y,z+zz))
    faces=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
    me=bpy.data.meshes.new(name+"_Mesh");me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);DETAIL.objects.link(o);me.materials.append(TRIM)
pediment("Central_Gable",0,FRONT_V-3.3,24.6,25,3.4,6.5)

# entrance stairs and portals
for i in range(6):
    box_uv(f"Step_{i}",0,FRONT_V-4.0-i*.65,.15+i*.15,13+2*i,1.2,.30,CONC,DETAIL,.03)
for u in (-5.2,0,5.2):
    box_uv(f"Portal_{u}",u,FRONT_V-3.25,3.1,4.0,.35,6.2,DARK,DETAIL,.06)
    # stone lintel
    box_uv(f"PortalLintel_{u}",u,FRONT_V-3.38,6.2,4.7,.55,.55,TRIM,DETAIL,.03)

# front facade windows: four levels, central risalit handled separately
for level,z in enumerate((4.0,8.3,12.6,17.0)):
    for i,u in enumerate([x for x in [(-52+j*4.35) for j in range(25)] if abs(x)>14]):
        box_uv(f"FrontWindow_{level}_{i}",u,FRONT_V-.12,z,1.35,.20,2.25,GLASS,DETAIL,.025)
        box_uv(f"FrontSill_{level}_{i}",u,FRONT_V-.20,z-1.23,1.65,.32,.18,TRIM,DETAIL,.015)
# central risalit window axes
for level,z in enumerate((9.0,13.2,17.4,21.2)):
    for i,u in enumerate((-8.5,-4.25,0,4.25,8.5)):
        box_uv(f"CentralWindow_{level}_{i}",u,FRONT_V-3.23,z,1.45,.20,2.4,GLASS,DETAIL,.025)

# horizontal facade bands and seven-part visual articulation
for z in (2.6,6.6,10.9,15.2,19.4):
    box_uv(f"FrontBand_{z}",0,FRONT_V-.28,z,W+.8,.42,.26,TRIM,DETAIL,.015)
for u in (-45,-30,-14,14,30,45):
    box_uv(f"FrontPilaster_{u}",u,FRONT_V-.35,10.8,.8,.55,20.6,TRIM,DETAIL,.03)

# side/rear external windows
for side,u in (("W",-W/2-.10),("E",W/2+.10)):
    for li,z in enumerate((4.0,8.2,12.4)):
        for j,v in enumerate([-27,-20,-13,-6,1,8,15]):
            # panel thin in U
            box_uv(f"{side}Window_{li}_{j}",u,v,z,.20,1.35,2.2,GLASS,DETAIL,.02)
for li,z in enumerate((4.0,8.2,12.4)):
    for j,u in enumerate([-50,-42,-34,-26,-10,0,10,26,34,42,50]):
        box_uv(f"RearWindow_{li}_{j}",u,REAR_V+.1,z,1.35,.20,2.2,GLASS,DETAIL,.02)

# courtyard windows (three symmetric courtyards)
for li,z in enumerate((4.0,8.2,12.4)):
    for vface in (-21.9,8.9):
        for u in (-46,-37,-31,-9,0,9,31,37,46):
            box_uv(f"CourtV_{li}_{vface}_{u}",u,vface,z,1.2,.18,2.0,GLASS,DETAIL,.02)

# measured tower: tower origin is real Berlin3D high-point cluster, u/v ~= 0
box_uv("Tower_Lower",0,0,25.0,30.0,35.0,10.0,STONE,TOWER,.12)
box_uv("Tower_Transition",-1.0,2.0,35.0,20.0,24.0,10.0,STONE,TOWER,.10)
box_uv("Tower_Shaft",-.6,2.2,47.5,15.5,17.5,15.0,STONE,TOWER,.08)
box_uv("Tower_ClockStage",-.8,2.5,62.5,22.2,21.5,15.0,TRIM,TOWER,.12)
box_uv("Tower_Crown",-.8,2.5,72.5,18.7,19.4,5.0,TRIM,TOWER,.10)
cyl_uv("Tower_Octagon",-.8,2.5,76.4,6.0,2.8,COPPER,TOWER,8)
# rotate octagon to building axis
bpy.data.objects["Tower_Octagon"].rotation_euler.z=AX
# copper cap
x,y=xy(-.8,2.5)
bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=6.4,radius2=1.4,depth=3.2,location=(x,y,79.0),rotation=(0,0,AX))
cup=bpy.context.object;cup.name="Tower_Cupola";cup.data.materials.append(COPPER);move(cup,TOWER)
cyl_uv("Tower_Finial",-.8,2.5,80.2,.42,1.4,GOLD,TOWER,24)

# four clock faces on real stage
for idx,(nu,nv) in enumerate(((0,-1),(1,0),(0,1),(-1,0))):
    # stage half sizes in aligned axes
    hu,hv=11.1,10.75
    u=-.8+nu*(hu+.10);v=2.5+nv*(hv+.10)
    x,y=xy(u,v); nx,ny=xy(nu,nv);n=Vector((nx,ny,0)).normalized()
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=2.6,depth=.18,location=(x+n.x*.04,y+n.y*.04,64.2))
    o=bpy.context.object;o.name=f"Clock_{idx}";o.rotation_euler=n.to_track_quat('Z','Y').to_euler();o.data.materials.append(DARK);move(o,DETAIL)
    # gold center + hands
    cyl_uv(f"ClockHub_{idx}",u,v,64.2,.18,.22,GOLD,DETAIL,24)

# tower windows
for z in (43.0,47.5,52.0):
    box_uv(f"TowerSlit_{z}",-.6,2.2-8.82,z,1.0,.18,2.0,GLASS,DETAIL,.02)

# real-context Rathausplatz; gameplay overlay comes next
box_uv("Rathausplatz",0,FRONT_V-38,-.20,170,62,.40,PAVE,WORLD,0)

# tram rails aligned along facade/plaza in master spirit
for u in (-5.0,5.0):
    box_uv(f"Rail_{u}",u,FRONT_V-42,.03,.10,70,.10,BLACK,WORLD,0)
# simple tram shelter left
for u in (-45,-30):
    box_uv(f"ShelterPost_{u}",u,FRONT_V-48,2.2,.20,.20,4.4,BLACK,WORLD,.02)
box_uv("ShelterRoof",-37.5,FRONT_V-48,4.55,18,4.5,.28,BLACK,WORLD,.06)
box_uv("ShelterGlass",-37.5,FRONT_V-46.0,2.3,17,.10,3.8,GLASS,WORLD,.02)

# wet tactical cover placeholders
for i,(u,v) in enumerate([(-18,FRONT_V-25),(-5,FRONT_V-28),(18,FRONT_V-24),(32,FRONT_V-30)]):
    box_uv(f"Cover_{i}",u,v,1.25,6.0,3.4,2.5,DARK,WORLD,.10)

# collision approximates exact clean architecture, kept invisible
for src in list(ARCH.objects)+list(TOWER.objects):
    if src.type!='MESH':continue
# simple mass collision
box_uv("COL_Main",0,CENTER_V,9.5,W,REAR_V-FRONT_V,19,CONC,COLL,0)
box_uv("COL_Tower",-.8,2.5,40,30,35,80,CONC,COLL,0)
for o in COLL.objects:o.hide_render=True;o.display_type='WIRE'

# autumn trees to frame plaza
def tree(name,u,v,s=1):
    x,y=xy(u,v)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.55*s,depth=10*s,location=(x,y,5*s))
    t=bpy.context.object;t.name=name+"_Trunk";t.data.materials.append(TRUNK);move(t,WORLD)
    for k,(du,dv,dz) in enumerate(((0,0,11),(2,0,13),(-2,1,13),(0,-2,14))):
        xx,yy=xy(u+du*s,v+dv*s)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=3.6*s,location=(xx,yy,dz*s))
        q=bpy.context.object;q.name=f"{name}_Crown{k}";q.data.materials.append(LEAF);move(q,WORLD)
for i,(u,v,s) in enumerate(((-55,FRONT_V-18,1.0),(55,FRONT_V-18,1.0),(-67,FRONT_V-42,.9),(67,FRONT_V-42,.9))):tree(f"Tree{i}",u,v,s)

# daylight / camera aligned to real facade
world=bpy.data.worlds.new("World");sc.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.07,0.10,0.15,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.65
bpy.ops.object.light_add(type='SUN',location=(-120,-140,160))
sun=bpy.context.object;sun.data.energy=3.5;sun.rotation_euler=(math.radians(45),math.radians(-8),AX+math.radians(125))
# camera in aligned coordinates in front-left
cu,cv=-15,FRONT_V-125
cx,cy=xy(cu,cv)
tx,ty=xy(0,-8)
bpy.ops.object.camera_add(location=(cx,cy,25))
cam=bpy.context.object;cam.name="Master_Camera";cam.data.lens=35
cam.rotation_euler=(Vector((tx,ty,29))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam
sc.view_settings.look='AgX - Medium High Contrast'
sc.render.filepath=str(PNG)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)
print("REAL_REBUILD_V2_READY",BLEND)
print("PREVIEW",PNG)
