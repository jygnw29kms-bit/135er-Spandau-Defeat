import bpy, math
from pathlib import Path
from mathutils import Vector
OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BLEND=OUT/"RathausSpandau_Real3D_GameMaster.blend"
PNG=OUT/"RathausSpandau_REAL_2025_clean_west.png"
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
sc=bpy.context.scene
for cname in ("80_COLLISION","90_GAMEPLAY"):
    col=bpy.data.collections.get(cname)
    if col:
        col.hide_render=True
        for o in col.objects:o.hide_render=True
raw=bpy.data.objects.get("RathausSpandau_REAL_2025")
if raw: raw.hide_render=True
opt=bpy.data.objects.get("RathausSpandau_REAL_2025_OPT")
if opt:
    opt.hide_render=False
    opt.hide_set(False)
cam=bpy.data.objects.get("Rathaus_Real_Master_Camera")
cam.location=(-125,-20,28)
cam.data.lens=38
cam.rotation_euler=(Vector((0,2,34))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam
sun=bpy.data.objects.get("Sun")
if sun:
    sun.data.energy=3.5
    sun.rotation_euler=(math.radians(48),math.radians(-10),math.radians(-65))
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.filepath=str(PNG)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
bpy.ops.render.render(write_still=True)
print("CLEAN_REAL_RENDER",PNG)
