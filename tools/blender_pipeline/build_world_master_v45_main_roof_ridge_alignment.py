import bpy
import json
import math
import os
from mathutils import Vector

EXPECTED_SOURCE_VERSION = "v44_CROWN_OPENING_DEPTH"
OUTPUT_VERSION = "v45_MAIN_ROOF_RIDGE_ALIGNMENT"
ROOF_NAME = "SM_MainRoof"

source_path = os.path.abspath(bpy.data.filepath)
source_dir = os.path.dirname(source_path)
OUT_BLEND = os.path.join(
    source_dir,
    "SpandauStrike_Rathaus_WORLD_MASTER_v45_MAIN_ROOF_RIDGE_ALIGNMENT.blend",
)
OUT_REPORT = os.path.splitext(OUT_BLEND)[0] + "_REPORT.json"

source_version = str(bpy.context.scene.get("ss_master_version", ""))
if source_version != EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f"Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}")

roof = bpy.data.objects.get(ROOF_NAME)
if not roof or roof.type != "MESH":
    raise RuntimeError(f"Missing mesh {ROOF_NAME}")
if roof.get("ss_export") is not True or roof.get("ss_role") != "production":
    raise RuntimeError(f"Unexpected metadata on {ROOF_NAME}")
if len(roof.data.vertices) != 10 or len(roof.data.polygons) != 9:
    raise RuntimeError(f"Unexpected {ROOF_NAME} topology")
if roof.data.users != 1:
    raise RuntimeError(f"{ROOF_NAME} mesh data is shared by {roof.data.users} objects")

v = roof.data.vertices
old_ridge = [v[8].co.copy(), v[9].co.copy()]
end_a = (v[4].co + v[7].co) * 0.5
end_b = (v[5].co + v[6].co) * 0.5
old_z = (old_ridge[0].z + old_ridge[1].z) * 0.5
end_a.z = old_z
end_b.z = old_z

long_edge = v[5].co - v[4].co
short_edge = v[7].co - v[4].co
old_vec = old_ridge[1] - old_ridge[0]
new_vec = end_b - end_a

def angle_deg(a: Vector, b: Vector) -> float:
    if a.length == 0 or b.length == 0:
        return 0.0
    return math.degrees(a.angle(b))

if not (105.0 < long_edge.length < 120.0 and 50.0 < short_edge.length < 58.0):
    raise RuntimeError(
        f"Unexpected main-roof footprint: long={long_edge.length:.3f}, short={short_edge.length:.3f}"
    )
if angle_deg(old_vec, short_edge) > 1.0 and abs(angle_deg(old_vec, short_edge) - 180.0) > 1.0:
    raise RuntimeError("Existing ridge is not aligned to the short axis as expected")

v[8].co = end_a
v[9].co = end_b
roof.data.update()
bpy.context.view_layer.update()

roof["ss_revision"] = OUTPUT_VERSION
roof["ss_v45_change"] = "Realigned main roof ridge from transverse to longitudinal facade axis"
roof["ss_tag"] = "rathaus_v45_main_roof_ridge_alignment"
bpy.context.scene["ss_master_version"] = OUTPUT_VERSION
bpy.context.scene["ss_v45_change"] = (
    "Realigned the two SM_MainRoof ridge vertices to the longitudinal roof axis; topology unchanged"
)

new_world_ridge = [roof.matrix_world @ v[8].co, roof.matrix_world @ v[9].co]
report = {
    "schema": "SpandauStrike.WorldMasterV45MainRoofRidgeAlignment.v1",
    "source_master": os.path.basename(source_path),
    "source_master_version": EXPECTED_SOURCE_VERSION,
    "output_master": os.path.basename(OUT_BLEND),
    "output_master_version": OUTPUT_VERSION,
    "object": ROOF_NAME,
    "topology": {"vertices": len(v), "polygons": len(roof.data.polygons)},
    "footprint_m": {
        "long_edge": float(long_edge.length),
        "short_edge": float(short_edge.length),
    },
    "old_ridge_local_m": [[float(x) for x in p] for p in old_ridge],
    "new_ridge_local_m": [[float(x) for x in v[i].co] for i in (8, 9)],
    "new_ridge_world_m": [[float(x) for x in p] for p in new_world_ridge],
    "ridge_length_before_m": float(old_vec.length),
    "ridge_length_after_m": float(new_vec.length),
    "old_ridge_vs_long_axis_deg": float(angle_deg(old_vec, long_edge)),
    "new_ridge_vs_long_axis_deg": float(min(angle_deg(new_vec, long_edge), 180.0 - angle_deg(new_vec, long_edge))),
    "policy": "Two-vertex geometry correction only. No topology, materials, facade, tower, gameplay or collision changes.",
}

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("V45_OUT=" + OUT_BLEND)
print("V45_REPORT=" + OUT_REPORT)
print(json.dumps(report, ensure_ascii=False))
