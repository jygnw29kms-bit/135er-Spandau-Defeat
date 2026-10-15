import bpy
import json
import os
from pathlib import Path

EXPECTED_VERSION="v51_PEDIMENT_READABILITY"
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"ue5"/"SpandauStrike"/"SourceArt"/"Rathaus"/"v51"
OUT.mkdir(parents=True,exist_ok=True)
FBX=OUT/"RathausSpandau_BUILDING_v51.fbx"
AUDIT=OUT/"RathausSpandau_BUILDING_v51_export.json"

if str(bpy.context.scene.get("ss_master_version","")) != EXPECTED_VERSION:
    raise RuntimeError(f"Expected {EXPECTED_VERSION}, got {bpy.context.scene.get('ss_master_version')}")

full_collections={
    "REAL_Rebuilt_Architecture",
    "RATHAUS_RECOVERED_ENTRANCE_STEPS",
    "PRODUCTION_FINISH",
    "PRODUCTION_RATHAUS_V24_PROFILE",
    "PRODUCTION_RATHAUS_V25_ACCURACY",
    "PRODUCTION_RATHAUS_V26_CLEAN",
    "PRODUCTION_RATHAUS_V31_FENESTRATION",
    "PRODUCTION_RATHAUS_V32_TOWER",
    "PRODUCTION_RATHAUS_V33_HISTORIC",
    "PRODUCTION_RATHAUS_V34_RELIEF_FIX",
    "PRODUCTION_RATHAUS_V37_TOWER",
}
production_model_prefixes=(
    "P_ProfileA_","P_ProfileB_","P_ProfileC_",
    "P_Dormer","P_Handle_","P_TransomGlass_",
)

def eligible(o):
    if o.type not in {"MESH","CURVE","FONT"}: return False
    if not bool(o.get("ss_export")): return False
    if o.get("ss_role") not in {"production","landmark"}: return False
    cols={c.name for c in o.users_collection}
    if cols & full_collections: return True
    if "PRODUCTION_MODELS" in cols and o.name.startswith(production_model_prefixes): return True
    return False

src=[o for o in bpy.context.scene.objects if eligible(o)]
if not src: raise RuntimeError("No Rathaus building objects selected")
source_names=sorted(o.name for o in src)
source_poly=sum(len(o.data.polygons) for o in src if o.type=="MESH")
source_vert=sum(len(o.data.vertices) for o in src if o.type=="MESH")

bpy.ops.object.select_all(action="DESELECT")
for o in src:
    o.hide_viewport=False; o.hide_render=False; o.select_set(True)
bpy.context.view_layer.objects.active=src[0]
bpy.ops.object.duplicate()
dups=list(bpy.context.selected_objects)
# Convert curves/text to evaluated mesh while preserving world transforms.
for o in list(dups):
    bpy.context.view_layer.objects.active=o
    o.select_set(True)
bpy.ops.object.convert(target="MESH")
dups=list(bpy.context.selected_objects)
if not dups: raise RuntimeError("Duplicate conversion produced no meshes")
bpy.context.view_layer.objects.active=dups[0]
bpy.ops.object.join()
joined=bpy.context.object
joined.name="RathausSpandau_BUILDING_v51"
# Put FBX object origin at authoritative world origin without moving geometry.
bpy.context.scene.cursor.location=(0.0,0.0,0.0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
joined["ss_source_master"]=EXPECTED_VERSION
joined["ss_export_role"]="rathaus_building"

# Bounds in Blender metres.
coords=[]
for c in joined.bound_box:
    w=joined.matrix_world @ __import__('mathutils').Vector(c)
    coords.append(tuple(w))
mins=[min(p[i] for p in coords) for i in range(3)]
maxs=[max(p[i] for p in coords) for i in range(3)]
size=[maxs[i]-mins[i] for i in range(3)]

bpy.ops.object.select_all(action="DESELECT"); joined.select_set(True); bpy.context.view_layer.objects.active=joined
bpy.ops.export_scene.fbx(
    filepath=str(FBX),
    use_selection=True,
    apply_scale_options="FBX_SCALE_ALL",
    axis_forward="-Y",
    axis_up="Z",
    add_leaf_bones=False,
    bake_anim=False,
    object_types={"MESH"},
)
report={
    "schema":"SpandauStrike.RathausBuildingUEExport.v1",
    "source_master":os.path.basename(bpy.data.filepath),
    "source_master_version":EXPECTED_VERSION,
    "fbx":str(FBX.relative_to(ROOT)).replace("\\","/"),
    "source_object_count":len(src),
    "source_vertices_mesh_only":source_vert,
    "source_polygons_mesh_only":source_poly,
    "joined_vertices":len(joined.data.vertices),
    "joined_polygons":len(joined.data.polygons),
    "material_slots":len(joined.material_slots),
    "bounds_min_m":mins,
    "bounds_max_m":maxs,
    "bounds_size_m":size,
    "selection_collections":sorted(full_collections),
    "production_model_prefixes":list(production_model_prefixes),
    "source_objects":source_names,
}
AUDIT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({k:report[k] for k in ["source_object_count","joined_vertices","joined_polygons","material_slots","bounds_size_m"]},ensure_ascii=False))
print("FBX="+str(FBX))
print("AUDIT="+str(AUDIT))
