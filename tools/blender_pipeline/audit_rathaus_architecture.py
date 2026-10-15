import bpy
import json
import os
from collections import Counter
from mathutils import Vector


def world_bounds(objects):
    mins = [float('inf')] * 3
    maxs = [float('-inf')] * 3
    found = False
    for obj in objects:
        if obj.type != 'MESH':
            continue
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            for i in range(3):
                mins[i] = min(mins[i], float(p[i]))
                maxs[i] = max(maxs[i], float(p[i]))
            found = True
    if not found:
        return None
    return {
        'min': mins,
        'max': maxs,
        'size': [maxs[i] - mins[i] for i in range(3)],
    }


def collections_for_object(obj):
    return sorted(c.name for c in obj.users_collection)


def is_rathaus_candidate(obj):
    if obj.type != 'MESH':
        return False
    name = obj.name.lower()
    colnames = ' '.join(collections_for_object(obj)).lower()
    role = str(obj.get('ss_role', '')).lower()
    keywords = (
        'rathaus', 'frontwing', 'rearwing', 'westsidewing', 'eastsidewing',
        'crosswing', 'risalit', 'gable', 'portal', 'window', 'sill', 'tower',
        'clock', 'roof', 'facade', 'fassade', 'cornice', 'door', 'arch'
    )
    collection_hints = ('10_arch', '20_detail', '30_tower', 'optical_setdressing')
    return (
        role == 'landmark'
        or any(k in name for k in keywords)
        or any(k in colnames for k in collection_hints)
    )


scene = bpy.context.scene
mesh_objects = [o for o in scene.objects if o.type == 'MESH']
candidates = [o for o in mesh_objects if is_rathaus_candidate(o)]

objects = []
for o in sorted(candidates, key=lambda x: x.name.lower()):
    me = o.data
    objects.append({
        'name': o.name,
        'collections': collections_for_object(o),
        'role': o.get('ss_role'),
        'tag': o.get('ss_tag'),
        'export': o.get('ss_export'),
        'vertices': len(me.vertices),
        'polygons': len(me.polygons),
        'dimensions': [float(v) for v in o.dimensions],
        'location': [float(v) for v in o.location],
        'scale': [float(v) for v in o.scale],
        'materials': [slot.material.name if slot.material else None for slot in o.material_slots],
    })

by_collection = {}
for c in bpy.data.collections:
    direct = [o for o in c.objects if o in candidates]
    if not direct:
        continue
    by_collection[c.name] = {
        'objects': len(direct),
        'vertices': sum(len(o.data.vertices) for o in direct if o.type == 'MESH'),
        'polygons': sum(len(o.data.polygons) for o in direct if o.type == 'MESH'),
        'bounds': world_bounds(direct),
    }

name_groups = {
    'wing': ['wing'],
    'roof': ['roof', 'dach'],
    'tower': ['tower', 'turm', 'clock'],
    'window': ['window', 'fenster', 'sill'],
    'portal_door': ['portal', 'door', 'tor'],
    'facade_detail': ['risalit', 'gable', 'cornice', 'facade', 'fassade'],
    'collision': ['collision', 'ucx_'],
}
groups = {}
for group, terms in name_groups.items():
    hits = [o.name for o in candidates if any(t in o.name.lower() for t in terms)]
    groups[group] = {'count': len(hits), 'sample': hits[:80]}

payload = {
    'file': bpy.data.filepath,
    'scene_objects': len(scene.objects),
    'mesh_objects': len(mesh_objects),
    'rathaus_candidates': len(candidates),
    'candidate_vertices': sum(len(o.data.vertices) for o in candidates),
    'candidate_polygons': sum(len(o.data.polygons) for o in candidates),
    'candidate_bounds': world_bounds(candidates),
    'roles': dict(Counter(str(o.get('ss_role', '')) for o in candidates)),
    'groups': groups,
    'collections': dict(sorted(by_collection.items())),
    'objects': objects,
}

out = os.path.splitext(bpy.data.filepath)[0] + '_ARCH_AUDIT.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)

print('ARCH_AUDIT_OUT=' + out)
print(json.dumps({
    'rathaus_candidates': payload['rathaus_candidates'],
    'candidate_vertices': payload['candidate_vertices'],
    'candidate_polygons': payload['candidate_polygons'],
    'candidate_bounds': payload['candidate_bounds'],
    'groups': {k: v['count'] for k, v in groups.items()},
}, ensure_ascii=False))
