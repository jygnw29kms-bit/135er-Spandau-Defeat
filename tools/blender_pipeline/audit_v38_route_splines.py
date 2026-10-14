import bpy, json
from pathlib import Path
blend=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v37_TOWER_TRANSITION.blend")
bpy.ops.wm.open_mainfile(filepath=str(blend))
for n in ['ROUTE_NORTH_REAR','ROUTE_CENTER_RATHAUS','ROUTE_SOUTH_PLAZA']:
 o=bpy.data.objects.get(n)
 print('ROUTE',n,'type',o.type if o else None,'loc',tuple(round(x,2) for x in o.location) if o else None)
 if not o: continue
 if o.type=='CURVE':
  for si,s in enumerate(o.data.splines):
   pts=[]
   if s.type=='BEZIER':
    for p in s.bezier_points:
     q=o.matrix_world @ p.co
     pts.append(tuple(round(v,2) for v in q))
   else:
    for p in s.points:
     q=o.matrix_world @ p.co.xyz
     pts.append(tuple(round(v,2) for v in q))
   print(' SPLINE',si,pts)
 elif o.type=='MESH':
  pts=[o.matrix_world @ v.co for v in o.data.vertices]
  print(' VERTS', [tuple(round(v,2) for v in q) for q in pts[:40]])
