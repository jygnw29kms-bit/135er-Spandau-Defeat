import bpy,json,math,re,statistics
from pathlib import Path
from mathutils import Vector
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v21_GEOFRAME.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v23_GROUNDED_CLEAN.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.view_layer.update();sc=bpy.context.scene
terrain=bpy.data.objects['SM_Rathaus_DGM1_1000m_v21'];N=513;HALF=500.;STEP=1000./(N-1)
def tz(x,y):
    if x<-HALF or x>HALF or y<-HALF or y>HALF:return None
    fx=(x+HALF)/STEP;fy=(y+HALF)/STEP;i0=int(math.floor(fx));j0=int(math.floor(fy));i1=min(N-1,i0+1);j1=min(N-1,j0+1);tx=fx-i0;ty=fy-j0
    def z(i,j):return float(terrain.data.vertices[j*N+i].co.z)
    return (z(i0,j0)*(1-tx)+z(i1,j0)*tx)*(1-ty)+(z(i0,j1)*(1-tx)+z(i1,j1)*tx)*ty
def bw(o):return [o.matrix_world@Vector(c) for c in o.bound_box]
# A) Objective templates: bake intended XY directly into unique mesh, then ground mesh directly.
objectives=[]
for name in ('SM_OBJECTIVE_A','SM_OBJECTIVE_B'):
    o=bpy.data.objects.get(name)
    if not o:continue
    intended=Vector((float(o.location.x),float(o.location.y),0));o.data=o.data.copy()
    for v in o.data.vertices:v.co.x+=intended.x;v.co.y+=intended.y
    o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
    minz=min(v.co.z for v in o.data.vertices);z=tz(intended.x,intended.y);dz=(z+.02)-minz
    for v in o.data.vertices:v.co.z+=dz
    o.data.update();o['ss_role']='gameplay';o['ss_tag']='objective';o['ss_export']=True
    objectives.append({'name':name,'xy':[intended.x,intended.y],'terrain_z':z,'mesh_z_shift':dz})
# B) Broken case templates are superseded by P_Crate production assemblies.
legacy_col=bpy.data.collections.get('LEGACY_GAMEPLAY_TEMPLATES') or bpy.data.collections.new('LEGACY_GAMEPLAY_TEMPLATES')
if legacy_col.name not in sc.collection.children:sc.collection.children.link(legacy_col)
legacy=[]
for i in range(5):
    o=bpy.data.objects.get(f'SM_COVER_CASE_{i}')
    if not o:continue
    for c in list(o.users_collection):c.objects.unlink(o)
    legacy_col.objects.link(o);o.hide_render=True;o.hide_viewport=True;o['ss_role']='reference';o['ss_tag']='cover_template';o['ss_export']=False;legacy.append(o.name)
# C) Pallet/barrier simple cover: bake intended XY and ground mesh directly.
simple_cover=[]
for o in list(sc.objects):
    if not (o.name.startswith('SM_COVER_PALLET_') or o.name.startswith('SM_COVER_BARRIER_')):continue
    intended=Vector((float(o.location.x),float(o.location.y),0));o.data=o.data.copy()
    for v in o.data.vertices:v.co.x+=intended.x;v.co.y+=intended.y
    o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
    minz=min(v.co.z for v in o.data.vertices);z=tz(intended.x,intended.y)
    if z is not None:
        dz=(z+.02)-minz
        for v in o.data.vertices:v.co.z+=dz
        o.data.update();simple_cover.append({'name':o.name,'xy':[intended.x,intended.y],'dz':dz})
    o['ss_role']='gameplay';o['ss_tag']='cover';o['ss_export']=True
