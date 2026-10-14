import bpy, json, math, os
from collections import Counter, defaultdict
from mathutils import Vector
scene=bpy.context.scene
objs=list(scene.objects)
meshes=[o for o in objs if o.type=='MESH']
res={}
res['file']=bpy.data.filepath
res['objects_total']=len(objs)
res['types']=dict(Counter(o.type for o in objs))
# collection direct object counts + recursive unique counts
cols={}
for c in bpy.data.collections:
    direct=list(c.objects)
    recursive=[]
    seen=set()
    def walk(cc):
        for o in cc.objects:
            if o.name not in seen:
                seen.add(o.name); recursive.append(o)
        for ch in cc.children: walk(ch)
    walk(c)
    cols[c.name]={'direct':len(direct),'recursive':len(recursive),'mesh_recursive':sum(o.type=='MESH' for o in recursive)}
res['collections']=dict(sorted(cols.items()))
# data reuse / linked instances
bydata=defaultdict(list)
for o in meshes:
    if o.data: bydata[o.data.name].append(o.name)
res['shared_mesh_data']={k:v for k,v in bydata.items() if len(v)>1}
res['shared_mesh_data_count']=len(res['shared_mesh_data'])
# bounds, poly/vert counts, materials
mins=[float('inf')]*3; maxs=[float('-inf')]*3
poly_total=vert_total=0
zero_poly=[]; no_material=[]; neg_scale=[]; unapplied_scale=[]; tiny=[]; huge=[]
for o in meshes:
    me=o.data
    poly_total += len(me.polygons); vert_total += len(me.vertices)
    if len(me.polygons)==0: zero_poly.append(o.name)
    if len(o.material_slots)==0: no_material.append(o.name)
    sc=o.scale
    if sc.x*sc.y*sc.z < 0: neg_scale.append(o.name)
    if any(abs(s-1.0)>1e-4 for s in (sc.x,sc.y,sc.z)): unapplied_scale.append((o.name,[sc.x,sc.y,sc.z]))
    try:
        dims=o.dimensions
        if max(dims)<0.02: tiny.append((o.name,[dims.x,dims.y,dims.z]))
        if max(dims)>1000: huge.append((o.name,[dims.x,dims.y,dims.z]))
    except: pass
    for c in o.bound_box:
        w=o.matrix_world@Vector(c)
        for i in range(3): mins[i]=min(mins[i],w[i]); maxs[i]=max(maxs[i],w[i])
res['mesh_objects']=len(meshes); res['vertices']=vert_total; res['polygons']=poly_total
res['bounds_min']=mins; res['bounds_max']=maxs; res['bounds_size']=[maxs[i]-mins[i] for i in range(3)]
res['zero_poly']=zero_poly[:200]; res['no_material_count']=len(no_material); res['no_material_sample']=no_material[:100]
res['negative_scale']=neg_scale[:100]; res['unapplied_scale_count']=len(unapplied_scale); res['unapplied_scale_sample']=unapplied_scale[:100]
res['tiny_count']=len(tiny); res['tiny_sample']=tiny[:100]; res['huge_count']=len(huge); res['huge_sample']=huge[:100]
# names useful for semantic/gameplay audit
terms=['spawn','cover','choke','objective','route','nav','collision','road','street','terrain','rathaus','tram','water','tree','veget']
res['semantic_name_hits']={t:[o.name for o in objs if t in o.name.lower()][:100] for t in terms}
# custom properties count
props={}
for o in objs:
    ks=[k for k in o.keys() if k!='_RNA_UI']
    if ks: props[o.name]={k:o[k] for k in ks if isinstance(o[k],(str,int,float,bool))}
res['custom_props_count']=len(props); res['custom_props_sample']=dict(list(props.items())[:100])
# materials/images
res['materials']=len(bpy.data.materials); res['images']=len(bpy.data.images)
res['missing_images']=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not os.path.exists(bpy.path.abspath(im.filepath))][:100]
# object complexity top
complexity=sorted(((len(o.data.polygons),len(o.data.vertices),o.name) for o in meshes), reverse=True)[:50]
res['top_complexity']=[{'polygons':p,'vertices':v,'name':n} for p,v,n in complexity]
out=os.path.splitext(bpy.data.filepath)[0]+'_AUDIT.json'
with open(out,'w',encoding='utf-8') as f: json.dump(res,f,indent=2,ensure_ascii=False)
print('AUDIT_OUT='+out)
print(json.dumps({k:res[k] for k in ['objects_total','types','mesh_objects','vertices','polygons','bounds_size','shared_mesh_data_count','no_material_count','unapplied_scale_count','tiny_count','huge_count','custom_props_count','materials','images']},ensure_ascii=False))
