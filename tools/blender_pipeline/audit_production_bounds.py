import bpy,json
from pathlib import Path
from mathutils import Vector
src=Path(bpy.data.filepath);rows=[];mn=[1e30]*3;mx=[-1e30]*3
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not bool(o.get('ss_export',True)) or o.get('ss_role','') in ('reference','blockout'):continue
    for c in o.bound_box:
        w=o.matrix_world@Vector(c)
        for i in range(3):mn[i]=min(mn[i],float(w[i]));mx[i]=max(mx[i],float(w[i]))
    rows.append(o.name)
rep={'file':str(src),'export_mesh_count':len(rows),'bounds_min':mn,'bounds_max':mx,'bounds_size':[mx[i]-mn[i] for i in range(3)]}
src.with_name(src.stem+'_PRODUCTION_BOUNDS.json').write_text(json.dumps(rep,indent=2),encoding='utf-8');print('PRODUCTION_BOUNDS',json.dumps(rep),flush=True)
