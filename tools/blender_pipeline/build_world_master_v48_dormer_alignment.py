import bpy
import json
import math
import os
from mathutils import Vector, Matrix

EXPECTED_SOURCE_VERSION = "v47_CROWN_GUARDRAILS"
OUTPUT_VERSION = "v48_DORMER_ALIGNMENT"
P_INDICES = [0, 1, 2, 3, 4, 8, 9, 10, 11, 12]
FACADE_DEG = 47.5
ROOF_SLOPE_DEG = 29.0

source_path = os.path.abspath(bpy.data.filepath)
source_dir = os.path.dirname(source_path)
OUT_BLEND = os.path.join(source_dir, "SpandauStrike_Rathaus_WORLD_MASTER_v48_DORMER_ALIGNMENT.blend")
OUT_REPORT = os.path.splitext(OUT_BLEND)[0] + "_REPORT.json"

source_version = str(bpy.context.scene.get("ss_master_version", ""))
if source_version != EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f"Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}")

angle = math.radians(FACADE_DEG)
rot_z = Matrix.Rotation(angle, 4, 'Z')
changed = []
anchors = []

for v16_index, p_index in enumerate(P_INDICES):
    pivot = bpy.data.objects.get(f"P_DormerBody_Dormer_{p_index}")
    target = bpy.data.objects.get(f"V16_DormerFrontBody_{v16_index}")
    if pivot is None or target is None:
        raise RuntimeError(f"Missing dormer anchor P={p_index} V16={v16_index}")

    old_pivot = Vector(pivot.location)
    new_pivot = Vector(target.location)
    group = [
        obj for obj in bpy.data.objects
        if obj.name.startswith("P_Dormer") and obj.name.endswith(f"_Dormer_{p_index}")
    ]
    if not group:
        raise RuntimeError(f"No production dormer group found for index {p_index}")

    anchors.append({
        "production_index": p_index,
        "reference_index": v16_index,
        "old_anchor": list(old_pivot),
        "new_anchor": list(new_pivot),
        "translation": list(new_pivot - old_pivot),
        "group_object_count": len(group),
    })

    for obj in group:
        before_loc = Vector(obj.location)
        before_rot = tuple(obj.rotation_euler)
        relative = before_loc - old_pivot
        obj.location = new_pivot + (rot_z @ relative)
        obj.rotation_euler.z += angle
        obj["ss_revision"] = OUTPUT_VERSION
        obj["ss_reference_basis"] = "media/theme/rathaus-spandau-photo.jpg; V16_DormerFront anchors"
        obj["ss_tag"] = "rathaus_front_dormer_aligned"
        changed.append({
            "name": obj.name,
            "before_location": list(before_loc),
            "after_location": list(obj.location),
            "before_rotation_rad": list(before_rot),
            "after_rotation_rad": list(obj.rotation_euler),
        })

    roof_l = bpy.data.objects.get(f"P_DormerRoofL_Dormer_{p_index}")
    roof_r = bpy.data.objects.get(f"P_DormerRoofR_Dormer_{p_index}")
    if roof_l is None or roof_r is None:
        raise RuntimeError(f"Missing roof pair for production dormer {p_index}")
    roof_l.rotation_euler.y = math.radians(-ROOF_SLOPE_DEG)
    roof_r.rotation_euler.y = math.radians(ROOF_SLOPE_DEG)

bpy.context.scene["ss_master_version"] = OUTPUT_VERSION
bpy.context.scene["ss_v48_change"] = (
    "Aligned ten existing detailed front dormer groups to the verified 47.5-degree facade axis and "
    "V16 front-dormer anchors; corrected left/right roof pitch signs to form upward gables. "
    "No mesh topology, gameplay, collision, route, objective, spawn or cover geometry changed."
)

report = {
    "schema": "SpandauStrike.WorldMasterV48DormerAlignment.v1",
    "source_master": os.path.basename(source_path),
    "source_master_version": EXPECTED_SOURCE_VERSION,
    "output_master": os.path.basename(OUT_BLEND),
    "output_master_version": OUTPUT_VERSION,
    "reference": "media/theme/rathaus-spandau-photo.jpg",
    "facade_alignment_deg": FACADE_DEG,
    "roof_pitch_deg": {"left": -ROOF_SLOPE_DEG, "right": ROOF_SLOPE_DEG},
    "dormer_groups": len(P_INDICES),
    "changed_object_count": len(changed),
    "anchors": anchors,
    "changed_objects": changed,
    "policy": "Transform-only correction of existing production dormer objects. Topology and gameplay/collision objects are unchanged."
}

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("V48_OUT=" + OUT_BLEND)
print("V48_REPORT=" + OUT_REPORT)
print(json.dumps({"groups": len(P_INDICES), "changed_objects": len(changed)}, ensure_ascii=False))