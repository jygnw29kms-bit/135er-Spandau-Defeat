import bpy,json,math,statistics,re
from pathlib import Path
from mathutils import Vector
src=Path(bpy.data.filepath);terrain=bpy.data.objects['SM_Rathaus_DGM1_1000m_v21'];N=513;HALF=500.;STEP=1000./(N-1)
def tz(x,y):
    if x<-HALF or x>HALF or y<-HALF or y>HALF:return None
    fx=(x+HALF)/STEP;fy=(y+HALF)/STEP;i0=int(math.floor(fx));j0=int(math.floor(fy));i1=min(N-1,i0+1);j1=min(N-1,j0+1);tx=fx-i0;ty=fy-j0
    def z(i,j):return float(terrain.data.vertices[j*N+i].co.z)
    return (z(i0,j0)*(1-tx)+z(i1,j0)*tx)*(1-ty)+(z(i0,j1)*(1-tx)+z(i1,j1)*tx)*ty
def check(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box];x=(min(p.x for p in bb)+max(p.x for p in bb))/2;y=(min(p.y for p in bb)+max(p.y for p in bb))/2;bottom=min(p.z for p in bb);z=tz(x,y);return {'name':o.name,'xy':[x,y],'bottom_z':bottom,'terrain_z':z,'delta':None if z is None else bottom-z,'role':o.get('ss_role',''),'tag':o.get('ss_tag',''),'export':bool(o.get('ss_export',True))}
targets=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    if re.match(r'^SM_SPAWN_(WEST|EAST)_[1-4]$',o.name) or o.name in ('SM_OBJECTIVE_A','SM_OBJECTIVE_B') or o.name.startswith('SM_COVER_PALLET_') or o.name.startswith('SM_COVER_BARRIER_') or o.name.startswith('P_CrateShell_COVER_CASE_') or o.name.startswith('SM_COVER_CASE_'):
        targets.append(check(o))
# buildings connected component audit
city=bpy.data.objects['SM_FULLMAP_SurroundingBuildings'];me=city.data;adj=[set() for _ in me.vertices]
for e in me.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
seen=set();d=[];outside=0
for seed in range(len(me.vertices)):
    if seed in seen:continue
    st=[seed];seen.add(seed);ids=[]
    while st:
        q=st.pop();ids.append(q)
        for j in adj[q]:
            if j not in seen:seen.add(j);st.append(j)
    ps=[city.matrix_world@me.vertices[i].co for i in ids];x=(min(p.x for p in ps)+max(p.x for p in ps))/2;y=(min(p.y for p in ps)+max(p.y for p in ps))/2;bottom=min(p.z for p in ps);z=tz(x,y)
    if z is None:outside+=1
    else:d.append(bottom-z)
rep={'file':str(src),'targets':targets,'buildings':{'inside':len(d),'outside':outside,'min':min(d),'max':max(d),'median':statistics.median(d),'abs_max':max(abs(x) for x in d),'>0.05m':sum(abs(x)>.05 for x in d)}}
src.with_name(src.stem+'_GROUNDING_TARGETS.json').write_text(json.dumps(rep,indent=2),encoding='utf-8');print('TARGETS',json.dumps(targets));print('BUILDINGS',json.dumps(rep['buildings']))
