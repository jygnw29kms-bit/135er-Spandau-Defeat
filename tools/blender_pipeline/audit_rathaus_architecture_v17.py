import bpy, json, re
from pathlib import Path
from collections import Counter
blend=Path(bpy.data.filepath)
out=blend.with_name(blend.stem+'_RATHAUS_ARCH_AUDIT.json')
cols={'REAL_Rebuilt_Architecture','REAL_Rebuilt_Detail','FULLMAP_UrbanDetail','PRODUCTION_RATHAUS_V16_DETAIL'}
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    oc={c.name for c in o.users_collection}; n=o.name.lower()
    is_rathaus=bool(oc & cols) or o.get('ss_tag','') in ('rathaus','rathaus_v16_detail') or o.get('spandau_tag','') in ('rathaus','rathaus_v16_detail') or 'rathaus' in n
    if not is_rathaus: continue
    if re.search(r'tower|clock|cupola|finial|bal|rail',n): cat='tower'
    elif re.search(r'window|glass|mullion|sill|glow',n): cat='windows'
    elif re.search(r'roof|gable|dormer|pediment',n): cat='roof'
    elif re.search(r'door|portal|entrance|step',n): cat='entrance'
    elif re.search(r'cornice|band|pilaster|plinth|trim|column|arch',n): cat='facade_detail'
    elif re.search(r'body|wing|risalit|cross',n): cat='massing'
    elif re.search(r'statue|ornament|crest|eagle|balustr',n): cat='ornament'
    else: cat='other'
    rows.append({'name':o.name,'category':cat,'collections':sorted(oc),'dimensions_m':[round(float(x),3) for x in o.dimensions],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)})
cats=Counter(r['category'] for r in rows)
primitive_like=sum(1 for r in rows if r['vertices']<=8 and r['polygons']<=6)
report={'file':str(blend),'rathaus_mesh_count':len(rows),'categories':dict(cats),'primitive_box_like':primitive_like,'primitive_box_ratio':round(primitive_like/max(1,len(rows)),4),'objects':rows}
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('RATHAUS_V17_AUDIT',json.dumps({k:v for k,v in report.items() if k!='objects'}))
