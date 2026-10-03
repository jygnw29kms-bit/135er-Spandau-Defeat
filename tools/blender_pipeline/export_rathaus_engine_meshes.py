import bpy, math
from pathlib import Path
BLEND=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\RathausSpandau_Master.blend")
OUT=BLEND.parent/"engine"
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
ARCH=bpy.data.collections["10_Rathaus_Architecture"]
DETAIL=bpy.data.collections["20_Rathaus_Detail"]

# duplicate visible landmark objects, convert modifiers/text, join to one mesh
bpy.ops.object.select_all(action='DESELECT')
src=[o for c in (ARCH,DETAIL) for o in c.objects if o.type in {'MESH','FONT'}]
for o in src:o.select_set(True)
bpy.context.view_layer.objects.active=src[0]
bpy.ops.object.duplicate()
dups=list(bpy.context.selected_objects)
for o in dups:o.hide_render=False;o.hide_viewport=False
bpy.ops.object.convert(target='MESH')
dups=list(bpy.context.selected_objects)
bpy.context.view_layer.objects.active=dups[0]
bpy.ops.object.join()
lod0=bpy.context.object
lod0.name="Rathaus_Landmark_LOD0"
bpy.context.scene.cursor.location=(0,0,0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

# Apply transforms while preserving world-aligned geometry
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
print("LOD0_VERTS",len(lod0.data.vertices),"POLYS",len(lod0.data.polygons),"MATS",len(lod0.data.materials))

# export LOD0 OBJ for Source conversion
bpy.ops.object.select_all(action='DESELECT');lod0.select_set(True);bpy.context.view_layer.objects.active=lod0
bpy.ops.wm.obj_export(filepath=str(OUT/"RathausSpandau_Landmark_LOD0.obj"),export_selected_objects=True,forward_axis='NEGATIVE_Z',up_axis='Y')
bpy.ops.export_scene.fbx(filepath=str(OUT/"RathausSpandau_Landmark_LOD0.fbx"),use_selection=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z')

# LOD1
lod1=lod0.copy();lod1.data=lod0.data.copy();bpy.context.collection.objects.link(lod1);lod1.name="Rathaus_Landmark_LOD1"
bpy.ops.object.select_all(action='DESELECT');lod1.select_set(True);bpy.context.view_layer.objects.active=lod1
dec=lod1.modifiers.new("LOD1_Decimate",'DECIMATE');dec.ratio=.42;dec.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier=dec.name)
bpy.ops.export_scene.fbx(filepath=str(OUT/"RathausSpandau_Landmark_LOD1.fbx"),use_selection=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z')
print("LOD1_VERTS",len(lod1.data.vertices),"POLYS",len(lod1.data.polygons))

# LOD2
lod2=lod0.copy();lod2.data=lod0.data.copy();bpy.context.collection.objects.link(lod2);lod2.name="Rathaus_Landmark_LOD2"
bpy.ops.object.select_all(action='DESELECT');lod2.select_set(True);bpy.context.view_layer.objects.active=lod2
dec=lod2.modifiers.new("LOD2_Decimate",'DECIMATE');dec.ratio=.16;dec.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier=dec.name)
bpy.ops.export_scene.fbx(filepath=str(OUT/"RathausSpandau_Landmark_LOD2.fbx"),use_selection=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z')
print("LOD2_VERTS",len(lod2.data.vertices),"POLYS",len(lod2.data.polygons))

# collision FBX from existing collision collection plus accurate wing proxies
for o in (lod0,lod1,lod2):o.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT')
COL=bpy.data.collections["90_Rathaus_Collision"]
for i,o in enumerate(COL.objects):
    o.hide_viewport=False
    o.name=f"UCX_Rathaus_Landmark_LOD0_{i:02d}"
    o.select_set(True)
if COL.objects:
    bpy.context.view_layer.objects.active=COL.objects[0]
    bpy.ops.export_scene.fbx(filepath=str(OUT/"RathausSpandau_Collision.fbx"),use_selection=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z')
print("ENGINE_EXPORT_READY",OUT)