bpy.context.view_layer.update()
# D) Production crate assemblies: use shell as ground reference; shift coherent object transforms together.
crate_groups=[]
for i in range(5):
    key=f'COVER_CASE_{i}';objs=[o for o in sc.objects if o.type=='MESH' and o.name.startswith('P_') and key in o.name]
    shell=bpy.data.objects.get(f'P_CrateShell_{key}')
    if not objs or not shell:continue
    bb=bw(shell);x=(min(p.x for p in bb)+max(p.x for p in bb))/2;y=(min(p.y for p in bb)+max(p.y for p in bb))/2;bottom=min(p.z for p in bb);z=tz(x,y);dz=(z+.02)-bottom
    for o in objs:o.location.z+=dz
    crate_groups.append({'group':key,'objects':len(objs),'xy':[x,y],'terrain_z':z,'dz':dz})
bpy.context.view_layer.update()
# E) Clamp and ground all active spawn markers/rings.
spawns=[]
for o in sc.objects:
    if o.type!='MESH' or o.get('ss_tag','')!='spawn':continue
    if re.match(r'^SM_SPAWN_(WEST|EAST)_[1-4]$',o.name):
        o.location.x=max(-495,min(495,o.location.x));o.location.y=max(-495,min(495,o.location.y));bpy.context.view_layer.update()
    bb=bw(o);x=(min(p.x for p in bb)+max(p.x for p in bb))/2;y=(min(p.y for p in bb)+max(p.y for p in bb))/2;bottom=min(p.z for p in bb);z=tz(x,y)
    if z is not None:
        dz=(z+.02)-bottom;o.location.z+=dz;spawns.append({'name':o.name,'xy':[x,y],'dz':dz})
bpy.context.view_layer.update()
# F) Ground disconnected surrounding-building components; sync collision from grounded result.
city=bpy.data.objects.get('SM_FULLMAP_SurroundingBuildings');coll=bpy.data.objects.get('UCX_COL_FULLMAP_SurroundingBuildings');bst={}
if city:
    me=city.data;adj=[set() for _ in me.vertices]
    for e in me.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    seen=set();components=[];shifts=[]
    for seed in range(len(me.vertices)):
        if seed in seen:continue
        stack=[seed];seen.add(seed);ids=[]
        while stack:
            q=stack.pop();ids.append(q)
            for j in adj[q]:
                if j not in seen:seen.add(j);stack.append(j)
        ps=[city.matrix_world@me.vertices[i].co for i in ids];x=(min(p.x for p in ps)+max(p.x for p in ps))/2;y=(min(p.y for p in ps)+max(p.y for p in ps))/2;bottom=min(p.z for p in ps);z=tz(x,y)
        if z is None:components.append((ids,None));continue
        dz=z-bottom;components.append((ids,dz));shifts.append(dz)
    for ids,dz in components:
        if dz is None:continue
        for i in ids:me.vertices[i].co.z+=dz
    me.update()
    if coll:
        old=coll.data;coll.data=me.copy();coll.data.name='UCX_COL_FULLMAP_SurroundingBuildings_Grounded_v23';
        if old.users==0:bpy.data.meshes.remove(old)
    bst={'components':len(components),'inside':len(shifts),'outside':len(components)-len(shifts),'shift_min':min(shifts),'shift_max':max(shifts),'shift_median':statistics.median(shifts),'gt_0_5':sum(abs(x)>.5 for x in shifts),'gt_1':sum(abs(x)>1 for x in shifts),'gt_2':sum(abs(x)>2 for x in shifts)}
sc['ss_master_version']='v23_GROUNDED_CLEAN';sc['grounding_policy']='DGM1 v21; gameplay surface +0.02m; buildings base=terrain; legacy case templates non-export';sc['spawn_safe_margin_m']=5.0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
rep={'source':str(SRC),'output':str(OUT),'objectives':objectives,'legacy_case_templates':legacy,'simple_cover':simple_cover,'crate_groups':crate_groups,'spawns':spawns,'buildings':bst}
REP.write_text(json.dumps(rep,indent=2),encoding='utf-8');print('V23_READY',json.dumps({'objectives':len(objectives),'legacy_case_templates':len(legacy),'simple_cover':len(simple_cover),'crate_groups':len(crate_groups),'spawns':len(spawns),'buildings':bst}),flush=True)
