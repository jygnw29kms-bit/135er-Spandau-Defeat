import bpy, math, json
from pathlib import Path
from mathutils import Vector

OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
SHELL=OUT/"Rathaus_Shell_REAL.obj"
ROOF=OUT/"Rathaus_Roof_REAL.obj"
PLAN=json.load(open(OUT/"Rathaus_roofplan_real.json"))
BLEND=OUT/"RathausSpandau_REAL_Rebuild_v1.blend"
PNG=OUT/"RathausSpandau_REAL_Rebuild_v1_preview.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.unit_settings.system='METRIC'
sc.unit_settings.scale_length=1.0
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'

ARCH=bpy.data.collections.new("10_ARCH_REAL")
DETAIL=bpy.data.collections.new("20_DETAIL")
TOWER=bpy.data.collections.new("30_TOWER")
WORLD=bpy.data.collections.new("40_WORLD")
COLL=bpy.data.collections.new("80_COLLISION")
for col in (ARCH,DETAIL,TOWER,WORLD,COLL):sc.collection.children.link(col)

def move(o,col):
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);return o

def mat(name,color,rough=.65,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m

STONE=mat("M_Rathaus_Stone",(0.34,0.29,0.23),.68)
TRIM=mat("M_Rathaus_Trim",(0.56,0.50,0.40),.62)
ROOFMAT=mat("M_Rathaus_RedTile",(0.34,0.055,0.027),.72)
COPPER=mat("M_Rathaus_Copper",(0.055,0.29,0.23),.48,.25)
GLASS=mat("M_Rathaus_Glass",(0.025,0.055,0.070),.18,.05)
DARK=mat("M_Rathaus_Dark",(0.018,0.018,0.020),.48)
GOLD=mat("M_Rathaus_ClockGold",(0.72,0.51,0.12),.28,.65)
PAVE=mat("M_Plaza",(0.19,0.18,0.17),.30)
CONC=mat("M_Collision",(0.08,0.30,0.10),.95)

# Import generated true-plan shell and actual measured roof component
def import_obj(path,name,col,material):
    bpy.ops.wm.obj_import(filepath=str(path))
    objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
    if not objs:raise RuntimeError("import failed "+str(path))
    if len(objs)>1:
        bpy.context.view_layer.objects.active=objs[0]
        for o in objs:o.select_set(True)
        bpy.ops.object.join();o=bpy.context.object
    else:o=objs[0]
    o.rotation_euler=(0,0,0)
    o.name=name
    if material:
        o.data.materials.clear();o.data.materials.append(material)
    move(o,col)
    return o

shell=import_obj(SHELL,"Rathaus_REAL_Walls",ARCH,STONE)
roof=import_obj(ROOF,"Rathaus_REAL_Roof",ARCH,ROOFMAT)
# Actual roof planes benefit from smooth shading but keep geometry unchanged
for p in roof.data.polygons:p.use_smooth=True

def box(name,loc,size,material,col,rz=0,bevel=.04):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=(0,0,rz))
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material:o.data.materials.append(material)
    if bevel:
        md=o.modifiers.new("Bevel","BEVEL");md.width=bevel;md.segments=2
    return move(o,col)

def cyl(name,loc,r,depth,material,col,verts=48,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object;o.name=name
    if material:o.data.materials.append(material)
    return move(o,col)

def cone(name,loc,r1,r2,depth,material,col,verts=12,rz=0):
    bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=depth,location=loc,rotation=(0,0,rz))
    o=bpy.context.object;o.name=name
    if material:o.data.materials.append(material)
    return move(o,col)

axis=math.radians(47.5)

# Measured tower cross-section profile from Berlin3D 2025
# centers are small offsets from verified high-vertex cluster
box("Tower_Lower",(-.5,0.0,23.1),(30.0,35.0,13.8),STONE,TOWER,axis,.12)  # 16.2..30
box("Tower_Transition",(-2.9,2.0,35.0),(20.0,24.0,10.0),STONE,TOWER,axis,.10)
box("Tower_Shaft",(-.7,1.3,47.5),(15.5,17.5,15.0),STONE,TOWER,axis,.08)
box("Tower_ClockStage",(-1.0,2.6,62.5),(22.2,21.5,15.0),TRIM,TOWER,axis,.12)
box("Tower_Crown",(-1.0,2.3,72.5),(18.7,19.4,5.0),TRIM,TOWER,axis,.10)
cyl("Tower_Octagon",(-.6,2.25,76.3),6.0,2.8,COPPER,TOWER,8,(0,0,axis))
cone("Tower_Cupola",(-.6,2.25,78.7),6.3,1.4,3.2,COPPER,TOWER,12,axis)
cyl("Tower_Finial",(-.6,2.25,80.15),.42,1.3,GOLD,TOWER,24)

