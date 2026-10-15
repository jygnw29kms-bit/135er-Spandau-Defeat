import bpy
import json
import os
from mathutils import Vector

EXPECTED_SOURCE_VERSION = "v46_RETIRE_LEGACY_TOWER_ROOF"
OUTPUT_VERSION = "v47_CROWN_GUARDRAILS"
OPENINGS = [
    "V37_CrownOpeningFront",
    "V37_CrownOpeningRear",
    "V37_CrownOpeningEast",
    "V37_CrownOpeningWest",
]

source_path = os.path.abspath(bpy.data.filepath)
source_dir = os.path.dirname(source_path)
OUT_BLEND = os.path.join(source_dir, "SpandauStrike_Rathaus_WORLD_MASTER_v47_CROWN_GUARDRAILS.blend")
OUT_REPORT = os.path.splitext(OUT_BLEND)[0] + "_REPORT.json"

source_version = str(bpy.context.scene.get("ss_master_version", ""))
if source_version != EXPECTED_SOURCE_VERSION:
    raise RuntimeError(f"Expected source {EXPECTED_SOURCE_VERSION}, got {source_version!r}")

for name in OPENINGS:
    if bpy.data.objects.get(name) is None:
        raise RuntimeError(f"Missing opening {name}")

mat = bpy.data.materials.get("M_V47_CrownRail")
if mat is None:
    mat = bpy.data.materials.new("M_V47_CrownRail")
    mat.diffuse_color = (0.08, 0.085, 0.09, 1.0)
    mat.metallic = 0.65
    mat.roughness = 0.38

created = []

def create_box(name, opening, local_center, local_dims):
    rot = opening.rotation_euler.to_matrix()
    world_center = opening.location + rot @ Vector(local_center)
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=world_center, rotation=opening.rotation_euler)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (local_dims[0] / 2.0, local_dims[1] / 2.0, local_dims[2] / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    obj["ss_role"] = "landmark"
    obj["ss_export"] = True
    obj["ss_revision"] = OUTPUT_VERSION
    obj["ss_tag"] = "rathaus_tower_crown_guardrail"
    obj["ss_reference_basis"] = "media/theme/rathaus-spandau-photo.jpg"
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target = opening.users_collection[0] if opening.users_collection else bpy.context.scene.collection
    target.objects.link(obj)
    return obj

for opening_name in OPENINGS:
    opening = bpy.data.objects[opening_name]
    dx, dy, _ = opening.dimensions
    width_axis = "X" if dx > dy else "Y"
    center = Vector((-3.6863865852, 3.3779511452, opening.location.z))
    local_delta = opening.rotation_euler.to_matrix().transposed() @ (opening.location - center)
    if width_axis == "X":
        outward_sign = -1.0 if local_delta.y < 0 else 1.0
        perp = outward_sign * 0.24
        bar_dims = (8.0, 0.12, 0.11)
        post_dims = (0.10, 0.12, 1.35)
        def pos(w, z): return (w, perp, z)
    else:
        outward_sign = -1.0 if local_delta.x < 0 else 1.0
        perp = outward_sign * 0.24
        bar_dims = (0.12, 8.0, 0.11)
        post_dims = (0.12, 0.10, 1.35)
        def pos(w, z): return (perp, w, z)

    parts = []
    for i, z in enumerate((-2.65, -2.05)):
        parts.append(create_box(f"V47_CrownRail_{opening_name}_{i}", opening, pos(0.0, z), bar_dims))
    for i, w in enumerate((-3.55, -1.78, 0.0, 1.78, 3.55)):
        parts.append(create_box(f"V47_CrownPost_{opening_name}_{i}", opening, pos(w, -2.35), post_dims))

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    rail = bpy.context.object
    rail.name = f"V47_CrownGuardrail_{opening_name.replace('V37_CrownOpening','')}"
    rail["ss_role"] = "landmark"
    rail["ss_export"] = True
    rail["ss_revision"] = OUTPUT_VERSION
    rail["ss_tag"] = "rathaus_tower_crown_guardrail"
    rail["ss_reference_basis"] = "media/theme/rathaus-spandau-photo.jpg"
    created.append(rail)

bpy.context.scene["ss_master_version"] = OUTPUT_VERSION
bpy.context.scene["ss_v47_change"] = (
    "Added four low metal crown guardrails matching the visible current Rathaus tower lantern rail; "
    "no existing geometry, transforms, collision or gameplay objects changed"
)

report = {
    "schema": "SpandauStrike.WorldMasterV47CrownGuardrails.v1",
    "source_master": os.path.basename(source_path),
    "source_master_version": EXPECTED_SOURCE_VERSION,
    "output_master": os.path.basename(OUT_BLEND),
    "output_master_version": OUTPUT_VERSION,
    "reference": "media/theme/rathaus-spandau-photo.jpg",
    "created_objects": [o.name for o in created],
    "created_count": len(created),
    "per_guardrail_topology": [
        {"name": o.name, "vertices": len(o.data.vertices), "polygons": len(o.data.polygons)} for o in created
    ],
    "design": {
        "opening_clear_width_m": 8.8,
        "rail_span_m": 8.0,
        "horizontal_bars": 2,
        "vertical_posts": 5,
        "guardrail_height_m": 1.35,
        "lower_bar_z_offset_from_opening_center_m": -2.65,
        "upper_bar_z_offset_from_opening_center_m": -2.05
    },
    "policy": "Additive landmark detail only. No existing mesh, transform, collision, gameplay, route, spawn, objective or cover change."
}

bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("V47_OUT=" + OUT_BLEND)
print("V47_REPORT=" + OUT_REPORT)
print(json.dumps(report, ensure_ascii=False))
