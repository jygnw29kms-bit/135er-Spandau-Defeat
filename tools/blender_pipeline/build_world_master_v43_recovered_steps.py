import bpy
import json
import os
from mathutils import Vector

SOURCE_V4 = r"C:\Users\dezen\Documents\SpandauStrike\Blender\analysis\IntegratedMaster_v4\RathausSpandau_REAL_Integrated_Master_v4.blend"
OUT_BLEND = r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v43_RECOVERED_ENTRANCE_STEPS.blend"
OUT_REPORT = os.path.splitext(OUT_BLEND)[0] + "_REPORT.json"
STEP_NAMES = [f"Step_{i}" for i in range(6)]
TRANSLATION = Vector((-5.197804768880208, 4.762911478678386, 0.10000014305114746))
COLLECTION_NAME = "RATHAUS_RECOVERED_ENTRANCE_STEPS"
EXPECTED_SOURCE_VERSION = "v42_RUNTIME_OBJECTIVES"

source_version = str(bpy.context.scene.get("ss_master_version", ""))
if source_version != EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f"Expected source master {EXPECTED_SOURCE_VERSION}, got {source_version!r}")

existing = [name for name in STEP_NAMES if bpy.data.objects.get(name)]
if existing:
    raise RuntimeError(f"Target already contains recovered step names: {existing}")

# Reconfirm the entrance reference frame before importing anything.
portal_source = {
    "Portal_-5.2": Vector((26.162343978881836, -31.026348114013672, 3.0999999046325684)),
    "Portal_0": Vector((29.675413131713867, -27.192506790161133, 3.0999999046325684)),
    "Portal_5.2": Vector((33.188480377197266, -23.35866355895996, 3.0999999046325684)),
}
door_target = {
    "SM_Door__5_2": "Portal_-5.2",
    "SM_Door_0": "Portal_0",
    "SM_Door_5_2": "Portal_5.2",
}
reference_errors = []
for door_name, portal_name in door_target.items():
    door = bpy.data.objects.get(door_name)
    if not door:
        raise RuntimeError(f"Missing v42 entrance reference {door_name}")
    expected = portal_source[portal_name] + TRANSLATION
    error = (door.location - expected).length
    reference_errors.append(float(error))
    if error > 0.00001:
        raise RuntimeError(f"Entrance reference mismatch {door_name}: {error} m")

collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None:
    collection = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(collection)

with bpy.data.libraries.load(SOURCE_V4, link=False) as (data_from, data_to):
    available = set(data_from.objects)
    missing = [name for name in STEP_NAMES if name not in available]
    if missing:
        raise RuntimeError(f"Missing source steps in recovered v4: {missing}")
    data_to.objects = STEP_NAMES

loaded = [obj for obj in data_to.objects if obj is not None]
if len(loaded) != 6:
    raise RuntimeError(f"Expected 6 loaded steps, got {len(loaded)}")

report_objects = []
for obj in loaded:
    collection.objects.link(obj)
    source_location = obj.location.copy()
    obj.location = source_location + TRANSLATION
    obj["ss_role"] = "landmark"
    obj["ss_export"] = True
    obj["ss_tag"] = "entrance_step"
    obj["ss_recovered_from"] = "RathausSpandau_REAL_Integrated_Master_v4"
    obj["ss_alignment"] = "entrance_portal_translation_v1"
    obj["ss_runtime"] = False
    report_objects.append({
        "name": obj.name,
        "source_location_m": [float(v) for v in source_location],
        "target_location_m": [float(v) for v in obj.location],
        "dimensions_m": [float(v) for v in obj.dimensions],
        "polygons": len(obj.data.polygons) if obj.type == "MESH" else 0,
        "vertices": len(obj.data.vertices) if obj.type == "MESH" else 0,
    })

bpy.context.scene["ss_master_version"] = "v43_RECOVERED_ENTRANCE_STEPS"
bpy.context.scene["ss_v43_change"] = "Recovered Step_0..Step_5 only using verified v42 entrance reference frame"

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

payload = {
    "schema": "SpandauStrike.WorldMasterV43RecoveredEntranceSteps.v1",
    "source_master": "SpandauStrike_Rathaus_WORLD_MASTER_v42_RUNTIME_OBJECTIVES.blend",
    "source_master_version": EXPECTED_SOURCE_VERSION,
    "recovery_source": "recovered/RathausSpandau_REAL_Integrated_Master_v4.blend",
    "output_master": os.path.basename(OUT_BLEND),
    "output_master_version": "v43_RECOVERED_ENTRANCE_STEPS",
    "collection": COLLECTION_NAME,
    "translation_m": [float(v) for v in TRANSLATION],
    "reference_max_error_m": max(reference_errors),
    "alignment_rms_m": 0.0000012715657552083333,
    "alignment_max_error_m": 0.0000014216537331209435,
    "objects_added": len(report_objects),
    "objects": report_objects,
    "policy": "No existing v42 object geometry or transform modified. Tower/plaza/statue recovery excluded."
}
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)

print("V43_OUT=" + OUT_BLEND)
print("V43_REPORT=" + OUT_REPORT)
print(json.dumps({"objects_added": len(report_objects), "reference_max_error_m": max(reference_errors)}, ensure_ascii=False))
