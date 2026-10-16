import bpy, json, os, sys

MODELS = ["PM_135_Operator", "PM_135_Scout", "PM_Opp_Assault", "PM_Opp_Recon"]
REQUIRED_BONES = ["root","pelvis","spine_01","spine_02","spine_03","head","upperarm_l","lowerarm_l","hand_l","upperarm_r","lowerarm_r","hand_r","thigh_l","calf_l","foot_l","thigh_r","calf_r","foot_r"]

blend_path = bpy.data.filepath
if not blend_path:
    raise RuntimeError("No .blend file is open")
source_dir = os.path.dirname(blend_path)

armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
rig = next((a for a in armatures if all(b in {x.name for x in a.data.bones} for b in REQUIRED_BONES)), None)
if rig is None:
    raise RuntimeError("No armature satisfies required Spandau Strike bone contract")

results = []
for name in MODELS:
    mesh = bpy.data.objects.get(name)
    if not mesh or mesh.type != 'MESH':
        raise RuntimeError(f"Missing mesh object: {name}")
    linked = [m.object for m in mesh.modifiers if m.type == 'ARMATURE' and m.object]
    if rig not in linked:
        raise RuntimeError(f"{name} is not bound to validated rig {rig.name}")

    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    out = os.path.join(source_dir, name + '.fbx')
    bpy.ops.export_scene.fbx(
        filepath=out,
        use_selection=True,
        object_types={'ARMATURE','MESH'},
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        use_space_transform=True,
        bake_space_transform=False,
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',
        use_armature_deform_only=False,
        mesh_smooth_type='FACE',
        use_tspace=True,
        bake_anim=False,
        path_mode='AUTO'
    )
    results.append({"name": name, "fbx": out, "bytes": os.path.getsize(out)})

report = {"blend": blend_path, "rig": rig.name, "exports": results}
out_report = os.path.join(source_dir, 'playermodel_export_report.json')
with open(out_report, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
print('PLAYMODEL_EXPORT=' + json.dumps({"rig": rig.name, "count": len(results), "report": out_report}))
