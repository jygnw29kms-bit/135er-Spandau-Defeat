import bpy, os, hashlib, struct, glob, json
SRC=bpy.data.filepath
OUT=os.path.join(os.path.dirname(SRC),'SpandauStrike_Rathaus_WORLD_MASTER_v15_OPTIMIZED.blend')
GIS=r'C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1'
# 1) Production visibility/export policy: preserve data, hide obsolete/redundant authoring layers.
nonprod={'ZERO_BLOCKOUT_MODELS','PHOTO_REAL_Background'}
for c in bpy.data.collections:
    if c.name in nonprod:
        c.hide_render=True
        c.hide_viewport=True
        c['ss_export']=False
        c['ss_role']='reference_or_obsolete'
    else:
        c['ss_export']=True
# 2) Semantic object tags for future UE importer/gameplay pipeline.
role_counts={}
def setrole(o,role,sub=''):
    o['ss_role']=role
    o['ss_export']= role not in {'reference','blockout'}
    if sub: o['ss_tag']=sub
    role_counts[role]=role_counts.get(role,0)+1
for o in bpy.context.scene.objects:
    n=o.name.lower()
    cols={c.name for c in o.users_collection}
    if 'ZERO_BLOCKOUT_MODELS' in cols: setrole(o,'blockout')
    elif n.startswith('ucx_') or 'FULLMAP_Collision' in cols: setrole(o,'collision')
    elif 'spawn' in n: setrole(o,'gameplay','spawn')
    elif 'objective' in n: setrole(o,'gameplay','objective')
    elif 'cover' in n: setrole(o,'gameplay','cover')
    elif 'nav_' in n or 'navblock' in n: setrole(o,'gameplay','nav')
    elif 'terrain' in n: setrole(o,'world','terrain')
    elif 'road' in n or 'street' in n: setrole(o,'world','road')
    elif 'water' in n: setrole(o,'world','water')
    elif 'rathaus' in n or any(k in n for k in ('mainbody','tower','centralrisalit')): setrole(o,'landmark','rathaus')
    elif 'PRODUCTION_MODELS' in cols or 'PRODUCTION_FINISH' in cols or 'REAL_Rebuilt_Architecture' in cols or 'REAL_Rebuilt_Detail' in cols: setrole(o,'production')
    elif 'PHOTO_REAL_Background' in cols: setrole(o,'reference')
    else: setrole(o,'setdressing')
# 3) Repair/pack Berlin3D textures for portable master.
image_repairs=[]
for im in bpy.data.images:
    if im.source!='FILE' or not im.filepath: continue
    p=bpy.path.abspath(im.filepath)
    if not os.path.exists(p):
        base=os.path.basename(im.filepath.replace('\\','/'))
        hits=glob.glob(os.path.join(GIS,'**',base),recursive=True)
        if hits:
            im.filepath=hits[0]
            try:
                im.reload(); im.pack(); image_repairs.append([im.name,hits[0],'packed'])
            except Exception as e: image_repairs.append([im.name,hits[0],str(e)])
    else:
        try: im.pack()
        except: pass
# 4) Exact mesh-data deduplication; preserves transforms/objects/materials/UVs.
def mesh_sig(me):
    h=hashlib.blake2b(digest_size=16)
    h.update(struct.pack('<III',len(me.vertices),len(me.loops),len(me.polygons)))
    for v in me.vertices: h.update(struct.pack('<3f',*v.co))
    for l in me.loops: h.update(struct.pack('<I',l.vertex_index))
    for p in me.polygons: h.update(struct.pack('<III',p.loop_start,p.loop_total,p.material_index))
    for uv in me.uv_layers:
        h.update(uv.name.encode('utf8','ignore'))
        for d in uv.data: h.update(struct.pack('<2f',*d.uv))
    for m in me.materials: h.update((m.name if m else '').encode('utf8','ignore')+b'\0')
    return h.digest()
canon={}; reassigned=0; groups=0
for o in [x for x in bpy.context.scene.objects if x.type=='MESH' and x.data]:
    me=o.data; sig=mesh_sig(me)
    if sig in canon:
        target=canon[sig]
        # verify basic counts/material slots before reuse
        if len(target.vertices)==len(me.vertices) and len(target.polygons)==len(me.polygons) and len(target.uv_layers)==len(me.uv_layers):
            o.data=target; reassigned+=1
    else:
        canon[sig]=me; groups+=1
# 5) Scene metadata/versioning.
sc=bpy.context.scene
sc['ss_master']='Rathaus World Master'
sc['ss_master_version']='v15'
sc['ss_source']='FULLMAP_v13_UE5_READY + verified GIS/raw data'
sc['ss_engine']='UE5 only'
sc['ss_policy']='Blender world master -> tagged modular UE5 export'
sc['ss_role_counts']=json.dumps(role_counts,sort_keys=True)
# purge unused mesh datablocks created by dedup
for me in list(bpy.data.meshes):
    if me.users==0: bpy.data.meshes.remove(me)
# save
bpy.ops.wm.save_as_mainfile(filepath=OUT)
report={'source':SRC,'output':OUT,'objects':len(sc.objects),'mesh_objects':sum(o.type=='MESH' for o in sc.objects),'unique_mesh_datablocks':len(bpy.data.meshes),'dedup_reassigned':reassigned,'signature_groups':groups,'role_counts':role_counts,'image_repairs':image_repairs,'hidden_nonproduction':sorted(nonprod)}
rep=os.path.splitext(OUT)[0]+'_OPTIMIZE_REPORT.json'
with open(rep,'w',encoding='utf8') as f: json.dump(report,f,indent=2,ensure_ascii=False)
print('OPTIMIZE_RESULT='+json.dumps(report,ensure_ascii=False))
