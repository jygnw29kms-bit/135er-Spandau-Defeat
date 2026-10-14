import bpy, math
A=math.radians(47.5); C=math.cos(A); S=math.sin(A)
def local_xy(x,y): return (x*C+y*S,-x*S+y*C)
keep={'REAL_Rebuilt_Architecture','PRODUCTION_RATHAUS_V16_DETAIL','PRODUCTION_RATHAUS_V24_PROFILE','PRODUCTION_RATHAUS_V25_ACCURACY','PRODUCTION_RATHAUS_V26_CLEAN','PRODUCTION_RATHAUS_V31_FENESTRATION','PRODUCTION_RATHAUS_V32_TOWER','PRODUCTION_RATHAUS_V33_HISTORIC','PRODUCTION_RATHAUS_V34_RELIEF_FIX','PRODUCTION_RATHAUS_V37_TOWER'}
rows=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.get('ss_export',True): continue
    if not ({c.name for c in o.users_collection}&keep): continue
    u,v=local_xy(o.location.x,o.location.y)
    z=o.location.z
    if abs(u)<=9 and -4<=v<=14 and 54<=z<=67:
        rows.append((o.name,round(u,3),round(v,3),round(z,3),tuple(round(x,3) for x in o.dimensions),o.get('ss_tag'),[c.name for c in o.users_collection]))
print('COUNT',len(rows))
for r in sorted(rows,key=lambda x:(x[3],x[0])):print('SPATIAL',r)
