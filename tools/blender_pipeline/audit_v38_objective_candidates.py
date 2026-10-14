import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
blend=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v37_TOWER_TRANSITION.blend")
bpy.ops.wm.open_mainfile(filepath=str(blend))
terr=bpy.data.objects['SM_Rathaus_DGM1_1000m_v21']
blockers=[bpy.data.objects.get('UCX_COL_Rathaus_Main'),bpy.data.objects.get('UCX_COL_FULLMAP_SurroundingBuildings')]
def bvh_world(o):
 deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh(); verts=[o.matrix_world@v.co for v in me.vertices]; polys=[p.vertices[:] for p in me.polygons]; tree=BVHTree.FromPolygons(verts,polys,all_triangles=False); ev.to_mesh_clear(); return tree
T=bvh_world(terr); Bs=[(o.name,bvh_world(o)) for o in blockers if o]
cands={'F1_WEST':(-275,-20),'F2_WEST_STREET':(-135,-80),'F3_RATHAUS':(5,-68),'F4_EAST_STREET':(125,65),'F5_EAST':(235,-10)}
for name,(x,y) in cands.items():
 hit=T.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200); z=hit[0].z if hit[0] else None
 blocked=[]
 for bn,b in Bs:
  h=b.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)
  if h[0] and z is not None and h[0].z>z+1.5: blocked.append((bn,round(h[0].z,2)))
 print('CAND',name,'xy',x,y,'terrain',round(z,2) if z is not None else None,'blocked',blocked)
