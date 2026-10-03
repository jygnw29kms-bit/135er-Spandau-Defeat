import bpy, math
from pathlib import Path
from mathutils import Vector

BLEND=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\RathausSpandau_Master.blend")
OUT=Path(r"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\content\csgo_addons\spandau_defeat\models\rathaus")
OUT.mkdir(parents=True,exist_ok=True)
FBX=OUT/"rathaus_spandau_source.fbx"

bpy.ops.wm.open_mainfile(filepath=str(BLEND))
ARCH=bpy.data.collections["10_Rathaus_Architecture"]
DETAIL=bpy.data.collections["20_Rathaus_Detail"]
CX,CY=100.850,2.896
ANG=math.radians(-37.4256)

bpy.ops.object.select_all(action='DESELECT')
src=[o for c in (ARCH,DETAIL) for o in c.objects if o.type in {'MESH','FONT'}]
for o in src:o.select_set(True)
bpy.context.view_layer.objects.active=src[0]
bpy.ops.object.duplicate()
bpy.ops.object.convert(target='MESH')
dups=list(bpy.context.selected_objects)
bpy.context.view_layer.objects.active=dups[0]
bpy.ops.object.join()
o=bpy.context.object
o.name="RathausSpandau_Source"

# Source 2 material names must be valid resource paths already inside the FBX.
mat_paths={
    "M_Rathaus_Stone":"materials/rathaus/rathaus_stone",
    "M_Rathaus_Trim":"materials/rathaus/rathaus_trim",
    "M_Rathaus_RedTile":"materials/rathaus/rathaus_roof",
    "M_Rathaus_Copper":"materials/rathaus/rathaus_copper",
    "M_Rathaus_Glass":"materials/rathaus/rathaus_glass",
    "M_Rathaus_Door":"materials/rathaus/rathaus_door",
    "M_Rathaus_ClockGold":"materials/rathaus/rathaus_gold",
    "M_Rathaus_StoneSteps":"materials/rathaus/rathaus_steps",
}
for slot in o.material_slots:
    if slot.material:
        base=slot.material.name.split(".")[0]
        if base in mat_paths:
            m=slot.material.copy()
            m.name=mat_paths[base]
            slot.material=m

# bake object transform, then convert world-aligned geometry into Rathaus-local XY
# Bake the joined object's complete transform so vertex coordinates are true world coordinates.
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)

ca,sa=math.cos(ANG),math.sin(ANG)
for v in o.data.vertices:
    x,y,z=v.co.x,v.co.y,v.co.z
    dx=x-CX; dy=y-CY
    lx= ca*dx + sa*dy
    ly=-sa*dx + ca*dy
    v.co=(lx,ly,z)

# source will use ModelDoc import_scale 0.4064: 39.37 in/m -> 16 map units/m
bpy.ops.object.select_all(action='DESELECT')
o.select_set(True)
bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,
    apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',
    add_leaf_bones=False,bake_anim=False)
xs=[v.co.x for v in o.data.vertices];ys=[v.co.y for v in o.data.vertices];zs=[v.co.z for v in o.data.vertices]
print("SOURCE_LOCAL_READY",FBX)
print("BOUNDS_M",min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
print("VERTS",len(o.data.vertices),"POLYS",len(o.data.polygons))