# Clock faces on four measured clock-stage faces
clock_z=64.2
for i,a in enumerate([axis,axis+math.pi/2,axis+math.pi,axis+3*math.pi/2]):
    # face normal in XY
    nx,ny=math.cos(a-math.pi/2),math.sin(a-math.pi/2)
    # half-depth approx 10.9m
    x=-1.0+nx*10.95;y=2.6+ny*10.95
    cyl(f"ClockFace_{i}",(x,y,clock_z),2.55,.18,DARK,DETAIL,64,(math.pi/2,0,a))
    # hands as slim boxes near face
    box(f"ClockHandV_{i}",(x+nx*.12,y+ny*.12,clock_z+.65),(.14,.10,1.55),GOLD,DETAIL,a,.01)

# tower slit windows
for z in (42.5,47.0,51.5):
    # place on west/front-ish face
    a=axis+math.pi
    nx,ny=math.cos(a-math.pi/2),math.sin(a-math.pi/2)
    box(f"TowerWindow_{z}",(-.7+nx*8.8,1.3+ny*8.8,z),(1.0,.16,2.0),GLASS,DETAIL,a,.02)

# Real-outline facade windows and cornice bands
outer=PLAN["contours"][0]["poly"]
holes=[x["poly"] for x in PLAN["contours"] if x["parent"]==0]

def signed_area(poly):
    return .5*sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))

def segment_details(poly,is_hole=False):
    area=signed_area(poly)
    for si,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
        x1,y1=a;x2,y2=b;dx=x2-x1;dy=y2-y1;L=math.hypot(dx,dy)
        if L<4.5:continue
        ang=math.atan2(dy,dx)
        # outward normal for exterior; courtyard-facing for holes
        if area>0:nx,ny=dy/L,-dx/L
        else:nx,ny=-dy/L,dx/L
        if is_hole:nx,ny=-nx,-ny
        # stone horizontal bands along substantial walls
        if L>8:
            for z in (3.0,7.2,11.4,15.2):
                box(f"Band_{'H' if is_hole else 'O'}_{si}_{z}",((x1+x2)/2+nx*.18,(y1+y2)/2+ny*.18,z),(L,.32,.20),TRIM,DETAIL,ang,.01)
        spacing=3.8
        count=max(1,int((L-2.0)//spacing))
        for k in range(count):
            t=(k+1)/(count+1)
            x=x1+dx*t+nx*.20;y=y1+dy*t+ny*.20
            for li,z in enumerate((4.1,8.3,12.5)):
                box(f"W_{'H' if is_hole else 'O'}_{si}_{k}_{li}",(x,y,z),(1.25,.18,2.15),GLASS,DETAIL,ang,.025)
                box(f"Sill_{'H' if is_hole else 'O'}_{si}_{k}_{li}",(x+nx*.04,y+ny*.04,z-1.18),(1.55,.28,.16),TRIM,DETAIL,ang,.01)

segment_details(outer,False)
for h in holes:segment_details(h,True)

# plaza for clean validation
box("Rathausplatz",(5,-72,-.18),(170,95,.36),PAVE,WORLD,axis,0)

# simple clean collision based on real shell/tower envelope
box("COL_Main",(12,-6,8.0),(95,122,16),CONC,COLL,axis,0)
box("COL_Tower",(-.5,2.0,40),(30,35,80),CONC,COLL,axis,0)
for o in COLL.objects:o.hide_render=True;o.display_type='WIRE'

# world / lighting
world=bpy.data.worlds.new("World");sc.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.065,0.085,0.12,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.6
bpy.ops.object.light_add(type='SUN',location=(-100,-140,160))
sun=bpy.context.object;sun.data.energy=3.6;sun.rotation_euler=(math.radians(48),math.radians(-8),math.radians(-55))
bpy.ops.object.light_add(type='AREA',location=(-40,-65,35))
fill=bpy.context.object;fill.data.energy=900;fill.data.size=45;fill.data.color=(1.0,.72,.50)

# camera from southwest plaza, looking at measured building center/tower
bpy.ops.object.camera_add(location=(-125,-120,24))
cam=bpy.context.object;cam.name="REAL_Rebuild_Camera";cam.data.lens=38
cam.rotation_euler=(Vector((8,-4,31))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam
sc.view_settings.look='AgX - Medium High Contrast'
sc.render.filepath=str(PNG)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)
print("REAL_REBUILD_READY",BLEND)
print("PREVIEW",PNG)
print("OBJECTS",len(bpy.data.objects))
