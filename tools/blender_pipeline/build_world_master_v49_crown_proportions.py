import bpy, json, os

EXPECTED_SOURCE_VERSION = "v48_DORMER_ALIGNMENT"
OUTPUT_VERSION = "v49_CROWN_PROPORTIONS"
FACTORS = {
    "V37_TowerTransitionLowerBand": 0.96,
    "V37_TowerTransitionUpperBand": 0.90,
    "V37_CrownBase": 0.90,
    "V37_CrownTopBand": 0.86,
    "V37_CopperOctagonalRoof": 0.86,
}

source_path = os.path.abspath(bpy.data.filepath)
source_dir = os.path.dirname(source_path)
OUT_BLEND = os.path.join(source_dir, "SpandauStrike_Rathaus_WORLD_MASTER_v49_CROWN_PROPORTIONS.blend")
OUT_REPORT = os.path.splitext(OUT_BLEND)[0] + "_REPORT.json"
source_version = str(bpy.context.scene.get("ss_master_version", ""))
if source_version != EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f"Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}")

before = {}
after = {}
for name, factor in FACTORS.items():
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != 'MESH':
        raise RuntimeError(f"Missing mesh {name}")
    before[name] = [float(v) for v in obj.dimensions]
    obj.scale.x *= factor
    obj.scale.y *= factor
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)
    obj["ss_revision"] = OUTPUT_VERSION
    obj["ss_reference_basis"] = "media/theme/rathaus-spandau-photo.jpg"
    obj["ss_tag"] = "rathaus_tower_crown_proportion_corrected"
    after[name] = [float(v) for v in obj.dimensions]

bpy.context.scene["ss_master_version"] = OUTPUT_VERSION
bpy.context.scene["ss_v49_change"] = (
    "Reference-driven Rathaus tower crown width correction: narrowed transition bands, crown base, "
    "top band and copper roof; topology, locations, gameplay, collision and crown opening geometry unchanged"
)

report = {
    "schema": "SpandauStrike.WorldMasterV49CrownProportions.v1",
    "source_master": os.path.basename(source_path),
    "source_master_version": EXPECTED_SOURCE_VERSION,
    "output_master": os.path.basename(OUT_BLEND),
    "output_master_version": OUTPUT_VERSION,
    "reference": "media/theme/rathaus-spandau-photo.jpg",
    "modified_objects": list(FACTORS.keys()),
    "xy_scale_factors": FACTORS,
    "before_dimensions_m": before,
    "after_dimensions_m": after,
    "policy": "Transform-only proportion correction on existing tower crown meshes. No topology, gameplay, collision, spawn, objective, cover or route changes."
}

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("V49_OUT=" + OUT_BLEND)
print("V49_REPORT=" + OUT_REPORT)
print(json.dumps(report, ensure_ascii=False))
