import bpy
import json
import os
from mathutils import Vector

EXPECTED_SOURCE_VERSION = "v45_MAIN_ROOF_RIDGE_ALIGNMENT"
OUTPUT_VERSION = "v46_RETIRE_LEGACY_TOWER_ROOF"
LEGACY_NAME = "V33_CopperOctagonalRoof"
CURRENT_NAME = "V37_CopperOctagonalRoof"

source_path = os.path.abspath(bpy.data.filepath)
source_dir = os.path.dirname(source_path)
OUT_BLEND = os.path.join(source_dir, "SpandauStrike_Rathaus_WORLD_MASTER_v46_RETIRE_LEGACY_TOWER_ROOF.blend")
OUT_REPORT = os.path.splitext(OUT_BLEND)[0] + "_REPORT.json"

source_version = str(bpy.context.scene.get("ss_master_version", ""))
if source_version != EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f"Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}")

legacy = bpy.data.objects.get(LEGACY_NAME)
current = bpy.data.objects.get(CURRENT_NAME)
if not legacy or legacy.type != "MESH":
    raise RuntimeError(f"Missing legacy roof {LEGACY_NAME}")
if not current or current.type != "MESH":
    raise RuntimeError(f"Missing current roof {CURRENT_NAME}")
if legacy.get("ss_export") is not True or legacy.get("ss_role") != "landmark":
    raise RuntimeError("Legacy roof is not in the expected accidentally-exported state")
if current.get("ss_export") is not True or current.get("ss_role") != "landmark":
    raise RuntimeError("Current V37 roof is not a production landmark")


def bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx

lmn, lmx = bounds(legacy)
cmn, cmx = bounds(current)
lc = (lmn + lmx) * 0.5
cc = (cmn + cmx) * 0.5
xy_offset = ((lc.x-cc.x)**2 + (lc.y-cc.y)**2) ** 0.5

# Guard: these are spatially the same tower cap, not unrelated objects.
if xy_offset > 0.05:
    raise RuntimeError(f"Legacy/current roof XY centers differ by {xy_offset:.3f} m")
if abs((lmx.z-lmn.z) - (cmx.z-cmn.z)) > 0.05:
    raise RuntimeError("Legacy/current roof heights differ unexpectedly")

before = {
    "role": legacy.get("ss_role"),
    "export": legacy.get("ss_export"),
    "hide_render": legacy.hide_render,
    "hide_viewport": legacy.hide_viewport,
}
legacy["ss_role"] = "reference"
legacy["ss_export"] = False
legacy["ss_revision"] = OUTPUT_VERSION
legacy["ss_tag"] = "replaced_v37_tower_roof"
legacy["ss_v46_change"] = "Retired duplicated V33 copper roof; V37 roof remains authoritative"
legacy.hide_render = True
legacy.hide_viewport = True

bpy.context.scene["ss_master_version"] = OUTPUT_VERSION
bpy.context.scene["ss_v46_change"] = (
    "Retired accidentally exported V33_CopperOctagonalRoof as hidden reference; "
    "V37_CopperOctagonalRoof remains the production tower roof"
)

after = {
    "role": legacy.get("ss_role"),
    "export": legacy.get("ss_export"),
    "hide_render": legacy.hide_render,
    "hide_viewport": legacy.hide_viewport,
}
report = {
    "schema": "SpandauStrike.WorldMasterV46RetireLegacyTowerRoof.v1",
    "source_master": os.path.basename(source_path),
    "source_master_version": EXPECTED_SOURCE_VERSION,
    "output_master": os.path.basename(OUT_BLEND),
    "output_master_version": OUTPUT_VERSION,
    "legacy_object": LEGACY_NAME,
    "current_object": CURRENT_NAME,
    "legacy_before": before,
    "legacy_after": after,
    "legacy_bounds_m": {"min": list(lmn), "max": list(lmx)},
    "current_bounds_m": {"min": list(cmn), "max": list(cmx)},
    "xy_center_offset_m": float(xy_offset),
    "z_center_offset_m": float(lc.z - cc.z),
    "topology": {
        "legacy_vertices": len(legacy.data.vertices),
        "legacy_polygons": len(legacy.data.polygons),
        "current_vertices": len(current.data.vertices),
        "current_polygons": len(current.data.polygons),
    },
    "policy": "Metadata/visibility retirement only. No mesh topology, transforms, materials, gameplay or collision changes.",
}

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("V46_OUT=" + OUT_BLEND)
print("V46_REPORT=" + OUT_REPORT)
print(json.dumps(report, ensure_ascii=False))
