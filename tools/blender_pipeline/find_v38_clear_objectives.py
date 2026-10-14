import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
blend=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v37_TOWER_TRANSITION.blend")
bpy.ops.wm.open_mainfile(filepath=str(blend))
def bvh_world(o):
 deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh(); verts=[o.matrix_world@v.co for v in me.vertices]; polys=[p.vertices[:] for p in me.polygons]; t=BVHTree.FromPolygons(verts,polys,all_triangles=False); ev.to_mesh_clear(); return t
T=bvh_world(bpy.data.objects['SM_Rathaus_DGM1_1000m_v21'])
Bs=[(n,bvh_world(bpy.data.objects[n])) for n in ['UCX_COL_Rathaus_Main','UCX_COL_FULLMAP_SurroundingBuildings']]
def test(x,y):
 h=T.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
 if not h[0]: return None
 z=h[0].z
 for bn,b in Bs:
  q=b.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
  if q[0] and q[0].z>z+1.5:return None
 return z
for name,(tx,ty) in {'F1_WEST':(-275,-20),'F2_WEST_STREET':(-135,-80),'F4_EAST_STREET':(125,65)}.items():
 found=[]
 for r in range(0,101,10):
  for a in range(0,360,15):
   x=tx+r*math.cos(math.radians(a));y=ty+r*math.sin(math.radians(a));z=test(x,y)
   if z is not None:found.append((r,abs(y-ty),x,y,z))
  if found:break
 found.sort()
 print('CLEAR',name,[(round(x,1),round(y,1),round(z,2),r) for r,dy,x,y,z in found[:8]])
