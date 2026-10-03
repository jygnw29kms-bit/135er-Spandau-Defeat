import bpy, math
from pathlib import Path
from mathutils import Vector

GIS=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1")
OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
OBJ_W=GIS/"Berlin3D_2025_3775_58218_-002"/"Mesh_3775_58218_-002.obj"
OBJ_E=GIS/"Berlin3D_2025_3779_58218_-002"/"Mesh_3779_58218_-002.obj"
BLEND=OUT/"RathausSpandau_Berlin3D_2025_Master.blend"
PREVIEW=OUT/"RathausSpandau_Berlin3D_2025_preview.png"

# Verified tower center from 2025 mesh high-vertex cluster
OX=377956.8271307037
OY=5822062.184676066
OZ=31.0

bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.unit_settings.system='METRIC'
sc.unit_settings.scale_length=1.0
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=1600
sc.render.resolution_y=900
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'

COL_REAL=bpy.data.collections.new("00_Berlin3D_2025_RealMesh")
COL_GAME=bpy.data.collections.new("10_Gameplay_Overlay")
COL_REF=bpy.data.collections.new("99_Reference")
for cc in (COL_REAL,COL_GAME,COL_REF):
    sc.collection.children.link(cc)

def move_to(o,coll):
    for cc in list(o.users_collection): cc.objects.unlink(o)
    coll.objects.link(o)

def import_tile(path,name):
    bpy.ops.wm.obj_import(filepath=str(path))
    objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
    for o in objs:
        # OBJ importer adds +90° X by default; neutralize to recover EPSG:25833 XYZ
        o.rotation_euler=(0,0,0)
        o.name=name
        # recenter entire tile around Rathaus tower
        o.location=(-OX,-OY,-OZ)
        move_to(o,COL_REAL)
    return objs

west=import_tile(OBJ_W,"Berlin3D_West_2025")
east=import_tile(OBJ_E,"Berlin3D_East_2025")

# Remove east-side overlap from west tile to avoid z-fighting.
# Boundary chosen midway through the ~28 m overlap.
cut_x=377936.5-OX
for o in west:
    me=o.data
    # mark vertices east of cut for deletion
    bpy.context.view_layer.objects.active=o
    o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in me.vertices:
        # local coords are still absolute EPSG; object translation recenters on display
        if v.co.x > 377936.5:
            v.select=True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    o.select_set(False)

# Reference origin marker
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.6,depth=4,location=(0,0,2))
origin=bpy.context.object
origin.name="Rathaus_Tower_Origin"
move_to(origin,COL_REF)
origin.hide_render=True

# Simple gameplay overlay materials
def mat(name,color,rough=.6):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return m
RED=mat("M_Gameplay_Red",(0.55,.02,.015),.5)
DARK=mat("M_Gameplay_Cover",(.10,.11,.12),.75)
CONC=mat("M_Gameplay_Concrete",(.30,.29,.27),.85)

def box(name,loc,size,material):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material);move_to(o,COL_GAME)
    return o

# Keep gameplay placeholders spatially separate and easy to edit;
# real city geometry remains untouched.
for i,(x,y) in enumerate([(-18,-35),(12,-38),(32,-44),(-40,-30)]):
    box(f"Cover_{i}",(x,y,1.25),(6,3.2,2.5),DARK)
for i,(x,y,w) in enumerate([(-8,-28,12),(38,-36,14)]):
    box(f"Barrier_{i}",(x,y,1.1),(w,1.2,2.2),CONC)

# Camera: southwest looking toward Rathaus tower, roughly optical-master composition
bpy.ops.object.camera_add(location=(-125,-160,32))
cam=bpy.context.object
cam.name="Rathaus_Master_Camera"
cam.data.lens=35
cam.rotation_euler=(Vector((0,0,34))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam

# Daylight
world=bpy.data.worlds.new("World");sc.world=world;world.use_nodes=True
bg=world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value=(0.055,0.075,0.11,1)
bg.inputs["Strength"].default_value=.55
bpy.ops.object.light_add(type='SUN',location=(-120,-160,180))
sun=bpy.context.object;sun.name="Sun";sun.data.energy=3.0
sun.rotation_euler=(math.radians(42),math.radians(-8),math.radians(-45))

sc.view_settings.look='AgX - Medium High Contrast'
sc.render.filepath=str(PREVIEW)

# Save first, then render
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)
print("BERLIN3D_MASTER_READY",BLEND)
print("PREVIEW",PREVIEW)
print("ORIGIN_UTM",OX,OY,OZ)
