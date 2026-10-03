import bpy, math
from pathlib import Path
from mathutils import Vector

GIS=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1")
OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
OBJ=GIS/"Berlin3D_2025_3779_58218_-002"/"Mesh_3779_58218_-002.obj"
BLEND=OUT/"RathausSpandau_Real3D_GameMaster.blend"
PREVIEW=OUT/"RathausSpandau_Real3D_GameMaster_preview.png"

# verified Rathaus tower center in Berlin 2025 mesh
OX=377956.8271307037
OY=5822062.184676066
GROUND=31.0

# crop bounds around Rathaus + Rathausplatz / immediate streets
MINX,MAXX=377895.0,378060.0
MINY,MAXY=5821970.0,5822165.0

bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.unit_settings.system='METRIC'
sc.unit_settings.scale_length=1.0
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=1600
sc.render.resolution_y=900
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'

REF=bpy.data.collections.new("00_REAL_Berlin3D_2025")
COLL=bpy.data.collections.new("80_COLLISION")
GAME=bpy.data.collections.new("90_GAMEPLAY")
for col in (REF,COLL,GAME): sc.collection.children.link(col)

# import actual photogrammetry tile and restore native XYZ
bpy.ops.wm.obj_import(filepath=str(OBJ))
src=[o for o in bpy.context.selected_objects if o.type=='MESH']
if not src: raise RuntimeError("No mesh imported")
o=src[0]
o.rotation_euler=(0,0,0)
bpy.context.view_layer.update()

# Crop faces by polygon center in original EPSG:25833 XY
me=o.data
keep=[]
for poly in me.polygons:
    c=poly.center
    if MINX <= c.x <= MAXX and MINY <= c.y <= MAXY:
        keep.append(poly.index)

keep_set=set(keep)
# delete polygons outside crop
bpy.context.view_layer.objects.active=o
o.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
for poly in me.polygons:
    poly.select = poly.index not in keep_set
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.delete(type='FACE')
bpy.ops.object.mode_set(mode='OBJECT')

# remove loose verts/edges
bpy.context.view_layer.objects.active=o
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.delete_loose(use_verts=True,use_edges=True,use_faces=False)
bpy.ops.object.mode_set(mode='OBJECT')

# recenter Rathaus tower to local origin, ground around Z=0
o.location=(-OX,-OY,-GROUND)
o.name="RathausSpandau_REAL_2025"
for cc in list(o.users_collection): cc.objects.unlink(o)
REF.objects.link(o)

# make a duplicate for optimized engine render mesh
opt=o.copy(); opt.data=o.data.copy(); REF.objects.link(opt)
opt.name="RathausSpandau_REAL_2025_OPT"
# decimate moderately, preserve UVs/materials
dec=opt.modifiers.new("GameDecimate","DECIMATE")
dec.decimate_type='COLLAPSE'
dec.ratio=0.55
dec.use_collapse_triangulate=True
bpy.context.view_layer.objects.active=opt
opt.select_set(True)
bpy.ops.object.modifier_apply(modifier=dec.name)
opt.select_set(False)
# hide raw full crop in renders; keep as reference
o.hide_render=True
o.hide_set(True)

# materials for collision/gameplay
def mat(name,color,rough=.8):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=rough
    return m
COLMAT=mat("M_COLLISION",(0.05,0.25,0.07),.95)
COVER=mat("M_COVER",(0.12,0.13,0.14),.78)
CONC=mat("M_CONCRETE",(0.30,0.29,0.27),.88)
RED=mat("M_MARKER",(0.62,0.02,0.015),.55)

def box(name,loc,size,material,coll):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    x=bpy.context.object;x.name=name;x.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    x.data.materials.append(material)
    for cc in list(x.users_collection):cc.objects.unlink(x)
    coll.objects.link(x)
    return x

# simple collision proxies for building mass and tower.
# visuals are real mesh; these are intentionally conservative/game-friendly.
box("COL_Rathaus_Main",(12,7,14),(92,74,28),COLMAT,COLL)
box("COL_Rathaus_Tower",(0,0,39),(25,25,78),COLMAT,COLL)

# ground/plaza collision
box("COL_Rathausplatz",(-15,-58,-0.35),(150,95,.7),COLMAT,COLL)

# master gameplay cover placeholders on real plaza side
for i,(x,y,sx,sy,sz) in enumerate([
    (-30,-46,7,3.5,2.5),(-18,-50,6,3.5,2.5),(8,-52,6,3.2,2.5),
    (26,-48,8,3.5,2.8),(40,-44,8,3.5,2.8)
]):
    box(f"Cover_{i}",(x,y,sz/2),(sx,sy,sz),COVER,GAME)

box("Barrier_A",(-10,-40,1.25),(12,1.4,2.5),CONC,GAME)
box("Barrier_B",(34,-42,1.25),(13,1.4,2.5),CONC,GAME)

# camera toward real Rathaus from plaza / southwest
bpy.ops.object.camera_add(location=(-95,-135,24))
cam=bpy.context.object;cam.name="Rathaus_Real_Master_Camera";cam.data.lens=35
cam.rotation_euler=(Vector((2,0,35))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam

world=bpy.data.worlds.new("World");sc.world=world;world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.07,0.09,0.13,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.5
bpy.ops.object.light_add(type='SUN',location=(-120,-120,180))
sun=bpy.context.object;sun.data.energy=3.2;sun.rotation_euler=(math.radians(45),0,math.radians(-50))

sc.view_settings.look='AgX - Medium High Contrast'
sc.render.filepath=str(PREVIEW)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)

# stats
print("REAL3D_GAMEMASTER_READY",BLEND)
print("PREVIEW",PREVIEW)
print("RAW_POLYS",len(o.data.polygons),"OPT_POLYS",len(opt.data.polygons))
