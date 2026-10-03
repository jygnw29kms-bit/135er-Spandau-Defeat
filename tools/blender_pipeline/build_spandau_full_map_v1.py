import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
GIS=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1")
BASE=ROOT/"RathausSpandau_MASTER_Scene_v10.blend"
OUT=ROOT/"SpandauStrike_Rathaus_FULLMAP_v1.blend"
PNG=ROOT/"SpandauStrike_Rathaus_FULLMAP_v1_overview.png"
META=ROOT/"SpandauStrike_Rathaus_FULLMAP_v1.json"

bpy.ops.wm.open_mainfile(filepath=str(BASE))
sc=bpy.context.scene

# authoritative center used by current Rathaus rebuild
CX,CY=377931.576,5822067.058
OE,ON=377897.8969272321,5822086.91786854
BASELINE,GROUND=33.45,31.0
DX=CX-OE
DY=ON-CY

ENV=bpy.data.collections.get("FULLMAP_Environment") or bpy.data.collections.new("FULLMAP_Environment")
if ENV.name not in sc.collection.children:sc.collection.children.link(ENV)
COL=bpy.data.collections.get("FULLMAP_Collision") or bpy.data.collections.new("FULLMAP_Collision")
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
GAME=bpy.data.collections.get("FULLMAP_Gameplay") or bpy.data.collections.new("FULLMAP_Gameplay")
if GAME.name not in sc.collection.children:sc.collection.children.link(GAME)

def move(o,col):
    for cc in list(o.users_collection):cc.objects.unlink(o)
    col.objects.link(o);return o

def mat(name,color,rough=.6,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    bs.inputs["Metallic"].default_value=metal
    return m

BUILD=mat("M_FullMap_Building",(0.22,0.20,0.18),.75)
WATER=mat("M_FullMap_Water",(0.025,0.09,0.12),.12,.05)
BOUND=mat("M_FullMap_Boundary",(0.03,0.03,0.035),.85)
SPAWN_W=mat("M_Spawn_West",(0.07,0.22,0.55),.5)
SPAWN_E=mat("M_Spawn_East",(0.55,0.12,0.08),.5)

def import_obj(path,name,material):
    bpy.ops.wm.obj_import(filepath=str(path))
    objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
    for i,o in enumerate(objs):
        o.name=name if len(objs)==1 else f"{name}_{i}"
        o.rotation_euler=(0,0,0)
        o.data.materials.clear();o.data.materials.append(material)
        move(o,ENV)
        # GIS assets are cm, Y inverted
        o.scale=(.01,-.01,.01)
        o.location=(-DX,DY,BASELINE-GROUND)
        bpy.context.view_layer.objects.active=o;o.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.select_set(False)
    return objs

# Surrounding building massing + water.
# Roads and terrain are already present in v10.
buildings=import_obj(GIS/"rathaus_buildings_no_landmark.obj","FULLMAP_SurroundingBuildings",BUILD)
water=import_obj(GIS/"rathaus_water.obj","FULLMAP_Water",WATER)

# 1 km map boundary
def box(name,x,y,z,sx,sy,sz,material,col):
    bpy.ops.mesh.primitive_cube_add(location=(x,y,z))
    o=bpy.context.object;o.name=name;o.dimensions=(sx,sy,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    return move(o,col)

half=500.0
wall_h=18.0
box("MAPBOUND_N",0,half,wall_h/2,1000,2,wall_h,BOUND,COL)
box("MAPBOUND_S",0,-half,wall_h/2,1000,2,wall_h,BOUND,COL)
box("MAPBOUND_E",half,0,wall_h/2,2,1000,wall_h,BOUND,COL)
box("MAPBOUND_W",-half,0,wall_h/2,2,1000,wall_h,BOUND,COL)

# spawn markers from prepared safe-spawn data (cm -> m), shifted from GIS center to Rathaus center.
sp=json.loads((GIS/"safe_spawns.json").read_text())
def spawn_marker(name,p,material):
    x_cm,y_cm,z_cm=p
    # source is local to GIS center in cm and same engine axes: x east, y south/inverted
    x=x_cm/100.0-DX
    y=-(y_cm/100.0)+DY
    z=z_cm/100.0+(BASELINE-GROUND)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=2.0,depth=.35,location=(x,y,z+.18))
    o=bpy.context.object;o.name=name;o.data.materials.append(material);move(o,GAME)
    return [x,y,z]
spawn_out={"west":[],"east":[]}
for side,material in (("west",SPAWN_W),("east",SPAWN_E)):
    for i,p in enumerate(sp.get(side,[])):
        spawn_out[side].append(spawn_marker(f"SPAWN_{side.upper()}_{i+1}",p,material))

# gameplay zones: Rathaus plaza objective + two side approaches
OBJ_A=mat("M_Objective_A",(0.55,0.03,0.02),.45)
OBJ_B=mat("M_Objective_B",(0.75,0.42,0.02),.45)
def zone(name,x,y,z,sx,sy,material):
    o=box(name,x,y,z,sx,sy,.08,material,GAME)
    return [x,y,z,sx,sy]
objectives=[
    zone("OBJECTIVE_A",-18,-68,.08,24,18,OBJ_A),
    zone("OBJECTIVE_B",32,-66,.08,24,18,OBJ_B),
]

# collision proxies for Rathaus mass + major plaza obstructions
box("COL_Rathaus_Main",0,8,10.5,112,70,21,BOUND,COL)
box("COL_Rathaus_Tower",0,5,41,14.5,15.5,82,BOUND,COL)

# hide collision objects in normal render/view
for o in COL.objects:
    o.hide_render=True
    o.display_type='WIRE'

# overview camera
cam=sc.camera
cam.location=(0,-720,520)
cam.data.lens=48
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.filepath=str(PNG)
sc.view_settings.exposure=.1

META.write_text(json.dumps({
 "build":"SpandauStrike_Rathaus_FULLMAP_v1",
 "map_extent_m":[1000,1000],
 "source_summary":json.loads((GIS/"summary.json").read_text()),
 "surrounding_building_objects":len(buildings),
 "water_objects":len(water),
 "spawn_markers":spawn_out,
 "objectives":objectives,
 "layers":["Rathaus master scene v10","terrain","roads","1717 surrounding buildings","water","spawn markers","objectives","boundary/collision"],
 "status":"full-map modeling candidate"
},indent=2),encoding="utf-8")

bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
bpy.ops.render.render(write_still=True)
print("FULLMAP_READY",OUT)
print("OVERVIEW",PNG)
print("BUILDING_OBJECTS",len(buildings),"WATER_OBJECTS",len(water))
