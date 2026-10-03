import bpy, math
from pathlib import Path
from mathutils import Matrix

BLEND=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\RathausSpandau_Master.blend")
OUT=Path(r"E:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\content\csgo_addons\spandau_defeat\models\rathaus\rathaus_spandau_collision_source.fbx")
CX,CY=100.850,2.896
ANG=math.radians(-37.4256)

bpy.ops.wm.open_mainfile(filepath=str(BLEND))
COL=bpy.data.collections["90_Rathaus_Collision"]
bpy.ops.object.select_all(action='DESELECT')
src=list(COL.objects)
for o in src:o.select_set(True)
bpy.context.view_layer.objects.active=src[0]
bpy.ops.object.duplicate()
dups=list(bpy.context.selected_objects)

to_local=Matrix.Rotation(-ANG,4,'Z') @ Matrix.Translation((-CX,-CY,0))
for i,o in enumerate(dups):
    o.name=f"Rathaus_Collision_{i:02d}"
    o.matrix_world=to_local @ o.matrix_world

bpy.ops.export_scene.fbx(filepath=str(OUT),use_selection=True,
    apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',
    add_leaf_bones=False,bake_anim=False)
print("COLLISION_SOURCE_READY",OUT,"HULLS",len(dups))
