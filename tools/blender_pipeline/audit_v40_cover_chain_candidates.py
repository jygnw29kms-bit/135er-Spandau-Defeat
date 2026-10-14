import bpy, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
blend=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v39_CLASSIC_COMBAT_FLOW.blend")
bpy.ops.wm.open_mainfile(filepath=str(blend))
def bvh_world(o):
 deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];ps=[p.vertices[:] for p in me.polygons];t=BVHTree.FromPolygons(vs,ps,all_triangles=False);ev.to_mesh_clear();return t
T=bvh_world(bpy.data.objects['SM_Rathaus_DGM1_1000m_v21']); B=bvh_world(bpy.data.objects['UCX_COL_FULLMAP_SurroundingBuildings']); R=bvh_world(bpy.data.objects['UCX_COL_Rathaus_Main'])
def z_at(x,y):
 h=T.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200);return h[0].z if h[0] else None
def clear(x,y):
 z=z_at(x,y)
 if z is None:return None
 for b in (B,R):
  h=b.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
  if h[0] and h[0].z>z+1.5:return None
 return z
def pts(o):
 s=o.data.splines[0]
 src=[p.co.xyz for p in s.points] if s.type!='BEZIER' else [p.co for p in s.bezier_points]
 return [o.matrix_world@q for q in src]
def sample_poly(ps,step=32):
 out=[]
 for a,b in zip(ps,ps[1:]):
  d=(b-a).length;n=max(1,int(d//step))
  for i in range(1,n+1):out.append(a.lerp(b,i/(n+1)))
 return out
res={}
for n in ['ROUTE_NORTH_REAR','ROUTE_CENTER_RATHAUS','ROUTE_SOUTH_PLAZA','CROSSLINK_WEST','CROSSLINK_MID','CROSSLINK_EAST']:
 o=bpy.data.objects.get(n);rows=[]
 for q in sample_poly(pts(o),32):
  z=clear(q.x,q.y)
  if z is not None:rows.append((round(q.x,1),round(q.y,1),round(z,2)))
 res[n]=rows
 print(n,'clear_candidates',len(rows),rows[:20])
Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\v40_cover_chain_candidates.json").write_text(json.dumps(res,indent=2),encoding='utf-8')

