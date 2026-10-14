import bpy
from pathlib import Path
for o in bpy.data.objects:
    if o.type!='MESH' or not o.get('ss_export', True):
        continue
    n=o.name
    if ('Tower' in n or 'Clock' in n or 'Crown' in n) and o.dimensions.z > 0.1:
        bb=[o.matrix_world @ v.co for v in o.data.vertices] if o.data and len(o.data.vertices)<5000 else []
        if bb:
            zmin=min(v.z for v in bb); zmax=max(v.z for v in bb)
        else:
            zmin=o.location.z-o.dimensions.z/2; zmax=o.location.z+o.dimensions.z/2
        if zmax>=52 and zmin<=86:
            print('T', n, 'z', round(zmin,3), round(zmax,3), 'dims', tuple(round(x,3) for x in o.dimensions), 'role',o.get('ss_role'), 'tag',o.get('ss_tag'), 'cols',[c.name for c in o.users_collection])
