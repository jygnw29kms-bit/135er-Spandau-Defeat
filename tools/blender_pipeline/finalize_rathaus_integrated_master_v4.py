import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline")
FINAL=ROOT/"rathaus_final"
GIS=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1")
BASE=FINAL/"RathausSpandau_REAL_Rebuild_v2.blend"
OUT=FINAL/"RathausSpandau_REAL_Integrated_Master_v4.blend"
PNG=FINAL/"RathausSpandau_REAL_Integrated_Master_v4_preview.png"
META=FINAL/"RathausSpandau_REAL_Integrated_Master_v4.json"

OX,OY=377956.8271307037,5822062.184676066
OE,ON=377897.8969272321,5822086.91786854
BASELINE=33.45;GROUND=31.0
DX=OX-OE; DY=ON-OY; DZ=BASELINE-GROUND

bpy.ops.wm.open_mainfile(filepath=str(BASE))
sc=bpy.context.scene

# provenance collections
REAL_WORLD=bpy.data.collections.get("REAL_Terrain_Roads_DGM_OSM") or bpy.data.collections.new("REAL_Terrain_Roads_DGM_OSM")
if REAL_WORLD.name not in sc.collection.children: sc.collection.children.link(REAL_WORLD)
RAWREF=bpy.data.collections.get("REAL_Raw_Berlin3D_Reference_Hidden") or bpy.data.collections.new("REAL_Raw_Berlin3D_Reference_Hidden")
if RAWREF.name not in sc.collection.children: sc.collection.children.link(RAWREF)
MASTER=bpy.data.collections.get("MASTER_Optical_SetDressing") or bpy.data.collections.new("MASTER_Optical_SetDressing")
if MASTER.name not in sc.collection.children: sc.collection.children.link(MASTER)

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

GROUND_M=mat("M_REAL_Ground",(0.11,0.13,0.105),.82)
ROAD_M=mat("M_REAL_Road",(0.035,0.04,0.045),.44)
RAW_M=mat("M_RAW_Reference",(0.18,0.28,0.48),.75)
WET=mat("M_MASTER_Wet",(0.025,0.045,0.06),.10,.03)
BLACK=mat("M_MASTER_BlackMetal",(0.025,0.027,0.03),.34,.5)
YELLOW=mat("M_MASTER_TramYellow",(0.88,0.50,0.025),.38)
STONE=bpy.data.materials.get("M_Stone") or mat("M_Stone",(0.35,0.30,0.235),.72)
GLASS=bpy.data.materials.get("M_Glass") or mat("M_Glass",(0.022,0.05,0.065),.16,.06)

def import_obj(path,name,col,material=None):
    bpy.ops.wm.obj_import(filepath=str(path))
    objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
    for i,o in enumerate(objs):
        o.name=name if len(objs)==1 else f"{name}_{i}"
        o.rotation_euler=(0,0,0)
        if material:
            o.data.materials.clear();o.data.materials.append(material)
        move(o,col)
    return objs

def box(name,loc,size,material,col,bev=.04):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material:o.data.materials.append(material)
    if bev:
        md=o.modifiers.new("Bevel","BEVEL");md.width=bev;md.segments=2
    return move(o,col)

# Real terrain / roads
terrain=import_obj(GIS/"rathaus_terrain.obj","REAL_DGM_Terrain",REAL_WORLD,GROUND_M)
roads=import_obj(GIS/"rathaus_roads.obj","REAL_OSM_Roads",REAL_WORLD,ROAD_M)
for o in terrain+roads:
    # GIS obj: x=(E-OE)*100, y=-(N-ON)*100, z=(Z-baseline)*100
    # final world: E-OX, N-OY, Z-ground
    o.scale=(.01,-.01,.01)
    o.location=(-DX,DY,DZ)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.select_set(False)

# Raw measured assets retained but hidden: evidence/reference, not visible game geometry
for fn,name in [("Rathaus_Shell_REAL.obj","RAW_REAL_Shell"),("Rathaus_Roof_REAL.obj","RAW_REAL_Roof")]:
    objs=import_obj(FINAL/fn,name,RAWREF,RAW_M)
    for o in objs:
        o.hide_render=True
        o.hide_viewport=True

# master set dressing separated from measured data
for i,(x,y,sx,sy) in enumerate([(-25,-65,16,4),(10,-70,14,4),(33,-68,12,3),(-6,-55,9,3)]):
    box(f"MASTER_Puddle_{i}",(x,y,.08),(sx,sy,.025),WET,MASTER,0)
for x in (-4.5,4.5):
    box(f"MASTER_Rail_{x}",(x,-78,.06),(.10,58,.10),BLACK,MASTER,0)
box("MASTER_Tram",(-51,-83,2.0),(27,4.8,3.8),YELLOW,MASTER,.28)
box("MASTER_TramGlass",(-51,-85.45,2.75),(23,.12,1.55),GLASS,MASTER,.02)
box("MASTER_StopRoof",(-34,-75,4.55),(18,4.2,.28),BLACK,MASTER,.06)
for px in (-42,-26):
    box(f"MASTER_StopPost_{px}",(px,-75,2.2),(.18,.18,4.4),BLACK,MASTER,.02)
box("MASTER_StatuePlinth",(42,-59,2.0),(8,8,4),STONE,MASTER,.08)

# improve actual scene materials/light from V2
for name,color,rough in [
    ("M_Stone",(0.38,0.32,0.25,1),.64),
    ("M_Trim",(0.56,0.50,0.41,1),.60),
    ("M_RedTile",(0.34,0.06,0.03,1),.68),
    ("M_WetPavers",(0.14,0.145,0.14,1),.20),
]:
    m=bpy.data.materials.get(name)
    if m and m.use_nodes:
        bs=m.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value=color
        bs.inputs["Roughness"].default_value=rough

world=sc.world
if world:
    world.use_nodes=True
    bg=world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value=(0.075,0.10,0.15,1)
        bg.inputs["Strength"].default_value=.75

# replace/retune sun
for o in [x for x in sc.objects if x.type=='LIGHT' and x.data.type=='SUN']:
    o.data.energy=4.0
    o.rotation_euler=(math.radians(50),math.radians(-8),math.radians(-42))

# camera: reveal facade, tower and some real streets
cam=sc.camera
if cam:
    cam.location=(-95,-150,30)
    cam.data.lens=42
    target=Vector((0,-6,30))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()

sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.filepath=str(PNG)
sc.view_settings.look='AgX - Medium High Contrast'

meta={
  "build":"RathausSpandau_REAL_Integrated_Master_v4",
  "status":"current integrated Blender game master",
  "authoritative_spatial_sources":["Berlin3D 2025","LoD2","DGM terrain","OSM roads"],
  "origin_utm":[OX,OY],
  "gis_center_utm":[OE,ON],
  "transform_m":{"x":-DX,"y":DY,"z":DZ,"source_gis_y_inverted":True},
  "visible_architecture":"clean game rebuild derived from measured Berlin3D/LoD2 dimensions",
  "hidden_reference":["Rathaus_Shell_REAL.obj","Rathaus_Roof_REAL.obj"],
  "master_layer":"separate MASTER_Optical_SetDressing collection",
  "policy":"real data -> clean game geometry -> gameplay -> master look"
}
META.write_text(json.dumps(meta,indent=2),encoding='utf-8')

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
print("FINAL_MASTER_READY",OUT)
print("PREVIEW",PNG)
print("META",META)
