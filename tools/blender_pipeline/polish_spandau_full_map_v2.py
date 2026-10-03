import bpy, bmesh, math, json, random
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BASE=ROOT/"SpandauStrike_Rathaus_FULLMAP_v1.blend"
OUT=ROOT/"SpandauStrike_Rathaus_FULLMAP_v2.blend"
PNG=ROOT/"SpandauStrike_Rathaus_FULLMAP_v2_overview.png"
META=ROOT/"SpandauStrike_Rathaus_FULLMAP_v2.json"

bpy.ops.wm.open_mainfile(filepath=str(BASE))
sc=bpy.context.scene

ENV=bpy.data.collections.get("FULLMAP_Environment")
DETAIL=bpy.data.collections.get("FULLMAP_Detail") or bpy.data.collections.new("FULLMAP_Detail")
if DETAIL.name not in sc.collection.children: sc.collection.children.link(DETAIL)
COL=bpy.data.collections.get("FULLMAP_Collision")
GAME=bpy.data.collections.get("FULLMAP_Gameplay")

def move(o,col):
    for cc in list(o.users_collection): cc.objects.unlink(o)
    col.objects.link(o); return o

def mat(name,color,rough=.6,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m

FACADE1=mat("M_City_Facade_Stone",(0.28,0.25,0.22),.72)
FACADE2=mat("M_City_Facade_Warm",(0.34,0.27,0.20),.70)
FACADE3=mat("M_City_Facade_Gray",(0.22,0.23,0.24),.68)
ROOF1=mat("M_City_Roof_Red",(0.22,0.045,0.02),.75)
ROOF2=mat("M_City_Roof_Dark",(0.06,0.065,0.07),.72)
ROAD=mat("M_City_Road_Wet",(0.035,0.04,0.045),.20,.03)
WATER=mat("M_City_Water",(0.018,0.09,0.13),.08,.05)
SIDEWALK=mat("M_City_Sidewalk",(0.22,0.22,0.21),.68)
TREE=mat("M_City_Tree",(0.38,0.14,0.025),.76)
TRUNK=mat("M_City_Trunk",(0.11,0.055,0.025),.88)
METAL=mat("M_City_Metal",(0.025,0.03,0.035),.35,.55)

# Tune existing roads/water materials
for o in sc.objects:
    if o.name.startswith("REAL_OSM_Roads") or o.name.startswith("FULLMAP_Road"):
        if o.type=="MESH":
            o.data.materials.clear(); o.data.materials.append(ROAD)
    if o.name.startswith("FULLMAP_Water"):
        if o.type=="MESH":
            o.data.materials.clear(); o.data.materials.append(WATER)

# City buildings: assign multiple façade + roof material slots per face
city=next((o for o in sc.objects if o.name.startswith("FULLMAP_SurroundingBuildings") and o.type=="MESH"),None)
if city:
    city.data.materials.clear()
    for m in (FACADE1,FACADE2,FACADE3,ROOF1,ROOF2): city.data.materials.append(m)
    bm=bmesh.new(); bm.from_mesh(city.data)
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        c=f.calc_center_median()
        n=f.normal.normalized()
        if n.z > .45:
            f.material_index = 3 if (int(abs(c.x)+abs(c.y))%3) else 4
        else:
            seed=int((c.x+500)//35)*73856093 ^ int((c.y+500)//35)*19349663
            f.material_index=abs(seed)%3
    bm.to_mesh(city.data); bm.free(); city.data.update()

# Create sidewalks / plazas as readable urban surfaces around center
def box(name,x,y,z,sx,sy,sz,material,col=DETAIL,bev=.03):
    bpy.ops.mesh.primitive_cube_add(location=(x,y,z))
    o=bpy.context.object;o.name=name;o.dimensions=(sx,sy,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bev:
        md=o.modifiers.new("Bevel","BEVEL");md.width=bev;md.segments=2
    return move(o,col)

for name,x,y,sx,sy in [
    ("FULLMAP_CenterPlaza",0,-70,145,80),
    ("FULLMAP_WestWalk",-120,-40,80,18),
    ("FULLMAP_EastWalk",120,-35,80,18),
]:
    box(name,x,y,.025,sx,sy,.05,SIDEWALK,DETAIL,0)

# Add urban tree bands / lamps along approach corridors
random.seed(135)
tree_pts=[]
for side in (-1,1):
    for i in range(18):
        x=side*(85+random.uniform(-8,8))
        y=-170+i*20+random.uniform(-4,4)
        tree_pts.append((x,y,random.uniform(.75,1.15)))
for i in range(14):
    x=-200+i*30
    y=115+random.uniform(-6,6)
    tree_pts.append((x,y,random.uniform(.75,1.05)))

for i,(x,y,s) in enumerate(tree_pts):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=.45*s,depth=6.5*s,location=(x,y,3.25*s))
    t=bpy.context.object;t.name=f"FULLMAP_TreeTrunk_{i}";t.data.materials.append(TRUNK);move(t,DETAIL)
    for j,(dx,dy,dz) in enumerate([(0,0,7.5),(2,0,8.5),(-2,1,8.5),(0,-2,9.5)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=2.8*s,location=(x+dx*s,y+dy*s,dz*s))
        o=bpy.context.object;o.name=f"FULLMAP_TreeCrown_{i}_{j}";o.data.materials.append(TREE);move(o,DETAIL)

# Street lamps along main approaches
lamp_pts=[]
for y in range(-220,181,35):
    for x in (-62,62): lamp_pts.append((x,y))
for i,(x,y) in enumerate(lamp_pts):
    box(f"FULLMAP_LampPost_{i}",x,y,4,.16,.16,8,METAL,DETAIL,.02)
    box(f"FULLMAP_LampHead_{i}",x,y-.7,7.75,.65,1.5,.22,METAL,DETAIL,.03)

# Create broad walkable collision ground and keep invisible
GROUND=mat("M_COLL_Ground",(0.05,0.05,0.05),1)
ground_col=box("COL_FULLMAP_Ground",0,0,-.35,1000,1000,.6,GROUND,COL,0)
ground_col.hide_render=True; ground_col.display_type='WIRE'

# Surroundings collision proxy uses the actual city mesh as source; duplicate for collision collection
if city:
    proxy=city.copy(); proxy.data=city.data.copy(); proxy.name="COL_FULLMAP_SurroundingBuildings"
    COL.objects.link(proxy); proxy.hide_render=True; proxy.display_type='WIRE'

# Navigation exclusion around map boundary corners / water
for i,(x,y,sx,sy) in enumerate([
    (-450,-450,90,90),(450,-450,90,90),(-450,450,90,90),(450,450,90,90)
]):
    o=box(f"NAV_BLOCK_{i}",x,y,3,sx,sy,6,GROUND,COL,0)
    o.hide_render=True;o.display_type='WIRE'

# Add secondary spawn-zone visual markers
SPAWNW=bpy.data.materials.get("M_Spawn_West")
SPAWNE=bpy.data.materials.get("M_Spawn_East")
for side,prefix,material in [("WEST","SPAWN_WEST_",SPAWNW),("EAST","SPAWN_EAST_",SPAWNE)]:
    markers=[o for o in sc.objects if o.name.startswith(prefix)]
    for i,o in enumerate(markers):
        if i>=2: continue
        bpy.ops.mesh.primitive_torus_add(major_radius=4.5,minor_radius=.18,major_segments=32,minor_segments=8,location=(o.location.x,o.location.y,o.location.z+.25))
        r=bpy.context.object;r.name=f"SPAWN_RING_{side}_{i+1}";r.data.materials.append(material);move(r,GAME)

# Overview camera closer / city readable
cam=sc.camera
cam.location=(0,-780,470)
cam.data.lens=52
cam.rotation_euler=(Vector((0,0,10))-cam.location).to_track_quat('-Z','Y').to_euler()

# lighting
world=sc.world
if world and world.use_nodes:
    bg=world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value=(.09,.12,.17,1);bg.inputs["Strength"].default_value=.80
for o in [x for x in sc.objects if x.type=="LIGHT" and x.data.type=="SUN"]:
    o.data.energy=4.0;o.data.color=(1.0,.78,.58)

sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(PNG)
sc.view_settings.exposure=.15

META.write_text(json.dumps({
  "build":"SpandauStrike_Rathaus_FULLMAP_v2",
  "base":"v1",
  "status":"full-map playable modeling pass",
  "added":["city facade/roof materials","wet roads","water material","center sidewalks","urban tree belts","street lamps","ground collision","surrounding-building collision proxy","nav blockers","spawn rings"],
  "extent_m":[1000,1000],
  "building_faces":len(city.data.polygons) if city else 0
},indent=2),encoding="utf-8")

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
print("FULLMAP_V2_READY",OUT)
print("OVERVIEW",PNG)
print("CITY_FACES",len(city.data.polygons) if city else 0)
