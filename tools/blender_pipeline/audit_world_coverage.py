import bpy, json
from pathlib import Path
from mathutils import Vector
src=Path(bpy.data.filepath); out=src.with_name(src.stem+'_WORLD_COVERAGE_AUDIT.json')
terms=['terrain','road','surrounding','water','building','rathaus','plaza','platz']
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    n=o.name.lower(); tag=str(o.get('ss_tag',o.get('spandau_tag',''))).lower(); role=str(o.get('ss_role',o.get('spandau_role','')))
    if not any(t in n or t in tag for t in terms): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
    rows.append({'name':o.name,'role':role,'tag':tag,'collections':[c.name for c in o.users_collection],'location_m':[round(float(x),3) for x in o.matrix_world.translation],'dimensions_m':[round(float(mx[i]-mn[i]),3) for i in range(3)],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)})
report={'file':str(src),'objects':rows}
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
for r in sorted(rows,key=lambda x:max(x['dimensions_m']),reverse=True)[:40]: print(r)
print('OUT',out)
