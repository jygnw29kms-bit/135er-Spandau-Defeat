import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
obs=[]
for n in ('UCX_COL_FULLMAP_SurroundingBuildings','UCX_COL_Rathaus_Main'):
    o=bpy.data.objects.get(n)
    if not o: continue
    verts=[o.matrix_world @ v.co for v in o.data.vertices]
    polys=[tuple(p.vertices) for p in o.data.polygons]
    obs.append((n,BVHTree.FromPolygons(verts,polys,all_triangles=False)))
def hitseg(a,b):
    d=b-a; L=d.length
    if L<1e-6:return None
    dn=d.normalized(); best=None
    for name,bvh in obs:
        h=bvh.ray_cast(a,dn,L)
        if h[0] is not None:
            dist=(h[0]-a).length
            if best is None or dist<best[1]:best=(name,dist,h[0])
    return best
spawns=[o for o in bpy.data.objects if o.name.startswith('SM_SPAWN_') and 'RING' not in o.name]
objs=[bpy.data.objects.get('SM_OBJECTIVE_A'),bpy.data.objects.get('SM_OBJECTIVE_B')]
rows=[]
for s in spawns:
    for target in objs:
        a=s.matrix_world.translation.copy();b=target.matrix_world.translation.copy();a.z+=1.45;b.z+=1.45
        h=hitseg(a,b); row={'spawn':s.name,'target':target.name,'distance_m':round((b-a).length,2),'blocked':bool(h)}
        if h: row.update({'blocker':h[0],'hit_distance_m':round(h[1],2),'hit':[round(x,2) for x in h[2]]})
        rows.append(row);print('ROUTE',row)
out=r'C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\v38_direct_route_audit.json'
open(out,'w',encoding='utf-8').write(json.dumps(rows,indent=2));print('OUT',out)
