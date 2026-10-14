import bpy, json, os

scene = bpy.context.scene
src = bpy.data.filepath
out = os.path.splitext(src)[0] + '_EXPORT_MANIFEST.json'

items = []
for o in scene.objects:
    role = o.get('ss_role', o.get('spandau_role', 'untagged'))
    export = bool(o.get('ss_export', o.get('ue_export', True)))
    tag = o.get('ss_tag', o.get('spandau_tag', ''))
    loc = o.matrix_world.translation
    rot = o.matrix_world.to_euler('XYZ')
    scl = o.matrix_world.to_scale()
    row = {
        'name': o.name,
        'type': o.type,
        'role': role,
        'tag': tag,
        'export': export,
        'location_m': [loc.x, loc.y, loc.z],
        'rotation_rad_xyz': [rot.x, rot.y, rot.z],
        'scale_xyz': [scl.x, scl.y, scl.z],
        'collections': [c.name for c in o.users_collection],
    }
    metadata = {}
    for k in o.keys():
        if str(k).startswith('ss_') and k not in ('ss_role','ss_tag','ss_export'):
            v = o.get(k)
            if isinstance(v, (str, int, float, bool)) or v is None:
                metadata[str(k)] = v
            elif hasattr(v, '__iter__'):
                try: metadata[str(k)] = list(v)
                except Exception: metadata[str(k)] = str(v)
            else:
                metadata[str(k)] = str(v)
    if metadata:
        row['metadata'] = metadata
    if o.type == 'MESH' and o.data:
        row['mesh_data'] = o.data.name
        row['vertices'] = len(o.data.vertices)
        row['polygons'] = len(o.data.polygons)
        row['materials'] = [m.name if m else None for m in o.data.materials]
    items.append(row)

roles = {}
for x in items:
    roles[x['role']] = roles.get(x['role'], 0) + 1

manifest = {
    'master_file': src,
    'master_version': scene.get('ss_master_version', scene.get('spandau_master_version', '')),
    'engine': scene.get('ss_engine', 'UE5 only'),
    'policy': scene.get('ss_policy', scene.get('spandau_master_policy', '')),
    'object_count': len(items),
    'role_counts': roles,
    'gameplay': [x for x in items if x['role'] == 'gameplay'],
    'gameplay_planning': [x for x in items if x['role'] == 'gameplay_planning'],
    'collision': [x for x in items if x['role'] == 'collision'],
    'landmarks': [x for x in items if x['role'] == 'landmark'],
    'world': [x for x in items if x['role'] == 'world'],
    'export_objects': [x['name'] for x in items if x['export']],
    'excluded_objects': [x['name'] for x in items if not x['export']],
}

with open(out, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print('MANIFEST=' + out)
print('ROLES=' + json.dumps(roles, sort_keys=True))


