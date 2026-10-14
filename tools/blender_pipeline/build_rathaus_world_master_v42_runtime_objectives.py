import bpy, math, json
from pathlib import Path
from mathutils import Vector
SRC=Path(bpy.data.filepath); OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v42_RUNTIME_OBJECTIVES.blend'); REP=OUT.with_suffix('.json')
sc=bpy.context.scene
col=bpy.data.collections.get('PRODUCTION_GAMEPLAY_V42_OBJECTIVES') or bpy.data.collections.new('PRODUCTION_GAMEPLAY_V42_OBJECTIVES')
if sc.collection.children.get(col.name) is None: sc.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o,do_unlink=True)
mat=bpy.data.materials.get('M_PlanterConcrete') or bpy.data.materials.get('M_Stone')
# shared 32-gon low cylinder mesh radius 1, height .12, scaled by capture radius for visible runtime proxy
n=32; verts=[]; faces=[]
for z in (0.0,0.12):
    for i in range(n):
        a=2*math.pi*i/n; verts.append((math.cos(a),math.sin(a),z))
faces.append(tuple(range(n-1,-1,-1))); faces.append(tuple(range(n,2*n)))
for i in range(n):
    j=(i+1)%n; faces.append((i,j,n+j,n+i))
me=bpy.data.meshes.new('SM_V42_ObjectiveAnchor_Module'); me.from_pydata(verts,[],faces); me.update()
if mat: me.materials.append(mat)
created=[]
for p in sorted([o for o in sc.objects if o.name.startswith('FLAG_') and o.get('ss_tag')=='territorial_objective'],key=lambda o:int(o.get('ss_sequence',0))):
    oid=int(p.get('ss_objective_id',p.get('ss_sequence',0))); players=int(p.get('ss_capture_players',1)); radius=5.5 if players>=2 else 4.0
    ground=min((p.matrix_world @ Vector(c)).z for c in p.bound_box)
    o=bpy.data.objects.new(f'OBJ_RUNTIME_{oid}_{p.name[5:]}',me); col.objects.link(o); o.location=(p.matrix_world.translation.x,p.matrix_world.translation.y,ground); o.scale=(radius,radius,1)
    o['ss_role']='gameplay'; o['ss_tag']='territorial_objective'; o['ss_export']=True; o['ss_runtime']=True; o['ss_gameplay_class']='territorial_capture'
    for k in p.keys():
        if str(k).startswith('ss_') and k not in ('ss_role','ss_tag','ss_export','ss_runtime'):
            try:o[k]=p[k]
            except: pass
    o['ss_objective_id']=oid; o['ss_capture_players']=players; o['ss_capture_radius_m']=radius; o['ss_capture_duration_s']=8.0 if players==1 else 10.0
    o['ss_contested_behavior']='pause'; o['ss_progress_decay']='hold_then_slow'; o['ss_backcap_allowed']=False; o['ss_frontline_mode']='linear_adjacent'
    created.append(o.name)
sc['ss_master_version']='v42_RUNTIME_OBJECTIVES'; sc['ss_runtime_objective_count']=len(created); sc['ss_territorial_objectives']=5
bpy.ops.wm.save_as_mainfile(filepath=str(OUT)); REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created':created},indent=2),encoding='utf-8')
print('V42_READY',len(created),OUT)
