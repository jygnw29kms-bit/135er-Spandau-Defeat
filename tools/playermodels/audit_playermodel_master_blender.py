import bpy, json, os, sys

REQUIRED_MODELS = ["PM_135_Operator", "PM_135_Scout", "PM_Opp_Assault", "PM_Opp_Recon"]
REQUIRED_BONES = ["root","pelvis","spine_01","spine_02","spine_03","head","upperarm_l","lowerarm_l","hand_l","upperarm_r","lowerarm_r","hand_r","thigh_l","calf_l","foot_l","thigh_r","calf_r","foot_r"]

blend_path = bpy.data.filepath
if not blend_path:
    raise RuntimeError("No .blend file is open")

armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
model_rows = []

for name in REQUIRED_MODELS:
    obj = bpy.data.objects.get(name)
    row = {"name": name, "exists": bool(obj), "type": getattr(obj, "type", None)}
    if obj and obj.type == 'MESH':
        mods = [m.object.name for m in obj.modifiers if m.type == 'ARMATURE' and m.object]
        row["armatures"] = mods
        row["vertices"] = len(obj.data.vertices)
        row["polygons"] = len(obj.data.polygons)
    model_rows.append(row)

rig_rows = []
for rig in armatures:
    names = {b.name for b in rig.data.bones}
    rig_rows.append({
        "name": rig.name,
        "bone_count": len(names),
        "missing_required_bones": [b for b in REQUIRED_BONES if b not in names],
        "has_all_required_bones": all(b in names for b in REQUIRED_BONES),
    })

valid_models = all(r["exists"] and r["type"] == "MESH" and r.get("armatures") for r in model_rows)
valid_rig = any(r["has_all_required_bones"] for r in rig_rows)
report = {
    "blend": os.path.abspath(blend_path),
    "models": model_rows,
    "armatures": rig_rows,
    "valid_models": valid_models,
    "valid_rig": valid_rig,
    "ready_for_export": bool(valid_models and valid_rig),
}

out = os.path.splitext(blend_path)[0] + "_PLAYMODEL_AUDIT.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print("PLAYMODEL_AUDIT=" + json.dumps({"ready_for_export": report["ready_for_export"], "output": out}))
if not report["ready_for_export"]:
    sys.exit(2)
