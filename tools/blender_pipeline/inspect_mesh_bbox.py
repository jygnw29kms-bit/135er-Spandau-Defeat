import bpy
from pathlib import Path
OBJ=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\Berlin3D_2025_3775_58218_-002\Mesh_3775_58218_-002.obj")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=str(OBJ))
for o in bpy.context.selected_objects:
    if o.type=='MESH':
        pts=[o.matrix_world @ v.co for v in o.data.vertices]
        xs=[p.x for p in pts];ys=[p.y for p in pts];zs=[p.z for p in pts]
        print('OBJ',o.name,'MIN',min(xs),min(ys),min(zs),'MAX',max(xs),max(ys),max(zs),'LOC',o.location[:],'ROT',o.rotation_euler[:])
