import bpy
keep={'REAL_Rebuilt_Architecture','PRODUCTION_RATHAUS_V16_DETAIL','PRODUCTION_RATHAUS_V24_PROFILE','PRODUCTION_RATHAUS_V25_ACCURACY','PRODUCTION_RATHAUS_V26_CLEAN','PRODUCTION_RATHAUS_V31_FENESTRATION','PRODUCTION_RATHAUS_V32_TOWER','PRODUCTION_RATHAUS_V33_HISTORIC','PRODUCTION_RATHAUS_V34_RELIEF_FIX','PRODUCTION_RATHAUS_V37_TOWER'}
rows=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.get('ss_export',True): continue
    if not ({c.name for c in o.users_collection}&keep): continue
    d=o.dimensions
    # tall/narrow candidates around tower shaft; based on world bbox center near Rathaus center
    if d.z>8 and (d.x<1.0 or d.y<1.0):
        rows.append((o.name,tuple(round(x,3) for x in o.location),tuple(round(x,3) for x in d),o.get('ss_tag'),[c.name for c in o.users_collection]))
print('COUNT',len(rows))
for r in rows: print('RIB',r)
