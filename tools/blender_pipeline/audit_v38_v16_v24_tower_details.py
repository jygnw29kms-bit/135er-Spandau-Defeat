import bpy, math
A=math.radians(47.5);C=math.cos(A);S=math.sin(A)
def uv(o):
 x,y=o.location.x,o.location.y
 return (x*C+y*S,-x*S+y*C)
for cname in ('PRODUCTION_RATHAUS_V16_DETAIL','PRODUCTION_RATHAUS_V24_PROFILE','REAL_Rebuilt_Detail'):
 c=bpy.data.collections.get(cname)
 if not c: continue
 print('COL',cname,'COUNT',len(c.objects))
 for o in c.objects:
  if o.type!='MESH' or not o.get('ss_export',True): continue
  u,v=uv(o);z=o.location.z
  if abs(u)<12 and -7<v<17 and 20<z<70:
   print('DETAIL',cname,o.name,'uvz',round(u,2),round(v,2),round(z,2),'dims',tuple(round(x,2) for x in o.dimensions),'tag',o.get('ss_tag'))
