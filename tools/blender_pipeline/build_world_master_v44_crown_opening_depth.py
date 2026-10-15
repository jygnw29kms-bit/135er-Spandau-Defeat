import bpy
import json
import os
from mathutils import Vector

OUT_BLEND = r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v44_CROWN_OPENING_DEPTH.blend"
OUT_REPORT = os.path.splitext(OUT_BLEND)[0] + "_REPORT.json"
EXPECTED_SOURCE_VERSION = "v43_RECOVERED_ENTRANCE_STEPS"
ANCHOR_NAME = "SM_TowerTopCornice"
OPENINGS = [
    "V37_CrownOpeningFront",
    "V37_CrownOpeningRear",
    "V37_CrownOpeningEast",
    "V37_CrownOpeningWest",
]
RECESS_M = 1.35

source_version = str(bpy.context.scene.get("ss_master_version", ""))
if source_version != EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f"Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}")

anchor = bpy.data.objects.get(ANCHOR_NAME)
if not anchor:
    raise RuntimeError(f"Missing {ANCHOR_NAME}")
center = Vector((float(anchor.location.x), float(anchor.location.y), 0.0))

report = []
for name in OPENINGS:
    obj = bpy.data.objects.get(name)
    if not obj or obj.type != "MESH":
        raise RuntimeError(f"Missing crown opening {name}")
    if obj.get("ss_export") is not True or obj.get("ss_role") != "landmark":
        raise RuntimeError(f"Unexpected metadata on {name}")
    if len(obj.data.vertices) != 8 or len(obj.data.polygons) != 6:
        raise RuntimeError(f"Unexpected shadowplate topology on {name}")
    dims = sorted(float(v) for v in obj.dimensions)
    if dims[0] > 0.20:
        raise RuntimeError(f"{name} is not a thin shadowplate: {obj.dimensions[:]}")

    original = obj.location.copy()
    to_center = Vector((center.x - original.x, center.y - original.y, 0.0))
    if to_center.length < 1.0:
        raise RuntimeError(f"Invalid crown opening radial vector for {name}")
    delta = to_center.normalized() * RECESS_M
    obj.location = original + delta
    obj["ss_v44_recess_m"] = RECESS_M
    obj["ss_v44_change"] = "Recessed crown shadowplate to create real opening depth"
    obj["ss_tag"] = "rathaus_v44_tower_crown_shadowplate"

    report.append({
        "name": name,
        "original_location_m": [float(v) for v in original],
        "target_location_m": [float(v) for v in obj.location],
        "delta_m": [float(v) for v in delta],
        "recess_m": RECESS_M,
        "dimensions_m": [float(v) for v in obj.dimensions],
        "material": obj.material_slots[0].material.name if obj.material_slots and obj.material_slots[0].material else None,
    })

bpy.context.view_layer.update()
# Preserve all topology: this version is transform-only for exactly four objects.
if len(report) != 4:
    raise RuntimeError("Expected exactly four crown opening changes")

bpy.context.scene["ss_master_version"] = "v44_CROWN_OPENING_DEPTH"
bpy.context.scene["ss_v44_change"] = "Recessed four V37 crown opening shadowplates by 1.35m; no topology changes"
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

payload = {
    "schema": "SpandauStrike.WorldMasterV44CrownOpeningDepth.v1",
    "source_master": "SpandauStrike_Rathaus_WORLD_MASTER_v43_RECOVERED_ENTRANCE_STEPS.blend",
    "source_master_version": EXPECTED_SOURCE_VERSION,
    "output_master": os.path.basename(OUT_BLEND),
    "output_master_version": "v44_CROWN_OPENING_DEPTH",
    "anchor": ANCHOR_NAME,
    "anchor_xy_m": [center.x, center.y],
    "recess_m": RECESS_M,
    "objects_modified": len(report),
    "objects": report,
    "policy": "Transform-only refinement. No mesh topology, materials, gameplay objects, collision, roof or tower stone geometry changed."
}
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)

print("V44_OUT=" + OUT_BLEND)
print("V44_REPORT=" + OUT_REPORT)
print(json.dumps({"objects_modified": len(report), "recess_m": RECESS_M}, ensure_ascii=False))
