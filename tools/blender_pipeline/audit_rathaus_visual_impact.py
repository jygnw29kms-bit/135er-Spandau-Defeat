import bpy,json,re,math
from pathlib import Path
src=Path(bpy.data.filepath);out=src.with_name(src.stem+'_RATHAUS_VISUAL_IMPACT.json')
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not bool(o.get('ss_export',True)):continue
    n=o.name.lower(); cols={c.name for c in o.users_collection}
    is_rathaus=('rathaus' in n or bool(cols & {'REAL_Rebuilt_Architecture','REAL_Rebuilt_Detail','PRODUCTION_RATHAUS_V16_DETAIL','ARCH_MICRODETAIL'}))
    if not is_rathaus:continue
    d=[float(x) for x in o.dimensions]; area=2*(d[0]*d[1]+d[0]*d[2]+d[1]*d[2]); vol=d[0]*d[1]*d[2]
    v=len(o.data.vertices);p=len(o.data.polygons); primitive=(v<=8 and p<=6)
    if re.search(r'tower|clock|cupola|finial|bal|rail',n):cat='tower'
    elif re.search(r'roof|gable|dormer|pediment',n):cat='roof'
    elif re.search(r'door|portal|entrance|step',n):cat='entrance'
    elif re.search(r'cornice|band|pilaster|plinth|trim|column|arch|eaves',n):cat='facade_detail'
    elif re.search(r'body|wing|risalit|cross',n):cat='massing'
    elif re.search(r'window|glass|mullion|sill',n):cat='windows'
    else:cat='other'
    # importance favors silhouette/massing and visible area, penalizes tiny repeated elements
    mult={'massing':4.0,'roof':3.5,'tower':3.5,'entrance':3.0,'facade_detail':2.0,'windows':.35,'other':.5}[cat]
    score=area*mult*(1.45 if primitive else 1.0)
    rows.append({'name':o.name,'category':cat,'primitive':primitive,'score':score,'area_proxy':area,'volume_proxy':vol,'dimensions':[round(x,3) for x in d],'location':[round(float(x),3) for x in o.location],'rotation_deg':[round(math.degrees(float(x)),2) for x in o.rotation_euler],'vertices':v,'polygons':p,'collections':sorted(cols),'materials':[m.name for m in o.data.materials if m]})
rows.sort(key=lambda x:x['score'],reverse=True)
rep={'file':str(src),'objects':len(rows),'primitive_count':sum(r['primitive'] for r in rows),'top':rows[:250]}
out.write_text(json.dumps(rep,indent=2),encoding='utf-8')
print('TOP_IMPACT')
for r in rows[:80]:print(json.dumps(r))
print('OUT',out)
