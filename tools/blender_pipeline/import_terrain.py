import bpy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MASTER=ROOT/"SpandauStrike_Master.blend"
OBJ=ROOT/"output"/"master"/"falkenhagener_feld_DGM1_4m.obj"
UE=ROOT/"output"/"ue5"/"falkenhagener_feld_DGM1_4m_UE5.fbx"

bpy.ops.wm.open_mainfile(filepath=str(MASTER))
terrain_col=bpy.data.collections.get("10_TERRAIN")
for o in list(terrain_col.objects):
    bpy.data.objects.remove(o, do_unlink=True)

before=set(bpy.data.objects)
bpy.ops.wm.obj_import(filepath=str(OBJ))
new=[o for o in bpy.data.objects if o not in before and o.type=="MESH"]
if not new:
    raise RuntimeError("Terrain OBJ import failed")
terrain=new[0]
terrain.name="Terrain_FalkenhagenerFeld_DGM1_4m"
for col in list(terrain.users_collection):
    col.objects.unlink(terrain)
terrain_col.objects.link(terrain)

mat=bpy.data.materials.get("M_TerrainPreview") or bpy.data.materials.new("M_TerrainPreview")
mat.diffuse_color=(0.18,0.32,0.12,1.0)
if not terrain.data.materials:
    terrain.data.materials.append(mat)

bpy.context.view_layer.objects.active=terrain
terrain.select_set(True)
bpy.ops.object.shade_smooth_by_angle()

tri=terrain.modifiers.new("Triangulate","TRIANGULATE")
tri.keep_custom_normals=True

bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))

bpy.ops.object.select_all(action="DESELECT")
terrain.select_set(True)
bpy.context.view_layer.objects.active=terrain
bpy.ops.export_scene.fbx(filepath=str(UE),use_selection=True,apply_unit_scale=True,
    object_types={'MESH'},add_leaf_bones=False,axis_forward='-Z',axis_up='Y')
bpy.ops.wm.save_as_mainfile(filepath=str(MASTER))
print("TERRAIN_IMPORT_OK",len(terrain.data.vertices),len(terrain.data.polygons))
